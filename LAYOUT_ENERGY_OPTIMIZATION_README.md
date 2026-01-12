# 布局能量优化模块说明

## 概述

本模块实现了基于能量最小化的布局优化算法，用于改进Transformer生成的初始布局，减少不理想的结构缺陷。

## 核心功能

### 1. 布局表示 (Layout Representation)

布局被表示为一个语义标签网格 $\mathbf{X} = \{ x_p \mid p \in \Omega \}$，其中：
- 每个网格单元 $x_p$ 被分配一个来自集合 $\mathcal{C} = \{1, \dots, K\}$ 的语义标签
- $\Omega$ 代表整个网格区域
- 使用2D numpy数组实现，默认大小为 64×64

### 2. 能量函数 (Energy Function)

总能量 $E(\mathbf{X})$ 是以下三个组件的加权之和：

$$E(\mathbf{X}) = \lambda_1 E_{\text{frag}} + \lambda_2 E_{\text{conn}} + \lambda_3 E_{\text{adj}}$$

#### 2.1 碎片能量 ($E_{\text{frag}}$)

**目标**：惩罚微小的独立区域

**实现**：
- 使用BFS找到所有连通区域
- 对于每个标签，计算其连通区域的数量和大小
- 小于5个单元的区域被认为是碎片
- 碎片能量 = $\sum_{\text{small regions}} (5 - \text{region\_size}) \times 0.5$

**默认权重**：$\lambda_1 = 1.0$

#### 2.2 连通性能量 ($E_{\text{conn}}$)

**目标**：强制相同语义区域内的连通性

**实现**：
- 对于每个标签，找到所有不连通的区域
- 如果有多个不连通的区域，增加惩罚
- 连通性能量 = $(\text{region\_count} - 1) \times 2.0$

**默认权重**：$\lambda_2 = 1.5$

#### 2.3 邻接能量 ($E_{\text{adj}}$)

**目标**：惩罚不合理的语义邻接关系

**实现**：
- 检查所有相邻的单元对
- 根据语义邻接规则计算惩罚分数
- 合理的邻接：惩罚 = 0.0
- 不合理的邻接：惩罚 = 2.0
- 默认邻接：惩罚 = 0.5

**语义邻接规则示例**：
- `tree` 可以靠近 `grass`, `flower`, `stone` (合理)
- `water` 不应该靠近 `building` (不合理)
- `path` 可以靠近 `tree`, `flower`, `grass` (合理)

**默认权重**：$\lambda_3 = 1.2$

### 3. 优化规则 (Optimization Rule)

优化过程根据能量函数迭代更新每个网格单元的标签 $x_p$。

#### 3.1 边界单元识别

在每次迭代中，算法识别所有边界单元（与不同标签相邻的单元）。

#### 3.2 标签更新

对于每个边界单元 $x_p$，算法尝试所有可能的标签 $k$，选择使局部能量最小化的标签：

$$x_p^{(t+1)} = \arg\min_k E(\mathbf{X}_{p \leftarrow k}^{(t)})$$

其中 $\mathbf{X}_{p \leftarrow k}^{(t)}$ 表示将单元 $p$ 的标签改为 $k$ 后的布局。

#### 3.3 局部能量计算

为了效率，只计算单元 $p$ 及其邻居的局部能量贡献，而不是整个网格的能量。

### 4. 终止条件 (Termination Criteria)

优化过程在满足以下任一条件时停止：

1. **最大迭代次数**：达到 $T_{\max} = 100$ 次迭代
2. **能量收敛**：连续迭代之间的能量变化小于阈值 $\epsilon = 0.01$：

$$\left| E(\mathbf{X}^{(t)}) - E(\mathbf{X}^{(t-1)}) \right| < \epsilon$$

## 使用示例

### 基本使用

