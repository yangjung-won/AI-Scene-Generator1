"""
AI场景生成器 - 场景管理器
实现单地形管理机制，解决地形冗杂问题

核心功能：
1. 单例模式管理地形（检查'Base_Terrain'是否存在）
2. 增量更新地形参数
3. 清理冗余地形碎片

作者: AI Team
版本: 1.0
"""

import json
from typing import Dict, Optional, List


class SceneManager:
    """
    场景管理器 - 单例模式管理地形和场景对象
    解决地形冗杂、物体悬空、模型调用不准确等问题
    """
    
    def __init__(self):
        """初始化场景管理器"""
        self.terrain_name = 'Base_Terrain'  # 标准地形名称
        self.terrain_object = None  # 当前地形对象引用
        self.scene_objects = {}  # 场景对象字典 {name: object}
        self.terrain_params_history = []  # 地形参数历史
        
    def check_terrain_exists(self, context=None):
        """
        检查场景中是否已存在'Base_Terrain'地形
        
        Args:
            context: Blender上下文（如果可用）
            
        Returns:
            bool: 地形是否存在
            object: 地形对象（如果存在）
        """
        # 如果提供了Blender上下文，直接检查
        if context and hasattr(context, 'scene'):
            try:
                import bpy
                if self.terrain_name in bpy.data.objects:
                    terrain_obj = bpy.data.objects[self.terrain_name]
                    self.terrain_object = terrain_obj
                    print(f"[TERRAIN] Found existing terrain: {self.terrain_name}")
                    return True, terrain_obj
            except:
                pass
        
        # 如果没有上下文或检查失败，返回状态
        if self.terrain_object is not None:
            return True, self.terrain_object
        
        return False, None
    
    def should_create_new_terrain(self, semantic_params: Dict, context=None) -> bool:
        """
        判断是否需要创建新地形
        
        规则：
        1. 如果地形不存在，需要创建
        2. 如果地形存在但语义参数变化很大，可能需要更新
        3. 如果用户明确要求"扩大地形"或"改变风格"，需要更新
        
        Args:
            semantic_params: 语义参数
            context: Blender上下文
            
        Returns:
            bool: 是否需要创建新地形
        """
        exists, terrain_obj = self.check_terrain_exists(context)
        
        if not exists:
            print("[TERRAIN] No existing terrain found, will create new")
            return True
        
        # 检查语义参数是否有重大变化
        if self.terrain_params_history:
            last_params = self.terrain_params_history[-1]
            if self._has_major_terrain_change(last_params, semantic_params):
                print("[TERRAIN] Major terrain change detected, will update existing")
                return False  # 不创建新地形，而是更新现有地形
        
        print("[TERRAIN] Using existing terrain, will update if needed")
        return False
    
    def _has_major_terrain_change(self, old_params: Dict, new_params: Dict) -> bool:
        """
        判断地形参数是否有重大变化
        
        Args:
            old_params: 旧参数
            new_params: 新参数
            
        Returns:
            bool: 是否有重大变化
        """
        # 检查关键语义标签的变化
        key_tags = ['mountain', 'desert', 'snow', 'winter', 'grassland', 'cave', 'water']
        
        for tag in key_tags:
            old_value = old_params.get(tag, 0.0)
            new_value = new_params.get(tag, 0.0)
            
            # 如果某个关键标签从无到有或变化超过0.5，认为是重大变化
            if abs(new_value - old_value) > 0.5:
                return True
        
        return False
    
    def update_terrain(self, terrain_params: Dict, context=None):
        """
        更新现有地形的参数
        
        Args:
            terrain_params: 地形参数
            context: Blender上下文
            
        Returns:
            bool: 是否更新成功
        """
        exists, terrain_obj = self.check_terrain_exists(context)
        
        if not exists:
            print("[TERRAIN] Cannot update: terrain does not exist")
            return False
        
        # 更新地形参数
        if context and hasattr(context, 'scene'):
            try:
                import bpy
                terrain_obj = bpy.data.objects.get(self.terrain_name)
                if terrain_obj:
                    # 更新地形材质和参数
                    self._apply_terrain_params(terrain_obj, terrain_params, context)
                    print(f"[TERRAIN] Updated terrain parameters: {terrain_params.get('terrain_type', 'unknown')}")
                    return True
            except Exception as e:
                print(f"[ERROR] Failed to update terrain: {e}")
                return False
        
        # 记录参数历史
        self.terrain_params_history.append(terrain_params)
        return True
    
    def _apply_terrain_params(self, terrain_obj, terrain_params: Dict, context):
        """
        应用地形参数到Blender对象
        
        Args:
            terrain_obj: Blender地形对象
            terrain_params: 地形参数
        """
        try:
            import bpy
            
            # 更新材质颜色
            if 'base_color' in terrain_params:
                # 解析颜色字符串 "(r, g, b, a)"
                color_str = terrain_params['base_color']
                if isinstance(color_str, str) and color_str.startswith('('):
                    color_str = color_str.strip('()')
                    color_values = [float(x.strip()) for x in color_str.split(',')]
                    if len(color_values) >= 3:
                        # 创建或更新材质
                        if not terrain_obj.data.materials:
                            mat = bpy.data.materials.new(name=f"{self.terrain_name}_Material")
                            terrain_obj.data.materials.append(mat)
                        else:
                            mat = terrain_obj.data.materials[0]
                        
                        mat.use_nodes = True
                        if mat.node_tree:
                            bsdf = mat.node_tree.nodes.get('Principled BSDF')
                            if bsdf:
                                # 🆕 应用颜色（确保alpha通道正确）
                                alpha = color_values[3] if len(color_values) > 3 else 1.0
                                bsdf.inputs['Base Color'].default_value = (
                                    color_values[0],
                                    color_values[1],
                                    color_values[2],
                                    alpha
                                )
                                print(f"[TERRAIN] Updated terrain color to: ({color_values[0]:.2f}, {color_values[1]:.2f}, {color_values[2]:.2f})")
            
            # 更新位移强度
            if 'DISPLACEMENT_STRENGTH' in terrain_params:
                for mod in terrain_obj.modifiers:
                    if mod.type == 'DISPLACE':
                        mod.strength = terrain_params['DISPLACEMENT_STRENGTH']
                        break
            
            # 更新厚度（如果有）
            if terrain_params.get('THICKNESS_ENABLED', False):
                thickness = terrain_params.get('THICKNESS', 0.0) or terrain_params.get('SNOW_DEPTH', 0.0)
                for mod in terrain_obj.modifiers:
                    if mod.type == 'SOLIDIFY':
                        mod.thickness = thickness
                        break
            
        except Exception as e:
            print(f"[WARN] Could not apply all terrain params: {e}")
    
    def clear_redundant_terrain(self, context=None):
        """
        清理冗余的地形碎片
        
        查找所有名称包含'terrain'、'Terrain'、'地形'的对象，
        除了'Base_Terrain'之外全部删除
        
        Args:
            context: Blender上下文
            
        Returns:
            int: 清理的对象数量
        """
        if not context or not hasattr(context, 'scene'):
            print("[WARN] Cannot clear terrain: no Blender context")
            return 0
        
        try:
            import bpy
            
            removed_count = 0
            # 🆕 扩展关键词列表，包括Ground_Plane等常见名称（更全面的清理）
            terrain_keywords = [
                'terrain', 'Terrain', '地形', 'Terrain_', 'terrain_',
                'Ground_Plane', 'ground_plane', 'GroundPlane', 'groundplane',
                'Ground', 'ground', 'Plane', 'plane', 'Base_Plane', 'base_plane',
                'Terrain_Plane', 'terrain_plane', 'TerrainPlane',
                'Grid', 'grid', 'Mesh', 'mesh',
                # 🆕 添加更多可能的变体
                'GroundPlane', 'GROUND_PLANE', 'GROUNDPLANE',
                'Plane.001', 'Plane.002', 'Plane.003',  # Blender自动命名的副本
                'Ground_Plane.001', 'Ground_Plane.002',  # 副本
                'terrain_block', 'Terrain_Block', 'terrain_block',
                'land', 'Land', 'LAND', 'landscape', 'Landscape'
            ]
            
            # 🆕 也检查对象类型（mesh类型且名称可疑的对象）
            for obj in list(bpy.data.objects):
                obj_name = obj.name
                
                # 跳过Base_Terrain
                if obj_name == self.terrain_name:
                    continue
                
                # 检查1：名称包含地形关键词
                name_match = any(keyword in obj_name for keyword in terrain_keywords)
                
                # 检查2：对象类型是MESH且可能是地形（平面形状）
                is_mesh_terrain = False
                if obj.type == 'MESH' and obj.data:
                    # 检查是否是平面形状（顶点数量少，主要是平面）
                    try:
                        vert_count = len(obj.data.vertices)
                        # 🆕 更严格的检查：如果顶点数在合理范围内（可能是地形网格），且名称可疑
                        # 或者对象位置在原点附近（可能是默认地形）
                        is_at_origin = abs(obj.location.x) < 0.1 and abs(obj.location.y) < 0.1 and abs(obj.location.z) < 0.1
                        if (4 <= vert_count <= 10000 and name_match) or (is_at_origin and name_match):
                            is_mesh_terrain = True
                    except:
                        pass
                
                # 🆕 检查3：如果对象名称以数字结尾（如Plane.001），且包含地形关键词，也删除
                is_numbered_copy = False
                if name_match:
                    # 检查是否是Blender自动命名的副本（如Plane.001, Ground_Plane.002等）
                    import re
                    if re.search(r'\.\d{3,}$', obj_name):  # 以.001, .002等结尾
                        is_numbered_copy = True
                
                # 如果匹配，删除
                if name_match or is_mesh_terrain or is_numbered_copy:
                    print(f"[CLEANUP] Removing redundant terrain: {obj_name} (type: {obj.type})")
                    bpy.data.objects.remove(obj, do_unlink=True)
                    removed_count += 1
            
            if removed_count > 0:
                print(f"[CLEANUP] Removed {removed_count} redundant terrain objects")
            else:
                print("[CLEANUP] No redundant terrain objects found")
            
            return removed_count
            
        except Exception as e:
            print(f"[ERROR] Failed to clear redundant terrain: {e}")
            return 0
    
    def register_terrain(self, terrain_obj, context=None):
        """
        注册新创建的地形对象
        
        Args:
            terrain_obj: 地形对象
            context: Blender上下文
        """
        try:
            import bpy
            
            # 确保对象名称是'Base_Terrain'
            if terrain_obj.name != self.terrain_name:
                terrain_obj.name = self.terrain_name
            
            self.terrain_object = terrain_obj
            self.scene_objects[self.terrain_name] = terrain_obj
            
            print(f"[TERRAIN] Registered terrain: {self.terrain_name}")
            
        except Exception as e:
            print(f"[ERROR] Failed to register terrain: {e}")
    
    def get_terrain_info(self, context=None) -> Dict:
        """
        获取当前地形信息
        
        Args:
            context: Blender上下文
            
        Returns:
            dict: 地形信息
        """
        exists, terrain_obj = self.check_terrain_exists(context)
        
        if not exists:
            return {
                'exists': False,
                'name': self.terrain_name,
                'object': None
            }
        
        info = {
            'exists': True,
            'name': self.terrain_name,
            'object': terrain_obj
        }
        
        # 尝试获取地形参数
        if terrain_obj and hasattr(terrain_obj, 'data'):
            try:
                import bpy
                # 获取材质信息
                if terrain_obj.data.materials:
                    mat = terrain_obj.data.materials[0]
                    info['material'] = mat.name
                
                # 获取修改器信息
                modifiers = [mod.name for mod in terrain_obj.modifiers]
                info['modifiers'] = modifiers
                
            except:
                pass
        
        return info
    
    def prepare_for_experiment(self, context=None):
        """
        为实验准备场景：清理所有旧地形和对象
        
        Args:
            context: Blender上下文
            
        Returns:
            dict: 清理结果
        """
        result = {
            'terrain_removed': 0,
            'objects_removed': 0
        }
        
        # 清理冗余地形
        result['terrain_removed'] = self.clear_redundant_terrain(context)
        
        # 可以扩展：清理其他实验相关的对象
        # result['objects_removed'] = self.clear_experiment_objects(context)
        
        print(f"[EXPERIMENT] Scene prepared: removed {result['terrain_removed']} terrain objects")
        
        return result

