"""
AI场景生成器 - 地形射线检测模块
实现物体在地形上的精确放置

核心功能：
1. 射线检测：从物体位置向下检测地形表面
2. 吸附对齐：将物体吸附到地形表面
3. 法线对齐：根据地形法线调整物体旋转
4. 厚度感知：确保物体吸附在加厚地形的顶面

作者: AI Team
版本: 1.0
"""

import math
from typing import Tuple, Optional, Dict, List
from scene_planner import Vector


class TerrainRaycast:
    """
    地形射线检测器
    用于将物体精确放置在地形表面上
    """
    
    def __init__(self, terrain_name='Base_Terrain'):
        """
        初始化射线检测器
        
        Args:
            terrain_name: 地形对象名称
        """
        self.terrain_name = terrain_name
        self.raycast_cache = {}  # 缓存射线检测结果
        
    def raycast_to_terrain(self, 
                          position: Vector, 
                          context=None,
                          max_distance: float = 100.0,
                          ray_direction: Tuple[float, float, float] = (0, 0, -1)) -> Optional[Dict]:
        """
        从指定位置向下发射射线，检测地形表面
        
        Args:
            position: 物体初始位置 (x, y, z)
            context: Blender上下文（如果可用）
            max_distance: 最大检测距离
            ray_direction: 射线方向（默认向下）
            
        Returns:
            dict: 碰撞信息 {
                'hit': bool,
                'location': Vector,  # 碰撞点位置
                'normal': Vector,    # 表面法线
                'distance': float    # 碰撞距离
            } 或 None
        """
        # 如果提供了Blender上下文，使用Blender的射线检测
        if context and hasattr(context, 'scene'):
            return self._blender_raycast(position, context, max_distance, ray_direction)
        
        # 否则使用简化的数学计算（用于后端测试）
        return self._simple_raycast(position, max_distance)
    
    def _blender_raycast(self, 
                        position: Vector,
                        context,
                        max_distance: float,
                        ray_direction: Tuple[float, float, float]) -> Optional[Dict]:
        """
        使用Blender API进行射线检测
        
        Args:
            position: 起始位置
            context: Blender上下文
            max_distance: 最大距离
            ray_direction: 射线方向
            
        Returns:
            dict: 碰撞信息或None
        """
        try:
            import bpy
            from mathutils import Vector as BlenderVector
            
            # 获取地形对象
            terrain_obj = bpy.data.objects.get(self.terrain_name)
            if not terrain_obj:
                print(f"[RAYCAST] Terrain '{self.terrain_name}' not found")
                return None
            
            # 确保地形在场景中
            if terrain_obj.name not in context.scene.objects:
                print(f"[RAYCAST] Terrain '{self.terrain_name}' not in scene")
                return None
            
            # 计算射线起点和方向
            ray_origin = BlenderVector((position.x, position.y, position.z))
            ray_direction_vec = BlenderVector(ray_direction)
            
            # 执行射线检测
            # 使用bpy.context.scene.ray_cast（Blender 2.8+）
            if hasattr(context.scene, 'ray_cast'):
                # 新API
                result, location, normal, face_index, obj, matrix = context.scene.ray_cast(
                    context.view_layer.depsgraph,
                    ray_origin,
                    ray_direction_vec,
                    distance=max_distance
                )
                
                if result and obj == terrain_obj:
                    return {
                        'hit': True,
                        'location': Vector((location.x, location.y, location.z)),
                        'normal': Vector((normal.x, normal.y, normal.z)),
                        'distance': (location - ray_origin).length,
                        'face_index': face_index,
                        'object': obj
                    }
            else:
                # 旧API（Blender 2.7）
                result, location, normal, face_index = context.scene.ray_cast(
                    ray_origin,
                    ray_direction_vec
                )
                
                if result:
                    return {
                        'hit': True,
                        'location': Vector((location.x, location.y, location.z)),
                        'normal': Vector((normal.x, normal.y, normal.z)),
                        'distance': (location - ray_origin).length,
                        'face_index': face_index
                    }
            
            return {
                'hit': False,
                'location': None,
                'normal': None,
                'distance': max_distance
            }
            
        except Exception as e:
            print(f"[ERROR] Blender raycast failed: {e}")
            return None
    
    def _simple_raycast(self, position: Vector, max_distance: float) -> Dict:
        """
        简化的射线检测（用于后端测试，不依赖Blender）
        
        假设地形在z=0平面，或根据位置估算高度
        
        Args:
            position: 起始位置
            max_distance: 最大距离
            
        Returns:
            dict: 简化的碰撞信息
        """
        # 简化：假设地形在z=0，或根据x,y计算一个简单的高度
        # 这只是一个占位实现，实际应该使用真实的地形高度图
        
        # 简单的噪声高度函数（用于测试）
        height = 0.0
        if hasattr(position, 'x') and hasattr(position, 'y'):
            # 简单的正弦波高度（模拟地形起伏）
            height = 0.5 * math.sin(position.x * 0.1) * math.cos(position.y * 0.1)
        
        hit_location = Vector((position.x, position.y, height))
        distance = abs(position.z - height) if hasattr(position, 'z') else max_distance
        
        return {
            'hit': True,
            'location': hit_location,
            'normal': Vector((0, 0, 1)),  # 假设法线向上
            'distance': min(distance, max_distance)
        }
    
    def snap_to_terrain(self,
                       position: Vector,
                       context=None,
                       offset: float = 0.0) -> Optional[Vector]:
        """
        将物体位置吸附到地形表面
        
        Args:
            position: 物体初始位置
            context: Blender上下文
            offset: 高度偏移（物体底部到地形的距离）
            
        Returns:
            Vector: 吸附后的位置，或None（如果检测失败）
        """
        raycast_result = self.raycast_to_terrain(position, context)
        
        if not raycast_result or not raycast_result.get('hit'):
            print(f"[SNAP] Raycast failed for position {position}")
            return None
        
        hit_location = raycast_result['location']
        
        # 应用偏移
        if offset != 0.0 and hit_location:
            # 沿法线方向偏移
            normal = raycast_result.get('normal', Vector((0, 0, 1)))
            offset_vector = Vector((
                normal.x * offset,
                normal.y * offset,
                normal.z * offset
            ))
            hit_location = Vector((
                hit_location.x + offset_vector.x,
                hit_location.y + offset_vector.y,
                hit_location.z + offset_vector.z
            ))
        
        return hit_location
    
    def align_to_terrain_normal(self,
                               position: Vector,
                               context=None,
                               up_axis: Tuple[float, float, float] = (0, 0, 1)) -> Optional[Tuple[float, float, float]]:
        """
        根据地形法线计算物体旋转
        
        Args:
            position: 物体位置
            context: Blender上下文
            up_axis: 物体的向上轴（默认z轴）
            
        Returns:
            tuple: 旋转角度 (rx, ry, rz) 或 None
        """
        raycast_result = self.raycast_to_terrain(position, context)
        
        if not raycast_result or not raycast_result.get('hit'):
            return None
        
        normal = raycast_result.get('normal', Vector((0, 0, 1)))
        
        # 计算旋转：使物体的向上轴对齐到地形法线
        # 简化实现：计算绕x和y轴的旋转
        
        # 计算绕x轴旋转（pitch）
        pitch = math.atan2(-normal.z, math.sqrt(normal.x**2 + normal.y**2))
        
        # 计算绕y轴旋转（yaw）
        yaw = math.atan2(normal.x, normal.y)
        
        # 绕z轴旋转保持为0（roll）
        roll = 0.0
        
        return (pitch, yaw, roll)
    
    def batch_snap_positions(self,
                           positions: List[Dict],
                           context=None,
                           object_offsets: Dict[str, float] = None) -> List[Dict]:
        """
        批量吸附多个物体位置到地形
        
        Args:
            positions: 位置列表 [{'type': 'tree', 'position': Vector(...), ...}, ...]
            context: Blender上下文
            object_offsets: 每种物体类型的偏移量 {'tree': 0.0, 'stone': 0.1, ...}
            
        Returns:
            list: 更新后的位置列表
        """
        if object_offsets is None:
            object_offsets = {
                'tree': 0.0,
                'flower': 0.0,
                'stone': 0.1,  # 石头稍微嵌入地面
                'grass': -0.05,  # 草稍微低于地面
                'bush': 0.0,
                'building': 0.0,
                'water': -0.2,  # 水体低于地面
                'path': 0.0
            }
        
        snapped_positions = []
        
        for pos_info in positions:
            obj_type = pos_info.get('type', 'unknown')
            position = pos_info.get('position')
            
            if not position:
                snapped_positions.append(pos_info)
                continue
            
            # 获取该类型的偏移量
            offset = object_offsets.get(obj_type, 0.0)
            
            # 执行吸附
            snapped_pos = self.snap_to_terrain(position, context, offset)
            
            if snapped_pos:
                # 更新位置
                updated_info = pos_info.copy()
                updated_info['position'] = snapped_pos
                
                # 计算旋转（可选）
                rotation = self.align_to_terrain_normal(position, context)
                if rotation:
                    updated_info['rotation'] = rotation
                    updated_info['aligned_to_terrain'] = True
                
                snapped_positions.append(updated_info)
            else:
                # 如果吸附失败，保持原位置
                snapped_positions.append(pos_info)
        
        return snapped_positions
    
    def check_thickness_penetration(self,
                                  position: Vector,
                                  context=None,
                                  object_height: float = 1.0) -> bool:
        """
        检查物体是否会穿透加厚地形的内部
        
        Args:
            position: 物体位置
            context: Blender上下文
            object_height: 物体高度
            
        Returns:
            bool: 是否会发生穿透
        """
        raycast_result = self.raycast_to_terrain(position, context)
        
        if not raycast_result or not raycast_result.get('hit'):
            return False
        
        # 检查地形是否有厚度
        try:
            import bpy
            terrain_obj = bpy.data.objects.get(self.terrain_name)
            if terrain_obj:
                # 检查是否有SOLIDIFY修改器
                for mod in terrain_obj.modifiers:
                    if mod.type == 'SOLIDIFY':
                        thickness = mod.thickness
                        # 如果物体底部低于地形顶部减去厚度，则穿透
                        terrain_top = raycast_result['location'].z
                        object_bottom = position.z - object_height / 2
                        
                        if object_bottom < (terrain_top - thickness):
                            return True
        except:
            pass
        
        return False









