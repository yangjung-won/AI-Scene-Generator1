#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查JSON中是否有path模型
"""

import json
import os
import sys
import io

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

json_path = r"C:\Users\Lenovo\Desktop\updated_descriptions_json.json"

print("=" * 80)
print("检查路径模型")
print("=" * 80)

if not os.path.exists(json_path):
    print(f"[ERROR] JSON文件不存在: {json_path}")
    exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

models = data.get('models', data if isinstance(data, list) else [])

# 查找path模型
path_models = [m for m in models if m.get('category') in ['path', 'trail']]

print(f"\n找到 {len(path_models)} 个路径模型:")
if path_models:
    for i, m in enumerate(path_models, 1):
        print(f"\n{i}. ID: {m.get('id', 'unknown')}")
        print(f"   类别: {m.get('category', 'unknown')}")
        print(f"   文件路径: {m.get('file_path') or m.get('file', 'N/A')}")
        if m.get('file_path') or m.get('file'):
            file_path = m.get('file_path') or m.get('file')
            exists = os.path.exists(file_path)
            print(f"   文件存在: {'[OK]' if exists else '[NOT FOUND]'}")
else:
    print("\n[WARN] 未找到路径模型")
    print("\n注意: 如果没有路径模型，系统会使用程序化生成路径")

