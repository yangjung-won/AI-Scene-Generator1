"""
AI场景生成器 - 布局能量优化模块
基于能量最小化的布局优化算法

实现：
- 碎片能量 (E_frag): 惩罚微小的独立区域
- 连通性能量 (E_conn): 强制相同语义区域内的连通性
- 邻接能量 (E_adj): 惩罚不合理的语义邻接关系

作者: AI Team
版本: 1.0
"""

import numpy as np
import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import math


class LayoutEnergyOptimizer:
    """
    布局能量优化器
    使用能量最小化方法优化布局网格
    """
    
    def __init__(self, 
                 grid_size: int = 64,
                 lambda_frag: float = 1.0,
                 lambda_conn: float = 1.5,
                 lambda_adj: float = 1.2,
                 max_iterations: int = 100,
                 energy_threshold: float = 0.01):
        """
        初始化优化器
        
        Args:
            grid_size: 网格大小 (grid_size x grid_size)
            lambda_frag: 碎片能量权重
            lambda_conn: 连通性能量权重
            lambda_adj: 邻接能量权重
            max_iterations: 最大迭代次数
            energy_threshold: 能量变化阈值
        """
        self.grid_size = grid_size
        self.lambda_frag = lambda_frag
        self.lambda_conn = lambda_conn
        self.lambda_adj = lambda_adj
        self.max_iterations = max_iterations
        self.energy_threshold = energy_threshold
        
        # 语义邻接规则（定义哪些标签可以相邻）
        # 例如：tree可以靠近grass、flower，但不应该靠近water
        self.semantic_adjacency_rules = self._initialize_adjacency_rules()
        
        print(f"[OK] Layout energy optimizer initialized: grid={grid_size}x{grid_size}")
    
    def _initialize_adjacency_rules(self) -> Dict[int, Dict[int, float]]:
        """
        初始化语义邻接规则
        返回: {label_i: {label_j: penalty_score}}
        penalty_score: 0.0=允许, >0.0=惩罚
        """
        # 标签映射（简化版，实际应该从输入获取）
        # 0=empty, 1=tree, 2=flower, 3=grass, 4=stone, 5=water, 6=path, 7=building
        rules = defaultdict(dict)
        
        # 定义合理的邻接关系（低惩罚）
        reasonable_adjacencies = [
            (1, 3), (1, 2), (1, 4),  # tree near grass/flower/stone
            (2, 3), (2, 6),          # flower near grass/path
            (3, 6), (3, 4),          # grass near path/stone
            (4, 6),                  # stone near path
            (5, 1), (5, 3), (5, 4),  # water near tree/grass/stone
            (6, 1), (6, 2), (6, 3),  # path near tree/flower/grass
            (7, 6), (7, 1),          # building near path/tree
        ]
        
        # 定义不合理的邻接关系（高惩罚）
        unreasonable_adjacencies = [
            (5, 7),  # water near building (不合理)
            (7, 5),  # building near water (不合理)
        ]
        
        # 初始化所有组合为中等惩罚
        for i in range(8):
            for j in range(8):
                if i != j:
                    rules[i][j] = 0.5  # 默认中等惩罚
        
        # 设置合理邻接为低惩罚
        for i, j in reasonable_adjacencies:
            rules[i][j] = 0.0
            rules[j][i] = 0.0
        
        # 设置不合理邻接为高惩罚
        for i, j in unreasonable_adjacencies:
            rules[i][j] = 2.0
            rules[j][i] = 2.0
        
        return rules
    
    def optimize_layout(self, raw_layout_json: Dict) -> Dict:
        """
        优化布局
        
        Args:
            raw_layout_json: 原始布局JSON，包含：
                - positions: 对象位置列表
                - object_types: 对象类型列表
                - area_size: 场景大小
        
        Returns:
            dict: 优化后的布局，包含：
                - optimized_grid: 优化后的网格 (numpy array)
                - grid_coordinates: 网格坐标到世界坐标的映射
                - energy_history: 能量变化历史
                - final_energy: 最终能量值
        """
        print("[OPTIMIZING] Starting layout energy optimization...")
        
        # 1. 将原始布局转换为网格表示
        grid, label_mapping = self._layout_to_grid(raw_layout_json)
        print(f"   [GRID] Created {self.grid_size}x{self.grid_size} grid with {len(label_mapping)} labels")
        
        # 2. 初始化能量历史
        energy_history = []
        
        # 3. 迭代优化
        current_grid = grid.copy()
        previous_energy = float('inf')
        
        for iteration in range(self.max_iterations):
            # 计算当前能量
            current_energy = self._compute_total_energy(current_grid)
            energy_history.append(current_energy)
            
            # 检查终止条件
            if iteration > 0:
                energy_change = abs(current_energy - previous_energy)
                if energy_change < self.energy_threshold:
                    print(f"   [CONVERGED] Energy change {energy_change:.6f} < threshold {self.energy_threshold}")
                    break
            
            # 更新网格
            current_grid = self._update_grid(current_grid)
            
            previous_energy = current_energy
            
            if iteration % 10 == 0:
                print(f"   Iteration {iteration}/{self.max_iterations}, Energy: {current_energy:.4f}")
        
        # 4. 将优化后的网格转换回坐标
        grid_coordinates = self._grid_to_coordinates(current_grid, label_mapping, raw_layout_json)
        
        result = {
            'optimized_grid': current_grid,
            'grid_coordinates': grid_coordinates,
            'energy_history': energy_history,
            'final_energy': current_energy,
            'iterations': iteration + 1,
            'converged': abs(current_energy - previous_energy) < self.energy_threshold
        }
        
        print(f"[OK] Layout optimization completed: final_energy={current_energy:.4f}, iterations={iteration+1}")
        
        return result
    
    def _layout_to_grid(self, layout_json: Dict) -> Tuple[np.ndarray, Dict]:
        """
        将原始布局转换为网格表示
        
        Args:
            layout_json: 布局JSON
        
        Returns:
            (grid, label_mapping): 网格数组和标签映射
        """
        positions = layout_json.get('positions', [])
        area_size = layout_json.get('area_size', 40.0)
        
        # 创建空网格（0表示空）
        grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int32)
        
        # 创建标签映射：object_type -> label_id
        object_types = list(set(p.get('type', 'unknown') for p in positions))
        label_mapping = {}
        reverse_mapping = {}
        
        # 标准标签映射
        type_to_label = {
            'tree': 1,
            'flower': 2,
            'grass': 3,
            'stone': 4,
            'water': 5,
            'path': 6,
            'building': 7,
            'bush': 1  # bush使用tree的标签
        }
        
        label_id = 1
        for obj_type in object_types:
            if obj_type in type_to_label:
                label = type_to_label[obj_type]
            else:
                label = label_id
                label_id += 1
            
            label_mapping[obj_type] = label
            reverse_mapping[label] = obj_type
        
        # 将位置映射到网格
        grid_scale = self.grid_size / area_size
        
        for pos_info in positions:
            pos = pos_info.get('position')
            if not pos:
                continue
            
            # 获取位置坐标
            if hasattr(pos, 'x'):
                x, y = pos.x, pos.y
            elif isinstance(pos, (list, tuple)):
                x, y = pos[0], pos[1]
            elif isinstance(pos, dict):
                x, y = pos.get('x', 0), pos.get('y', 0)
            else:
                continue
            
            # 转换为网格坐标
            grid_x = int((x + area_size / 2) * grid_scale)
            grid_y = int((y + area_size / 2) * grid_scale)
            
            # 边界检查
            grid_x = max(0, min(self.grid_size - 1, grid_x))
            grid_y = max(0, min(self.grid_size - 1, grid_y))
            
            # 获取标签
            obj_type = pos_info.get('type', 'unknown')
            label = label_mapping.get(obj_type, 0)
            
            # 在网格中设置标签（使用小区域）
            radius = max(1, int(2 * grid_scale))  # 根据对象大小调整
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nx, ny = grid_x + dx, grid_y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        if dx*dx + dy*dy <= radius*radius:
                            if grid[ny, nx] == 0:  # 只覆盖空区域
                                grid[ny, nx] = label
        
        return grid, label_mapping
    
    def _compute_total_energy(self, grid: np.ndarray) -> float:
        """
        计算总能量
        
        E(X) = λ₁E_frag + λ₂E_conn + λ₃E_adj
        
        Args:
            grid: 网格数组
        
        Returns:
            总能量值
        """
        E_frag = self._compute_fragmentation_energy(grid)
        E_conn = self._compute_connectivity_energy(grid)
        E_adj = self._compute_adjacency_energy(grid)
        
        total_energy = (
            self.lambda_frag * E_frag +
            self.lambda_conn * E_conn +
            self.lambda_adj * E_adj
        )
        
        return total_energy
    
    def _compute_fragmentation_energy(self, grid: np.ndarray) -> float:
        """
        计算碎片能量
        惩罚微小的独立区域
        
        Args:
            grid: 网格数组
        
        Returns:
            碎片能量值
        """
        visited = np.zeros_like(grid, dtype=bool)
        fragmentation_score = 0.0
        
        for label in np.unique(grid):
            if label == 0:  # 跳过空区域
                continue
            
            # 找到所有该标签的连通区域
            regions = []
            for y in range(self.grid_size):
                for x in range(self.grid_size):
                    if grid[y, x] == label and not visited[y, x]:
                        # BFS找到连通区域
                        region = self._find_connected_region(grid, x, y, label, visited)
                        if region:
                            regions.append(region)
            
            # 计算碎片化：小区域越多，碎片化越高
            for region in regions:
                region_size = len(region)
                if region_size < 5:  # 小于5个单元的区域被认为是碎片
                    fragmentation_score += (5 - region_size) * 0.5
        
        return fragmentation_score
    
    def _compute_connectivity_energy(self, grid: np.ndarray) -> float:
        """
        计算连通性能量
        强制相同语义区域内的连通性
        
        Args:
            grid: 网格数组
        
        Returns:
            连通性能量值
        """
        connectivity_score = 0.0
        
        for label in np.unique(grid):
            if label == 0:
                continue
            
            # 找到所有该标签的连通区域
            visited = np.zeros_like(grid, dtype=bool)
            regions = []
            
            for y in range(self.grid_size):
                for x in range(self.grid_size):
                    if grid[y, x] == label and not visited[y, x]:
                        region = self._find_connected_region(grid, x, y, label, visited)
                        if region:
                            regions.append(region)
            
            # 如果有多个不连通的区域，增加惩罚
            if len(regions) > 1:
                connectivity_score += (len(regions) - 1) * 2.0
        
        return connectivity_score
    
    def _compute_adjacency_energy(self, grid: np.ndarray) -> float:
        """
        计算邻接能量
        惩罚不合理的语义邻接关系
        
        Args:
            grid: 网格数组
        
        Returns:
            邻接能量值
        """
        adjacency_score = 0.0
        
        # 检查所有相邻的单元对
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                label1 = grid[y, x]
                if label1 == 0:
                    continue
                
                # 检查四个方向的邻居
                neighbors = [
                    (x+1, y), (x-1, y), (x, y+1), (x, y-1)
                ]
                
                for nx, ny in neighbors:
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        label2 = grid[ny, nx]
                        if label2 == 0:
                            continue
                        
                        if label1 != label2:
                            # 查找邻接规则
                            penalty = self.semantic_adjacency_rules.get(label1, {}).get(label2, 0.5)
                            adjacency_score += penalty
        
        return adjacency_score
    
    def _find_connected_region(self, grid: np.ndarray, start_x: int, start_y: int, 
                               label: int, visited: np.ndarray) -> List[Tuple[int, int]]:
        """
        使用BFS找到连通区域
        
        Args:
            grid: 网格数组
            start_x, start_y: 起始坐标
            label: 标签值
            visited: 访问标记数组
        
        Returns:
            连通区域的坐标列表
        """
        region = []
        queue = [(start_x, start_y)]
        visited[start_y, start_x] = True
        
        while queue:
            x, y = queue.pop(0)
            region.append((x, y))
            
            # 检查四个方向的邻居
            neighbors = [
                (x+1, y), (x-1, y), (x, y+1), (x, y-1)
            ]
            
            for nx, ny in neighbors:
                if (0 <= nx < self.grid_size and 0 <= ny < self.grid_size and
                    grid[ny, nx] == label and not visited[ny, nx]):
                    visited[ny, nx] = True
                    queue.append((nx, ny))
        
        return region
    
    def _update_grid(self, grid: np.ndarray) -> np.ndarray:
        """
        更新网格：尝试更新边界单元以最小化能量
        
        Args:
            grid: 当前网格
        
        Returns:
            更新后的网格
        """
        new_grid = grid.copy()
        
        # 找到所有边界单元（与不同标签相邻的单元）
        boundary_cells = []
        for y in range(1, self.grid_size - 1):
            for x in range(1, self.grid_size - 1):
                current_label = grid[y, x]
                if current_label == 0:
                    continue
                
                # 检查是否有不同标签的邻居
                neighbors = [
                    grid[y+1, x], grid[y-1, x], grid[y, x+1], grid[y, x-1]
                ]
                if any(n != current_label and n != 0 for n in neighbors):
                    boundary_cells.append((x, y, current_label))
        
        # 随机打乱边界单元顺序（增加随机性）
        np.random.shuffle(boundary_cells)
        
        # 尝试更新每个边界单元
        for x, y, current_label in boundary_cells:
            # 尝试所有可能的标签
            best_label = current_label
            best_energy = float('inf')
            
            # 获取当前单元的局部能量
            test_grid = new_grid.copy()
            
            for test_label in np.unique(grid):
                if test_label == current_label:
                    continue
                
                # 尝试将标签改为test_label
                test_grid[y, x] = test_label
                
                # 计算局部能量（只计算该单元及其邻居的能量）
                local_energy = self._compute_local_energy(test_grid, x, y)
                
                if local_energy < best_energy:
                    best_energy = local_energy
                    best_label = test_label
            
            # 如果找到更好的标签，更新
            if best_label != current_label:
                new_grid[y, x] = best_label
        
        return new_grid
    
    def _compute_local_energy(self, grid: np.ndarray, x: int, y: int) -> float:
        """
        计算局部能量（只考虑单元(x,y)及其邻居）
        
        Args:
            grid: 网格数组
            x, y: 单元坐标
        
        Returns:
            局部能量值
        """
        local_energy = 0.0
        
        # 只计算该单元对总能量的贡献
        label = grid[y, x]
        if label == 0:
            return 0.0
        
        # 邻接能量贡献
        neighbors = [
            (x+1, y), (x-1, y), (x, y+1), (x, y-1)
        ]
        for nx, ny in neighbors:
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbor_label = grid[ny, nx]
                if neighbor_label != 0 and neighbor_label != label:
                    penalty = self.semantic_adjacency_rules.get(label, {}).get(neighbor_label, 0.5)
                    local_energy += self.lambda_adj * penalty
        
        return local_energy
    
    def _grid_to_coordinates(self, grid: np.ndarray, label_mapping: Dict, 
                           layout_json: Dict) -> List[Dict]:
        """
        将优化后的网格转换回坐标
        
        Args:
            grid: 优化后的网格
            label_mapping: 标签映射
            layout_json: 原始布局JSON
        
        Returns:
            优化后的坐标列表
        """
        area_size = layout_json.get('area_size', 40.0)
        grid_scale = area_size / self.grid_size
        
        # 反向映射：label -> object_type
        reverse_mapping = {v: k for k, v in label_mapping.items()}
        
        # 为每个标签找到连通区域，并计算中心坐标
        coordinates = []
        visited = np.zeros_like(grid, dtype=bool)
        
        for label in np.unique(grid):
            if label == 0:
                continue
            
            obj_type = reverse_mapping.get(label, 'unknown')
            
            # 找到所有该标签的连通区域
            for y in range(self.grid_size):
                for x in range(self.grid_size):
                    if grid[y, x] == label and not visited[y, x]:
                        region = self._find_connected_region(grid, x, y, label, visited)
                        
                        if region:
                            # 计算区域中心
                            center_x = sum(px for px, py in region) / len(region)
                            center_y = sum(py for px, py in region) / len(region)
                            
                            # 转换为世界坐标
                            world_x = (center_x / self.grid_size) * area_size - area_size / 2
                            world_y = (center_y / self.grid_size) * area_size - area_size / 2
                            
                            from scene_planner import Vector
                            coordinates.append({
                                'type': obj_type,
                                'position': Vector((world_x, world_y, 0)),
                                'region_size': len(region)
                            })
        
        return coordinates
