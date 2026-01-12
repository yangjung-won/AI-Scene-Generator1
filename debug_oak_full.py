# -*- coding: utf-8 -*-
"""
Debug oak tree selection - trace the entire flow
"""
import json
import os
import sys

# Set encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("DEBUG: Oak Tree Selection Full Trace")
print("=" * 60)

# Step 1: Check model library for oak models
print("\n[STEP 1] Checking model library for oak models...")
# 使用实际的模型库路径（与model_selector.py一致）
model_library_path = r"C:\Users\Lenovo\Desktop\updated_descriptions_json.json"

if os.path.exists(model_library_path):
    with open(model_library_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both dict format (with 'models' key) and list format
    if isinstance(data, dict) and 'models' in data:
        model_library = data['models']
    elif isinstance(data, list):
        model_library = data
    else:
        model_library = []
    
    print(f"Model library loaded: {len(model_library)} models total")
    
    # Find all oak models
    oak_models = []
    tree_models = []
    for model in model_library:
        model_id = str(model.get('id', '')).lower()
        model_name = str(model.get('name', '')).lower()
        model_file = str(model.get('file', '') or model.get('file_path', '')).lower()
        category = str(model.get('category', '')).lower()
        
        if category == 'tree' or 'tree' in model_id:
            tree_models.append(model)
            if 'oak' in model_id or 'oak' in model_name or 'oak' in model_file:
                oak_models.append(model)
    
    print(f"Tree models found: {len(tree_models)}")
    print(f"Oak models found: {len(oak_models)}")
    
    if oak_models:
        print("\nOak models in library:")
        for m in oak_models[:10]:
            print(f"  - ID: {m.get('id')}")
            print(f"    File: {m.get('file') or m.get('file_path')}")
            print(f"    Category: {m.get('category')}")
    else:
        print("\n[WARNING] No oak models found in library!")
        print("Checking all tree model IDs:")
        for m in tree_models[:20]:
            print(f"  - {m.get('id')}")
else:
    print(f"[ERROR] Model library not found at {model_library_path}")
    model_library = []
    tree_models = []
    oak_models = []

# Step 2: Test NLP parsing
print("\n" + "=" * 60)
print("[STEP 2] Testing NLP parsing...")
print("=" * 60)

test_input = "A dense oak forest with oak trees scattered across the landscape."
print(f"Test input: {test_input}")

try:
    from nlp_parser import NLPParser
    parser = NLPParser()
    nlp_result = parser.parse(test_input)
    
    print(f"\nNLP Result:")
    print(f"  objects: {nlp_result.get('objects', [])}")
    print(f"  keywords: {nlp_result.get('keywords', [])}")
    print(f"  style: {nlp_result.get('style')}")
    print(f"  original_text: {nlp_result.get('original_text', '')[:100]}...")
    
    # Check if oak is detected
    all_text = ' '.join([
        str(nlp_result.get('original_text', '')),
        ' '.join(nlp_result.get('keywords', [])),
        ' '.join([str(o) for o in nlp_result.get('objects', [])])
    ]).lower()
    
    if 'oak' in all_text:
        print("\n[OK] 'oak' found in NLP result")
    else:
        print("\n[WARNING] 'oak' NOT found in NLP result!")
        
except Exception as e:
    print(f"[ERROR] NLP parsing failed: {e}")
    nlp_result = {'original_text': test_input, 'keywords': ['oak', 'forest'], 'objects': [{'type': 'tree'}]}

# Step 3: Test model selector
print("\n" + "=" * 60)
print("[STEP 3] Testing model selector...")
print("=" * 60)

try:
    from model_selector import ModelSelector
    
    # ModelSelector不接受参数，它内部使用固定路径
    selector = ModelSelector()
    
    # Create a scene plan that matches what the system actually uses
    # 重要：nlp_result需要通过scene_plan传递
    scene_plan = {
        'object_counts': {
            'tree': 5
        },
        'layout_config': {},
        'planning_metadata': {},
        'nlp_result': nlp_result,  # 传递NLP结果
        'style': 'natural',
        'terrain_size': 50.0
    }
    
    print(f"\nScene plan object_counts: {scene_plan.get('object_counts', {})}")
    print(f"NLP result keywords: {nlp_result.get('keywords', [])}")
    print(f"NLP result original_text contains 'oak': {'oak' in nlp_result.get('original_text', '').lower()}")
    
    # Call select_models with only scene_plan (it extracts nlp_result internally)
    print("\nCalling select_models...")
    selected = selector.select_models(scene_plan)
    
    # select_models returns a dict with 'selected_models' key
    selected_models = selected.get('selected_models', {})
    trees = selected_models.get('trees', [])
    
    print(f"\nSelected tree models count: {len(trees)}")
    
    # Check selected models
    oak_selected = 0
    non_oak_selected = 0
    procedural_count = 0
    
    for model in trees:
        model_id = str(model.get('id', '')).lower()
        model_file = str(model.get('file', '') or model.get('file_path', '')).lower()
        is_procedural = model.get('type') == 'procedural' or 'procedural' in model_id
        
        if is_procedural:
            procedural_count += 1
            print(f"  [PROCEDURAL] {model.get('id')}")
        elif 'oak' in model_id or 'oak' in model_file:
            oak_selected += 1
            print(f"  [OAK] {model.get('id')} -> {model.get('file') or model.get('file_path')}")
        else:
            non_oak_selected += 1
            print(f"  [OTHER] {model.get('id')} -> {model.get('file') or model.get('file_path')}")
    
    print(f"\n[SUMMARY]")
    print(f"  Oak models selected: {oak_selected}")
    print(f"  Non-oak models selected: {non_oak_selected}")
    print(f"  Procedural models: {procedural_count}")
    
    if oak_selected == 0 and len(oak_models) > 0:
        print("\n[PROBLEM IDENTIFIED] Oak models exist in library but none were selected!")
        print("This indicates a bug in the model selection logic.")
    elif oak_selected == 0 and len(oak_models) == 0:
        print("\n[ROOT CAUSE] No oak models in the library!")
        print("You need to add oak tree models to your model library.")
    
except Exception as e:
    import traceback
    print(f"[ERROR] Model selection failed: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Debug complete")
print("=" * 60)
