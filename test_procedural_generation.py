"""
测试程序化模型生成功能
"""

def test_procedural_generation():
    """测试程序化生成"""
    print("=" * 70)
    print("测试程序化模型生成")
    print("=" * 70)
    
    try:
        from procedural_model_generator import ProceduralModelGenerator
        
        generator = ProceduralModelGenerator()
        print("\n[OK] 程序化生成器初始化成功")
        
        # 测试各种类型
        test_types = ['tree', 'flower', 'stone', 'building', 'bush']
        ltc_params = {'complexity_factor': 0.7}
        
        for obj_type in test_types:
            print(f"\n测试生成: {obj_type}")
            config = generator.generate_model(obj_type, {'size': 'medium'}, ltc_params)
            
            print(f"  类型: {config['type']}")
            print(f"  操作步骤: {len(config['blender_operations'])}")
            print(f"  材质数: {len(config['material'])}")
            
            # 显示操作步骤
            for i, op in enumerate(config['blender_operations'], 1):
                print(f"    步骤{i}: {op['step']} - {op['method']}")
        
        print("\n" + "=" * 70)
        print("[SUCCESS] 程序化生成测试通过")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_selector_integration():
    """测试模型选择器集成"""
    print("\n" + "=" * 70)
    print("测试模型选择器集成")
    print("=" * 70)
    
    try:
        from model_selector import ModelSelector
        from scene_planner import ScenePlanner
        from ltc_analyzer import LTCAnalyzer
        from nlp_parser import NLPParser
        
        # 创建场景规划（模拟）
        nlp = NLPParser()
        nlp_result = nlp.parse("创建一个花园")
        ltc = LTCAnalyzer()
        ltc_result = ltc.analyze(nlp_result)
        planner = ScenePlanner()
        scene_plan = planner.plan_scene(ltc_result)
        
        # 测试模型选择（包含程序化生成）
        selector = ModelSelector()
        
        # 测试选择不存在的类型（会触发程序化生成）
        print("\n测试选择不存在的模型类型...")
        result = selector.select_models(scene_plan)
        
        print(f"\n选择结果:")
        print(f"  总请求: {result['selection_stats']['total_requested']}")
        print(f"  总选择: {result['selection_stats']['total_selected']}")
        
        # 检查是否有程序化生成的模型
        procedural_count = 0
        for category, models in result['selected_models'].items():
            for model in models:
                if model.get('type') == 'procedural':
                    procedural_count += 1
                    print(f"  发现程序化模型: {model.get('id')}")
        
        if procedural_count > 0:
            print(f"\n[OK] 成功生成 {procedural_count} 个程序化模型")
        else:
            print("\n[INFO] 所有模型都来自模型库（未触发程序化生成）")
        
        print("\n" + "=" * 70)
        print("[SUCCESS] 集成测试通过")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_procedural_generation()
    success2 = test_model_selector_integration()
    
    if success1 and success2:
        print("\n[SUCCESS] 所有测试通过!")
    else:
        print("\n[FAIL] 部分测试失败")



























