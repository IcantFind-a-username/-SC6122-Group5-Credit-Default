"""Build figures and report text from a completed run; no training or tuning.
Run: python -m part2.plots_and_report [--output-dir results/decision_tree]
"""

import argparse
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

ROOT = Path(__file__).resolve().parents[1]


def table(frame, columns):
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame.iterrows():
        lines.append(
            "| "
            + " | ".join(
                f"{row[c]:.4f}" if isinstance(row[c], (float, np.floating)) else str(row[c]) for c in columns
            )
            + " |"
        )
    return "\n".join(lines)


def run(output_dir=None):
    out = Path(output_dir).resolve() if output_dir else ROOT / "results/decision_tree"
    figs = out / "figures"
    figs.mkdir(exist_ok=True)
    protocol = json.loads((out / "protocol_frozen.json").read_text())
    cv = pd.read_csv(out / "cv_results.csv")
    final = pd.read_csv(out / "test_metrics.csv", float_precision="round_trip")
    selected = cv.loc[cv.Candidate == protocol["Selected_candidate"]].iloc[0]
    base_cv = cv.loc[(cv.Max_depth.astype(str) == "Unlimited") & (cv.Min_samples_leaf == 1)].iloc[0]
    fixed = cv.loc[cv.Min_samples_leaf == 1]
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, key, label in zip(axes, ["AP", "ROC_AUC"], ["Average Precision (selection metric)", "ROC-AUC"]):
        ax.plot(fixed.Max_depth, fixed["Mean_fit_" + key], "o-", label="CV training folds", color="#2563a6")
        ax.errorbar(
            fixed.Max_depth,
            fixed["Mean_CV_" + key],
            yerr=fixed["SD_CV_" + key],
            fmt="o-",
            capsize=3,
            label="CV holdout folds ± SD",
            color="#db7d22",
        )
        ax.set(xlabel="Maximum depth", ylabel=label)
        ax.grid(alpha=0.18)
        ax.legend(fontsize=9)
    fig.suptitle("Overfitting as depth increases | minimum leaf size fixed at 1")
    fig.tight_layout()
    fig.savefig(figs / "01_overfitting.png", dpi=180)
    plt.close(fig)

    model = joblib.load(out / "tuned_pipeline.joblib")
    tree = model.named_steps["model"]
    names = model.named_steps["preprocess"].get_feature_names_out()
    fig, ax = plt.subplots(figsize=(19, 9))
    plot_tree(
        tree, feature_names=names, max_depth=2, filled=True, rounded=True, impurity=False, fontsize=10, ax=ax
    )
    depth_label = (
        "Unlimited"
        if protocol["Selected_parameters"]["max_depth"] is None
        else str(protocol["Selected_parameters"]["max_depth"])
    )
    ax.set_title(
        f"Selected decision tree: top levels | max_depth={depth_label}, "
        f"min_samples_leaf={protocol['Selected_parameters']['min_samples_leaf']}",
        fontsize=17,
    )
    fig.text(
        0.5,
        0.01,
        "value = [non-default, default] in the 18,000 fitting rows; (...) indicates omitted lower branches.",
        ha="center",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(figs / "02_tree_top_levels.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.5))
    for ax, (_, row) in zip(axes, final.iterrows()):
        cm = np.array([[row.TN, row.FP], [row.FN, row.TP]], dtype=int)
        ax.imshow(cm, cmap="Blues", vmin=0, vmax=6000)
        for (i, j), value in np.ndenumerate(cm):
            ax.text(
                j,
                i,
                str(value),
                ha="center",
                va="center",
                fontsize=17,
                color="white" if value > 3000 else "#18212c",
            )
        ax.set(
            xticks=[0, 1],
            yticks=[0, 1],
            xticklabels=["Normal", "Default"],
            yticklabels=["Normal", "Default"],
            xlabel="Predicted label",
            ylabel="Actual label",
            title=row.Model,
        )
    fig.suptitle("Final test set: 6,000 clients | score ≥ 0.5 predicts default")
    fig.tight_layout()
    fig.savefig(figs / "03_test_confusion.png", dpi=180)
    plt.close(fig)

    t = final.iloc[1]
    columns = ["Model", "AP", "ROC-AUC", "Accuracy", "Precision", "Recall", "F1"]
    final_table = table(final, columns)
    fit = pd.read_csv(out / "fit_metrics.csv", float_precision="round_trip")
    validation = pd.read_csv(out / "validation_metrics.csv", float_precision="round_trip")
    full = pd.concat(
        [
            fit.assign(Partition="Fit (18,000)"),
            validation.assign(Partition="Validation (6,000)"),
            final.assign(Partition="Test (6,000)"),
        ]
    )
    full.to_csv(out / "all_partition_metrics.csv", index=False)
    p = protocol["Selected_parameters"].copy()
    if p["max_depth"] is None:
        p["max_depth"] = "unlimited (None)"
    rules = pd.read_csv(out / "leaf_rules.csv")
    examples = rules.groupby("Predicted_default_at_0.5", group_keys=False).head(1)
    examples.to_csv(out / "representative_rules.csv", index=False)
    root = tree.tree_
    root_name = names[root.feature[0]]
    root_cut = root.threshold[0]
    left, right = root.children_left[0], root.children_right[0]
    root_values = []
    for n in [left, right]:
        values = root.value[n][0]
        root_values.append(float(values[1] / values.sum()))

    report = f"""# Decision Tree: Methods and Findings

## Methods
We used the team-supplied cleaned data and fixed 24,000/6,000 training–test split. To match Part 4, the development data were further split into 18,000 fitting and 6,000 validation observations. The fitting/validation membership and five stratified cross-validation folds were verified against Part 4's saved row-level files. SEX, EDUCATION and MARRIAGE were one-hot encoded within each training fold; other features retained their cleaned numeric values. The row identifier and outcome were excluded from predictors.

An unrestricted decision tree was compared with 21 combinations of maximum depth (2, 3, 4, 5, 6, 8, unlimited) and minimum leaf size (1, 20, 100). Parameters were selected by mean five-fold Average Precision (AP); ROC-AUC was also recorded. The selected setting was maximum depth **{p["max_depth"]}** and minimum leaf size **{p["min_samples_leaf"]}**. Both models were fitted on the 18,000 fitting observations and kept unchanged for validation and final test evaluation. Consistent with Part 4, no refit used the validation rows. The fixed classification rule was probability ≥0.5; thresholds were not tuned in this contribution.

## Overfitting and final evaluation
The unrestricted model's mean CV training AP was {base_cv.Mean_fit_AP:.4f}, versus {base_cv.Mean_CV_AP:.4f} on CV holdout folds. For the selected tree, the corresponding values were {selected.Mean_fit_AP:.4f} and {selected.Mean_CV_AP:.4f} (holdout-fold SD {selected.SD_CV_AP:.4f}). The reduced training–validation gap supports controlling tree complexity. The selected tree has no explicit depth cap, but its minimum leaf size still limits complexity: the fitted tree has {tree.get_depth()} levels of splits and {tree.get_n_leaves()} leaves. The depth curve fixes minimum leaf size at 1 and isolates the effect of depth; it is distinct from the joint parameter search.

{final_table}

The final test results above use the same 6,000 clients for both trees. At threshold 0.5, the selected tree produced {int(t.TP)} true positives, {int(t.FN)} false negatives, {int(t.FP)} false positives and {int(t.TN)} true negatives. AP and ROC-AUC assess ranking; accuracy and the default-class precision/recall/F1 use the fixed threshold. All-negative prediction would achieve 77.88% accuracy, illustrating why accuracy alone is insufficient.

## Interpretable rules
The root split was `{root_name} <= {root_cut:g}`. Within the fitting data, the default proportions were {root_values[0]:.2%} on the left and {root_values[1]:.2%} on the right. These are observed node proportions, not causal effects or externally validated individual probabilities. The top-level figure is truncated: its intermediate nodes must not be described as final predictions. Exact root-to-leaf rules, support counts and default fractions are recorded in `leaf_rules.csv`; `representative_rules.csv` contains the largest-support leaf for each predicted class present.

## Limitations and integration
Hyperparameter selection uses CV scores and can introduce selection optimism; final claims therefore use held-out test metrics. The test data were first loaded by this runner after parameters and fitted models were frozen. Other team members' test results were already visible; this is not a new globally untouched dataset. No additional parameter changes were made after this decision-tree test evaluation. No confidence intervals or significance claims are supplied. The historical Taiwan sample and retained identical feature vectors limit generalization claims. Model rules describe associations, not causal explanations.

The integration now includes verified RF results and a separately labelled post-hoc logistic supplement. Legacy logistic CSVs remain unverified: their original training procedure and PR-AUC definition were not recoverable. The complete comparison and submission materials are in results/final/ and submission/. Shared splits do not imply identical search budgets or globally unseen historical test data.

## Sources
- Team repository, reviewed base commit `{protocol["Source_commit"]}`: https://github.com/IcantFind-a-username/-SC6122-Group5-Credit-Default
- UCI dataset: Yeh, I. (2009). Default of Credit Card Clients. https://doi.org/10.24432/C55S3H (CC BY 4.0).
- Decision-tree implementation: https://scikit-learn.org/stable/modules/tree.html
"""
    (out / "report_en.md").write_text(report, encoding="utf-8")
    zh = f"""# 第二位：决策树正式实验说明

本版本取代旧版初步实验。直接使用小组清洗后的公共 CSV，不使用旧 Excel 自行划分。

## 已完成
- 与第四位核对了拟合/验证客户及五折划分，成员和顺序完全一致。
- 18,000 人拟合；6,000 人验证；6,000 人最终测试。
- 搜索 21 组参数，按五折平均 AP 选参；不在测试集上选参数。
- 最优参数：max_depth={p["max_depth"]}，min_samples_leaf={p["min_samples_leaf"]}。
- 为公平对照第四位，选参后仍用 18,000 人拟合，不加入验证集重训。
- 完成固定阈值 0.5 的最终测试，输出规则、图表、报告英文内容。

## 最终测试结果
{final_table}

AP 是 Average Precision，概括 precision–recall 表现；不要把 AP 直接等同于梯形积分 PR-AUC。AUC 不是准确率。表中 recall、precision、F1 均针对违约类。

调参树识别出 {int(t.TP)} 个违约客户，漏掉 {int(t.FN)} 个；误报 {int(t.FP)} 个正常客户，正确识别 {int(t.TN)} 个正常客户。阈值取舍由第四位负责，本部分只需解释这里的局限。

## 过拟合证据
默认树 CV 训练 AP={base_cv.Mean_fit_AP:.4f}，CV 验证 AP={base_cv.Mean_CV_AP:.4f}；调参后为 {selected.Mean_fit_AP:.4f} 和 {selected.Mean_CV_AP:.4f}。训练和验证差距缩小，是本部分讨论的重点。最终虽然不限制最大深度，但叶节点至少 100 人仍有效限制复杂度；实际拟合树深度为 {tree.get_depth()}，叶节点数量为 {tree.get_n_leaves()}。

01_overfitting 图固定叶节点最小样本数为 1，只改变深度；最终模型来自两个参数的联合搜索。图中 SD 表示五折成绩标准差，不是置信区间。

## 判断规则
根节点先判断 {root_name} <= {root_cut:g}。左侧训练客户的违约比例为 {root_values[0]:.2%}，右侧为 {root_values[1]:.2%}。数字是拟合数据中的观察比例，不是因果关系，也不是已经校准的未来概率。

叶节点规则见 leaf_rules.csv，示例见 representative_rules.csv。树图只展示顶部，省略的分支不是叶节点，不可以把它当成最终判断。

## 为什么与旧版结果不同
旧版使用未合并类别的 Excel，在 24,000 人上按 ROC-AUC 选参；新版使用小组清洗 CSV，在与第四位相同的 18,000 人上按 AP 选参。旧版成绩是交叉验证；这里的主要成绩是最终测试，不能混在一起比较。

## 最终整合说明
整合分支现已包含随机森林核验结果和单独标记的逻辑回归事后复现补充。原逻辑回归 CSV 的训练过程与 PR-AUC 定义仍不可恢复，不与补充实验混淆。完整比较与交付文件位于 results/final/ 和 submission/；共同划分不代表搜索预算相同或历史测试集从未被全组查看。
"""
    (out / "report_zh.md").write_text(zh, encoding="utf-8")
    slides = f"""# Member 2: three-minute presentation content

## Slide 1 — Decision tree and complexity control (about 55 seconds)
Visual: figures/01_overfitting.png.
- Same supplied data and development/CV membership as Part 4.
- 21 combinations; select by five-fold Average Precision.
- Selected max_depth={p["max_depth"]}, min_samples_leaf={p["min_samples_leaf"]}.
- CV AP: unrestricted {base_cv.Mean_CV_AP:.3f}; selected {selected.Mean_CV_AP:.3f}.

Speaker notes: My part focuses on the decision tree. It learns a sequence of conditions to divide customers into groups. An unrestricted tree can memorize training examples, so a strong training score does not necessarily mean it will work well on new customers. I tested maximum depth and minimum leaf size using the same cross-validation membership as Part Four. I selected the model using Average Precision. This figure fixes the minimum leaf size at one, so it isolates the effect of increasing depth. The final model was selected from the joint search over both parameters.

## Slide 2 — What the tree learned (about 55 seconds)
Visual: figures/02_tree_top_levels.png.
- First split: {root_name} ≤ {root_cut:g}.
- Fit-data default share: left {root_values[0]:.1%}; right {root_values[1]:.1%}.
- Lower nodes add further conditions; displayed branches are truncated.
- Rules describe predictive associations, not causality.

Speaker notes: The tree is interpretable because we can follow the actual conditions it learned. Its first split uses {root_name}. The two branches contain customers with very different observed default rates in the fitting data. Later splits refine those groups using additional information. These proportions help explain the model, but they are not proof that a feature causes default. The figure shows only the upper levels; the dots represent further branches. Complete leaf rules and sample counts are included in my results.

## Slide 3 — Final test results and limitations (about 60 seconds)
Visual: figures/03_test_confusion.png; add a small two-row metric table.
- Selected tree: AP {t.AP:.3f}; ROC-AUC {t["ROC-AUC"]:.3f}.
- Accuracy {t.Accuracy:.1%}; precision {t.Precision:.1%}; recall {t.Recall:.1%}.
- False negatives {int(t.FN)}; false positives {int(t.FP)}.
- Fixed threshold 0.5; threshold optimization is addressed in Part 4.

Speaker notes: After selecting the parameters, I froze both fitted models and evaluated them on the same six thousand test customers. The selected model achieved an AP of {t.AP:.3f} and a ROC-AUC of {t["ROC-AUC"]:.3f}. At the fixed threshold of zero point five, recall was {t.Recall:.1%}, so there were still {int(t.FN)} missed defaults. There were also {int(t.FP)} false alarms among normal customers. This shows why we need several metrics instead of accuracy alone. My conclusion is that complexity control helps the tree generalize, while the remaining false negatives make the threshold trade-off relevant to the next part of our project.

## 问答准备
Q：你做了什么？ A：接公共数据，训练和调参决策树，核对开发集划分，分析过拟合和实际规则，完成固定阈值最终测试。
Q：为什么 AP？ A：违约是少数类，AP 关注 precision–recall 表现，并与第四位选参标准一致。
Q：为什么不是把树越长越好？ A：过细规则会拟合训练样本中的偶然情况，训练分高但验证分低。
Q：为什么不用验证集一起重训？ A：为了与第四位实际使用的 18,000 人拟合方案对齐，避免混入训练规模差异。
Q：为什么不挑测试集上最好的参数？ A：那会让测试数据参与选择，失去独立评价意义。
Q：代码是自己手写算法吗？ A：采用 scikit-learn 的决策树实现；本部分工作是实验设计、参数搜索、评价和解释。

这份是可编辑展示文案，不是已排版的 PPT。根据实际语速排练并控制在约三分钟。
"""
    (out / "presentation_notes.md").write_text(slides, encoding="utf-8")
    print("Figures and bilingual report / presentation text generated:", out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    run(parser.parse_args().output_dir)
