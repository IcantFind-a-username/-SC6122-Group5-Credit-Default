import numpy as np
import pandas as pd
import pytest

from part4.evaluation import feature_target, metrics, select_threshold, split_development, threshold_table
from part4.experiment import make_pipeline


def frame(n=80):
    return pd.DataFrame({"row_id": np.arange(n), "SEX": [1, 2] * (n // 2),
                         "EDUCATION": [1, 2, 3, 4] * (n // 4),
                         "MARRIAGE": [1, 2] * (n // 2),
                         "LIMIT_BAL": np.arange(n) * 1000,
                         "default": [0, 0, 0, 1] * (n // 4)})


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
    assert m["AP"] == pytest.approx(5 / 6)


def test_threshold_selection_counts_tied_scores_as_a_group():
    y = [0, 1, 0, 1]
    p = [.1, .2, .8, .9]
    t = threshold_table(y, p)
    selected = select_threshold(t, 5)
    assert selected == .2  # one FP, no FN: cost 1
    assert metrics(y, p, selected)["Cost_5"] == 1
    tied = threshold_table([0, 1, 0, 1], [.2, .2, .8, .8])
    assert len(tied) == 3  # predict none, both high-score rows, all rows
    for _, r in tied.iterrows():
        direct = metrics([0, 1, 0, 1], [.2, .2, .8, .8], r.Threshold)
        assert r.Cost_5 == direct["Cost_5"]


def test_equal_cost_tie_prefers_largest_threshold():
    t = threshold_table([0, 1], [.5, .5])
    assert select_threshold(t, 1) > 1  # all-negative endpoint, cost equal to all-positive


@pytest.mark.parametrize("p", [[.1, float("nan")], [-.1, .2], [.1, 1.1]])
def test_invalid_scores_fail_instead_of_producing_plausible_metrics(p):
    with pytest.raises(ValueError):
        metrics([0, 1], p, .5)


def test_pipeline_encodes_categories_without_learning_validation_values():
    x, y = feature_target(frame())
    estimator = make_pipeline({"n_estimators": 3, "max_depth": 2}, threads=1)
    estimator.fit(x, y)
    before = [v.copy() for v in estimator.named_steps["preprocess"].named_transformers_["categorical"].categories_]
    unseen = x.iloc[:2].copy()
    unseen["EDUCATION"] = 99
    assert np.isfinite(estimator.predict_proba(unseen)).all()
    after = estimator.named_steps["preprocess"].named_transformers_["categorical"].categories_
    assert all(np.array_equal(a, b) for a, b in zip(before, after))
