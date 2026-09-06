"""Post-hoc logistic reproducibility supplement after historic test results existed.

Run: python -m part1.experiment --output-dir results/logistic_supplement
The historic holdout is reused; this is not a new independent unseen-test claim.
All choices in this supplement use fit CV or validation only.
"""
import argparse
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
from sklearn.inspection import permutation_importance
from sklearn.model_selection import ParameterGrid, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

from part4.evaluation import COST_RATIOS, feature_target, metrics, select_threshold, split_development, threshold_table

from integration.artifacts import file_hash, save_predictions, write_json
from integration.uncertainty import paired_bootstrap

BASELINE = {"C": 1., "class_weight": None}
SEARCH_SPACE = {"C": [.001, .01, .1, 1., 10., 100.],
                "class_weight": [None, "balanced"]}
ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_STATUS = "Post-hoc reproducibility supplement after historic test results existed"


def make_pipeline(params=None):
    """Learn categories and numeric scaling only inside each training fold."""
    preprocessing = ColumnTransformer([
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         ["SEX", "EDUCATION", "MARRIAGE"])], remainder=StandardScaler(),
        verbose_feature_names_out=False)
    model = LogisticRegression(**(BASELINE | (params or {})), solver="lbfgs",
                               l1_ratio=0., max_iter=3000, random_state=42)
    return Pipeline([("preprocess", preprocessing), ("model", model)])


