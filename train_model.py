"""
模型训练脚本
基于 training_data_scenes.json 训练场景参数预测模型

训练流程：
1. 加载数据和预处理
2. 文本特征提取（TF-IDF / Word2Vec / BERT）
3. 训练回归模型（Ridge / Random Forest / Neural Network）
4. 评估模型性能
5. 保存最佳模型
"""

import json
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import jieba

print("[INFO] 场景参数预测模型训练系统 v1.0")
print("="*70)

# ============================================
# 1. 数据加载与预处理
# ============================================

def load_and_preprocess_data(file_path='training_data_scenes.json'):
    """加载并预处理训练数据"""
    print(f"\n[STEP 1] 加载数据: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    texts = [item['text'] for item in data]
    labels = np.array([item['labels'] for item in data])
    
    print(f"  - 数据量: {len(texts)} 条")
    print(f"  - 标签维度: {labels.shape[1]}")
    print(f"  - 文本平均长度: {np.mean([len(t) for t in texts]):.1f} 字")
    
    return texts, labels


def segment_texts(texts):
    """中文分词"""
    print(f"\n[STEP 2] 中文分词")
    
    segmented = []
    for i, text in enumerate(texts):
        words = jieba.lcut(text)
        segmented.append(' '.join(words))
        
        if (i+1) % 100 == 0:
            print(f"  - 进度: {i+1}/{len(texts)}")
    
    print(f"  - 分词完成")
    return segmented


# ============================================
# 2. 特征提取
# ============================================

def extract_tfidf_features(texts_seg, max_features=1000):
    """提取TF-IDF特征"""
    print(f"\n[STEP 3] 提取TF-IDF特征 (max_features={max_features})")
    
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),  # 支持unigram和bigram
        min_df=2,            # 至少出现2次
        max_df=0.8           # 最多出现在80%文档中
    )
    
    X = vectorizer.fit_transform(texts_seg)
    print(f"  - 特征矩阵形状: {X.shape}")
    print(f"  - 特征维度: {X.shape[1]}")
    
    return X, vectorizer


# ============================================
# 3. 模型训练
# ============================================

def train_baseline_model(X_train, y_train, X_test, y_test):
    """训练基线模型 - 岭回归"""
    print(f"\n[STEP 4] 训练基线模型 (Ridge Regression)")
    
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    
    # 预测
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # 评估
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    test_mse = mean_squared_error(y_test, y_pred_test)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    
    print(f"  Training R2: {train_r2:.4f}")
    print(f"  Test R2: {test_r2:.4f}")
    print(f"  Test MSE: {test_mse:.4f}")
    print(f"  Test MAE: {test_mae:.4f}")
    
    # 逐维度评估
    print(f"\n  各维度预测性能:")
    dimension_names = [
        "tau", "complexity", "naturalness",
        "param3", "param4", "param5", "param6", "param7",
        "param8", "param9", "param10", "param11", "param12",
        "param13", "param14", "param15"
    ]
    
    for i in range(y_test.shape[1]):
        r2_i = r2_score(y_test[:, i], y_pred_test[:, i])
        mae_i = mean_absolute_error(y_test[:, i], y_pred_test[:, i])
        print(f"    Dim{i:2d} ({dimension_names[i]:<12}): R2={r2_i:.3f}, MAE={mae_i:.4f}")
    
    return model, {
        'train_r2': train_r2,
        'test_r2': test_r2,
        'test_mse': test_mse,
        'test_mae': test_mae
    }


def train_random_forest(X_train, y_train, X_test, y_test):
    """训练随机森林模型"""
    print(f"\n[STEP 5] 训练随机森林模型 (Random Forest)")
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    print(f"  - 训练中...")
    model.fit(X_train, y_train)
    
    # 预测
    y_pred_test = model.predict(X_test)
    
    # 评估
    test_r2 = r2_score(y_test, y_pred_test)
    test_mse = mean_squared_error(y_test, y_pred_test)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    
    print(f"  Test R2: {test_r2:.4f}")
    print(f"  Test MSE: {test_mse:.4f}")
    print(f"  Test MAE: {test_mae:.4f}")
    
    return model, {
        'test_r2': test_r2,
        'test_mse': test_mse,
        'test_mae': test_mae
    }


