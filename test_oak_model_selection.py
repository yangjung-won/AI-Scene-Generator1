"""
测试oak模型选择
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend_processor import AISceneGeneratorBackend

def test_oak_selection():
    """测试oak模型选择"""
    
    print("=" * 80)
    print("测试Oak模型选择")
    print("=" * 80)
    
    # 初始化后端
    backend = AISceneGeneratorBackend()
    
    # 测试指令
    test_input = "A dense oak forest consisting exclusively of oak trees, with majestic oak trees scattered throughout the landscape, the ground completely covered with lush green grass, and the terrain painted in deep dark green colors."
    
    print(f"\n输入指令: {test_input}\n")
    
    # 处理请求
    result = backend.process_request(test_input)
    
    if not result.get('success'):
        print(f"\n[ERROR] 处理失败: {result.get('error')}")
        return
    
    # 检查模型选择
    model_selection = result.get('model_selection', {})
    selected_models = model_selection.get('selected_models', {})
    trees = selected_models.get('trees', [])
    
    print(f"\n选中的树木总数: {len(trees)}")
    
    # 检查oak模型
    oak_models = []
    for tree in trees:
        tree_id = str(tree.get('id', '')).lower()
        tree_name = str(tree.get('name', '')).lower()
        file_path = tree.get('file') or tree.get('file_path', '')
        
        if 'oak' in tree_id or 'oak' in tree_name:
            oak_models.append({
                'id': tree.get('id'),
                'name': tree.get('name'),
                'file': file_path,
                'exists': os.path.exists(file_path) if file_path else False
            })
    
    print(f"\nOak模型数量: {len(oak_models)}/{len(trees)}")
    
    if oak_models:
        print("\n选中的Oak模型:")
        for i, oak in enumerate(oak_models, 1):
            print(f"  {i}. ID: {oak['id']}")
            print(f"     Name: {oak['name']}")
            print(f"     File: {oak['file']}")
            print(f"     文件存在: {'[OK]' if oak['exists'] else '[NOT FOUND]'}")
    else:
        print("\n[WARN] 没有选择到Oak模型！")
        
        # 检查模型库中的oak模型
        model_selector = backend.modules.get('selector')
        if model_selector:
            all_trees = [m for m in model_selector.models_data if m.get('category') == 'tree']
            oak_in_library = [m for m in all_trees if 'oak' in str(m.get('id', '')).lower() or 'oak' in str(m.get('name', '')).lower()]
            print(f"\n模型库中的Oak模型总数: {len(oak_in_library)}")
            if oak_in_library:
                print("\n模型库中的Oak模型:")
                for i, m in enumerate(oak_in_library[:10], 1):
                    file_path = m.get('file') or m.get('file_path', '')
                    exists = os.path.exists(file_path) if file_path else False
                    print(f"  {i}. ID: {m.get('id')}")
                    print(f"     Name: {m.get('name')}")
                    print(f"     File: {file_path}")
                    print(f"     文件存在: {'[OK]' if exists else '[NOT FOUND]'}")

if __name__ == "__main__":
    test_oak_selection()


