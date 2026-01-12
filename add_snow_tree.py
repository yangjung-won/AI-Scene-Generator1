import json
import os

# 读取当前使用的模型库
current_file = r"C:\Users\Lenovo\Desktop\updated_descriptions_json.json"

print("正在读取当前模型库...")
with open(current_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

models = data.get('models', [])

# 检查是否已经有 snow_tree_002
existing_ids = [m.get('id') for m in models]
if 'snow_tree_002' in existing_ids:
    print("snow_tree_002 已经存在于模型库中！")
else:
    print("snow_tree_002 不存在，准备添加...")
    
    # 创建 snow_tree_002 模型数据（根据 backup 文件中的信息，修复格式错误）
    snow_tree_002 = {
        "id": "snow_tree_002",
        "file": "D:/assets/tree/snow_tree_002.blend",
        "category": "tree",
        "name": "snow pine tree",
        "height": 10.0,
        "width": 2.0,
        "leaf_type": "pine",
        "season": ["winter"],
        "color": "green,white",
        "style": ["cartoon", "cute", "lowpoly"],
        "semantic_tags": "forest,meadow,garden,flowerbed,river,lake,street,park,yard",
        "placement_scalable": True,
        "placement_repeatable": True,
        "placement_collision": "base",
        "condition": "fresh",
        "description": "This whimsical low-poly pine tree brings a crisp winter charm to garden spaces. Its layered, softly tapered canopies are lightly dusted with fluffy white snow, pairing the geometric, playful design with the iconic silhouette of a pine."
    }
    
    # 添加到模型列表
    models.append(snow_tree_002)
    
    # 更新 metadata
    if 'metadata' in data:
        data['metadata']['total_models'] = len(models)
    
    # 保存文件
    print(f"正在添加 snow_tree_002 到模型库...")
    with open(current_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] 成功添加 snow_tree_002！")
    print(f"   文件路径: {snow_tree_002['file']}")
    print(f"   季节: {snow_tree_002['season']}")
    print(f"   风格: {snow_tree_002['style']}")

# 验证
print(f"\n验证: 模型库中现在有 {len(models)} 个模型")
snow_trees = [m for m in models if 'snow_tree' in str(m.get('id', '')).lower()]
print(f"找到 {len(snow_trees)} 个 snow_tree 模型:")
for m in snow_trees:
    print(f"  - {m.get('id')}: season={m.get('season')}")

