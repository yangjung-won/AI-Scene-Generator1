# -*- coding: utf-8 -*-
"""
调试oak模型选择问题
"""
import sys
import os
import io

# 设置编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("调试Oak模型选择")
print("=" * 80)

# 1. 测试NLP解析器
print("\n[1] 测试NLP解析器")
from nlp_parser import NLPParser
nlp = NLPParser()
test_input = "A dense oak forest with oak trees scattered across the landscape."
nlp_result = nlp.parse(test_input)
print(f"  original_text: {nlp_result.get('original_text', 'NOT FOUND')[:50]}...")
print(f"  scene_type: {nlp_result.get('scene_type')}")
print(f"  objects: {nlp_result.get('objects')}")

# 2. 测试LTC分析器
print("\n[2] 测试LTC分析器")
from ltc_analyzer import LTCAnalyzer
ltc = LTCAnalyzer()
ltc_result = ltc.analyze(nlp_result)
print(f"  nlp_result in ltc_result: {'nlp_result' in ltc_result}")
if 'nlp_result' in ltc_result:
    print(f"  original_text in nlp_result: {'original_text' in ltc_result['nlp_result']}")
    if 'original_text' in ltc_result['nlp_result']:
        print(f"  original_text value: {ltc_result['nlp_result']['original_text'][:50]}...")

# 3. 测试场景规划器
print("\n[3] 测试场景规划器")
from scene_planner import ScenePlanner
planner = ScenePlanner()
scene_plan = planner.plan_scene(ltc_result)
print(f"  nlp_result in scene_plan: {'nlp_result' in scene_plan}")
if 'nlp_result' in scene_plan:
    print(f"  original_text in nlp_result: {'original_text' in scene_plan['nlp_result']}")
    if 'original_text' in scene_plan['nlp_result']:
        print(f"  original_text value: {scene_plan['nlp_result']['original_text'][:50]}...")
print(f"  tree count: {scene_plan.get('object_counts', {}).get('tree', 0)}")

# 4. 测试模型选择器
print("\n[4] 测试模型选择器")
from model_selector import ModelSelector
selector = ModelSelector()

# 检查oak模型
oak_models = [m for m in selector.models_data if 'oak' in str(m.get('id', '')).lower()]
print(f"  模型库中的oak模型数量: {len(oak_models)}")
for m in oak_models[:3]:
    print(f"    - {m.get('id')}")

# 执行模型选择
model_selection = selector.select_models(scene_plan)
selected_trees = model_selection.get('selected_models', {}).get('trees', [])
print(f"  选择的树木数量: {len(selected_trees)}")

oak_count = 0
for tree in selected_trees[:10]:
    tree_id = str(tree.get('id', '')).lower()
    is_oak = 'oak' in tree_id
    if is_oak:
        oak_count += 1
    print(f"    - {tree.get('id')} {'[OAK]' if is_oak else ''}")

print(f"\n  Oak模型数量: {oak_count}/{len(selected_trees)}")

if oak_count == 0:
    print("\n[ERROR] 没有选择到oak模型!")
    print("\n诊断:")
    print(f"  1. original_text是否正确传递: {'original_text' in scene_plan.get('nlp_result', {})}")
    print(f"  2. original_text内容: {scene_plan.get('nlp_result', {}).get('original_text', 'N/A')[:50]}")
else:
    print("\n[OK] 成功选择了oak模型!")

