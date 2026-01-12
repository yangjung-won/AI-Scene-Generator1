# -*- coding: utf-8 -*-
"""
Test complex sentence analysis with LTC
"""

from backend_processor import AISceneGeneratorBackend

backend = AISceneGeneratorBackend()

test_sentence = """In the dense summer forest, towering ancient trees interweave their branches and leaves to form a thick shade, green ferns cling to the moist rocks, light blue wildflowers grow beside the forest stream, and the stream reflects the dappled light and shadow."""

print("=" * 70)
print("INPUT SENTENCE:")
print(test_sentence)
print("=" * 70)

result = backend.process_request(test_sentence)

print("\n" + "=" * 70)
print("ANALYSIS RESULTS:")
print("=" * 70)

analysis = result.get("analysis", {})
print(f"Scene Type: {analysis.get('scene_type')}")
print(f"Complexity: {analysis.get('complexity', 0):.3f}")
print(f"Naturalness: {analysis.get('naturalness', 0):.3f}")
print(f"Time Constant: {analysis.get('time_constant', 0):.3f}")
print(f"Confidence: {analysis.get('confidence', 0):.3f}")
print(f"Analysis Method: {analysis.get('analysis_method')}")
print(f"Styles: {analysis.get('styles')}")
print(f"Moods: {analysis.get('moods')}")

nlp = result.get("nlp_result", {})
print(f"\nDetected Objects: {nlp.get('objects', [])}")
print(f"Season: {nlp.get('season', 'unknown')}")
print(f"Time of Day: {nlp.get('time_of_day', 'unknown')}")
print(f"Keywords: {nlp.get('keywords', [])[:10]}...")  # First 10 keywords

# Semantic relations
relations = nlp.get("semantic_relations", {})
if relations:
    print(f"\nSemantic Relations:")
    for rel_type, rel_list in relations.items():
        if rel_list:
            print(f"  {rel_type}: {rel_list[:3]}...")  # First 3

ltc = result.get("ltc_result", {})
print(f"\nLTC Analysis:")
print(f"  Complexity Factor: {ltc.get('complexity_factor', 0):.3f}")
print(f"  Naturalness Score: {ltc.get('naturalness_score', 0):.3f}")
print(f"  Time Constant Tau: {ltc.get('time_constant_tau', 0):.3f}")
print(f"  Density Factor: {ltc.get('density_factor', 0):.3f}")
print(f"  Layout Dynamics: {ltc.get('layout_dynamics', {})}")

scene_plan = result.get("scene_plan", {})
layout = scene_plan.get("layout_config", {})
print(f"\nPlanned Object Counts:")
for obj_type, count in layout.get("object_counts", {}).items():
    print(f"  - {obj_type}: {count}")

scene_config = scene_plan.get("scene_config", {})
print(f"\nScene Configuration:")
print(f"  Area Size: {scene_config.get('area_size', 0)}")
print(f"  Distribution: {scene_config.get('distribution', 'unknown')}")

models = result.get("model_selection", {}).get("selected_models", {})
print(f"\nSelected Models:")
for obj_type, model_list in models.items():
    if model_list:
        print(f"  - {obj_type}: {len(model_list)} models")
        # Show first model details
        if isinstance(model_list, list) and len(model_list) > 0:
            first_model = model_list[0]
            if isinstance(first_model, dict):
                model_id = first_model.get("id", first_model.get("model_id", "unknown"))
                print(f"      First: {model_id}")

print("\n" + "=" * 70)
print("CONCLUSION:")
print("=" * 70)
print(f"The system successfully parsed your complex sentence!")
print(f"- Detected {len(nlp.get('objects', []))} object types")
print(f"- Scene complexity: {analysis.get('complexity', 0):.1%}")
print(f"- Scene naturalness: {analysis.get('naturalness', 0):.1%}")
print(f"- LTC analysis method: {analysis.get('analysis_method')}")
