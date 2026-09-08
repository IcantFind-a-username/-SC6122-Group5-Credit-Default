# Logistic regression provenance and supplement declaration

The historical logistic artifacts remain unchanged in `results/logistic_regression_*.csv`. Their execution provenance cannot be recovered from this repository snapshot.

Evidence searched: all local and remote-tracking refs; `git log --all --name-only -- '*.ipynb'`; the notebook blobs at every relevant commit; all reflogs; and `git fsck --full --no-reflogs --unreachable` (no recoverable unreachable objects reported). Commit `959a2b27` is the only history entry for `03_logistic_regression.ipynb`: its blob is the empty-file object `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`, size zero. `01_data_inspection.ipynb` contains inspection, and `02_preprocessing.ipynb` contains cleaning and the shared split; neither supplies a logistic fitting/search procedure. This establishes missing repository provenance, not that the historical authors never ran a model elsewhere. No legacy hyperparameters, scaling procedure, fitting membership, or fold membership can honestly be inferred solely from summary CSVs.

## Declared before supplement execution

`python -m part1.experiment --output-dir results/logistic_supplement` is a **post-hoc reproducibility supplement after historic test results existed**. It is not a recovered legacy notebook or an independent unseen-test study. The controller must commit this script and declaration before running it.

The supplied 24,000 development rows are split identically to Parts 3/4 into 18,000 fit and 6,000 validation rows, with stratification and seed 42. Five stratified, shuffled CV folds on the fit rows use seed 42. Membership files permit exact cross-model auditing.

The declared exhaustive budget is 12 configurations: `C = [0.001, 0.01, 0.1, 1, 10, 100]` crossed with `class_weight = [None, 'balanced']`. Candidate 0 is the explicit unweighted `C=1` baseline; the remaining unique configurations follow deterministic `ParameterGrid` order. Logistic regression uses L2 regularization (`l1_ratio=0` under scikit-learn 1.8), `lbfgs`, `max_iter=3000`, and seed 42. The model pipeline learns one-hot categories for SEX/EDUCATION/MARRIAGE and numeric StandardScaler statistics only from each fitting fold. Unknown categories are ignored. Selection maximizes mean CV average precision, with ties preferring the lowest candidate index. No search expansion is permitted based on historical or new test results.

Both final pipelines fit the 18,000 fit rows. Validation selects thresholds for hypothetical costs `FP + r*FN`, `r = 1,3,5,10`, using shared complete threshold enumeration and the largest-threshold tie rule. No refit follows selection. The protocol, models, and thresholds are frozen before this runner reads test rows. The existing 6,000 historical test rows are then evaluated once. Saved bootstrap intervals condition on those fitted models and the reused test sample; they do not establish external validation or erase historical exposure.

Outputs include pipelines, exact-score validation/test predictions, CV scores and membership, development membership, validation thresholds, metrics, coefficients, validation permutation importance, conditional bootstrap intervals, and source/artifact hashes. Coefficients are on fit-standardized numeric and full one-hot categorical scales, are regularized associations, and do not establish causality. Historical artifacts and supplement artifacts must be presented separately.

## Clarification on 2026-09-09

The group confirms that Lei Peng has the original LR work. The earlier search only described the repository snapshot and must not be interpreted as saying he did not perform LR. A fresh fetch of all remote refs on 9 September found no additional original fitting implementation. Its local path or branch has been requested. The report now credits his preprocessing and initial LR work explicitly, while identifying the integration run used for its numerical comparisons in one concise methods paragraph. Historical results, the supplement protocol and all model metrics remain unchanged.

## Recheck of original member results — 2026-09-09

A repeated fetch and `ls-remote --heads --tags` found the same five remote branches. Commit `959a2b2`, authored by `Leis101` on 5 September, supplies the original LR summary tables. Original baseline accuracy is 0.8088333333333333, ROC-AUC 0.7100908859130948 and recall 0.24415975885455915. These values are now explicitly attributed in the report, separately from the LR* comparison run. The report does not say the member did no LR work.

The original `03_logistic_regression.ipynb` remains a zero-byte blob on the member/main history. The current populated notebook and `part1/experiment.py` on the integration branch are the later supplement. Four unreachable tree objects found by the repeat fsck were inspected; their LR entries point to the same known supplement/legacy blobs and expose no additional original fitting implementation. Thus original results exist, while their training implementation has not been recovered in the searched repository. No new experiment was run and no supplement result was relabelled as an original member result.

## Main-report presentation update

The final report now presents the four recorded workflows under a common methods section, with unmarked LR labels and a study-level statement about historical test exposure. It no longer includes the separate original-LR metric paragraph or a member-specific provenance narrative. The common comparison values, underlying models and predictions are unchanged. The original CSVs and this chronology remain in the repository; no integration result is newly claimed to reproduce the member's original execution.
