# -*- coding: utf-8 -*-
"""
Test script to analyze how a complex sentence is processed through the pipeline
"""

import sys
import os

# Ensure proper encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

# Add backend path
BACKEND_PATH = r"C:\Users\Lenovo\.cursor\extensions\backend"
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

print("=" * 70)
print("TESTING SENTENCE ANALYSIS PIPELINE")
print("=" * 70)

# Test sentence
test_sentence = """In the dense summer forest, towering ancient trees interweave their branches and leaves to form a thick shade, green ferns cling to the moist rocks, light blue wildflowers grow beside the forest stream, and the stream reflects the dappled light and shadow."""

print(f"\n[INPUT SENTENCE]\n{test_sentence}\n")
print("=" * 70)

# Step 1: NLP Parsing
print("\n[STEP 1] NLP PARSING")
print("-" * 50)

from nlp_parser import NLPParser

nlp_parser = NLPParser(use_trained_predictor=True)
nlp_result = nlp_parser.parse(test_sentence)

print(f"\n  Scene Type: {nlp_result.get('scene_type', 'unknown')}")
print(f"  Season: {nlp_result.get('season', 'unknown')}")
print(f"  Style: {nlp_result.get('style', 'unknown')}")
print(f"  Mood: {nlp_result.get('mood', 'unknown')}")
print(f"  Time of Day: {nlp_result.get('time_of_day', 'unknown')}")

print(f"\n  Detected Objects:")
objects = nlp_result.get('objects', [])
for obj in objects:
    if isinstance(obj, dict):
        print(f"    - {obj.get('type', 'unknown')}: count={obj.get('count', 1)}, keywords={obj.get('keywords', [])}")
    else:
        print(f"    - {obj}")

print(f"\n  Style Keywords: {nlp_result.get('style_keywords', [])}")
print(f"  Semantic Keywords: {nlp_result.get('semantic_keywords', [])}")

# Check if trained model was used
if nlp_result.get('using_trained_model'):
    print(f"\n  [TRAINED MODEL] Using trained predictor")
    pred_params = nlp_result.get('predicted_parameters', {})
    print(f"    - Complexity: {pred_params.get('complexity', 'N/A')}")
    print(f"    - Naturalness: {pred_params.get('naturalness', 'N/A')}")
    print(f"    - Object Density: {pred_params.get('object_density', 'N/A')}")

print("\n" + "=" * 70)

# Step 2: LTC Analysis
print("\n[STEP 2] LTC ANALYSIS")
print("-" * 50)

from ltc_analyzer import LTCAnalyzer

ltc_analyzer = LTCAnalyzer()
ltc_result = ltc_analyzer.analyze(nlp_result)

# Use actual LTC result keys
print(f"\n  Complexity: {ltc_result.get('complexity_factor', 'N/A')}")
print(f"  Naturalness: {ltc_result.get('naturalness_score', 'N/A')}")
print(f"  Tau (time constant): {ltc_result.get('time_constant_tau', 'N/A')}")
print(f"  Adaptation Rate: {ltc_result.get('adaptation_rate', 'N/A')}")
print(f"  Analysis Method: {ltc_result.get('analysis_method', 'N/A')}")

# Scene parameters
scene_params = ltc_result.get('scene_parameters', {})
print(f"\n  Scene Parameters:")
for key, value in scene_params.items():
    print(f"    - {key}: {value}")

# Dynamic coefficients
dynamic_coefs = ltc_result.get('dynamic_coefficients', {})
if dynamic_coefs:
    print(f"\n  Dynamic Coefficients:")
    for key, value in dynamic_coefs.items():
        if isinstance(value, float):
            print(f"    - {key}: {value:.3f}")
        else:
            print(f"    - {key}: {value}")

# Object parameters
obj_params = ltc_result.get('object_parameters', {})
if obj_params:
    print(f"\n  Object-Specific Parameters:")
    for obj_type, params in obj_params.items():
        print(f"    {obj_type}: {params}")

print("\n" + "=" * 70)

# Step 3: Scene Planning
print("\n[STEP 3] SCENE PLANNING")
print("-" * 50)

from scene_planner import ScenePlanner

scene_planner = ScenePlanner()
# Pass nlp_result through ltc_result (it should contain the nlp_result data)
ltc_result['nlp_result'] = nlp_result
scene_plan = scene_planner.plan_scene(ltc_result)

