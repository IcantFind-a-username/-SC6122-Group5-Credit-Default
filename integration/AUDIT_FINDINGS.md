# Frozen-artifact audit

223 checks passed; 0 discrepancies require interpretation or correction.

Executed from committed integration/audit.py in the unified environment. No model was trained and no historical artifact was overwritten.

## Dataset identity

Byte hashes, LF/CRLF variants and every available historical data blob are recorded in results/final/audit.json. Parsed comparisons include exact values, dtypes and row/column order.

02_preprocessing.ipynb documents EDUCATION {0,5,6}->4, MARRIAGE 0->3; no rows removed/imputation; negative repayment codes and large/negative amounts retained. Original historical download bytes were not preserved; the separate results/final/source_audit.json records fresh official-source replay evidence.

Equal feature vectors retained; do not establish duplicate customers.

## Reconciliation

All audited identities, memberships, models, probabilities, metrics and recorded selections reconcile.

## Concrete findings

- DT/XGBoost training-source hashes match current LF bytes; RF source and metadata hashes match exact CRLF variants. Parsed source values, dtypes and order are unchanged across available git history.
- Fit/validation/test membership is 18000/6000/6000, with defaults 3982/1327/1327; all four models share exact membership and CV folds.
- There are 39 repeated development feature rows beyond the first and 15 test rows whose features occur in development. These are retained per team protocol.
- RF protocol history records an earlier run (3da46a6) and environment regeneration (421b0e1). Timestamp, dependency versions and serialized model hashes changed; current metadata hashes reconcile and prediction CSV history is identical. This chronology must remain visible; it does not establish a newly unseen test set.
- RF historical .5/r=5 group counts and most-confident FN/FP case identities reconcile with full-precision predictions and the exact frozen threshold. No descriptive correction is indicated by these checks.

## Interpretation and limits

- Frozen timestamps are historical self-reports. This audit cannot prove the test set was never viewed before freezing.
- DT/RF serialized training-row counts are checked. XGBoost training row count is not serialized; source code and exact fit membership support 18000, without an independent booster count.
- CV memberships, fold-score arithmetic and recorded winner selection are checked; no CV model is refitted.
- All prediction CSVs are read with float_precision='round_trip'. The >= rule includes exact ties; default pandas parsing can shift a threshold-boundary score.
- results/final/model_comparison.csv contains the historical baseline/tuned 0.5 and historically frozen validation-selected policies; DT has no historical cost-selected policy and none is invented.
- Logistic Regression is a post-hoc reproducibility supplement using the historic holdout, not an independent unseen-test claim. Unverified legacy logistic CSVs are excluded from these comparisons.
- XGBoost replay accepts absolute score differences <=1e-7 consistent with float32 platform drift, while requiring exact decisions at every frozen cutoff. Historical probabilities remain the metric source; replay AP/ROC-AUC/Brier deltas are separately recorded.
- results/final/audit_rf_* are regenerated descriptive RF reference tables. If historical cases/groups differ, replace descriptive RF tables from these files and refresh dependent figures/prose; preserve the frozen models/protocols/predictions.
