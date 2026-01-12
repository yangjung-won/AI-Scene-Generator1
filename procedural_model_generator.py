"""
AI场景生成器 - 程序化模型生成器
当模型库中不存在物体时，使用Blender API程序化生成复杂模型

作者: AI Team
版本: 1.0
"""

import math
import random
import numpy as np


class ProceduralModelGenerator:
    """
    程序化模型生成器
    使用Blender API生成复杂的3D模型（不是简单几何体）
    """
    
    def __init__(self):
        """初始化生成器"""
        self.generation_templates = self._load_generation_templates()
        print("[OK] Procedural model generator initialized")
    
    def _load_generation_templates(self):
        """加载生成模板配置"""
        return {
            'tree': {
                'type': 'complex_tree',
                'complexity': 'high',
                'methods': ['parametric_branches', 'leaf_clusters', 'bark_detail']
            },
            'flower': {
                'type': 'complex_flower',
                'complexity': 'medium',
                'methods': ['petal_layers', 'stamen_center', 'stem_detail']
            },
            'stone': {
                'type': 'complex_stone',
                'complexity': 'medium',
                'methods': ['organic_shape', 'surface_detail', 'erosion_pattern']
            },
            'building': {
                'type': 'complex_building',
                'complexity': 'high',
                'methods': ['architectural_elements', 'window_patterns', 'roof_structure']
            },
            'bush': {
                'type': 'complex_bush',
                'complexity': 'medium',
                'methods': ['foliage_clusters', 'branch_structure', 'natural_shape']
            },
            'water': {
                'type': 'complex_water',
                'complexity': 'low',
                'methods': ['surface_waves', 'depth_variation']
            },
            'path': {
                'type': 'complex_path',
                'complexity': 'low',
                'methods': ['stone_pattern', 'irregular_edges']
            },
            'grass': {
                'type': 'complex_grass',
                'complexity': 'low',
                'methods': ['blade_clusters', 'natural_distribution']
            }
        }
    
    def generate_model(self, object_type, attributes=None, ltc_params=None):
        """
        生成程序化模型
        
        Args:
            object_type: 对象类型 ('tree', 'flower', 'stone', etc.)
            attributes: 对象属性 {'size': 'large', 'color': 'red', ...}
            ltc_params: LTC参数（影响生成复杂度）
        
        Returns:
            dict: 生成配置，包含Blender操作指令
        """
        if object_type not in self.generation_templates:
            print(f"[WARN] No template for {object_type}, using default")
            return self._generate_default_model(object_type, attributes)
        
        template = self.generation_templates[object_type]
        complexity = ltc_params.get('complexity_factor', 0.5) if ltc_params else 0.5
        
        print(f"[GENERATING] Procedural {object_type} (complexity: {complexity:.2f})")
        
        # 根据类型生成
        if object_type == 'tree':
            return self._generate_complex_tree(attributes, complexity)
        elif object_type == 'flower':
            return self._generate_complex_flower(attributes, complexity)
        elif object_type == 'stone':
            return self._generate_complex_stone(attributes, complexity)
        elif object_type == 'building':
            return self._generate_complex_building(attributes, complexity)
        elif object_type == 'bush':
            return self._generate_complex_bush(attributes, complexity)
        elif object_type == 'water':
            return self._generate_complex_water(attributes, complexity)
        elif object_type == 'path':
            return self._generate_complex_path(attributes, complexity)
        elif object_type == 'grass':
            return self._generate_complex_grass(attributes, complexity)
        else:
            return self._generate_default_model(object_type, attributes)
    
    def _generate_complex_tree(self, attributes, complexity):
        """生成复杂的树模型"""
        size = attributes.get('size', 'medium') if attributes else 'medium'
        size_multiplier = {'small': 0.7, 'medium': 1.0, 'large': 1.5}.get(size, 1.0)
        
        # 基础参数
        trunk_height = 3.0 * size_multiplier * (0.8 + complexity * 0.4)
        trunk_radius = 0.3 * size_multiplier * (0.7 + complexity * 0.6)
        branch_count = int(8 + complexity * 12)
        leaf_density = 0.5 + complexity * 0.5
        
        return {
            'type': 'procedural_tree',
            'blender_operations': [
                {
                    'step': 'trunk',
                    'method': 'parametric_cylinder',
                    'params': {
                        'height': trunk_height,
                        'radius_base': trunk_radius,
                        'radius_top': trunk_radius * 0.6,
                        'segments': 8,
                        'taper': 0.3
                    }
                },
                {
                    'step': 'branches',
                    'method': 'recursive_branches',
                    'params': {
                        'count': branch_count,
                        'levels': 3,
                        'angle_variation': 30,
                        'length_factor': 0.6,
                        'thickness_decay': 0.7
                    }
                },
                {
                    'step': 'leaves',
                    'method': 'leaf_clusters',
                    'params': {
                        'density': leaf_density,
                        'cluster_count': branch_count * 2,
                        'leaf_size_variation': 0.3,
                        'natural_distribution': True
                    }
                },
                {
                    'step': 'bark_detail',
                    'method': 'displacement_texture',
                    'params': {
                        'strength': 0.1,
                        'scale': 5.0,
                        'detail': 8
                    }
                }
            ],
            'material': {
                'trunk': {'base_color': (0.4, 0.3, 0.2), 'roughness': 0.8},
                'leaves': {'base_color': (0.2, 0.5, 0.1), 'roughness': 0.6, 'transmission': 0.1}
            },
            'metadata': {
                'generation_method': 'procedural',
                'complexity': complexity,
                'size': size
            }
        }
    
    def _generate_complex_flower(self, attributes, complexity):
        """生成复杂的花模型"""
        petal_count = int(5 + complexity * 7)  # 5-12片花瓣
        petal_layers = 2 if complexity > 0.6 else 1
        
        return {
            'type': 'procedural_flower',
            'blender_operations': [
                {
                    'step': 'petals',
                    'method': 'layered_petals',
                    'params': {
                        'petal_count': petal_count,
                        'layers': petal_layers,
                        'petal_shape': 'organic',
                        'curvature': 0.5,
                        'size_variation': 0.2
                    }
                },
                {
                    'step': 'center',
                    'method': 'stamen_cluster',
                    'params': {
                        'stamen_count': int(8 + complexity * 12),
                        'anther_size': 0.1,
                        'filament_length': 0.3
                    }
                },
                {
                    'step': 'stem',
                    'method': 'curved_stem',
                    'params': {
                        'length': 0.5,
                        'thickness': 0.05,
                        'curvature': 0.2
                    }
                }
            ],
            'material': {
                'petals': {'base_color': (1.0, 0.8, 0.9), 'roughness': 0.3, 'subsurface': 0.2},
                'center': {'base_color': (1.0, 0.9, 0.2), 'roughness': 0.5}
            },
            'metadata': {
                'generation_method': 'procedural',
                'complexity': complexity
            }
        }
    
    def _generate_complex_stone(self, attributes, complexity):
        """生成复杂的石头模型"""
        return {
            'type': 'procedural_stone',
            'blender_operations': [
                {
                    'step': 'base_shape',
                    'method': 'organic_mesh',
                    'params': {
                        'subdivisions': int(3 + complexity * 3),
                        'noise_strength': 0.3,
                        'smooth_iterations': 2
                    }
                },
                {
                    'step': 'surface_detail',
                    'method': 'displacement_noise',
                    'params': {
                        'strength': 0.05,
                        'scale': 10.0,
                        'detail': int(5 + complexity * 5)
                    }
                },
                {
                    'step': 'erosion',
                    'method': 'erosion_pattern',
                    'params': {
                        'erosion_strength': complexity * 0.2,
                        'crack_density': complexity * 0.3
                    }
                }
            ],
            'material': {
                'base': {'base_color': (0.5, 0.5, 0.5), 'roughness': 0.9, 'metallic': 0.1}
            },
            'metadata': {
                'generation_method': 'procedural',
                'complexity': complexity
            }
        }
    
    def _generate_complex_building(self, attributes, complexity):
        """生成复杂的建筑模型（V4超级增强版 - 用户反馈太简单，大幅提升复杂度和美观度）"""
        # 🆕🆕 V4: 超大幅增加楼层数和尺寸（让建筑更壮观华丽）
        floors = int(8 + complexity * 16)  # 🆕🆕 V4: 8-24层（超大幅增加）
        windows_per_floor = int(10 + complexity * 15)  # 🆕🆕 V4: 10-25个窗户（更多窗户）
        
        # 🆕🆕 V4: 建筑风格随机化（增加更多高级风格）
        import random
        styles = ['modern', 'classical', 'victorian', 'industrial', 'art_deco', 'mediterranean', 'gothic', 'baroque', 
                  'renaissance', 'neoclassical', 'brutalist', 'futuristic', 'asian_temple', 'islamic', 'romanesque']  # 🆕🆕 V4: 新增7种风格
        style = random.choice(styles)
        
        # 🆕🆕 V4: 根据风格调整尺寸和比例（更大更美观，新增多种风格）
        if style == 'modern':
            width = 14.0 + complexity * 8.0  # 🆕🆕 V4: 现代风格更宽更壮观
            depth = 12.0 + complexity * 6.0
            floor_height = 4.0
        elif style == 'classical':
            width = 12.0 + complexity * 7.0  # 🆕🆕 V4: 增大尺寸
            depth = 12.0 + complexity * 7.0  # 古典风格更方正
            floor_height = 4.8  # 更高的楼层
        elif style == 'victorian':
            width = 11.0 + complexity * 6.0  # 🆕🆕 V4: 增大尺寸
            depth = 10.5 + complexity * 5.5
            floor_height = 4.5
        elif style == 'art_deco':
            width = 13.0 + complexity * 7.5  # 🆕🆕 V4: 增大尺寸
            depth = 11.5 + complexity * 6.0
            floor_height = 4.2
        elif style == 'mediterranean':
            width = 10.5 + complexity * 5.5  # 🆕🆕 V4: 增大尺寸
            depth = 10.0 + complexity * 5.0
            floor_height = 3.8
        elif style == 'gothic':
            width = 11.5 + complexity * 6.5  # 🆕🆕 V4: 增大尺寸
            depth = 11.0 + complexity * 6.0
            floor_height = 5.5  # 哥特式更高更壮观
        elif style == 'baroque':
            width = 13.5 + complexity * 8.0  # 🆕🆕 V4: 增大尺寸
            depth = 12.5 + complexity * 7.0
            floor_height = 5.2  # 巴洛克式高大华丽
        elif style == 'industrial':
            width = 15.0 + complexity * 9.0  # 🆕🆕 V4: 工业风格更大
            depth = 13.0 + complexity * 7.0
            floor_height = 5.5  # 更高的工业空间
        # 🆕🆕 V4: 新增风格的尺寸配置
        elif style == 'renaissance':
            width = 12.5 + complexity * 7.5
            depth = 12.0 + complexity * 7.0
            floor_height = 5.0  # 文艺复兴高大华丽
        elif style == 'neoclassical':
            width = 13.0 + complexity * 8.0
            depth = 12.5 + complexity * 7.5
            floor_height = 5.2  # 新古典主义宏伟
        elif style == 'brutalist':
            width = 16.0 + complexity * 10.0  # 野兽派粗犷巨大
            depth = 14.0 + complexity * 8.0
            floor_height = 4.5
        elif style == 'futuristic':
            width = 14.5 + complexity * 9.0  # 未来主义流线型
            depth = 13.0 + complexity * 7.5
            floor_height = 4.2
        elif style == 'asian_temple':
            width = 11.0 + complexity * 6.0  # 亚洲寺庙风格
            depth = 11.0 + complexity * 6.0  # 方正对称
            floor_height = 4.8
        elif style == 'islamic':
            width = 12.0 + complexity * 7.0  # 伊斯兰风格
            depth = 12.0 + complexity * 7.0  # 方正对称
            floor_height = 5.0
        else:  # romanesque
            width = 11.5 + complexity * 6.5  # 罗马式厚重
            depth = 11.0 + complexity * 6.0
            floor_height = 4.8
        
        return {
            'type': 'procedural_building',
            'blender_operations': [
                {
                    'step': 'structure',
                    'method': 'modular_floors',
                    'params': {
                        'floor_count': floors,
                        'floor_height': floor_height,
                        'width': width,
                        'depth': depth,
                        'style': style,  # 🆕 添加风格参数
                        'wall_thickness': 0.2  # 🆕 墙体厚度
                    }
                },
                {
                    'step': 'windows',
                    'method': 'window_pattern',
                    'params': {
                        'windows_per_floor': windows_per_floor,
                        'window_size': (2.0, 2.8),  # 🆕🆕🆕 V4: 超大窗户尺寸，更壮观美观
                        'frame_thickness': 0.28,  # 🆕🆕 V4: 增加窗框厚度
                        'pattern': self._get_window_pattern(style),  # 🆕🆕 V4: 更丰富的窗户样式系统
                        'window_depth': 0.35,  # 🆕🆕🆕 V4: 大幅增加窗户深度（嵌入墙体更深，更立体）
                        'has_sills': True,  # 🆕 窗台
                        'sill_depth': 0.28,  # 🆕🆕 V4: 更深的窗台
                        'sill_height': 0.20,  # 🆕🆕 V4: 更高的窗台
                        'has_architrave': style in ['classical', 'victorian', 'art_deco', 'baroque', 'renaissance', 'neoclassical', 'romanesque'],  # 🆕🆕 V4: 更多风格有装饰框
                        'architrave_width': 0.40,  # 🆕🆕 V4: 更宽的装饰框
                        'architrave_depth': 0.22,  # 🆕🆕 V4: 更深的装饰框
                        'architrave_style': 'ornate' if style in ['baroque', 'renaissance'] else 'simple',  # 🆕🆕 V4: 装饰框风格
                        'has_lintels': True,  # 🆕 窗楣
                        'lintel_depth': 0.22,  # 🆕🆕 V4: 更深的窗楣
                        'lintel_height': 0.28,  # 🆕🆕 V4: 更高的窗楣
                        'lintel_style': 'carved' if style in ['baroque', 'victorian', 'renaissance'] else 'plain',  # 🆕🆕 V4: 窗楣雕刻
                        'has_glass_panes': True,  # 🆕🆕 V3: 玻璃窗格分割
                        'pane_divisions': 6 if style in ['victorian', 'classical', 'renaissance'] else (3 if style in ['art_deco', 'neoclassical'] else 2),  # 🆕🆕 V4: 更多窗格分割
                        'has_shutters': style in ['mediterranean', 'victorian', 'renaissance', 'romanesque'],  # 🆕🆕 V4: 更多风格有百叶窗
                        'shutter_style': 'louvered' if style == 'mediterranean' else 'panel',
                        'has_window_boxes': style in ['victorian', 'mediterranean', 'renaissance'],  # 🆕🆕 V4: 窗台花箱
                        'has_stained_glass': style in ['gothic', 'romanesque', 'islamic'],  # 🆕🆕 V4: 彩色玻璃
                        'has_mullions': style in ['gothic', 'tudor', 'victorian'],  # 🆕🆕 V4: 窗棂
                        'mullion_pattern': 'tracery' if style == 'gothic' else 'grid'
                    }
                },
                # 🆕🆕🆕 V4: 超级增强阳台细节（让建筑更立体华丽好看）
                {
                    'step': 'balconies',
                    'method': 'add_balconies',
                    'params': {
                        'enabled': complexity > 0.2,  # 🆕🆕 V4: 进一步降低阈值，几乎所有建筑都有阳台
                        'balcony_depth': 2.5,  # 🆕🆕🆕 V4: 大幅增加阳台深度
                        'balcony_width': 5.5,  # 🆕🆕🆕 V4: 大幅增加阳台宽度
                        'railing_height': 1.3,  # 🆕🆕 V4: 更高的栏杆
                        'railing_style': self._get_railing_style(style),  # 🆕🆕 V4: 更丰富的栏杆风格系统
                        'railing_thickness': 0.10,  # 🆕🆕 V4: 更粗的栏杆
                        'railing_posts': True,  # 🆕 栏杆柱子
                        'post_spacing': 0.7,  # 🆕🆕 V4: 更密集的柱子
                        'post_style': 'carved' if style in ['baroque', 'renaissance', 'victorian'] else 'simple',  # 🆕🆕 V4: 雕刻柱子
                        'has_columns': style in ['classical', 'mediterranean', 'baroque', 'renaissance', 'neoclassical'],  # 🆕🆕 V4: 更多风格有柱子
                        'column_style': self._get_column_style(style),  # 🆕🆕 V4: 柱式系统
                        'column_count': 3 if style in ['baroque', 'renaissance'] else 2,  # 🆕🆕 V4: 更多柱子
                        'has_brackets': style in ['victorian', 'art_deco', 'renaissance', 'baroque'],  # 🆕🆕 V4: 更多托架
                        'bracket_style': 'ornate' if style in ['baroque', 'renaissance'] else 'simple',
                        'bracket_count': 4,  # 🆕🆕 V4: 更多托架
                        'has_floor_tiles': True,  # 🆕🆕 V3: 阳台地板瓷砖
                        'tile_pattern': self._get_tile_pattern(style),  # 🆕🆕 V4: 瓷砖图案系统
                        'has_planters': style in ['mediterranean', 'modern', 'victorian'],  # 🆕🆕 V4: 花盆
                        'planter_count': 4,
                        'has_awning': style in ['mediterranean', 'modern'],  # 🆕🆕 V4: 遮阳篷
                        'awning_style': 'striped' if style == 'mediterranean' else 'solid',
                        'has_lighting': complexity > 0.6,  # 🆕🆕 V4: 阳台照明
                        'floors_with_balconies': [i for i in range(2, floors) if i % 2 == 0 or (style in ['mediterranean', 'modern', 'futuristic'] and i > floors // 3)]  # 🆕🆕 V4: 更多楼层有阳台
                    }
                },
                # 🆕 添加入口和门廊 - 增强版
                {
                    'step': 'entrance',
                    'method': 'add_entrance',
                    'params': {
                        'door_width': 1.4,  # 🆕 更宽的门
                        'door_height': 2.6,  # 🆕 更高的门
                        'door_style': 'double' if style in ['classical', 'victorian', 'mediterranean'] else 'single',  # 🆕 双开门
                        'has_portico': style in ['classical', 'victorian', 'mediterranean'],  # 门廊
                        'portico_depth': 2.0,  # 🆕 更深的门廊
                        'portico_width': 3.5,  # 🆕 更宽的门廊
                        'has_columns': style in ['classical', 'mediterranean'],  # 🆕 门廊柱子
                        'column_count': 2 if style == 'classical' else 0,
                        'column_style': 'ionic' if style == 'classical' else 'simple',
                        'has_pediment': style == 'classical',  # 🆕 三角楣饰
                        'has_steps': True,
                        'step_count': 4,  # 🆕 更多台阶
                        'step_width': 4.0,  # 🆕 更宽的台阶
                        'has_handrails': True  # 🆕 扶手
                    }
                },
                # 🆕🆕🆕 V4: 超级增强装饰元素（让建筑更华丽精致）
                {
                    'step': 'decorations',
                    'method': 'add_decorative_elements',
                    'params': {
                        'has_cornice': True,  # 檐口
                        'cornice_depth': 0.6,  # 🆕🆕 V4: 更深的檐口
                        'cornice_height': 0.4,  # 🆕🆕 V4: 更高的檐口
                        'cornice_style': self._get_cornice_style(style),  # 🆕🆕 V4: 檐口风格系统
                        'has_pilasters': style in ['classical', 'victorian', 'art_deco', 'renaissance', 'neoclassical', 'baroque'],  # 🆕🆕 V4: 更多风格有壁柱
                        'pilaster_width': 0.7,  # 🆕🆕 V4: 更宽的壁柱
                        'pilaster_depth': 0.25,  # 🆕🆕 V4: 壁柱突出深度
                        'pilaster_count': windows_per_floor + 1,  # 🆕 在窗户之间添加壁柱
                        'pilaster_style': self._get_column_style(style),  # 🆕🆕 V4: 壁柱使用柱式
                        'has_string_course': complexity > 0.3,  # 🆕🆕 V4: 进一步降低阈值，更多建筑有腰线
                        'string_course_floors': [i for i in range(1, floors) if i % 2 == 1 or (style in ['renaissance', 'baroque'] and i % 3 == 0)],  # 🆕🆕 V4: 更多层腰线
                        'string_course_depth': 0.20,  # 🆕🆕 V4: 更深的腰线
                        'string_course_height': 0.15,  # 🆕🆕 V4: 更高的腰线
                        'has_quoins': style in ['classical', 'victorian', 'renaissance', 'neoclassical', 'romanesque'],  # 🆕🆕 V4: 更多风格有角石
                        'quoin_size': 0.4,  # 🆕🆕 V4: 更大的角石
                        'quoin_depth': 0.15,  # 🆕🆕 V4: 角石突出深度
                        'has_frieze': style in ['classical', 'art_deco', 'renaissance', 'neoclassical'],  # 🆕🆕 V4: 更多风格有檐壁
                        'frieze_height': 0.7,  # 🆕🆕 V4: 更高的檐壁
                        'frieze_style': 'carved' if style in ['renaissance', 'baroque'] else 'plain',  # 🆕🆕 V4: 雕刻檐壁
                        'has_rustication': style in ['classical', 'renaissance', 'neoclassical'],  # 🆕🆕 V4: 更多风格有粗琢石
                        'rustication_floors': [0, 1] if complexity > 0.7 else [0],  # 🆕🆕 V4: 多层粗琢石
                        'rustication_depth': 0.12,  # 🆕🆕 V4: 粗琢石深度
                        'has_medallions': style in ['victorian', 'art_deco', 'baroque', 'renaissance'],  # 🆕🆕 V4: 更多风格有装饰章
                        'medallion_count': 4 if style in ['baroque', 'renaissance'] else 2,  # 🆕🆕 V4: 更多装饰章
                        'medallion_size': 0.8,  # 🆕🆕 V4: 更大的装饰章
                        'has_pediments': style in ['classical', 'neoclassical', 'renaissance'],  # 🆕🆕 V4: 三角楣饰
                        'pediment_locations': ['top', 'entrance'],
                        'has_dentils': style in ['classical', 'neoclassical', 'georgian'],  # 🆕🆕 V4: 齿饰
                        'dentil_size': 0.08,
                        'has_modillions': style in ['baroque', 'renaissance'],  # 🆕🆕 V4: 托臂装饰
                        'modillion_spacing': 0.6,
                        'has_spandrels': style in ['gothic', 'art_deco'],  # 🆕🆕 V4: 拱肩装饰
                        'has_finials': style in ['gothic', 'victorian', 'asian_temple'],  # 🆕🆕 V4: 顶饰
                        'finial_count': 4,
                        'has_gargoyles': style == 'gothic',  # 🆕🆕 V4: 滴水兽
                        'gargoyle_count': 2
                    }
                },
                {
                    'step': 'roof',
                    'method': 'pitched_roof',
                    'params': {
                        'angle': 35 if style in ['classical', 'victorian'] else 25,  # 🆕 根据风格调整角度
                        'overhang': 0.7,  # 🆕 增加悬挑
                        'detail_level': int(3 + complexity * 4),  # 🆕 更多细节
                        'has_dormers': style == 'victorian',  # 🆕 老虎窗（维多利亚风格）
                        'dormer_count': 2 if style == 'victorian' else 0,
                        'has_chimneys': style in ['classical', 'victorian'],  # 🆕 烟囱
                        'chimney_count': 1 if style in ['classical', 'victorian'] else 0
                    }
                },
                # 🆕 添加细节装饰
                {
                    'step': 'details',
                    'method': 'architectural_details',
                    'params': {
                        'cornice': True,
                        'door': True,
                        'balcony': complexity > 0.6,
                        'has_window_shutters': style == 'victorian',  # 🆕 百叶窗
                        'has_awnings': style == 'modern' and complexity > 0.7,  # 🆕 遮阳篷
                        'has_facade_texture': True,  # 🆕 立面纹理
                        'texture_type': 'brick' if style in ['classical', 'industrial'] else 'plaster'
                    }
                }
            ],
            'material': {
                # 🆕 根据风格调整材质
                'walls': {
                    'base_color': (0.85, 0.82, 0.75) if style in ['classical', 'victorian'] else (0.75, 0.75, 0.72),
                    'roughness': 0.8 if style in ['classical', 'industrial'] else 0.6,
                    'metallic': 0.0,
                    'normal_strength': 0.5  # 🆕 法线贴图强度（砖纹理）
                },
                'windows': {
                    'base_color': (0.5, 0.6, 0.8),
                    'roughness': 0.05,  # 🆕 更光滑的玻璃
                    'transmission': 0.95,  # 🆕 更高透明度
                    'ior': 1.45  # 🆕 玻璃折射率
                },
                'window_frames': {  # 🆕 窗框单独材质
                    'base_color': (0.3, 0.3, 0.3),
                    'roughness': 0.4,
                    'metallic': 0.2
                },
                'roof': {
                    'base_color': (0.35, 0.25, 0.15) if style in ['classical', 'victorian'] else (0.3, 0.3, 0.35),
                    'roughness': 0.85,
                    'metallic': 0.0
                },
                'door': {  # 🆕 门的材质
                    'base_color': (0.4, 0.25, 0.15),
                    'roughness': 0.5,
                    'metallic': 0.0
                },
                'decorations': {  # 🆕 装饰元素材质
                    'base_color': (0.9, 0.88, 0.85),
                    'roughness': 0.7,
                    'metallic': 0.0
                }
            },
            'metadata': {
                'generation_method': 'procedural',
                'complexity': complexity,
                'style': style,  # 🆕 记录风格
                'floors': floors,
                'dimensions': {'width': width, 'depth': depth, 'height': floors * floor_height}
            }
        }
    
    def _generate_complex_bush(self, attributes, complexity):
        """生成复杂的灌木模型"""
        cluster_count = int(5 + complexity * 10)
        
        return {
            'type': 'procedural_bush',
            'blender_operations': [
                {
                    'step': 'foliage',
                    'method': 'foliage_clusters',
                    'params': {
                        'cluster_count': cluster_count,
                        'cluster_size': 0.3,
                        'density': 0.6 + complexity * 0.4,
                        'natural_distribution': True
                    }
                },
                {
                    'step': 'branches',
                    'method': 'hidden_branches',
                    'params': {
                        'branch_count': cluster_count // 2,
                        'thickness': 0.05
                    }
                }
            ],
            'material': {
                'foliage': {'base_color': (0.2, 0.4, 0.1), 'roughness': 0.6}
            },
            'metadata': {
                'generation_method': 'procedural',
                'complexity': complexity
            }
        }
    
    def _generate_complex_water(self, attributes, complexity):
        """生成复杂的水体模型"""
        return {
            'type': 'procedural_water',
            'blender_operations': [
                {
                    'step': 'surface',
                    'method': 'wave_surface',
                    'params': {
                        'wave_amplitude': 0.1,
                        'wave_frequency': 2.0,
                        'turbulence': complexity * 0.3,
                        'subdivisions': int(4 + complexity * 4)
                    }
                },
                {
                    'step': 'depth',
                    'method': 'depth_variation',
                    'params': {
                        'max_depth': 1.0,
                        'variation': complexity * 0.5
                    }
                }
            ],
            'material': {
                'water': {
                    'base_color': (0.1, 0.3, 0.5),
                    'roughness': 0.0,
                    'transmission': 1.0,
                    'ior': 1.33,
                    'subsurface': 0.1
                }
            },
            'metadata': {
                'generation_method': 'procedural',
                'complexity': complexity
            }
        }
    
    def _generate_complex_path(self, attributes, complexity):
        """生成复杂的路径模型"""
        return {
            'type': 'procedural_path',
            'blender_operations': [
                {
                    'step': 'base',
                    'method': 'irregular_path',
                    'params': {
                        'width': 1.5,
                        'length': 10.0,
                        'curvature': 0.3,
                        'subdivisions': int(3 + complexity * 3)
                    }
                },
                {
                    'step': 'stones',
                    'method': 'stone_pattern',
                    'params': {
                        'stone_count': int(20 + complexity * 30),
                        'stone_size_variation': 0.4,
                        'irregular_placement': True
                    }
                }
            ],
            'material': {
                'path': {'base_color': (0.6, 0.5, 0.4), 'roughness': 0.8}
            },
            'metadata': {
                'generation_method': 'procedural',
                'complexity': complexity
            }
        }
    
    def _generate_complex_grass(self, attributes, complexity):
        """生成复杂的草模型"""
        blade_count = int(50 + complexity * 100)
        
        return {
            'type': 'procedural_grass',
            'blender_operations': [
                {
                    'step': 'blades',
                    'method': 'grass_blade_cluster',
                    'params': {
                        'blade_count': blade_count,
                        'height_variation': 0.3,
                        'width_variation': 0.2,
                        'natural_distribution': True,
                        'wind_effect': complexity * 0.3
                    }
                }
            ],
            'material': {
                'grass': {'base_color': (0.2, 0.5, 0.1), 'roughness': 0.7}
            },
            'metadata': {
                'generation_method': 'procedural',
                'complexity': complexity
            }
        }
    
    def _generate_default_model(self, object_type, attributes):
        """生成默认模型（当没有模板时）"""
        return {
            'type': f'procedural_{object_type}',
            'blender_operations': [
                {
                    'step': 'base',
                    'method': 'organic_mesh',
                    'params': {
                        'subdivisions': 3,
                        'noise_strength': 0.2
                    }
                }
            ],
            'material': {
                'base': {'base_color': (0.5, 0.5, 0.5), 'roughness': 0.7}
            },
            'metadata': {
                'generation_method': 'procedural',
                'complexity': 0.5
            }
        }
    
    def get_generation_instructions(self, model_config):
        """
        获取Blender生成指令（供Blender插件使用）
        
        Args:
            model_config: 模型生成配置
        
        Returns:
            list: Blender操作指令列表
        """
        return model_config.get('blender_operations', [])
    
    def can_generate(self, object_type):
        """检查是否可以生成指定类型的模型"""
        return object_type in self.generation_templates or object_type in [
            'tree', 'flower', 'stone', 'building', 'bush', 'water', 'path', 'grass'
        ]
    
    # 🆕🆕 V4: 辅助方法 - 建筑风格系统
    def _get_window_pattern(self, style):
        """根据风格获取窗户图案"""
        patterns = {
            'modern': 'grid',
            'classical': 'arched',
            'victorian': 'bay',
            'industrial': 'grid',
            'art_deco': 'geometric',
            'mediterranean': 'arched',
            'gothic': 'pointed_arch',
            'baroque': 'ornate_arch',
            'renaissance': 'arched',
            'neoclassical': 'arched',
            'brutalist': 'rectangular',
            'futuristic': 'curved',
            'asian_temple': 'lattice',
            'islamic': 'horseshoe_arch',
            'romanesque': 'round_arch'
        }
        return patterns.get(style, 'grid')
    
    def _get_railing_style(self, style):
        """根据风格获取栏杆样式"""
        styles_map = {
            'modern': 'glass',
            'classical': 'ornate',
            'victorian': 'cast_iron',
            'industrial': 'metal_bars',
            'art_deco': 'geometric',
            'mediterranean': 'wrought_iron',
            'gothic': 'tracery',
            'baroque': 'ornate_carved',
            'renaissance': 'balustrade',
            'neoclassical': 'balustrade',
            'brutalist': 'concrete',
            'futuristic': 'transparent',
            'asian_temple': 'wooden_lattice',
            'islamic': 'geometric_pattern',
            'romanesque': 'stone_balustrade'
        }
        return styles_map.get(style, 'modern')
    
    def _get_column_style(self, style):
        """根据风格获取柱式"""
        column_styles = {
            'classical': 'corinthian',
            'victorian': 'composite',
            'baroque': 'twisted',
            'renaissance': 'ionic',
            'neoclassical': 'doric',
            'mediterranean': 'tuscan',
            'romanesque': 'romanesque',
            'gothic': 'clustered',
            'islamic': 'moorish',
            'asian_temple': 'pagoda'
        }
        return column_styles.get(style, 'simple')
    
    def _get_tile_pattern(self, style):
        """根据风格获取瓷砖图案"""
        patterns = {
            'mediterranean': 'mosaic',
            'islamic': 'zellige',
            'victorian': 'checkerboard',
            'art_deco': 'geometric',
            'asian_temple': 'tatami',
            'modern': 'plain',
            'classical': 'herringbone'
        }
        return patterns.get(style, 'plain')
    
    def _get_cornice_style(self, style):
        """根据风格获取檐口样式"""
        cornice_styles = {
            'classical': 'dentil',
            'victorian': 'ornate',
            'baroque': 'modillion',
            'renaissance': 'carved',
            'neoclassical': 'dentil',
            'art_deco': 'geometric',
            'gothic': 'corbel',
            'romanesque': 'corbel_table',
            'islamic': 'muqarnas',
            'asian_temple': 'bracket_set'
        }
        return cornice_styles.get(style, 'simple')



























