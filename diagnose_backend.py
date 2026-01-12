"""
诊断脚本：测试不同输入，查看各模块输出
用于诊断为什么不同输入产生相似效果
"""

import json
import sys
import io

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from backend_processor import AISceneGeneratorBackend

def test_different_inputs():
    """测试不同输入，查看各模块输出"""
    
    print("正在初始化后端...")
    try:
        # 初始化后端
        backend = AISceneGeneratorBackend()
        print("[OK] 后端初始化成功\n")
    except Exception as e:
        print(f"[ERROR] 后端初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 测试用例
    test_cases = [
        "A dense forest scene with tall trees",
        "A spring garden with pink cherry trees and purple flowers",
        "A winter landscape with snow-covered trees",
        "A desert scene with sparse vegetation and rocks"
    ]
    
    results = {}
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {user_input}")
        print('='*60)
        
        try:
            # 调用后端处理
            result = backend.process_request(user_input)
            
            # 提取关键信息
            nlp_result = result.get('nlp_result', {})
            ltc_result = result.get('ltc_result', {})
            scene_plan = result.get('scene_plan', {})
            model_selection = result.get('model_selection', {})
            
            # 正确访问模型选择结果
            selected_models_dict = model_selection.get('selected_models', {}) if isinstance(model_selection, dict) else {}
            
            # 保存结果
            results[user_input] = {
                'nlp_objects': nlp_result.get('objects', []),
                'nlp_scene_type': nlp_result.get('scene_type', 'unknown'),
                'ltc_complexity': ltc_result.get('complexity_factor', 0),
                'ltc_naturalness': ltc_result.get('naturalness_score', 0),
                'object_params': ltc_result.get('object_parameters', {}),
                'object_counts': scene_plan.get('object_counts', {}),
                'selected_models': {
                    'trees': len(selected_models_dict.get('trees', [])),
                    'flowers': len(selected_models_dict.get('flowers', [])),
                    'stones': len(selected_models_dict.get('stones', [])),
                    'grasses': len(selected_models_dict.get('grasses', []))
                }
            }
            
            # 打印关键信息
            print(f"\n[NLP] 识别对象: {nlp_result.get('objects', [])}")
            print(f"[NLP] 场景类型: {nlp_result.get('scene_type', 'unknown')}")
            print(f"[LTC] 复杂度: {ltc_result.get('complexity_factor', 0):.2f}")
            print(f"[LTC] 自然度: {ltc_result.get('naturalness_score', 0):.2f}")
            print(f"[PLANNING] 对象数量: {scene_plan.get('object_counts', {})}")
            print(f"[SELECTION] 选中模型: {results[user_input]['selected_models']}")
            
            # 打印模型ID示例
            selected_models_dict = model_selection.get('selected_models', {}) if isinstance(model_selection, dict) else {}
            if selected_models_dict.get('trees'):
                tree_ids = [m.get('id', 'unknown') for m in selected_models_dict['trees'][:3]]
                print(f"[SELECTION] 树模型ID示例: {tree_ids}")
            if selected_models_dict.get('flowers'):
                flower_ids = [m.get('id', 'unknown') for m in selected_models_dict['flowers'][:3]]
                print(f"[SELECTION] 花模型ID示例: {flower_ids}")
            
        except Exception as e:
            print(f"[ERROR] 错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 对比分析
    print(f"\n\n{'='*60}")
    print("对比分析")
    print('='*60)
    
    # 检查是否所有结果都相似
    all_same = True
    first_result = list(results.values())[0] if results else None
    
    for input_text, result in results.items():
        print(f"\n输入: {input_text}")
        print(f"  对象: {result['nlp_objects']}")
        print(f"  场景类型: {result['nlp_scene_type']}")
        print(f"  对象数量: {result['object_counts']}")
        print(f"  复杂度: {result['ltc_complexity']:.3f}")
        print(f"  自然度: {result['ltc_naturalness']:.3f}")
        
        if first_result and result != first_result:
            all_same = False
    
    if all_same and first_result:
        print("\n[WARN] 警告：所有输入产生了相似的结果！")
        print("可能的问题：")
        print("1. NLP解析器没有正确识别不同输入")
        print("2. LTC分析器返回了相似的结果")
        print("3. 场景规划器使用了默认值")
        print("4. 模型选择器没有根据输入过滤模型")
    else:
        print("\n[OK] 不同输入产生了不同的结果")
    
    # 保存详细结果到文件
    try:
        with open('diagnostic_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] 详细结果已保存到 diagnostic_results.json")
    except Exception as e:
        print(f"\n[WARN] 保存结果失败: {e}")

if __name__ == '__main__':
    test_different_inputs()
