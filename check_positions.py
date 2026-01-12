# -*- coding: utf-8 -*-
"""Check position distribution"""
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from backend_processor import AISceneGeneratorBackend

backend = AISceneGeneratorBackend()
result = backend.process_request("A dense oak forest with oak trees scattered across the landscape.")

if result.get('success'):
    scene_plan = result.get('scene_plan', {})
    layout_config = scene_plan.get('layout_config', {})
    positions = layout_config.get('positions', [])
    
    print("="*60)
    print("POSITION DISTRIBUTION CHECK")
    print("="*60)
    
    # Filter tree positions
    tree_positions = [p for p in positions if p.get('type') == 'tree']
    
    print(f"\nTotal positions: {len(positions)}")
    print(f"Tree positions: {len(tree_positions)}")
    print(f"Scene size: {layout_config.get('area_size', 'N/A')}")
    
    if tree_positions:
        # Calculate statistics
        xs = []
        ys = []
        for p in tree_positions:
            pos = p.get('position')
            if pos:
                if hasattr(pos, 'x'):
                    xs.append(pos.x)
                    ys.append(pos.y)
                elif isinstance(pos, (list, tuple)):
                    xs.append(pos[0])
                    ys.append(pos[1])
                elif isinstance(pos, dict):
                    xs.append(pos.get('x', 0))
                    ys.append(pos.get('y', 0))
        
        if xs:
            print(f"\nTree position statistics:")
            print(f"  X range: [{min(xs):.2f}, {max(xs):.2f}]")
            print(f"  Y range: [{min(ys):.2f}, {max(ys):.2f}]")
            print(f"  X spread: {max(xs) - min(xs):.2f}")
            print(f"  Y spread: {max(ys) - min(ys):.2f}")
            
            # Count trees near origin
            near_origin = sum(1 for x, y in zip(xs, ys) if abs(x) < 5 and abs(y) < 5)
            print(f"\n  Trees near origin (|x|<5, |y|<5): {near_origin}/{len(xs)}")
            
            # Show first 10 positions
            print(f"\nFirst 10 tree positions:")
            for i, (x, y) in enumerate(zip(xs[:10], ys[:10])):
                print(f"  Tree {i+1}: ({x:.2f}, {y:.2f})")
        else:
            print("\n[ERROR] Could not extract coordinates from positions!")
            print(f"Position format: {tree_positions[0] if tree_positions else 'N/A'}")
    else:
        print("\n[ERROR] No tree positions found!")
    
    print("\n" + "="*60)
else:
    print(f"Error: {result.get('error')}")

