# -*- coding: utf-8 -*-
"""
Test full pipeline with correct flow
"""
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("FULL PIPELINE TEST")
print("=" * 60)

test_input = "A dense oak forest with oak trees scattered across the landscape."
print(f"Input: {test_input}")
print()

# Use backend processor for complete flow
from backend_processor import AISceneGeneratorBackend

backend = AISceneGeneratorBackend()
result = backend.process_request(test_input)

print()
print("=" * 60)
print("CHECKING RESULTS")
print("=" * 60)

# Check nlp_result
nlp_result = result.get('nlp_result', {})
print(f"nlp_result.original_text: {nlp_result.get('original_text', '')[:60]}...")
print(f"'oak' in original_text: {'oak' in nlp_result.get('original_text', '').lower()}")

# Check ltc_result
ltc_result = result.get('ltc_result', {})
ltc_nlp = ltc_result.get('nlp_result', {})
print(f"ltc_result has nlp_result: {'nlp_result' in ltc_result}")
print(f"ltc_nlp.original_text: {ltc_nlp.get('original_text', '')[:60]}...")

# Check scene_plan
scene_plan = result.get('scene_plan', {})
plan_nlp = scene_plan.get('nlp_result', {})
print(f"scene_plan has nlp_result: {'nlp_result' in scene_plan}")
print(f"plan_nlp.original_text: {plan_nlp.get('original_text', '')[:60]}...")

# Check model selection
model_selection = result.get('model_selection', {})
selected_models = model_selection.get('selected_models', {})
trees = selected_models.get('trees', [])

print()
print("=" * 60)
print("TREE SELECTION RESULTS")
print("=" * 60)
print(f"Trees selected: {len(trees)}")

oak_count = 0
non_oak_count = 0
procedural_count = 0

for i, tree in enumerate(trees):
    tree_id = str(tree.get('id', '')).lower()
    tree_file = str(tree.get('file', '') or tree.get('file_path', '')).lower()
    is_procedural = tree.get('type') == 'procedural' or 'procedural' in tree_id
    
    if is_procedural:
        procedural_count += 1
        marker = "PROCEDURAL"
    elif 'oak' in tree_id or 'oak' in tree_file:
        oak_count += 1
        marker = "OAK"
    else:
        non_oak_count += 1
        marker = "OTHER"
    
    print(f"  [{i+1}] {marker}: {tree.get('id')} -> {tree.get('file') or tree.get('file_path')}")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Oak models selected: {oak_count}")
print(f"  Non-oak models selected: {non_oak_count}")
print(f"  Procedural models: {procedural_count}")

if oak_count == 0:
    print()
    print("[PROBLEM] No oak models were selected despite user requesting oak!")

