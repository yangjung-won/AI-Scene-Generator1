"""
AI场景生成器 - 文本编码模块
使用真实的NLP模型将文本转换为语义向量

作者: AI Team
版本: 2.0 (集成预训练NLP模型)

支持的编码方法:
1. sentence-transformers (推荐) - 使用预训练的句子嵌入模型
2. spacy - 使用spaCy的词向量
3. hybrid - 组合TF-IDF和基础词嵌入
4. basic - 简单的词袋模型（备用）
"""

import numpy as np
import re
from collections import Counter
import warnings

# 尝试导入高级NLP库
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    warnings.warn("sentence-transformers未安装，将使用备用编码方法")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class TextEncoder:
    """
    文本编码器 - 将自然语言转换为语义向量
    
    支持多种编码方法，自动降级到可用的最佳方法
    """
    
    def __init__(self, encoding_dim=128, method="auto"):
        """
        初始化文本编码器
        
        Args:
            encoding_dim: 输出向量维度
            method: 编码方法 ('auto', 'sentence_transformers', 'spacy', 'hybrid', 'basic')
        """
        self.encoding_dim = encoding_dim
        self.requested_method = method
        self.method = None
        self.model = None
        self.nlp = None
        
        # 场景相关的领域词汇（用于增强语义理解）- 必须在初始化编码器之前
        self.domain_vocabulary = self._build_domain_vocabulary()
        
        # 初始化编码器
        self._initialize_encoder()
        
    def _initialize_encoder(self):
        """初始化最佳可用的编码器"""
        
        # 方法优先级
        if self.requested_method == "auto":
            methods_to_try = ['sentence_transformers', 'spacy', 'hybrid', 'basic']
        elif self.requested_method == "sentence_transformers":
            methods_to_try = ['sentence_transformers', 'hybrid', 'basic']
        elif self.requested_method == "spacy":
            methods_to_try = ['spacy', 'hybrid', 'basic']
        elif self.requested_method == "hybrid":
            methods_to_try = ['hybrid', 'basic']
        else:
            methods_to_try = ['basic']
        
        # 尝试初始化编码器
        for method in methods_to_try:
            try:
                if method == 'sentence_transformers' and SENTENCE_TRANSFORMERS_AVAILABLE:
                    self._init_sentence_transformers()
                    self.method = 'sentence_transformers'
                    print(f"[OK] Text encoder initialized: sentence-transformers (dim: {self.encoding_dim})")
                    return
                
                elif method == 'spacy' and SPACY_AVAILABLE:
                    self._init_spacy()
                    self.method = 'spacy'
                    print(f"[OK] Text encoder initialized: spaCy (dim: {self.encoding_dim})")
                    return
                
                elif method == 'hybrid':
                    self._init_hybrid()
                    self.method = 'hybrid'
                    print(f"[OK] Text encoder initialized: hybrid TF-IDF (dim: {self.encoding_dim})")
                    return
                
                elif method == 'basic':
                    self._init_basic()
                    self.method = 'basic'
                    print(f"[OK] Text encoder initialized: basic (dim: {self.encoding_dim})")
                    return
                    
            except Exception as e:
                print(f"[WARN] Cannot initialize {method}: {e}")
                continue
        
        # 如果所有方法都失败，使用最基础的方法
        self._init_basic()
        self.method = 'basic'
        print(f"[WARN] Using basic encoding method (dim: {self.encoding_dim})")
    
    def _init_sentence_transformers(self):
        """初始化sentence-transformers模型"""
        # 使用轻量级的多语言模型
        model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
        print(f"[LOADING] sentence-transformers model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"[OK] Model loaded")
    
    def _init_spacy(self):
        """初始化spaCy模型"""
        try:
            # 尝试加载中文和英文模型
            self.nlp = spacy.load("zh_core_web_md")
            print("[OK] Loaded spaCy Chinese model")
        except:
            try:
                self.nlp = spacy.load("en_core_web_md")
                print("[OK] Loaded spaCy English model")
            except:
                raise ImportError("spaCy model not found. Please run: python -m spacy download zh_core_web_md or en_core_web_md")
    
    def _init_hybrid(self):
        """初始化混合编码器（TF-IDF + 词嵌入）"""
        # 构建基础词汇表和词向量
        self.vocab_embeddings = self._build_vocab_embeddings()
        print("[OK] Initialized hybrid encoder (TF-IDF + word embeddings)")
    
    def _init_basic(self):
        """初始化基础编码器"""
        print("[OK] Initialized basic bag-of-words encoder")
    
    def encode(self, text):
        """
        编码文本为语义向量
        
        Args:
            text: 输入文本
            
        Returns:
            tuple: (encoding_vector, manual_features)
                - encoding_vector: numpy数组 [encoding_dim]
                - manual_features: 手工提取的特征字典
        """
        if not text or not isinstance(text, str):
            return np.zeros(self.encoding_dim), {}
        
        # 根据方法选择编码策略
        if self.method == 'sentence_transformers':
            encoding = self._encode_with_sentence_transformers(text)
        elif self.method == 'spacy':
            encoding = self._encode_with_spacy(text)
        elif self.method == 'hybrid':
            encoding = self._encode_with_hybrid(text)
        else:
            encoding = self._encode_with_basic(text)
        
        # 提取手工特征（补充语义信息）
        manual_features = self._extract_manual_features(text)
        
        # 确保输出维度正确
        if len(encoding) != self.encoding_dim:
            encoding = self._resize_vector(encoding, self.encoding_dim)
        
        return encoding, manual_features
    
    def _encode_with_sentence_transformers(self, text):
        """使用sentence-transformers编码"""
        try:
            # 生成句子嵌入
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"[WARN] sentence-transformers encoding failed: {e}")
            return self._encode_with_basic(text)
    
    def _encode_with_spacy(self, text):
        """使用spaCy编码"""
        try:
            doc = self.nlp(text)
            # 使用文档向量
            return doc.vector
        except Exception as e:
            print(f"[WARN] spaCy encoding failed: {e}")
            return self._encode_with_basic(text)
    
    def _encode_with_hybrid(self, text):
        """使用混合方法编码（TF-IDF + 词嵌入）"""
        # 1. 分词
        tokens = self._tokenize(text)
        
        # 2. 计算词频
        token_counts = Counter(tokens)
        total_tokens = len(tokens)
        
        # 3. 构建加权向量
        vector = np.zeros(self.encoding_dim)
        
        for token, count in token_counts.items():
            # TF (词频)
            tf = count / total_tokens if total_tokens > 0 else 0
            
            # 获取词嵌入（如果在词汇表中）
            if token in self.vocab_embeddings:
                word_vector = self.vocab_embeddings[token]
                # 加权累加
                vector += tf * word_vector
            else:
                # 未知词：使用简单的哈希编码
                hash_idx = hash(token) % self.encoding_dim
                vector[hash_idx] += tf
        
        # 4. 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def _encode_with_basic(self, text):
        """使用基础方法编码（词袋 + 哈希）"""
        vector = np.zeros(self.encoding_dim)
        
        # 分词
        tokens = self._tokenize(text)
        
        # 使用哈希技巧将词映射到向量空间
        for token in tokens:
            # 计算哈希索引
            hash_idx = hash(token) % self.encoding_dim
            vector[hash_idx] += 1.0
            
            # 添加双字符特征
            if len(token) >= 2:
                bigram_hash = hash(token[:2]) % self.encoding_dim
                vector[bigram_hash] += 0.5
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def _tokenize(self, text):
        """简单的分词器（支持中英文）"""
        # 转小写
        text = text.lower()
        
        # 分割中英文
        # 匹配英文单词和中文字符
        tokens = re.findall(r'[a-z]+|[\u4e00-\u9fff]', text)
        
        # 过滤停用词
        stopwords = {'的', '了', '和', '是', '在', '有', '我', '你', '他', 
                     'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        tokens = [t for t in tokens if t not in stopwords and len(t) > 1]
        
        return tokens
    
    def _build_vocab_embeddings(self):
        """构建领域词汇的词嵌入"""
        embeddings = {}
        
        # 为每个领域词汇生成一个特征向量
        for category, words in self.domain_vocabulary.items():
            # 为类别生成一个基础向量
            category_seed = hash(category) % 1000
            np.random.seed(category_seed)
            base_vector = np.random.randn(self.encoding_dim)
            base_vector = base_vector / np.linalg.norm(base_vector)
            
            # 为类别中的每个词生成相似的向量
            for word in words:
                word_seed = hash(word) % 1000
                np.random.seed(word_seed)
                noise = np.random.randn(self.encoding_dim) * 0.3
                word_vector = base_vector + noise
                word_vector = word_vector / np.linalg.norm(word_vector)
                embeddings[word.lower()] = word_vector
        
        return embeddings
    
    def _build_domain_vocabulary(self):
        """构建场景生成领域的词汇表"""
        return {
            'scene': ['花园', '森林', '湖泊', '山', '海滩', '草原', '城市', '室内', '沙漠',
                     'garden', 'forest', 'lake', 'mountain', 'beach', 'meadow', 'city', 
                     'indoor', 'desert', '庭院', '树林', '河流', 'river', 'park', '公园'],
            
            'nature': ['树', '花', '草', '石头', '水', '天空', '云', '太阳', '月亮',
                      'tree', 'flower', 'grass', 'stone', 'water', 'sky', 'cloud', 
                      'sun', 'moon', '植物', 'plant', '灌木', 'bush', 'shrub'],
            
            'structure': ['建筑', '房子', '桥', '路', '围栏', '长椅', '灯', '喷泉',
                         'building', 'house', 'bridge', 'path', 'fence', 'bench', 
                         'lamp', 'fountain', '塔', 'tower', '亭子', 'pavilion'],
            
            'style': ['自然', '写实', '卡通', '简约', '现代', '古典', '奇幻', '工业',
                     'natural', 'realistic', 'cartoon', 'minimal', 'modern', 'classical',
                     'fantasy', 'industrial', '可爱', 'cute', '真实', 'detailed'],
            
            'mood': ['宁静', '平静', '活力', '神秘', '浪漫', '狂野', '温馨', '黑暗',
                    'peaceful', 'calm', 'vibrant', 'mysterious', 'romantic', 'wild',
                    'cozy', 'dark', '明亮', 'bright', '阴暗', 'gloomy'],
            
            'quantity': ['几个', '许多', '很多', '密集', '稀疏', '少量',
                        'few', 'many', 'lots', 'dense', 'sparse', 'several', 'plenty'],
            
            'size': ['大', '小', '高', '矮', '宽', '窄', '巨大', '微小',
                    'big', 'small', 'large', 'tiny', 'tall', 'short', 'wide', 'narrow',
                    'huge', 'giant', 'little'],
            
            'color': ['红', '蓝', '绿', '黄', '紫', '橙', '粉', '白', '黑', '灰',
                     'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink',
                     'white', 'black', 'gray', '鲜艳', 'colorful', '暗淡', 'dull'],
            
            'time': ['早晨', '白天', '傍晚', '夜晚', '春天', '夏天', '秋天', '冬天',
                    'morning', 'day', 'evening', 'night', 'spring', 'summer', 
                    'autumn', 'winter', '黎明', 'dawn', '黄昏', 'dusk'],
            
            'specific_trees': ['松树', '柏树', '樱花', '枫树', '柳树', '橡树', '竹子',
                             'pine', 'cypress', 'cherry', 'maple', 'willow', 'oak', 
                             'bamboo', '棕榈', 'palm', '椰子', 'coconut'],
            
            'specific_flowers': ['玫瑰', '郁金香', '向日葵', '百合', '菊花', '牡丹',
                               'rose', 'tulip', 'sunflower', 'lily', 'chrysanthemum',
                               'peony', '兰花', 'orchid', '莲花', 'lotus'],
            
            'water_features': ['池塘', '湖', '河', '溪流', '瀑布', '喷泉', '海洋',
                             'pond', 'lake', 'river', 'stream', 'waterfall', 'fountain',
                             'ocean', '小溪', 'creek', '泉水', 'spring'],
            
            'terrain': ['山丘', '峡谷', '平原', '丘陵', '高地', '低地', '斜坡',
                       'hill', 'canyon', 'plain', 'highland', 'lowland', 'slope',
                       '山脉', 'mountain range', '山峰', 'peak', '悬崖', 'cliff']
        }
    
    def _extract_manual_features(self, text):
        """提取手工特征（用于补充语义信息）"""
        text_lower = text.lower()
        
        features = {
            'text_length': len(text),
            'word_count': len(self._tokenize(text)),
            'has_numbers': bool(re.search(r'\d', text)),
            'has_chinese': bool(re.search(r'[\u4e00-\u9fff]', text)),
            'has_english': bool(re.search(r'[a-zA-Z]', text)),
        }
        
        # 检测领域词汇出现频率
        for category, words in self.domain_vocabulary.items():
            category_count = sum(1 for word in words if word in text_lower)
            features[f'{category}_count'] = category_count
            features[f'has_{category}'] = category_count > 0
        
        # 计算文本复杂度
        tokens = self._tokenize(text)
        unique_tokens = set(tokens)
        features['lexical_diversity'] = len(unique_tokens) / len(tokens) if tokens else 0
        
        return features
    
    def _resize_vector(self, vector, target_dim):
        """调整向量维度"""
        current_dim = len(vector)
        
        if current_dim == target_dim:
            return vector
        elif current_dim > target_dim:
            # 截断
            return vector[:target_dim]
        else:
            # 填充
            padded = np.zeros(target_dim)
            padded[:current_dim] = vector
            return padded
    
    def get_encoding_info(self):
        """获取编码器信息"""
        return {
            'method': self.method,
            'encoding_dim': self.encoding_dim,
            'has_model': self.model is not None,
            'domain_vocab_size': sum(len(words) for words in self.domain_vocabulary.values())
        }


# 便捷函数
def create_text_encoder(encoding_dim=128, method="auto"):
    """
    创建文本编码器实例
    
    Args:
        encoding_dim: 输出向量维度
        method: 编码方法 ('auto', 'sentence_transformers', 'spacy', 'hybrid', 'basic')
    
    Returns:
        TextEncoder实例
    """
    return TextEncoder(encoding_dim=encoding_dim, method=method)


# 测试函数
def test_encoder():
    """测试文本编码器"""
    print("=" * 60)
    print("Text Encoder Test")
    print("=" * 60)
    
    # 创建编码器
    encoder = create_text_encoder(encoding_dim=128, method="auto")
    
    # 测试文本
    test_texts = [
        "创建一个宁静的花园，有樱花树和小溪",
        "Make a vibrant forest with tall pine trees",
        "我想要一个现代城市场景，有高楼大厦",
        "A peaceful meadow with wildflowers and butterflies"
    ]
    
    print(f"\n使用编码方法: {encoder.method}")
    print(f"编码维度: {encoder.encoding_dim}")
    print(f"领域词汇量: {encoder.get_encoding_info()['domain_vocab_size']}")
    print("\n" + "=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n测试 {i}: {text}")
        encoding, features = encoder.encode(text)
        print(f"  编码向量形状: {encoding.shape}")
        print(f"  向量范数: {np.linalg.norm(encoding):.4f}")
        print(f"  手工特征数: {len(features)}")
        print(f"  词数: {features.get('word_count', 0)}")
        print(f"  场景词: {features.get('scene_count', 0)}")
        print(f"  自然元素: {features.get('nature_count', 0)}")
        print(f"  风格词: {features.get('style_count', 0)}")
    
    print("\n" + "=" * 60)
    print("[OK] Text encoder test completed")
    print("=" * 60)


if __name__ == "__main__":
    test_encoder()

