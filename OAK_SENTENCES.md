# Oak模型调用指令

## 推荐指令（按优先级排序）

### 指令1（最推荐 - 最明确）
```
A dense oak forest consisting exclusively of oak trees, with majestic oak trees scattered throughout the landscape, the ground completely covered with lush green grass, and the terrain painted in deep dark green colors.
```

### 指令2（强调oak）
```
An oak grove featuring tall oak trees, lush grass covering the entire ground, creating a dark green forest floor beneath the oak canopy.
```

### 指令3（简洁明确）
```
Oak trees only in an oak forest, lush grass covering the ground, dark green terrain. No other tree types, only oak trees.
```

### 指令4（强调排除其他树）
```
A pure oak forest with oak trees exclusively, no pine trees, no maple trees, no tropical trees, only oak trees. The ground is covered with lush grass and the terrain is deep dark green.
```

### 指令5（最简单）
```
Oak forest with oak trees, lush grass, dark green terrain.
```

### 指令6（详细描述）
```
A serene oak forest landscape with multiple oak trees distributed across the scene. The ground is completely covered with lush green grass, and the terrain features a deep dark green color. Only oak trees are present in this forest.
```

### 指令7（强调oak grove）
```
An oak grove with oak trees, the ground blanketed with thick lush grass, and dark green terrain beneath the oak canopy.
```

### 指令8（最直接）
```
Create an oak forest with oak trees. Ground covered with lush grass. Terrain is dark green.
```

## 关键要点

1. **必须包含 "oak" 关键词**：指令中必须明确使用以下关键词之一：
   - "oak"
   - "oak tree"
   - "oak forest"
   - "oak grove"

2. **重复强调**：多次使用 "oak" 关键词可以提高匹配权重

3. **明确排除其他树**（可选）：可以添加 "no pine", "no maple", "only oak trees" 等

4. **其他场景元素**（可选）：
   - "lush grass" - 草地
   - "dark green" 或 "deep dark green" - 深绿色地形

## 系统匹配逻辑

系统会检查以下字段是否包含 "oak"：
- 模型ID：`tree_oak tree_001` ✓
- 模型名称：`oak tree` ✓
- 文件路径：`D:/assets/tree/tree_oak tree_001.blend` ✓

当检测到 "oak" 关键词时：
- Oak模型评分 +500（最高优先级）
- 非Oak模型评分 -200（大幅降低）
- 强制从Oak模型中选择（排除非Oak模型）

## 可调用的Oak模型

根据模型库，以下模型会被调用：
- `tree_oak tree_001`
- `tree_oak tree_002`
- `tree_oak tree_003`
- `tree_oak_001` (winter season)
- `tree_oak_002` (autumn season)

## 测试建议

使用指令1或指令3进行测试，它们最明确且包含足够的oak关键词。


