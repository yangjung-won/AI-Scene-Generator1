# -*- coding: utf-8 -*-
"""Quick test for oak model selection"""
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*50)
print("QUICK TEST: Oak Model Selection")
print("="*50)

# Test input
test_input = "A dense oak forest with oak trees scattered across the landscape."
print(f"Input: {test_input}")

# Run pipeline
from backend_processor import AISceneGeneratorBackend
backend = AISceneGeneratorBackend()
result = backend.process_request(test_input)

if result.get('success'):
    # Check selected models
    model_selection = result.get('model_selection', {})
    selected_models = model_selection.get('selected_models', {})
    trees = selected_models.get('trees', [])
    
    print(f"\nTotal trees selected: {len(trees)}")
    
    oak_count = 0
    for i, tree in enumerate(trees[:10]):  # Show first 10
        model_id = str(tree.get('id', '')).lower()
        model_file = str(tree.get('file', '') or tree.get('file_path', '')).lower()
        is_oak = 'oak' in model_id or 'oak' in model_file
        if is_oak:
            oak_count += 1
        tag = "[OAK]" if is_oak else "[OTHER]"
        print(f"  {i+1}. {tag} {tree.get('id')} -> {tree.get('file') or tree.get('file_path')}")
    
    if len(trees) > 10:
        # Count remaining oaks
        for tree in trees[10:]:
            model_id = str(tree.get('id', '')).lower()
            model_file = str(tree.get('file', '') or tree.get('file_path', '')).lower()
            if 'oak' in model_id or 'oak' in model_file:
                oak_count += 1
        print(f"  ... and {len(trees) - 10} more trees")
    
    print(f"\n[RESULT] Oak trees: {oak_count}/{len(trees)}")
    if oak_count == len(trees):
        print("[SUCCESS] All trees are oak!")
    elif oak_count == 0:
        print("[FAIL] No oak trees selected!")
    else:
        print(f"[PARTIAL] {oak_count} oak, {len(trees) - oak_count} other")
else:
    print(f"[ERROR] {result.get('error')}")

print("="*50)

