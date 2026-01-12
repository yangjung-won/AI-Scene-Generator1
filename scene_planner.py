"""
AI场景生成器 - 场景规划模块
根据NLP和LTC分析结果生成具体的场景布局规划

作者: coco
版本: 1.0
"""

import math
import random

# 简单的Vector类替代
class Vector:
    def __init__(self, values):
        if isinstance(values, (list, tuple)):
            self.x, self.y, self.z = values[0], values[1], values[2] if len(values) > 2 else 0
        else:
            self.x = self.y = self.z = 0

    def __getitem__(self, key):
        if key == 0: return self.x
        if key == 1: return self.y
        if key == 2: return self.z
        raise IndexError

    def __sub__(self, other):
        return Vector((self.x - other.x, self.y - other.y, self.z - other.z))

    @property
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def __repr__(self):
        return f"Vector({self.x}, {self.y}, {self.z})"

# ===========================================
# 场景规划模块
# ===========================================

class ScenePlanner:
    """场景规划器"""

    def __init__(self):
        # 场景规划参数
        self.default_scene_size = 50.0  # 🆕 增加场景大小，确保能容纳足够的树木
        self.min_object_distance = 2.5
        self.max_scene_complexity = 100

        # 对象特定的规划参数
        self.object_planning_params = {
            'tree': {
                'base_count': 600,  # 🆕🆕🆕🆕 V4: 大幅增加树木数量到600（用户反馈树木不够多）
                'spacing': 4.0,     # 🆕🆕 V4: 进一步减小间距到4.0，允许更密集的树木
                'height_variation': 0.3,
                'clustering_factor': 0.4  # 🆕 适度聚类，让树木分布更自然
            },
            'flower': {
                'base_count': 20,  # 🆕 增加花朵基础数量（从12增加到20），让画面更丰富
                'spacing': 1.2,    # 🆕 减小间距，让花朵更密集
                'height_variation': 0.1,
                'clustering_factor': 0.8
            },
            'stone': {
                'base_count': 12,  # 🆕 增加石头基础数量（从6增加到12），让画面更丰富
                'spacing': 2.5,   # 🆕 减小间距，让石头更密集
                'height_variation': 0.2,
                'clustering_factor': 0.5  # 🆕 增加聚类因子，让石头更聚集
            },
            'grass': {
                'base_count': 80,  # 🆕 大幅增加草的基础数量（从15增加到80），实现铺满效果
                'spacing': 0.5,    # 🆕 减小间距（从1.0减小到0.5），使草更密集
                'height_variation': 0.05,
                'clustering_factor': 0.9
            },
            'building': {
                'base_count': 2,
                'spacing': 15.0,
                'height_variation': 0.5,
                'clustering_factor': 0.2
            },
            'water': {
                'base_count': 1,
                'spacing': 10.0,
                'height_variation': 0.0,
                'clustering_factor': 0.1
            },
            'bush': {
                'base_count': 12,  # 🆕 增加灌木基础数量（从5增加到12），让画面更丰富
                'spacing': 2.0,   # 🆕 减小间距，让灌木更密集
                'height_variation': 0.2,
                'clustering_factor': 0.7
            },
            'path': {
                'base_count': 1,
                'spacing': 8.0,
                'height_variation': 0.0,
                'clustering_factor': 0.0
            }
        }

    def plan_scene(self, ltc_result):
        """
        规划场景布局

        Args:
            ltc_result (dict): LTC分析结果

        Returns:
            dict: 场景规划结果
        """
        print("[PLANNING] Starting scene planning...")

        # 提取关键参数
        complexity_factor = ltc_result.get('complexity_factor', 0.5)
        naturalness_score = ltc_result.get('naturalness_score', 0.7)
        object_params = ltc_result.get('object_parameters', {})
        scene_params = ltc_result.get('scene_parameters', {})
        
        # 🆕 从LTC结果中获取NLP结果（如果存在），确保所有识别的对象都被包含
        # 这修复了"樱花林"只识别到flower而没有tree的问题
        nlp_result = ltc_result.get('nlp_result', {})
        nlp_objects = nlp_result.get('objects', [])
        
        # 🆕 确保所有NLP识别的对象都在object_params中（即使LTC没有为它们生成参数）
        for obj_type in nlp_objects:
            if obj_type not in object_params:
                # 为未在object_params中的对象创建默认参数
                object_params[obj_type] = {}

        # 计算场景基本参数
        scene_config = self._compute_scene_configuration(complexity_factor, naturalness_score)

        # 计算对象数量
        object_counts = self._compute_object_counts(object_params, complexity_factor, scene_config, ltc_result)

        # [FIX] 根据树木数量动态调整场景大小，确保有足够空间
        tree_count = object_counts.get('tree', 0)
        if tree_count > 0:
            # 每棵树需要约 10x10 的空间（最小间距10.0）
            # 计算需要的最小场景大小
            min_tree_spacing = 10.0
            # 使用sqrt估算网格大小
            grid_size = math.ceil(math.sqrt(tree_count))
            required_size = (grid_size + 2) * min_tree_spacing * 1.2  # 额外20%空间
            
            # 如果当前场景太小，增大它
            if scene_config['area_size'] < required_size:
                old_size = scene_config['area_size']
                scene_config['area_size'] = round(required_size, 1)
                print(f"[PLANNING] Increased scene size from {old_size:.1f} to {scene_config['area_size']:.1f} for {tree_count} trees")

        # 生成布局配置
        layout_config = self._generate_layout_configuration(
            object_counts, scene_config, scene_params
        )

        # 生成环境配置
        environmental_config = self._generate_environmental_configuration(
            scene_params, naturalness_score
        )

        result = {
            'scene_config': scene_config,
            'object_counts': object_counts,
            'layout_config': layout_config,
            'environmental_config': environmental_config,
            'planning_metadata': {
                'complexity_factor': complexity_factor,
                'naturalness_score': naturalness_score,
                'total_objects': sum(object_counts.values()),
                'scene_area': scene_config['area_size'] ** 2
            },
            # 🆕 确保scene_plan包含nlp_result，供模型选择器使用
            'nlp_result': nlp_result
        }

        print(f"[OK] Scene planning completed: {sum(object_counts.values())} objects, scene size {scene_config['area_size']:.1f}x{scene_config['area_size']:.1f}")

        return result

    def _compute_scene_configuration(self, complexity_factor, naturalness_score):
        """计算场景基本配置"""
        # 场景大小基于复杂度
        base_size = self.default_scene_size
        size_multiplier = 1.0 + complexity_factor * 0.5
        area_size = base_size * size_multiplier

        # 高度变化基于自然度
        height_variation = naturalness_score * 2.0

        # 密度控制
        density_factor = 0.7 + complexity_factor * 0.6

        return {
            'area_size': round(area_size, 1),
            'height_variation': round(height_variation, 2),
            'density_factor': round(density_factor, 2),
            'boundary_softness': round(naturalness_score * 0.3, 2),
            'terrain_complexity': round(complexity_factor * 0.8, 2)
        }

    def _compute_object_counts(self, object_params, complexity_factor, scene_config, ltc_result=None):
        """计算每个对象类型的数量"""
        object_counts = {}

        for obj_type, params in object_params.items():
            if obj_type in self.object_planning_params:
                planning_param = self.object_planning_params[obj_type]

                # 基础数量
                base_count = planning_param['base_count']

                # 复杂度调整
                complexity_adjustment = complexity_factor * 2.0
                adjusted_count = base_count * (1 + complexity_adjustment)

                # 场景密度调整
                density_adjustment = scene_config['density_factor'] - 0.7
                adjusted_count *= (1 + density_adjustment)

                # 对象特定参数调整
                if obj_type == 'tree' and 'growth_rate' in params:
                    growth_factor = params['growth_rate'] / planning_param.get('growth_rate', {}).get('default', 1.0)
                    adjusted_count *= (0.8 + growth_factor * 0.4)

                elif obj_type == 'flower' and 'bloom_rate' in params:
                    bloom_factor = params['bloom_rate'] / planning_param.get('bloom_rate', {}).get('default', 1.0)
                    adjusted_count *= (0.9 + bloom_factor * 0.2)
                
                # 🆕 对于草，检测用户输入中是否包含"lush"、"green grass"等关键词，进一步增加数量
                elif obj_type == 'grass':
                    # 从ltc_result中获取用户输入
                    user_input = ''
                    if ltc_result:
                        nlp_result = ltc_result.get('nlp_result', {})
                        user_input = nlp_result.get('user_input', '').lower() if nlp_result else ''
                    # 尝试从object_params中获取用户输入（如果ltc_result不可用）
                    if not user_input:
                        user_input = str(params.get('user_input', '')).lower()
                    
                    # 检测关键词
                    lush_keywords = ['lush', 'green grass', 'dense grass', 'thick grass', 'covered with grass', 
                                   'surrounded by grass', 'full of grass', 'abundant grass', 'rich grass',
                                   '茂密', '绿草', '青草', '芳草', '铺满']
                    has_lush_grass = any(kw in user_input for kw in lush_keywords)
                    
                    if has_lush_grass:
                        # 如果包含"lush"等关键词，进一步增加草的数量（增加50%）
                        adjusted_count *= 1.5
                        print(f"[PLANNING] Detected lush grass keywords, increasing grass count by 50%")

                # 转换为整数并限制范围
                final_count = int(round(adjusted_count))
                # 🆕🆕🆕🆕 V4: 对于树木，大幅增加数量范围到300-500棵 - 用户反馈树木不够多
                if obj_type == 'tree':
                    final_count = max(300, min(final_count, 500))  # 🆕🆕🆕🆕 V4: 增加到300-500棵
                    print(f"[PLANNING] Tree count: {final_count}")
                # 🆕 对于草，允许更多数量（最多200个），实现铺满效果
                elif obj_type == 'grass':
                    final_count = max(1, min(final_count, 200))  # 草最多200个
                # 🆕 对于花朵和石头，也增加最大数量，让画面更丰富
                elif obj_type in ['flower', 'stone', 'bush']:
                    final_count = max(1, min(final_count, 40))  # 🆕 增加花朵、石头、灌木的最大数量
                else:
                    final_count = max(1, min(final_count, self.max_scene_complexity // 2))

                object_counts[obj_type] = final_count

        # 🆕 确保至少有一些对象
        if not object_counts:
            object_counts = {
                'tree': 400,   # 🆕🆕🆕🆕 V4: 大幅增加默认树木数量到400（用户反馈不够多）
                'flower': 20,
                'stone': 12,
                'bush': 15,
                'grass': 100
            }
        
        # 🆕🆕🆕🆕 V4: 确保树木数量合理（最终检查）- 用户反馈树木不够多
        if 'tree' in object_counts:
            original_count = object_counts['tree']
            object_counts['tree'] = max(300, min(500, object_counts['tree']))  # 🆕🆕🆕🆕 V4: 大幅增加范围到300-500
            print(f"[PLANNING] Final tree count: {object_counts['tree']} (original: {original_count})")
        else:
            # 如果没有树，添加默认数量
            object_counts['tree'] = 400  # 🆕🆕🆕🆕 V4: 增加默认值到400
            print(f"[PLANNING] Added default tree count: 400")

        return object_counts

    def _generate_layout_configuration(self, object_counts, scene_config, scene_params):
        """生成布局配置"""
        area_size = scene_config['area_size']
        layout_dynamics = scene_params.get('layout_dynamics', {})

        # 生成聚类中心
        cluster_centers = self._generate_cluster_centers(
            object_counts, area_size, layout_dynamics
        )

        # 为每个对象生成位置
        positions = []
        placed_positions = []

        for obj_type, count in object_counts.items():
            obj_positions = self._generate_positions_for_object_type(
                obj_type, count, area_size, cluster_centers,
                layout_dynamics, placed_positions
            )
            positions.extend(obj_positions)
            placed_positions.extend([pos['position'] for pos in obj_positions])

        # 生成地形配置
        terrain_config = self._generate_terrain_configuration(scene_config)

        return {
            'area_size': area_size,
            'cluster_centers': cluster_centers,
            'positions': positions,
            'terrain_config': terrain_config,
            'spatial_constraints': self._generate_spatial_constraints(layout_dynamics)
        }

    def _generate_cluster_centers(self, object_counts, area_size, layout_dynamics):
        """生成聚类中心"""
        cluster_strength = layout_dynamics.get('clustering_coefficient', 0.5)

        # 计算需要的聚类中心数量
        total_objects = sum(object_counts.values())
        num_clusters = max(3, min(8, int(total_objects / 10) + 1))  # 🆕 增加聚类中心数量

        centers = []
        for i in range(num_clusters):
            # 🆕 改进的聚类中心分布：使用更分散的螺旋分布
            angle = i * 2 * math.pi / num_clusters
            # 🆕 使用更大的半径范围，确保聚类中心分散在整个场景中
            base_radius = area_size * 0.15  # 最小半径
            max_radius = area_size * 0.4     # 最大半径
            radius = base_radius + (max_radius - base_radius) * (i / max(num_clusters - 1, 1))

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            # 🆕 添加更大的随机偏移，使聚类中心更分散
            offset_range = area_size * 0.15
            x += random.uniform(-offset_range, offset_range)
            y += random.uniform(-offset_range, offset_range)
            
            # 🆕 确保聚类中心在场景边界内
            x = max(-area_size/2 + 2, min(area_size/2 - 2, x))
            y = max(-area_size/2 + 2, min(area_size/2 - 2, y))

            centers.append(Vector((x, y, 0)))

        return centers

    def _generate_positions_for_object_type(self, obj_type, count, area_size,
                                          cluster_centers, layout_dynamics, placed_positions):
        """为特定对象类型生成位置"""
        positions = []
        planning_param = self.object_planning_params.get(obj_type, {})

        spacing = planning_param.get('spacing', 3.0)
        # 🆕 对于树木，增加基础间距，确保不重叠
        if obj_type == 'tree':
            spacing = max(spacing, 8.0)  # 树木最小间距8.0
        clustering_factor = planning_param.get('clustering_factor', 0.5)
        spatial_dist = layout_dynamics.get('spatial_distribution', {})

        distribution_type = spatial_dist.get('type', 'natural')
        cluster_strength = spatial_dist.get('cluster_strength', 0.5)

        # [FIX] 获取最小距离配置，用于碰撞检测
        min_distances = {
            'tree': 10.0,  # [FIX] 增加树木最小距离，确保绝对不重叠
            'building': 8.0,
            'bush': 3.0,
            'flower': 1.5,
            'stone': 2.0,
            'grass': 0.5,
        }
        min_distance = min_distances.get(obj_type, spacing * 0.8)
        
        for i in range(count):
            position = self._find_valid_position(
                obj_type, spacing, area_size, cluster_centers,
                clustering_factor, cluster_strength, placed_positions,
                distribution_type
            )

            if position:
                # [DISABLED] 不再添加随机偏移 - 保持物体原本的xyz位置
                # 用户要求：不改变物体原本的xyz，直接使用碰撞检测后的有效位置
                # 所有对象类型都不添加偏移
                
                # [DISABLED] 不添加随机旋转 - 保持原始旋转角度为0
                random_rotation = 0.0  # 无旋转
                
                # 根据对象类型调整大小变化范围（保留大小变化功能）
                if obj_type in ['tree', 'bush']:
                    scale_var = random.uniform(0.8, 1.25)
                elif obj_type == 'flower':
                    scale_var = random.uniform(0.85, 1.2)
                elif obj_type == 'stone':
                    scale_var = random.uniform(0.9, 1.15)
                else:
                    scale_var = random.uniform(0.9, 1.1)
                
                positions.append({
                    'type': obj_type,
                    'position': position,
                    'index': i,
                    'clustering_factor': clustering_factor,
                    'spacing': spacing,
                    'rotation_z': random_rotation,
                    'scale_variation': scale_var
                })

        return positions

    def _find_valid_position(self, obj_type, spacing, area_size, cluster_centers,
                           clustering_factor, cluster_strength, placed_positions,
                           distribution_type):
        """找到有效的对象位置"""
        max_attempts = 200  # 🆕 增加尝试次数，确保找到有效位置
        total_objects = len(placed_positions)  # 🆕 获取已放置对象数量，用于备用策略
        
        # [FIX] 根据对象类型设置最小距离（确保不重叠）
        min_distances = {
            'tree': 8.0,  # 🆕 减小树木最小距离到8.0，允许更多树木（原10.0）
            'building': 8.0,
            'bush': 3.0,
            'flower': 1.5,
            'stone': 2.0,
            'grass': 0.5,
            'water': 5.0,
            'path': 4.0,
        }
        min_distance = min_distances.get(obj_type, spacing * 0.8)

        for attempt in range(max_attempts):
            if distribution_type == 'clustered' and cluster_centers and random.random() < cluster_strength:
                # 🆕 改进的聚类分布：使用更大的偏移范围，避免过度集中
                cluster_center = random.choice(cluster_centers)
                # 🆕 增加偏移距离范围，使对象更分散在聚类中心周围
                max_offset = min(spacing * 4, area_size * 0.2)  # 限制最大偏移，避免超出场景
                offset_distance = random.uniform(0, max_offset)
                offset_angle = random.uniform(0, 2 * math.pi)

                x = cluster_center.x + offset_distance * math.cos(offset_angle)
                y = cluster_center.y + offset_distance * math.sin(offset_angle)
                
                # 🆕 确保位置在场景边界内
                x = max(-area_size/2 + 1, min(area_size/2 - 1, x))
                y = max(-area_size/2 + 1, min(area_size/2 - 1, y))
            else:
                # 均匀分布或散布分布
                if distribution_type == 'scattered':
                    # 散布分布 - 更远离中心
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(area_size * 0.3, area_size * 0.45)  # 🆕 使用更大的范围
                    x = distance * math.cos(angle)
                    y = distance * math.sin(angle)
                else:
                    # 🆕 改进的自然分布：避免集中在原点附近
                    # 使用分层随机分布，确保覆盖整个场景
                    layer = random.random()  # 0-1之间的随机数
                    if layer < 0.3:
                        # 内层：30%的对象在中心区域
                        radius = random.uniform(0, area_size * 0.2)
                    elif layer < 0.7:
                        # 中层：40%的对象在中间区域
                        radius = random.uniform(area_size * 0.2, area_size * 0.35)
                    else:
                        # 外层：30%的对象在外围区域
                        radius = random.uniform(area_size * 0.35, area_size * 0.45)
                    
                    angle = random.uniform(0, 2 * math.pi)
                    x = radius * math.cos(angle)
                    y = radius * math.sin(angle)

            position = Vector((x, y, 0))

            # 检查是否与其他对象太近（使用_get_min_distance_for_type计算，更灵活）
            calculated_min_distance = self._get_min_distance_for_type(obj_type, spacing)
            # 使用计算出的最小距离和之前定义的最小距离中的较大值，确保不重叠
            effective_min_distance = max(min_distance, calculated_min_distance)
            if self._is_position_valid(position, placed_positions, effective_min_distance, area_size):
                return position

        # 🆕 如果找不到有效位置，使用更均匀的分布策略（避免堆积在原点）
        # 使用螺旋分布或网格分布，确保覆盖整个场景
        attempt_count = len(placed_positions) if placed_positions else 0
        
        # 方法1: 螺旋分布（优先）
        if attempt_count < total_objects * 0.8:  # 如果还有空间，使用螺旋分布
            spiral_angle = attempt_count * 0.5  # 螺旋角度
            spiral_radius = (area_size * 0.4) * (1 + attempt_count * 0.01)  # 逐渐向外扩展
            x = spiral_radius * math.cos(spiral_angle)
            y = spiral_radius * math.sin(spiral_angle)
        else:
            # 方法2: 网格分布（当空间较满时）
            grid_size = int(math.sqrt(total_objects)) + 1
            grid_x = (attempt_count % grid_size) - grid_size // 2
            grid_y = (attempt_count // grid_size) - grid_size // 2
            cell_size = area_size / (grid_size + 1)
            x = grid_x * cell_size + random.uniform(-cell_size * 0.3, cell_size * 0.3)
            y = grid_y * cell_size + random.uniform(-cell_size * 0.3, cell_size * 0.3)
        
        # 确保在边界内
        x = max(-area_size/2 + 1, min(area_size/2 - 1, x))
        y = max(-area_size/2 + 1, min(area_size/2 - 1, y))
        
        return Vector((x, y, 0))

    def _get_min_distance_for_type(self, obj_type, base_spacing):
        """获取对象类型的最小距离"""
        # 🆕 直接返回固定的最小距离，确保不重叠
        fixed_min_distances = {
            'tree': 8.0,   # 🆕 合理的树木固定最小距离
            'flower': 1.5,
            'stone': 2.0,
            'grass': 0.5,
            'building': 8.0,
            'water': 5.0,
            'bush': 3.0,
            'path': 4.0
        }
        
        return fixed_min_distances.get(obj_type, base_spacing)

    def _is_position_valid(self, position, placed_positions, min_distance, area_size):
        """检查位置是否有效"""
        # 检查边界
        if abs(position.x) > area_size/2 or abs(position.y) > area_size/2:
            return False

        # 检查与其他位置的距离
        for existing_pos in placed_positions:
            if (position - existing_pos).length < min_distance:
                return False

        return True

    def _generate_terrain_configuration(self, scene_config):
        """生成地形配置"""
        return {
            'height_map_resolution': 64,
            'max_height': scene_config['height_variation'],
            'smoothness': 0.8,
            'noise_scale': 0.05,
            'terrace_count': int(scene_config['terrain_complexity'] * 3)
        }

    def _generate_spatial_constraints(self, layout_dynamics):
        """生成空间约束"""
        return {
            'min_separation': self.min_object_distance,
            'max_clustering': layout_dynamics.get('clustering_coefficient', 0.5),
            'boundary_margin': 2.0,
            'height_constraints': {
                'min': -1.0,
                'max': 5.0
            }
        }

    def _generate_environmental_configuration(self, scene_params, naturalness_score):
        """生成环境配置"""
        lighting_dynamics = scene_params.get('lighting_dynamics', {})
        environmental_dynamics = scene_params.get('environmental_dynamics', {})

        return {
            'lighting': {
                'intensity': 2.5 + naturalness_score * 0.5,
                'color_temperature': 5500 + (naturalness_score - 0.5) * 1000,
                'shadow_softness': lighting_dynamics.get('shadow_dynamics', 0.4),
                'ambient_occlusion': 0.3 + naturalness_score * 0.4
            },
            'atmosphere': {
                'fog_density': (1.0 - naturalness_score) * 0.2,
                'sky_color': [0.6, 0.8, 1.0] if naturalness_score > 0.6 else [0.4, 0.6, 0.9],
                'sun_angle': 45 + (naturalness_score - 0.5) * 20
            },
            'ecosystem': {
                'stability': environmental_dynamics.get('weather_stability', 0.8),
                'diversity': naturalness_score * 0.8 + 0.2,
                'interaction_strength': environmental_dynamics.get('ecosystem_balance', 0.7)
            }
        }
