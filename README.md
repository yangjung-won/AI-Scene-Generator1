# AI Scene Generator

Transform your ideas into stunning 3D nature scenes with natural language! This AI-powered scene generator uses advanced Liquid Time-Constant (LTC) neural networks to create realistic landscapes, forests, gardens, and natural environments.

## 🌟 Key Features

- **Natural Language Processing**: Simply describe your scene in plain English
- **AI-Powered Generation**: Advanced LTC neural networks analyze complexity, naturalness, and spatial relationships
- **Intelligent Layout**: Smart positioning and clustering algorithms create realistic scene composition
- **Procedural Content**: Automatic generation of trees, flowers, rocks, and architectural elements
- **Seasonal & Style Support**: Create scenes for different seasons, moods, and artistic styles

## 🎨 What You Can Create

- Dense forests with hundreds of trees
- Colorful flower meadows and gardens
- Mountain landscapes and lake scenes
- Urban-nature hybrids with buildings
- Seasonal variations (spring blossoms, autumn colors, winter snowscapes)

## 🧠 Advanced Technology

- Liquid Time-Constant neural networks for continuous scene evolution
- Multi-modal analysis (objects, relationships, emotions, styles)
- Semantic mapping and spatial dependency processing
- Real-time procedural generation for unmatched variety

## 🚀 Quick Start

### Blender Plugin Setup

1. **Download the Plugin**:
   ```bash
   git clone https://github.com/yangjung-won/AI-Scene-Generator.git
   cd AI-Scene-Generator
   ```

2. **Install in Blender**:
   - Open Blender
   - Go to `Edit > Preferences > Add-ons`
   - Click `Install...` and select the plugin file
   - Enable "AI Scene Generator (Hybrid)"

3. **Generate Your First Scene**:
   - Go to the 3D Viewport
   - Look for the "AI Scene" panel in the sidebar (N key)
   - Enter a description like "Peaceful cherry blossom lake"
   - Click "Generate Scene"

## 📁 Project Structure

```
AI-Scene-Generator/
├── backend_processor.py          # Main backend processor
├── ltc_analyzer.py               # LTC neural network analyzer
├── scene_planner.py              # Scene planning and layout
├── procedural_model_generator.py # Procedural model generation
├── nlp_parser.py                 # Natural language processing
├── model_selector.py             # Intelligent model selection
├── scene_manager.py              # Scene management utilities
├── terrain_generator.py          # Terrain generation
├── blender_ai_scene_generator.py # Blender plugin (frontend)
├── models/                       # ML models and data
├── tests/                        # Test files
└── docs/                         # Documentation
```

## 🏗️ Architecture

### Frontend (Blender Plugin)
- User interface with scene description input
- Real-time status updates and progress indicators
- LTC analysis result visualization
- Scene generation controls

### Backend (AI Processing Pipeline)
1. **NLP Analysis**: Parse natural language descriptions
2. **LTC Neural Network**: Advanced parameter calculation
3. **Scene Planning**: Layout optimization and object placement
4. **Model Selection**: Intelligent asset selection
5. **Procedural Generation**: Fallback content creation

### Core Technologies

#### Liquid Time-Constant (LTC) Networks
- **Continuous Time Modeling**: Unlike discrete RNNs, LTC works in continuous time
- **Adaptive Time Constants**: τ adjusts based on scene characteristics
- **Natural Scene Dynamics**: Captures organic growth and evolution patterns

#### Multi-Modal Analysis
- **Semantic Relations**: Understands object relationships (trees near water, flowers under trees)
- **Emotional Context**: Recognizes moods and atmospheres
- **Style Recognition**: Adapts to different artistic preferences

## 🎯 Example Scenes

| Description | LTC Analysis | Generated Scene |
|-------------|--------------|-----------------|
| "Dense forest with flowers" | Complexity: 0.75, Naturalness: 0.9 | 400+ trees, 25 flowers, clustered layout |
| "Peaceful lake scene" | Complexity: 0.6, τ: 1.8 | Calm water, scattered trees, natural distribution |
| "Mountain landscape" | Complexity: 0.8, τ: 0.9 | Rocky terrain, high-altitude trees, dynamic layout |

## 📊 Performance Metrics

- **Scene Generation**: < 30 seconds for complex scenes
- **Object Count**: 300-500 objects per scene
- **Layout Optimization**: Automatic collision avoidance
- **Procedural Fallback**: 100% coverage for missing assets

## 🔧 Requirements

- **Blender**: 4.0 or higher
- **Python**: 3.8+ (included with Blender)
- **Memory**: 4GB+ RAM recommended
- **Storage**: 2GB+ for model assets

## 🧪 Testing

Run the test suite:
```bash
python test_backend.py
python test_full_pipeline.py
python test_procedural_generation.py
```

## 📚 Documentation

- [LTC System Analysis](LTC系统深度分析报告.md) - Detailed technical analysis
- [Tree & Building Improvements](树木数量和建筑改进说明_V4.md) - Recent enhancements
- [Position & Rotation Fixes](物体位置和旋转修复说明.md) - Object placement fixes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with advanced AI techniques for natural scene generation
- Inspired by cutting-edge research in continuous-time neural networks
- Designed for artists, game developers, and 3D enthusiasts

---

**Perfect for creating beautiful natural scenes effortlessly!** 🌳🌸🏞️