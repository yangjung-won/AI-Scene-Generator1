"""
检查 transformers 和相关依赖的安装状态
"""

def check_transformers():
    """检查transformers和相关依赖"""
    print("=" * 60)
    print("检查 Transformers 安装状态")
    print("=" * 60)
    
    results = {}
    
    # 检查 transformers
    print("\n1. 检查 transformers 库...")
    try:
        import transformers
        version = transformers.__version__
        print(f"   [OK] transformers 已安装")
        print(f"   版本: {version}")
        results['transformers'] = True
    except ImportError:
        print("   [FAIL] transformers 未安装")
        print("   需要运行: pip install transformers>=4.30.0")
        results['transformers'] = False
    
    # 检查 torch
    print("\n2. 检查 PyTorch (torch)...")
    try:
        import torch
        version = torch.__version__
        print(f"   [OK] torch 已安装")
        print(f"   版本: {version}")
        results['torch'] = True
    except ImportError:
        print("   [FAIL] torch 未安装")
        print("   需要运行: pip install torch>=2.0.0")
        results['torch'] = False
    
    # 检查关键组件
    print("\n3. 检查关键组件...")
    try:
        from transformers import AutoModel, AutoTokenizer
        print("   [OK] AutoModel 可用")
        print("   [OK] AutoTokenizer 可用")
        results['components'] = True
    except ImportError as e:
        print(f"   [FAIL] 组件导入失败: {e}")
        results['components'] = False
    
    # 总结
    print("\n" + "=" * 60)
    if all(results.values()):
        print("[SUCCESS] 所有检查通过！Transformers 已准备就绪")
        print("=" * 60)
        print("\n注意：首次运行时会自动下载BERT模型（约400MB）")
        return True
    else:
        print("[FAIL] 部分组件缺失，请安装缺失的依赖")
        print("=" * 60)
        return False

if __name__ == "__main__":
    check_transformers()

