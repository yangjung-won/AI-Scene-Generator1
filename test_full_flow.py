# -*- coding: utf-8 -*-
"""
完整流程测试 - 测试从用户输入到模型选择的完整流程
"""
import json
import os

print("=" * 60)
print("Full Flow Test: Oak Forest")
print("=" * 60)

# 导入后端处理器
from backend_processor import AISceneGeneratorBackend

# 创建后端实例
backend = AISceneGeneratorBackend()

# 测试输入
test_input = "A dense oak forest with oak trees scattered across the landscape."
print(f"\n[INPUT] {test_input}")

# 处理请求
result = backend.process_request(test_input)

print("\n" + "=" * 60)
print("Result Analysis")
print("=" * 60)

if result.get('success'):
    # 检查NLP结果
    nlp_result = result.get('nlp_result', {})
    print(f"\n[NLP] Scene Type: {nlp_result.get('scene_type')}")
    print(f"[NLP] Objects: {nlp_result.get('objects')}")
    print(f"[NLP] Original Text: {nlp_result.get('original_text', 'N/A')[:100]}...")
    
    # 检查场景规划
    scene_plan = result.get('scene_plan', {})
    object_counts = scene_plan.get('object_counts', {})
    print(f"\n[PLAN] Object Counts: {object_counts}")
    
    # 检查NLP结果是否传递到scene_plan
    plan_nlp = scene_plan.get('nlp_result', {})
    print(f"[PLAN] NLP Original Text in Scene Plan: {plan_nlp.get('original_text', 'NOT FOUND')[:100] if plan_nlp.get('original_text') else 'NOT FOUND'}...")
    
    # 检查模型选择结果
    model_selection = result.get('model_selection', {})
    selected_models = model_selection.get('selected_models', {})
    trees = selected_models.get('trees', [])
    
    print(f"\n[MODELS] Selected {len(trees)} trees:")
    oak_count = 0
    non_oak_count = 0
    for i, tree in enumerate(trees):
        tree_id = tree.get('id', 'unknown')
        tree_file = tree.get('file') or tree.get('file_path', 'N/A')
        tree_type = tree.get('type', 'library')
        is_oak = 'oak' in tree_id.lower() or 'oak' in str(tree_file).lower()
        
        if is_oak:
            oak_count += 1
        else:
            non_oak_count += 1
        
        if i < 10:  # Only show first 10
            print(f"  {i+1}. ID: {tree_id}")
            print(f"     File: {tree_file}")
            print(f"     Is Oak: {is_oak}")
    
    if len(trees) > 10:
        print(f"  ... and {len(trees) - 10} more trees")
    
    print(f"\n[SUMMARY]")
    print(f"  Oak trees: {oak_count}")
    print(f"  Non-oak trees: {non_oak_count}")
    print(f"  Oak percentage: {oak_count / len(trees) * 100:.1f}%")
    
    # 检查位置分布
    layout_config = scene_plan.get('layout_config', {})
    positions = layout_config.get('positions', [])
    tree_positions = [p for p in positions if p.get('type') == 'tree']
    
    print(f"\n[POSITIONS] {len(tree_positions)} tree positions:")
    
    # 检查重叠
    overlap_count = 0
    min_distance = 8.0  # 树木最小距离
    for i, pos1 in enumerate(tree_positions):
        for j, pos2 in enumerate(tree_positions):
            if i >= j:
                continue
            p1 = pos1.get('position')
            p2 = pos2.get('position')
            if p1 and p2:
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                distance = (dx**2 + dy**2)**0.5
                if distance < min_distance:
                    overlap_count += 1
                    if overlap_count <= 5:
                        print(f"  [OVERLAP] Tree {i} and Tree {j}: distance = {distance:.2f} (< {min_distance})")
    
    print(f"\n[OVERLAP CHECK] Found {overlap_count} potential overlaps (distance < {min_distance})")
    
    # 显示位置分布统计
    if tree_positions:
        xs = [p.get('position').x for p in tree_positions if p.get('position')]
        ys = [p.get('position').y for p in tree_positions if p.get('position')]
        print(f"\n[DISTRIBUTION]")
        print(f"  X range: {min(xs):.1f} to {max(xs):.1f}")
        print(f"  Y range: {min(ys):.1f} to {max(ys):.1f}")
        
        # 检查是否集中在原点
        center_count = sum(1 for x, y in zip(xs, ys) if abs(x) < 5 and abs(y) < 5)
        print(f"  Trees near center (|x|<5, |y|<5): {center_count}/{len(tree_positions)}")

else:
    print(f"[ERROR] {result.get('error', 'Unknown error')}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

