# 地形厚度生成说明

## 概述

地形生成器现在支持**有厚度的地形**生成，特别是雪地地形，可以生成有厚度、有起伏的雪地场景。

## 新增功能

### 1. 雪地地形类型

系统新增了两种雪地地形类型：

#### `snow` (雪地)
- **默认厚度**: 1.5单位
- **起伏强度**: 2.5 (中等起伏)
- **颜色**: 雪白色 (0.95, 0.95, 0.98)
- **特点**: 有自然起伏的雪地

#### `winter` (冬季地形)
- **默认厚度**: 2.0单位（更厚）
- **起伏强度**: 2.8 (中等偏强起伏)
- **颜色**: 冬季雪白色 (0.92, 0.94, 0.96)
- **特点**: 冬季雪堆更明显，厚度更大

### 2. 厚度参数

#### 核心参数

- **`THICKNESS_ENABLED`**: 是否启用厚度模式（布尔值）
- **`SNOW_DEPTH`**: 雪地深度（0.5-3.0单位）
- **`SNOW_THICKNESS`**: 雪层厚度（与SNOW_DEPTH相同）
- **`SNOW_DRIFT`**: 雪堆起伏（0.3-0.5）
- **`THICKNESS`**: 通用厚度参数

#### 语义映射

系统会自动识别以下语义标签并应用厚度：

- `snow` / `雪` → 启用雪地厚度
- `snowy` / `雪地` → 启用雪地厚度
- `winter` / `冬天` / `冬季` → 启用冬季厚度（更厚）
- `frozen` / `冰冻` → 启用冰雪厚度

### 3. 地形匹配机制

#### 从JSON资产匹配

如果地形JSON中包含以下语义标签，系统会自动启用厚度：

```json
{
  "id": "snow_terrain_001",
  "file": "path/to/snow.blend",
  "semantic_tags": ["snow", "winter", "frozen"]
}
```

系统会：
1. 检测到 `snow` 或 `winter` 标签
2. 自动设置 `THICKNESS_ENABLED: true`
3. 根据标签类型设置默认厚度（snow=1.5, winter=2.0）
4. 添加雪地相关参数（SNOW_DEPTH, SNOW_THICKNESS, SNOW_DRIFT）

#### 程序化生成

如果没有匹配的资产，系统会根据语义参数程序化生成：

```python
semantic_params = {
    'snow': 0.8,  # 雪地强度
    'winter': 0.9  # 冬季强度
}
```

系统会：
1. 识别为 `snow` 或 `winter` 地形类型
2. 使用对应的默认参数（包含厚度）
3. 根据语义值调整厚度（0.5-3.0范围）

## 使用示例

### 示例1: 用户输入"冬天的雪地场景"

```
用户输入: "冬天的雪地场景"
    ↓
[NLP解析]
  - 识别季节: ['winter']
  - 识别场景: ['snow']
    ↓
[地形生成]
  - 匹配地形: winter类型
  - 启用厚度: True
  - 厚度值: 2.0单位
  - 起伏强度: 2.8
    ↓
[输出]
  - terrain_type: 'winter'
  - THICKNESS_ENABLED: True
  - SNOW_DEPTH: 2.0
  - SNOW_THICKNESS: 2.0
  - SNOW_DRIFT: 0.5
  - DISPLACEMENT_STRENGTH: 2.8
```

### 示例2: JSON地形资产

```json
{
  "id": "snow_field_001",
  "file": "C:/assets/snow_field.blend",
  "type": "terrain",
  "semantic_tags": ["snow", "field", "winter"]
}
```

系统输出：
```python
{
  'terrain_type': 'snow_field_001',
  'terrain_params': {
    'THICKNESS_ENABLED': True,
    'SNOW_DEPTH': 1.5,
    'SNOW_THICKNESS': 1.5,
    'SNOW_DRIFT': 0.3,
    'DISPLACEMENT_STRENGTH': 2.5,
    'base_color': '(0.95, 0.95, 0.98, 1)'
  },
  'metadata': {
    'has_thickness': True,
    'thickness_value': 1.5
  }
}
```

## 参数说明

### 厚度参数范围

| 参数 | 范围 | 说明 |
|------|------|------|
| SNOW_DEPTH | 0.5 - 3.0 | 雪地深度（单位） |
| SNOW_THICKNESS | 0.5 - 3.0 | 雪层厚度（单位） |
| SNOW_DRIFT | 0.3 - 0.5 | 雪堆起伏强度 |
| DISPLACEMENT_STRENGTH | 2.5 - 2.8 | 地形起伏强度 |

### 复杂度影响

根据LTC分析的复杂度因子，厚度会自动调整：

- **低复杂度** (0.0-0.3): 厚度 × 0.8（较薄）
- **中复杂度** (0.3-0.7): 厚度 × 1.0（标准）
- **高复杂度** (0.7-1.0): 厚度 × 1.2（较厚，变化更大）

## Blender集成

### 厚度参数在Blender中的使用

地形参数会传递给Blender插件，插件可以使用这些参数：

1. **创建基础地形平面**
2. **应用位移修改器**（使用DISPLACEMENT_STRENGTH）
3. **添加厚度**（如果THICKNESS_ENABLED为True）：
   - 使用Solidify修改器，厚度 = SNOW_DEPTH
   - 或使用体积建模创建雪层
4. **应用材质**（使用base_color）
5. **添加细节**（使用SNOW_DRIFT创建雪堆效果）

### Blender操作示例

```python
# 伪代码示例
if terrain_params.get('THICKNESS_ENABLED'):
    # 添加Solidify修改器
    solidify = terrain_obj.modifiers.new(name="SnowThickness", type='SOLIDIFY')
    solidify.thickness = terrain_params['SNOW_DEPTH']
    solidify.use_even_offset = True
    
    # 添加位移修改器（起伏）
    displace = terrain_obj.modifiers.new(name="SnowDisplace", type='DISPLACE')
    displace.strength = terrain_params['DISPLACEMENT_STRENGTH']
    displace.mid_level = 0.5
```

## 不同字段对应不同地形

系统支持以下地形类型，每个都有独特的参数：

| 输入字段 | 地形类型 | 厚度 | 起伏 | 颜色 |
|---------|---------|------|------|------|
| `snow` / `雪` | snow | 1.5 | 2.5 | 雪白 |
| `winter` / `冬天` | winter | 2.0 | 2.8 | 冬季白 |
| `grass` / `草` | grassland | 0 | 1.2 | 绿色 |
| `mountain` / `山` | mountain | 0 | 3.5 | 灰色 |
| `desert` / `沙漠` | desert | 0 | 2.0 | 沙色 |
| `rocky` / `岩石` | rocky | 0 | 3.0 | 深灰 |

## 验证

系统会在控制台输出地形生成信息：

```
🏔️ 开始生成地形...
🎯 找到匹配地形: snow_field_001 (匹配度: 0.95)
✅ 地形生成完成: snow_field_001
   [THICKNESS] 启用厚度模式，厚度: 1.5单位
   [PARAMS] SNOW_DEPTH=1.5, DISPLACEMENT_STRENGTH=2.5
```

## 版本信息

- **版本**: 2.0
- **新增功能**: 地形厚度支持
- **支持的地形**: snow, winter
- **文件**: `terrain_generator.py`

## 未来改进

1. **更多有厚度的地形**：泥地、沙地等
2. **动态厚度**：根据位置变化的厚度
3. **多层厚度**：支持多层地形（如雪+冰）
4. **厚度动画**：支持厚度随时间变化（如积雪效果）















