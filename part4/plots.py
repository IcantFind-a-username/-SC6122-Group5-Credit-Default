"""Generate publication figures from saved predictions; never retrain or tune."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_curve

from .experiment import ROOT

BLUE, ORANGE, GREEN, GREY = "#0072B2", "#D55E00", "#009E73", "#777777"


def generate(output):
    output = Path(output)
    figures = output / "figures"
    figures.mkdir(exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titlesize": 12, "figure.dpi": 120, "savefig.dpi": 200,
                         "svg.fonttype": "none"})
    predictions = pd.read_csv(output / "test_predictions.csv", float_precision="round_trip")
    result = pd.read_csv(output / "test_metrics.csv").set_index("Model")
    protocol = json.loads((output / "protocol_frozen.json").read_text())
    thresholds = protocol["Validation_thresholds"]
    threshold = thresholds["5"]

    def save(fig, name):
        for ext in ["png", "svg"]:
            fig.savefig(figures / f"{name}.{ext}", bbox_inches="tight", facecolor="white")
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for name, column, color in [("Baseline XGBoost", "Baseline_probability", BLUE),
                                ("Tuned XGBoost", "Tuned_probability", ORANGE)]:
        fpr, tpr, _ = roc_curve(predictions.default, predictions[column])
        axes[0].plot(fpr, tpr, color=color, lw=1.8,
                     label=f"{name}: AUC {result.loc[name, 'ROC-AUC']:.3f}")
        precision, recall, _ = precision_recall_curve(predictions.default, predictions[column])
        axes[1].plot(recall, precision, color=color, lw=1.5,
                     label=f"{name}: AP {result.loc[name, 'AP']:.3f}")
    axes[0].plot([0, 1], [0, 1], "--", color=GREY, lw=1, label="Chance ranking")
    axes[1].axhline(predictions.default.mean(), ls="--", color=GREY, lw=1, label="Test prevalence")
    for ax, xlabel, ylabel, title in zip(axes, ["False positive rate", "Recall"],
                                        ["True positive rate", "Precision"],
                                        ["Held-out ROC curves", "Held-out precision-recall curves"]):
        ax.set(xlabel=xlabel, ylabel=ylabel, title=title, xlim=(0, 1), ylim=(0, 1.02))
        ax.legend(loc="lower right" if ax is axes[0] else "upper right", fontsize=8)
        ax.grid(alpha=.15)
    save(fig, "01_ranking_curves")

    curves = pd.read_csv(output / "validation_thresholds.csv", float_precision="round_trip").sort_values("Threshold")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    axes[0].plot(curves.Threshold, curves.Recall, label="Recall", color=BLUE)
    axes[0].plot(curves.Threshold, curves.Precision, label="Precision", color=ORANGE)
    axes[0].plot(curves.Threshold, curves.Alert_rate, label="Fraction flagged", color=GREEN, ls="--")
    axes[0].set(title="Validation decision trade-off", xlabel="Decision threshold", ylabel="Rate", xlim=(0, 1))
    axes[0].legend(fontsize=9)
    axes[1].plot(curves.Threshold, curves.Cost_5_per_1000, color=BLUE)
    chosen = curves.iloc[(curves.Threshold - threshold).abs().argmin()]
    axes[1].scatter([threshold], [chosen.Cost_5_per_1000], color=ORANGE, zorder=3)
    axes[1].set(title="Validation cost: FP + 5 FN", xlabel="Decision threshold",
                ylabel="Hypothetical cost units per 1,000", xlim=(0, 1))
    for ax in axes:
        ax.axvline(threshold, color=ORANGE, ls=":", lw=1.3)
        ax.axvline(.5, color=GREY, ls="--", lw=1)
        ax.grid(alpha=.15)
    axes[1].text(.04, .94, f"Selected on validation: {threshold:.3f}\nDashed grey: default 0.500",
                 transform=axes[1].transAxes, va="top", fontsize=9,
                 bbox={"facecolor": "white", "edgecolor": "none", "alpha": .95})
    save(fig, "02_validation_threshold")

    fig, axes = plt.subplots(1, 2, figsize=(9, 4), layout="constrained")
    for ax, model, title in zip(axes, ["Tuned XGBoost", "Tuned XGBoost / cost ratio 5"],
                                ["Default threshold: 0.500", f"Validation-selected threshold: {threshold:.3f}"]):
        row = result.loc[model]
        matrix = np.array([[row.TN, row.FP], [row.FN, row.TP]], dtype=int)
        ax.imshow(matrix, cmap="Blues", vmin=0, vmax=4500)
        for (i, j), value in np.ndenumerate(matrix):
            ax.text(j, i, f"{value:,}", ha="center", va="center", fontsize=15,
                    color="white" if value > 2600 else "black")
        ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["No default", "Default"],
               yticklabels=["No default", "Default"], xlabel="Predicted", ylabel="Observed", title=title)
    fig.suptitle("Same tuned model, same 6,000 test customers", fontsize=12)
    save(fig, "03_confusion_matrices")

    importance = pd.read_csv(output / "validation_importance.csv").head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 4.5), layout="constrained")
    ax.barh(importance.Feature, importance.Mean_AP_decrease, xerr=importance.SD_AP_decrease,
            color=BLUE, error_kw={"capsize": 3, "elinewidth": 1})
    ax.set(title="Validation permutation importance", xlabel="Decrease in AP after permutation (mean +/- SD, 5 repeats)")
    ax.grid(axis="x", alpha=.15)
    save(fig, "04_feature_importance")

    fig, ax = plt.subplots(figsize=(9, 4.5), layout="constrained")
    ratios, x = [1, 3, 5, 10], np.arange(4)
    configs = [("Tuned model, threshold 0.5", BLUE, -.27, lambda r: "Tuned XGBoost"),
               ("Validation-selected threshold", ORANGE, -.09, lambda r: f"Tuned XGBoost / cost ratio {r}"),
               ("Always negative", GREY, .09, lambda r: "Always negative"),
               ("Always positive", GREEN, .27, lambda r: "Always positive")]
    for label, color, offset, get_model in configs:
        values = [result.loc[get_model(r), f"Cost_{r}_per_1000"] for r in ratios]
        ax.bar(x + offset, np.asarray(values, dtype=float), width=.18, color=color, label=label)
    ax.set(xticks=x, xticklabels=["1:1", "3:1", "5:1 (primary)", "10:1"],
           xlabel="Assumed false-negative : false-positive cost ratio",
           ylabel="Held-out hypothetical cost units per 1,000", title="Cost sensitivity on the fixed test set")
    ax.legend(fontsize=8, ncol=2, loc="upper left")
    ax.grid(axis="y", alpha=.15)
    save(fig, "05_cost_sensitivity")
    return figures


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/xgboost")
    print(generate(parser.parse_args().output_dir))
