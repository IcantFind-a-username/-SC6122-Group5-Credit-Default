# Part 2 — Decision Tree

本目录是第二位成员的决策树部分，配合仓库公共数据和第四位的评价函数使用。
已完成正式模型实验、最终测试、规则分析及过拟合图。报告和三页展示文案在结果目录中；不包含排版好的 PPTX。

## Windows 最简单运行方式

下载实验包并解压，用 VS Code 打开最外层项目文件夹：应同时看到 `part2`、`part4`、`data`、`results` 和 `requirements-part2.txt`。终端必须位于这个目录，不要进入 part2 子目录，也不要放进旧版 decision_tree_starter。

创建独立环境（Python 3.12）：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-part2.txt
```

结果已经随包提供，想先查看无需运行。要在自己电脑复现，写到单独目录：

```powershell
.\.venv\Scripts\python.exe -m part2.experiment --output-dir results/decision_tree_reproduction
.\.venv\Scripts\python.exe -m part2.plots_and_report --output-dir results/decision_tree_reproduction
```

实验会显示 21 个候选参数的进度，然后打印最终测试结果。已有 protocol_frozen.json 的实验目录禁止覆盖；重复复现时指定另一个新目录即可，无需删除现有结果。不能根据测试集结果继续选参。

## 合入小组仓库

本部分新增：`part2/`、`04_decision_tree.ipynb`、`requirements-part2.txt`、`results/decision_tree/`。
不需要覆盖同学的 `part4`、公共 `data` 或其他模型结果。代码调用原有 `part4.evaluation`，不需要安装 XGBoost，不会执行同学的训练流程。

本交付包内附公共数据及上述评价函数，是为了可独立复现；上传自己的贡献时只需新增四项，不要重复上传 `.venv` 或整个旧版实验包。
当前仅本地完成，尚未推送 GitHub。

## 和第四位对齐的内容

| 项目 | 本部分做法 |
|---|---|
| 输入 | 原样读取 `data/splits/train.csv` / `test.csv` |
| 样本 | 18,000 拟合；6,000 验证；6,000 最终测试 |
| 划分核验 | 开发集成员与顺序、五折成员与顺序，逐行对照第四位保存的 CSV |
| 类别编码 | SEX、EDUCATION、MARRIAGE 在每个训练折内 one-hot；其余保留公共清洗结果 |
| 搜索 | 最大深度 2/3/4/5/6/8/None × 叶节点最少样本 1/20/100，共 21 组 |
| 选参指标 | 五折平均 AP；并列时选候选编号最小者 |
| 预测规则 | 概率 ≥0.5 视为违约，与第四位一致；不调用 predict 的平票规则 |
| 最终模型 | 仅拟合 18,000 人，不加入验证集重训，与第四位实际流程一致 |
| 测试 | 参数、模型冻结后读取并评价；保存逐客户预测和混淆矩阵 |

候选数量、模型和调参空间不同；逻辑回归完整方法尚不可核实，不宣称四种模型所有细节完全一致。

## 先看哪些结果

1. `results/decision_tree/report_zh.md`：中文进度和结论。
2. `results/decision_tree/test_metrics.csv`：最终测试成绩。
3. `results/decision_tree/figures/01_overfitting.png`：过拟合。
4. `results/decision_tree/figures/02_tree_top_levels.png`：实际判断规则。
5. `results/decision_tree/report_en.md`：可整合进小组报告的英文内容。
6. `results/decision_tree/presentation_notes.md`：三页展示文案、口头稿和问答。

`cv_results.csv` 是选参成绩，不要与 test_metrics 的最终成绩混用。leaf_rules 保存完整叶节点规则；顶部图的中间节点并不是最终预测。

## 来源与边界

基于仓库提交 `0188f4a0df4e46140c8aa8ebfef4ba4a54403255`。
公共数据来源：Yeh, I. (2009), Default of Credit Card Clients, UCI，https://doi.org/10.24432/C55S3H ，CC BY 4.0。
本包保留团队清洗方式（教育 0/5/6 合并为 4，婚姻 0 合并为 3）和数据划分。
共享数据和 part4/evaluation.py 为同学已有工作；新增决策树实验及文案为本部分内容。
历史台湾数据并不能证明模型适用于当前银行业务，规则也不代表因果关系。
