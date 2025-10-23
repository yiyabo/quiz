"""
CCI 竞赛的机器学习基线（纯 Python 实现）

思路：
1. 读取 train / val / test 三个数据集
2. 在训练集中为每个节点统计正/负边次数与比例
3. 将这些节点统计值组合成边的特征
4. 使用简单的梯度下降 Logistic Regression 进行训练
5. 在验证集上打印 Accuracy / F1
6. 使用 train+val 重新训练，并对测试集生成提交文件
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

Edge = Tuple[int, int, int]
EdgeNoLabel = Tuple[int, int]
NodeStats = Dict[int, Dict[str, float]]


def read_edges(path: Path, expect_label: bool = True) -> List[Edge]:
    edges: List[Edge] = []
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = int(row["source"])
            target = int(row["target"])
            if expect_label:
                label = int(row["label"])
            else:
                label = 0
            edges.append((source, target, label))
    return edges


def read_edges_without_label(path: Path) -> List[EdgeNoLabel]:
    edges: List[EdgeNoLabel] = []
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = int(row["source"])
            target = int(row["target"])
            edges.append((source, target))
    return edges


def compute_node_stats(edges: Sequence[Edge]) -> NodeStats:
    stats: NodeStats = {}
    for source, target, label in edges:
        for node in (source, target):
            entry = stats.setdefault(node, {"pos": 0.0, "neg": 0.0})
            if label == 1:
                entry["pos"] += 1.0
            else:
                entry["neg"] += 1.0
    for entry in stats.values():
        total = entry["pos"] + entry["neg"]
        entry["total"] = total
        entry["pos_ratio"] = entry["pos"] / total if total > 0 else 0.0
        entry["neg_ratio"] = entry["neg"] / total if total > 0 else 0.0
    return stats


def get_node_info(stats: NodeStats, node: int) -> Dict[str, float]:
    if node in stats:
        return stats[node]
    return {"pos": 0.0, "neg": 0.0, "total": 0.0, "pos_ratio": 0.0, "neg_ratio": 0.0}


def build_edge_features(edges: Sequence[Tuple[int, int]], stats: NodeStats) -> List[List[float]]:
    features: List[List[float]] = []
    for source, target in edges:
        src = get_node_info(stats, source)
        tgt = get_node_info(stats, target)
        src_total = src["total"]
        tgt_total = tgt["total"]
        src_pos_ratio = src["pos_ratio"]
        tgt_pos_ratio = tgt["pos_ratio"]

        feature_vector = [
            src_total,
            tgt_total,
            src["pos"],
            tgt["pos"],
            src["neg"],
            tgt["neg"],
            src_pos_ratio,
            tgt_pos_ratio,
            (src_pos_ratio + tgt_pos_ratio) / 2.0,
            src_pos_ratio - tgt_pos_ratio,
            src_pos_ratio * tgt_pos_ratio,
            src_total + tgt_total,
            src_total - tgt_total,
            src_total * tgt_total,
            min(src_total, tgt_total),
            max(src_total, tgt_total),
            1.0 if source == target else 0.0,
        ]
        features.append(feature_vector)
    return features


def standardize(
    features: List[List[float]],
    mean: List[float] | None = None,
    std: List[float] | None = None,
) -> Tuple[List[List[float]], List[float], List[float]]:
    if not features:
        raise ValueError("Features list is empty")
    n_samples = len(features)
    n_features = len(features[0])
    if mean is None:
        mean = [0.0] * n_features
        for j in range(n_features):
            mean[j] = sum(sample[j] for sample in features) / n_samples
    if std is None:
        std = [0.0] * n_features
        for j in range(n_features):
            variance = sum((sample[j] - mean[j]) ** 2 for sample in features) / n_samples
            std[j] = math.sqrt(variance)
            if std[j] < 1e-6:
                std[j] = 1.0
    normalized = []
    for sample in features:
        normalized.append([(sample[j] - mean[j]) / std[j] for j in range(n_features)])
    return normalized, mean, std


def dot_product(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def sigmoid(z: float) -> float:
    if z >= 0:
        exp_neg = math.exp(-z)
        return 1.0 / (1.0 + exp_neg)
    exp_pos = math.exp(z)
    return exp_pos / (1.0 + exp_pos)


def train_logistic_regression(
    features: List[List[float]],
    labels: Sequence[int],
    learning_rate: float = 0.05,
    epochs: int = 300,
    l2: float = 1e-4,
) -> Tuple[List[float], float]:
    n_samples = len(features)
    n_features = len(features[0])
    weights = [0.0] * n_features
    bias = 0.0

    for epoch in range(epochs):
        grad_w = [0.0] * n_features
        grad_b = 0.0
        loss = 0.0

        for x, y in zip(features, labels):
            z = dot_product(weights, x) + bias
            pred = sigmoid(z)
            error = pred - y
            for j in range(n_features):
                grad_w[j] += error * x[j]
            grad_b += error

            # 对数损失
            loss += -(y * math.log(pred + 1e-9) + (1 - y) * math.log(1 - pred + 1e-9))

        # 平均梯度 + L2 正则
        for j in range(n_features):
            grad_w[j] = grad_w[j] / n_samples + l2 * weights[j]
        grad_b /= n_samples
        loss = loss / n_samples + (l2 / 2.0) * sum(w * w for w in weights)

        # 参数更新
        for j in range(n_features):
            weights[j] -= learning_rate * grad_w[j]
        bias -= learning_rate * grad_b

        if epoch % 50 == 0 or epoch == epochs - 1:
            print(f"Epoch {epoch:3d} | loss={loss:.4f}")

    return weights, bias


def predict_probabilities(features: List[List[float]], weights: Sequence[float], bias: float) -> List[float]:
    return [sigmoid(dot_product(weights, x) + bias) for x in features]


def predict_labels(probs: Iterable[float], threshold: float = 0.5) -> List[int]:
    return [1 if p >= threshold else 0 for p in probs]


def compute_metrics(y_true: Sequence[int], y_pred: Sequence[int]) -> Tuple[float, float]:
    total = len(y_true)
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    accuracy = correct / total if total > 0 else 0.0

    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return accuracy, f1


def main() -> None:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2]
    dataset_dir = repo_root / "cci test" / "dataset"

    train_edges = read_edges(dataset_dir / "train_edges.csv", expect_label=True)
    val_edges = read_edges(dataset_dir / "val_edges.csv", expect_label=True)
    test_edges = read_edges_without_label(dataset_dir / "test_edges.csv")

    # 训练阶段：仅用训练集统计节点特征
    train_stats = compute_node_stats(train_edges)
    train_features = build_edge_features([(s, t) for s, t, _ in train_edges], train_stats)
    train_labels = [label for _, _, label in train_edges]

    train_features_std, mean, std = standardize(train_features)
    weights, bias = train_logistic_regression(train_features_std, train_labels)

    # 验证集评估
    val_features = build_edge_features([(s, t) for s, t, _ in val_edges], train_stats)
    val_features_std, _, _ = standardize(val_features, mean=mean, std=std)
    val_labels = [label for _, _, label in val_edges]
    val_probs = predict_probabilities(val_features_std, weights, bias)
    val_preds = predict_labels(val_probs, threshold=0.5)
    val_acc, val_f1 = compute_metrics(val_labels, val_preds)
    print(f"[Validation] Accuracy={val_acc:.4f}, F1={val_f1:.4f}")

    # 使用 train + val 重新训练
    full_edges = train_edges + val_edges
    full_stats = compute_node_stats(full_edges)
    full_features = build_edge_features([(s, t) for s, t, _ in full_edges], full_stats)
    full_labels = [label for _, _, label in full_edges]
    full_features_std, full_mean, full_std = standardize(full_features)
    final_weights, final_bias = train_logistic_regression(full_features_std, full_labels)

    # 生成测试集预测
    test_features = build_edge_features(test_edges, full_stats)
    test_features_std, _, _ = standardize(test_features, mean=full_mean, std=full_std)
    test_probs = predict_probabilities(test_features_std, final_weights, final_bias)
    test_preds = predict_labels(test_probs, threshold=0.5)

    output_dir = repo_root / "submissions"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "cci_ml_baseline.csv"

    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "label"])
        for (source, target), label in zip(test_edges, test_preds):
            writer.writerow([source, target, label])

    print(f"✅ 生成提交文件: {output_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
