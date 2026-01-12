#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查Transformer是否可用"""

import sys
import os

# 添加后端路径
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("检查 Transformer 布局算法状态")
print("=" * 60)

# 1. 检查 transformers 库
print("\n[1] 检查 transformers 库...")
try:
    from transformers import AutoModel, AutoTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
    print("  [OK] transformers library installed")
    import transformers
    print(f"     Version: {transformers.__version__}")
    print(f"     torch Version: {torch.__version__}")
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    print(f"  [FAIL] transformers library not installed: {e}")
    print("     将使用备用布局生成方法")

# 2. 检查 LayoutTransformer 模块
print("\n[2] 检查 LayoutTransformer 模块...")
try:
    from layout_transformer import LayoutTransformer
    transformer = LayoutTransformer(model_name="bert-base-chinese", device='cpu')
    
    if transformer.use_transformer:
        print("  [OK] Transformer loaded successfully")
        print(f"     Model: bert-base-chinese")
        print(f"     Device: cpu")
        print("     Status: Can use Transformer for layout generation")
    else:
        print("  [WARN] Transformer module exists but not enabled")
        print("     Will use fallback layout generation")
except Exception as e:
    print(f"  [FAIL] LayoutTransformer loading failed: {e}")

# 3. 检查后端处理器
print("\n[3] 检查后端处理器...")
try:
    from backend_processor import AISceneGeneratorBackend
    backend = AISceneGeneratorBackend(device='cpu')
    
    status = backend.get_module_status()
    
    if 'layout_transformer' in status:
        tf_status = status['layout_transformer']
        print(f"  LayoutTransformer 状态: {tf_status}")
        
        if tf_status == 'loaded':
            print("  [OK] Backend loaded Transformer module")
        else:
            print(f"  [WARN] Backend Transformer status: {tf_status}")
    
    if 'ordered_optimizer' in status:
        opt_status = status['ordered_optimizer']
        print(f"  OrderedLayoutOptimizer status: {opt_status}")
        
        if opt_status == 'loaded':
            print("  [OK] Backend loaded OrderedLayoutOptimizer")
        else:
            print(f"  [WARN] Backend optimizer status: {opt_status}")
            
except Exception as e:
    print(f"  ❌ 后端处理器检查失败: {e}")
    import traceback
    traceback.print_exc()

# 4. 测试实际使用
print("\n[4] 测试实际布局生成...")
try:
    from backend_processor import AISceneGeneratorBackend
    backend = AISceneGeneratorBackend(device='cpu')
    
    # 检查模块
    if backend.modules.get('layout_transformer') is not None:
        transformer = backend.modules['layout_transformer']
        if transformer.use_transformer:
            print("  [OK] Will actually use Transformer for layout generation")
            
            # 测试生成
            test_layout = transformer.generate_initial_layout(
                "a peaceful garden",
                ['tree', 'flower'],
                {'area_size': 40.0}
            )
            print(f"  [OK] Test layout generation successful")
            print(f"     Generated positions: {len(test_layout.get('positions', []))}")
        else:
            print("  [WARN] Will use fallback layout generation (Transformer not enabled)")
    else:
        print("  [WARN] LayoutTransformer module not loaded")
        
except Exception as e:
    print(f"  [FAIL] Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)

