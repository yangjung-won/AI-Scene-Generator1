# -*- coding: utf-8 -*-
"""
Final verification test: Oak selection and collision detection
"""
import sys
import math
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("FINAL VERIFICATION TEST")
print("=" * 60)

test_input = "A dense oak forest with oak trees scattered across the landscape."
print(f"Input: {test_input}")
print()

# Use backend processor for complete flow
from backend_processor import AISceneGeneratorBackend

backend = AISceneGeneratorBackend()
result = backend.process_request(test_input)

# Get scene plan
scene_plan = result.get('scene_plan', {})
layout_config = scene_plan.get('layout_config', {})
positions = layout_config.get('positions', [])

# Get model selection
model_selection = result.get('model_selection', {})
selected_models = model_selection.get('selected_models', {})
trees = selected_models.get('trees', [])

print()
print("=" * 60)
print("1. OAK SELECTION TEST")
print("=" * 60)

oak_count = 0
for tree in trees:
    tree_id = str(tree.get('id', '')).lower()
    tree_file = str(tree.get('file', '') or tree.get('file_path', '')).lower()
    if 'oak' in tree_id or 'oak' in tree_file:
        oak_count += 1

print(f"Total trees selected: {len(trees)}")
print(f"Oak trees selected: {oak_count}")
print(f"Oak percentage: {100 * oak_count / len(trees) if trees else 0:.1f}%")

if oak_count == len(trees):
    print("[PASS] All trees are oak trees!")
else:
    print(f"[WARN] Only {oak_count}/{len(trees)} are oak trees")

print()
print("=" * 60)
print("2. COLLISION DETECTION TEST")
print("=" * 60)

# Get tree positions
tree_positions = [p for p in positions if p.get('type') == 'tree']
print(f"Tree positions in layout: {len(tree_positions)}")

# Check for collisions
MIN_TREE_DISTANCE = 8.0
collision_count = 0
collision_pairs = []

for i, pos1 in enumerate(tree_positions):
    for j, pos2 in enumerate(tree_positions):
        if i >= j:
            continue
        
        p1 = pos1.get('position')
        p2 = pos2.get('position')
        
        if p1 and p2:
            dx = p1.x - p2.x
            dy = p1.y - p2.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < MIN_TREE_DISTANCE:
                collision_count += 1
                collision_pairs.append((i, j, distance))

print(f"Minimum tree distance required: {MIN_TREE_DISTANCE}")
print(f"Collisions detected: {collision_count}")

if collision_count == 0:
    print("[PASS] No tree collisions!")
else:
    print(f"[FAIL] {collision_count} tree pairs are too close:")
    for i, j, dist in collision_pairs[:5]:  # Show first 5
        print(f"  Tree {i} and Tree {j}: distance = {dist:.2f}")

# Calculate distance statistics
if len(tree_positions) >= 2:
    distances = []
    for i, pos1 in enumerate(tree_positions):
        for j, pos2 in enumerate(tree_positions):
            if i < j:
                p1 = pos1.get('position')
                p2 = pos2.get('position')
                if p1 and p2:
                    dx = p1.x - p2.x
                    dy = p1.y - p2.y
                    distances.append(math.sqrt(dx*dx + dy*dy))
    
    if distances:
        print()
        print("Distance statistics:")
        print(f"  Min distance: {min(distances):.2f}")
        print(f"  Max distance: {max(distances):.2f}")
        print(f"  Average distance: {sum(distances)/len(distances):.2f}")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
oak_pass = oak_count == len(trees)
collision_pass = collision_count == 0

print(f"Oak selection: {'PASS' if oak_pass else 'FAIL'}")
print(f"Collision detection: {'PASS' if collision_pass else 'FAIL'}")
print()
if oak_pass and collision_pass:
    print("[SUCCESS] All tests passed!")
else:
    print("[ISSUES] Some tests failed. Please review.")

