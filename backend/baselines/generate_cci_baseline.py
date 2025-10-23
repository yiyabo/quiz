"""
CCI 基线预测脚本

读取 cci test/dataset/test_edges.csv，并生成一个简单的 CSV 提交文件。
当前基线策略：始终预测 0（表示无细胞间相互作用）。
"""
from pathlib import Path
import csv


def generate_baseline_submission(output_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    dataset_dir = repo_root / "cci test" / "dataset"
    test_file = dataset_dir / "test_edges.csv"

    if not test_file.exists():
        raise FileNotFoundError(f"找不到测试集文件: {test_file}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with test_file.open("r", newline="") as infile, output_path.open("w", newline="") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ["source", "target", "label"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            writer.writerow({
                "source": row["source"],
                "target": row["target"],
                "label": 0  # 简单基线：全部预测为 0
            })

    print(f"✅ 基线提交文件已生成: {output_path.relative_to(repo_root)}")


# 默认输出到项目根目录的 submissions/cci_baseline.csv
if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[2]
    default_output = repo_root / "submissions" / "cci_baseline.csv"
    generate_baseline_submission(default_output)
