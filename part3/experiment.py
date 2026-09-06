"""Fit/select Random Forest on development data; freeze decisions before the final holdout.

Run from the repository root: python -m part3.experiment

Follows the group protocol frozen by Part 4 (results/xgboost/protocol_frozen.json):
dataset and development split, CV scheme, selection metric, cost ratios,
threshold selection rule and bootstrap recipe are identical so all four models
compare on equal terms.
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import ParameterSampler, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .evaluation import (COST_RATIOS, feature_target, metrics, paired_bootstrap,
                         select_threshold, split_development, threshold_table)

BASELINE = dict(n_estimators=100, max_depth=None, min_samples_split=2,
                min_samples_leaf=1, max_features="sqrt", criterion="gini",
                class_weight=None)
SEARCH_SPACE = dict(n_estimators=[150, 300, 500], max_depth=[4, 8, 12, None],
                    min_samples_split=[2, 5, 10], min_samples_leaf=[1, 2, 5],
                    max_features=["sqrt", "log2", .3, .5],
                    class_weight=[None, {0: 1, 1: 3}])
ROOT = Path(__file__).resolve().parents[1]
MODEL_NAME = "rf"


def make_pipeline(params=None, threads=2):
    preprocess = ColumnTransformer([
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         ["SEX", "EDUCATION", "MARRIAGE"])], remainder="passthrough",
        verbose_feature_names_out=False)
    parameters = BASELINE | (params or {})
    model = RandomForestClassifier(**parameters, random_state=42, n_jobs=threads)
    return Pipeline([("preprocess", preprocess), ("model", model)])


def best_candidate(results):
    """Highest mean CV AP; ties resolve to the lowest candidate index (as Part 4)."""
    return int(results.sort_values(["Mean_CV_AP", "Candidate"],
                                   ascending=[False, True]).iloc[0].Candidate)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False, default=lambda x: x.item()) + "\n")


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_predictions(path, row_ids, labels, baseline, tuned):
    """Preserve exact float32 scores in CSV; read with float_precision='round_trip'."""
    pd.DataFrame({"row_id": np.asarray(row_ids), "default": np.asarray(labels),
                  "Baseline_probability": np.asarray(baseline, dtype=float),
                  "Tuned_probability": np.asarray(tuned, dtype=float)}).to_csv(path, index=False)
