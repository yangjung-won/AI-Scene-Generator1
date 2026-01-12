# 橡树林生成指令

## 问题诊断和修复

已修复以下问题：
1. ✅ **scene_plan缺少nlp_result**：已修复，确保scene_plan包含nlp_result供模型选择器使用
2. ✅ **橡树模型匹配逻辑**：已添加橡树关键词识别和高优先级评分

## 推荐指令（按优先级排序）

### 指令1（最推荐）
```
A dense oak forest with majestic oak trees scattered across the landscape, the ground completely covered with lush green grass, and the terrain painted in deep dark green colors.
```

### 指令2
```
An oak grove featuring tall oak trees, lush grass covering the entire ground, creating a dark green forest floor.
```

### 指令3
```
A serene oak forest with oak trees, the ground blanketed with thick lush grass, and dark green terrain beneath the canopy.
```

### 指令4（最简单）
```
Oak trees in an oak forest, lush grass covering the ground, dark green terrain.
```

## 关键要点

1. **必须包含 "oak" 关键词**：指令中必须明确使用 "oak" 或 "oak forest" 或 "oak grove"
2. **草地关键词**：包含 "lush grass"、"grass covering the ground" 等
3. **深绿色地形**：包含 "dark green" 或 "deep dark green"

## 系统流程

1. **NLP解析**：识别 "oak" 关键词和场景类型
2. **LTC分析**：分析场景复杂度和自然度
3. **场景规划**：计算对象数量和布局（现在包含nlp_result）
4. **模型选择**：根据oak关键词优先选择 `tree_oak tree_001` 系列模型

## 模型库中的橡树模型

- `tree_oak tree_001`
- `tree_oak tree_002`
- `tree_oak tree_003`
- `tree_oak_001` (winter season)
- `tree_oak_002` (autumn season)

## 测试方法

运行测试脚本：
```bash
python generate_oak_forest_instruction.py
```



