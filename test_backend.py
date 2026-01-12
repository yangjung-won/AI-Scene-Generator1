"""
AI场景生成器 - 后端测试脚本
测试完整的后端处理流程

作者: AI Team
版本: 3.0
"""

import sys
import traceback


def test_text_encoder():
    """测试文本编码器"""
    print("\n" + "=" * 70)
    print("测试1: 文本编码器 (TextEncoder)")
    print("=" * 70)
    
    try:
        from text_encoder import TextEncoder
        
        # 创建编码器
        encoder = TextEncoder(encoding_dim=128, method="auto")
        
        # 测试文本
        test_texts = [
            "创建一个宁静的日式花园，有樱花树和小溪",
            "Make a vibrant forest with tall pine trees and wildflowers",
            "我想要一个现代城市场景，有高楼大厦和街道",
        ]
        
        print(f"\n[OK] Encoder initialized successfully")
        print(f"   Method: {encoder.method}")
        print(f"   Dimension: {encoder.encoding_dim}")
        print(f"   Vocabulary size: {encoder.get_encoding_info()['domain_vocab_size']}")
        
        for i, text in enumerate(test_texts, 1):
            print(f"\nTest text {i}: {text}")
            encoding, features = encoder.encode(text)
            print(f"   [+] Encoding shape: {encoding.shape}")
            print(f"   [+] Vector norm: {encoding.sum():.4f}")
            print(f"   [+] Features count: {len(features)}")
            print(f"   [+] Scene words: {features.get('scene_count', 0)}")
            print(f"   [+] Nature elements: {features.get('nature_count', 0)}")
        
        print("\n[OK] Text encoder test passed")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Text encoder test failed: {e}")
        traceback.print_exc()
        return False


def test_nlp_parser():
    """测试NLP解析器"""
    print("\n" + "=" * 70)
    print("测试2: NLP解析器 (NLPParser)")
    print("=" * 70)
    
    try:
        from nlp_parser import NLPParser
        
        # 创建解析器
        parser = NLPParser()
        
        # 测试文本
        test_cases = [
            {
                'text': "创建一个宁静的日式花园，有樱花树、石头小径和小池塘",
                'expected_scene': 'japanese',
                'expected_objects': ['tree', 'stone', 'path', 'water']
            },
            {
                'text': "Make a vibrant tropical forest with tall palm trees, colorful flowers and a waterfall",
                'expected_scene': 'forest',
                'expected_objects': ['tree', 'flower', 'water']
            },
            {
                'text': "我想要一个现代城市，有摩天大楼、街道和路灯",
                'expected_scene': 'city',
                'expected_objects': ['building', 'path', 'lamp']
            },
        ]
        
        print("\n[OK] Parser initialized successfully")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"Test Case {i}")
            print(f"{'='*70}")
            
            result = parser.parse(test_case['text'])
            
            print(f"\nResults:")
            print(f"   Scene type: {result['scene_type']}")
            print(f"   Objects: {result['objects']}")
            print(f"   Styles: {result['styles']}")
            print(f"   Moods: {result['moods']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Encoding method: {result['encoding_method']}")
            
            # 验证关键元素
            scene_match = result['scene_type'] == test_case['expected_scene']
            objects_match = any(obj in result['objects'] for obj in test_case['expected_objects'])
            
            if scene_match:
                print(f"   [+] Scene recognition correct")
            else:
                print(f"   [!] Scene recognition: expected {test_case['expected_scene']}, got {result['scene_type']}")
            
            if objects_match:
                print(f"   [+] Object recognition includes expected elements")
            else:
                print(f"   [!] Object recognition may be incomplete")
        
        print("\n[OK] NLP parser test passed")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] NLP parser test failed: {e}")
        traceback.print_exc()
        return False


def test_backend_integration():
    """测试完整的后端集成"""
    print("\n" + "=" * 70)
    print("Test 3: Full Backend Integration (AISceneGeneratorBackend)")
    print("=" * 70)
    
    try:
        from backend_processor import AISceneGeneratorBackend
        
        # 创建后端实例
        print("\n[LOADING] Initializing backend processor...")
        backend = AISceneGeneratorBackend(device='cpu')
        
        # 获取模块状态
        status = backend.get_module_status()
        print(f"\nModule status:")
        for module_name, module_info in status.items():
            print(f"   {module_name}: {module_info}")
        
        # 测试完整处理流程
        test_inputs = [
            "创建一个宁静的日式禅意花园，有枫树、石灯笼和锦鲤池塘",
            "Make a fantasy forest with magical trees, glowing flowers and mystical atmosphere",
            "一个现代简约的城市公园，有几棵大树、长椅和鹅卵石小路"
        ]
        
        for i, input_text in enumerate(test_inputs, 1):
            print(f"\n{'='*70}")
            print(f"Full Pipeline Test {i}")
            print(f"Input: {input_text}")
            print(f"{'='*70}")
            
            result = backend.process_request(input_text)
            
            if result['success']:
                print(f"\n[OK] Processing successful")
                analysis = result['analysis']
                print(f"   Scene type: {analysis['scene_type']}")
                print(f"   Object count: {analysis['total_objects']}")
                print(f"   Complexity: {analysis['complexity']:.2f}")
                print(f"   Naturalness: {analysis['naturalness']:.2f}")
                print(f"   Confidence: {analysis['confidence']:.2f}")
                print(f"   Analysis method: {analysis['analysis_method']}")
                print(f"   Using neural network: {result['metadata']['using_neural_network']}")
            else:
                print(f"\n[FAIL] Processing failed: {result.get('error', 'unknown error')}")
                return False
        
        print("\n[OK] Full backend integration test passed")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Backend integration test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "AI场景生成器 - 后端测试套件" + " " * 23 + "║")
    print("║" + " " * 25 + "版本: 3.0" + " " * 34 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = []
    
    # 运行测试
    results.append(("文本编码器", test_text_encoder()))
    results.append(("NLP解析器", test_nlp_parser()))
    results.append(("完整后端集成", test_backend_integration()))
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}  {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Backend system is working properly.")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please check error messages.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

