# Cell-Cell Interaction (CCI) Score Prediction Task


本任务要求你根据空间转录组数据，预测是否有细胞间相互作用（Cell-Cell Interaction, CCI）。

给定一对细胞（source cell 和 target cell），你需要：
1. 计算它们之间的CCI分数
2. 预测它们的相互作用标签：
   - **Label 1**: 强相互作用
   - **Label 0**: 无相互作用

---

## 📂 数据文件说明
### 1. `Visium_Human_Breast_Cancer_filtered_feature_bc_matrix.h5ad`
空间转录组数据文件（AnnData格式），包含：
- **基因表达矩阵**: 4,898个细胞 × 36,601个基因
- **空间坐标**: 每个细胞在组织切片上的2D坐标
- **细胞索引**: 0-4897

### 2. `celltalk_human_lr_pair.txt`
配体-受体（Ligand-Receptor, L-R）对数据库


### 3. 边数据文件
#### `train_edges.csv` (12,000条边)
训练集，用于学习CCI分数与标签的关系
#### `val_edges.csv` (4,000条边)
验证集，用于测试模型效能
#### `test_edges.csv` (4,000条边)
测试集，需要你预测的数据

**文件格式**:
```csv
source,target,label
1999,2313,1
4252,1273,0
2979,2047,1
...
```

- `source`: 源细胞ID（配体表达细胞）
- `target`: 目标细胞ID（受体表达细胞）
- `label`: 相互作用有无标签（0或1）
