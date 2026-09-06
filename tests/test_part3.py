import numpy as np
import pandas as pd
import pytest

from part3.evaluation import (COST_RATIOS, feature_target, metrics,
                              paired_bootstrap, select_threshold,
                              split_development, threshold_table)
import part4.evaluation as p4


def frame(n=80):
    return pd.DataFrame({"row_id": np.arange(n), "SEX": [1, 2] * (n // 2),
                         "EDUCATION": [1, 2, 3, 4] * (n // 4),
                         "MARRIAGE": [1, 2] * (n // 2),
                         "LIMIT_BAL": np.arange(n) * 1000,
                         "default": [0, 0, 0, 1] * (n // 4)})


def test_reexports_match_part4():
    """Single source of truth: Part 3 must use the exact Part 4 objects."""
    assert COST_RATIOS == p4.COST_RATIOS
    for name in ["feature_target", "metrics", "select_threshold",
                 "split_development", "threshold_table"]:
        assert globals()[name] is getattr(p4, name)


def test_row_id_and_label_cannot_be_predictors():
    x, y = feature_target(frame())
    assert "row_id" not in x and "default" not in x
    assert list(y) == frame()["default"].tolist()


def test_inner_split_preserves_membership_is_disjoint_and_repeatable():
    a, b = split_development(frame())
    a2, b2 = split_development(frame())
    assert (len(a), len(b)) == (60, 20)
    assert set(a.row_id).isdisjoint(b.row_id)
    assert set(a.row_id) | set(b.row_id) == set(range(80))
    assert a.equals(a2) and b.equals(b2)
    assert a.default.mean() == b.default.mean() == 0.25


def test_metrics_match_hand_calculation():
    m = metrics([0, 1, 0, 1], [.1, .2, .8, .9], .5)
    assert [m[k] for k in ["TN", "FP", "FN", "TP"]] == [1, 1, 1, 1]
    assert m["Accuracy"] == m["Recall"] == m["Precision"] == .5
    assert m["Cost_5"] == 6
    assert m["ROC-AUC"] == .75


def test_threshold_selection_counts_tied_scores_as_a_group():
    t = threshold_table([0, 1, 0, 1], [.2, .2, .8, .8])
    assert len(t) == 3
    assert select_threshold(t, 5) == .2


def test_identical_models_have_zero_paired_bootstrap_differences():
    p = np.array([.1, .2, .8, .9])
    result = paired_bootstrap([0, 1, 0, 1], p, p, .5, repeats=100).set_index("Quantity")
    for metric in ["AP", "ROC-AUC"]:
        row = result.loc[f"{metric} difference: tuned - baseline"]
        assert row.Estimate == row.CI_low == row.CI_high == 0
