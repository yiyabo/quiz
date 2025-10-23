#!/usr/bin/env python3
"""
评分脚本 - 评估学生提交的预测结果

使用方法:
  python3 evaluate_submission.py <submission.csv>

评分指标（加权）:
  - Accuracy: 30%
  - Precision: 20%
  - Recall: 20%
  - F1-Score: 30%

最终得分 = Accuracy×0.3 + Precision×0.2 + Recall×0.2 + F1×0.3
"""

import sys
import csv
import os

def load_csv_as_dict(filename, key_cols):
    """加载CSV文件为字典"""
    data = {}
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if len(key_cols) == 2:
                key = (row[key_cols[0]], row[key_cols[1]])
            else:
                key = row[key_cols[0]]
            data[key] = row
    return data

def evaluate_submission(submission_file, labels_file='test_labels.csv'):
    """评估提交文件"""

    # 检查文件是否存在
    if not os.path.exists(submission_file):
        print(f"错误: 找不到提交文件 {submission_file}")
        sys.exit(1)

    if not os.path.exists(labels_file):
        print(f"错误: 找不到标签文件 {labels_file}")
        sys.exit(1)

    # 加载真实标签
    print("加载测试集真实标签...")
    labels = load_csv_as_dict(labels_file, ['protein_A', 'protein_B'])
    print(f"  测试集样本数: {len(labels)}")

    # 加载学生提交
    print(f"\n加载学生提交: {submission_file}")
    try:
        submissions = load_csv_as_dict(submission_file, ['protein_A', 'protein_B'])
        print(f"  提交样本数: {len(submissions)}")
    except Exception as e:
        print(f"错误: 无法读取提交文件 - {e}")
        sys.exit(1)

    # 验证格式
    print("\n验证提交格式...")
    required_cols = ['protein_A', 'protein_B', 'prediction']
    sample_row = next(iter(submissions.values()))

    for col in required_cols:
        if col not in sample_row:
            print(f"错误: 缺少必需列 '{col}'")
            print(f"要求的列: {required_cols}")
            print(f"实际的列: {list(sample_row.keys())}")
            sys.exit(1)

    # 检查样本数量匹配
    if len(submissions) != len(labels):
        print(f"警告: 提交样本数({len(submissions)}) != 测试集样本数({len(labels)})")

    # 计算评分指标
    print("\n计算评分指标...")

    tp = 0  # True Positive
    tn = 0  # True Negative
    fp = 0  # False Positive
    fn = 0  # False Negative

    missing_samples = []
    invalid_predictions = []

    for key, label_row in labels.items():
        true_label = int(label_row['label'])

        if key not in submissions:
            missing_samples.append(key)
            continue

        pred_str = submissions[key]['prediction'].strip()

        # 验证预测值
        try:
            pred_label = int(pred_str)
            if pred_label not in [0, 1]:
                invalid_predictions.append((key, pred_str))
                continue
        except ValueError:
            invalid_predictions.append((key, pred_str))
            continue

        # 统计混淆矩阵
        if true_label == 1 and pred_label == 1:
            tp += 1
        elif true_label == 0 and pred_label == 0:
            tn += 1
        elif true_label == 0 and pred_label == 1:
            fp += 1
        elif true_label == 1 and pred_label == 0:
            fn += 1

    # 报告错误
    if missing_samples:
        print(f"\n警告: {len(missing_samples)} 个样本缺失")
        if len(missing_samples) <= 5:
            for sample in missing_samples:
                print(f"  缺失: {sample}")

    if invalid_predictions:
        print(f"\n警告: {len(invalid_predictions)} 个无效预测值（应为0或1）")
        if len(invalid_predictions) <= 5:
            for sample, pred in invalid_predictions:
                print(f"  无效: {sample} -> '{pred}'")

    # 计算指标
    total = tp + tn + fp + fn

    if total == 0:
        print("\n错误: 没有有效的预测样本")
        sys.exit(1)

    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    # 加权得分
    weights = {
        'accuracy': 0.3,
        'precision': 0.2,
        'recall': 0.2,
        'f1': 0.3
    }

    final_score = (
        accuracy * weights['accuracy'] +
        precision * weights['precision'] +
        recall * weights['recall'] +
        f1 * weights['f1']
    )

    # 输出结果
    print("\n" + "=" * 70)
    print("评分结果")
    print("=" * 70)

    print(f"\n【混淆矩阵】")
    print(f"  True Positive (TP):  {tp:>6}")
    print(f"  True Negative (TN):  {tn:>6}")
    print(f"  False Positive (FP): {fp:>6}")
    print(f"  False Negative (FN): {fn:>6}")
    print(f"  总计:                {total:>6}")

    print(f"\n【评分指标】")
    print(f"  Accuracy:  {accuracy:.4f}  (权重: {weights['accuracy']:.0%})")
    print(f"  Precision: {precision:.4f}  (权重: {weights['precision']:.0%})")
    print(f"  Recall:    {recall:.4f}  (权重: {weights['recall']:.0%})")
    print(f"  F1-Score:  {f1:.4f}  (权重: {weights['f1']:.0%})")

    print(f"\n【最终得分】")
    print(f"  {final_score:.4f} / 1.0000  ({final_score * 100:.2f}%)")

    print("\n" + "=" * 70)

    # 返回详细结果
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'final_score': final_score,
        'tp': tp,
        'tn': tn,
        'fp': fp,
        'fn': fn,
        'total': total,
        'missing': len(missing_samples),
        'invalid': len(invalid_predictions)
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python3 evaluate_submission.py <submission.csv>")
        print("\n示例:")
        print("  python3 evaluate_submission.py ../submissions/student1_submission.csv")
        sys.exit(1)

    submission_file = sys.argv[1]
    results = evaluate_submission(submission_file)

    # 可以将结果保存到文件
    import json
    result_file = submission_file.replace('.csv', '_score.json')
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n评分结果已保存到: {result_file}")
