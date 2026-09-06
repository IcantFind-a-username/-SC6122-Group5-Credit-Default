"""Audit historical frozen artifacts without fitting or changing their files.

Run only after this measurement script is committed: python -m integration.audit.
"""
from dataclasses import asdict, dataclass
from io import BytesIO
import json
from pathlib import Path
import platform
import subprocess
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split

from integration.artifacts import bytes_hash, file_hash, write_json
from part3.misclassification import case_snapshots, compute_profiles, derive_features
from part4.evaluation import COST_RATIOS, feature_target, metrics, select_threshold, split_development, threshold_table

ROOT = Path(__file__).resolve().parents[1]
MODELS = {"decision_tree": "Decision Tree", "rf": "RF", "xgboost": "XGBoost"}


@dataclass
class Check:
    name: str
    passed: bool
    detail: object


def read_csv(path):
    """One explicit parser policy for every numerical artifact audited here."""
    return pd.read_csv(path, float_precision="round_trip")


def frame_check(left, right):
    """Expose values, schema, dtype and order differences without stopping audit."""
    try:
        pd.testing.assert_frame_equal(left.reset_index(drop=True), right.reset_index(drop=True), check_exact=True)
        return True, "Exact values, column order, row order and dtypes"
    except AssertionError as exc:
        return False, str(exc)[:1200]


def hash_evidence(path, expected):
    """Check bytes/newlines and every historical data blob against frozen hashes."""
    raw = path.read_bytes()
    normalized = raw.replace(b"\r\n", b"\n")
    variants = {"current": raw, "LF": normalized, "CRLF": normalized.replace(b"\n", b"\r\n")}
    relative = path.relative_to(ROOT).as_posix()
    commits = subprocess.check_output(["git", "log", "--all", "--format=%H", "--", relative], cwd=ROOT, text=True).splitlines()
    history = []
    for commit in commits:
        blob = subprocess.run(["git", "show", f"{commit}:{relative}"], cwd=ROOT, capture_output=True, check=False)
        if blob.returncode:
            continue
        same, detail = frame_check(read_csv(BytesIO(raw)), read_csv(BytesIO(blob.stdout)))
        history.append({"commit": commit, "sha256": bytes_hash(blob.stdout), "parsed_exact": same, "comparison": detail})
        variants[f"git:{commit}"] = blob.stdout
    hashes = {name: bytes_hash(value) for name, value in variants.items()}
    return {"current_sha256": file_hash(path), "variants": hashes, "historical_blobs": history,
            "expected_matches": {value: [name for name, digest in hashes.items() if digest == value] for value in expected},
            "newline_variants_parse_identically": all(frame_check(read_csv(BytesIO(raw)), read_csv(BytesIO(value)))[0] for value in variants.values())}


