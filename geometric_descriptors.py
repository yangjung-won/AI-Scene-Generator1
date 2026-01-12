"""
AI场景生成器 - 几何描述量模块
计算三个几何描述量：距离、方向、邻居多样性

作者: AI Team
版本: 1.0
"""

import numpy as np
import math
from collections import Counter


class GeometricDescriptors:
    """计算几何描述量"""
    
    def __init__(self, neighbor_radius=5.0):
        """
        初始化
        
        Args:
            neighbor_radius: 邻居搜索半径
        """
        self.neighbor_radius = neighbor_radius
    
    def compute_all_descriptors(self, positions, object_types, region_centroids=None):
        """
        为所有对象计算三个几何描述量
        
        Args:
            positions: 位置列表 [{'type': 'tree', 'position': Vector(...), ...}, ...]
            object_types: 对象类型列表
            region_centroids: 区域中心字典 {obj_type: Vector(...)}
        
        Returns:
            dict: 描述量和目标值
        """
        if not positions:
            return {'descriptors': [], 'targets': {}}
        
        # 如果没有提供区域中心，计算每个类型的中心
        if region_centroids is None:
            region_centroids = self._compute_region_centroids(positions, object_types)
        
        descriptors = []
        
        for pos_info in positions:
            obj_type = pos_info['type']
            position = pos_info['position']
            centroid = region_centroids.get(obj_type)
            
            if centroid is None:
                # 如果没有该类型的中心，使用全局中心
                centroid = self._compute_global_centroid(positions)
            
            # 计算三个描述量
            d_t = self.compute_distance_to_centroid(position, centroid)
            θ_t = self.compute_direction_to_centroid(position, centroid)
            
            # 找到邻居
            neighbors = self.find_neighbors(position, positions, self.neighbor_radius)
            b_t = self.compute_neighbor_diversity(position, neighbors, obj_type)
            
            descriptors.append({
                'd_t': d_t,
                'θ_t': θ_t,
                'b_t': b_t,
                'position': position,
                'type': obj_type,
                'centroid': centroid
            })
        
        # 计算目标值（用于优化）
        targets = self._compute_targets(descriptors)
        
        return {
            'descriptors': descriptors,
            'targets': targets
        }
    
    def compute_distance_to_centroid(self, position, centroid):
        """
        计算到区域中心的距离
        d_t = ||x_t - centroid||
        """
        dx = position.x - centroid.x
        dy = position.y - centroid.y
        dz = position.z - centroid.z if hasattr(position, 'z') else 0
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def compute_direction_to_centroid(self, position, centroid):
        """
        计算到中心的方向
        θ_t = arctan2(y_t - y_centroid, x_t - x_centroid)
        """
        dx = position.x - centroid.x
        dy = position.y - centroid.y
        return math.atan2(dy, dx)
    
    def find_neighbors(self, position, all_positions, radius):
        """找到半径内的邻居"""
        neighbors = []
        for other in all_positions:
            if other['position'] == position:
                continue
            
            distance = self._compute_distance(position, other['position'])
            if distance <= radius:
                neighbors.append(other)
        
        return neighbors
    
    def compute_neighbor_diversity(self, position, neighbors, object_type):
        """
        计算异类邻居比例
        b_t = 异类邻居数 / 总邻居数
        """
        if not neighbors:
            return 0.0
        
        different_type_count = sum(
            1 for n in neighbors if n['type'] != object_type
        )
        
        return different_type_count / len(neighbors)
    
    def _compute_region_centroids(self, positions, object_types):
        """计算每个对象类型的区域中心"""
        centroids = {}
        
        for obj_type in object_types:
            type_positions = [p for p in positions if p['type'] == obj_type]
            if type_positions:
                centroid = self._compute_centroid(type_positions)
                centroids[obj_type] = centroid
        
        return centroids
    
    def _compute_centroid(self, positions):
        """计算位置列表的中心"""
        if not positions:
            from scene_planner import Vector
            return Vector((0, 0, 0))
        
        x_sum = sum(p['position'].x for p in positions)
        y_sum = sum(p['position'].y for p in positions)
        z_sum = sum(p['position'].z for p in positions) if hasattr(positions[0]['position'], 'z') else 0
        
        n = len(positions)
        from scene_planner import Vector
        return Vector((x_sum/n, y_sum/n, z_sum/n))
    
    def _compute_global_centroid(self, positions):
        """计算全局中心"""
        return self._compute_centroid(positions)
    
    def _compute_distance(self, pos1, pos2):
        """计算两点距离"""
        dx = pos1.x - pos2.x
        dy = pos1.y - pos2.y
        dz = (pos1.z - pos2.z) if hasattr(pos1, 'z') and hasattr(pos2, 'z') else 0
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def _compute_targets(self, descriptors):
        """计算目标值（用于优化）"""
        if not descriptors:
            return {}
        
        d_t_values = [d['d_t'] for d in descriptors]
        θ_t_values = [d['θ_t'] for d in descriptors]
        b_t_values = [d['b_t'] for d in descriptors]
        
        return {
            'd_t_mean': np.mean(d_t_values),
            'd_t_std': np.std(d_t_values),
            'θ_t_mean': np.mean(θ_t_values),
            'θ_t_std': np.std(θ_t_values),
            'b_t_mean': np.mean(b_t_values),
            'b_t_std': np.std(b_t_values)
        }



