scene_config = scene_plan.get('scene_config', {})
print(f"\n  Scene Config:")
print(f"    - Scene Type: {scene_config.get('scene_type', 'N/A')}")
print(f"    - Area Size: {scene_config.get('area_size', 'N/A')}")
print(f"    - Season: {scene_config.get('season', 'N/A')}")
print(f"    - Style: {scene_config.get('style', 'N/A')}")

# Object counts
obj_counts = scene_plan.get('object_counts', {})
print(f"\n  Planned Object Counts:")
for obj_type, count in obj_counts.items():
    print(f"    - {obj_type}: {count}")

# Positions
positions = scene_plan.get('positions', [])
print(f"\n  Generated Positions: {len(positions)} total")

# Count by type
type_counts = {}
for pos in positions:
    obj_type = pos.get('type', 'unknown')
    type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
print(f"  Position breakdown by type:")
for obj_type, count in type_counts.items():
    print(f"    - {obj_type}: {count}")

print("\n" + "=" * 70)

# Step 4: Model Selection
print("\n[STEP 4] MODEL SELECTION")
print("-" * 50)

from model_selector import ModelSelector

model_selector = ModelSelector()
# Pass nlp_result within scene_plan
scene_plan['nlp_result'] = nlp_result
selected_models = model_selector.select_models(scene_plan)

print(f"\n  Selected Models by Category:")
for category, models in selected_models.items():
    if isinstance(models, list) and models:
        print(f"\n  [{category.upper()}] - {len(models)} models")
        show_count = min(3, len(models))
        for i in range(show_count):
            model = models[i]
            if isinstance(model, dict):
                model_id = model.get('id', 'unknown')
                model_name = model.get('name', model_id)
                is_procedural = model.get('is_procedural', False)
                file_path = model.get('file_path', model.get('file', 'N/A'))
                if is_procedural:
                    print(f"    {i+1}. [PROCEDURAL] {model_name}")
                else:
                    print(f"    {i+1}. {model_name}")
                    if file_path and file_path != 'N/A':
                        # Shorten the path for display
                        short_path = file_path.split('\\')[-1] if '\\' in file_path else file_path.split('/')[-1]
                        print(f"       File: {short_path}")
            else:
                print(f"    {i+1}. {model}")
        if len(models) > 3:
            print(f"    ... and {len(models) - 3} more")

print("\n" + "=" * 70)
print("\n[ANALYSIS COMPLETE]")
print("=" * 70)

# Summary
print("\n[SUMMARY]")
print("-" * 50)

# Get season from nlp_result
detected_seasons = nlp_result.get('seasons', [])
season_str = detected_seasons[0] if detected_seasons else nlp_result.get('season', 'unknown')

print(f"""
This sentence would be analyzed as:

1. SCENE TYPE: {nlp_result.get('scene_type', 'unknown').upper()}
2. SEASON: {str(season_str).upper()}
3. OBJECTS DETECTED:""")

for obj in objects:
    if isinstance(obj, dict):
        print(f"   - {obj.get('type', 'unknown')}: {obj.get('count', 1)}")
    else:
        print(f"   - {obj}")

print(f"""
4. LTC PARAMETERS:
   - Complexity: {ltc_result.get('complexity_factor', 'N/A'):.3f}
   - Naturalness: {ltc_result.get('naturalness_score', 'N/A'):.3f}
   - Tau: {ltc_result.get('time_constant_tau', 'N/A'):.3f}

5. SCENE WILL INCLUDE:""")

total_objects = sum(obj_counts.values())
print(f"   - Total objects: {total_objects}")
for obj_type, count in sorted(obj_counts.items(), key=lambda x: -x[1]):
    if count > 0:
        print(f"   - {obj_type}: {count}")

# Count selected models by type
print("\n6. MODELS SELECTED:")
for category, models in selected_models.items():
    if isinstance(models, list) and models:
        procedural_count = sum(1 for m in models if isinstance(m, dict) and m.get('is_procedural', False))
        real_count = len(models) - procedural_count
        if procedural_count > 0:
            print(f"   - {category}: {real_count} real + {procedural_count} procedural")
        else:
            print(f"   - {category}: {len(models)} real")

print("\n" + "=" * 70)