# ============================================
# 4. 模型保存
# ============================================

def save_model(model, vectorizer, performance, model_name='best_model'):
    """保存模型和向量化器"""
    print(f"\n[STEP 6] 保存模型")
    
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    # 保存模型
    model_path = models_dir / f'{model_name}.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"  - 模型已保存: {model_path}")
    
    # 保存向量化器
    vectorizer_path = models_dir / f'{model_name}_vectorizer.pkl'
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"  - 向量化器已保存: {vectorizer_path}")
    
    # 保存性能指标
    performance_path = models_dir / f'{model_name}_performance.json'
    with open(performance_path, 'w', encoding='utf-8') as f:
        json.dump(performance, f, indent=2, ensure_ascii=False)
    print(f"  - 性能指标已保存: {performance_path}")
    
    return model_path, vectorizer_path


# ============================================
# 5. 模型测试
# ============================================

def test_model(model, vectorizer, test_texts):
    """测试模型预测"""
    print(f"\n[STEP 7] 模型测试")
    
    for i, text in enumerate(test_texts, 1):
        # 分词
        words = jieba.lcut(text)
        text_seg = ' '.join(words)
        
        # 特征提取
        X = vectorizer.transform([text_seg])
        
        # 预测
        prediction = model.predict(X)[0]
        
        print(f"\n测试 {i}: {text[:40]}...")
        print(f"  预测参数:")
        print(f"    tau={prediction[0]:.3f}, "
              f"complexity={prediction[1]:.3f}, "
              f"naturalness={prediction[2]:.3f}")


# ============================================
# 主程序
# ============================================

def main():
    """主训练流程"""
    print("\n" + "="*70)
    print("开始训练流程")
    print("="*70)
    
    # 1. 加载数据
    texts, labels = load_and_preprocess_data()
    
    # 2. 分词
    texts_seg = segment_texts(texts)
    
    # 3. 提取特征
    X, vectorizer = extract_tfidf_features(texts_seg, max_features=1000)
    
    # 4. 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=0.2, random_state=42
    )
    print(f"\n数据集划分:")
    print(f"  训练集: {X_train.shape[0]} 条")
    print(f"  测试集: {X_test.shape[0]} 条")
    
    # 5. 训练模型
    ridge_model, ridge_perf = train_baseline_model(X_train, y_train, X_test, y_test)
    rf_model, rf_perf = train_random_forest(X_train, y_train, X_test, y_test)
    
    # 6. 选择最佳模型
    print(f"\n" + "="*70)
    print("Model Comparison")
    print("="*70)
    print(f"Ridge Regression: R2 = {ridge_perf['test_r2']:.4f}")
    print(f"Random Forest:    R2 = {rf_perf['test_r2']:.4f}")
    
    if rf_perf['test_r2'] > ridge_perf['test_r2']:
        best_model = rf_model
        best_perf = rf_perf
        model_name = 'random_forest'
        print(f"\nBest model: Random Forest")
    else:
        best_model = ridge_model
        best_perf = ridge_perf
        model_name = 'ridge_regression'
        print(f"\nBest model: Ridge Regression")
    
    # 7. 保存最佳模型
    model_path, vectorizer_path = save_model(
        best_model, vectorizer, best_perf, model_name
    )
    
    # 8. 测试模型
    test_texts = [
        "春天来了，树木开始发芽，草地上长满了花",
        "高山峻岭，白雪皑皑，云雾缭绕",
        "城市里高楼林立，街道上车水马龙"
    ]
    test_model(best_model, vectorizer, test_texts)
    
    # 9. 生成总结
    print(f"\n" + "="*70)
    print("训练完成！")
    print("="*70)
    print(f"\n模型文件:")
    print(f"  1. {model_path}")
    print(f"  2. {vectorizer_path}")
    print(f"\n性能指标:")
    for key, value in best_perf.items():
        print(f"  {key}: {value:.4f}")
    print(f"\n使用方法:")
    print(f"  from predictor import ScenePredictor")
    print(f"  predictor = ScenePredictor('{model_path}', '{vectorizer_path}')")
    print(f"  params = predictor.predict('您的场景描述')")


if __name__ == "__main__":
    main()

