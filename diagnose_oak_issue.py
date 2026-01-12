# -*- coding: utf-8 -*-
"""
诊断oak模型选择问题
"""
import json
import os

# 加载JSON模型库
json_path = r"C:\Users\Lenovo\Desktop\updated_descriptions_json.json"

print("=" * 60)
print("诊断oak模型选择问题")
print("=" * 60)

# 1. 检查JSON文件是否存在
if not os.path.exists(json_path):
    print(f"[ERROR] JSON文件不存在: {json_path}")
    exit(1)

# 2. 加载JSON数据
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

if 'models' in data:
    models = data['models']
else:
    models = data if isinstance(data, list) else []

print(f"[INFO] 总模型数: {len(models)}")

# 3. 筛选tree类别的模型
tree_models = [m for m in models if m.get('category') == 'tree']
print(f"[INFO] tree类别模型数: {len(tree_models)}")

# 4. 查找所有包含"oak"的模型
print("\n" + "=" * 60)
print("搜索包含 'oak' 的模型")
print("=" * 60)

oak_models = []
for model in tree_models:
    model_id = str(model.get('id', '')).lower()
    model_name = str(model.get('name', '')).lower()
    model_file = str(model.get('file', '') or model.get('file_path', '')).lower()
    model_desc = str(model.get('description', '')).lower()
    
    # 检查是否包含oak
    if 'oak' in model_id or 'oak' in model_name or 'oak' in model_file or 'oak' in model_desc:
        oak_models.append(model)
        print(f"\n[OAK MODEL FOUND]")
        print(f"  ID: {model.get('id')}")
        print(f"  Name: {model.get('name')}")
        print(f"  File: {model.get('file') or model.get('file_path')}")
        print(f"  Category: {model.get('category')}")

print(f"\n[SUMMARY] 找到 {len(oak_models)} 个oak模型")

# 5. 显示前10个tree模型的ID和文件路径
print("\n" + "=" * 60)
print("前10个tree模型")
print("=" * 60)
for i, model in enumerate(tree_models[:10]):
    print(f"{i+1}. ID: {model.get('id')}")
    print(f"   File: {model.get('file') or model.get('file_path')}")
    print(f"   Available: {os.path.exists(str(model.get('file') or model.get('file_path') or ''))}")

# 6. 检查oak模型文件是否存在
print("\n" + "=" * 60)
print("检查oak模型文件是否存在")
print("=" * 60)

for model in oak_models:
    file_path = model.get('file') or model.get('file_path')
    if file_path:
        # 处理路径格式
        file_path_check = file_path.replace('/', '\\')
        exists = os.path.exists(file_path_check)
        print(f"[{'OK' if exists else 'MISSING'}] {file_path}")
    else:
        print(f"[NO PATH] {model.get('id')}")

# 7. 测试模型选择器
print("\n" + "=" * 60)
print("测试模型选择器")
print("=" * 60)

from model_selector import ModelSelector
selector = ModelSelector()

# 创建模拟的scene_plan
test_scene_plan = {
    'object_counts': {'tree': 5},
    'nlp_result': {
        'original_text': 'A dense oak forest with oak trees scattered across the landscape.',
        'scene_type': 'forest',
        'styles': [],
        'seasons': []
    },
    'planning_metadata': {}
}

print(f"\n[TEST] 输入文本: {test_scene_plan['nlp_result']['original_text']}")
print(f"[TEST] 请求树木数量: 5")

# 调用选择器
selected_trees = selector._select_tree_models(5, test_scene_plan)

print(f"\n[RESULT] 选择了 {len(selected_trees)} 棵树:")
for i, tree in enumerate(selected_trees):
    tree_id = tree.get('id', 'unknown')
    tree_file = tree.get('file') or tree.get('file_path', 'N/A')
    tree_type = tree.get('type', 'library')
    is_oak = 'oak' in tree_id.lower() or 'oak' in str(tree_file).lower()
    print(f"  {i+1}. ID: {tree_id}")
    print(f"     File: {tree_file}")
    print(f"     Type: {tree_type}")
    print(f"     Is Oak: {is_oak}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
