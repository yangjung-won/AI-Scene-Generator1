# 程序化模型生成说明

## 概述

当模型库中不存在某个物体时，系统会自动使用**程序化生成**创建复杂的3D模型（不是简单几何体）。

## 工作原理

### 1. 自动检测
- 模型选择器首先尝试从模型库中查找模型
- 如果模型库中没有或文件不可用，自动切换到程序化生成

### 2. 生成配置
程序化生成器会创建详细的Blender操作指令，包括：
- **复杂几何结构**：参数化分支、分层花瓣、有机形状等
- **细节处理**：表面纹理、侵蚀效果、自然分布等
- **材质配置**：PBR材质、颜色、粗糙度等

### 3. 复杂度自适应
根据LTC分析的`complexity_factor`自动调整：
- 低复杂度：简单结构，较少细节
- 高复杂度：复杂结构，丰富细节

## 支持的对象类型

### 已实现程序化生成：

1. **树 (tree)**
   - 参数化树干（锥形、分段）
   - 递归分支系统（多层级）
   - 叶子簇（自然分布）
   - 树皮细节（位移纹理）

2. **花 (flower)**
   - 分层花瓣（多层、有机形状）
   - 花蕊中心（雄蕊簇）
   - 弯曲花茎

3. **石头 (stone)**
   - 有机形状（噪声变形）
   - 表面细节（位移噪声）
   - 侵蚀图案

4. **建筑 (building)**
   - 模块化楼层
   - 窗户图案（网格布局）
   - 坡屋顶
   - 建筑细节（檐口、门、阳台）

5. **灌木 (bush)**
   - 叶子簇（自然分布）
   - 隐藏分支结构

6. **水体 (water)**
   - 波浪表面
   - 深度变化

7. **路径 (path)**
   - 不规则路径
   - 石头图案

8. **草 (grass)**
   - 草叶簇
   - 自然分布
   - 风效果

## 生成配置格式

每个程序化模型包含：

```python
{
    'type': 'procedural_tree',
    'blender_operations': [
        {
            'step': 'trunk',
            'method': 'parametric_cylinder',
            'params': {...}
        },
        {
            'step': 'branches',
            'method': 'recursive_branches',
            'params': {...}
        },
        ...
    ],
    'material': {
        'trunk': {...},
        'leaves': {...}
    },
    'metadata': {
        'generation_method': 'procedural',
        'complexity': 0.7
    }
}
```

## 在Blender插件中使用

### 检测程序化模型

```python
# 在Blender插件中
for model in selected_models['trees']:
    if model.get('type') == 'procedural':
        # 这是程序化生成的模型
        generation_config = model.get('generation_config')
        blender_ops = generation_config.get('blender_operations', [])
        
        # 执行Blender操作
        for op in blender_ops:
            execute_blender_operation(op)
```

### 执行生成操作

需要在Blender插件中实现对应的操作函数：

```python
def execute_blender_operation(operation):
    step = operation['step']
    method = operation['method']
    params = operation['params']
    
    if method == 'parametric_cylinder':
        # 创建参数化圆柱体（树干）
        create_parametric_cylinder(params)
    elif method == 'recursive_branches':
        # 创建递归分支
        create_recursive_branches(params)
    elif method == 'leaf_clusters':
        # 创建叶子簇
        create_leaf_clusters(params)
    # ... 其他方法
```

## 示例：生成复杂树

### 生成配置示例

```python
{
    'blender_operations': [
        {
            'step': 'trunk',
            'method': 'parametric_cylinder',
            'params': {
                'height': 4.2,
                'radius_base': 0.3,
                'radius_top': 0.18,
                'segments': 8,
                'taper': 0.3
            }
        },
        {
            'step': 'branches',
            'method': 'recursive_branches',
            'params': {
                'count': 15,
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
                'density': 0.8,
                'cluster_count': 30,
                'leaf_size_variation': 0.3,
                'natural_distribution': True
            }
        }
    ]
}
```

### Blender实现示例

```python
import bpy
import bmesh

def create_parametric_cylinder(params):
    """创建参数化圆柱体（树干）"""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=params['segments'],
        radius=params['radius_base'],
        depth=params['height']
    )
    trunk = bpy.context.active_object
    
    # 应用锥形（taper）
    bpy.ops.object.mode_set(mode='EDIT')
    bmesh_obj = bmesh.from_mesh(trunk.data)
    # ... 应用taper变形
    bmesh.update_edit_mesh(trunk.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return trunk

def create_recursive_branches(params):
    """创建递归分支"""
    # 实现递归分支算法
    # 使用bmesh创建复杂的分支结构
    pass

def create_leaf_clusters(params):
    """创建叶子簇"""
    # 在分支末端创建叶子簇
    # 使用粒子系统或实例化
    pass
```

## 优势

1. **自动补充**：模型库缺失时自动生成
2. **复杂模型**：不是简单几何体，而是参数化的复杂结构
3. **自适应**：根据场景复杂度调整细节
4. **可扩展**：易于添加新的生成方法

## 扩展新类型

要添加新的程序化生成类型：

1. 在`procedural_model_generator.py`中添加模板
2. 实现`_generate_complex_xxx`方法
3. 定义Blender操作步骤
4. 在Blender插件中实现对应的操作函数

## 注意事项

- 程序化生成的模型在`metadata`中标记为`'generated': True`
- `file_path`为`None`（因为是程序化生成）
- Blender插件需要实现所有`blender_operations`中的方法
- 复杂度越高，生成时间越长



























