# -*- coding: utf-8 -*-
"""Check model selection format"""
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import json

from backend_processor import AISceneGeneratorBackend

backend = AISceneGeneratorBackend()
result = backend.process_request("A dense oak forest with oak trees")

if result.get('success'):
    model_selection = result.get('model_selection', {})
    selected_models = model_selection.get('selected_models', {})
    
    print("="*50)
    print("MODEL SELECTION FORMAT CHECK")
    print("="*50)
    
    print(f"\nType of selected_models: {type(selected_models)}")
    print(f"Keys in selected_models: {list(selected_models.keys())}")
    
    for key, value in selected_models.items():
        print(f"\n[{key}]")
        print(f"  Type: {type(value)}")
        if isinstance(value, list):
            print(f"  Count: {len(value)}")
            if value:
                print(f"  First item type: {type(value[0])}")
                print(f"  First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else 'N/A'}")
                if isinstance(value[0], dict):
                    print(f"  First item id: {value[0].get('id', 'N/A')}")
                    print(f"  First item file: {value[0].get('file', value[0].get('file_path', 'N/A'))}")
        elif isinstance(value, dict):
            print(f"  Dict keys: {list(value.keys())}")
    
    print("\n" + "="*50)
else:
    print(f"Error: {result.get('error')}")

