"""Cross-model evaluation helpers, re-exported from part4.evaluation.

Part 4's evaluation module is the group's single auditable source of truth for
metrics, threshold tables and the development split. Part 3 re-exports the same
objects so the Random Forest pipeline cannot drift from the XGBoost pipeline;
tests/test_part3.py::test_reexports_match_part4 pins this contract.

paired_bootstrap is re-implemented here (identical recipe and labels as
part4.experiment.paired_bootstrap) so Part 3 stays runnable without xgboost.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from part4.evaluation import (COST_RATIOS, feature_target, metrics,
                              select_threshold, split_development,
                              threshold_table)

__all__ = ["COST_RATIOS", "feature_target", "metrics", "paired_bootstrap",
           "select_threshold", "split_development", "threshold_table"]


def paired_bootstrap(y, baseline, tuned, threshold, repeats=1000, seed=20260905):
    """Stratified paired bootstrap on test outcomes (same recipe as Part 4)."""
    y = np.asarray(y)
    rng = np.random.default_rng(seed)
    groups = [np.flatnonzero(y == label) for label in [0, 1]]
    loss_default = np.where(y == 1, 5 * (tuned < .5), (tuned >= .5)).astype(float)
    loss_selected = np.where(y == 1, 5 * (tuned < threshold), (tuned >= threshold)).astype(float)
    draws = []
    for _ in range(repeats):
        i = np.concatenate([rng.choice(g, size=len(g), replace=True) for g in groups])
        draws.append([average_precision_score(y[i], tuned[i]),
                      roc_auc_score(y[i], tuned[i]),
                      average_precision_score(y[i], tuned[i]) - average_precision_score(y[i], baseline[i]),
                      roc_auc_score(y[i], tuned[i]) - roc_auc_score(y[i], baseline[i]),
                      (loss_selected[i] - loss_default[i]).mean() * 1000])
    observed = [average_precision_score(y, tuned), roc_auc_score(y, tuned),
                average_precision_score(y, tuned) - average_precision_score(y, baseline),
                roc_auc_score(y, tuned) - roc_auc_score(y, baseline),
                (loss_selected - loss_default).mean() * 1000]
    labels = ["Tuned AP", "Tuned ROC-AUC", "AP difference: tuned - baseline",
              "ROC-AUC difference: tuned - baseline",
              "Cost/1000 difference: tuned r=5 threshold - tuned threshold 0.5"]
    low, high = np.percentile(draws, [2.5, 97.5], axis=0)
    return pd.DataFrame({"Quantity": labels, "Estimate": observed,
                         "CI_low": low, "CI_high": high, "Bootstrap_replicates": repeats})
