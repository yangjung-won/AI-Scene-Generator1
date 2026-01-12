"""
场景参数预测器
加载训练好的模型，从文本预测场景参数

使用方法:
    predictor = ScenePredictor()
    params = predictor.predict("春天来了，树木开始发芽")
    # params = {
    #     'tau': 1.25,
    #     'complexity': 0.5,
    #     'naturalness': 0.7,
    #     ...
    # }
"""

import pickle
import numpy as np
from pathlib import Path
import jieba


class ScenePredictor:
    """场景参数预测器"""
    
    def __init__(self, model_path=None, vectorizer_path=None):
        """
        初始化预测器
        
        Args:
            model_path: 模型文件路径
            vectorizer_path: 向量化器路径
        """
        self.model = None
        self.vectorizer = None
        self.is_loaded = False
        
        # 参数名称映射
        self.param_names = [
            'time_constant_tau',      # 0
            'complexity_factor',      # 1
            'naturalness_score',      # 2
            'adaptation_rate',        # 3
            'scene_parameter_4',      # 4
            'scene_parameter_5',      # 5
            'scene_parameter_6',      # 6
            'scene_parameter_7',      # 7
            'scene_parameter_8',      # 8
            'scene_parameter_9',      # 9
            'scene_parameter_10',     # 10
            'scene_parameter_11',     # 11
            'scene_parameter_12',     # 12
            'scene_parameter_13',     # 13
            'scene_parameter_14',     # 14
            'scene_parameter_15',     # 15
        ]
        
        # 尝试加载模型
        if model_path and vectorizer_path:
            self.load_model(model_path, vectorizer_path)
        else:
            self._try_load_default_model()
    
    def _try_load_default_model(self):
        """尝试加载默认模型"""
        models_dir = Path(__file__).parent / 'models'
        
        if not models_dir.exists():
            print("[WARN] 模型目录不存在，请先训练模型")
            return
        
        # 查找可用模型
        model_files = list(models_dir.glob('*.pkl'))
        model_files = [f for f in model_files if 'vectorizer' not in f.name]
        
        if not model_files:
            print("[WARN] 未找到训练好的模型，请先运行 train_model.py")
            return
        
        # 使用第一个找到的模型
        model_file = model_files[0]
        model_name = model_file.stem
        vectorizer_file = models_dir / f'{model_name}_vectorizer.pkl'
        
        if vectorizer_file.exists():
            self.load_model(model_file, vectorizer_file)
        else:
            print(f"[WARN] 未找到对应的向量化器: {vectorizer_file}")
    
    def load_model(self, model_path, vectorizer_path):
        """加载模型和向量化器"""
        try:
            model_path = Path(model_path)
            vectorizer_path = Path(vectorizer_path)
            
            if not model_path.exists():
                print(f"[ERROR] 模型文件不存在: {model_path}")
                return False
            
            if not vectorizer_path.exists():
                print(f"[ERROR] 向量化器文件不存在: {vectorizer_path}")
                return False
            
            # 加载模型
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # 加载向量化器
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            self.is_loaded = True
            print(f"[OK] 模型加载成功: {model_path.name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 模型加载失败: {e}")
            return False
    
    def predict(self, text):
        """
        预测场景参数
        
        Args:
            text: 场景描述文本
            
        Returns:
            dict: 预测的参数字典
        """
        if not self.is_loaded:
            print("[WARN] 模型未加载，返回默认参数")
            return self._get_default_parameters()
        
        try:
            # 1. 分词
            words = jieba.lcut(text)
            text_seg = ' '.join(words)
            
            # 2. 特征提取
            X = self.vectorizer.transform([text_seg])
            
            # 3. 预测
            prediction = self.model.predict(X)[0]
            
            # 4. 组织结果
            result = {}
            for i, name in enumerate(self.param_names):
                result[name] = float(prediction[i])
            
            # 添加元数据
            result['prediction_method'] = 'trained_model'
            result['model_type'] = type(self.model).__name__
            
            return result
            
        except Exception as e:
            print(f"[ERROR] 预测失败: {e}")
            return self._get_default_parameters()
    
    def predict_batch(self, texts):
        """
        批量预测
        
        Args:
            texts: 文本列表
            
        Returns:
            list: 预测结果列表
        """
        results = []
        for text in texts:
            results.append(self.predict(text))
        return results
    
    def _get_default_parameters(self):
        """获取默认参数（当模型未加载时）"""
        return {
            'time_constant_tau': 1.25,
            'complexity_factor': 0.5,
            'naturalness_score': 0.7,
            'adaptation_rate': 0.1,
            'scene_parameter_4': 0.7,
            'scene_parameter_5': 0.5,
            'scene_parameter_6': 0.8,
            'scene_parameter_7': 0.5,
            'scene_parameter_8': 0.55,
            'scene_parameter_9': 0.51,
            'scene_parameter_10': 0.6,
            'scene_parameter_11': 0.5,
            'scene_parameter_12': 0.5,
            'scene_parameter_13': 0.5,
            'scene_parameter_14': 0.5,
            'scene_parameter_15': 0.5,
            'prediction_method': 'default',
            'model_type': 'None'
        }
    
    def get_info(self):
        """获取预测器信息"""
        info = {
            'is_loaded': self.is_loaded,
            'model_type': type(self.model).__name__ if self.model else None,
            'feature_dim': self.vectorizer.get_feature_names_out().shape[0] if self.vectorizer else None,
            'param_count': len(self.param_names)
        }
        return info


# ============================================
# 便捷函数
# ============================================

def create_predictor(model_path=None, vectorizer_path=None):
    """创建预测器实例"""
    return ScenePredictor(model_path, vectorizer_path)


def quick_predict(text, model_path=None, vectorizer_path=None):
    """快速预测（单次使用）"""
    predictor = ScenePredictor(model_path, vectorizer_path)
    return predictor.predict(text)


# ============================================
# 测试代码
# ============================================

def test_predictor():
    """测试预测器"""
    print("="*70)
    print("测试场景参数预测器")
    print("="*70)
    
    # 创建预测器
    predictor = ScenePredictor()
    
    # 显示信息
    info = predictor.get_info()
    print(f"\n预测器信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 测试文本
    test_texts = [
        "春天来了，树木开始发芽，草地上长满了花",
        "高山峻岭，白雪皑皑，云雾缭绕",
        "城市里高楼林立，街道上车水马龙",
        "宁静的森林，阳光透过树叶洒下斑驳的光影"
    ]
    
    print(f"\n开始预测:")
    for i, text in enumerate(test_texts, 1):
        print(f"\n测试 {i}: {text}")
        params = predictor.predict(text)
        
        print(f"  预测参数:")
        print(f"    tau (时间常数): {params['time_constant_tau']:.3f}")
        print(f"    complexity (复杂度): {params['complexity_factor']:.3f}")
        print(f"    naturalness (自然度): {params['naturalness_score']:.3f}")
        print(f"    方法: {params['prediction_method']}")
    
    print(f"\n" + "="*70)
    print("测试完成")
    print("="*70)


if __name__ == "__main__":
    test_predictor()




























