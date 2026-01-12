"""
测试热带树模型选择
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nlp_parser import NLPParser
from ltc_analyzer import LTCAnalyzer
from scene_planner import ScenePlanner
from model_selector import ModelSelector

def test_tropical_tree_selection():
    """测试热带树模型选择"""
    
    # 测试句子
    test_sentences = [
        "A lush tropical paradise with towering palm trees and exotic tropical trees scattered across the vibrant green landscape.",
        "A tropical landscape filled with diverse tropical trees under a warm, sunny sky.",
        "A sun-drenched tropical beach lined with swaying tropical trees.",
        "A dense tropical rainforest teeming with diverse tropical trees.",
        "An exotic tropical garden featuring elegant tropical trees.",
    ]
    
    print("=" * 80)
    print("测试热带树模型选择")
    print("=" * 80)
    
    # 初始化模块
    nlp_parser = NLPParser()
    ltc_analyzer = LTCAnalyzer()
    scene_planner = ScenePlanner()
    model_selector = ModelSelector()
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n{'='*80}")
        print(f"测试 {i}: {sentence}")
        print(f"{'='*80}\n")
        
        # 1. NLP解析
        print("[STEP 1] NLP解析...")
        nlp_result = nlp_parser.parse(sentence)
        print(f"  场景类型: {nlp_result.get('scene_type')}")
        print(f"  对象: {nlp_result.get('objects')}")
        print(f"  季节: {nlp_result.get('seasons')}")
        print(f"  风格: {nlp_result.get('styles')}")
        
        # 2. LTC分析
        print("\n[STEP 2] LTC分析...")
        ltc_result = ltc_analyzer.analyze(nlp_result)
        print(f"  复杂度: {ltc_result.get('complexity_factor', 0):.3f}")
        print(f"  自然度: {ltc_result.get('naturalness_score', 0):.3f}")
        
        # 3. 场景规划
        print("\n[STEP 3] 场景规划...")
        scene_plan = scene_planner.plan_scene(ltc_result)
        print(f"  树木数量: {scene_plan.get('object_counts', {}).get('tree', 0)}")
        
        # 4. 模型选择
        print("\n[STEP 4] 模型选择...")
        # 将NLP结果添加到scene_plan中
        scene_plan['nlp_result'] = nlp_result
        model_selection = model_selector.select_models(scene_plan)
        
        # 检查选中的树木模型
        selected_trees = model_selection.get('selected_models', {}).get('trees', [])
        print(f"\n  选中的树木模型 ({len(selected_trees)} 个):")
        tropical_count = 0
        for tree in selected_trees[:10]:  # 只显示前10个
            tree_id = tree.get('id', 'unknown')
            tree_name = tree.get('name', 'unknown')
            is_tropical = 'tropical' in str(tree_id).lower() or 'tropical' in str(tree_name).lower()
            if is_tropical:
                tropical_count += 1
                print(f"    [TROPICAL] {tree_id} ({tree_name}) - 热带树")
            else:
                print(f"    [OTHER]    {tree_id} ({tree_name}) - 非热带树")
        
        if tropical_count > 0:
            print(f"\n  [SUCCESS] 成功选择了 {tropical_count} 个热带树模型")
        else:
            print(f"\n  [FAIL] 没有选择到热带树模型！")
        
        print("\n" + "-" * 80)

if __name__ == "__main__":
    test_tropical_tree_selection()

