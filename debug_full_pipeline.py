# -*- coding: utf-8 -*-
"""
Debug full pipeline - trace from NLP to model selection
"""
import json
import os
import sys

# Set encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("DEBUG: Full Pipeline Trace")
print("=" * 60)

test_input = "A dense oak forest with oak trees scattered across the landscape."
print(f"Test input: {test_input}")

# Step 1: NLP parsing
print("\n" + "=" * 60)
print("[STEP 1] NLP Parsing")
print("=" * 60)

from nlp_parser import NLPParser
parser = NLPParser()
nlp_result = parser.parse(test_input)

print(f"NLP Result:")
print(f"  original_text: {nlp_result.get('original_text', 'MISSING!')}")
print(f"  objects: {nlp_result.get('objects', [])}")
print(f"  keywords: {nlp_result.get('keywords', [])}")
print(f"  'oak' in original_text: {'oak' in nlp_result.get('original_text', '').lower()}")

# Step 2: LTC analysis
print("\n" + "=" * 60)
print("[STEP 2] LTC Analysis")
print("=" * 60)

from ltc_analyzer import LTCAnalyzer
ltc = LTCAnalyzer()
ltc_result = ltc.analyze(nlp_result)

print(f"LTC Result contains nlp_result: {'nlp_result' in ltc_result}")
if 'nlp_result' in ltc_result:
    nested_nlp = ltc_result['nlp_result']
    print(f"  Nested nlp_result.original_text exists: {'original_text' in nested_nlp}")
    if 'original_text' in nested_nlp:
        print(f"  'oak' in nested original_text: {'oak' in nested_nlp.get('original_text', '').lower()}")

# Step 3: Scene planning
print("\n" + "=" * 60)
print("[STEP 3] Scene Planning")
print("=" * 60)

from scene_planner import ScenePlanner
planner = ScenePlanner()
scene_plan = planner.plan_scene(ltc_result)

print(f"Scene Plan contains nlp_result: {'nlp_result' in scene_plan}")
if 'nlp_result' in scene_plan:
    plan_nlp = scene_plan['nlp_result']
    print(f"  Plan nlp_result.original_text exists: {'original_text' in plan_nlp}")
    if 'original_text' in plan_nlp:
        print(f"  Plan original_text: {plan_nlp.get('original_text', '')[:80]}...")
        print(f"  'oak' in plan original_text: {'oak' in plan_nlp.get('original_text', '').lower()}")

print(f"\nScene Plan object_counts: {scene_plan.get('object_counts', {})}")

# Step 4: Model selection
print("\n" + "=" * 60)
print("[STEP 4] Model Selection")
print("=" * 60)

from model_selector import ModelSelector
selector = ModelSelector()
model_selection = selector.select_models(scene_plan)

# Check selected models
selected_models = model_selection.get('selected_models', {})
trees = selected_models.get('trees', [])

print(f"\nSelected tree models: {len(trees)}")

oak_count = 0
other_count = 0
procedural_count = 0

for i, model in enumerate(trees):
    model_id = str(model.get('id', '')).lower()
    model_file = str(model.get('file', '') or model.get('file_path', '')).lower()
    is_procedural = model.get('type') == 'procedural' or 'procedural' in model_id
    
    if is_procedural:
        procedural_count += 1
        tag = "[PROCEDURAL]"
    elif 'oak' in model_id or 'oak' in model_file:
        oak_count += 1
        tag = "[OAK]"
    else:
        other_count += 1
        tag = "[OTHER]"
    
    print(f"  {i+1}. {tag} {model.get('id')} -> {model.get('file') or model.get('file_path', 'N/A')}")

print(f"\n[SUMMARY]")
print(f"  Oak models: {oak_count}")
print(f"  Other models: {other_count}")
print(f"  Procedural: {procedural_count}")

if oak_count == 0:
    print("\n[PROBLEM] No oak models selected!")
    print("Checking model library for oak models...")
    
    # Check model library
    model_library_path = r"C:\Users\Lenovo\Desktop\updated_descriptions_json.json"
    if os.path.exists(model_library_path):
        with open(model_library_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'models' in data:
            model_library = data['models']
        elif isinstance(data, list):
            model_library = data
        else:
            model_library = []
        
        oak_in_lib = [m for m in model_library if 'oak' in str(m.get('id', '')).lower()]
        print(f"  Oak models in library: {len(oak_in_lib)}")
        for m in oak_in_lib:
            print(f"    - {m.get('id')}")
else:
    print("\n[SUCCESS] Oak models were correctly selected!")

print("\n" + "=" * 60)
print("Debug complete")
print("=" * 60)

