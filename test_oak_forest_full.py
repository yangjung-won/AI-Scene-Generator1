"""
完整测试橡树林生成流程
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend_processor import AISceneGeneratorBackend

def test_oak_forest():
    """测试橡树林生成"""
    
    print("=" * 80)
    print("测试橡树林生成 - 完整流程诊断")
    print("=" * 80)
    
    # 初始化后端
    backend = AISceneGeneratorBackend()
    
    # 测试指令
    test_input = "A dense oak forest with majestic oak trees scattered across the landscape, the ground completely covered with lush green grass, and the terrain painted in deep dark green colors."
    
    print(f"\n输入指令: {test_input}\n")
    
    # 处理请求
    result = backend.process_request(test_input)
    
    if not result.get('success'):
        print(f"\n[ERROR] 处理失败: {result.get('error')}")
        return
    
    # 检查NLP结果
    print("\n" + "=" * 80)
    print("1. NLP解析结果")
    print("=" * 80)
    nlp_result = result.get('nlp_result', {})
    print(f"  场景类型: {nlp_result.get('scene_type')}")
    print(f"  识别对象: {nlp_result.get('objects')}")
    print(f"  季节: {nlp_result.get('seasons')}")
    print(f"  风格: {nlp_result.get('styles')}")
    
    # 检查LTC结果
    print("\n" + "=" * 80)
    print("2. LTC分析结果")
    print("=" * 80)
    ltc_result = result.get('ltc_result', {})
    print(f"  复杂度: {ltc_result.get('complexity_factor', 0):.3f}")
    print(f"  自然度: {ltc_result.get('naturalness_score', 0):.3f}")
    print(f"  分析方法: {ltc_result.get('analysis_method')}")
    print(f"  是否包含NLP结果: {'nlp_result' in ltc_result}")
    
    # 检查场景规划
    print("\n" + "=" * 80)
    print("3. 场景规划结果")
    print("=" * 80)
    scene_plan = result.get('scene_plan', {})
    object_counts = scene_plan.get('object_counts', {})
    print(f"  对象数量: {object_counts}")
    print(f"  是否包含NLP结果: {'nlp_result' in scene_plan}")
    
    # 检查模型选择
    print("\n" + "=" * 80)
    print("4. 模型选择结果")
    print("=" * 80)
    model_selection = result.get('model_selection', {})
    selected_models = model_selection.get('selected_models', {})
    trees = selected_models.get('trees', [])
    
    print(f"  选中的树木数量: {len(trees)}")
    print(f"\n  前10个树木模型:")
    
    oak_count = 0
    for i, tree in enumerate(trees[:10], 1):
        tree_id = tree.get('id', 'unknown')
        tree_name = tree.get('name', 'unknown')
        is_oak = 'oak' in str(tree_id).lower() or 'oak' in str(tree_name).lower()
        if is_oak:
            oak_count += 1
            print(f"    [{i}] [OAK] {tree_id} ({tree_name})")
        else:
            print(f"    [{i}] [OTHER] {tree_id} ({tree_name})")
    
    print(f"\n  橡树模型数量: {oak_count}/{len(trees)}")
    
    if oak_count == 0:
        print("\n  [WARNING] 没有选择到橡树模型！")
        print("\n  诊断信息:")
        
        # 检查模型库中是否有橡树模型
        model_selector = backend.modules.get('selector')
        if model_selector:
            all_trees = [m for m in model_selector.models_data if m.get('category') == 'tree']
            oak_models = [m for m in all_trees if 'oak' in str(m.get('id', '')).lower() or 'oak' in str(m.get('name', '')).lower()]
            print(f"    模型库中橡树模型总数: {len(oak_models)}")
            if oak_models:
                print(f"    前5个橡树模型:")
                for m in oak_models[:5]:
                    print(f"      - {m.get('id')} ({m.get('name')})")
    else:
        print(f"\n  [SUCCESS] 成功选择了 {oak_count} 个橡树模型！")

if __name__ == "__main__":
    test_oak_forest()



