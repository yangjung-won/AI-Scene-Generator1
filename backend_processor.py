"""
AI场景生成器 - 后端主处理器
协调所有后端模块的处理流程

作者: AI Team
版本: 2.0 (集成真实LTC神经网络)
"""

import json
import os
from pathlib import Path

# ===========================================
# 后端主处理器
# ===========================================

class AISceneGeneratorBackend:
    """AI场景生成器后端主处理器（增强版）"""

    def __init__(self, nlp_model_path=None, ltc_model_path=None, device='cpu'):
        """
        初始化后端处理器
        
        Args:
            nlp_model_path: NLP模型路径（保留接口兼容性）
            ltc_model_path: LTC模型权重路径
            device: 计算设备 ('cpu' or 'cuda')
        """
        self.nlp_model_path = nlp_model_path
        self.ltc_model_path = ltc_model_path
        self.device = device
        self.modules = {}
        self._load_modules()

    def _load_modules(self):
        """加载所有后端子模块"""
        try:
            print("🔧 正在加载后端模块...")
            
            # NLP解析模块（增强版，集成文本编码）
            from nlp_parser import NLPParser
            self.modules['nlp'] = NLPParser(
                use_pretrained_model=self.nlp_model_path is not None, 
                model_path=self.nlp_model_path
            )
            print("✅ NLP解析模块加载成功（增强版 with 文本编码）")

            # LTC分析模块（真实神经网络）
            from ltc_analyzer import LTCAnalyzer
            use_pretrained = self.ltc_model_path is not None
            self.modules['ltc'] = LTCAnalyzer(
                use_pretrained_model=use_pretrained, 
                model_path=self.ltc_model_path,
                device=self.device
            )
            
            if use_pretrained and self.ltc_model_path and os.path.exists(self.ltc_model_path):
                print("✅ LTC分析模块加载成功（使用预训练神经网络）")
            else:
                print("✅ LTC分析模块加载成功（使用随机初始化，建议训练后使用）")

            # 场景规划模块
            from scene_planner import ScenePlanner
            self.modules['planner'] = ScenePlanner()
            print("✅ 场景规划模块加载成功")

            # 模型选择模块
            from model_selector import ModelSelector
            self.modules['selector'] = ModelSelector()
            print("✅ 模型选择模块加载成功")
            
            print("🎉 所有模块加载完成")

        except ImportError as e:
            print(f"❌ 模块加载失败: {e}")
            import traceback
            traceback.print_exc()
            raise

    def process_request(self, natural_language_input):
        """
        处理前端请求的完整流程

        Args:
            natural_language_input (str): 用户的自然语言输入

        Returns:
            dict: 处理结果
        """
        try:
            print("🚀 后端开始处理请求...")

            # 步骤1: NLP解析
            print("📝 步骤1: 自然语言解析")
            nlp_result = self.modules['nlp'].parse(natural_language_input)

            # 步骤2: LTC分析
            print("🧠 步骤2: LTC神经网络分析")
            ltc_result = self.modules['ltc'].analyze(nlp_result)

            # 步骤3: 场景规划
            print("📐 步骤3: 场景规划")
            scene_plan = self.modules['planner'].plan_scene(ltc_result)

            # 步骤4: 模型选择
            print("🎨 步骤4: 模型选择")
            model_selection = self.modules['selector'].select_models(scene_plan)

            # 组合结果
            result = {
                "success": True,
                "analysis": {
                    "scene_type": nlp_result.get("scene_type", "unknown"),
                    "objects": nlp_result.get("objects", []),
                    "complexity": ltc_result.get("complexity_factor", 0.0),
                    "naturalness": ltc_result.get("naturalness_score", 0.0),
                    "time_constant": ltc_result.get("time_constant_tau", 1.5),
                    "total_objects": len(model_selection.get("selected_models", {})),
                    "confidence": nlp_result.get("confidence", 0.5),
                    "analysis_method": ltc_result.get("analysis_method", "unknown"),
                    "styles": nlp_result.get("styles", []),
                    "moods": nlp_result.get("moods", []),
                },
                "nlp_result": nlp_result,
                "ltc_result": ltc_result,
                "scene_plan": scene_plan,
                "model_selection": model_selection,
                "metadata": {
                    "version": "2.0",
                    "using_neural_network": ltc_result.get("analysis_method") == "neural_network",
                    "device": self.device,
                }
            }

            print("✅ 后端处理完成")
            print(f"   分析方法: {result['analysis']['analysis_method']}")
            print(f"   场景类型: {result['analysis']['scene_type']}")
            print(f"   复杂度: {result['analysis']['complexity']:.2f}")
            print(f"   自然度: {result['analysis']['naturalness']:.2f}")
            return result

        except Exception as e:
            print(f"❌ 后端处理异常: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"后端处理异常: {str(e)}"
            }

    def get_module_status(self):
        """获取各模块状态"""
        status = {}
        for name, module in self.modules.items():
            module_status = {
                "loaded": True,
                "type": type(module).__name__
            }
            
            # LTC模块的额外状态信息
            if name == 'ltc' and hasattr(module, 'ltc_model'):
                module_status['has_neural_network'] = module.ltc_model is not None
                module_status['device'] = str(module.device)
                module_status['using_pretrained'] = module.use_pretrained_model
            
            # NLP模块的额外状态信息
            if name == 'nlp' and hasattr(module, 'text_encoder'):
                module_status['has_text_encoder'] = module.text_encoder is not None
                module_status['encoding_method'] = getattr(module.text_encoder, 'method', 'unknown')
            
            status[name] = module_status
        
        return status
    
    def save_ltc_model(self, save_path):
        """
        保存LTC模型
        
        Args:
            save_path: 保存路径
        """
        if 'ltc' in self.modules and hasattr(self.modules['ltc'], 'save_model'):
            self.modules['ltc'].save_model(save_path)
            print(f"✅ LTC模型已保存: {save_path}")
        else:
            print("❌ LTC模块不支持保存")
    
    def set_device(self, device):
        """
        设置计算设备
        
        Args:
            device: 'cpu' or 'cuda'
        """
        self.device = device
        if 'ltc' in self.modules and hasattr(self.modules['ltc'], 'set_device'):
            self.modules['ltc'].set_device(device)
            print(f"✅ 设备已切换到: {device}")
