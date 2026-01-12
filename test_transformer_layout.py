"""
测试 Transformer 和有序布局算法
"""

import sys

def test_transformer_and_layout():
    """测试Transformer和布局优化器"""
    print("=" * 70)
    print("测试 Transformer 和有序布局算法")
    print("=" * 70)
    
    try:
        # 1. 测试后端加载
        print("\n[TEST 1] 加载后端处理器...")
        from backend_processor import AISceneGeneratorBackend
        backend = AISceneGeneratorBackend(device='cpu')
        print("[OK] 后端处理器加载成功")
        
        # 2. 检查模块状态
        print("\n[TEST 2] 检查模块状态...")
        status = backend.get_module_status()
        
        print("\n模块列表:")
        for module_name, module_info in status.items():
            print(f"  - {module_name}:")
            for key, value in module_info.items():
                print(f"      {key}: {value}")
        
        # 检查关键模块
        has_transformer = status.get('layout_transformer', {}).get('loaded', False)
        has_optimizer = status.get('ordered_optimizer', {}).get('loaded', False)
        
        if has_transformer:
            print("\n[OK] Layout Transformer 模块已加载")
            transformer_info = status.get('layout_transformer', {})
            if transformer_info.get('using_transformer'):
                print("  [OK] 使用本地Transformer模型")
            else:
                print("  [INFO] 使用备用布局生成方法")
        else:
            print("\n[WARN] Layout Transformer 模块未加载")
        
        if has_optimizer:
            print("[OK] Ordered Layout Optimizer 模块已加载")
            optimizer_info = status.get('ordered_optimizer', {})
            print(f"  最大迭代次数: {optimizer_info.get('max_iterations', 'N/A')}")
            print(f"  学习率: {optimizer_info.get('learning_rate', 'N/A')}")
        else:
            print("[WARN] Ordered Layout Optimizer 模块未加载")
        
        # 3. 测试完整处理流程
        print("\n[TEST 3] 测试完整处理流程...")
        test_input = "创建一个宁静的日式花园，有樱花树、石灯笼和小池塘"
        print(f"输入文本: {test_input}")
        
        result = backend.process_request(test_input)
        
        if result['success']:
            print("\n[OK] 处理成功!")
            
            # 显示分析结果
            analysis = result['analysis']
            print(f"\n分析结果:")
            print(f"  场景类型: {analysis['scene_type']}")
            print(f"  对象数量: {analysis['total_objects']}")
            print(f"  复杂度: {analysis['complexity']:.2f}")
            print(f"  自然度: {analysis['naturalness']:.2f}")
            
            # 显示元数据
            metadata = result['metadata']
            print(f"\n元数据:")
            print(f"  版本: {metadata['version']}")
            print(f"  使用Transformer: {metadata.get('using_transformer', False)}")
            print(f"  使用有序优化: {metadata.get('using_ordered_optimization', False)}")
            print(f"  使用神经网络: {metadata.get('using_neural_network', False)}")
            
            # 检查布局结果
            if 'initial_layout' in result and result['initial_layout']:
                print("\n[OK] 初始布局已生成")
                initial = result['initial_layout']
                print(f"  位置数量: {len(initial.get('positions', []))}")
                print(f"  聚类中心: {len(initial.get('cluster_centers', []))}")
            
            if 'optimized_layout' in result and result['optimized_layout']:
                print("[OK] 优化布局已生成")
                optimized = result['optimized_layout']
                print(f"  位置数量: {len(optimized.get('positions', []))}")
                if 'geometric_descriptors' in optimized:
                    desc = optimized['geometric_descriptors']
                    print(f"  几何描述量数量: {len(desc.get('descriptors', []))}")
                if 'optimization_metadata' in optimized:
                    opt_meta = optimized['optimization_metadata']
                    print(f"  优化迭代次数: {opt_meta.get('iterations', 'N/A')}")
                    print(f"  最终损失: {opt_meta.get('final_loss', 'N/A'):.4f}")
            else:
                print("[INFO] 未生成优化布局（可能使用了备用方法）")
            
            print("\n" + "=" * 70)
            print("[SUCCESS] 所有测试通过!")
            print("=" * 70)
            return True
        else:
            print(f"\n[FAIL] 处理失败: {result.get('error', 'unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_transformer_and_layout()
    sys.exit(0 if success else 1)



