def run():
    output = ROOT / "results/final"
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    details = {}
    comparisons = []
    costs = []

    def check(name, passed, detail=""):
        checks.append(Check(name, bool(passed), detail))

    def compare(name, left, right):
        passed, detail = frame_check(left, right)
        check(name, passed, detail)

    protocols = {name: json.loads((ROOT / "results" / name / "protocol_frozen.json").read_text()) for name in MODELS}
    audits = {name: json.loads((ROOT / "results" / name / "data_audit.json").read_text()) for name in MODELS}
    train = read_csv(ROOT / "data/splits/train.csv")
    test = read_csv(ROOT / "data/splits/test.csv")
    clean = read_csv(ROOT / "data/credit_card_default_clean.csv")
    for partition, expected in [("train", [p["Source_train_SHA256"] for p in protocols.values()]),
                                ("test", [p["Source_test_SHA256"] for p in audits.values()])]:
        evidence = hash_evidence(ROOT / f"data/splits/{partition}.csv", set(expected))
        details[f"{partition}_hash_evidence"] = evidence
        check(f"{partition}: every historical hash explained", all(evidence["expected_matches"].values()), evidence["expected_matches"])
        check(f"{partition}: historical parsed identity", evidence["newline_variants_parse_identically"])
    check("source: row_id uniqueness and complete coverage", clean.row_id.is_unique and sorted(clean.row_id) == list(range(30000)))
    check("source: no missing values", not clean.isna().any().any())
    check("source: disjoint train/test", set(train.row_id).isdisjoint(test.row_id))
    check("source: train/test cover clean", set(train.row_id) | set(test.row_id) == set(clean.row_id))
    expected_train, expected_test = train_test_split(clean, test_size=.2, random_state=42, stratify=clean.default)
    for partition, frame, expected in [("train", train, expected_train), ("test", test, expected_test)]:
        compare(f"{partition}: original stratified split/order/values", frame, expected)
        compare(f"{partition}: supplied index membership/order", frame[["row_id"]], read_csv(ROOT / f"data/splits/{partition}_indices.csv"))
        compare(f"{partition}: source row_id joined feature/label identity", frame, clean.set_index("row_id").loc[frame.row_id].reset_index())
    fit, validation = split_development(train)
    x_fit, y_fit = feature_target(fit)
    features = x_fit.columns.tolist()
    train_hash = pd.util.hash_pandas_object(train[features], index=False)
    test_hash = pd.util.hash_pandas_object(test[features], index=False)
    details["source"] = {"clean_rows": len(clean), "fit_rows": len(fit), "validation_rows": len(validation), "test_rows": len(test),
                         "fit_defaults": int(fit.default.sum()), "validation_defaults": int(validation.default.sum()), "test_defaults": int(test.default.sum()),
                         "clean_duplicate_features_excluding_first": int(clean[features].duplicated().sum()),
                         "train_duplicate_features_excluding_first": int(train_hash.duplicated().sum()),
                         "test_rows_features_seen_in_development": int(test_hash.isin(set(train_hash)).sum()),
                         "cleaning": "02_preprocessing.ipynb documents EDUCATION {0,5,6}->4, MARRIAGE 0->3; no rows removed/imputation; negative repayment codes and large/negative amounts retained. Original pre-cleaning raw dataset is not committed, so its transformation cannot be independently replayed.",
                         "duplicate_interpretation": "Equal feature vectors retained; do not establish duplicate customers."}
    membership = pd.concat([fit[["row_id"]].assign(Partition="fit"), validation[["row_id"]].assign(Partition="validation")], ignore_index=True)
    cv = list(StratifiedKFold(n_splits=5, shuffle=True, random_state=42).split(x_fit, y_fit))
    cv_membership = pd.DataFrame([{"row_id": int(row), "CV_fold": fold} for fold, (_, indices) in enumerate(cv) for row in fit.iloc[indices].row_id])
    details["cv_folds"] = [{"fold": k, "fit_n": len(a), "heldout_n": len(b), "heldout_defaults": int(y_fit.iloc[b].sum()),
                            "disjoint": set(a).isdisjoint(b)} for k, (a, b) in enumerate(cv)]
    for family, label in MODELS.items():
        print(f"Auditing {label}: membership, serialized models, probabilities, metrics and selection", flush=True)
        folder = ROOT / "results" / family
        protocol = protocols[family]
        compare(f"{family}: development membership and row order", read_csv(folder / "development_membership.csv"), membership)
        compare(f"{family}: all CV memberships and row order", read_csv(folder / "cv_membership.csv"), cv_membership)
        check(f"{family}: declared feature list", protocol["Features"] == features)
        metadata = json.loads((folder / "run_metadata.json").read_text())
        for key, filename in [("Frozen_protocol_SHA256", "protocol_frozen.json"), ("Test_predictions_SHA256", "test_predictions.csv")]:
            check(f"{family}: {key}", metadata[key] == file_hash(folder / filename), {"expected": metadata[key], "actual": file_hash(folder / filename)})
        cv_results = read_csv(folder / "cv_results.csv")
        winner = cv_results.sort_values(["Mean_CV_AP", "Candidate"], ascending=[False, True]).iloc[0]
        check(f"{family}: CV winner", int(winner.Candidate) == protocol["Selected_candidate"])
        check(f"{family}: CV winner parameters", json.loads(winner.Parameters) == protocol["Selected_parameters"])
        folds = cv_results[[f"Fold_{k}_AP" for k in range(5)]]
        check(f"{family}: fold AP aggregation", np.allclose(folds.mean(axis=1), cv_results.Mean_CV_AP, rtol=0, atol=1e-15) and np.allclose(folds.std(axis=1, ddof=1), cv_results.SD_CV_AP, rtol=0, atol=1e-15))
        details[family] = {"selected_candidate": int(winner.Candidate), "cv_ap": float(winner.Mean_CV_AP), "cv_ap_sd": float(winner.SD_CV_AP), "models": {}, "thresholds": {}}
        pipelines = {}
        for variant in ["baseline", "tuned"]:
            filename = f"{variant}_pipeline.joblib"
            check(f"{family}/{variant}: model SHA256", file_hash(folder / filename) == protocol["Model_SHA256"][filename])
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                pipeline = joblib.load(folder / filename)
            pipelines[variant] = pipeline
            prep, model = pipeline.named_steps["preprocess"], pipeline.named_steps["model"]
            parameters = protocol["Baseline_parameters" if variant == "baseline" else "Selected_parameters"]
            actual = model.get_params()
            check(f"{family}/{variant}: fitted estimator parameters", all(json.dumps(actual[k], sort_keys=True) == json.dumps(v, sort_keys=True) for k, v in parameters.items()))
            categories = prep.named_transformers_["categorical"].categories_
            expected_categories = [np.sort(fit[c].unique()) for c in ["SEX", "EDUCATION", "MARRIAGE"]]
            check(f"{family}/{variant}: one-hot categories from fit", all(np.array_equal(a, b) for a, b in zip(categories, expected_categories, strict=True)))
            transformed = prep.get_feature_names_out().tolist()
            check(f"{family}/{variant}: ID/outcome excluded from preprocessing", list(prep.feature_names_in_) == features and "row_id" not in transformed and "default" not in transformed)
            if family == "decision_tree":
                fit_n = int(model.tree_.n_node_samples[0])
                fit_evidence = "Serialized tree root n_node_samples"
            elif family == "rf":
                fit_n = int(model._n_samples)
                fit_evidence = "Serialized RandomForest _n_samples (bootstrap root distinct counts are not fit n)"
            else:
                fit_n = None
                fit_evidence = "XGBoost serialization does not record training row count; 18000 is supported by source and memberships, not independently recoverable from booster."
            if fit_n is not None:
                check(f"{family}/{variant}: serialized fit n", fit_n == len(fit), fit_n)
            details[family]["models"][variant] = {"fit_n": fit_n, "fit_n_evidence": fit_evidence,
                "preprocess_features": transformed, "encoder_handle_unknown": prep.named_transformers_["categorical"].handle_unknown,
                "load_warnings": [str(w.message) for w in caught]}
        for partition, frame in [("validation", validation), ("test", test)]:
            saved = read_csv(folder / f"{partition}_predictions.csv")
            compare(f"{family}/{partition}: row_id and labels including order", saved[["row_id", "default"]], frame[["row_id", "default"]])
            check(f"{family}/{partition}: unique prediction row_ids", saved.row_id.is_unique)
            joined = frame.merge(saved, on="row_id", how="left", validate="one_to_one", suffixes=("", "_saved"))
            check(f"{family}/{partition}: label join", np.array_equal(joined.default, joined.default_saved))
            x, y = feature_target(frame)
            for variant in ["baseline", "tuned"]:
                p = pipelines[variant].predict_proba(x)[:, 1].astype(float)
                recorded = joined[f"{variant.title()}_probability"].to_numpy()
                error = float(np.max(np.abs(p - recorded)))
                check(f"{family}/{partition}/{variant}: replay probabilities", np.allclose(p, recorded, rtol=0, atol=1e-14), {"max_abs_error": error, "bit_exact": bool(np.array_equal(p, recorded))})
                cutoffs = [.5] + list(protocol.get("Validation_thresholds", {}).values())
                check(f"{family}/{partition}/{variant}: replay frozen decisions", all(np.array_equal(p >= t, recorded >= t) for t in cutoffs))
                details[family]["models"][variant][f"{partition}_ties_at_0.5"] = int((recorded == .5).sum())
            historical = read_csv(folder / f"{partition}_metrics.csv")
            for _, row in historical.iterrows():
                column = "Baseline_probability" if row.Model.startswith("Baseline") else "Tuned_probability"
                probability = joined[column].to_numpy()
                if row.Model.startswith("Always"):
                    probability = np.full(len(y), y_fit.mean())
                recomputed = metrics(y, probability, row.Threshold)
                differences = {k: {"saved": float(row[k]), "recomputed": float(v)} for k, v in recomputed.items() if not np.isclose(row[k], v, rtol=0, atol=1e-12)}
                check(f"{family}/{partition}: metrics {row.Model}", not differences, differences)
                comparisons.append({"Family": label, "Partition": partition, "Model": row.Model,
                                    "Policy_origin": "Historical frozen validation selection" if "cost ratio" in row.Model else "Historical fixed policy", **recomputed})
            if partition == "validation" and "Validation_thresholds" in protocol:
                table = threshold_table(y, joined.Tuned_probability)
                compare(f"{family}: full validation threshold table", read_csv(folder / "validation_thresholds.csv"), table)
                for ratio in COST_RATIOS:
                    chosen = select_threshold(table, ratio)
                    frozen = protocol["Validation_thresholds"][str(ratio)]
                    check(f"{family}: validation threshold r={ratio}", chosen == frozen, {"reselected": chosen, "frozen": frozen})
                    tied = table[table[f"Cost_{ratio}"] == table[f"Cost_{ratio}"].min()]
                    details[family]["thresholds"][str(ratio)] = {"frozen": frozen, "reselected": chosen, "equal_minimum_cost_candidates": len(tied), "validation_scores_at_threshold": int((joined.Tuned_probability == frozen).sum())}
            if partition == "test":
                for _, row in historical.iterrows():
                    for ratio in COST_RATIOS:
                        costs.append({"Family": label, "Model": row.Model, "Threshold": row.Threshold, "Cost_ratio": ratio,
                                      "FP": int(row.FP), "FN": int(row.FN), "Cost": int(row.FP + ratio * row.FN),
                                      "Cost_per_1000": (row.FP + ratio * row.FN) / len(y) * 1000})
                if family == "rf":
                    derived = derive_features(joined.drop(columns="default_saved"))
                    threshold = protocol["Validation_thresholds"]["5"]
                    profiles = pd.concat([compute_profiles(derived, .5), compute_profiles(derived, threshold)], ignore_index=True)
                    original_profiles = read_csv(folder / "misclassification_profiles.csv")
                    compare("rf: historical misclassification group counts", original_profiles[["Threshold", "Group", "N"]], profiles[["Threshold", "Group", "N"]])
                    for suffix, cutoff in [("05", .5), ("r5", threshold)]:
                        expected = case_snapshots(derived, cutoff).reset_index(drop=True)
                        old = read_csv(folder / f"misclassification_cases_{suffix}.csv")
                        compare(f"rf: historical {suffix} case identities/groups", old[["row_id", "Group"]], expected[["row_id", "Group"]])
                        expected.to_csv(output / f"audit_rf_cases_{suffix}.csv", index=False)
                    profiles.to_csv(output / "audit_rf_profiles.csv", index=False)
    pd.DataFrame(comparisons).to_csv(output / "model_comparison.csv", index=False)
    pd.DataFrame(costs).to_csv(output / "cost_comparison.csv", index=False)
    failed = [asdict(c) for c in checks if not c.passed]
    result = {"scope": "Retrospective audit only; no fitting, threshold changes or alteration of frozen artifacts. Recorded CV scores reconciled but CV fitting not replayed.",
              "python": platform.python_version(), "script_sha256": file_hash(Path(__file__)),
              "checks": [asdict(c) for c in checks], "passed": len(checks) - len(failed), "failed": len(failed), "details": details}
    write_json(output / "audit.json", result)
    findings = ["# Frozen-artifact audit", "", f"{result['passed']} checks passed; {result['failed']} discrepancies require interpretation or correction.", "",
                "Executed from committed integration/audit.py in the unified environment. No model was trained and no historical artifact was overwritten.", "",
                "## Dataset identity", "", "Byte hashes, LF/CRLF variants and every available historical data blob are recorded in results/final/audit.json. Parsed comparisons include exact values, dtypes and row/column order.",
                "", details["source"]["cleaning"], "", details["source"]["duplicate_interpretation"],
                "", "## Reconciliation", ""]
    for failure in failed:
        findings.append(f"- **{failure['name']}**: {failure['detail']}")
    if not failed:
        findings.append("All audited identities, memberships, models, probabilities, metrics and recorded selections reconcile.")
    findings.extend(["", "## Interpretation and limits", "",
        "- Frozen timestamps are historical self-reports. This audit cannot prove the test set was never viewed before freezing.",
        "- DT/RF serialized training-row counts are checked. XGBoost training row count is not serialized; source code and exact fit membership support 18000, without an independent booster count.",
        "- CV memberships, fold-score arithmetic and recorded winner selection are checked; no CV model is refitted.",
        "- All prediction CSVs are read with float_precision='round_trip'. The >= rule includes exact ties; default pandas parsing can shift a threshold-boundary score.",
        "- results/final/model_comparison.csv contains the historical baseline/tuned 0.5 and historically frozen validation-selected policies; DT has no historical cost-selected policy and none is invented.",
        "- results/final/audit_rf_* are regenerated descriptive RF reference tables. If historical cases/groups differ, replace descriptive RF tables from these files and refresh dependent figures/prose; preserve the frozen models/protocols/predictions.", ""])
    (ROOT / "integration/AUDIT_FINDINGS.md").write_text("\n".join(findings), encoding="utf-8")
    print(f"Audit: {result['passed']} passed, {result['failed']} discrepancies; {output / 'audit.json'}", flush=True)
    return output


if __name__ == "__main__":
    run()
