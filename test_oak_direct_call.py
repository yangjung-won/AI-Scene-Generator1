"""
测试直接调用oak模型
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接检查模型库中的oak模型
json_path = r"C:\Users\Lenovo\Desktop\updated_descriptions_json.json"

print("=" * 80)
print("检查Oak模型在模型库中的状态")
print("=" * 80)

if not os.path.exists(json_path):
    print(f"[ERROR] JSON文件不存在: {json_path}")
    exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

models = data.get('models', data if isinstance(data, list) else [])

# 查找oak模型
oak_models = []
for m in models:
    if m.get('category') == 'tree':
        model_id = str(m.get('id', '')).lower()
        model_name = str(m.get('name', '')).lower()
        if 'oak' in model_id or 'oak' in model_name:
            oak_models.append(m)

print(f"\n找到 {len(oak_models)} 个Oak模型:\n")

for i, m in enumerate(oak_models, 1):
    model_id = m.get('id', 'unknown')
    model_name = m.get('name', 'unknown')
    file_path = m.get('file') or m.get('file_path', 'N/A')
    
    # 检查文件是否存在
    exists = False
    if file_path and file_path != 'N/A':
        # 处理路径格式
        if '/' in file_path:
            file_path_win = file_path.replace('/', os.sep)
        else:
            file_path_win = file_path
        
        exists = os.path.exists(file_path_win)
        if not exists:
            # 尝试原始路径
            exists = os.path.exists(file_path)
    
    print(f"{i}. ID: {model_id}")
    print(f"   Name: {model_name}")
    print(f"   File: {file_path}")
    print(f"   文件存在: {'[OK]' if exists else '[NOT FOUND]'}")
    
    if exists:
        try:
            file_size = os.path.getsize(file_path_win if '/' in file_path else file_path)
            print(f"   文件大小: {file_size:,} bytes")
        except:
            pass
    print()

# 测试模型选择器
print("=" * 80)
print("测试模型选择器")
print("=" * 80)

from model_selector import ModelSelector

model_selector = ModelSelector()

# 检查模型选择器加载的oak模型
selector_oak_models = [m for m in model_selector.models_data 
                      if m.get('category') == 'tree' and 
                      ('oak' in str(m.get('id', '')).lower() or 'oak' in str(m.get('name', '')).lower())]

print(f"\n模型选择器加载了 {len(selector_oak_models)} 个Oak模型:\n")

for i, m in enumerate(selector_oak_models, 1):
    model_id = m.get('id', 'unknown')
    is_available = model_selector._is_model_available(m)
    print(f"{i}. {model_id} - 可用: {'[YES]' if is_available else '[NO]'}")
    if not is_available:
        file_path = m.get('file') or m.get('file_path', '')
        print(f"   文件路径: {file_path}")

print("\n" + "=" * 80)
print("结论")
print("=" * 80)

if selector_oak_models:
    available_count = sum(1 for m in selector_oak_models if model_selector._is_model_available(m))
    print(f"✓ 找到 {len(selector_oak_models)} 个Oak模型")
    print(f"✓ 其中 {available_count} 个模型可用")
    if available_count > 0:
        print("\n✓ 系统应该能够调用这些Oak模型")
        print("\n推荐使用的指令（确保包含'oak'关键词）:")
        print("  - 'A dense oak forest with oak trees'")
        print("  - 'Oak trees in an oak forest'")
        print("  - 'An oak grove with oak trees'")
    else:
        print("\n✗ 所有Oak模型都不可用（文件不存在或路径错误）")
        print("  需要检查文件路径是否正确")
else:
    print("✗ 模型选择器未加载任何Oak模型")


