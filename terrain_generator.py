"""
AI场景生成器 - 地形生成模块
基于用户JSON数据生成地形

作者: coco
版本: 1.0
"""

import json
import random
from pathlib import Path

# ===========================================
# 地形生成模块
# ===========================================

class TerrainGenerator:
    """地形生成器"""

    def __init__(self):
        # 加载用户的地形JSON数据
        self.terrains_data = self._load_terrains_data()

        # 语义参数到代码变量的映射
        self.semantic_mapping = self._load_semantic_mapping()

        # 地形类型定义
        self.terrain_types = self._load_terrain_types()

        # 通用地形参数 - 确保所有地形都有起伏
        self.universal_terrain_params = {
            'ASSET_ID': 'universal_terrain',
            'PLANE_SIZE': 50,
            'SUBDIVISIONS_COUNT': 5,
            'DISPLACEMENT_STRENGTH': 1.5,  # 增强位移强度
            'noise_scale': 1.0,
            'noise_detail': 15.0,
            'ramp_min': 0.3,  # 降低最小值以增强对比度
            'ramp_max': 0.7,  # 提高最大值以增强对比度
            'base_color': '(0.7, 0.6, 0.4, 1)',  # 默认沙地色
            'roughness_value': 0.8,
            'THICKNESS_ENABLED': False,  # 🆕 默认不启用厚度
            'THICKNESS': 0.0  # 🆕 默认厚度为0
        }


    def _load_terrains_data(self):
        """加载用户地形数据"""
        terrains_json_path = r"C:\Users\Lenovo\Desktop\terrains_metadata.json"
        try:
            with open(terrains_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 处理semantic_tags，将逗号分隔的标签转换为列表
            for terrain in data:
                if 'semantic_tags' in terrain and isinstance(terrain['semantic_tags'], str):
                    # 处理中英文逗号和分号
                    tags = terrain['semantic_tags'].replace('，', ',').replace(';', ',')
                    terrain['semantic_tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()]

            print(f"✅ 加载了 {len(data)} 个地形资源")
            return data

        except Exception as e:
            print(f"❌ 加载地形数据失败: {e}")
            return []

    def _load_semantic_mapping(self):
        """加载语义参数映射规则"""
        return {
            # 地形类型语义
            'erosion': {
                'primary_var': 'DISPLACEMENT_STRENGTH',
                'secondary_vars': ['noise_detail', 'ramp_min'],
                'range': [1.5, 4.0],  # 增强侵蚀强度
                'description': '地形侵蚀程度'
            },
            'yardang': {
                'primary_var': 'DISPLACEMENT_STRENGTH',
                'secondary_vars': ['noise_scale', 'ramp_min'],
                'range': [2.0, 5.0],  # 雅丹需要强起伏
                'description': '雅丹地貌特征'
            },
            'mountain': {
                'primary_var': 'MOUNTAIN_HEIGHT',
                'secondary_vars': ['ridge_sharpness', 'valley_depth'],
                'range': [5.0, 15.0],
                'description': '山脉高度'
            },
            'valley': {
                'primary_var': 'VALLEY_DEPTH',
                'secondary_vars': ['slope_gradient', 'river_bed_width'],
                'range': [2.0, 8.0],
                'description': '山谷深度'
            },
            'plateau': {
                'primary_var': 'PLATEAU_ELEVATION',
                'secondary_vars': ['edge_sharpness', 'surface_flatness'],
                'range': [3.0, 10.0],
                'description': '高原高度'
            },
            'canyon': {
                'primary_var': 'CANYON_DEPTH',
                'secondary_vars': ['wall_steepness', 'floor_width'],
                'range': [4.0, 12.0],
                'description': '峡谷深度'
            },
            'dune': {
                'primary_var': 'DUNE_HEIGHT',
                'secondary_vars': ['wave_frequency', 'sand_grain_size'],
                'range': [1.0, 6.0],
                'description': '沙丘高度'
            },
            'grass': {
                'primary_var': 'GRASS_DENSITY',
                'secondary_vars': ['blade_height', 'wind_sway'],
                'range': [0.5, 2.0],
                'description': '草地密度'
            },

            # 地表特征语义
            'rough': {
                'primary_var': 'DISPLACEMENT_STRENGTH',
                'secondary_vars': ['noise_detail', 'ramp_min'],
                'range': [2.5, 5.0],  # 极强粗糙地形起伏
                'description': '表面粗糙度'
            },
            'smooth': {
                'primary_var': 'DISPLACEMENT_STRENGTH',
                'secondary_vars': ['noise_detail', 'ramp_max'],
                'range': [0.8, 2.0],  # 平滑地形较弱起伏
                'description': '表面平滑度'
            },
            'rocky': {
                'primary_var': 'DISPLACEMENT_STRENGTH',
                'secondary_vars': ['noise_detail', 'ramp_min'],
                'range': [2.0, 4.0],  # 岩石地形强起伏
                'description': '岩石密度'
            },
            'sandy': {
                'primary_var': 'SAND_GRAIN_SIZE',
                'secondary_vars': ['dune_stability', 'wind_erosion'],
                'range': [0.1, 0.8],
                'description': '沙粒大小'
            },
            'coast': {
                'primary_var': 'COAST_LEVEL',
                'secondary_vars': ['wave_height', 'shore_smoothness'],
                'range': [0.0, 2.0],
                'description': '海岸线高度'
            },
            'beach': {
                'primary_var': 'BEACH_WIDTH',
                'secondary_vars': ['sand_softness', 'tide_range'],
                'range': [5.0, 20.0],
                'description': '海滩宽度'
            },
            'water': {
                'primary_var': 'WATER_DEPTH',
                'secondary_vars': ['current_strength', 'transparency'],
                'range': [1.0, 10.0],
                'description': '水体深度'
            },
            'cliff': {
                'primary_var': 'CLIFF_HEIGHT',
                'secondary_vars': ['face_steepness', 'crack_density'],
                'range': [3.0, 15.0],
                'description': '悬崖高度'
            },

            # 环境特征
            'wet': {
                'primary_var': 'MOISTURE_LEVEL',
                'secondary_vars': ['water_reflection', 'mud_viscosity'],
                'range': [0.4, 1.0],
                'description': '湿度水平'
            },
            'dry': {
                'primary_var': 'DRYNESS_FACTOR',
                'secondary_vars': ['crack_density', 'dust_amount'],
                'range': [0.0, 0.6],
                'description': '干燥程度'
            },
            'frozen': {
                'primary_var': 'ICE_COVERAGE',
                'secondary_vars': ['frost_crystal_size', 'snow_depth'],
                'range': [0.2, 1.0],
                'description': '冰雪覆盖'
            },
            'snow': {
                'primary_var': 'SNOW_DEPTH',
                'secondary_vars': ['snow_thickness', 'snow_roughness', 'snow_drift'],
                'range': [0.5, 3.0],  # 雪地厚度范围（单位）
                'description': '雪地厚度'
            },
            'snowy': {
                'primary_var': 'SNOW_DEPTH',
                'secondary_vars': ['snow_thickness', 'snow_roughness'],
                'range': [0.5, 3.0],
                'description': '雪地厚度'
            },

            # 规模特征
            'large': {
                'primary_var': 'TERRAIN_SCALE',
                'secondary_vars': ['feature_size_multiplier', 'detail_level'],
                'range': [1.5, 3.0],
                'description': '地形规模'
            },
            'small': {
                'primary_var': 'TERRAIN_SCALE',
                'secondary_vars': ['feature_size_multiplier', 'detail_level'],
                'range': [0.3, 0.8],
                'description': '地形规模'
            }
        }

    def _load_terrain_types(self):
        """加载地形类型定义"""
        return {
            'grassland': {
                'base_template': 'universal_terrain',
                'default_params': {
                    'ASSET_ID': 'terrain_grassland',
                    'DISPLACEMENT_STRENGTH': 1.2,  # 增强起伏
                    'PLANE_SIZE': 60,
                    'SUBDIVISIONS_COUNT': 5,
                    'noise_scale': 0.8,    # 适中的尺度
                    'noise_detail': 12.0,  # 较高细节
                    'ramp_min': 0.35,      # 增强对比度
                    'ramp_max': 0.65,
                    'base_color': '(0.2, 0.5, 0.1, 1)',  # 绿色草地
                    'roughness_value': 0.9
                },
                'semantic_weights': {
                    'grass': 1.0,
                    'smooth': 0.8,
                    'wet': 0.6
                }
            },
            'mountain': {
                'base_template': 'universal_terrain',
                'default_params': {
                    'ASSET_ID': 'terrain_mountain',
                    'DISPLACEMENT_STRENGTH': 3.5,  # 强起伏
                    'PLANE_SIZE': 80,
                    'SUBDIVISIONS_COUNT': 6,
                    'noise_scale': 0.3,    # 较大特征
                    'noise_detail': 8.0,   # 中等细节
                    'ramp_min': 0.25,      # 强对比度
                    'ramp_max': 0.75,
                    'base_color': '(0.4, 0.4, 0.4, 1)',  # 灰色岩石
                    'roughness_value': 0.95
                },
                'semantic_weights': {
                    'mountain': 1.0,
                    'rough': 0.9,
                    'large': 0.7
                }
            },
            'desert': {
                'base_template': 'universal_terrain',
                'default_params': {
                    'ASSET_ID': 'terrain_desert',
                    'DISPLACEMENT_STRENGTH': 2.0,  # 中等起伏
                    'PLANE_SIZE': 70,
                    'SUBDIVISIONS_COUNT': 5,
                    'noise_scale': 0.5,    # 沙丘尺度
                    'noise_detail': 10.0,  # 适中细节
                    'ramp_min': 0.4,       # 适中对比度
                    'ramp_max': 0.6,
                    'base_color': '(0.8, 0.7, 0.5, 1)',  # 沙色
                    'roughness_value': 0.7
                },
                'semantic_weights': {
                    'dune': 1.0,
                    'sandy': 0.9,
                    'dry': 0.8
                }
            },
            'canyon': {
                'base_template': 'universal_terrain',
                'default_params': {
                    'ASSET_ID': 'terrain_canyon',
                    'DISPLACEMENT_STRENGTH': 4.0,  # 极强起伏
                    'PLANE_SIZE': 75,
                    'SUBDIVISIONS_COUNT': 7,
                    'noise_scale': 0.2,    # 峡谷尺度
                    'noise_detail': 6.0,   # 较低细节
                    'ramp_min': 0.2,       # 极强对比度
                    'ramp_max': 0.8,
                    'base_color': '(0.6, 0.5, 0.4, 1)',  # 岩石色
                    'roughness_value': 0.98
                },
                'semantic_weights': {
                    'canyon': 1.0,
                    'rough': 0.8,
                    'dry': 0.6
                }
            },
            'rocky': {
                'base_template': 'universal_terrain',
                'default_params': {
                    'ASSET_ID': 'terrain_rocky',
                    'DISPLACEMENT_STRENGTH': 3.0,  # 高起伏
                    'PLANE_SIZE': 60,
                    'SUBDIVISIONS_COUNT': 6,
                    'noise_scale': 0.4,    # 岩石结构尺度
                    'noise_detail': 16.0,  # 极高细节，模拟裂纹
                    'ramp_min': 0.35,      # 强对比度
                    'ramp_max': 0.65,
                    'base_color': '(0.3, 0.3, 0.3, 1)',  # 深灰岩石
                    'roughness_value': 0.9
                },
                'semantic_weights': {
                    'rocky': 1.0,
                    'rough': 0.9,
                    'erosion': 0.7
                }
            },
            'snow': {
                'base_template': 'universal_terrain',
                'default_params': {
                    'ASSET_ID': 'terrain_snow',
                    'DISPLACEMENT_STRENGTH': 2.5,  # 中等起伏（雪地有自然起伏）
                    'PLANE_SIZE': 60,
                    'SUBDIVISIONS_COUNT': 6,
                    'noise_scale': 0.6,    # 雪地起伏尺度
                    'noise_detail': 10.0,  # 中等细节
                    'ramp_min': 0.4,       # 中等对比度
                    'ramp_max': 0.6,
                    'base_color': '(0.95, 0.95, 0.98, 1)',  # 雪白色
                    'roughness_value': 0.3,  # 雪地较光滑
                    'SNOW_DEPTH': 1.5,     # 🆕 雪地厚度（单位）
                    'SNOW_THICKNESS': 1.5,  # 🆕 雪层厚度
                    'SNOW_DRIFT': 0.3,      # 🆕 雪堆起伏
                    'THICKNESS_ENABLED': True  # 🆕 启用厚度模式
                },
                'semantic_weights': {
                    'snow': 1.0,
                    'snowy': 1.0,
                    'frozen': 0.8,
                    'smooth': 0.6
                }
            },
            'winter': {
                'base_template': 'universal_terrain',
                'default_params': {
                    'ASSET_ID': 'terrain_winter',
                    'DISPLACEMENT_STRENGTH': 2.8,  # 中等偏强起伏
                    'PLANE_SIZE': 60,
                    'SUBDIVISIONS_COUNT': 6,
                    'noise_scale': 0.5,
                    'noise_detail': 12.0,
                    'ramp_min': 0.35,
                    'ramp_max': 0.65,
                    'base_color': '(0.92, 0.94, 0.96, 1)',  # 冬季雪白色
                    'roughness_value': 0.4,
                    'SNOW_DEPTH': 2.0,     # 🆕 冬季雪地更厚
                    'SNOW_THICKNESS': 2.0,
                    'SNOW_DRIFT': 0.5,     # 🆕 冬季雪堆更明显
                    'THICKNESS_ENABLED': True
                },
                'semantic_weights': {
                    'winter': 1.0,
                    'snow': 0.9,
                    'snowy': 0.9,
                    'frozen': 0.7
                }
            }
        }

    def generate_terrain(self, semantic_params, ltc_params=None):
        """
        根据语义参数生成地形

        Args:
            semantic_params (dict): 语义参数
            ltc_params (dict): LTC分析结果

        Returns:
            dict: 地形生成结果
        """
        print("🏔️ 开始生成地形...")

        # 首先尝试从JSON中找到匹配的地形资源
        matching_terrain = self.find_matching_terrain(semantic_params)

        if matching_terrain:
            # 使用实际的地形资源
            result = self._generate_terrain_from_asset(matching_terrain, semantic_params, ltc_params)
        else:
            # 使用程序化生成作为后备
            result = self._generate_terrain_programmatic(semantic_params, ltc_params)

        print(f"✅ 地形生成完成: {result['terrain_type']}")
        return result

    def _generate_terrain_from_asset(self, terrain_asset, semantic_params, ltc_params=None):
        """从实际资产生成地形 - 增强：支持厚度参数"""
        terrain_type = terrain_asset['id']
        file_path = terrain_asset['file']
        asset_type = terrain_asset['type']
        
        # 🆕 检查是否需要添加厚度参数（基于语义标签）
        terrain_tags = terrain_asset.get('semantic_tags', [])
        has_snow = any('snow' in str(tag).lower() or '雪' in str(tag) for tag in terrain_tags)
        has_winter = any('winter' in str(tag).lower() or '冬天' in str(tag) or '冬季' in str(tag) for tag in terrain_tags)
        
        # 🆕 构建地形参数（包含厚度信息）
        terrain_params = {}
        if has_snow or has_winter:
            # 雪地/冬季地形需要厚度参数
            terrain_params = {
                'THICKNESS_ENABLED': True,
                'SNOW_DEPTH': 1.5 if has_snow else 2.0,
                'SNOW_THICKNESS': 1.5 if has_snow else 2.0,
                'SNOW_DRIFT': 0.3 if has_snow else 0.5,
                'DISPLACEMENT_STRENGTH': 2.5,  # 雪地有起伏
                'base_color': '(0.95, 0.95, 0.98, 1)' if has_snow else '(0.92, 0.94, 0.96, 1)'
            }
            
            # 根据语义参数调整厚度
            if 'snow' in semantic_params:
                snow_value = semantic_params.get('snow', 0.5)
                terrain_params['SNOW_DEPTH'] = 0.5 + snow_value * 2.5  # 0.5-3.0范围
                terrain_params['SNOW_THICKNESS'] = terrain_params['SNOW_DEPTH']

        result = {
            'terrain_type': terrain_type,
            'terrain_asset': terrain_asset,
            'terrain_params': terrain_params,  # 🆕 添加地形参数
            'metadata': {
                'source': 'asset',
                'file_path': file_path,
                'asset_type': asset_type,
                'semantic_params': semantic_params,
                'semantic_tags': terrain_tags,
                'has_thickness': has_snow or has_winter,  # 🆕 标记是否有厚度
                'thickness_value': terrain_params.get('SNOW_DEPTH', 0.0) if (has_snow or has_winter) else 0.0
            }
        }

        return result

    def _generate_terrain_programmatic(self, semantic_params, ltc_params=None):
        """程序化生成地形（后备方案）"""
        # 确定地形类型
        terrain_type = self._identify_terrain_type(semantic_params)
        
        # 🆕 如果识别为winter类型，强制设置雪地参数
        if terrain_type == 'winter':
            print("[TERRAIN] Applying winter terrain parameters (snow color)")
            # 确保semantic_params包含winter和snow
            if 'winter' not in semantic_params:
                semantic_params['winter'] = 1.0
            if 'snow' not in semantic_params:
                semantic_params['snow'] = 1.0

        # 计算地形参数
        terrain_params = self._compute_terrain_parameters(semantic_params, ltc_params, terrain_type)
        
        # 🆕 如果是winter类型，确保颜色是雪白色
        if terrain_type == 'winter':
            terrain_params['base_color'] = '(0.92, 0.94, 0.96, 1)'  # 冬季雪白色
            terrain_params['THICKNESS_ENABLED'] = True
            if 'SNOW_DEPTH' not in terrain_params:
                terrain_params['SNOW_DEPTH'] = 2.0
            if 'SNOW_THICKNESS' not in terrain_params:
                terrain_params['SNOW_THICKNESS'] = 2.0
            print(f"[TERRAIN] Winter terrain: color={terrain_params['base_color']}, thickness={terrain_params.get('SNOW_DEPTH', 0)}")

        result = {
            'terrain_type': terrain_type,
            'terrain_params': terrain_params,
            'metadata': {
                'source': 'procedural',
                'semantic_params': semantic_params,
                'ltc_influence': ltc_params is not None,
                'template_used': self.terrain_types[terrain_type]['base_template']
            }
        }

        return result

    def find_matching_terrain(self, semantic_tags):
        """根据语义标签查找匹配的地形资源"""
        if not semantic_tags or not self.terrains_data:
            return None

        # 计算每个地形资源的匹配度
        matches = []
        for terrain in self.terrains_data:
            terrain_tags = terrain.get('semantic_tags', [])
            if not terrain_tags:
                continue

            # 计算匹配分数
            match_score = 0
            for user_tag in semantic_tags.keys():
                for terrain_tag in terrain_tags:
                    # 支持中英文匹配
                    if user_tag.lower() in terrain_tag.lower() or terrain_tag.lower() in user_tag.lower():
                        match_score += semantic_tags[user_tag]
                        break

            if match_score > 0:
                matches.append((match_score, terrain))

        # 返回匹配度最高的地形
        if matches:
            matches.sort(key=lambda x: x[0], reverse=True)
            best_match = matches[0][1]
            print(f"🎯 找到匹配地形: {best_match['id']} (匹配度: {matches[0][0]:.2f})")
            return best_match

        return None

    def _identify_terrain_type(self, semantic_params):
        """识别地形类型"""
        # 🆕 优先检查winter和snow关键词（高优先级）
        semantic_text = ' '.join([str(k) + ' ' + str(v) for k, v in semantic_params.items()]).lower()
        
        # 检查是否有winter/snow相关关键词
        winter_keywords = ['winter', 'snow', 'snowy', 'frost', 'frosty', 'ice', 'frozen', 
                          '冬天', '冬季', '雪', '雪地', '霜', '冰', '冰冻']
        has_winter = any(kw in semantic_text for kw in winter_keywords)
        
        if has_winter:
            print(f"[TERRAIN] Detected winter/snow keywords, using winter terrain type")
            return 'winter'  # 直接返回winter类型
        
        # 计算每种地形类型的匹配度
        scores = {}

        for terrain_type, terrain_info in self.terrain_types.items():
            score = 0.0
            weights = terrain_info['semantic_weights']

            for semantic, weight in weights.items():
                if semantic in semantic_params:
                    score += weight * semantic_params[semantic]

            if score > 0:
                scores[terrain_type] = score

        if scores:
            # 返回得分最高的类型
            return max(scores, key=scores.get)

        return 'grassland'  # 默认类型

    def _compute_terrain_parameters(self, semantic_params, ltc_params, terrain_type):
        """计算地形参数"""
        # 起始参数基于地形类型
        base_params = self.terrain_types[terrain_type]['default_params'].copy()

        # 应用语义参数映射
        for semantic, value in semantic_params.items():
            if semantic in self.semantic_mapping:
                mapping = self.semantic_mapping[semantic]

                # 主变量
                primary_var = mapping['primary_var']
                if primary_var in base_params:
                    # 根据语义值调整参数
                    param_range = mapping['range']
                    normalized_value = (value - 0.0) / 1.0  # 假设语义值在0-1范围
                    adjusted_value = param_range[0] + normalized_value * (param_range[1] - param_range[0])
                    base_params[primary_var] = round(adjusted_value, 3)
                    
                    # 🆕 如果是SNOW_DEPTH，同时设置THICKNESS
                    if primary_var == 'SNOW_DEPTH':
                        base_params['THICKNESS'] = adjusted_value
                        base_params['THICKNESS_ENABLED'] = True

                # 次要变量
                for secondary_var in mapping['secondary_vars']:
                    if secondary_var in base_params:
                        # 次要变量调整较小
                        current_value = base_params[secondary_var]
                        adjustment = (value - 0.5) * 0.3  # 较小的调整
                        base_params[secondary_var] = round(current_value * (1 + adjustment), 3)
                    
                    # 🆕 处理snow_thickness等厚度相关参数
                    if secondary_var == 'snow_thickness' and 'THICKNESS' not in base_params:
                        base_params['THICKNESS'] = current_value * (1 + adjustment)
                        base_params['THICKNESS_ENABLED'] = True

        # 应用LTC参数影响
        if ltc_params:
            complexity = ltc_params.get('complexity_factor', 0.5)
            naturalness = ltc_params.get('naturalness_score', 0.7)

            # 复杂度影响细分次数和平面大小
            base_params['SUBDIVISIONS_COUNT'] = max(3, min(8, int(base_params['SUBDIVISIONS_COUNT'] * (0.8 + complexity * 0.4))))
            base_params['PLANE_SIZE'] = round(base_params['PLANE_SIZE'] * (0.9 + complexity * 0.2), 1)

            # 自然度影响位移强度
            base_params['DISPLACEMENT_STRENGTH'] = round(base_params['DISPLACEMENT_STRENGTH'] * (0.7 + naturalness * 0.6), 3)
            
            # 🆕 对于有厚度的地形（如雪地），根据复杂度调整厚度
            if base_params.get('THICKNESS_ENABLED', False):
                thickness_multiplier = 0.8 + complexity * 0.4  # 复杂度越高，厚度变化越大
                if 'THICKNESS' in base_params:
                    base_params['THICKNESS'] = round(base_params['THICKNESS'] * thickness_multiplier, 3)
                if 'SNOW_DEPTH' in base_params:
                    base_params['SNOW_DEPTH'] = round(base_params['SNOW_DEPTH'] * thickness_multiplier, 3)
                if 'SNOW_THICKNESS' in base_params:
                    base_params['SNOW_THICKNESS'] = round(base_params['SNOW_THICKNESS'] * thickness_multiplier, 3)
            
            # 🆕 检查用户输入中是否包含"dark green"或"深绿"关键词
            nlp_result = ltc_params.get('nlp_result', {})
            user_input = nlp_result.get('original_text', '').lower() if nlp_result else ''
            if not user_input:
                # 尝试从semantic_params中获取用户输入
                user_input = str(semantic_params.get('user_input', '')).lower()
            
            dark_green_keywords = ['dark green', 'darkgreen', '深绿', '深绿色', '墨绿', '墨绿色']
            has_dark_green = any(kw in user_input for kw in dark_green_keywords)
            
            if has_dark_green:
                # 设置深绿色地形颜色 (RGB: 0.1, 0.3, 0.05)
                base_params['base_color'] = '(0.1, 0.3, 0.05, 1)'
                print(f"[TERRAIN] Detected dark green keyword, setting terrain color to dark green")

        return base_params

    def get_available_terrain_types(self):
        """获取可用的地形类型"""
        return list(self.terrain_types.keys())

    def get_semantic_mapping_info(self):
        """获取语义映射信息"""
        return {
            semantic: {
                'description': info['description'],
                'primary_var': info['primary_var'],
                'range': info['range']
            }
            for semantic, info in self.semantic_mapping.items()
        }

