# 语义增强功能说明

## 概述

本次更新大幅增强了插件的语义解析和空间布局能力，实现了以下三个核心功能：

1. **增强语义解析**：利用LTC机制解析输入指令中的成对关系和组间关系
2. **JSON数据对齐**：确保后端能完美读懂模型风格信息
3. **空间连续性推理**：在生成坐标时考虑物体间的空间依赖性，确保生成的位姿符合逻辑

## 1. 语义关系解析模块

### 新增文件：`semantic_relation_parser.py`

该模块能够解析以下类型的语义关系：

#### 成对关系（Pair Relations）
- **next_to** (旁边/附近): "树在石头旁边" / "tree next to stone"
- **around** (围绕): "花围绕石头" / "flowers around stone"
- **behind** (后面): "树在建筑后面"
- **in_front_of** (前面): "树在建筑前面"
- **on** (上面): "花在石头上"
- **under** (下面): "草在树下"
- **between** (之间): "树在建筑之间"
- **along** (沿着): "树沿着路径"
- 等等...

#### 组间关系（Group Relations）
- **circle_around** (一圈围绕): "一圈树围绕石头" / "a circle of trees around stone"
- **line_along** (一排): "一排树沿着路径"
- **cluster_near** (聚集): "花聚集在树附近"
- **scatter_around** (散布): "花散布在草地上"
- **symmetrical** (对称): "对称的树"
- **random** (随机): "随机分布"

### 使用示例

```python
from semantic_relation_parser import SemanticRelationParser

parser = SemanticRelationParser()
text = "一圈樱花树围绕一块大石头"
objects = ['tree', 'stone']

relations = parser.parse_relations(text, objects)
# 输出：
# {
#   'pair_relations': [],
#   'group_relations': [{
#     'type': 'circle_around',
#     'group_type': 'tree',
#     'center_type': 'stone',
#     'radius': 5.0,
#     'quantity': 5
#   }],
#   'relation_graph': {...}
# }
```

## 2. LTC语义映射增强

### 修改文件：`ltc_analyzer.py`

新增 `_process_semantic_relations()` 方法，将语义关系转换为空间依赖映射：

```python
spatial_dependencies = {
    'pair_constraints': [
        {
            'type': 'next_to',
            'subject': 'tree',
            'object': 'stone',
            'distance': 3.0,
            'confidence': 0.8,
            'ltc_weight': 0.7  # 自然度影响约束强度
        }
    ],
    'group_constraints': [
        {
            'type': 'circle_around',
            'group_type': 'tree',
            'center_type': 'stone',
            'radius': 5.0,
            'quantity': 5
        }
    ],
    'dependency_graph': {
        'tree': [{'depends_on': 'stone', 'relation': 'next_to', 'distance': 3.0}]
    }
}
```

## 3. 空间连续性推理

### 修改文件：`ordered_layout_optimizer.py`

#### 新增方法：

1. **`_apply_spatial_dependencies()`**: 在迭代优化前应用空间依赖约束
   - 处理成对关系：调整物体位置以满足距离要求
   - 处理组间关系：按圆形、线性、聚集等方式排列物体

2. **`_apply_spatial_constraint_in_iteration()`**: 在每次迭代中应用空间约束
   - 确保优化过程中保持语义关系

3. **`_get_direction_vector()`**: 计算方向向量
4. **`_compute_angle()`**: 计算角度

#### 工作原理：

```python
# 示例：处理"树在石头旁边"的关系
constraint = {
    'type': 'next_to',
    'subject': 'tree',
    'object': 'stone',
    'distance': 3.0
}

# 系统会：
# 1. 找到所有tree和stone对象
# 2. 为每个tree找到最近的stone
# 3. 调整tree的位置，使其距离stone恰好3.0单位
# 4. 在迭代优化中持续维护这个关系
```

#### 组间关系处理：

- **circle_around**: 将group对象按圆形排列在center对象周围
- **line_along**: 将group对象线性排列
- **cluster_near**: 将group对象聚集在center对象附近

## 4. 模型风格对齐

### 修改文件：`model_selector.py`

增强了 `_score_tree_model()` 方法，现在能够：

1. **读取模型风格**：从JSON的`style`字段读取模型风格
2. **匹配NLP识别的风格**：将模型风格与用户输入中识别的风格进行匹配
3. **风格评分**：风格匹配时大幅提高评分（+100分）

#### 支持的风格关键词：

- realistic (写实/真实/逼真)
- cartoon (卡通/可爱/动画)
- minimal (简约/简单/极简)
- natural (自然/天然)
- fantasy (奇幻/幻想/魔幻)
- modern (现代/当代)
- classical (古典/经典)
- japanese (日式/和风/禅意)
- chinese (中式/中国风)

#### 使用示例：

```json
// 模型JSON中的style字段
{
  "id": "cherry_tree_001",
  "category": "tree",
  "style": "realistic",
  "file_path": "..."
}
```

如果用户输入包含"写实风格的花园"，系统会优先选择`style: "realistic"`的模型。

## 5. 完整流程集成

### 处理流程：

```
用户输入: "一圈樱花树围绕一块大石头，写实风格"
    ↓
[NLP解析] 
  - 识别对象: ['tree', 'stone']
  - 识别风格: ['realistic']
  - 解析关系: circle_around(tree, stone)
    ↓
[LTC分析]
  - 处理语义关系 → spatial_dependencies
  - 计算复杂度、自然度等参数
    ↓
[场景规划]
  - 生成对象数量
  - 创建初始布局
    ↓
[布局优化]
  - 应用空间依赖约束
    - 将树按圆形排列在石头周围
  - 迭代优化位置
  - 确保物体贴合地面
    ↓
[模型选择]
  - 优先选择style="realistic"的模型
  - 考虑语义匹配（樱花关键词）
    ↓
[最终输出]
  - 优化后的布局
  - 选定的模型
  - 符合语义关系的位姿
```

## 技术细节

### 空间依赖约束的优先级

1. **成对关系约束**：在迭代优化前应用，确保基础关系正确
2. **组间关系约束**：在迭代优化前应用，确保组结构正确
3. **迭代优化**：在每次迭代中应用轻微调整，保持关系稳定

### 距离估计

系统根据关系类型自动估计距离：
- `next_to`: 3.0单位
- `around`: 5.0单位
- `circle_around`: 5.0单位半径
- `line_along`: 10.0单位长度

### 边界处理

所有位置调整都会考虑场景边界，确保物体不会超出场景范围。

## 测试建议

### 测试用例：

1. **成对关系测试**：
   - "树在石头旁边"
   - "花在建筑前面"
   - "草沿着路径"

2. **组间关系测试**：
   - "一圈树围绕石头"
   - "一排花沿着路径"
   - "花聚集在树附近"

3. **风格匹配测试**：
   - "写实风格的花园" → 应选择realistic模型
   - "卡通风格的花园" → 应选择cartoon模型

4. **组合测试**：
   - "一圈写实风格的樱花树围绕一块大石头"

## 版本信息

- **版本**: 4.0
- **新增模块**: `semantic_relation_parser.py`
- **增强模块**: 
  - `nlp_parser.py` (集成关系解析)
  - `ltc_analyzer.py` (语义映射)
  - `ordered_layout_optimizer.py` (空间依赖)
  - `model_selector.py` (风格匹配)

## 兼容性

- 向后兼容：如果语义关系解析失败，系统会降级到原有行为
- 可选功能：语义关系解析是可选的，不影响核心功能
















