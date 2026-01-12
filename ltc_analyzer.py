"""
AI场景生成器 - LTC分析模块
基于Liquid Time-Constant神经网络分析场景参数

作者: AI Team
版本: 1.0

LTC (Liquid Time-Constant) 网络特点:
- 连续时间神经网络
- 自适应时间常数
- 动态参数计算
"""

import math
import random

# ===========================================
# LTC分析模块
# ===========================================

class LTCAnalyzer:
    """LTC神经网络分析器"""

    def __init__(self, use_pretrained_model=True, model_path=None, device='cpu'):
        self.use_pretrained_model = use_pretrained_model
        self.model_path = model_path
        self.device = device  # 计算设备 ('cpu' or 'cuda')

        # 如果使用预训练模型，尝试加载
        if self.use_pretrained_model and self.model_path:
            try:
                self.load_pretrained_ltc_model()
                print("[OK] Pretrained LTC model loaded successfully")
            except Exception as e:
                print(f"[WARN] Pretrained LTC model loading failed, using rule-based method: {e}")
                self.use_pretrained_model = False

        # LTC网络参数（规则方法备用）
        self.base_time_constant = 1.5
        self.adaptation_rate = 0.1
        self.complexity_threshold = 0.7

        # 预训练模型相关
        self.ltc_model = None
        self.parameter_scaler = None
        
        # 对象特定的LTC参数映射（规则方法备用）
        self.object_ltc_params = {
            'tree': {
                'growth_rate': {'min': 0.5, 'max': 2.0, 'default': 1.0},
                'branching_factor': {'min': 0.3, 'max': 0.9, 'default': 0.6},
                'leaf_density': {'min': 0.4, 'max': 1.0, 'default': 0.8}
            },
            'flower': {
                'bloom_rate': {'min': 0.3, 'max': 1.5, 'default': 0.8},
                'color_variation': {'min': 0.2, 'max': 0.8, 'default': 0.5},
                'petal_count': {'min': 3, 'max': 12, 'default': 6}
            },
            'water': {
                'flow_rate': {'min': 0.1, 'max': 1.0, 'default': 0.3},
                'turbulence': {'min': 0.0, 'max': 0.7, 'default': 0.2},
                'depth_variation': {'min': 0.5, 'max': 2.0, 'default': 1.0}
            },
            'grass': {
                'height_variation': {'min': 0.3, 'max': 1.5, 'default': 0.8},
                'density_factor': {'min': 0.4, 'max': 1.2, 'default': 0.9},
                'wind_response': {'min': 0.1, 'max': 0.8, 'default': 0.4}
            },
            'stone': {
                'erosion_factor': {'min': 0.1, 'max': 0.6, 'default': 0.3},
                'texture_variation': {'min': 0.2, 'max': 0.9, 'default': 0.5},
                'size_distribution': {'min': 0.4, 'max': 1.0, 'default': 0.7}
            },
            'building': {
                'architectural_complexity': {'min': 0.3, 'max': 1.0, 'default': 0.6},
                'material_variation': {'min': 0.2, 'max': 0.8, 'default': 0.5},
                'structural_integrity': {'min': 0.7, 'max': 1.0, 'default': 0.9}
            }
        }

    def load_pretrained_ltc_model(self):
        """加载预训练LTC模型"""
        try:
            import joblib
            import os

            model_dir = os.path.dirname(self.model_path)

            # 尝试加载LTC模型文件
            model_files = ['ltc_model.pkl', 'ltc_model.joblib', 'ltc_network.pkl']
            for model_file in model_files:
                model_path = os.path.join(model_dir, model_file)
                if os.path.exists(model_path):
                    self.ltc_model = joblib.load(model_path)
                    print(f"[OK] Loaded LTC model: {model_path}")
                    break

            # 加载参数缩放器
            scaler_files = ['ltc_scaler.pkl', 'parameter_scaler.pkl']
            for scaler_file in scaler_files:
                scaler_path = os.path.join(model_dir, scaler_file)
                if os.path.exists(scaler_path):
                    self.parameter_scaler = joblib.load(scaler_path)
                    print(f"[OK] Loaded parameter scaler: {scaler_path}")
                    break

            if not self.ltc_model:
                raise FileNotFoundError("Pretrained LTC model files not found")

        except ImportError:
            print("[ERROR] Need to install joblib: pip install joblib")
            raise
        except Exception as e:
            print(f"[ERROR] Pretrained LTC model loading failed: {e}")
            raise

    def analyze(self, nlp_result):
        """
        使用LTC网络分析NLP结果
        
        优先级：
        1. 如果NLP结果包含训练模型预测的参数，直接使用
        2. 如果有预训练的LTC模型，使用模型分析
        3. 否则使用规则方法
        
        Args:
            nlp_result (dict): NLP解析结果
        
        Returns:
            dict: LTC分析结果
        """
        print("[ANALYZING] LTC network analysis started...")

        # 优先级1：使用训练模型预测的参数
        if nlp_result.get('predicted_parameters') and nlp_result.get('using_trained_model'):
            print("[TRAINED MODEL] Using parameters from trained predictor")
            return self._analyze_with_trained_params(nlp_result)

        # 优先级2：使用预训练模型
        if self.use_pretrained_model and self.ltc_model:
            return self._analyze_with_pretrained_model(nlp_result)

        # 优先级3：使用规则方法
        return self._analyze_with_rules(nlp_result)

    def _analyze_with_trained_params(self, nlp_result):
        """使用训练模型预测的参数"""
        predicted = nlp_result['predicted_parameters']
        
        # 构建LTC参数字典（包含所有必需的键）
        ltc_params = {
            'tau': predicted.get('time_constant_tau', 1.25),
            'complexity': predicted.get('complexity_factor', 0.5),
            'naturalness': predicted.get('naturalness_score', 0.7),
            'adaptation': predicted.get('adaptation_rate', 0.1),
            'dynamics': {
                'stability': 0.8,
                'variability': predicted.get('complexity_factor', 0.5),
                'continuity': predicted.get('naturalness_score', 0.7)
            }
        }
        
        # 使用LTC参数构建结果
        result = {
            'time_constant_tau': ltc_params['tau'],
            'complexity_factor': ltc_params['complexity'],
            'naturalness_score': ltc_params['naturalness'],
            'adaptation_rate': ltc_params['adaptation'],
            'analysis_method': 'trained_model',
            'model_type': predicted.get('model_type', 'unknown'),
            'nlp_result': nlp_result  # 🆕 将NLP结果包含在LTC结果中
        }
        
        # 计算场景和对象参数（传递包含dynamics的ltc_params）
        result['scene_parameters'] = self._compute_scene_parameters(nlp_result, ltc_params)
        result['object_parameters'] = self._compute_object_parameters(nlp_result, ltc_params)
        result['dynamic_coefficients'] = ltc_params['dynamics']
        
        print(f"[OK] Analysis completed with trained model: "
              f"tau={result['time_constant_tau']:.2f}, "
              f"complexity={result['complexity_factor']:.2f}, "
              f"naturalness={result['naturalness_score']:.2f}")
        
        return result
    
    def _analyze_with_pretrained_model(self, nlp_result):
        """使用预训练LTC模型分析"""
        try:
            print("[MODEL] Using pretrained LTC model for analysis")

            # 提取特征向量
            features = self._extract_ltc_features(nlp_result)

            # 使用模型预测
            predictions = self.ltc_model.predict(features)

            # 如果有缩放器，反缩放预测结果
            if self.parameter_scaler:
                predictions = self.parameter_scaler.inverse_transform(predictions)

            # 解析预测结果
            result = {
                'time_constant_tau': float(predictions[0][0]) if len(predictions[0]) > 0 else 1.5,
                'complexity_factor': float(predictions[0][1]) if len(predictions[0]) > 1 else 0.5,
                'naturalness_score': float(predictions[0][2]) if len(predictions[0]) > 2 else 0.7,
                'adaptation_rate': 0.1,
                'scene_parameters': {},
                'object_parameters': {},
                'dynamic_coefficients': {
                    'stability': 0.8,
                    'variability': 0.4,
                    'continuity': 0.9
                }
            }

            # 计算场景和对象参数
            result['scene_parameters'] = self._compute_scene_parameters(nlp_result, result)
            result['object_parameters'] = self._compute_object_parameters(nlp_result, result)
            result['nlp_result'] = nlp_result  # 🆕 将NLP结果包含在LTC结果中

            print(f"[OK] Pretrained LTC analysis completed: tau={result['time_constant_tau']:.2f}, complexity={result['complexity_factor']:.2f}")

            return result

        except Exception as e:
            print(f"[WARN] Pretrained LTC model analysis failed, fallback to rule-based method: {e}")
            return self._analyze_with_rules(nlp_result)
    
    def _extract_ltc_features(self, nlp_result):
        """提取LTC分析的特征向量"""
        import numpy as np

        # 构建特征向量
        features = []

        # 对象数量特征
        objects = nlp_result.get('objects', [])
        features.extend([
            len(objects),  # 总对象数
            1 if 'tree' in objects else 0,  # 是否有树
            1 if 'flower' in objects else 0,  # 是否有花
            1 if 'water' in objects else 0,  # 是否有水
            1 if 'building' in objects else 0,  # 是否有建筑
        ])

        # 场景类型特征
        scene_type = nlp_result.get('scene_type', 'garden')
        scene_features = [0] * 5  # 假设有5种场景类型
        scene_mapping = {'garden': 0, 'forest': 1, 'lake': 2, 'mountain': 3, 'beach': 4}
        if scene_type in scene_mapping:
            scene_features[scene_mapping[scene_type]] = 1
        features.extend(scene_features)

        # 情绪和风格特征
        styles = nlp_result.get('styles', [])
        moods = nlp_result.get('moods', [])
        features.extend([
            1 if 'natural' in styles else 0,
            1 if 'realistic' in styles else 0,
            1 if 'cartoon' in styles else 0,
            1 if 'peaceful' in moods else 0,
            1 if 'vibrant' in moods else 0,
        ])

        return np.array([features])

    def _analyze_with_rules(self, nlp_result):
        """使用规则方法分析"""
        print("[RULES] Using rule-based LTC analysis")

        # 初始化LTC参数
        ltc_params = self._initialize_ltc_parameters()

        # 基于NLP结果调整LTC参数
        ltc_params = self._adapt_ltc_parameters(ltc_params, nlp_result)

        # 计算场景级参数
        scene_params = self._compute_scene_parameters(nlp_result, ltc_params)

        # 计算对象级动态参数
        object_params = self._compute_object_parameters(nlp_result, ltc_params)
        
        # 🆕 处理语义关系映射
        spatial_dependencies = self._process_semantic_relations(nlp_result, ltc_params)

        result = {
            'time_constant_tau': ltc_params['tau'],
            'complexity_factor': ltc_params['complexity'],
            'naturalness_score': ltc_params['naturalness'],
            'adaptation_rate': ltc_params['adaptation'],
            'scene_parameters': scene_params,
            'object_parameters': object_params,
            'dynamic_coefficients': ltc_params['dynamics'],
            'analysis_method': 'rule_based',  # 添加分析方法标识
            'nlp_result': nlp_result,  # 🆕 将NLP结果包含在LTC结果中，供场景规划器使用
            'spatial_dependencies': spatial_dependencies  # 🆕 空间依赖关系
        }

        print(f"[OK] LTC analysis completed: tau={ltc_params['tau']:.2f}, complexity={ltc_params['complexity']:.2f}, naturalness={ltc_params['naturalness']:.2f}")

        return result

    def _initialize_ltc_parameters(self):
        """初始化LTC网络参数"""
        return {
            'tau': self.base_time_constant,  # 时间常数
            'complexity': 0.5,              # 复杂度因子
            'naturalness': 0.7,             # 自然度评分
            'adaptation': self.adaptation_rate,  # 自适应率
            'dynamics': {                   # 动态系数
                'stability': 0.8,
                'variability': 0.4,
                'continuity': 0.9
            }
        }

    def _adapt_ltc_parameters(self, ltc_params, nlp_result):
        """
        基于NLP结果自适应调整LTC参数
        这模拟了LTC网络的连续时间适应过程
        """
        # 基于对象数量调整复杂度
        object_count = len(nlp_result.get('objects', []))
        ltc_params['complexity'] = min(1.0, object_count * 0.15 + 0.3)

        # 基于场景类型调整时间常数
        scene_type = nlp_result.get('scene_type', 'garden')
        scene_tau_multipliers = {
            'garden': 1.2,    # 花园更静态
            'forest': 0.8,    # 森林更动态
            'lake': 1.5,      # 湖泊更平静
            'mountain': 0.6,  # 山脉更变化
            'beach': 1.0,     # 海滩平衡
            'meadow': 1.3,    # 草地宁静
            'river': 0.7      # 河流流动
        }
        tau_multiplier = scene_tau_multipliers.get(scene_type, 1.0)
        ltc_params['tau'] = self.base_time_constant * tau_multiplier

        # 基于风格调整自然度
        styles = nlp_result.get('styles', [])
        if 'natural' in styles or 'realistic' in styles:
            ltc_params['naturalness'] += 0.2
        if 'cartoon' in styles:
            ltc_params['naturalness'] -= 0.1
        if 'minimal' in styles:
            ltc_params['naturalness'] += 0.1

        ltc_params['naturalness'] = max(0.0, min(1.0, ltc_params['naturalness']))

        # 基于情绪调整动态系数
        moods = nlp_result.get('moods', [])
        if 'peaceful' in moods:
            ltc_params['dynamics']['stability'] += 0.2
            ltc_params['dynamics']['variability'] -= 0.1
        elif 'vibrant' in moods:
            ltc_params['dynamics']['stability'] -= 0.1
            ltc_params['dynamics']['variability'] += 0.2

        # 限制参数范围
        for key in ltc_params['dynamics']:
            ltc_params['dynamics'][key] = max(0.0, min(1.0, ltc_params['dynamics'][key]))

        return ltc_params

    def _compute_scene_parameters(self, nlp_result, ltc_params):
        """计算场景级参数"""
        scene_params = {
            'environmental_dynamics': {},
            'layout_dynamics': {},
            'lighting_dynamics': {},
            'temporal_evolution': {}
        }

        # 环境动态参数
        scene_params['environmental_dynamics'] = {
            'weather_stability': ltc_params['dynamics']['stability'],
            'seasonal_variation': ltc_params['dynamics']['variability'],
            'ecosystem_balance': ltc_params['naturalness'] * 0.8 + 0.2
        }

        # 布局动态参数
        scene_params['layout_dynamics'] = {
            'spatial_distribution': self._compute_spatial_distribution(ltc_params),
            'clustering_coefficient': ltc_params['complexity'] * 0.6 + 0.2,
            'flow_patterns': ltc_params['dynamics']['continuity']
        }

        # 光照动态参数
        time_of_day = nlp_result.get('attributes', {}).get('time', 'day')
        scene_params['lighting_dynamics'] = {
            'light_intensity_variation': self._compute_light_variation(time_of_day, ltc_params),
            'shadow_dynamics': ltc_params['dynamics']['variability'],
            'color_temperature_shift': ltc_params['tau'] / 2.0
        }

        # 时间演化参数
        scene_params['temporal_evolution'] = {
            'growth_cycles': ltc_params['tau'] * 10,  # 生长周期
            'seasonal_transitions': ltc_params['dynamics']['continuity'] * 100,
            'environmental_changes': ltc_params['dynamics']['variability'] * 50
        }

        return scene_params

    def _compute_object_parameters(self, nlp_result, ltc_params):
        """计算对象级动态参数"""
        object_params = {}

        objects = nlp_result.get('objects', [])

        for obj_type in objects:
            if obj_type in self.object_ltc_params:
                base_params = self.object_ltc_params[obj_type]

                # 使用LTC网络计算动态参数
                dynamic_params = {}
                for param_name, param_range in base_params.items():
                    # 基于LTC参数调整基础值
                    base_value = param_range['default']

                    # 复杂度影响
                    complexity_factor = (ltc_params['complexity'] - 0.5) * 0.4
                    adjusted_value = base_value * (1 + complexity_factor)

                    # 自然度影响
                    naturalness_factor = (ltc_params['naturalness'] - 0.5) * 0.3
                    adjusted_value *= (1 + naturalness_factor)

                    # 时间常数影响（模拟连续时间动态）
                    tau_factor = (ltc_params['tau'] - 1.5) * 0.2
                    adjusted_value *= (1 + tau_factor)

                    # 添加随机变异（基于variability）
                    variability = ltc_params['dynamics']['variability']
                    random_factor = random.uniform(-variability * 0.5, variability * 0.5)
                    final_value = adjusted_value * (1 + random_factor)

                    # 限制在有效范围内
                    final_value = max(param_range['min'], min(param_range['max'], final_value))

                    dynamic_params[param_name] = round(final_value, 3)

                object_params[obj_type] = dynamic_params

        return object_params

    def _compute_spatial_distribution(self, ltc_params):
        """计算空间分布参数"""
        # 基于LTC参数计算对象的空间分布特征
        stability = ltc_params['dynamics']['stability']
        variability = ltc_params['dynamics']['variability']

        # 计算分布类型
        if stability > 0.7:
            distribution_type = 'clustered'  # 聚集分布
            cluster_strength = stability * 0.8
        elif variability > 0.6:
            distribution_type = 'scattered'  # 散布分布
            cluster_strength = 1 - variability
        else:
            distribution_type = 'natural'  # 自然分布
            cluster_strength = 0.5 + variability * 0.3

        return {
            'type': distribution_type,
            'cluster_strength': round(cluster_strength, 3),
            'spacing_variation': round(variability * 0.6 + 0.2, 3),
            'boundary_effects': round(stability * 0.4 + 0.3, 3)
        }

    def _compute_light_variation(self, time_of_day, ltc_params):
        """计算光照变化参数"""
        base_variation = 0.3

        # 根据时间调整
        time_multipliers = {
            'morning': 0.8,
            'day': 1.0,
            'evening': 1.2,
            'night': 1.5
        }

        time_multiplier = time_multipliers.get(time_of_day, 1.0)

        # LTC参数影响
        stability = ltc_params['dynamics']['stability']
        variability = ltc_params['dynamics']['variability']

        final_variation = base_variation * time_multiplier * (1 + variability - stability * 0.5)

        return round(max(0.1, min(1.0, final_variation)), 3)
    
    def _process_semantic_relations(self, nlp_result, ltc_params):
        """
        🆕 处理语义关系，生成空间依赖映射
        
        Args:
            nlp_result: NLP解析结果（包含semantic_relations）
            ltc_params: LTC参数
        
        Returns:
            dict: 空间依赖关系映射
        """
        spatial_dependencies = {
            'pair_constraints': [],
            'group_constraints': [],
            'dependency_graph': {}
        }
        
        semantic_relations = nlp_result.get('semantic_relations')
        if not semantic_relations:
            return spatial_dependencies
        
        # 处理成对关系
        pair_relations = semantic_relations.get('pair_relations', [])
        for rel in pair_relations:
            constraint = {
                'type': rel['type'],
                'subject': rel['subject'],
                'object': rel['object'],
                'distance': rel['distance'],
                'confidence': rel['confidence'],
                'ltc_weight': ltc_params['naturalness']  # 自然度影响约束强度
            }
            spatial_dependencies['pair_constraints'].append(constraint)
            
            # 构建依赖图
            if rel['subject'] not in spatial_dependencies['dependency_graph']:
                spatial_dependencies['dependency_graph'][rel['subject']] = []
            spatial_dependencies['dependency_graph'][rel['subject']].append({
                'depends_on': rel['object'],
                'relation': rel['type'],
                'distance': rel['distance']
            })
        
        # 处理组间关系
        group_relations = semantic_relations.get('group_relations', [])
        for rel in group_relations:
            constraint = {
                'type': rel['type'],
                'group_type': rel['group_type'],
                'center_type': rel.get('center_type'),
                'radius': rel['radius'],
                'quantity': rel.get('quantity', 5),
                'confidence': rel['confidence'],
                'ltc_weight': ltc_params['complexity']  # 复杂度影响组关系
            }
            spatial_dependencies['group_constraints'].append(constraint)
        
        print(f"[SPATIAL] Processed {len(pair_relations)} pair constraints, {len(group_relations)} group constraints")
        
        return spatial_dependencies