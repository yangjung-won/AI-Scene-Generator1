"""
测试橡树模型选择 - 完整流程诊断
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend_processor import AISceneGeneratorBackend

def test_oak_forest():
    """测试橡树林生成"""
    
    # 测试句子
    test_sentences = [
        "A dense oak forest with majestic oak trees scattered across the landscape, the ground completely covered with lush green grass, and the terrain painted in deep dark green colors.",
        "An oak forest filled with oak trees, lush grass covering the ground, and dark green terrain.",
        "A serene oak grove featuring a cluster of tall oak trees, the entire ground blanketed with thick lush grass, creating a deep dark green forest floor beneath the canopy.",
    ]
    
    print("=" * 80)
    print("测试橡树林模型选择 - 完整流程诊断")
    print("=" * 80)
    
    # 初始化后端
    backend = AISceneGeneratorBackend()
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n{'='*80}")
        print(f"测试 {i}: {sentence}")
        print(f"{'='*80}\n")
        
        try:
            # 处理请求
            result = backend.process_request(sentence)
            
            if not result.get('success'):
                print(f"[ERROR] 处理失败: {result.get('error')}")
                continue
            
            # 提取关键信息
            nlp_result = result.get('nlp_result', {})
            ltc_result = result.get('ltc_result', {})
            scene_plan = result.get('scene_plan', {})
            model_selection = result.get('model_selection', {})
            
            print(f"\n[NLP] 场景类型: {nlp_result.get('scene_type')}")
            print(f"[NLP] 识别对象: {nlp_result.get('objects')}")
            print(f"[NLP] 原始文本: {nlp_result.get('original_text', '')[:100]}")
            
            print(f"\n[LTC] 复杂度: {ltc_result.get('complexity_factor', 0):.3f}")
            print(f"[LTC] 自然度: {ltc_result.get('naturalness_score', 0):.3f}")
            print(f"[LTC] 分析方法: {ltc_result.get('analysis_method', 'unknown')}")
            
            print(f"\n[PLANNING] 树木数量: {scene_plan.get('object_counts', {}).get('tree', 0)}")
            print(f"[PLANNING] 草数量: {scene_plan.get('object_counts', {}).get('grass', 0)}")
            
            # 检查scene_plan中是否有nlp_result
            if 'nlp_result' in scene_plan:
                print(f"[PLANNING] ✅ scene_plan包含nlp_result")
            else:
                print(f"[PLANNING] ❌ scene_plan不包含nlp_result！")
            
            # 检查模型选择结果
            selected_models = model_selection.get('selected_models', {})
            selected_trees = selected_models.get('trees', [])
            
            print(f"\n[MODEL_SELECTION] 选中的树木模型 ({len(selected_trees)} 个):")
            oak_count = 0
            for j, tree in enumerate(selected_trees[:15], 1):  # 显示前15个
                tree_id = tree.get('id', 'unknown')
                tree_name = tree.get('name', 'unknown')
                is_oak = 'oak' in str(tree_id).lower() or 'oak' in str(tree_name).lower()
                if is_oak:
                    oak_count += 1
                    print(f"  [{j:2d}] [OAK] {tree_id} ({tree_name})")
                else:
                    print(f"  [{j:2d}] [OTHER] {tree_id} ({tree_name})")
            
            if oak_count > 0:
                print(f"\n[SUCCESS] ✅ 成功选择了 {oak_count} 个橡树模型")
            else:
                print(f"\n[FAIL] ❌ 没有选择到橡树模型！")
                print(f"  可能原因：")
                print(f"  1. NLP没有识别到'oak'关键词")
                print(f"  2. 模型选择器没有正确匹配oak模型")
                print(f"  3. scene_plan中没有传递nlp_result")
                
        except Exception as e:
            print(f"[ERROR] 测试失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "-" * 80)

if __name__ == "__main__":
    test_oak_forest()

