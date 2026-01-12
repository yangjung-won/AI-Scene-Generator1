# -*- coding: utf-8 -*-
"""
Debug positions - check for overlapping objects
"""
import json
import os
import sys
import math

# Set encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("DEBUG: Position Distribution and Collision Check")
print("=" * 60)

test_input = "A dense oak forest with oak trees scattered across the landscape."
print(f"Test input: {test_input}")

# Run the full pipeline
from nlp_parser import NLPParser
from ltc_analyzer import LTCAnalyzer
from scene_planner import ScenePlanner
from ordered_layout_optimizer import OrderedLayoutOptimizer
from model_selector import ModelSelector

print("\n[STEP 1] Running full pipeline...")
parser = NLPParser()
nlp_result = parser.parse(test_input)

ltc = LTCAnalyzer()
ltc_result = ltc.analyze(nlp_result)

planner = ScenePlanner()
scene_plan = planner.plan_scene(ltc_result)

print(f"\nScene plan:")
print(f"  Terrain size: {scene_plan.get('terrain_config', {}).get('size', 'N/A')}")
print(f"  Object counts: {scene_plan.get('object_counts', {})}")

# Get layout
layout_config = scene_plan.get('layout_config', {})
initial_positions = layout_config.get('positions', [])  # Key is 'positions' not 'object_positions'

print(f"\n[STEP 2] Checking initial positions...")
print(f"  Total objects: {len(initial_positions)}")

# Count tree positions
tree_positions = [p for p in initial_positions if p.get('type') == 'tree']
print(f"  Tree positions: {len(tree_positions)}")

# Check for tree overlaps in initial positions
def check_overlaps(positions, obj_type, min_distance):
    overlaps = []
    type_positions = [p for p in positions if p.get('type') == obj_type]
    for i, pos1 in enumerate(type_positions):
        for j, pos2 in enumerate(type_positions):
            if i >= j:
                continue
            p1 = pos1.get('position', {})
            p2 = pos2.get('position', {})
            if isinstance(p1, dict):
                x1, y1 = p1.get('x', 0), p1.get('y', 0)
            else:
                x1, y1 = p1.x, p1.y
            if isinstance(p2, dict):
                x2, y2 = p2.get('x', 0), p2.get('y', 0)
            else:
                x2, y2 = p2.x, p2.y
            
            distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            if distance < min_distance:
                overlaps.append({
                    'obj1': i,
                    'obj2': j,
                    'distance': distance,
                    'min_required': min_distance
                })
    return overlaps

# Check initial tree overlaps
tree_min_distance = 8.0
initial_tree_overlaps = check_overlaps(initial_positions, 'tree', tree_min_distance)
print(f"\n[INITIAL] Tree overlaps (min distance {tree_min_distance}):")
if initial_tree_overlaps:
    print(f"  Found {len(initial_tree_overlaps)} overlapping pairs!")
    for overlap in initial_tree_overlaps[:10]:
        print(f"    Trees {overlap['obj1']} and {overlap['obj2']}: distance={overlap['distance']:.2f}")
else:
    print("  No overlaps found!")

# Run ordered layout optimizer
print(f"\n[STEP 3] Running ordered layout optimizer...")
optimizer = OrderedLayoutOptimizer()

# Get area size from scene plan
scene_config = scene_plan.get('scene_config', {})
area_size = scene_config.get('area_size', 50.0)

# The optimizer expects initial_layout format from scene_planner
initial_layout = scene_plan.get('layout_config', {})
if not initial_layout:
    initial_layout = {
        'object_positions': initial_positions,
        'terrain_config': scene_plan.get('terrain_config', {})
    }

optimized = optimizer.optimize(
    initial_layout=initial_layout,
    ltc_params=ltc_result,
    scene_config=scene_config
)

optimized_positions = optimized.get('positions', [])  # Key is 'positions' not 'optimized_positions'
print(f"  Optimized positions: {len(optimized_positions)}")

# Check optimized tree overlaps
optimized_tree_overlaps = check_overlaps(optimized_positions, 'tree', tree_min_distance)
print(f"\n[OPTIMIZED] Tree overlaps (min distance {tree_min_distance}):")
if optimized_tree_overlaps:
    print(f"  Found {len(optimized_tree_overlaps)} overlapping pairs!")
    for overlap in optimized_tree_overlaps[:10]:
        print(f"    Trees {overlap['obj1']} and {overlap['obj2']}: distance={overlap['distance']:.2f}")
else:
    print("  No overlaps found!")

# Print tree position distribution
print(f"\n[DISTRIBUTION] Tree positions (first 10):")
tree_optimized = [p for p in optimized_positions if p.get('type') == 'tree'][:10]
for i, pos in enumerate(tree_optimized):
    p = pos.get('position', {})
    if isinstance(p, dict):
        x, y = p.get('x', 0), p.get('y', 0)
    else:
        x, y = p.x, p.y
    print(f"  Tree {i+1}: ({x:.2f}, {y:.2f})")

# Calculate statistics
print(f"\n[STATISTICS]")
all_tree_positions = [p for p in optimized_positions if p.get('type') == 'tree']
if all_tree_positions:
    xs = []
    ys = []
    for p in all_tree_positions:
        pos = p.get('position', {})
        if isinstance(pos, dict):
            xs.append(pos.get('x', 0))
            ys.append(pos.get('y', 0))
        else:
            xs.append(pos.x)
            ys.append(pos.y)
    
    print(f"  X range: [{min(xs):.2f}, {max(xs):.2f}]")
    print(f"  Y range: [{min(ys):.2f}, {max(ys):.2f}]")
    print(f"  X spread: {max(xs) - min(xs):.2f}")
    print(f"  Y spread: {max(ys) - min(ys):.2f}")
    print(f"  Area size: {area_size}")

# Calculate minimum distances between all tree pairs
print(f"\n[MIN DISTANCES] Between all tree pairs:")
min_dist = float('inf')
max_dist = 0
total_dist = 0
count = 0
for i, pos1 in enumerate(all_tree_positions):
    for j, pos2 in enumerate(all_tree_positions):
        if i >= j:
            continue
        p1 = pos1.get('position', {})
        p2 = pos2.get('position', {})
        if isinstance(p1, dict):
            x1, y1 = p1.get('x', 0), p1.get('y', 0)
        else:
            x1, y1 = p1.x, p1.y
        if isinstance(p2, dict):
            x2, y2 = p2.get('x', 0), p2.get('y', 0)
        else:
            x2, y2 = p2.x, p2.y
        
        distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        min_dist = min(min_dist, distance)
        max_dist = max(max_dist, distance)
        total_dist += distance
        count += 1

if count > 0:
    print(f"  Minimum distance: {min_dist:.2f}")
    print(f"  Maximum distance: {max_dist:.2f}")
    print(f"  Average distance: {total_dist / count:.2f}")
    
    if min_dist < tree_min_distance:
        print(f"\n  [WARNING] Minimum distance ({min_dist:.2f}) is less than required ({tree_min_distance})!")
    else:
        print(f"\n  [OK] All trees have sufficient spacing!")

print("\n" + "=" * 60)
print("Debug complete")
print("=" * 60)

