# -*- coding: utf-8 -*-
"""Check terrain bounds vs object positions"""
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from backend_processor import AISceneGeneratorBackend

backend = AISceneGeneratorBackend()
result = backend.process_request("A dense oak forest with oak trees scattered across the landscape.")

if result.get('success'):
    scene_plan = result.get('scene_plan', {})
    layout_config = scene_plan.get('layout_config', {})
    scene_config = scene_plan.get('scene_config', {})
    
    # Get terrain/area size
    area_size = scene_config.get('area_size', layout_config.get('area_size', 50))
    terrain_config = layout_config.get('terrain_config', {})
    terrain_size = terrain_config.get('size', area_size)
    
    positions = layout_config.get('positions', [])
    
    print("="*60)
    print("TERRAIN BOUNDS vs OBJECT POSITIONS")
    print("="*60)
    
    print(f"\nScene config area_size: {scene_config.get('area_size', 'N/A')}")
    print(f"Layout config area_size: {layout_config.get('area_size', 'N/A')}")
    print(f"Terrain config size: {terrain_size}")
    print(f"Terrain half size: {terrain_size / 2 if terrain_size else 'N/A'}")
    
    # Check all positions
    half_size = terrain_size / 2 if terrain_size else 25
    out_of_bounds = 0
    max_x = max_y = 0
    min_x = min_y = float('inf')
    
    for p in positions:
        pos = p.get('position')
        if pos:
            if hasattr(pos, 'x'):
                x, y = pos.x, pos.y
            elif isinstance(pos, (list, tuple)):
                x, y = pos[0], pos[1]
            elif isinstance(pos, dict):
                x, y = pos.get('x', 0), pos.get('y', 0)
            else:
                continue
            
            max_x = max(max_x, abs(x))
            max_y = max(max_y, abs(y))
            min_x = min(min_x, abs(x))
            min_y = min(min_y, abs(y))
            
            if abs(x) > half_size or abs(y) > half_size:
                out_of_bounds += 1
    
    print(f"\nTotal positions: {len(positions)}")
    print(f"Out of bounds: {out_of_bounds}")
    print(f"Max |X|: {max_x:.2f}")
    print(f"Max |Y|: {max_y:.2f}")
    print(f"Terrain half size: {half_size:.2f}")
    
    if max_x > half_size or max_y > half_size:
        print(f"\n[WARNING] Objects exceed terrain bounds!")
        print(f"  Max X exceeds by: {max_x - half_size:.2f}")
        print(f"  Max Y exceeds by: {max_y - half_size:.2f}")
    else:
        print(f"\n[OK] All objects within terrain bounds")
    
    print("\n" + "="*60)
else:
    print(f"Error: {result.get('error')}")

