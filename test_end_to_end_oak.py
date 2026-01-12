# -*- coding: utf-8 -*-
"""
End-to-end test for oak tree selection
"""
import json
import sys

# Set encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("END-TO-END TEST: Oak Tree Selection")
print("=" * 60)

# Import the main backend processor
from backend_processor import AISceneGeneratorBackend

# Initialize the backend
print("\n[1] Initializing backend...")
backend = AISceneGeneratorBackend()

# Test input
test_input = "A dense oak forest with oak trees scattered across the landscape."
print(f"\n[2] Test input: {test_input}")

# Process the request
print("\n[3] Processing request...")
result = backend.process_request(test_input)

# Check the results
print("\n" + "=" * 60)
print("RESULTS ANALYSIS")
print("=" * 60)

if not result.get('success'):
    print(f"ERROR: Processing failed - {result.get('error')}")
else:
    # Check NLP result
    nlp_result = result.get('nlp_result', {})
    print(f"\n[NLP RESULT]")
    print(f"  original_text: {nlp_result.get('original_text', '')[:50]}...")
    print(f"  scene_type: {nlp_result.get('scene_type')}")
    print(f"  objects: {nlp_result.get('objects', [])}")
    print(f"  'oak' in original_text: {'oak' in nlp_result.get('original_text', '').lower()}")
    
    # Check scene plan
    scene_plan = result.get('scene_plan', {})
    plan_nlp = scene_plan.get('nlp_result', {})
    print(f"\n[SCENE PLAN]")
    print(f"  nlp_result present: {bool(plan_nlp)}")
    print(f"  nlp_result.original_text: {plan_nlp.get('original_text', '')[:50] if plan_nlp else 'N/A'}...")
    print(f"  object_counts: {scene_plan.get('object_counts', {})}")
    
    # Check model selection
    model_selection = result.get('model_selection', {})
    selected_models = model_selection.get('selected_models', {})
    trees = selected_models.get('trees', [])
    
    print(f"\n[MODEL SELECTION]")
    print(f"  Total trees selected: {len(trees)}")
    
    oak_count = 0
    non_oak_count = 0
    procedural_count = 0
    
    print(f"\n  Tree models:")
    for tree in trees:
        model_id = str(tree.get('id', '')).lower()
        model_file = str(tree.get('file', '') or tree.get('file_path', '')).lower()
        is_procedural = tree.get('type') == 'procedural' or 'procedural' in model_id
        
        if is_procedural:
            procedural_count += 1
            print(f"    [PROCEDURAL] {tree.get('id')}")
        elif 'oak' in model_id or 'oak' in model_file:
            oak_count += 1
            print(f"    [OAK] {tree.get('id')} -> {tree.get('file') or tree.get('file_path')}")
        else:
            non_oak_count += 1
            print(f"    [OTHER] {tree.get('id')} -> {tree.get('file') or tree.get('file_path')}")
    
    print(f"\n[SUMMARY]")
    print(f"  Oak trees: {oak_count}")
    print(f"  Non-oak trees: {non_oak_count}")
    print(f"  Procedural trees: {procedural_count}")
    
    # Check positions for overlaps
    layout_config = scene_plan.get('layout_config', {})
    tree_positions = layout_config.get('tree', {}).get('positions', [])
    
    if tree_positions:
        print(f"\n[POSITION CHECK]")
        print(f"  Total positions: {len(tree_positions)}")
        
        # Check for overlaps
        import math
        min_distance = 8.0  # Expected minimum distance
        overlaps = []
        
        for i, pos1 in enumerate(tree_positions):
            for j, pos2 in enumerate(tree_positions):
                if i < j:
                    dx = pos1[0] - pos2[0]
                    dy = pos1[1] - pos2[1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < min_distance:
                        overlaps.append((i, j, dist))
        
        if overlaps:
            print(f"  WARNING: Found {len(overlaps)} overlapping positions!")
            for i, j, dist in overlaps[:5]:
                print(f"    Tree {i} and Tree {j}: distance = {dist:.2f} (min: {min_distance})")
        else:
            print(f"  OK: No overlapping positions found (min distance: {min_distance})")

print("\n" + "=" * 60)
print("END-TO-END TEST COMPLETE")
print("=" * 60)

