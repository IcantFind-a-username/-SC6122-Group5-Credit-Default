"""Descriptive misclassification analysis from frozen test predictions (no retraining).

Run from the repository root: python -m part3.misclassification
Reads results/rf/test_predictions.csv and data/splits/test.csv, profiles the
false-negative / false-positive groups at both decision thresholds (0.500 and
the validation-selected primary ratio-5 threshold), and exports representative
cases. Everything here is descriptive: threshold selection happened on the
validation split before the test set was first read.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .experiment import ROOT

PROFILE_COLUMNS = ["Mean_probability", "Mean_PAY_0", "Mean_PAY_2", "Mean_PAY_6",
                   "Mean_LIMIT_BAL", "Mean_BILL_AMT1", "Mean_PAY_AMT1",
                   "Mean_Utilization_1", "Mean_Payment_share_1", "Mean_AGE",
                   "Pct_PAY_0_overdue", "Pct_PAY_2_overdue"]
CASE_COLUMNS = ["row_id", "Group", "default", "Tuned_probability", "PAY_0", "PAY_2",
                "PAY_6", "LIMIT_BAL", "BILL_AMT1", "PAY_AMT1", "BILL_AMT6",
                "PAY_AMT6", "Utilization_1", "Payment_share_1", "AGE", "SEX",
                "EDUCATION", "MARRIAGE"]


def derive_features(frame):
    """Add interpretable ratios; division-by-zero becomes NaN (mean skips NaN)."""
    out = frame.copy()
    out["Utilization_1"] = out["BILL_AMT1"] / out["LIMIT_BAL"].replace(0, np.nan)
    share = out["PAY_AMT1"] / out["BILL_AMT1"].replace(0, np.nan)
    out["Payment_share_1"] = share.replace([np.inf, -np.inf], np.nan)
    return out


def compute_profiles(frame, threshold):
    """Group-mean profile of FN/FP/TP/TN at one decision threshold."""
    out = frame.copy()
    out["Predicted"] = (out["Tuned_probability"] >= threshold).astype(int)
    out["Group"] = np.select([(out.default == 1) & (out.Predicted == 0),
                              (out.default == 0) & (out.Predicted == 1),
                              (out.default == 1) & (out.Predicted == 1)],
                             ["FN", "FP", "TP"], default="TN")
    rows = []
    for group in ["FN", "FP", "TP", "TN"]:
        g = out[out.Group == group]
        rows.append({"Threshold": float(threshold), "Group": group, "N": len(g),
                     "Mean_probability": g.Tuned_probability.mean(),
                     "Mean_PAY_0": g.PAY_0.mean(), "Mean_PAY_2": g.PAY_2.mean(),
                     "Mean_PAY_6": g.PAY_6.mean(), "Mean_LIMIT_BAL": g.LIMIT_BAL.mean(),
                     "Mean_BILL_AMT1": g.BILL_AMT1.mean(), "Mean_PAY_AMT1": g.PAY_AMT1.mean(),
                     "Mean_Utilization_1": g.Utilization_1.mean(),
                     "Mean_Payment_share_1": g.Payment_share_1.mean(),
                     "Mean_AGE": g.AGE.mean(),
                     "Pct_PAY_0_overdue": (g.PAY_0 >= 1).mean(),
                     "Pct_PAY_2_overdue": (g.PAY_2 >= 1).mean()})
    return pd.DataFrame(rows)


def case_snapshots(frame, threshold, k=5):
    """Most confident errors: k lowest-prob false negatives and k highest-prob false positives."""
    out = frame.copy()
    out["Group"] = np.select([(out.default == 1) & (out.Tuned_probability < threshold),
                              (out.default == 0) & (out.Tuned_probability >= threshold)],
                             ["FN", "FP"], default="")
    fn = out[out.Group == "FN"].nsmallest(k, "Tuned_probability")
    fp = out[out.Group == "FP"].nlargest(k, "Tuned_probability")
    return pd.concat([fn, fp])[CASE_COLUMNS]


def run(output_dir=None):
    output = Path(output_dir) if output_dir else ROOT / "results/rf"
    protocol = json.loads((output / "protocol_frozen.json").read_text())
    threshold = float(protocol["Validation_thresholds"]["5"])
    test = pd.read_csv(ROOT / "data/splits/test.csv")
    predictions = pd.read_csv(output / "test_predictions.csv", float_precision="round_trip")
    frame = derive_features(test.merge(predictions[["row_id", "Baseline_probability", "Tuned_probability"]],
                                       on="row_id", how="left"))
    profiles = pd.concat([compute_profiles(frame, .5), compute_profiles(frame, threshold)])
    profiles.to_csv(output / "misclassification_profiles.csv", index=False)
    case_snapshots(frame, .5).to_csv(output / "misclassification_cases_05.csv", index=False)
    case_snapshots(frame, threshold).to_csv(output / "misclassification_cases_r5.csv", index=False)
    print(profiles[["Threshold", "Group", "N", "Mean_PAY_0", "Mean_Utilization_1"]].to_string(index=False), flush=True)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    print(run(parser.parse_args().output_dir))