```python
from layout_energy_optimizer import LayoutEnergyOptimizer

# 创建优化器
optimizer = LayoutEnergyOptimizer(
    grid_size=64,
    lambda_frag=1.0,
    lambda_conn=1.5,
    lambda_adj=1.2,
    max_iterations=100,
    energy_threshold=0.01
)

# 准备布局JSON
raw_layout = {
    'positions': [
        {'type': 'tree', 'position': Vector((10, 10, 0))},
        {'type': 'flower', 'position': Vector((15, 15, 0))},
        {'type': 'grass', 'position': Vector((20, 20, 0))}
    ],
    'area_size': 40.0
}

# 执行优化
result = optimizer.optimize_layout(raw_layout)

# 获取结果
optimized_grid = result['optimized_grid']
grid_coordinates = result['grid_coordinates']
energy_history = result['energy_history']
final_energy = result['final_energy']
```

### 结果结构

```python
{
    'optimized_grid': np.ndarray,  # 优化后的网格 (64x64)
    'grid_coordinates': [          # 优化后的坐标列表
        {
            'type': 'tree',
            'position': Vector((x, y, z)),
            'region_size': 15
        },
        ...
    ],
    'energy_history': [0.5, 0.4, 0.3, ...],  # 能量变化历史
    'final_energy': 0.25,                     # 最终能量值
    'iterations': 45,                         # 实际迭代次数
    'converged': True                          # 是否收敛
}
```

## 参数调整

### 网格大小 (grid_size)

- **默认值**：64
- **影响**：更大的网格提供更高的分辨率，但计算成本更高
- **建议**：根据场景大小调整，场景越大，网格应该越大

### 能量权重

- **lambda_frag** (默认1.0)：控制碎片惩罚的强度
- **lambda_conn** (默认1.5)：控制连通性要求的强度
- **lambda_adj** (默认1.2)：控制邻接关系惩罚的强度

**调整建议**：
- 如果布局过于碎片化，增加 `lambda_frag`
- 如果区域不连通，增加 `lambda_conn`
- 如果语义邻接不合理，增加 `lambda_adj`

### 迭代参数

- **max_iterations** (默认100)：最大迭代次数
- **energy_threshold** (默认0.01)：能量收敛阈值

## 集成到后端

该模块已集成到 `backend_processor.py` 中，作为步骤4.5执行：

```
步骤1: NLP解析
步骤2: LTC分析
步骤3: 场景规划
步骤3.5: Transformer生成初始布局
步骤4: 有序布局优化
步骤4.5: 🆕 布局能量优化
步骤5: 模型选择
```

## 算法流程

```
1. 将原始布局转换为网格表示
   ↓
2. 初始化能量历史
   ↓
3. 迭代优化循环：
   a. 计算当前总能量
   b. 检查终止条件
   c. 识别边界单元
   d. 对每个边界单元：
      - 尝试所有可能的标签
      - 选择使局部能量最小的标签
      - 更新网格
   ↓
4. 将优化后的网格转换回坐标
   ↓
5. 返回优化结果
```

## 性能考虑

- **时间复杂度**：O(T × B × K × N)
  - T: 迭代次数
  - B: 边界单元数量
  - K: 标签数量
  - N: 邻居数量（通常为4）

- **空间复杂度**：O(G²)
  - G: 网格大小

- **优化建议**：
  - 使用较小的网格大小（如果场景较小）
  - 减少最大迭代次数（如果不需要高精度）
  - 调整能量阈值（允许更早收敛）

## 语义邻接规则

系统预定义了语义邻接规则，但可以根据需要自定义：

```python
# 合理的邻接（低惩罚）
reasonable_adjacencies = [
    (tree, grass), (tree, flower), (tree, stone),
    (flower, grass), (flower, path),
    (grass, path), (grass, stone),
    (water, tree), (water, grass), (water, stone),
    (path, tree), (path, flower), (path, grass),
    (building, path), (building, tree)
]

# 不合理的邻接（高惩罚）
unreasonable_adjacencies = [
    (water, building),  # 水不应该靠近建筑
]
```

## 版本信息

- **版本**: 1.0
- **文件**: `layout_energy_optimizer.py`
- **依赖**: numpy, scene_planner

## 未来改进

1. **自适应权重**：根据布局特征自动调整能量权重
2. **多尺度优化**：在不同分辨率下进行优化
3. **并行计算**：并行处理边界单元更新
4. **更复杂的邻接规则**：支持方向性邻接（如"树在建筑前面"）
















