# -*- coding: utf-8 -*-
"""
Complete test of oak tree selection
"""
import sys
import os

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("FULL OAK SELECTION TEST")
print("=" * 60)

# Test input
test_input = "A dense oak forest with oak trees scattered across the landscape."
print(f"Test input: {test_input}")
print()

# Step 1: NLP Parsing
print("[STEP 1] NLP Parsing...")
from nlp_parser import NLPParser
parser = NLPParser()
nlp_result = parser.parse(test_input)

print(f"  scene_type: {nlp_result.get('scene_type')}")
print(f"  objects: {nlp_result.get('objects')}")
print(f"  original_text: {nlp_result.get('original_text')}")
print(f"  'oak' in original_text: {'oak' in nlp_result.get('original_text', '').lower()}")
print()

# Step 2: Scene Planning
print("[STEP 2] Scene Planning...")
from scene_planner import ScenePlanner
planner = ScenePlanner()
scene_plan = planner.plan_scene(nlp_result)

print(f"  object_counts: {scene_plan.get('object_counts')}")
print(f"  scene_plan has nlp_result: {'nlp_result' in scene_plan}")
if 'nlp_result' in scene_plan:
    print(f"  nlp_result.original_text in scene_plan: {scene_plan['nlp_result'].get('original_text', '')[:50]}")
print()

# Step 3: Model Selection
print("[STEP 3] Model Selection...")
from model_selector import ModelSelector
selector = ModelSelector()

print(f"  JSON path: {selector.json_path}")
print(f"  Total models loaded: {len(selector.models_data)}")

# Check tree models
tree_models = [m for m in selector.models_data if m.get('category') == 'tree']
print(f"  Tree models: {len(tree_models)}")

# Check oak models in loaded data
oak_models = []
for m in tree_models:
    model_id = str(m.get('id', '')).lower()
    model_name = str(m.get('name', '')).lower()
    model_file = str(m.get('file', '') or m.get('file_path', '')).lower()
    if 'oak' in model_id or 'oak' in model_name or 'oak' in model_file:
        oak_models.append(m)
print(f"  Oak models in loaded data: {len(oak_models)}")

if oak_models:
    print("  Oak model IDs:")
    for m in oak_models:
        print(f"    - {m.get('id')}")
print()

# Now call select_models
print("[STEP 4] Calling select_models...")
result = selector.select_models(scene_plan)

print(f"  Selection result keys: {result.keys()}")
selected_models = result.get('selected_models', {})
trees = selected_models.get('trees', [])
print(f"  Trees selected: {len(trees)}")

# Check selected trees
oak_count = 0
non_oak_count = 0
procedural_count = 0

print("\n  Selected tree details:")
for i, tree in enumerate(trees):
    tree_id = str(tree.get('id', '')).lower()
    tree_file = str(tree.get('file', '') or tree.get('file_path', '')).lower()
    is_procedural = tree.get('type') == 'procedural' or 'procedural' in tree_id
    
    if is_procedural:
        procedural_count += 1
        print(f"    [{i+1}] PROCEDURAL: {tree.get('id')}")
    elif 'oak' in tree_id or 'oak' in tree_file:
        oak_count += 1
        print(f"    [{i+1}] OAK: {tree.get('id')} -> {tree.get('file') or tree.get('file_path')}")
    else:
        non_oak_count += 1
        print(f"    [{i+1}] OTHER: {tree.get('id')} -> {tree.get('file') or tree.get('file_path')}")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Oak models available: {len(oak_models)}")
print(f"  Oak models selected: {oak_count}")
print(f"  Non-oak models selected: {non_oak_count}")
print(f"  Procedural models: {procedural_count}")

if oak_count == 0 and len(oak_models) > 0:
    print()
    print("[PROBLEM] Oak models exist but were NOT selected!")
    print("This indicates a bug in the model selection logic.")

