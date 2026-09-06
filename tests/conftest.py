import numpy as np
import pandas as pd
import pytest

from integration.artifacts import save_predictions
from integration.uncertainty import paired_bootstrap
from part1.experiment import make_pipeline as make_lr
from part3.experiment import make_pipeline as make_rf
from part3.misclassification import case_snapshots, compute_profiles, derive_features
from part4.evaluation import feature_target, metrics, split_development, threshold_table
from part4.experiment import make_pipeline as make_xgb


@pytest.fixture
def frame():
    def factory(n=80):
        return pd.DataFrame(
            {
                "row_id": np.arange(n),
                "SEX": [1, 2] * (n // 2),
                "EDUCATION": [1, 2, 3, 4] * (n // 4),
                "MARRIAGE": [1, 2] * (n // 2),
                "LIMIT_BAL": np.arange(n) * 1000,
                "default": [0, 0, 0, 1] * (n // 4),
            }
        )

    return factory


@pytest.fixture
def cases_frame():
    return pd.DataFrame(
        {
            "row_id": np.arange(8),
            "default": [1, 1, 1, 1, 0, 0, 0, 0],
            "Tuned_probability": [0.10, 0.20, 0.80, 0.90, 0.10, 0.25, 0.75, 0.85],
            "PAY_0": [-1, -1, 2, 2, -1, -1, 0, 0],
            "PAY_2": [-1, -1, 2, 2, -1, -1, 0, 0],
            "PAY_6": [-1, -1, 2, 2, -1, -1, 0, 0],
            "LIMIT_BAL": [10000] * 8,
            "BILL_AMT1": [500, 5000, 5000, 5000, 500, 5000, 5000, 5000],
            "PAY_AMT1": [500, 0, 500, 500, 500, 0, 500, 500],
            "BILL_AMT6": [500] * 8,
            "PAY_AMT6": [500] * 8,
            "AGE": [30] * 8,
            "SEX": [1, 2] * 4,
            "EDUCATION": [1, 2] * 4,
            "MARRIAGE": [1, 2] * 4,
        }
    )


@pytest.fixture
def score_sample():
    return np.array([0, 1, 0, 1]), np.array([.1, .2, .8, .9])


@pytest.fixture
def split_results(frame):
    original = frame()
    return original, split_development(original), split_development(original)


@pytest.fixture
def hand_metrics(score_sample):
    return metrics(*score_sample)


@pytest.fixture
def tied_thresholds():
    return threshold_table([0, 1, 0, 1], [.2, .2, .8, .8])


@pytest.fixture
def identical_bootstrap(score_sample):
    labels, scores = score_sample
    return paired_bootstrap(labels, scores, scores, .5, repeats=100).set_index("Quantity")


@pytest.fixture
def roundtrip_predictions(tmp_path, score_sample):
    labels, _ = score_sample
    scores = np.array([.1, .31501567, .8, .9], dtype=np.float32)
    path = tmp_path / "predictions.csv"
    save_predictions(path, np.arange(4), labels, scores, scores)
    return labels, scores, pd.read_csv(path, float_precision="round_trip")


@pytest.fixture(params=["lr_category", "lr_numeric", "rf", "xgboost"])
def preprocessing_probe(request, frame):
    factories = {"lr_category": make_lr, "lr_numeric": make_lr,
                 "rf": lambda: make_rf({"n_estimators": 3, "max_depth": 2}, threads=1),
                 "xgboost": lambda: make_xgb({"n_estimators": 3, "max_depth": 2}, threads=1)}
    x, y = feature_target(frame())
    model = factories[request.param]().fit(x, y)
    prep = model.named_steps["preprocess"]
    before = [v.copy() for v in prep.named_transformers_["categorical"].categories_]
    scaler = prep.named_transformers_["remainder"]
    means = scaler.mean_.copy() if hasattr(scaler, "mean_") else None
    unseen = x.iloc[:2].copy()
    unseen["LIMIT_BAL" if request.param == "lr_numeric" else "EDUCATION"] = (
        1e12 if request.param == "lr_numeric" else 99)
    probabilities = model.predict_proba(unseen)
    after = prep.named_transformers_["categorical"].categories_
    return {"finite_scores": np.isfinite(probabilities).all(),
            "fit_state_unchanged": all(np.array_equal(a, b) for a, b in zip(before, after, strict=True))
            and (means is None or np.array_equal(means, scaler.mean_))}


@pytest.fixture
def case_profiles(cases_frame):
    return compute_profiles(derive_features(cases_frame), threshold=.5).set_index("Group")


@pytest.fixture
def case_examples(cases_frame):
    return case_snapshots(derive_features(cases_frame), threshold=.5, k=2)


@pytest.fixture
def frozen_output(tmp_path):
    (tmp_path / "protocol_frozen.json").write_text("frozen")
    return tmp_path
