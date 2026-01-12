# -*- coding: utf-8 -*-
import json
import os

json_path = r"C:\Users\Lenovo\Desktop\updated_descriptions_json.json"

print(f"Checking: {json_path}")
print(f"Exists: {os.path.exists(json_path)}")

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

models = data if isinstance(data, list) else data.get('models', [])
print(f"Total models: {len(models)}")

# Find oak and tree models
oak_models = []
tree_models = []

for m in models:
    model_id = str(m.get('id', '')).lower()
    model_name = str(m.get('name', '')).lower()
    model_file = str(m.get('file', '') or m.get('file_path', '')).lower()
    category = str(m.get('category', '')).lower()
    
    if category == 'tree' or 'tree' in model_id:
        tree_models.append(m)
        if 'oak' in model_id or 'oak' in model_name or 'oak' in model_file:
            oak_models.append(m)

print(f"\nTree models: {len(tree_models)}")
print(f"Oak models: {len(oak_models)}")

if oak_models:
    print("\nOak models found:")
    for m in oak_models:
        print(f"  ID: {m.get('id')}")
        print(f"  File: {m.get('file') or m.get('file_path')}")
        file_path = m.get('file') or m.get('file_path')
        if file_path:
            exists = os.path.exists(file_path)
            print(f"  File exists: {exists}")
        print()
else:
    print("\nNO OAK MODELS FOUND!")
    print("\nAll tree model IDs:")
    for m in tree_models:
        print(f"  {m.get('id')} -> {m.get('file') or m.get('file_path')}")

