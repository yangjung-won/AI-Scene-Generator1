# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from nlp_parser import NLPParser
from ltc_analyzer import LTCAnalyzer
from scene_planner import ScenePlanner
from model_selector import ModelSelector

# 测试 winter 场景
test_input = "A winter landscape with snow-covered trees"

print("="*60)
print("测试 snow_tree_002 模型选择")
print("="*60)
print(f"\n输入: {test_input}\n")

# 1. NLP 解析
print("[1] NLP 解析...")
nlp_parser = NLPParser()
nlp_result = nlp_parser.parse(test_input)
print(f"  场景类型: {nlp_result.get('scene_type')}")
print(f"  季节: {nlp_result.get('season')}")
print(f"  风格: {nlp_result.get('style')}")

# 2. LTC 分析
print("\n[2] LTC 分析...")
ltc_analyzer = LTCAnalyzer()
ltc_result = ltc_analyzer.analyze(nlp_result)
print(f"  复杂度: {ltc_result.get('complexity_factor')}")
print(f"  自然度: {ltc_result.get('naturalness_score')}")

# 3. 场景规划
print("\n[3] 场景规划...")
scene_planner = ScenePlanner()
# 将 nlp_result 添加到 ltc_result 中
ltc_result['nlp_result'] = nlp_result
scene_plan = scene_planner.plan_scene(ltc_result)
print(f"  树木数量: {scene_plan.get('object_counts', {}).get('tree', 0)}")

# 4. 模型选择
print("\n[4] 模型选择...")
model_selector = ModelSelector()

# 检查 snow_tree_002 是否在模型库中
all_models = model_selector.models_data
snow_tree_002 = [m for m in all_models if m.get('id') == 'snow_tree_002']
if snow_tree_002:
    st = snow_tree_002[0]
    print(f"  snow_tree_002 在模型库中:")
    print(f"    ID: {st.get('id')}")
    print(f"    文件路径: {st.get('file') or st.get('file_path')}")
    print(f"    季节: {st.get('season')}")
    print(f"    风格: {st.get('style')}")
    
    # 检查文件是否存在
    file_path = st.get('file') or st.get('file_path')
    if file_path:
        exists = os.path.exists(file_path)
        print(f"    文件存在: {exists}")
        if exists:
            file_size = os.path.getsize(file_path)
            print(f"    文件大小: {file_size} bytes")
        
        # 检查模型是否可用
        is_available = model_selector._is_model_available(st)
        print(f"    模型可用: {is_available}")
else:
    print("  [ERROR] snow_tree_002 不在模型库中!")

# 执行模型选择
model_selection = model_selector.select_models(scene_plan)

# 检查选择的树木模型
selected_trees = model_selection.get('selected_models', {}).get('trees', [])
print(f"\n[5] 选择的树木模型 ({len(selected_trees)} 个):")
snow_trees_selected = [t for t in selected_trees if 'snow_tree' in str(t.get('id', '')).lower()]
print(f"  选择的 snow_tree 模型: {len(snow_trees_selected)} 个")
for i, tree in enumerate(selected_trees[:10], 1):
    tree_id = tree.get('id', 'unknown')
    season = tree.get('season', [])
    is_snow = 'snow' in str(tree_id).lower()
    marker = " <-- snow_tree" if is_snow else ""
    print(f"  {i}. {tree_id} (season: {season}){marker}")

if snow_trees_selected:
    print("\n[OK] snow_tree_002 已被成功选择!")
else:
    print("\n[WARN] snow_tree_002 未被选择，可能原因:")
    print("  1. 文件路径不存在")
    print("  2. 模型评分不够高")
    print("  3. 季节过滤逻辑有问题")

