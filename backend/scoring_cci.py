"""
CCI竞赛评分服务 - 细胞间相互作用预测
"""
import csv
import os
from typing import Dict, List


def load_csv_as_dict(filename: str, key_cols: List[str]) -> Dict:
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


def evaluate_cci_submission(submission_file: str, labels_file: str) -> Dict:
    """
    评估CCI竞赛提交文件
    
    提交格式:
    source,target,label
    1999,2313,1
    4252,1273,0
    
    返回格式:
    {
        'accuracy': float,
        'precision': float,
        'recall': float,
        'f1': float,
        'final_score': float,
        'tp': int,
        'tn': int,
        'fp': int,
        'fn': int,
        'total': int,
        'status': 'success' or 'error',
        'error_message': str (if error)
    }
    """
    
    # 检查文件是否存在
    if not os.path.exists(submission_file):
        return {
            'status': 'error',
            'error_message': f'找不到提交文件: {submission_file}'
        }
    
    if not os.path.exists(labels_file):
        return {
            'status': 'error',
            'error_message': f'找不到标签文件: {labels_file}'
        }
    
    try:
        # 加载真实标签
        labels = load_csv_as_dict(labels_file, ['source', 'target'])
        
        # 加载学生提交
        submissions = load_csv_as_dict(submission_file, ['source', 'target'])
        
        # 验证格式
        required_cols = ['source', 'target', 'label']
        if len(submissions) == 0:
            return {
                'status': 'error',
                'error_message': '提交文件为空'
            }
        
        sample_row = next(iter(submissions.values()))
        for col in required_cols:
            if col not in sample_row:
                return {
                    'status': 'error',
                    'error_message': f'缺少必需列 "{col}"。要求的列: {required_cols}'
                }
        
        # 检查样本数量
        if len(submissions) != len(labels):
            return {
                'status': 'error',
                'error_message': f'提交样本数({len(submissions)}) 不等于 测试集样本数({len(labels)})'
            }
        
        # 计算评分指标
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
            
            pred_str = submissions[key]['label'].strip()
            
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
            return {
                'status': 'error',
                'error_message': f'{len(missing_samples)} 个样本缺失'
            }
        
        if invalid_predictions:
            sample_invalid = invalid_predictions[0]
            return {
                'status': 'error',
                'error_message': f'{len(invalid_predictions)} 个无效预测值（应为0或1）。例如: {sample_invalid[0]} -> "{sample_invalid[1]}"'
            }
        
        # 计算指标
        total = tp + tn + fp + fn
        
        if total == 0:
            return {
                'status': 'error',
                'error_message': '没有有效的预测样本'
            }
        
        accuracy = (tp + tn) / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # 加权得分（与PPI相同）
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
        
        return {
            'status': 'success',
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'final_score': final_score,
            'tp': tp,
            'tn': tn,
            'fp': fp,
            'fn': fn,
            'total': total
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error_message': f'评分过程出错: {str(e)}'
        }

