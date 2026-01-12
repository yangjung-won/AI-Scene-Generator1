"""
生成橡树林指令并测试
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend_processor import AISceneGeneratorBackend

# 推荐的橡树林指令
OAK_FOREST_INSTRUCTIONS = [
    "A dense oak forest with majestic oak trees scattered across the landscape, the ground completely covered with lush green grass, and the terrain painted in deep dark green colors.",
    "An oak grove featuring tall oak trees, lush grass covering the entire ground, creating a dark green forest floor.",
    "A serene oak forest with oak trees, the ground blanketed with thick lush grass, and dark green terrain beneath the canopy.",
    "Oak trees in an oak forest, lush grass covering the ground, dark green terrain.",
]

def test_instruction(instruction):
    """测试单个指令"""
    print(f"\n{'='*80}")
    print(f"测试指令: {instruction}")
    print(f"{'='*80}\n")
    
    backend = AISceneGeneratorBackend()
    result = backend.process_request(instruction)
    
    if not result.get('success'):
        print(f"[ERROR] 处理失败: {result.get('error')}")
        return False
    
    # 检查模型选择
    model_selection = result.get('model_selection', {})
    selected_models = model_selection.get('selected_models', {})
    trees = selected_models.get('trees', [])
    
    oak_count = 0
    for tree in trees[:20]:  # 检查前20个
        tree_id = str(tree.get('id', '')).lower()
        tree_name = str(tree.get('name', '')).lower()
        if 'oak' in tree_id or 'oak' in tree_name:
            oak_count += 1
    
    print(f"  选中树木总数: {len(trees)}")
    print(f"  橡树模型数量: {oak_count}")
    
    if oak_count > 0:
        print(f"  [SUCCESS] 成功选择了 {oak_count} 个橡树模型！")
        return True
    else:
        print(f"  [FAIL] 没有选择到橡树模型")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("橡树林指令生成和测试")
    print("=" * 80)
    
    success_count = 0
    for i, instruction in enumerate(OAK_FOREST_INSTRUCTIONS, 1):
        if test_instruction(instruction):
            success_count += 1
            print(f"\n✅ 指令 {i} 成功！")
            print(f"\n推荐使用此指令:")
            print(f'"{instruction}"')
            break
    
    if success_count == 0:
        print("\n所有指令都失败了，请检查系统配置。")



