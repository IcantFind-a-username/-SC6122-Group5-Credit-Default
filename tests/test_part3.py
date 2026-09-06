from part3.experiment import BASELINE, SEARCH_SPACE, best_candidate, make_pipeline
from part3.misclassification import case_snapshots, compute_profiles, derive_features
from integration.artifacts import save_predictions
from part3.experiment import run
import numpy as np
import pandas as pd
import pytest

from part3.evaluation import (COST_RATIOS, feature_target, metrics,
                              paired_bootstrap, select_threshold,
                              split_development, threshold_table)
import part4.evaluation as p4


def test_reexports_match_part4():
    """Single source of truth: Part 3 must use the exact Part 4 objects."""
    assert COST_RATIOS == p4.COST_RATIOS
    for name in ["feature_target", "metrics", "select_threshold",
                 "split_development", "threshold_table"]:
        assert globals()[name] is getattr(p4, name)


def test_row_id_and_label_cannot_be_predictors(frame):
    x, y = feature_target(frame())
    assert "row_id" not in x and "default" not in x
    assert list(y) == frame()["default"].tolist()


def test_inner_split_preserves_membership_is_disjoint_and_repeatable(frame):
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




def test_baseline_hyperparameters_are_frozen():
    model = make_pipeline({}, threads=1).named_steps["model"]
    assert model.n_estimators == BASELINE["n_estimators"] == 100
    assert model.max_depth is None
    assert model.min_samples_split == 2
    assert model.min_samples_leaf == 1
    assert model.max_features == "sqrt"
    assert model.criterion == "gini"
    assert model.class_weight is None
    assert model.random_state == 42


def test_search_space_mirrors_protocol_breadth():
    assert set(SEARCH_SPACE) == {"n_estimators", "max_depth", "min_samples_split",
                                 "min_samples_leaf", "max_features", "class_weight"}
    assert None in SEARCH_SPACE["max_depth"]
    assert {0: 1, 1: 3} in SEARCH_SPACE["class_weight"]
    assert "sqrt" in SEARCH_SPACE["max_features"]


def test_pipeline_encodes_categories_without_learning_validation_values(frame):
    x, y = feature_target(frame())
    estimator = make_pipeline({"n_estimators": 3, "max_depth": 2}, threads=1)
    estimator.fit(x, y)
    before = [v.copy() for v in estimator.named_steps["preprocess"].named_transformers_["categorical"].categories_]
    unseen = x.iloc[:2].copy()
    unseen["EDUCATION"] = 99
    assert np.isfinite(estimator.predict_proba(unseen)).all()
    after = estimator.named_steps["preprocess"].named_transformers_["categorical"].categories_
    assert all(np.array_equal(a, b) for a, b in zip(before, after))


def test_best_candidate_breaks_ties_by_lowest_candidate_index():
    rows = pd.DataFrame({"Candidate": [3, 1, 2],
                         "Mean_CV_AP": [.70, .70, .69]})
    assert best_candidate(rows) == 1


def test_save_predictions_roundtrip_preserves_float32_decisions(tmp_path):
    scores = np.array([.1, .31501567, .8, .9], dtype=np.float32)
    threshold = float(scores[1])
    path = tmp_path / "predictions.csv"
    save_predictions(path, np.arange(4), [0, 1, 0, 1], scores, scores)
    restored = pd.read_csv(path, float_precision="round_trip")
    assert np.array_equal(restored.Tuned_probability.to_numpy(), scores.astype(float))
    assert metrics(restored.default, restored.Tuned_probability, threshold) == metrics([0, 1, 0, 1], scores, threshold)




def test_compute_profiles_group_counts_and_derived_features(cases_frame):
    frame = derive_features(cases_frame)
    profile = compute_profiles(frame, threshold=.5)
    groups = profile.set_index("Group")
    assert groups.loc["FN", "N"] == 2 and groups.loc["TP", "N"] == 2
    assert groups.loc["FP", "N"] == 2 and groups.loc["TN", "N"] == 2
    assert groups.loc["TP", "Mean_Utilization_1"] == 0.5
    assert groups.loc["FN", "Mean_PAY_0"] == -1.0
    assert groups.loc["TN", "Mean_Payment_share_1"] == 0.5
    assert groups.loc["FP", "Mean_Payment_share_1"] == 0.1
    assert groups.loc["FP", "Pct_PAY_0_overdue"] == 0.0


def test_case_snapshots_pick_the_extremes(cases_frame):
    frame = derive_features(cases_frame)
    snap = case_snapshots(frame, threshold=.5, k=2)
    fn = snap[snap.Group == "FN"]
    assert fn.Tuned_probability.tolist() == [.10, .20]
    fp = snap[snap.Group == "FP"]
    assert fp.Tuned_probability.tolist() == [.85, .75]
    assert {"row_id", "Group", "Tuned_probability", "Utilization_1"}.issubset(snap.columns)


def test_run_refuses_frozen_output_dir(tmp_path):
    (tmp_path / "protocol_frozen.json").write_text("{}")
    with pytest.raises(FileExistsError):
        run(output_dir=tmp_path, candidates=2, bootstrap_repeats=100)
