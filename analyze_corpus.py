"""
语料库分析脚本
分析 training_data_scenes.json 数据集

分析内容：
1. 基础统计（数据量、文本长度）
2. 标签分布分析
3. 高频词统计
4. 词性分析
5. 文本-标签相关性
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import sys

# 检查依赖
try:
    import jieba
except ImportError:
    print("[ERROR] 需要安装jieba: pip install jieba")
    sys.exit(1)

# 配置中文字体（防止乱码）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def load_data(file_path='training_data_scenes.json'):
    """加载训练数据"""
    print(f"[LOADING] 加载数据: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"[OK] 加载完成，共 {len(data)} 条数据")
    return data


def analyze_text_statistics(data):
    """文本基础统计"""
    print("\n" + "="*70)
    print("文本统计分析")
    print("="*70)
    
    texts = [item['text'] for item in data]
    lengths = [len(text) for text in texts]
    
    print(f"总数据量: {len(data)} 条")
    print(f"平均文本长度: {np.mean(lengths):.1f} 字")
    print(f"最短文本: {min(lengths)} 字")
    print(f"最长文本: {max(lengths)} 字")
    print(f"中位数长度: {np.median(lengths):.1f} 字")
    
    # 文本长度分布
    plt.figure(figsize=(10, 5))
    plt.hist(lengths, bins=30, edgecolor='black', alpha=0.7)
    plt.xlabel('文本长度（字）')
    plt.ylabel('频次')
    plt.title('训练数据文本长度分布')
    plt.axvline(np.mean(lengths), color='r', linestyle='--', label=f'平均值: {np.mean(lengths):.1f}')
    plt.legend()
    plt.tight_layout()
    plt.savefig('corpus_analysis_length.png', dpi=300, bbox_inches='tight')
    print("[SAVED] 文本长度分布图: corpus_analysis_length.png")
    plt.close()
    
    # 显示一些示例
    print(f"\n示例文本:")
    for i in range(min(3, len(texts))):
        print(f"  {i+1}. {texts[i][:50]}...")
    
    return texts, lengths


def analyze_labels(data):
    """标签分布分析"""
    print("\n" + "="*70)
    print("标签分布分析（16维场景参数）")
    print("="*70)
    
    labels = np.array([item['labels'] for item in data])
    print(f"标签矩阵形状: {labels.shape}")
    
    # 各维度统计
    print(f"\n各维度统计:")
    print(f"{'维度':<6} {'均值':<8} {'标准差':<8} {'最小值':<8} {'最大值':<8}")
    print("-" * 50)
    
    for i in range(labels.shape[1]):
        col = labels[:, i]
        print(f"维度{i:<3} {col.mean():<8.3f} {col.std():<8.3f} "
              f"{col.min():<8.3f} {col.max():<8.3f}")
    
    # 可视化标签分布
    fig, axes = plt.subplots(4, 4, figsize=(16, 12))
    axes = axes.flatten()
    
    for i in range(labels.shape[1]):
        axes[i].hist(labels[:, i], bins=20, edgecolor='black', alpha=0.7)
        axes[i].set_title(f'维度 {i}')
        axes[i].set_xlabel('值')
        axes[i].set_ylabel('频次')
        axes[i].axvline(labels[:, i].mean(), color='r', linestyle='--', linewidth=1)
    
    plt.tight_layout()
    plt.savefig('corpus_analysis_labels.png', dpi=300, bbox_inches='tight')
    print("[SAVED] 标签分布图: corpus_analysis_labels.png")
    plt.close()
    
    # 标签相关性矩阵
    correlation = np.corrcoef(labels.T)
    plt.figure(figsize=(12, 10))
    plt.imshow(correlation, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
    plt.colorbar(label='相关系数')
    plt.title('标签维度间相关性矩阵')
    plt.xlabel('维度')
    plt.ylabel('维度')
    plt.xticks(range(16))
    plt.yticks(range(16))
    plt.tight_layout()
    plt.savefig('corpus_analysis_correlation.png', dpi=300, bbox_inches='tight')
    print("[SAVED] 标签相关性图: corpus_analysis_correlation.png")
    plt.close()
    
    return labels


def analyze_vocabulary(texts):
    """词汇分析"""
    print("\n" + "="*70)
    print("词汇统计分析")
    print("="*70)
    
    # 分词
    all_words = []
    for text in texts:
        words = jieba.lcut(text)
        all_words.extend([w for w in words if len(w.strip()) > 0])
    
    # 统计
    word_freq = Counter(all_words)
    print(f"总词数: {len(all_words)}")
    print(f"不重复词数: {len(word_freq)}")
    print(f"平均每句词数: {len(all_words) / len(texts):.1f}")
    
    # 高频词
    print(f"\nTop 30 高频词:")
    for i, (word, count) in enumerate(word_freq.most_common(30), 1):
        print(f"  {i:2d}. {word:<6} : {count:>4} 次 ({count/len(texts):.2f}次/句)")
    
    # 词频分布（幂律分布）
    freqs = [count for word, count in word_freq.most_common(200)]
    plt.figure(figsize=(10, 5))
    plt.plot(range(1, len(freqs)+1), freqs, 'b-', linewidth=2)
    plt.xlabel('词排名')
    plt.ylabel('出现频次')
    plt.title('词频分布（Top 200）')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('corpus_analysis_word_freq.png', dpi=300, bbox_inches='tight')
    print("[SAVED] 词频分布图: corpus_analysis_word_freq.png")
    plt.close()
    
    return word_freq


def analyze_vocabulary_by_category(texts):
    """按类别分析词汇"""
    print("\n" + "="*70)
    print("领域词汇分类统计")
    print("="*70)
    
    # 定义场景相关词汇类别
    categories = {
        '自然景观': ['山', '河', '湖', '树', '林', '草', '花', '石', '水', '云', '天', 
                  '日', '月', '星', '风', '雨', '雪'],
        '植物': ['树木', '草地', '花朵', '树林', '森林', '灌木', '藤蔓', '叶子', 
               '根', '枝', '干', '果'],
        '动物': ['鸟', '虫', '兽', '鱼', '蝶', '蜂', '蚁', '羊', '牛', '马'],
        '建筑': ['房', '屋', '楼', '塔', '桥', '路', '墙', '门', '窗', '亭'],
        '颜色': ['红', '绿', '蓝', '黄', '白', '黑', '灰', '紫', '橙', '粉'],
        '形态': ['大', '小', '高', '低', '长', '短', '宽', '窄', '厚', '薄'],
        '质感': ['粗', '细', '软', '硬', '光', '暗', '亮', '滑', '糙'],
        '数量': ['一', '二', '三', '多', '少', '些', '群', '片', '堆'],
    }
    
    # 统计各类别词频
    all_words = []
    for text in texts:
        all_words.extend(jieba.lcut(text))
    
    word_freq = Counter(all_words)
    
    category_stats = {}
    for category, keywords in categories.items():
        total = sum(word_freq.get(word, 0) for word in keywords)
        category_stats[category] = total
    
    # 排序并显示
    sorted_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n各类别词汇出现频次:")
    for category, count in sorted_categories:
        print(f"  {category:<10} : {count:>5} 次")
    
    # 可视化
    categories_names = [c for c, _ in sorted_categories]
    counts = [c for _, c in sorted_categories]
    
    plt.figure(figsize=(10, 6))
    plt.barh(categories_names, counts, color='steelblue', edgecolor='black')
    plt.xlabel('出现频次')
    plt.title('场景相关词汇分类统计')
    plt.tight_layout()
    plt.savefig('corpus_analysis_categories.png', dpi=300, bbox_inches='tight')
    print("[SAVED] 类别统计图: corpus_analysis_categories.png")
    plt.close()


def generate_report(data, texts, labels, word_freq):
    """生成分析报告"""
    print("\n" + "="*70)
    print("生成分析报告")
    print("="*70)
    
    report = []
    report.append("=" * 70)
    report.append("场景描述语料库分析报告")
    report.append("=" * 70)
    report.append("")
    
    # 基础统计
    report.append("## 1. 数据概况")
    report.append(f"- 总数据量: {len(data)} 条")
    report.append(f"- 平均文本长度: {np.mean([len(t) for t in texts]):.1f} 字")
    report.append(f"- 标签维度: {labels.shape[1]}")
    report.append(f"- 词汇量: {len(word_freq)}")
    report.append("")
    
    # 标签统计
    report.append("## 2. 标签参数分析")
    report.append("各维度统计（推测含义）:")
    dim_names = [
        "tau (时间常数)",
        "complexity (复杂度)", 
        "naturalness (自然度)",
        "参数3", "参数4", "参数5", "参数6", "参数7",
        "参数8", "参数9", "参数10", "参数11", "参数12",
        "参数13", "参数14", "参数15"
    ]
    
    for i in range(labels.shape[1]):
        col = labels[:, i]
        report.append(f"- 维度{i} ({dim_names[i]}): "
                     f"均值={col.mean():.3f}, 标准差={col.std():.3f}")
    report.append("")
    
    # 高频词
    report.append("## 3. 高频词 Top 20")
    for i, (word, count) in enumerate(word_freq.most_common(20), 1):
        report.append(f"{i:2d}. {word} - {count} 次")
    report.append("")
    
    # 保存报告
    report_text = '\n'.join(report)
    with open('corpus_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print("[SAVED] 分析报告: corpus_analysis_report.txt")
    print("\n报告内容:")
    print(report_text)


def main():
    """主函数"""
    print("\n" + "="*70)
    print("场景描述语料库分析工具")
    print("="*70)
    
    # 加载数据
    data = load_data()
    
    # 文本统计
    texts, lengths = analyze_text_statistics(data)
    
    # 标签分析
    labels = analyze_labels(data)
    
    # 词汇分析
    word_freq = analyze_vocabulary(texts)
    
    # 类别分析
    analyze_vocabulary_by_category(texts)
    
    # 生成报告
    generate_report(data, texts, labels, word_freq)
    
    print("\n" + "="*70)
    print("分析完成！")
    print("="*70)
    print("\n生成的文件:")
    print("  1. corpus_analysis_length.png - 文本长度分布")
    print("  2. corpus_analysis_labels.png - 标签分布")
    print("  3. corpus_analysis_correlation.png - 标签相关性")
    print("  4. corpus_analysis_word_freq.png - 词频分布")
    print("  5. corpus_analysis_categories.png - 类别统计")
    print("  6. corpus_analysis_report.txt - 分析报告")
    print("\n建议:")
    print("  - 查看报告了解数据特征")
    print("  - 根据高频词优化关键词库")
    print("  - 分析标签相关性指导特征工程")


if __name__ == "__main__":
    main()




























