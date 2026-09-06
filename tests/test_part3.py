import pandas as pd
import pytest

from part3.experiment import best_candidate, make_pipeline
from part3.misclassification import case_snapshots, derive_features


@pytest.mark.parametrize("parameter,expected", [
    ("n_estimators", 100), ("max_depth", None), ("min_samples_split", 2),
    ("min_samples_leaf", 1), ("max_features", "sqrt"), ("criterion", "gini"),
    ("class_weight", None), ("random_state", 42),
])
def test_baseline_hyperparameters_are_frozen(parameter, expected):
    assert make_pipeline({}, threads=1).named_steps["model"].get_params()[parameter] == expected


def test_best_candidate_breaks_ties_by_lowest_candidate_index():
    rows = pd.DataFrame({"Candidate": [3, 1, 2], "Mean_CV_AP": [.70, .70, .69]})
    assert best_candidate(rows) == 1


@pytest.mark.parametrize("group,column,expected", [
    ("FN", "N", 2), ("TP", "N", 2), ("FP", "N", 2), ("TN", "N", 2),
    ("TP", "Mean_Utilization_1", .5), ("FN", "Mean_PAY_0", -1.),
    ("TN", "Mean_Payment_share_1", .5), ("FP", "Mean_Payment_share_1", .1),
    ("FP", "Pct_PAY_0_overdue", 0.),
])
def test_compute_profiles_group_counts_and_derived_features(case_profiles, group, column, expected):
    assert case_profiles.loc[group, column] == expected


@pytest.mark.parametrize("group,expected", [("FN", [.10, .20]), ("FP", [.85, .75])])
def test_case_snapshots_pick_the_extremes(case_examples, group, expected):
    assert case_examples.loc[case_examples.Group == group, "Tuned_probability"].tolist() == expected


@pytest.mark.parametrize("threshold,expected", [(.5, [0, 1, 7, 6]), (.2, [0, 7, 6])])
def test_cases_follow_each_threshold_including_equality(cases_frame, threshold, expected):
    snapshots = case_snapshots(derive_features(cases_frame), threshold, k=2)
    assert snapshots.row_id.tolist() == expected
