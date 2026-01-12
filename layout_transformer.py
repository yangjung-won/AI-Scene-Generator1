"""
AI场景生成器 - 布局Transformer模块
使用本地预训练Transformer模型生成初始布局

作者: AI Team
版本: 1.0
"""

import numpy as np
import warnings

# 尝试导入transformers库
try:
    from transformers import AutoModel, AutoTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    warnings.warn("transformers未安装，将使用备用布局生成方法")


class LayoutTransformer:
    """
    使用本地Transformer生成初始布局
    无需API，完全离线工作
    """
    
    def __init__(self, model_name="bert-base-chinese", device='cpu'):
        """
        初始化本地Transformer模型
        
        Args:
            model_name: Hugging Face模型名称
                - "bert-base-chinese" (中文，推荐)
                - "distilbert-base-chinese" (轻量级中文)
                - "bert-base-uncased" (英文)
            device: 计算设备 ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self.use_transformer = False
        
        if TRANSFORMERS_AVAILABLE:
            try:
                print(f"[LOADING] Loading local Transformer: {model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModel.from_pretrained(model_name)
                self.model.to(device)
                self.model.eval()  # 评估模式
                self.use_transformer = True
                print(f"[OK] Transformer loaded (local, no API needed)")
            except Exception as e:
                print(f"[WARN] Failed to load Transformer: {e}")
                print("[INFO] Will use fallback layout generation")
                self.use_transformer = False
        else:
            print("[INFO] transformers not available, using fallback method")
            self.use_transformer = False
    
    def generate_initial_layout(self, text_description, object_types, scene_config):
        """
        根据文本描述生成初始布局
        
        Args:
            text_description: 场景描述文本
            object_types: 对象类型列表 ['tree', 'flower', ...]
            scene_config: 场景配置 {'area_size': 40.0, ...}
        
        Returns:
            dict: 初始布局配置
        """
        area_size = scene_config.get('area_size', 40.0)
        
        if self.use_transformer:
            # 使用Transformer生成
            layout = self._generate_with_transformer(
                text_description, object_types, area_size
            )
        else:
            # 使用备用方法
            layout = self._generate_fallback(object_types, area_size)
        
        return layout
    
    def _generate_with_transformer(self, text, object_types, area_size):
        """使用Transformer生成布局"""
        # 1. 文本编码
        encoded = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128
        ).to(self.device)
        
        # 2. 获取语义表示
        with torch.no_grad():
            outputs = self.model(**encoded)
            # 使用[CLS] token的表示或平均池化
            text_embedding = outputs.last_hidden_state.mean(dim=1)  # [1, hidden_dim]
            text_embedding = text_embedding.cpu().numpy()[0]
        
        # 3. 基于语义生成初始布局
        positions = []
        cluster_centers = []
        
        # 生成聚类中心（基于语义嵌入）
        num_clusters = min(4, len(object_types)) if object_types else 3
        for i in range(num_clusters):
            # 使用embedding的不同维度作为种子
            seed = int(abs(text_embedding[i * 10 % len(text_embedding)] * 1000))
            np.random.seed(seed)
            
            angle = i * 2 * np.pi / num_clusters
            radius = area_size * 0.2 + (i * 0.1)
            x = radius * np.cos(angle) + np.random.uniform(-area_size*0.1, area_size*0.1)
            y = radius * np.sin(angle) + np.random.uniform(-area_size*0.1, area_size*0.1)
            
            from scene_planner import Vector
            cluster_centers.append(Vector((x, y, 0)))
        
        # 为每个对象类型生成初始位置
        for obj_idx, obj_type in enumerate(object_types):
            # 使用embedding的不同部分作为该对象类型的特征
            seed_base = int(abs(text_embedding[obj_idx * 5 % len(text_embedding)] * 1000))
            
            # 估算对象数量（简化，实际应该从scene_plan获取）
            count = 5
            
            for i in range(count):
                np.random.seed(seed_base + i)
                
                # 选择聚类中心
                cluster_idx = obj_idx % len(cluster_centers) if cluster_centers else None
                
                if cluster_idx is not None and cluster_centers:
                    center = cluster_centers[cluster_idx]
                    # 在聚类中心周围生成位置
                    angle = np.random.uniform(0, 2 * np.pi)
                    distance = np.random.uniform(0, area_size * 0.15)
                    x = center.x + distance * np.cos(angle)
                    y = center.y + distance * np.sin(angle)
                else:
                    # 随机分布
                    x = np.random.uniform(-area_size/2, area_size/2)
                    y = np.random.uniform(-area_size/2, area_size/2)
                
                from scene_planner import Vector
                positions.append({
                    'type': obj_type,
                    'position': Vector((x, y, 0)),
                    'index': i,
                    'cluster_id': cluster_idx
                })
        
        # 构建初始空间关系图（简化版）
        spatial_graph = self._build_initial_spatial_graph(object_types, positions)
        
        return {
            'positions': positions,
            'cluster_centers': cluster_centers,
            'spatial_graph': spatial_graph,
            'area_size': area_size
        }
    
    def _generate_fallback(self, object_types, area_size):
        """备用布局生成方法（不使用Transformer）"""
        from scene_planner import Vector
        
        positions = []
        cluster_centers = []
        
        # 简单的螺旋分布
        num_clusters = min(3, len(object_types)) if object_types else 2
        for i in range(num_clusters):
            angle = i * 2 * np.pi / num_clusters
            radius = area_size * 0.25
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            cluster_centers.append(Vector((x, y, 0)))
        
        for obj_idx, obj_type in enumerate(object_types):
            count = 5  # 默认数量
            cluster_idx = obj_idx % len(cluster_centers) if cluster_centers else None
            
            for i in range(count):
                if cluster_idx is not None and cluster_centers:
                    center = cluster_centers[cluster_idx]
                    angle = np.random.uniform(0, 2 * np.pi)
                    distance = np.random.uniform(0, area_size * 0.2)
                    x = center.x + distance * np.cos(angle)
                    y = center.y + distance * np.sin(angle)
                else:
                    x = np.random.uniform(-area_size/2, area_size/2)
                    y = np.random.uniform(-area_size/2, area_size/2)
                
                positions.append({
                    'type': obj_type,
                    'position': Vector((x, y, 0)),
                    'index': i,
                    'cluster_id': cluster_idx
                })
        
        spatial_graph = self._build_initial_spatial_graph(object_types, positions)
        
        return {
            'positions': positions,
            'cluster_centers': cluster_centers,
            'spatial_graph': spatial_graph,
            'area_size': area_size
        }
    
    def _build_initial_spatial_graph(self, object_types, positions):
        """构建初始空间关系图（简化版DAG）"""
        graph = {
            'nodes': [{'id': i, 'type': obj_type} for i, obj_type in enumerate(object_types)],
            'edges': []
        }
        
        # 基于对象类型建立基本关系
        type_hierarchy = {
            'water': 0,      # anchor
            'path': 0,       # anchor
            'building': 1,   # secondary
            'tree': 1,       # secondary
            'stone': 2,      # filler
            'flower': 2,     # filler
            'grass': 2,      # filler
            'bush': 2        # filler
        }
        
        for i, obj_type_i in enumerate(object_types):
            rank_i = type_hierarchy.get(obj_type_i, 1)
            for j, obj_type_j in enumerate(object_types):
                if i != j:
                    rank_j = type_hierarchy.get(obj_type_j, 1)
                    # 高rank决定低rank的位置
                    if rank_i < rank_j:
                        graph['edges'].append({
                            'from': i,
                            'to': j,
                            'relation': 'constrains',
                            'type': 'semantic_hierarchy'
                        })
        
        return graph



























