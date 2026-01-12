"""
AI场景生成器 - NLP解析模块 (重构版本)
解析自然语言输入，提取场景元素和参数，集成文本编码

作者: AI Team
版本: 3.0 (集成真实NLP模型)
"""

import re
import numpy as np
from text_encoder import TextEncoder


class NLPParser:
    """
    自然语言处理解析器（增强版）
    集成预训练文本编码器和高级特征提取
    支持使用训练好的参数预测模型
    """
    
    def __init__(self, use_pretrained_model=False, model_path=None, use_trained_predictor=True):
        """
        初始化NLP解析器
        
        Args:
            use_pretrained_model: 是否使用预训练模型
            model_path: 模型路径（预留）
            use_trained_predictor: 是否使用训练好的参数预测模型
        """
        self.use_pretrained_model = use_pretrained_model
        self.model_path = model_path
        self.use_trained_predictor = use_trained_predictor
        
        # 集成文本编码器 - 自动选择最佳可用方法
        print("[LOADING] Initializing text encoder...")
        self.text_encoder = TextEncoder(encoding_dim=128, method="auto")
        
        # 🆕 集成语义关系解析器
        try:
            from semantic_relation_parser import SemanticRelationParser
            self.relation_parser = SemanticRelationParser()
            print("[OK] Semantic relation parser loaded")
        except Exception as e:
            print(f"[WARN] Semantic relation parser not available: {e}")
            self.relation_parser = None
        
        # 集成训练好的参数预测器（如果可用）
        self.scene_predictor = None
        if use_trained_predictor:
            try:
                from predictor import ScenePredictor
                self.scene_predictor = ScenePredictor()
                if self.scene_predictor.is_loaded:
                    print("[OK] Trained parameter predictor loaded")
                else:
                    print("[INFO] Predictor not loaded, using rule-based method")
                    self.scene_predictor = None
            except Exception as e:
                print(f"[WARN] Could not load predictor: {e}")
                self.scene_predictor = None
        
        # 场景类型关键词（大幅扩展）
        self.scene_keywords = {
            'garden': ['花园', '庭院', '园林', '后院', '前院', 'garden', 'yard', 'courtyard', 
                      'backyard', 'frontyard', '园子', '小园'],
            'forest': ['森林', '树林', '丛林', '林地', '密林', 'forest', 'woods', 'jungle', 
                      'woodland', 'grove', '林区', '树丛', '樱花林', '櫻花林', '樱花', '櫻花', 
                      'cherry forest', 'cherry blossom forest'],
            'winter': ['冬天', '冬季', '冬日', 'winter', 'wintery', 'wintry', 'snow', 'snowy', 
                      'snow-covered', 'snowdusted', 'frost', 'frosty', 'ice', 'icy', 'frozen',
                      '雪地', '雪景', '雪', '霜', '冰', '冰冻', 'landscape'],  # 🆕 添加landscape到winter，避免误判为indoor
            'city': ['城市', '街道', '都市', '市区', '城区', 'city', 'urban', 'street', 
                    'downtown', 'metropolitan', '街景', '市中心'],
            'indoor': ['室内', '房间', '屋内', 'indoor', 'room', 'interior', 'inside',
                      '房内', '内部空间'],
            'desert': ['沙漠', '荒漠', 'desert', 'dune', '沙丘', '戈壁'],
            'beach': ['海滩', '沙滩', '海边', '海岸', 'beach', 'seaside', 'coast', 
                     'shore', 'coastline', '海滨'],
            'mountain': ['山', '山地', '山区', '山岳', '高山', 'mountain', 'hill', 'peak', 
                        'highland', 'alps', '山峰', '山脉'],
            'grassland': ['草原', '草地', '牧场', '平原', 'grassland', 'meadow', 'prairie',
                         'plain', 'pasture', '草场', '原野'],
            'lake': ['湖', '湖泊', '湖边', 'lake', 'lakeside', '湖畔'],
            'river': ['河', '河流', '江', '溪', 'river', 'stream', 'creek', '小溪', '河边'],
            'park': ['公园', '园区', 'park', '市立公园', '休闲公园'],
            'japanese': ['日式', '日本风', '和风', 'japanese', 'zen', '禅意'],
            'chinese': ['中式', '中国风', '古典', 'chinese', 'traditional', '传统'],
            'tropical': ['热带', '雨林', 'tropical', 'rainforest', '热带雨林']
        }
        
        # 对象关键词（大幅扩展，包含更多变体和特定类型）
        self.object_keywords = {
            'tree': ['树', '大树', '树木', '乔木', 'tree', 'oak', 'pine', 'birch', 
                    '松树', '柏树', '樱花', '樱花树', '枫树', '柳树', '橡树', '竹子',
                    'cherry', 'maple', 'willow', 'bamboo', 'palm', '棕榈', '椰子树',
                    'cedar', 'spruce', 'fir', '杉树', '银杏'],
            'flower': ['花', '鲜花', '花朵', '花卉', 'flower', 'blossom', 'bloom', 
                      '玫瑰', '郁金香', '向日葵', '百合', '菊花', '牡丹', '兰花', '莲花',
                      'rose', 'tulip', 'sunflower', 'lily', 'chrysanthemum', 'peony',
                      'orchid', 'lotus', '野花', 'wildflower', '花丛', '花束'],
            'grass': ['草', '草地', '草坪', '草皮', 'grass', 'lawn', 'turf', 
                     '野草', '芳草', '绿草', '青草'],
            'stone': ['石头', '岩石', '石块', '巨石', 'stone', 'rock', 'boulder', 
                     'pebble', '卵石', '碎石', '石子', '石材', '岩层'],
            'water': ['水', '水体', '水面', 'water', '池塘', '湖', '河', '溪流',
                     'pond', 'lake', 'river', 'stream', '喷泉', 'fountain', 
                     '瀑布', 'waterfall', '小溪', 'creek', '泉水', 'spring'],
            'path': ['路', '小路', '道路', '小径', '步道', 'path', 'trail', 'walkway',
                    'pathway', 'road', '石板路', '林荫道', '人行道'],
            'building': ['建筑', '房子', '建筑物', '楼', '楼房', 'building', 'house', 
                        'structure', '房屋', '别墅', 'villa', '小屋', 'cottage', 
                        '高楼', 'skyscraper', '大厦', 'tower', '塔'],
            'bench': ['长椅', '座椅', '椅子', '长凳', 'bench', 'seat', '坐凳'],
            'lamp': ['灯', '路灯', '灯具', '灯笼', 'lamp', 'light', 'lantern', 
                    'streetlight', '照明', '灯光'],
            'fountain': ['喷泉', '水景', 'fountain', '喷水池'],
            'bridge': ['桥', '桥梁', 'bridge', '小桥', '拱桥', '木桥', '石桥'],
            'fence': ['栅栏', '围栏', '篱笆', 'fence', 'railing', '护栏', '栏杆'],
            'bush': ['灌木', '矮树', '树丛', 'bush', 'shrub', '灌木丛'],
            'hedge': ['树篱', '绿篱', 'hedge', '围篱'],
            'car': ['车', '汽车', '车辆', 'car', 'vehicle', 'automobile', '轿车'],
            'sky': ['天空', '天', 'sky', 'clouds', '云', '云层'],
            'sun': ['太阳', '日', 'sun', 'sunshine', '阳光', '日光'],
            'moon': ['月亮', '月', 'moon', '月光', 'moonlight'],
            'bird': ['鸟', '鸟类', 'bird', '飞鸟', '禽'],
            'butterfly': ['蝴蝶', 'butterfly', '蝶'],
            'statue': ['雕像', '雕塑', 'statue', 'sculpture', '塑像'],
            'pavilion': ['亭子', '凉亭', 'pavilion', 'gazebo', '亭'],
            'pergola': ['廊架', '花架', 'pergola', '藤架'],
            'deck': ['平台', '甲板', '露台', 'deck', 'terrace', 'patio']
        }
        
        # 风格关键词（扩展）
        self.style_keywords = {
            'cartoon': ['卡通', '可爱', '动画', 'cartoon', 'cute', 'kawaii', 'animated', 
                       'anime', '二次元', '萌'],
            'realistic': ['写实', '真实', '逼真', 'realistic', 'detailed', 'photorealistic',
                         'lifelike', 'natural', '照片级', '超写实'],
            'minimal': ['简约', '简单', '极简', 'minimal', 'clean', 'simple', 'minimalist',
                       '简洁', '素雅'],
            'natural': ['自然', '天然', 'natural', 'organic', '原生态', '野生'],
            'fantasy': ['奇幻', '幻想', '魔幻', 'fantasy', 'magical', 'mystical', 'fairy',
                       '童话', '仙境', 'fairytale'],
            'modern': ['现代', '当代', 'modern', 'contemporary', '摩登', '时尚'],
            'classical': ['古典', '经典', '传统', 'classical', 'classic', 'traditional',
                         '复古', 'vintage', 'retro', '古风'],
            'industrial': ['工业', '机械', 'industrial', 'mechanical', 'steampunk', 
                          '工业风'],
            'japanese': ['日式', '和风', '禅意', 'japanese', 'zen', '和式'],
            'chinese': ['中式', '中国风', 'chinese', '东方', 'oriental'],
            'european': ['欧式', '欧洲', 'european', '西式', 'western'],
            'futuristic': ['未来', '科幻', 'futuristic', 'sci-fi', 'cyberpunk', '赛博'],
        }
        
        # 🆕 季节关键词（增强：扩展winter相关关键词）
        self.season_keywords = {
            'spring': ['春天', '春季', '春日', 'spring', 'vernal'],
            'summer': ['夏天', '夏季', '夏日', 'summer'],
            'autumn': ['秋天', '秋季', '秋日', 'autumn', 'fall'],
            'winter': ['冬天', '冬季', '冬日', 'winter', 'wintery', 'wintry',
                      'snow', 'snowy', 'snow-dusted', 'snowdusted', 'snowed',
                      '雪', '雪花', '下雪', '雪地', '雪白', '积雪', '白雪',
                      'frost', 'frosty', 'frosted', 'frosting', '霜', '霜冻',
                      'ice', 'icy', 'iced', '冰', '冰冻', '结冰',
                      'frozen', 'freezing', 'freeze', '冰冻的']
        }
        
        # 情绪关键词（扩展）
        self.mood_keywords = {
            'peaceful': ['宁静', '平静', '安静', '祥和', 'peaceful', 'calm', 'serene', 
                        'tranquil', 'quiet', '静谧'],
            'vibrant': ['活力', '活跃', '生机', '朝气', 'vibrant', 'lively', 'energetic', 
                       'bright', 'dynamic', '充满活力'],
            'mysterious': ['神秘', '神奇', '魔幻', 'mysterious', 'magical', 'enchanted',
                          'mystic', '幽秘', '诡异'],
            'romantic': ['浪漫', '温馨', 'romantic', 'lovely', 'charming', 'sweet', 
                        '甜蜜', '唯美'],
            'wild': ['狂野', '野性', 'wild', 'untamed', 'savage', 'fierce', '原始'],
            'cozy': ['温馨', '舒适', '惬意', 'cozy', 'warm', 'comfortable', 'snug', 
                    '温暖', '舒服'],
            'dark': ['黑暗', '阴暗', '阴郁', 'dark', 'gloomy', 'dim', 'shadowy', 
                    '幽暗', '昏暗'],
            'elegant': ['优雅', '典雅', 'elegant', 'graceful', 'refined', '精致'],
            'dramatic': ['戏剧性', '壮观', 'dramatic', 'spectacular', 'striking', '震撼'],
            'melancholic': ['忧郁', '伤感', 'melancholic', 'sad', 'nostalgic', '怀旧'],
        }
        
        # 数量关键词（扩展）
        self.quantity_keywords = {
            'few': ['几个', '少量', '一些', '少数', 'few', 'some', 'several', 'a couple'],
            'many': ['许多', '很多', '大量', '众多', 'many', 'lots', 'numerous', 'plenty',
                    'abundant', '丰富'],
            'dense': ['密集', '茂密', '浓密', 'dense', 'thick', 'packed', 'crowded', 
                     '稠密'],
            'sparse': ['稀疏', '稀少', '零星', 'sparse', 'scattered', 'thin', 'sporadic',
                      '疏落'],
        }
        
        # 尺寸/形容词关键词（扩展）
        self.attribute_keywords = {
            'big': ['大', '大的', '巨大', '庞大', 'big', 'large', 'huge', 'giant', 
                   'massive', 'enormous', '宽大'],
            'small': ['小', '小的', '微小', '迷你', 'small', 'tiny', 'little', 'mini',
                     'miniature', '细小'],
            'tall': ['高', '高的', '高大', '高耸', 'tall', 'high', 'towering', '挺拔'],
            'short': ['矮', '低', '矮小', 'short', 'low', 'squat', '低矮'],
            'wide': ['宽', '宽阔', '开阔', 'wide', 'broad', 'expansive', '宽广'],
            'narrow': ['窄', '狭窄', 'narrow', 'thin', 'slim', '狭小'],
            'bright': ['明亮', '鲜艳', '明媚', 'bright', 'vivid', 'colorful', 'brilliant',
                      '亮丽', '灿烂'],
            'dark': ['暗', '暗淡', '昏暗', 'dark', 'dim', 'dull', 'murky', '阴沉'],
        }
        
        print("[OK] NLP parser initialized with text encoding")
    
    def parse(self, text):
        """
        解析自然语言输入（增强版）
        
        Args:
            text: 用户输入的自然语言文本
        
        Returns:
            解析结果字典
        """
        print(f"[PARSING] Input: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # 1. 基础文本处理
        text_lower = text.lower()
        
        # 2. 使用文本编码器提取语义特征
        print("   [PROCESSING] Extracting semantic features...")
        text_encoding, manual_features = self.text_encoder.encode(text)
        
        # 3. 规则方法提取结构化信息
        print("   [PROCESSING] Identifying scene elements...")
        scene_type = self._identify_scene_type(text_lower)
        objects = self._identify_objects(text_lower)
        styles = self._identify_styles(text_lower)
        moods = self._identify_moods(text_lower)
        seasons = self._identify_seasons(text_lower)  # 🆕 识别季节
        quantities = self._identify_quantities(text_lower)
        attributes = self._extract_attributes(text)
        
        # 4. 使用语义特征增强识别结果
        # 如果语义特征显示某些领域词汇，但规则方法没有识别到，进行补充
        objects = self._enhance_objects_with_semantics(objects, manual_features)
        
        # 5. 🆕 解析语义关系（成对关系和组间关系）
        semantic_relations = None
        if self.relation_parser:
            try:
                semantic_relations = self.relation_parser.parse_relations(text, objects)
                print(f"   [RELATIONS] Found {len(semantic_relations.get('pair_relations', []))} pair relations, "
                      f"{len(semantic_relations.get('group_relations', []))} group relations")
            except Exception as e:
                print(f"   [WARN] Relation parsing failed: {e}")
                semantic_relations = None
        
        # 6. 使用训练好的模型预测参数（如果可用）
        predicted_params = None
        if self.scene_predictor:
            try:
                predicted_params = self.scene_predictor.predict(text)
                print(f"   [TRAINED MODEL] Predicted tau={predicted_params.get('time_constant_tau', 0):.3f}, "
                      f"complexity={predicted_params.get('complexity_factor', 0):.3f}, "
                      f"naturalness={predicted_params.get('naturalness_score', 0):.3f}")
            except Exception as e:
                print(f"   [WARN] Prediction failed: {e}")
                predicted_params = None
        
        # 7. 计算置信度（基于多个因素）
        confidence = self._calculate_confidence(
            text, objects, styles, moods, manual_features
        )
        
        # 8. 组装结果
        result = {
            'original_text': text,
            'scene_type': scene_type,
            'objects': objects,
            'styles': styles,
            'moods': moods,
            'seasons': seasons,  # 🆕 季节信息
            'quantities': quantities,
            'attributes': attributes,
            
            # 🆕 语义关系
            'semantic_relations': semantic_relations,
            
            # 文本编码和特征
            'text_encoding': text_encoding,  # numpy array [encoding_dim]
            'manual_features': manual_features,  # 手工特征字典
            
            # 训练模型预测的参数（如果可用）
            'predicted_parameters': predicted_params,
            
            # 元数据
            'confidence': confidence,
            'parsing_method': f'{self.text_encoder.method}_with_rules' + ('_and_trained_model' if predicted_params else '') + ('_with_relations' if semantic_relations else ''),
            'encoding_method': self.text_encoder.method,
            'text_length': len(text),
            'word_count': manual_features.get('word_count', 0),
            'using_trained_model': predicted_params is not None,
            'has_spatial_relations': semantic_relations is not None and semantic_relations.get('has_spatial_constraints', False)
        }
        
        print(f"[OK] Parsing completed: scene={scene_type}, objects={len(objects)}, "
              f"styles={len(styles)}, seasons={seasons}, confidence={confidence:.2f}")
        
        return result
    
    def _identify_seasons(self, text_lower):
        """
        🆕 识别季节（增强版）
        支持多季节识别
        """
        found_seasons = []
        season_scores = {}
        
        for season, keywords in self.season_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword == text_lower:
                    score += 10
                elif f' {keyword} ' in f' {text_lower} ':
                    score += 5
                elif keyword in text_lower:
                    score += 2
            
            if score > 0:
                season_scores[season] = score
        
        # 返回所有匹配的季节（支持多季节）
        if season_scores:
            found_seasons = [season for season, score in season_scores.items() if score >= 2]
            found_seasons = sorted(found_seasons, key=lambda x: season_scores[x], reverse=True)
            
            if found_seasons:
                print(f"   识别到季节: {', '.join(found_seasons)}")
        
        return found_seasons
    
    def _enhance_objects_with_semantics(self, objects, manual_features):
        """
        使用语义特征增强对象识别
        如果某类对象在语义中有较高权重但未被规则识别，则添加
        """
        # 检查语义特征中的对象类别
        nature_count = manual_features.get('nature_count', 0)
        structure_count = manual_features.get('structure_count', 0)
        water_count = manual_features.get('water_features_count', 0)
        
        # 如果语义显示有自然元素，但对象列表太少，添加默认自然对象
        if nature_count > 0 and len(objects) < 3:
            default_nature = ['tree', 'grass', 'flower']
            for obj in default_nature:
                if obj not in objects:
                    objects.append(obj)
                    if len(objects) >= 3:
                        break
        
        # 如果语义显示有建筑结构，但没有识别到，添加
        if structure_count > 0 and 'building' not in objects and 'path' not in objects:
            objects.append('path')
        
        # 如果语义显示有水景，但没有识别到，添加
        if water_count > 0 and 'water' not in objects:
            objects.append('water')
        
        return objects
    
    def _calculate_confidence(self, text, objects, styles, moods, manual_features):
        """
        计算解析置信度
        基于多个因素综合评估
        """
        confidence = 0.5  # 基础置信度
        
        # 因素1: 文本长度（太短或太长都降低置信度）
        text_len = len(text)
        if 10 <= text_len <= 200:
            confidence += 0.1
        elif text_len < 5:
            confidence -= 0.2
        
        # 因素2: 识别到的元素数量
        total_elements = len(objects) + len(styles) + len(moods)
        if total_elements >= 3:
            confidence += 0.15
        elif total_elements >= 5:
            confidence += 0.2
        
        # 因素3: 语义特征的丰富程度
        semantic_richness = sum([
            manual_features.get('scene_count', 0) > 0,
            manual_features.get('nature_count', 0) > 0,
            manual_features.get('style_count', 0) > 0,
            manual_features.get('mood_count', 0) > 0
        ]) * 0.05
        confidence += semantic_richness
        
        # 因素4: 词汇多样性
        lexical_diversity = manual_features.get('lexical_diversity', 0)
        confidence += lexical_diversity * 0.1
        
        # 限制在0-1范围
        return max(0.0, min(1.0, confidence))
    
    def _identify_scene_type(self, text_lower):
        """
        识别场景类型（增强版）
        支持多种匹配策略，提高识别准确率
        """
        # 🆕 优先检查特殊场景类型（winter, desert等），避免误判
        # 检查winter相关关键词（高优先级）
        winter_keywords = ['winter', 'wintery', 'wintry', 'snow', 'snowy', 'snow-covered', 
                          'snowdusted', 'frost', 'frosty', 'ice', 'icy', 'frozen',
                          '冬天', '冬季', '雪地', '雪景', '雪', '霜', '冰', '冰冻']
        if any(kw in text_lower for kw in winter_keywords):
            print(f"   场景识别: winter (置信度: 10)")
            return 'winter'
        
        # 记录每个场景类型的匹配分数
        scene_scores = {}
        
        for scene_type, keywords in self.scene_keywords.items():
            # 跳过winter（已经优先处理）
            if scene_type == 'winter':
                continue
                
            score = 0
            for keyword in keywords:
                # 精确匹配（最高权重）
                if keyword == text_lower:
                    score += 10
                # 完整词匹配（高权重）
                elif f' {keyword} ' in f' {text_lower} ':
                    score += 5
                # 包含匹配（中权重）
                elif keyword in text_lower:
                    score += 2
                # 部分匹配（低权重） - 支持词干匹配
                elif len(keyword) > 3 and any(keyword[:3] in word for word in text_lower.split()):
                    score += 1
            
            if score > 0:
                scene_scores[scene_type] = score
        
        # 返回得分最高的场景类型
        if scene_scores:
            best_scene = max(scene_scores.items(), key=lambda x: x[1])
            print(f"   场景识别: {best_scene[0]} (置信度: {best_scene[1]})")
            return best_scene[0]
        
        # 默认场景
        return 'garden'
    
    def _identify_objects(self, text_lower):
        """
        识别对象（增强版）
        支持更智能的对象识别和相关性推断
        """
        found_objects = []
        object_scores = {}
        
        for obj_type, keywords in self.object_keywords.items():
            score = 0
            for keyword in keywords:
                # 精确匹配
                if keyword == text_lower:
                    score += 10
                # 完整词匹配
                elif f' {keyword} ' in f' {text_lower} ' or \
                     text_lower.startswith(keyword + ' ') or \
                     text_lower.endswith(' ' + keyword):
                    score += 5
                # 包含匹配
                elif keyword in text_lower:
                    score += 2
            
            if score > 0:
                object_scores[obj_type] = score
        
        # 按分数排序，取分数大于阈值的对象
        if object_scores:
            # 过滤低分对象（减少误报）
            threshold = 2
            found_objects = [obj for obj, score in object_scores.items() 
                           if score >= threshold]
            
            # 按分数排序（方便调试）
            found_objects = sorted(found_objects, 
                                 key=lambda x: object_scores[x], 
                                 reverse=True)
            
            print(f"   识别到对象: {len(found_objects)} 个")
            for obj in found_objects[:5]:  # 只打印前5个
                print(f"      - {obj} (分数: {object_scores[obj]})")
        
        # 如果没有识别到对象，根据场景类型提供默认对象
        if not found_objects:
            # 从文本中推断场景类型
            scene_type = self._identify_scene_type(text_lower)
            found_objects = self._get_default_objects_for_scene(scene_type)
            print(f"   使用默认对象: {found_objects}")
        
        return found_objects
    
    def _get_default_objects_for_scene(self, scene_type):
        """根据场景类型返回默认对象"""
        default_objects = {
            'garden': ['tree', 'flower', 'grass', 'path'],
            'forest': ['tree', 'grass', 'stone', 'bush'],
            'city': ['building', 'path', 'lamp'],
            'beach': ['water', 'stone', 'grass'],
            'mountain': ['tree', 'stone', 'grass'],
            'grassland': ['grass', 'flower', 'tree'],
            'lake': ['water', 'tree', 'grass'],
            'river': ['water', 'tree', 'stone'],
            'park': ['tree', 'grass', 'flower', 'bench', 'path'],
            'japanese': ['tree', 'stone', 'water', 'bridge'],
            'chinese': ['tree', 'pavilion', 'stone', 'water'],
        }
        return default_objects.get(scene_type, ['tree', 'grass'])
    
    def _identify_styles(self, text_lower):
        """
        识别风格（增强版）
        支持多风格混合识别
        """
        found_styles = []
        style_scores = {}
        
        for style, keywords in self.style_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword == text_lower:
                    score += 10
                elif f' {keyword} ' in f' {text_lower} ':
                    score += 5
                elif keyword in text_lower:
                    score += 2
            
            if score > 0:
                style_scores[style] = score
        
        # 返回所有匹配的风格（支持多风格）
        if style_scores:
            # 按分数排序，返回所有得分>=2的风格
            found_styles = [style for style, score in style_scores.items() if score >= 2]
            found_styles = sorted(found_styles, key=lambda x: style_scores[x], reverse=True)
            
            if found_styles:
                print(f"   识别到风格: {', '.join(found_styles)}")
        
        return found_styles
    
    def _identify_moods(self, text_lower):
        """
        识别情绪/氛围（增强版）
        支持多情绪识别
        """
        found_moods = []
        mood_scores = {}
        
        for mood, keywords in self.mood_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword == text_lower:
                    score += 10
                elif f' {keyword} ' in f' {text_lower} ':
                    score += 5
                elif keyword in text_lower:
                    score += 2
            
            if score > 0:
                mood_scores[mood] = score
        
        # 返回所有匹配的情绪（支持多情绪）
        if mood_scores:
            found_moods = [mood for mood, score in mood_scores.items() if score >= 2]
            found_moods = sorted(found_moods, key=lambda x: mood_scores[x], reverse=True)
            
            if found_moods:
                print(f"   识别到情绪: {', '.join(found_moods)}")
        
        return found_moods
    
    def _identify_quantities(self, text_lower):
        """识别数量描述"""
        quantities = {}
        for quantity_type, keywords in self.quantity_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    quantities['default'] = quantity_type
                    break
        
        # 提取具体数字
        numbers = re.findall(r'(\d+)\s*(?:个|棵|朵|块|座)?', text_lower)
        if numbers:
            quantities['specific_count'] = int(numbers[0])
        
        return quantities
    
    def _extract_attributes(self, text):
        """提取属性描述"""
        text_lower = text.lower()
        attributes = {
            'size': [],
            'color': [],
            'other': []
        }
        
        # 尺寸属性
        for attr_type, keywords in self.attribute_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if attr_type in ['big', 'small', 'tall', 'short', 'wide', 'narrow']:
                        if attr_type not in attributes['size']:
                            attributes['size'].append(attr_type)
                    elif attr_type in ['bright', 'dark']:
                        if attr_type not in attributes['color']:
                            attributes['color'].append(attr_type)
                    break
        
        # 颜色提取
        colors = ['红', '蓝', '绿', '黄', '紫', '橙', '粉', '白', '黑', '灰',
                 'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'white', 'black', 'gray']
        for color in colors:
            if color in text_lower:
                attributes['color'].append(color)
        
        return attributes


# 便捷函数
def create_nlp_parser(model_path=None):
    """创建NLP解析器实例"""
    use_pretrained = model_path is not None
    return NLPParser(
        use_pretrained_model=use_pretrained,
        model_path=model_path
    )

