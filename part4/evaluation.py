"""Small, auditable data and decision-metric functions."""
import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
                             confusion_matrix, f1_score, precision_score, recall_score,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import train_test_split

COST_RATIOS = (1, 3, 5, 10)


def feature_target(frame):
    """Remove bookkeeping ID and outcome; never infer an ID as a predictor."""
    if frame.row_id.duplicated().any():
        raise ValueError("row_id must uniquely identify a row")
    x = frame.drop(columns=["row_id", "default"])
    y = frame["default"].astype(int)
    if not frame["default"].isin([0, 1]).all() or y.nunique() != 2:
        raise ValueError("default must contain both binary classes")
    if not np.isfinite(x.to_numpy(dtype=float)).all():
        raise ValueError("Expected finite numeric source features")
    return x, y


def split_development(frame):
    feature_target(frame)
    fit, validation = train_test_split(frame, test_size=.25, random_state=42,
                                       stratify=frame["default"])
    return fit.copy(), validation.copy()


def _checked(y, probability):
    y, p = np.asarray(y), np.asarray(probability, dtype=float)
    if y.ndim != 1 or p.ndim != 1 or len(y) != len(p) or not len(y):
        raise ValueError("Outcomes and scores must be aligned nonempty vectors")
    if not np.isin(y, [0, 1]).all() or len(np.unique(y)) != 2:
        raise ValueError("Evaluation requires both binary classes")
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError("Scores must be finite and within [0, 1]")
    return y.astype(int), p


def metrics(y, probability, threshold=.5):
    y, p = _checked(y, probability)
    if not np.isfinite(threshold):
        raise ValueError("Threshold must be finite")
    pred = (p >= threshold).astype(int)
    tn, fp, fn, tp = (int(v) for v in confusion_matrix(y, pred, labels=[0, 1]).ravel())
    result = {"Threshold": float(threshold), "N": len(y), "TN": tn, "FP": fp,
              "FN": fn, "TP": tp, "Accuracy": accuracy_score(y, pred),
              "Precision": precision_score(y, pred, zero_division=0),
              "Recall": recall_score(y, pred), "F1": f1_score(y, pred, zero_division=0),
              "Specificity": tn / (tn + fp), "FPR": fp / (tn + fp),
              "FNR": fn / (fn + tp), "ROC-AUC": roc_auc_score(y, p),
              "AP": average_precision_score(y, p), "Brier": brier_score_loss(y, p),
              "Alert_rate": float(pred.mean())}
    for ratio in COST_RATIOS:
        result[f"Cost_{ratio}"] = fp + ratio * fn
        result[f"Cost_{ratio}_per_1000"] = (fp + ratio * fn) * 1000 / len(y)
    return result


def threshold_table(y, probability):
    """All distinct decision sets, with tied scores handled together (>= rule)."""
    y, p = _checked(y, probability)
    fpr, tpr, cutoffs = roc_curve(y, p, drop_intermediate=False)
    cutoffs[0] = np.nextafter(1.0, 2.0)  # finite all-negative sentinel, even if p=1
    positive, negative = int(y.sum()), int((y == 0).sum())
    tp, fp = np.rint(tpr * positive).astype(int), np.rint(fpr * negative).astype(int)
    fn, tn = positive - tp, negative - fp
    precision = np.divide(tp, tp + fp, out=np.zeros_like(tpr), where=(tp + fp) > 0)
    f1 = np.divide(2 * tp, 2 * tp + fp + fn, out=np.zeros_like(tpr),
                   where=(2 * tp + fp + fn) > 0)
    table = pd.DataFrame({"Threshold": cutoffs, "TN": tn, "FP": fp, "FN": fn,
                          "TP": tp, "Precision": precision, "Recall": tpr,
                          "F1": f1, "FPR": fpr, "Alert_rate": (tp + fp) / len(y)})
    for ratio in COST_RATIOS:
        table[f"Cost_{ratio}"] = fp + ratio * fn
        table[f"Cost_{ratio}_per_1000"] = (fp + ratio * fn) * 1000 / len(y)
    return table


def select_threshold(table, ratio):
    """Choose minimum validation cost; equal costs prefer fewer alerts."""
    if ratio not in COST_RATIOS:
        raise ValueError("Unsupported predeclared cost ratio")
    return float(table.sort_values([f"Cost_{ratio}", "Threshold"],
                                   ascending=[True, False]).iloc[0].Threshold)
