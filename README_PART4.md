# Part 4: XGBoost and cost-sensitive thresholds

Open [06_xgboost.ipynb](06_xgboost.ipynb) to read the executed analysis. The experiment uses the group's existing CSV files; downloading the data or running another member's notebook is unnecessary.

## Main result

Hyperparameter tuning did not establish improved test ranking: baseline AP was 0.5544 and tuned AP was 0.5516. For the predeclared hypothetical loss `FP + 5 FN`, selecting a threshold on a separate validation set reduced test cost from 3,685 to 3,408 units compared with the same tuned model at threshold 0.5. Recall increased from 54.86% to 82.52%, while false positives increased from 690 to 2,248. The cost reduction is 7.52%, conditional on the assumed loss; it is not a claim about actual monetary savings.

## Setup

Tested with Python 3.12. Run commands from the repository root:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-part4.txt
python -m pytest tests/test_part4.py -q
```

The requirements use the smaller CPU-only XGBoost distribution on Linux/Windows and the standard distribution on macOS. Both expose the same Python module. No GPU is needed. Install a Jupyter notebook frontend separately if desired, or open the notebook with VS Code's Jupyter extension and select this environment.

## Reproduce

```bash
# A separate directory preserves the submitted run and makes comparisons explicit.
python -m part4.experiment --output-dir results/xgboost_reproduction
python -m part4.plots --output-dir results/xgboost_reproduction

# Redraw the submitted figures from saved outputs, without model fitting:
python -m part4.plots
```

The submitted notebook was executed sequentially with in-process IPython because this environment disallows kernel sockets; all seven code cells completed and their outputs are embedded. It can be rerun using a normal Jupyter kernel in the installed environment.

The full run uses 24 configurations, five folds, and 1,000 paired bootstrap replicates. Run time depends on hardware. A directory containing `protocol_frozen.json` cannot be overwritten by the experiment runner. Inspect a reproduction for consistency, not to select another model based on its test outcome. Persisted joblib models should only be loaded from a source you trust.

## Experimental boundaries

- Existing `train.csv`: 24,000 rows, internally divided into fitting (18,000) and validation (6,000), stratified with seed 42.
- Existing `test.csv`: 6,000 rows, unchanged. `row_id` is bookkeeping, not a predictor.
- SEX, EDUCATION and MARRIAGE are one-hot encoded inside every training fold. All other source predictors are retained. No scaling or oversampling is applied.
- Five-fold CV on fitting rows selects mean **average precision (AP)**. The selected model and baseline both fit 18,000 rows. CV mean/SD are selection diagnostics, not independent final performance estimates.
- The validation set selects thresholds for `FP + r FN`, with `r = 1, 3, 5, 10`; **r=5 is the primary predeclared scenario**. All distinct score cutoffs are considered; ties prefer the largest threshold. Classify positive when score >= cutoff.
- Fitted models, thresholds and protocol are saved before the runner loads test observations. No refitting follows threshold selection.
- The class-weighted model's scores are not calibrated default probabilities. In particular, threshold 0.315 does not establish a 31.5% real-world default probability.
- The 1,000 stratified paired bootstrap replicates resample fixed test predictions. Their intervals condition on the fitted models, validation thresholds and class counts; they omit fitting and threshold-selection variability.

## Files for the group

| File | Use |
|---|---|
| `06_xgboost.ipynb` | Executed analysis, tables, figures and interpretation |
| `part4/experiment.py` | Reproducible training, CV, threshold selection and final evaluation |
| `part4/evaluation.py` | Auditable metrics and threshold calculation |
| `part4/plots.py` | Regenerates PNG/SVG figures from saved artifacts |
| `results/xgboost/test_metrics.csv` | Final results for all predeclared decision rules |
| `results/xgboost/cv_results.csv` | All candidate settings, five fold scores and fit scores |
| `results/xgboost/protocol_frozen.json` | Parameters, thresholds, versions and model hashes frozen before test loading |
| `results/xgboost/development_membership.csv` | Exact inner fitting/validation membership |
| `results/xgboost/cv_membership.csv` | Exact CV validation-fold membership within fitting rows |
| `results/xgboost/test_predictions.csv` | Saved holdout scores for checking figures and metrics |
| `results/xgboost/validation_thresholds.csv` | Full validation cost/threshold trade-off |
| `results/xgboost/bootstrap_intervals.csv` | Conditional absolute and paired uncertainty estimates |
| `results/xgboost/validation_importance.csv` | Validation permutation importance, five repeats |
| `results/xgboost/figures/` | Five figures in PNG and editable SVG formats |
| `docs/part4_report.md` | English section to integrate into the seven-page group report |
| `docs/part4_presentation.md` | Three-slide outline, English talk and Chinese Q&A notes |

When loading probability or threshold CSVs, use `pd.read_csv(path, float_precision="round_trip")` so an observation exactly at a selected cutoff keeps the same decision. Predictions are exported as full-precision float64 representations of the model scores.

AP is computed by `average_precision_score`; it is not trapezoidal integration of a precision-recall curve. Verify how other members compute a column named PR-AUC before combining tables. All models must share the test membership, and their fitting/validation allocations must be documented. The existing logistic-regression result files are not treated as a controlled comparison because its original notebook was empty and its workflow could not be recovered; see `integration/LOGISTIC_PROVENANCE.md` for the separately labelled supplement. This contribution makes no claim to be the group's best model.

## Sources

- [UCI Default of Credit Card Clients](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients), DOI: 10.24432/C55S3H, CC BY 4.0.
- [XGBoost parameters](https://xgboost.readthedocs.io/en/stable/parameter.html).
- [scikit-learn: decision threshold selection](https://scikit-learn.org/stable/modules/classification_threshold.html).
- [scikit-learn: average precision](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html).
- [scikit-learn: permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html).
