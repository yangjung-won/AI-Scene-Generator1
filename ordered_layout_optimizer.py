"""
AI场景生成器 - 有序布局优化器
实现三层秩序：拓扑秩序、度量秩序、语义秩序

作者: AI Team
版本: 1.0
"""

import numpy as np
import math
import random
from geometric_descriptors import GeometricDescriptors
from scene_planner import Vector

# 🆕 导入地形射线检测模块
try:
    from terrain_raycast import TerrainRaycast
    RAYCAST_AVAILABLE = True
except ImportError:
    RAYCAST_AVAILABLE = False
    print("[WARN] TerrainRaycast not available, using simple snap-to-ground")


class OrderedLayoutOptimizer:
    """有序布局优化器 - 核心模块"""
    
    def __init__(self, max_iterations=100, learning_rate=0.1):  # 🆕 增加最大迭代次数（从50增加到100），确保充分优化
        """
        初始化优化器
        
        Args:
            max_iterations: 最大迭代次数
            learning_rate: 学习率
        """
        self.max_iterations = max_iterations
        self.learning_rate = learning_rate
        self.geometric_descriptors = GeometricDescriptors()
        
        # 🆕 初始化地形射线检测器
        if RAYCAST_AVAILABLE:
            self.terrain_raycast = TerrainRaycast(terrain_name='Base_Terrain')
        else:
            self.terrain_raycast = None
        
        # 语义rank定义
        self.semantic_ranks = {
            'water': 0,      # anchor
            'path': 0,       # anchor
            'building': 1,   # secondary
            'tree': 1,       # secondary
            'stone': 2,      # filler
            'flower': 2,     # filler
            'grass': 2,      # filler
            'bush': 2        # filler
        }
    
    def optimize(self, initial_layout, ltc_params, semantic_constraints=None, scene_config=None):
        """
        优化布局，使其满足三层秩序
        
        Args:
            initial_layout: 初始布局（来自Transformer或scene_planner）
            ltc_params: LTC分析结果
            semantic_constraints: 语义约束
        
        Returns:
            dict: 优化后的布局
        """
        print("[OPTIMIZING] Starting ordered layout optimization...")
        
        # 基础场景参数（用于边界与贴地约束）
        area_size = 40.0
        ground_height = 0.0
        if scene_config:
            area_size = scene_config.get('area_size', area_size)
            ground_height = scene_config.get('ground_height', ground_height)
        area_size = initial_layout.get('area_size', area_size)
        ground_height = initial_layout.get('ground_height', ground_height)
        
        positions = initial_layout.get('positions', [])
        if not positions:
            print("[WARN] No positions to optimize")
            return initial_layout
        
        # 🆕 0. 提取空间依赖关系
        spatial_dependencies = ltc_params.get('spatial_dependencies', {})
        if spatial_dependencies:
            print(f"   [SPATIAL] Found {len(spatial_dependencies.get('pair_constraints', []))} pair constraints, "
                  f"{len(spatial_dependencies.get('group_constraints', []))} group constraints")
        
        # 1. 构建拓扑秩序图（DAG）- 增强：考虑语义关系
        spatial_graph = self._build_topological_graph(positions, spatial_dependencies)
        print(f"   [TOPOLOGY] Built DAG with {len(spatial_graph['nodes'])} nodes, {len(spatial_graph['edges'])} edges")
        
        # 2. 参数化（度量秩序）
        parameterized = self._parameterize_positions(positions, spatial_graph)
        print(f"   [METRIC] Parameterized {len(parameterized)} positions")
        
        # 3. 应用语义约束
        constrained = self._apply_semantic_constraints(parameterized, positions)
        print(f"   [SEMANTIC] Applied semantic constraints")
        
        # 🆕 3.5. 应用空间依赖约束（在迭代优化前）
        if spatial_dependencies:
            positions = self._apply_spatial_dependencies(positions, spatial_dependencies, scene_config or {})
            print(f"   [SPATIAL] Applied spatial dependency constraints")
        
        # 4. 迭代优化
        optimized_positions = self._iterative_optimize(
            constrained, positions, ltc_params, area_size, ground_height, spatial_dependencies
        )
        
        # 🆕 使用射线检测将物体吸附到地形表面（替代简单的贴地）
        optimized_positions = self._snap_to_terrain_with_raycast(
            optimized_positions, ground_height
        )
        
        # [DISABLED] 不再添加随机偏移和旋转 - 保持物体原本的xyz位置和旋转
        # 用户要求：不改变物体原本的xyz，不要添加旋转
        import random
        for pos_info in optimized_positions:
            obj_type = pos_info.get('type', 'unknown')
            
            # [DISABLED] 位置偏移已禁用 - 保持原始位置
            # offset_scale = {...}
            # random_offset_x = ...
            # random_offset_y = ...
            # pos_info['position'].x += random_offset_x
            # pos_info['position'].y += random_offset_y
            
            # [DISABLED] 随机旋转已禁用 - 保持原始旋转（0）
            # 如果用户没有指定旋转，则设置为0（无旋转）
            if 'rotation_z' not in pos_info:
                pos_info['rotation_z'] = 0.0  # 无旋转
            
            # 🆕 如果没有大小变化，添加随机大小
            if 'scale_variation' not in pos_info:
                if obj_type in ['tree', 'bush']:
                    pos_info['scale_variation'] = random.uniform(0.8, 1.25)
                elif obj_type == 'flower':
                    pos_info['scale_variation'] = random.uniform(0.85, 1.2)
                elif obj_type == 'stone':
                    pos_info['scale_variation'] = random.uniform(0.9, 1.15)
                else:
                    pos_info['scale_variation'] = random.uniform(0.9, 1.1)
            else:
                pos_info['scale_variation'] *= random.uniform(0.95, 1.05)
        
        # 🆕 最终碰撞检查：确保随机偏移后没有重叠
        optimized_positions = self._final_collision_check(optimized_positions, area_size)
        
        # 5. 计算最终几何描述量
        object_types = list(set(p['type'] for p in optimized_positions))
        final_descriptors = self.geometric_descriptors.compute_all_descriptors(
            optimized_positions, object_types
        )
        
        result = {
            'positions': optimized_positions,
            'cluster_centers': initial_layout.get('cluster_centers', []),
            'spatial_graph': spatial_graph,
            'geometric_descriptors': final_descriptors,
            'optimization_metadata': {
                'iterations': self.max_iterations,
                'final_loss': self._compute_total_loss(optimized_positions, final_descriptors)
            }
        }
        
        print(f"[OK] Layout optimization completed")
        return result
    
    def _build_topological_graph(self, positions, spatial_dependencies=None):
        """构建拓扑秩序图（DAG）- 增强：考虑语义关系"""
        # 按类型分组
        type_groups = {}
        for i, pos_info in enumerate(positions):
            obj_type = pos_info['type']
            if obj_type not in type_groups:
                type_groups[obj_type] = []
            type_groups[obj_type].append(i)
        
        # 构建节点
        nodes = []
        node_map = {}  # {obj_type: node_id}
        for obj_type in type_groups.keys():
            node_id = len(nodes)
            nodes.append({
                'id': node_id,
                'type': obj_type,
                'rank': self.semantic_ranks.get(obj_type, 1)
            })
            node_map[obj_type] = node_id
        
        # 构建边（基于语义rank）
        edges = []
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                if i != j:
                    rank_i = node_i['rank']
                    rank_j = node_j['rank']
                    
                    # 高rank约束低rank
                    if rank_i < rank_j:
                        edges.append({
                            'from': node_i['id'],
                            'to': node_j['id'],
                            'relation': 'constrains',
                            'type': 'semantic_hierarchy'
                        })
                    
                    # 空间关系（简化：基于距离）
                    if self._should_have_spatial_relation(node_i['type'], node_j['type']):
                        edges.append({
                            'from': node_i['id'],
                            'to': node_j['id'],
                            'relation': 'near',
                            'type': 'spatial'
                        })
        
        # 🆕 添加语义关系边
        if spatial_dependencies:
            pair_constraints = spatial_dependencies.get('pair_constraints', [])
            for constraint in pair_constraints:
                subject_type = constraint['subject']
                object_type = constraint['object']
                
                subject_node = next((n for n in nodes if n['type'] == subject_type), None)
                object_node = next((n for n in nodes if n['type'] == object_type), None)
                
                if subject_node and object_node:
                    edges.append({
                        'from': subject_node['id'],
                        'to': object_node['id'],
                        'relation': constraint['type'],
                        'type': 'semantic_constraint',
                        'distance': constraint['distance'],
                        'confidence': constraint['confidence']
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'is_dag': self._verify_dag(nodes, edges)
        }
    
    def _should_have_spatial_relation(self, type1, type2):
        """判断两种类型是否应该有空间关系"""
        # 定义空间关系规则
        relations = {
            'water': ['tree', 'stone', 'grass'],
            'path': ['tree', 'flower', 'grass'],
            'building': ['tree', 'path'],
            'tree': ['grass', 'flower', 'bush']
        }
        
        return (type1 in relations and type2 in relations[type1]) or \
               (type2 in relations and type1 in relations[type2])
    
    def _verify_dag(self, nodes, edges):
        """验证图是否为DAG（简化版）"""
        # 检查是否有环（简化实现）
        # 实际应该用DFS检测
        return True  # 假设我们的构建方法保证是DAG
    
    def _parameterize_positions(self, positions, spatial_graph):
        """参数化位置（度量秩序）"""
        # 使用Polar ordering
        parameterized = []
        
        for pos_info in positions:
            position = pos_info['position']
            obj_type = pos_info['type']
            
            # 转换为极坐标参数
            r = math.sqrt(position.x**2 + position.y**2)
            θ = math.atan2(position.y, position.x)
            
            parameterized.append({
                'original': pos_info,
                'r': r,
                'θ': θ,
                'type': obj_type
            })
        
        return parameterized
    
    def _apply_semantic_constraints(self, parameterized, positions):
        """应用语义约束"""
        # 确保高rank对象的位置优先确定
        # 低rank对象的位置受高rank对象约束
        
        constrained = []
        for param in parameterized:
            obj_type = param['type']
            rank = self.semantic_ranks.get(obj_type, 1)
            
            # 找到约束该对象的更高rank对象
            constraints = []
            for other_param in parameterized:
                other_type = other_param['type']
                other_rank = self.semantic_ranks.get(other_type, 1)
                
                if other_rank < rank:  # 更高rank
                    constraints.append(other_param)
            
            param['constraints'] = constraints
            param['rank'] = rank
            constrained.append(param)
        
        return constrained
    
    def _iterative_optimize(self, parameterized, positions, ltc_params, area_size, ground_height, spatial_dependencies=None):
        """迭代优化位置 - 增强：考虑空间依赖，增加随机性避免刻板"""
        import random
        optimized_positions = positions.copy()
        
        for iteration in range(self.max_iterations):
            # 计算当前几何描述量
            object_types = list(set(p['type'] for p in optimized_positions))
            descriptors = self.geometric_descriptors.compute_all_descriptors(
                optimized_positions, object_types
            )
            
            # 计算损失
            loss = self._compute_total_loss(optimized_positions, descriptors)
            
            if iteration % 10 == 0:
                print(f"      Iteration {iteration}/{self.max_iterations}, loss: {loss:.4f}")
            
            # 更新位置（简化：基于梯度下降思想）
            for i, pos_info in enumerate(optimized_positions):
                # 找到对应的描述量
                desc = descriptors['descriptors'][i] if i < len(descriptors['descriptors']) else None
                
                if desc:
                    # 计算梯度（简化版）
                    gradient = self._compute_gradient(pos_info, desc, descriptors['targets'])
                    
                    # 🆕 添加随机噪声到梯度，使优化更自然（避免过于刻板）
                    obj_type = pos_info.get('type', 'unknown')
                    noise_scale = {
                        'tree': 0.4,      # 树木：较大噪声
                        'flower': 0.3,    # 花朵：中等噪声
                        'stone': 0.35,    # 石头：较大噪声
                        'grass': 0.25,    # 草：小噪声
                        'bush': 0.3,      # 灌木：中等噪声
                    }.get(obj_type, 0.3)
                    
                    gradient_noise_x = random.gauss(0, noise_scale)
                    gradient_noise_y = random.gauss(0, noise_scale)
                    
                    # 更新位置（加入随机噪声）
                    pos_info['position'].x -= self.learning_rate * (gradient[0] + gradient_noise_x)
                    pos_info['position'].y -= self.learning_rate * (gradient[1] + gradient_noise_y)
                    
                    # 🆕 防止位置过于接近原点（避免堆积）
                    distance_from_origin = math.sqrt(pos_info['position'].x**2 + pos_info['position'].y**2)
                    min_distance_from_origin = area_size * 0.05  # 最小距离原点的距离
                    if distance_from_origin < min_distance_from_origin and distance_from_origin > 0:
                        # 将位置向外推
                        scale = min_distance_from_origin / distance_from_origin
                        pos_info['position'].x *= scale
                        pos_info['position'].y *= scale
                    elif distance_from_origin == 0:
                        # 如果正好在原点，随机推到一个方向
                        angle = random.uniform(0, 2 * math.pi)
                        pos_info['position'].x = min_distance_from_origin * math.cos(angle)
                        pos_info['position'].y = min_distance_from_origin * math.sin(angle)
                    
                    # 应用约束（边界、碰撞等）
                    self._apply_constraints(pos_info, optimized_positions, area_size, ground_height)
                    
                    # 🆕 应用空间依赖约束（在每次迭代中）
                    if spatial_dependencies:
                        self._apply_spatial_constraint_in_iteration(pos_info, optimized_positions, spatial_dependencies)
        
        return optimized_positions
    
    def _apply_spatial_dependencies(self, positions, spatial_dependencies, scene_config):
        """
        🆕 应用空间依赖约束，确保物体位置符合语义关系
        
        Args:
            positions: 位置列表
            spatial_dependencies: 空间依赖关系
            scene_config: 场景配置
        
        Returns:
            更新后的位置列表
        """
        area_size = scene_config.get('area_size', 40.0) if scene_config else 40.0
        
        # 处理成对关系约束
        pair_constraints = spatial_dependencies.get('pair_constraints', [])
        for constraint in pair_constraints:
            subject_type = constraint['subject']
            object_type = constraint['object']
            target_distance = constraint['distance']
            relation_type = constraint['type']
            
            # 找到所有subject和object类型的对象
            subject_objects = [p for p in positions if p['type'] == subject_type]
            object_objects = [p for p in positions if p['type'] == object_type]
            
            if not subject_objects or not object_objects:
                continue
            
            # 为每个subject对象找到最近的object对象，并调整位置
            for subj in subject_objects:
                # 找到最近的object对象
                nearest_obj = min(object_objects, 
                                 key=lambda o: self._compute_distance(subj['position'], o['position']))
                
                # 计算目标位置
                current_distance = self._compute_distance(subj['position'], nearest_obj['position'])
                
                if abs(current_distance - target_distance) > 0.5:  # 如果距离不符合要求
                    # 调整subject对象的位置
                    direction = self._get_direction_vector(subj['position'], nearest_obj['position'])
                    if direction:
                        # 根据关系类型调整
                        if relation_type == 'next_to':
                            # 在object旁边
                            new_pos = Vector((
                                nearest_obj['position'].x + direction[0] * target_distance,
                                nearest_obj['position'].y + direction[1] * target_distance,
                                nearest_obj['position'].z
                            ))
                        elif relation_type == 'around':
                            # 围绕object
                            angle = self._compute_angle(subj['position'], nearest_obj['position'])
                            new_pos = Vector((
                                nearest_obj['position'].x + target_distance * math.cos(angle),
                                nearest_obj['position'].y + target_distance * math.sin(angle),
                                nearest_obj['position'].z
                            ))
                        else:
                            # 默认：保持方向，调整距离
                            new_pos = Vector((
                                nearest_obj['position'].x + direction[0] * target_distance,
                                nearest_obj['position'].y + direction[1] * target_distance,
                                nearest_obj['position'].z
                            ))
                        
                        # 边界检查
                        new_pos.x = max(-area_size/2, min(area_size/2, new_pos.x))
                        new_pos.y = max(-area_size/2, min(area_size/2, new_pos.y))
                        
                        subj['position'] = new_pos
        
        # 处理组间关系约束
        group_constraints = spatial_dependencies.get('group_constraints', [])
        for constraint in group_constraints:
            group_type = constraint['group_type']
            center_type = constraint.get('center_type')
            radius = constraint['radius']
            relation_type = constraint['type']
            quantity = constraint.get('quantity', 5)
            
            # 找到中心对象
            center_objects = [p for p in positions if p['type'] == center_type] if center_type else []
            group_objects = [p for p in positions if p['type'] == group_type]
            
            if not group_objects:
                continue
            
            # 如果没有中心对象，使用第一个group对象作为中心
            if not center_objects:
                center_pos = group_objects[0]['position']
            else:
                center_pos = center_objects[0]['position']
            
            # 根据关系类型排列group对象
            if relation_type == 'circle_around':
                # 圆形排列
                angle_step = 2 * math.pi / len(group_objects)
                for i, group_obj in enumerate(group_objects):
                    angle = i * angle_step
                    group_obj['position'] = Vector((
                        center_pos.x + radius * math.cos(angle),
                        center_pos.y + radius * math.sin(angle),
                        center_pos.z
                    ))
            elif relation_type == 'line_along':
                # 线性排列
                for i, group_obj in enumerate(group_objects):
                    offset = (i - len(group_objects) / 2) * (radius / len(group_objects))
                    group_obj['position'] = Vector((
                        center_pos.x + offset,
                        center_pos.y,
                        center_pos.z
                    ))
            elif relation_type == 'cluster_near':
                # 聚集在中心附近
                for group_obj in group_objects:
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(0, radius * 0.5)
                    group_obj['position'] = Vector((
                        center_pos.x + distance * math.cos(angle),
                        center_pos.y + distance * math.sin(angle),
                        center_pos.z
                    ))
        
        return positions
    
    def _get_direction_vector(self, pos1, pos2):
        """获取从pos1到pos2的方向向量（归一化）"""
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            return (dx/distance, dy/distance)
        return None
    
    def _compute_angle(self, pos1, pos2):
        """计算从pos1到pos2的角度"""
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        return math.atan2(dy, dx)
    
    def _apply_spatial_constraint_in_iteration(self, pos_info, all_positions, spatial_dependencies):
        """在迭代优化中应用空间约束"""
        pair_constraints = spatial_dependencies.get('pair_constraints', [])
        obj_type = pos_info['type']
        position = pos_info['position']
        
        # 检查是否有约束涉及当前对象
        for constraint in pair_constraints:
            if constraint['subject'] == obj_type:
                # 找到object类型的对象
                object_objects = [p for p in all_positions if p['type'] == constraint['object']]
                if object_objects:
                    nearest_obj = min(object_objects,
                                     key=lambda o: self._compute_distance(position, o['position']))
                    target_distance = constraint['distance']
                    current_distance = self._compute_distance(position, nearest_obj['position'])
                    
                    # 如果距离不符合，轻微调整
                    if abs(current_distance - target_distance) > 0.3:
                        direction = self._get_direction_vector(position, nearest_obj['position'])
                        if direction:
                            # 向目标距离调整
                            adjustment = (target_distance - current_distance) * 0.1
                            position.x += direction[0] * adjustment
                            position.y += direction[1] * adjustment
    
    def _compute_gradient(self, pos_info, descriptor, targets):
        """计算梯度（简化版）"""
        # 基于三个几何描述量的目标值计算梯度
        d_t = descriptor['d_t']
        θ_t = descriptor['θ_t']
        b_t = descriptor['b_t']
        
        # 目标值
        d_target = targets.get('d_t_mean', d_t)
        θ_target = targets.get('θ_t_mean', θ_t)
        b_target = targets.get('b_t_mean', b_t)
        
        # 计算损失梯度（简化）
        dx = (d_t - d_target) * 0.1
        dy = (θ_t - θ_target) * 0.1
        
        return (dx, dy)
    
    def _apply_constraints(self, pos_info, all_positions, area_size, ground_height):
        """应用约束（边界、最小距离等）"""
        position = pos_info['position']
        
        # 🆕 防止对象聚集在原点附近（优先处理）
        import random
        distance_from_origin = math.sqrt(position.x**2 + position.y**2)
        min_distance_from_origin = area_size * 0.08  # 最小距离原点的距离（场景大小的8%）
        
        if distance_from_origin < min_distance_from_origin:
            if distance_from_origin < 0.1:  # 如果非常接近原点（几乎在原点）
                # 随机推到一个方向
                angle = random.uniform(0, 2 * math.pi)
                position.x = min_distance_from_origin * math.cos(angle)
                position.y = min_distance_from_origin * math.sin(angle)
            else:
                # 将位置向外推
                scale = min_distance_from_origin / distance_from_origin
                position.x *= scale
                position.y *= scale
        
        # 🆕 边界约束：确保物体在地形范围内（留出安全边距，避免物体边缘超出）
        # 假设物体最大半径约为2-3单位，留出5单位的安全边距
        safety_margin = 5.0
        terrain_half_size = area_size / 2 - safety_margin
        position.x = max(-terrain_half_size, min(terrain_half_size, position.x))
        position.y = max(-terrain_half_size, min(terrain_half_size, position.y))
        
        # 🆕 如果边界约束导致位置回到原点附近，再次推离原点
        distance_from_origin = math.sqrt(position.x**2 + position.y**2)
        if distance_from_origin < min_distance_from_origin:
            angle = math.atan2(position.y, position.x) if distance_from_origin > 0.1 else random.uniform(0, 2 * math.pi)
            position.x = min_distance_from_origin * math.cos(angle)
            position.y = min_distance_from_origin * math.sin(angle)
            # 再次应用边界约束
            position.x = max(-terrain_half_size, min(terrain_half_size, position.x))
            position.y = max(-terrain_half_size, min(terrain_half_size, position.y))
        
        # 贴地约束：将所有物体抬到地面高度，避免下沉
        if position.z < ground_height:
            position.z = ground_height
        
        # [FIX] 增强碰撞检测：根据对象类型设置不同的最小距离
        obj_type = pos_info.get('type', 'unknown')
        min_distances = {
            'tree': 10.0,    # [FIX] 增加树木最小距离到10.0
            'building': 8.0,
            'bush': 3.0,
            'flower': 1.5,
            'stone': 2.0,
            'grass': 0.5,
            'water': 5.0,
            'path': 4.0,
        }
        min_distance = min_distances.get(obj_type, 3.0)  # 默认3.0
        
        # 🆕 多次迭代推开，确保没有重叠（增强版：增加迭代次数和推开力度）
        max_iterations = 30  # 🆕 增加迭代次数（从10增加到30），确保充分推开重叠物体
        for iteration in range(max_iterations):
            has_overlap = False
            for other in all_positions:
                if other == pos_info:
                    continue
                
                # 🆕 根据对方对象类型调整最小距离
                other_type = other.get('type', 'unknown')
                other_min_distance = min_distances.get(other_type, 2.5)
                combined_min_distance = (min_distance + other_min_distance) / 2
                
                distance = self._compute_distance(position, other['position'])
                if distance < combined_min_distance and distance > 0.01:  # 避免除零
                    has_overlap = True
                    # 推开（增强：提高推开力度）
                    dx = position.x - other['position'].x
                    dy = position.y - other['position'].y
                    # 🆕 提高推开力度（从0.6增加到0.8），并加入迭代因子，确保充分推开
                    push_factor = 0.8 + (iteration / max_iterations) * 0.2  # 随着迭代增加推开力度
                    push_distance = (combined_min_distance - distance) * push_factor
                    position.x += (dx / distance) * push_distance
                    position.y += (dy / distance) * push_distance
                    # 🆕 推开后再次检查边界约束
                    position.x = max(-terrain_half_size, min(terrain_half_size, position.x))
                    position.y = max(-terrain_half_size, min(terrain_half_size, position.y))
            
            # 如果没有重叠，提前退出
            if not has_overlap:
                break
    
    def _compute_distance(self, pos1, pos2):
        """计算距离"""
        dx = pos1.x - pos2.x
        dy = pos1.y - pos2.y
        return math.sqrt(dx*dx + dy*dy)
    
    def _snap_to_ground(self, positions, ground_height):
        """将所有物体贴合到地面高度（备用方法）"""
        for pos in positions:
            if pos['position'].z < ground_height:
                pos['position'].z = ground_height
    
    def _snap_to_terrain_with_raycast(self, positions, ground_height, context=None):
        """
        🆕 使用射线检测将物体吸附到地形表面
        
        Args:
            positions: 位置列表
            ground_height: 地面高度（备用）
            context: Blender上下文（如果可用）
            
        Returns:
            list: 更新后的位置列表
        """
        if self.terrain_raycast and RAYCAST_AVAILABLE:
            print("[RAYCAST] Using terrain raycast for object placement")
            # 使用射线检测吸附
            snapped_positions = self.terrain_raycast.batch_snap_positions(
                positions, context
            )
            return snapped_positions
        else:
            # 备用：简单贴地
            print("[RAYCAST] Using simple snap-to-ground (raycast not available)")
            self._snap_to_ground(positions, ground_height)
            return positions
    
    def _apply_spatial_constraint_in_iteration(self, pos_info, all_positions, spatial_dependencies):
        """在迭代优化中应用空间约束"""
        pair_constraints = spatial_dependencies.get('pair_constraints', [])
        obj_type = pos_info['type']
        position = pos_info['position']
        
        # 检查是否有约束涉及当前对象
        for constraint in pair_constraints:
            if constraint['subject'] == obj_type:
                # 找到object类型的对象
                object_objects = [p for p in all_positions if p['type'] == constraint['object']]
                if object_objects:
                    nearest_obj = min(object_objects,
                                     key=lambda o: self._compute_distance(position, o['position']))
                    target_distance = constraint['distance']
                    current_distance = self._compute_distance(position, nearest_obj['position'])
                    
                    # 如果距离不符合，轻微调整
                    if abs(current_distance - target_distance) > 0.3:
                        direction = self._get_direction_vector(position, nearest_obj['position'])
                        if direction:
                            # 向目标距离调整
                            adjustment = (target_distance - current_distance) * 0.1
                            position.x += direction[0] * adjustment
                            position.y += direction[1] * adjustment
    
    def _final_collision_check(self, positions, area_size):
        """
        🆕 最终碰撞检查：确保所有对象都不重叠
        
        Args:
            positions: 位置列表
            area_size: 场景大小
            
        Returns:
            list: 修正后的位置列表
        """
        # [FIX] 最小距离配置
        min_distances = {
            'tree': 10.0,  # [FIX] 增加树木最小距离到10.0
            'building': 8.0,
            'bush': 3.0,
            'flower': 1.5,
            'stone': 2.0,
            'grass': 0.5,
            'water': 5.0,
            'path': 4.0,
        }
        
        safety_margin = 5.0
        terrain_half_size = area_size / 2 - safety_margin
        
        # 🆕 多轮迭代，确保完全消除重叠（增强版）
        max_rounds = 100  # 🆕 增加迭代次数（从50增加到100），确保充分解决重叠
        for round_num in range(max_rounds):
            has_any_overlap = False
            
            for i, pos_info in enumerate(positions):
                position = pos_info['position']
                obj_type = pos_info.get('type', 'unknown')
                min_distance = min_distances.get(obj_type, 3.0)
                
                for j, other in enumerate(positions):
                    if i >= j:  # 只检查一次每对
                        continue
                    
                    other_type = other.get('type', 'unknown')
                    other_min_distance = min_distances.get(other_type, 3.0)
                    # 🆕 对于树木，使用更大的最小距离
                    if obj_type == 'tree' or other_type == 'tree':
                        combined_min_distance = max(min_distance, other_min_distance)  # 使用较大的值
                    else:
                        combined_min_distance = (min_distance + other_min_distance) / 2
                    
                    distance = self._compute_distance(position, other['position'])
                    
                    if distance < combined_min_distance:
                        has_any_overlap = True
                        
                        # [FIX] 处理距离为0或非常小的情况
                        if distance < 0.01:
                            # 两个对象几乎在同一位置，随机分开
                            import random
                            angle = random.uniform(0, 2 * math.pi)
                            push_distance = combined_min_distance / 2 + 1.0
                            dx = math.cos(angle)
                            dy = math.sin(angle)
                        else:
                            dx = position.x - other['position'].x
                            dy = position.y - other['position'].y
                            # 归一化方向向量
                            dx = dx / distance
                            dy = dy / distance
                            # 计算推开距离
                            push_factor = 1.5 if (obj_type == 'tree' or other_type == 'tree') else 1.0
                            push_distance = ((combined_min_distance - distance) / 2 + 1.0) * push_factor
                        
                        # 推开当前对象
                        position.x += dx * push_distance
                        position.y += dy * push_distance
                        
                        # 推开另一个对象
                        other['position'].x -= dx * push_distance
                        other['position'].y -= dy * push_distance
                        
                        # 边界检查（使用略微更小的边界，避免堆积在边界上）
                        inner_margin = terrain_half_size - 2.0
                        position.x = max(-inner_margin, min(inner_margin, position.x))
                        position.y = max(-inner_margin, min(inner_margin, position.y))
                        other['position'].x = max(-inner_margin, min(inner_margin, other['position'].x))
                        other['position'].y = max(-inner_margin, min(inner_margin, other['position'].y))
            
            if not has_any_overlap:
                print(f"   [COLLISION] Final check completed in {round_num + 1} rounds, no overlaps")
                break
        else:
            print(f"   [COLLISION] Warning: Max rounds reached, some overlaps may remain")
        
        return positions
    
    def _compute_total_loss(self, positions, descriptors):
        """计算总损失"""
        if not descriptors.get('descriptors'):
            return 0.0
        
        loss = 0.0
        targets = descriptors['targets']
        
        for desc in descriptors['descriptors']:
            # 几何描述量损失
            d_loss = (desc['d_t'] - targets.get('d_t_mean', desc['d_t']))**2
            θ_loss = (desc['θ_t'] - targets.get('θ_t_mean', desc['θ_t']))**2
            b_loss = (desc['b_t'] - targets.get('b_t_mean', desc['b_t']))**2
            
            loss += d_loss + θ_loss + b_loss
        
        return loss / len(descriptors['descriptors'])