def run(output_dir=None, bootstrap_repeats=1000):
    if bootstrap_repeats < 100:
        raise ValueError("Use at least 100 bootstrap replicates")
    output = Path(output_dir) if output_dir else ROOT / "results/logistic_supplement"
    if (output / "protocol_frozen.json").exists():
        raise FileExistsError("This run is frozen. Use --output-dir for a separately labelled reproduction.")
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    train_path, test_path = ROOT / "data/splits/train.csv", ROOT / "data/splits/test.csv"
    train = pd.read_csv(train_path)
    if len(train) != 24000 or len(train.columns) != 25:
        raise ValueError("Expected supplied training data: 24,000 rows, row_id + 23 predictors + label")
    expected_ids = pd.read_csv(ROOT / "data/splits/train_indices.csv").row_id
    if train.row_id.tolist() != expected_ids.tolist():
        raise ValueError("Training membership/order differs from the supplied index file")
    fit, validation = split_development(train)
    x_fit, y_fit = feature_target(fit)
    x_val, y_val = feature_target(validation)
    pd.concat([fit[["row_id"]].assign(Partition="fit"),
               validation[["row_id"]].assign(Partition="validation")]).to_csv(output / "development_membership.csv", index=False)
    cv = list(StratifiedKFold(n_splits=5, shuffle=True, random_state=42).split(x_fit, y_fit))
    cv_members = []
    for fold, (_, holdout) in enumerate(cv):
        cv_members.extend({"row_id": int(v), "CV_fold": fold} for v in fit.iloc[holdout].row_id)
    pd.DataFrame(cv_members).to_csv(output / "cv_membership.csv", index=False)
    settings = [BASELINE.copy()] + [p for p in ParameterGrid(SEARCH_SPACE) if p != BASELINE]
    candidates = len(settings)
    rows = []
    print(f"Fitting rows={len(fit)}, validation rows={len(validation)}; {candidates} candidates x 5 folds", flush=True)
    for number, parameters in enumerate(settings):
        scores = cross_validate(make_pipeline(parameters), x_fit, y_fit, cv=cv,
                                scoring={"AP": "average_precision", "ROC_AUC": "roc_auc"},
                                n_jobs=1, return_train_score=True, error_score="raise")
        row = {"Candidate": number, "Parameters": json.dumps(parameters, sort_keys=True),
               "Mean_CV_AP": float(scores["test_AP"].mean()),
               "SD_CV_AP": float(scores["test_AP"].std(ddof=1)),
               "Mean_fit_AP": float(scores["train_AP"].mean()),
               "Mean_CV_ROC_AUC": float(scores["test_ROC_AUC"].mean()),
               "Mean_fit_seconds": float(scores["fit_time"].mean())}
        row.update({f"Fold_{k}_AP": float(v) for k, v in enumerate(scores["test_AP"])})
        rows.append(row)
        pd.DataFrame(rows).to_csv(output / "cv_results.csv", index=False)
        print(f"Candidate {number + 1}/{candidates}: CV AP={row['Mean_CV_AP']:.5f}", flush=True)
    best_id = int(pd.DataFrame(rows).sort_values(["Mean_CV_AP", "Candidate"], ascending=[False, True]).iloc[0].Candidate)
    baseline, tuned = make_pipeline(BASELINE), make_pipeline(settings[best_id])
    baseline.fit(x_fit, y_fit)
    tuned.fit(x_fit, y_fit)
    val_base, val_tuned = baseline.predict_proba(x_val)[:, 1], tuned.predict_proba(x_val)[:, 1]
    table = threshold_table(y_val, val_tuned)
    table.to_csv(output / "validation_thresholds.csv", index=False)
    thresholds = {str(r): select_threshold(table, r) for r in COST_RATIOS}
    save_predictions(output / "validation_predictions.csv", validation.row_id, y_val, val_base, val_tuned)
    val_metrics = [{"Model": "Baseline LR supplement", **metrics(y_val, val_base)},
                   {"Model": "Tuned LR supplement", **metrics(y_val, val_tuned)}]
    val_metrics += [{"Model": f"Tuned LR supplement / cost ratio {r}", **metrics(y_val, val_tuned, thresholds[str(r)])} for r in COST_RATIOS]
    pd.DataFrame(val_metrics).to_csv(output / "validation_metrics.csv", index=False)
    importance = permutation_importance(tuned, x_val, y_val, scoring="average_precision",
                                        n_repeats=5, random_state=42, n_jobs=1)
    pd.DataFrame({"Feature": x_val.columns, "Mean_AP_decrease": importance.importances_mean,
                  "SD_AP_decrease": importance.importances_std}).sort_values("Mean_AP_decrease", ascending=False).to_csv(output / "validation_importance.csv", index=False)
    pd.DataFrame({"Feature": tuned.named_steps["preprocess"].get_feature_names_out(),
                  "Coefficient": tuned.named_steps["model"].coef_[0]}).to_csv(
                      output / "coefficients.csv", index=False)
    write_json(output / "intercept.json", {"Intercept": tuned.named_steps["model"].intercept_[0],
               "Note": "Numeric coefficients use fit-standardized predictors; category coefficients use full one-hot coding and L2 regularization."})
    joblib.dump(baseline, output / "baseline_pipeline.joblib", compress=3)
    joblib.dump(tuned, output / "tuned_pipeline.joblib", compress=3)
    versions = {name: importlib.metadata.version(name) for name in
                ["numpy", "pandas", "scikit-learn", "matplotlib", "scipy", "joblib"]}
    protocol = {"Stage": "Supplement choices frozen before this runner loads historic test rows",
                "Evidence_status": EVIDENCE_STATUS, "Estimator": "LogisticRegression",
                "Independent_unseen_test_claim": False,
                "Source_script_SHA256": file_hash(Path(__file__)),
                "Preprocessing": "Fold-trained full one-hot SEX/EDUCATION/MARRIAGE; StandardScaler for remaining numeric predictors",
                "Fixed_estimator_parameters": {"solver": "lbfgs", "l1_ratio": 0., "max_iter": 3000, "random_state": 42}, "Frozen_at_UTC": datetime.now(timezone.utc).isoformat(),
                "Source_train_SHA256": file_hash(train_path), "Features": x_fit.columns.tolist(),
                "Fit_rows": len(fit), "Validation_rows": len(validation), "Seed": 42,
                "CV_folds": 5, "Candidates": candidates, "Selection_metric": "average_precision",
                "Baseline_parameters": BASELINE, "Selected_parameters": settings[best_id],
                "Selected_candidate": best_id, "Search_space": SEARCH_SPACE,
                "Validation_thresholds": thresholds, "Primary_cost_ratio": 5,
                "Cost_definition": "FP + ratio * FN; hypothetical equal unit cost per false positive",
                "Threshold_tie_rule": "largest threshold", "Prediction_rule": "score >= threshold",
                "Refit_after_threshold_selection": False, "Bootstrap_replicates": bootstrap_repeats,
                "Bootstrap_seed": 20260905, "Python": platform.python_version(), "Packages": versions,
                "Model_SHA256": {name: file_hash(output / name) for name in ["baseline_pipeline.joblib", "tuned_pipeline.joblib"]}}
    write_json(output / "protocol_frozen.json", protocol)
    print("Supplement choices frozen; evaluating the previously used historical test split.", flush=True)

    # First test-row read by this supplement only. Historic test results already existed.
    test = pd.read_csv(test_path)
    if len(test) != 6000 or test.columns.tolist() != train.columns.tolist():
        raise ValueError("Unexpected test size/schema")
    if not set(test.row_id).isdisjoint(train.row_id):
        raise ValueError("Training/test row IDs overlap")
    if test.row_id.tolist() != pd.read_csv(ROOT / "data/splits/test_indices.csv").row_id.tolist():
        raise ValueError("Test membership/order differs from supplied index file")
    x_test, y_test = feature_target(test)
    base_p, tuned_p = baseline.predict_proba(x_test)[:, 1], tuned.predict_proba(x_test)[:, 1]
    save_predictions(output / "test_predictions.csv", test.row_id, y_test, base_p, tuned_p)
    comparison = [{"Model": "Baseline LR supplement", **metrics(y_test, base_p)},
                  {"Model": "Tuned LR supplement", **metrics(y_test, tuned_p)}]
    comparison += [{"Model": f"Tuned LR supplement / cost ratio {r}", **metrics(y_test, tuned_p, thresholds[str(r)])} for r in COST_RATIOS]
    constant = np.full(len(test), y_fit.mean())
    comparison += [{"Model": "Always negative", **metrics(y_test, constant, 1.)},
                   {"Model": "Always positive", **metrics(y_test, constant, 0.)}]
    results = pd.DataFrame(comparison)
    results.to_csv(output / "test_metrics.csv", index=False)
    intervals = paired_bootstrap(y_test, base_p, tuned_p, thresholds["5"], bootstrap_repeats)
    intervals.to_csv(output / "bootstrap_intervals.csv", index=False)
    train_hash = pd.util.hash_pandas_object(train[x_fit.columns], index=False)
    test_hash = pd.util.hash_pandas_object(x_test, index=False)
    audit = {"Training_rows": len(train), "Test_rows": len(test), "Row_ID_overlap": 0,
             "Training_duplicate_feature_rows": int(train_hash.duplicated().sum()),
             "Test_rows_with_features_seen_in_development": int(test_hash.isin(set(train_hash)).sum()),
             "Source_test_SHA256": file_hash(test_path),
             "Note": "Identical feature vectors are retained per group protocol; they do not establish duplicate customers."}
    write_json(output / "data_audit.json", audit)
    write_json(output / "run_metadata.json", {"Status": "Complete", "Completed_at_UTC": datetime.now(timezone.utc).isoformat(),
                                             "Elapsed_seconds": time.perf_counter() - started,
                                             "Frozen_protocol_SHA256": file_hash(output / "protocol_frozen.json"),
                                             "Test_predictions_SHA256": file_hash(output / "test_predictions.csv")})
    print(results[["Model", "AP", "ROC-AUC", "Recall", "Precision", "Cost_5"]].to_string(index=False), flush=True)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--bootstrap-repeats", type=int, default=1000)
    args = parser.parse_args()
    run(args.output_dir, args.bootstrap_repeats)
