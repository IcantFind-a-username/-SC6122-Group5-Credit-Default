import numpy as np
import pytest

from part1.experiment import run as run_lr
from part2.experiment import run as run_tree
from part3.experiment import run as run_rf
from part4.evaluation import feature_target, metrics, select_threshold, threshold_table
from part4.experiment import run as run_xgb


@pytest.mark.parametrize("quantity", ["features", "labels"])
def test_row_id_and_label_cannot_be_predictors(frame, quantity):
    original = frame()
    x, y = feature_target(original)
    expected = {"features": original.columns.drop(["row_id", "default"]).tolist(),
                "labels": original.default.tolist()}
    observed = {"features": x.columns.tolist(), "labels": y.tolist()}
    assert observed[quantity] == expected[quantity]


@pytest.mark.parametrize("quantity,expected", [
    ("sizes", (60, 20)), ("disjoint", True), ("complete", True),
    ("repeatable", True), ("prevalence", (.25, .25)),
])
def test_inner_split_preserves_membership_and_stratification(split_results, quantity, expected):
    original, (fit, validation), (again_fit, again_validation) = split_results
    observed = {"sizes": (len(fit), len(validation)),
                "disjoint": set(fit.row_id).isdisjoint(validation.row_id),
                "complete": set(fit.row_id) | set(validation.row_id) == set(original.row_id),
                "repeatable": fit.equals(again_fit) and validation.equals(again_validation),
                "prevalence": (fit.default.mean(), validation.default.mean())}
    assert observed[quantity] == expected


@pytest.mark.parametrize("quantity,expected", [
    ("TN", 1), ("FP", 1), ("FN", 1), ("TP", 1), ("Accuracy", .5),
    ("Recall", .5), ("Precision", .5), ("Cost_5", 6), ("ROC-AUC", .75), ("AP", 5 / 6),
])
def test_metrics_match_hand_calculation(hand_metrics, quantity, expected):
    assert hand_metrics[quantity] == pytest.approx(expected)


@pytest.mark.parametrize("position,counts", [(0, [2, 0, 2, 0]), (1, [1, 1, 1, 1]), (2, [0, 2, 0, 2])])
def test_threshold_table_moves_tied_scores_as_one_group(tied_thresholds, position, counts):
    assert tied_thresholds.loc[position, ["TN", "FP", "FN", "TP"]].tolist() == counts


@pytest.mark.parametrize("scores,ratio,expected", [
    ([.1, .2, .8, .9], 5, .2), ([.2, .2, .8, .8], 5, .2),
    ([.5, .5, .5, .5], 1, np.nextafter(1., 2.)),
])
def test_validation_cost_selection_and_largest_threshold_tie(score_sample, scores, ratio, expected):
    labels, _ = score_sample
    assert select_threshold(threshold_table(labels, scores), ratio) == expected


@pytest.mark.parametrize("scores", [[.1, float("nan")], [-.1, .2], [.1, 1.1]])
def test_invalid_scores_fail_instead_of_producing_plausible_metrics(scores):
    with pytest.raises(ValueError):
        metrics([0, 1], scores, .5)


@pytest.mark.parametrize("invariant", ["finite_scores", "fit_state_unchanged"])
def test_preprocessing_does_not_learn_prediction_values(preprocessing_probe, invariant):
    assert preprocessing_probe[invariant]


@pytest.mark.parametrize("metric", ["AP", "ROC-AUC"])
@pytest.mark.parametrize("quantity", ["Estimate", "CI_low", "CI_high"])
def test_identical_models_have_zero_paired_bootstrap_differences(identical_bootstrap, metric, quantity):
    assert identical_bootstrap.loc[f"{metric} difference: tuned - baseline", quantity] == 0


@pytest.mark.parametrize("quantity", ["scores", "metrics"])
def test_csv_roundtrip_preserves_decisions_at_float32_threshold(roundtrip_predictions, quantity):
    labels, scores, restored = roundtrip_predictions
    threshold = float(scores[1])
    observed = {"scores": restored.Tuned_probability.tolist(),
                "metrics": metrics(restored.default, restored.Tuned_probability, threshold)}
    expected = {"scores": scores.astype(float).tolist(), "metrics": metrics(labels, scores, threshold)}
    assert observed[quantity] == expected[quantity]


@pytest.mark.parametrize("runner,kwargs", [
    (run_lr, {}), (run_tree, {}),
    (run_rf, {"candidates": 2, "bootstrap_repeats": 100}),
    (run_xgb, {"candidates": 2, "bootstrap_repeats": 100}),
])
def test_frozen_experiments_cannot_be_overwritten(frozen_output, runner, kwargs):
    with pytest.raises(FileExistsError):
        runner(output_dir=frozen_output, **kwargs)
    assert (frozen_output / "protocol_frozen.json").read_text() == "frozen"
