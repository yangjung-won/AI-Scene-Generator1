# 有序布局算法模块说明

## 概述

本插件已集成**Transformer**和**有序布局算法**，实现了从简单的"无碰撞"布局到"有序结构空间"的升级。

## 核心特性

### 1. Transformer布局生成 (`layout_transformer.py`)
- 使用本地预训练BERT模型生成初始布局
- 无需API，完全离线工作
- 自动降级：如果transformers不可用，使用备用方法

### 2. 几何描述量计算 (`geometric_descriptors.py`)
实现了三个核心几何描述量：
- **d_t**: 到区域中心的距离 `||x_t - centroid||`
- **θ_t**: 到中心的方向 `arctan2(y_t - y_centroid, x_t - x_centroid)`
- **b_t**: 异类邻居比例 `异类邻居数 / 总邻居数`

### 3. 有序布局优化器 (`ordered_layout_optimizer.py`)
实现了三层秩序架构：

#### 拓扑秩序（Topological Order）
- 构建空间关系图 DAG
- 边类型：`constrains`, `near`, `spatial`
- 确保布局的方向性和不混乱性

#### 度量秩序（Metric Regularity）
- 使用Polar ordering参数化
- 有序正变量保证间距均匀
- 支持极坐标和径向分布

#### 语义秩序（Semantic Coherence）
- 语义rank层次：`anchor` > `secondary` > `filler`
- 高rank对象约束低rank对象的位置
- 确保布局的语义合理性

## 安装依赖

```bash
pip install transformers>=4.30.0 torch>=2.0.0
```

首次运行会自动下载BERT模型（约400MB，仅一次）。

## 使用流程

```
用户输入文本
    ↓
NLP解析 → LTC分析 → 场景规划
    ↓
Transformer生成初始布局 ⭐ 新增
    ↓
有序布局优化（三层秩序）⭐ 新增
    ↓
模型选择 → 最终输出
```

## 架构说明

### 新增模块

1. **LayoutTransformer**: 使用本地BERT模型生成初始布局
2. **GeometricDescriptors**: 计算三个几何描述量
3. **OrderedLayoutOptimizer**: 实现三层秩序优化

### 修改的模块

1. **backend_processor.py**: 
   - 版本升级到 3.0
   - 集成Transformer和优化器
   - 新增处理步骤 3.5 和 4

## 输出结果

优化后的结果包含：
- `initial_layout`: Transformer生成的初始布局
- `optimized_layout`: 经过三层秩序优化的最终布局
- `geometric_descriptors`: 几何描述量计算结果
- `spatial_graph`: 拓扑关系图（DAG）

## 降级策略

如果transformers库不可用：
- 自动使用备用布局生成方法
- 不影响其他功能
- 系统继续正常工作

## 性能说明

- Transformer模型：首次加载需要下载（约400MB）
- 优化迭代：默认50次迭代，可调整
- 计算设备：支持CPU和CUDA

## 版本信息

- 插件版本：3.0
- 新增功能：Transformer布局生成 + 有序布局优化
- 兼容性：向后兼容，不影响现有功能



























