"""
Conditional Autoregressive Layout Generation Model

Research-grade implementation of a conditional autoregressive model for 2D discrete
spatial layout generation with geometry-aware supervision and progressive planning.

Mathematical formulation:
    p(X | X_partial, c) = ∏_{t=1}^T p(x_t | x_<t, h)
    h = concat(SpatialEncoder(X_partial), SemanticEncoder(c))

References:
    - Vaswani et al., "Attention Is All You Need", NeurIPS 2017
    - LayoutTransformer, BLT, and related layout generation works
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class ModelConfig:
    """Configuration for the Conditional Layout Model."""
    # Layout parameters
    num_categories: int = 16          # Number of category labels (including MASK, PAD, START)
    max_seq_length: int = 1024        # Maximum layout size (H * W)
    layout_height: int = 32           # Layout grid height
    layout_width: int = 32            # Layout grid width
    
    # Special tokens
    pad_token_id: int = 0
    mask_token_id: int = 1
    start_token_id: int = 2
    num_special_tokens: int = 3
    
    # Model dimensions
    d_model: int = 512                # Model dimension
    d_ff: int = 2048                  # Feed-forward dimension
    num_heads: int = 8                # Number of attention heads
    
    # Encoder parameters
    spatial_encoder_layers: int = 6   # Layers in spatial encoder
    semantic_encoder_layers: int = 4  # Layers in semantic encoder
    
    # Decoder parameters
    decoder_layers: int = 8           # Layers in autoregressive decoder
    
    # Regularization
    dropout: float = 0.1
    attention_dropout: float = 0.1
    
    # Loss weights
    lambda_geo: float = 0.5           # Weight for geometry loss
    lambda_plan: float = 0.3          # Weight for planning loss
    
    # Training
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    warmup_steps: int = 4000
    max_epochs: int = 100
    batch_size: int = 32
    
    # Inference
    top_k: int = 5                    # Top-k sampling


# =============================================================================
# Positional Encoding
# =============================================================================

class SinusoidalPositionalEncoding(nn.Module):
    """Standard sinusoidal positional encoding."""
    
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # [1, max_len, d_model]
        
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape [batch_size, seq_len, d_model]
        Returns:
            Tensor of shape [batch_size, seq_len, d_model]
        """
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class Learned2DPositionalEncoding(nn.Module):
    """Learned 2D positional encoding for spatial layouts."""
    
    def __init__(self, d_model: int, height: int, width: int, dropout: float = 0.1):
        super().__init__()
        self.height = height
        self.width = width
        self.d_model = d_model
        
        self.row_embed = nn.Embedding(height, d_model // 2)
        self.col_embed = nn.Embedding(width, d_model // 2)
        self.dropout = nn.Dropout(p=dropout)
        
        self._init_weights()
    
    def _init_weights(self):
        nn.init.uniform_(self.row_embed.weight, -0.1, 0.1)
        nn.init.uniform_(self.col_embed.weight, -0.1, 0.1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape [batch_size, seq_len, d_model]
        Returns:
            Tensor of shape [batch_size, seq_len, d_model]
        """
        batch_size, seq_len, _ = x.shape
        
        # Generate position indices
        positions = torch.arange(seq_len, device=x.device)
        row_pos = positions // self.width
        col_pos = positions % self.width
        
        # Clamp to valid range
        row_pos = row_pos.clamp(0, self.height - 1)
        col_pos = col_pos.clamp(0, self.width - 1)
        
        # Get embeddings
        row_emb = self.row_embed(row_pos)  # [seq_len, d_model // 2]
        col_emb = self.col_embed(col_pos)  # [seq_len, d_model // 2]
        
        # Concatenate and add to input
        pos_emb = torch.cat([row_emb, col_emb], dim=-1)  # [seq_len, d_model]
        pos_emb = pos_emb.unsqueeze(0).expand(batch_size, -1, -1)
        
        return self.dropout(x + pos_emb)


# =============================================================================
# Attention Mechanisms
# =============================================================================

class MultiHeadAttention(nn.Module):
    """Multi-head attention with optional causal masking."""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(p=dropout)
        self.scale = math.sqrt(self.d_k)
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
        causal: bool = False
    ) -> torch.Tensor:
        """
        Args:
            query: [batch_size, seq_len_q, d_model]
            key: [batch_size, seq_len_k, d_model]
            value: [batch_size, seq_len_v, d_model]
            mask: Optional attention mask
            causal: Whether to apply causal masking
        Returns:
            output: [batch_size, seq_len_q, d_model]
        """
        batch_size, seq_len_q, _ = query.shape
        seq_len_k = key.shape[1]
        
        # Linear projections
        Q = self.W_q(query).view(batch_size, seq_len_q, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).view(batch_size, seq_len_k, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(batch_size, seq_len_k, self.num_heads, self.d_k).transpose(1, 2)
        
        # Attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale
        
        # Apply causal mask
        if causal:
            causal_mask = torch.triu(
                torch.ones(seq_len_q, seq_len_k, device=query.device, dtype=torch.bool),
                diagonal=1
            )
            scores = scores.masked_fill(causal_mask.unsqueeze(0).unsqueeze(0), float('-inf'))
        
        # Apply provided mask
        if mask is not None:
            scores = scores.masked_fill(mask.unsqueeze(1), float('-inf'))
        
        # Softmax and dropout
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        # Apply attention to values
        output = torch.matmul(attn_weights, V)
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len_q, self.d_model)
        
        return self.W_o(output)


# =============================================================================
# Transformer Blocks
# =============================================================================

class FeedForward(nn.Module):
    """Position-wise feed-forward network."""
    
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(p=dropout)
        self.activation = nn.GELU()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear2(self.dropout(self.activation(self.linear1(x))))


class TransformerEncoderLayer(nn.Module):
    """Standard Transformer encoder layer."""
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.ff = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(p=dropout)
        self.dropout2 = nn.Dropout(p=dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Self-attention with residual
        attn_out = self.self_attn(x, x, x, mask=mask)
        x = self.norm1(x + self.dropout1(attn_out))
        
        # Feed-forward with residual
        ff_out = self.ff(x)
        x = self.norm2(x + self.dropout2(ff_out))
        
        return x


class TransformerDecoderLayer(nn.Module):
    """Transformer decoder layer with causal self-attention and cross-attention."""
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.cross_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.ff = FeedForward(d_model, d_ff, dropout)
        
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        
        self.dropout1 = nn.Dropout(p=dropout)
        self.dropout2 = nn.Dropout(p=dropout)
        self.dropout3 = nn.Dropout(p=dropout)
    
    def forward(
        self,
        x: torch.Tensor,
        memory: torch.Tensor,
        tgt_mask: Optional[torch.Tensor] = None,
        memory_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        # Causal self-attention
        self_attn_out = self.self_attn(x, x, x, mask=tgt_mask, causal=True)
        x = self.norm1(x + self.dropout1(self_attn_out))
        
        # Cross-attention to encoder output
        cross_attn_out = self.cross_attn(x, memory, memory, mask=memory_mask)
        x = self.norm2(x + self.dropout2(cross_attn_out))
        
        # Feed-forward
        ff_out = self.ff(x)
        x = self.norm3(x + self.dropout3(ff_out))
        
        return x


# =============================================================================
# Encoders
# =============================================================================

class SpatialEncoder(nn.Module):
    """
    Transformer encoder for partially observed (masked) layout tokens.
    Encodes X_partial with 2D positional information.
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        
        # Token embedding
        self.token_embedding = nn.Embedding(
            config.num_categories,
            config.d_model,
            padding_idx=config.pad_token_id
        )
        
        # 2D positional encoding
        self.pos_encoding = Learned2DPositionalEncoding(
            config.d_model,
            config.layout_height,
            config.layout_width,
            config.dropout
        )
        
        # Transformer layers
        self.layers = nn.ModuleList([
            TransformerEncoderLayer(
                config.d_model,
                config.num_heads,
                config.d_ff,
                config.dropout
            )
            for _ in range(config.spatial_encoder_layers)
        ])
        
        self.norm = nn.LayerNorm(config.d_model)
        self.dropout = nn.Dropout(p=config.dropout)
    
    def forward(
        self,
        x_partial: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Args:
            x_partial: Partially masked layout tokens [batch_size, seq_len]
            mask: Padding mask [batch_size, seq_len]
        Returns:
            Encoded representation [batch_size, seq_len, d_model]
        """
        # Embed tokens
        x = self.token_embedding(x_partial)
        x = self.dropout(x)
        
        # Add positional encoding
        x = self.pos_encoding(x)
        
        # Transform through encoder layers
        for layer in self.layers:
            x = layer(x, mask=mask)
        
        return self.norm(x)


class SemanticEncoder(nn.Module):
    """
    Transformer encoder for semantic composition constraint vector c.
    c represents target category proportions.
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        
        # Project composition vector to sequence of embeddings
        # Each category gets its own embedding slot
        num_semantic_categories = config.num_categories - config.num_special_tokens
        self.category_embedding = nn.Embedding(num_semantic_categories, config.d_model)
        
        # Linear projection for proportion values
        self.proportion_proj = nn.Linear(1, config.d_model)
        
        # Combine category and proportion information
        self.combine = nn.Linear(2 * config.d_model, config.d_model)
        
        # Positional encoding for category order
        self.pos_encoding = SinusoidalPositionalEncoding(
            config.d_model,
            max_len=num_semantic_categories,
            dropout=config.dropout
        )
        
        # Transformer layers
        self.layers = nn.ModuleList([
            TransformerEncoderLayer(
                config.d_model,
                config.num_heads,
                config.d_ff,
                config.dropout
            )
            for _ in range(config.semantic_encoder_layers)
        ])
        
        self.norm = nn.LayerNorm(config.d_model)
        self.dropout = nn.Dropout(p=config.dropout)
    
    def forward(self, c: torch.Tensor) -> torch.Tensor:
        """
        Args:
            c: Composition vector [batch_size, num_categories - num_special_tokens]
               Each element is the target proportion for that category
        Returns:
            Encoded semantic representation [batch_size, num_semantic_cats, d_model]
        """
        batch_size, num_cats = c.shape
        device = c.device
        
        # Get category embeddings
        cat_indices = torch.arange(num_cats, device=device).unsqueeze(0).expand(batch_size, -1)
        cat_emb = self.category_embedding(cat_indices)  # [batch, num_cats, d_model]
        
        # Project proportion values
        prop_emb = self.proportion_proj(c.unsqueeze(-1))  # [batch, num_cats, d_model]
        
        # Combine
        x = self.combine(torch.cat([cat_emb, prop_emb], dim=-1))
        x = self.dropout(x)
        
        # Add positional encoding
        x = self.pos_encoding(x)
        
        # Transform through encoder layers
        for layer in self.layers:
            x = layer(x)
        
        return self.norm(x)


# =============================================================================
# Autoregressive Decoder
# =============================================================================

class AutoregressiveDecoder(nn.Module):
    """
    Transformer decoder with causal self-attention and cross-attention to h.
    h = concat(SpatialEncoder(X_partial), SemanticEncoder(c))
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        
        # Token embedding (shared with output projection for weight tying)
        self.token_embedding = nn.Embedding(
            config.num_categories,
            config.d_model,
            padding_idx=config.pad_token_id
        )
        
        # Positional encoding
        self.pos_encoding = SinusoidalPositionalEncoding(
            config.d_model,
            max_len=config.max_seq_length + 1,  # +1 for START token
            dropout=config.dropout
        )
        
        # Transformer decoder layers
        self.layers = nn.ModuleList([
            TransformerDecoderLayer(
                config.d_model,
                config.num_heads,
                config.d_ff,
                config.dropout
            )
            for _ in range(config.decoder_layers)
        ])
        
        self.norm = nn.LayerNorm(config.d_model)
        self.dropout = nn.Dropout(p=config.dropout)
        
        # Output projection for next token prediction
        self.output_proj = nn.Linear(config.d_model, config.num_categories)
        
        # Auxiliary heads for geometry prediction
        self.distance_head = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.GELU(),
            nn.Linear(config.d_model // 2, 1),
            nn.Sigmoid()  # Normalized distance [0, 1]
        )
        
        self.direction_head = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.GELU(),
            nn.Linear(config.d_model // 2, 1),
            nn.Sigmoid()  # Normalized direction [0, 1] (θ / 2π)
        )
        
        self.boundary_head = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.GELU(),
            nn.Linear(config.d_model // 2, 1),
            nn.Sigmoid()  # Boundary complexity [0, 1]
        )
        
        # Planning head for remaining category distribution
        num_semantic_cats = config.num_categories - config.num_special_tokens
        self.planning_head = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.GELU(),
            nn.Linear(config.d_model // 2, num_semantic_cats),
        )
        
        # Weight tying between embedding and output projection
        self.output_proj.weight = self.token_embedding.weight
    
    def forward(
        self,
        tgt: torch.Tensor,
        memory: torch.Tensor,
        tgt_mask: Optional[torch.Tensor] = None,
        memory_mask: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Args:
            tgt: Target sequence (shifted right, with START prepended) [batch, tgt_len]
            memory: Encoder output h [batch, memory_len, d_model]
            tgt_mask: Target padding mask
            memory_mask: Memory padding mask
        Returns:
            Dictionary containing:
                - logits: Token logits [batch, tgt_len, num_categories]
                - distance: Predicted distance [batch, tgt_len, 1]
                - direction: Predicted direction [batch, tgt_len, 1]
                - boundary: Predicted boundary complexity [batch, tgt_len, 1]
                - planning: Predicted remaining distribution [batch, tgt_len, num_semantic_cats]
                - hidden_states: Decoder hidden states [batch, tgt_len, d_model]
        """
        # Embed target tokens
        x = self.token_embedding(tgt)
        x = self.dropout(x)
        
        # Add positional encoding
        x = self.pos_encoding(x)
        
        # Transform through decoder layers
        for layer in self.layers:
            x = layer(x, memory, tgt_mask=tgt_mask, memory_mask=memory_mask)
        
        hidden_states = self.norm(x)
        
        # Output projections
        logits = self.output_proj(hidden_states)
        distance = self.distance_head(hidden_states)
        direction = self.direction_head(hidden_states)
        boundary = self.boundary_head(hidden_states)
        planning = self.planning_head(hidden_states)
        
        return {
            'logits': logits,
            'distance': distance,
            'direction': direction,
            'boundary': boundary,
            'planning': planning,
            'hidden_states': hidden_states
        }


# =============================================================================
# Complete Model
# =============================================================================

class ConditionalLayoutModel(nn.Module):
    """
    Complete conditional autoregressive layout generation model.
    
    p(X | X_partial, c) = ∏_{t=1}^T p(x_t | x_<t, h)
    h = concat(SpatialEncoder(X_partial), SemanticEncoder(c))
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        
        # Encoders
        self.spatial_encoder = SpatialEncoder(config)
        self.semantic_encoder = SemanticEncoder(config)
        
        # Decoder
        self.decoder = AutoregressiveDecoder(config)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights with Xavier uniform."""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def encode(
        self,
        x_partial: torch.Tensor,
        c: torch.Tensor,
        partial_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Encode partial layout and semantic composition.
        
        Args:
            x_partial: Partially masked layout [batch, seq_len]
            c: Composition vector [batch, num_semantic_cats]
            partial_mask: Padding mask for partial layout
        Returns:
            h: Combined encoding [batch, spatial_len + semantic_len, d_model]
        """
        # Encode spatial (partial layout)
        h_spatial = self.spatial_encoder(x_partial, mask=partial_mask)
        
        # Encode semantic (composition)
        h_semantic = self.semantic_encoder(c)
        
        # Concatenate
        h = torch.cat([h_spatial, h_semantic], dim=1)
        
        return h
    
    def forward(
        self,
        x_partial: torch.Tensor,
        c: torch.Tensor,
        tgt: torch.Tensor,
        partial_mask: Optional[torch.Tensor] = None,
        tgt_mask: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass for training with teacher forcing.
        
        Args:
            x_partial: Partially masked layout [batch, seq_len]
            c: Composition vector [batch, num_semantic_cats]
            tgt: Target sequence (original layout, will be shifted) [batch, seq_len]
            partial_mask: Padding mask for partial layout
            tgt_mask: Padding mask for target
        Returns:
            Model outputs dictionary
        """
        # Encode
        h = self.encode(x_partial, c, partial_mask)
        
        # Prepare decoder input (prepend START token, shift right)
        batch_size = tgt.shape[0]
        start_tokens = torch.full(
            (batch_size, 1),
            self.config.start_token_id,
            dtype=torch.long,
            device=tgt.device
        )
        decoder_input = torch.cat([start_tokens, tgt[:, :-1]], dim=1)
        
        # Decode
        outputs = self.decoder(decoder_input, h, tgt_mask=tgt_mask)
        
        return outputs
    
    @torch.no_grad()
    def generate(
        self,
        x_partial: torch.Tensor,
        c: torch.Tensor,
        partial_mask: Optional[torch.Tensor] = None,
        temperature: float = 1.0,
        top_k: Optional[int] = None
    ) -> torch.Tensor:
        """
        Autoregressive generation with top-k sampling.
        
        Args:
            x_partial: Partially masked layout [batch, seq_len]
            c: Composition vector [batch, num_semantic_cats]
            partial_mask: Padding mask
            temperature: Sampling temperature
            top_k: Top-k sampling parameter (defaults to config value)
        Returns:
            Generated layout [batch, seq_len]
        """
        self.eval()
        
        if top_k is None:
            top_k = self.config.top_k
        
        batch_size, seq_len = x_partial.shape
        device = x_partial.device
        
        # Encode context
        h = self.encode(x_partial, c, partial_mask)
        
        # Initialize with START token
        generated = torch.full(
            (batch_size, 1),
            self.config.start_token_id,
            dtype=torch.long,
            device=device
        )
        
        # Autoregressive generation
        for t in range(seq_len):
            # Decode current sequence
            outputs = self.decoder(generated, h)
            logits = outputs['logits'][:, -1, :] / temperature
            
            # Top-k sampling
            if top_k > 0:
                values, indices = torch.topk(logits, top_k, dim=-1)
                logits = torch.full_like(logits, float('-inf'))
                logits.scatter_(-1, indices, values)
            
            # Sample
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            
            # Append
            generated = torch.cat([generated, next_token], dim=1)
        
        # Remove START token
        return generated[:, 1:]


# =============================================================================
# Geometry Target Computation
# =============================================================================

class GeometryTargetComputer:
    """
    Computes geometry-aware supervision targets.
    
    For each spatial position t, computes:
    - d_t: normalized distance to region centroid
    - θ_t: normalized direction to centroid  
    - b_t: boundary complexity (neighbor label disagreement)
    """
    
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
    
    def compute_targets(
        self,
        layout: torch.Tensor,
        num_categories: int,
        num_special_tokens: int = 3
    ) -> Dict[str, torch.Tensor]:
        """
        Compute geometry targets for a batch of layouts.
        
        Args:
            layout: Layout tensor [batch, height * width] or [batch, height, width]
            num_categories: Total number of categories
            num_special_tokens: Number of special tokens (PAD, MASK, START)
        Returns:
            Dictionary with 'distance', 'direction', 'boundary' tensors
        """
        batch_size = layout.shape[0]
        device = layout.device
        
        # Reshape to 2D if needed
        if layout.dim() == 2:
            layout_2d = layout.view(batch_size, self.height, self.width)
        else:
            layout_2d = layout
        
        distances = torch.zeros(batch_size, self.height, self.width, device=device)
        directions = torch.zeros(batch_size, self.height, self.width, device=device)
        boundaries = torch.zeros(batch_size, self.height, self.width, device=device)
        
        for b in range(batch_size):
            layout_b = layout_2d[b]
            
            # Compute centroid for each category
            centroids = self._compute_centroids(layout_b, num_categories, num_special_tokens)
            
            # Compute distance and direction to centroid
            for i in range(self.height):
                for j in range(self.width):
                    cat = layout_b[i, j].item()
                    
                    # Skip special tokens
                    if cat < num_special_tokens:
                        continue
                    
                    if cat in centroids:
                        cy, cx = centroids[cat]
                        
                        # Distance (normalized by max possible distance)
                        dist = math.sqrt((i - cy) ** 2 + (j - cx) ** 2)
                        max_dist = math.sqrt(self.height ** 2 + self.width ** 2)
                        distances[b, i, j] = dist / max_dist
                        
                        # Direction (normalized to [0, 1])
                        angle = math.atan2(cy - i, cx - j)  # [-π, π]
                        directions[b, i, j] = (angle + math.pi) / (2 * math.pi)
            
            # Compute boundary complexity
            boundaries[b] = self._compute_boundary_complexity(layout_b)
        
        # Flatten back to sequence
        return {
            'distance': distances.view(batch_size, -1, 1),
            'direction': directions.view(batch_size, -1, 1),
            'boundary': boundaries.view(batch_size, -1, 1)
        }
    
    def _compute_centroids(
        self,
        layout: torch.Tensor,
        num_categories: int,
        num_special_tokens: int
    ) -> Dict[int, Tuple[float, float]]:
        """Compute centroid for each category in the layout."""
        centroids = {}
        
        for cat in range(num_special_tokens, num_categories):
            mask = (layout == cat)
            if mask.sum() > 0:
                positions = mask.nonzero(as_tuple=False).float()
                centroid_y = positions[:, 0].mean().item()
                centroid_x = positions[:, 1].mean().item()
                centroids[cat] = (centroid_y, centroid_x)
        
        return centroids
    
    def _compute_boundary_complexity(self, layout: torch.Tensor) -> torch.Tensor:
        """
        Compute boundary complexity as neighbor label disagreement.
        For each position, count how many of its 4-neighbors have different labels.
        Normalized to [0, 1].
        """
        h, w = layout.shape
        complexity = torch.zeros_like(layout, dtype=torch.float)
        
        for i in range(h):
            for j in range(w):
                current = layout[i, j]
                neighbors = []
                
                if i > 0:
                    neighbors.append(layout[i-1, j])
                if i < h - 1:
                    neighbors.append(layout[i+1, j])
                if j > 0:
                    neighbors.append(layout[i, j-1])
                if j < w - 1:
                    neighbors.append(layout[i, j+1])
                
                if neighbors:
                    disagreements = sum(1 for n in neighbors if n != current)
                    complexity[i, j] = disagreements / len(neighbors)
        
        return complexity


# =============================================================================
# Planning Target Computation
# =============================================================================

class PlanningTargetComputer:
    """
    Computes progressive planning constraint targets.
    
    At each step t, defines c_>t = remaining target category distribution.
    """
    
    def __init__(self, num_categories: int, num_special_tokens: int = 3):
        self.num_categories = num_categories
        self.num_special_tokens = num_special_tokens
        self.num_semantic_cats = num_categories - num_special_tokens
    
    def compute_targets(
        self,
        layout: torch.Tensor,
        target_composition: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute remaining category distribution at each position.
        
        Args:
            layout: Layout tensor [batch, seq_len]
            target_composition: Target category proportions [batch, num_semantic_cats]
        Returns:
            Remaining distributions [batch, seq_len, num_semantic_cats]
        """
        batch_size, seq_len = layout.shape
        device = layout.device
        
        # Initialize remaining counts from target composition
        total_per_cat = (target_composition * seq_len).long()
        
        remaining_dists = torch.zeros(
            batch_size, seq_len, self.num_semantic_cats,
            device=device
        )
        
        for b in range(batch_size):
            remaining = total_per_cat[b].clone().float()
            
            for t in range(seq_len):
                # Normalize to get distribution
                total_remaining = remaining.sum()
                if total_remaining > 0:
                    remaining_dists[b, t] = remaining / total_remaining
                else:
                    # Uniform if nothing remaining
                    remaining_dists[b, t] = 1.0 / self.num_semantic_cats
                
                # Update remaining counts based on current token
                cat = layout[b, t].item()
                if cat >= self.num_special_tokens:
                    cat_idx = cat - self.num_special_tokens
                    remaining[cat_idx] = max(0, remaining[cat_idx] - 1)
        
        return remaining_dists


# =============================================================================
# Loss Functions
# =============================================================================

class LayoutLoss(nn.Module):
    """
    Combined loss for layout generation.
    
    L = L_cat + λ_geo * L_geo + λ_plan * L_plan
    
    Where:
    - L_cat: categorical cross-entropy over layout tokens
    - L_geo: L1 loss for geometry predictions (distance, direction, boundary)
    - L_plan: KL divergence for progressive planning constraint
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.ce_loss = nn.CrossEntropyLoss(ignore_index=config.pad_token_id)
        self.l1_loss = nn.L1Loss(reduction='none')
        self.kl_loss = nn.KLDivLoss(reduction='batchmean')
        
        self.geometry_computer = GeometryTargetComputer(
            config.layout_height,
            config.layout_width
        )
        self.planning_computer = PlanningTargetComputer(
            config.num_categories,
            config.num_special_tokens
        )
    
    def forward(
        self,
        outputs: Dict[str, torch.Tensor],
        targets: torch.Tensor,
        composition: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Compute combined loss.
        
        Args:
            outputs: Model outputs dictionary
            targets: Ground truth layout [batch, seq_len]
            composition: Target composition vector [batch, num_semantic_cats]
            mask: Optional mask for valid positions
        Returns:
            Dictionary with loss components and total loss
        """
        batch_size, seq_len = targets.shape
        device = targets.device
        
        # =====================================================================
        # 1. Categorical Cross-Entropy Loss
        # =====================================================================
        logits = outputs['logits']  # [batch, seq_len, num_categories]
        loss_cat = self.ce_loss(
            logits.view(-1, self.config.num_categories),
            targets.view(-1)
        )
        
        # =====================================================================
        # 2. Geometry Loss
        # =====================================================================
        geo_targets = self.geometry_computer.compute_targets(
            targets,
            self.config.num_categories,
            self.config.num_special_tokens
        )
        
        loss_distance = self.l1_loss(
            outputs['distance'],
            geo_targets['distance']
        )
        loss_direction = self.l1_loss(
            outputs['direction'],
            geo_targets['direction']
        )
        loss_boundary = self.l1_loss(
            outputs['boundary'],
            geo_targets['boundary']
        )
        
        # Apply mask if provided
        if mask is not None:
            mask_expanded = mask.unsqueeze(-1).float()
            loss_distance = (loss_distance * mask_expanded).sum() / mask_expanded.sum()
            loss_direction = (loss_direction * mask_expanded).sum() / mask_expanded.sum()
            loss_boundary = (loss_boundary * mask_expanded).sum() / mask_expanded.sum()
        else:
            loss_distance = loss_distance.mean()
            loss_direction = loss_direction.mean()
            loss_boundary = loss_boundary.mean()
        
        loss_geo = loss_distance + loss_direction + loss_boundary
        
        # =====================================================================
        # 3. Planning Loss (KL Divergence)
        # =====================================================================
        planning_targets = self.planning_computer.compute_targets(
            targets,
            composition
        )
        
        # Log softmax for KL divergence
        planning_logprobs = F.log_softmax(outputs['planning'], dim=-1)
        
        # KL divergence: KL(target || predicted)
        loss_plan = self.kl_loss(
            planning_logprobs.view(-1, planning_targets.shape[-1]),
            planning_targets.view(-1, planning_targets.shape[-1])
        )
        
        # =====================================================================
        # Total Loss
        # =====================================================================
        loss_total = (
            loss_cat +
            self.config.lambda_geo * loss_geo +
            self.config.lambda_plan * loss_plan
        )
        
        return {
            'loss': loss_total,
            'loss_cat': loss_cat,
            'loss_geo': loss_geo,
            'loss_distance': loss_distance,
            'loss_direction': loss_direction,
            'loss_boundary': loss_boundary,
            'loss_plan': loss_plan
        }


# =============================================================================
# Masking Strategies
# =============================================================================

class MaskingStrategy:
    """
    Random masking strategies for training.
    
    Strategies:
    - full_mask: Mask all tokens
    - strokes: Mask random strokes/lines
    - borders: Mask border regions
    - patches: Mask random rectangular patches
    - random: Random token masking
    """
    
    def __init__(
        self,
        height: int,
        width: int,
        mask_token_id: int,
        mask_ratio_range: Tuple[float, float] = (0.3, 0.9)
    ):
        self.height = height
        self.width = width
        self.mask_token_id = mask_token_id
        self.mask_ratio_range = mask_ratio_range
    
    def apply_mask(
        self,
        layout: torch.Tensor,
        strategy: Optional[str] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Apply masking to layout.
        
        Args:
            layout: Original layout [batch, seq_len] or [batch, height, width]
            strategy: Masking strategy ('full', 'strokes', 'borders', 'patches', 'random')
                     If None, randomly selects a strategy
        Returns:
            masked_layout: Layout with masks applied
            mask: Boolean tensor indicating masked positions
        """
        if strategy is None:
            strategy = np.random.choice(['full', 'strokes', 'borders', 'patches', 'random'])
        
        batch_size = layout.shape[0]
        device = layout.device
        
        # Reshape to 2D
        if layout.dim() == 2 and layout.shape[1] == self.height * self.width:
            layout_2d = layout.view(batch_size, self.height, self.width)
            was_flat = True
        else:
            layout_2d = layout
            was_flat = False
        
        if strategy == 'full':
            mask = torch.ones_like(layout_2d, dtype=torch.bool)
        elif strategy == 'strokes':
            mask = self._stroke_mask(batch_size, device)
        elif strategy == 'borders':
            mask = self._border_mask(batch_size, device)
        elif strategy == 'patches':
            mask = self._patch_mask(batch_size, device)
        else:  # random
            mask = self._random_mask(batch_size, device)
        
        # Apply mask
        masked_layout = layout_2d.clone()
        masked_layout[mask] = self.mask_token_id
        
        # Flatten if input was flat
        if was_flat:
            masked_layout = masked_layout.view(batch_size, -1)
            mask = mask.view(batch_size, -1)
        
        return masked_layout, mask
    
    def _random_mask(self, batch_size: int, device: torch.device) -> torch.Tensor:
        """Random token masking."""
        ratio = np.random.uniform(*self.mask_ratio_range)
        mask = torch.rand(batch_size, self.height, self.width, device=device) < ratio
        return mask
    
    def _stroke_mask(self, batch_size: int, device: torch.device) -> torch.Tensor:
        """Mask random horizontal and vertical strokes."""
        mask = torch.zeros(batch_size, self.height, self.width, dtype=torch.bool, device=device)
        
        for b in range(batch_size):
            # Random number of strokes
            num_h_strokes = np.random.randint(1, self.height // 4 + 1)
            num_v_strokes = np.random.randint(1, self.width // 4 + 1)
            
            # Horizontal strokes
            h_indices = np.random.choice(self.height, num_h_strokes, replace=False)
            for h in h_indices:
                mask[b, h, :] = True
            
            # Vertical strokes
            v_indices = np.random.choice(self.width, num_v_strokes, replace=False)
            for v in v_indices:
                mask[b, :, v] = True
        
        return mask
    
    def _border_mask(self, batch_size: int, device: torch.device) -> torch.Tensor:
        """Mask border regions."""
        mask = torch.zeros(batch_size, self.height, self.width, dtype=torch.bool, device=device)
        
        for b in range(batch_size):
            border_width = np.random.randint(1, min(self.height, self.width) // 4 + 1)
            
            # Top and bottom borders
            mask[b, :border_width, :] = True
            mask[b, -border_width:, :] = True
            
            # Left and right borders
            mask[b, :, :border_width] = True
            mask[b, :, -border_width:] = True
        
        return mask
    
    def _patch_mask(self, batch_size: int, device: torch.device) -> torch.Tensor:
        """Mask random rectangular patches."""
        mask = torch.zeros(batch_size, self.height, self.width, dtype=torch.bool, device=device)
        
        for b in range(batch_size):
            num_patches = np.random.randint(1, 5)
            
            for _ in range(num_patches):
                # Random patch size
                ph = np.random.randint(self.height // 8, self.height // 2)
                pw = np.random.randint(self.width // 8, self.width // 2)
                
                # Random position
                top = np.random.randint(0, self.height - ph)
                left = np.random.randint(0, self.width - pw)
                
                mask[b, top:top+ph, left:left+pw] = True
        
        return mask


# =============================================================================
# Training Loop
# =============================================================================

class LayoutTrainer:
    """Training loop for the conditional layout model."""
    
    def __init__(
        self,
        model: ConditionalLayoutModel,
        config: ModelConfig,
        device: torch.device
    ):
        self.model = model.to(device)
        self.config = config
        self.device = device
        
        # Loss function
        self.criterion = LayoutLoss(config)
        
        # Masking strategy
        self.masking = MaskingStrategy(
            config.layout_height,
            config.layout_width,
            config.mask_token_id
        )
        
        # Optimizer
        self.optimizer = AdamW(
            model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )
        
        # Scheduler
        self.scheduler = CosineAnnealingLR(
            self.optimizer,
            T_max=config.max_epochs,
            eta_min=config.learning_rate * 0.01
        )
        
        # Warmup
        self.warmup_steps = config.warmup_steps
        self.current_step = 0
    
    def _get_lr_scale(self) -> float:
        """Compute learning rate scale for warmup."""
        if self.current_step < self.warmup_steps:
            return self.current_step / self.warmup_steps
        return 1.0
    
    def compute_composition(
        self,
        layout: torch.Tensor,
        num_categories: int,
        num_special_tokens: int
    ) -> torch.Tensor:
        """
        Compute category composition (proportions) from layout.
        
        Args:
            layout: Layout tensor [batch, seq_len]
            num_categories: Total number of categories
            num_special_tokens: Number of special tokens
        Returns:
            Composition vector [batch, num_semantic_cats]
        """
        batch_size, seq_len = layout.shape
        num_semantic_cats = num_categories - num_special_tokens
        
        composition = torch.zeros(batch_size, num_semantic_cats, device=layout.device)
        
        for b in range(batch_size):
            for cat in range(num_special_tokens, num_categories):
                count = (layout[b] == cat).sum().float()
                composition[b, cat - num_special_tokens] = count / seq_len
        
        return composition
    
    def train_step(
        self,
        batch: torch.Tensor,
        masking_strategy: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Single training step.
        
        Args:
            batch: Batch of layouts [batch_size, seq_len]
            masking_strategy: Optional specific masking strategy
        Returns:
            Dictionary of loss values
        """
        self.model.train()
        self.current_step += 1
        
        batch = batch.to(self.device)
        
        # Compute composition from ground truth
        composition = self.compute_composition(
            batch,
            self.config.num_categories,
            self.config.num_special_tokens
        )
        
        # Apply masking
        x_partial, mask = self.masking.apply_mask(batch, masking_strategy)
        
        # Forward pass
        outputs = self.model(x_partial, composition, batch)
        
        # Compute loss
        losses = self.criterion(outputs, batch, composition)
        
        # Backward pass with warmup
        self.optimizer.zero_grad()
        losses['loss'].backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        
        # Apply warmup to learning rate
        lr_scale = self._get_lr_scale()
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = self.config.learning_rate * lr_scale
        
        self.optimizer.step()
        
        return {k: v.item() for k, v in losses.items()}
    
    def train_epoch(
        self,
        dataloader: torch.utils.data.DataLoader,
        epoch: int
    ) -> Dict[str, float]:
        """
        Train for one epoch.
        
        Args:
            dataloader: Training data loader
            epoch: Current epoch number
        Returns:
            Average losses for the epoch
        """
        epoch_losses = {}
        num_batches = 0
        
        for batch in dataloader:
            losses = self.train_step(batch)
            
            for k, v in losses.items():
                epoch_losses[k] = epoch_losses.get(k, 0) + v
            num_batches += 1
        
        # Update scheduler
        self.scheduler.step()
        
        # Average losses
        return {k: v / num_batches for k, v in epoch_losses.items()}
    
    @torch.no_grad()
    def evaluate(
        self,
        dataloader: torch.utils.data.DataLoader
    ) -> Dict[str, float]:
        """
        Evaluate model on validation set.
        
        Args:
            dataloader: Validation data loader
        Returns:
            Average losses
        """
        self.model.eval()
        
        total_losses = {}
        num_batches = 0
        
        for batch in dataloader:
            batch = batch.to(self.device)
            
            composition = self.compute_composition(
                batch,
                self.config.num_categories,
                self.config.num_special_tokens
            )
            
            x_partial, mask = self.masking.apply_mask(batch, 'random')
            outputs = self.model(x_partial, composition, batch)
            losses = self.criterion(outputs, batch, composition)
            
            for k, v in losses.items():
                total_losses[k] = total_losses.get(k, 0) + v.item()
            num_batches += 1
        
        return {k: v / num_batches for k, v in total_losses.items()}


# =============================================================================
# Inference
# =============================================================================

class LayoutGenerator:
    """Inference utilities for layout generation."""
    
    def __init__(
        self,
        model: ConditionalLayoutModel,
        config: ModelConfig,
        device: torch.device
    ):
        self.model = model.to(device)
        self.config = config
        self.device = device
        self.masking = MaskingStrategy(
            config.layout_height,
            config.layout_width,
            config.mask_token_id
        )
    
    @torch.no_grad()
    def generate(
        self,
        x_partial: Optional[torch.Tensor] = None,
        composition: Optional[torch.Tensor] = None,
        batch_size: int = 1,
        temperature: float = 1.0,
        top_k: Optional[int] = None
    ) -> torch.Tensor:
        """
        Generate layouts.
        
        Args:
            x_partial: Optional partial layout [batch, seq_len]
            composition: Optional target composition [batch, num_semantic_cats]
            batch_size: Number of layouts to generate
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
        Returns:
            Generated layouts [batch, seq_len]
        """
        self.model.eval()
        
        seq_len = self.config.layout_height * self.config.layout_width
        num_semantic_cats = self.config.num_categories - self.config.num_special_tokens
        
        # Create fully masked partial layout if not provided
        if x_partial is None:
            x_partial = torch.full(
                (batch_size, seq_len),
                self.config.mask_token_id,
                dtype=torch.long,
                device=self.device
            )
        else:
            x_partial = x_partial.to(self.device)
            batch_size = x_partial.shape[0]
        
        # Create uniform composition if not provided
        if composition is None:
            composition = torch.ones(
                batch_size, num_semantic_cats,
                device=self.device
            ) / num_semantic_cats
        else:
            composition = composition.to(self.device)
        
        return self.model.generate(
            x_partial,
            composition,
            temperature=temperature,
            top_k=top_k or self.config.top_k
        )
    
    @torch.no_grad()
    def complete(
        self,
        x_partial: torch.Tensor,
        composition: torch.Tensor,
        temperature: float = 1.0,
        top_k: Optional[int] = None
    ) -> torch.Tensor:
        """
        Complete a partially observed layout.
        
        Args:
            x_partial: Partial layout with masked positions [batch, seq_len]
            composition: Target composition [batch, num_semantic_cats]
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
        Returns:
            Completed layouts [batch, seq_len]
        """
        return self.generate(
            x_partial,
            composition,
            temperature=temperature,
            top_k=top_k
        )


# =============================================================================
# Utility Functions
# =============================================================================

def create_model(config: Optional[ModelConfig] = None) -> ConditionalLayoutModel:
    """Create a new model with given configuration."""
    if config is None:
        config = ModelConfig()
    return ConditionalLayoutModel(config)


def load_model(
    checkpoint_path: str,
    config: Optional[ModelConfig] = None,
    device: torch.device = torch.device('cpu')
) -> ConditionalLayoutModel:
    """Load a model from checkpoint."""
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    if config is None:
        config = checkpoint.get('config', ModelConfig())
    
    model = ConditionalLayoutModel(config)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    
    return model


def save_model(
    model: ConditionalLayoutModel,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    config: ModelConfig,
    checkpoint_path: str
):
    """Save model checkpoint."""
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'config': config
    }, checkpoint_path)


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == '__main__':
    # Configuration
    config = ModelConfig(
        num_categories=16,
        layout_height=32,
        layout_width=32,
        d_model=256,
        num_heads=4,
        spatial_encoder_layers=4,
        semantic_encoder_layers=2,
        decoder_layers=4,
        batch_size=4
    )
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create model
    model = create_model(config)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Create dummy data
    batch_size = config.batch_size
    seq_len = config.layout_height * config.layout_width
    num_semantic_cats = config.num_categories - config.num_special_tokens
    
    # Random layout (categories from num_special_tokens to num_categories)
    dummy_layout = torch.randint(
        config.num_special_tokens,
        config.num_categories,
        (batch_size, seq_len)
    )
    
    # Create trainer
    trainer = LayoutTrainer(model, config, device)
    
    # Training step
    print("\n--- Training Step ---")
    losses = trainer.train_step(dummy_layout)
    for k, v in losses.items():
        print(f"  {k}: {v:.4f}")
    
    # Generation
    print("\n--- Generation ---")
    generator = LayoutGenerator(model, config, device)
    
    # Generate with uniform composition
    generated = generator.generate(batch_size=2, temperature=0.8)
    print(f"Generated layout shape: {generated.shape}")
    print(f"Generated layout sample:\n{generated[0].view(config.layout_height, config.layout_width)[:8, :8]}")
    
    # Complete partial layout
    masking = MaskingStrategy(
        config.layout_height,
        config.layout_width,
        config.mask_token_id
    )
    x_partial, mask = masking.apply_mask(dummy_layout[:1], 'patches')
    composition = trainer.compute_composition(
        dummy_layout[:1],
        config.num_categories,
        config.num_special_tokens
    )
    
    completed = generator.complete(x_partial, composition)
    print(f"\nCompleted layout shape: {completed.shape}")
    
    print("\n--- Target Computation Example ---")
    
    # Geometry targets
    geo_computer = GeometryTargetComputer(config.layout_height, config.layout_width)
    geo_targets = geo_computer.compute_targets(
        dummy_layout,
        config.num_categories,
        config.num_special_tokens
    )
    print(f"Distance targets shape: {geo_targets['distance'].shape}")
    print(f"Direction targets shape: {geo_targets['direction'].shape}")
    print(f"Boundary targets shape: {geo_targets['boundary'].shape}")
    
    # Planning targets
    plan_computer = PlanningTargetComputer(config.num_categories, config.num_special_tokens)
    plan_targets = plan_computer.compute_targets(dummy_layout, composition.expand(batch_size, -1))
    print(f"Planning targets shape: {plan_targets.shape}")
    
    print("\n--- Done ---")

