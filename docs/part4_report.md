# XGBoost: discrimination and cost-sensitive decisions

## Method

XGBoost fits an additive ensemble of regularized decision trees, allowing nonlinear relationships and interactions between predictors. This analysis separates two questions: whether hyperparameter selection improves discrimination, and whether a decision threshold matched to a specified loss improves classification decisions. The data are the UCI credit-card default records used throughout the project [1].

The shared 24,000-row training partition was divided into 18,000 fitting and 6,000 validation observations by stratified sampling with seed 42. The group's 6,000-row test partition was preserved. Row identifiers and the target were excluded from the predictors. SEX, EDUCATION and MARRIAGE were one-hot encoded inside the estimator pipeline, with encoding learned independently in each cross-validation fold. Other predictors followed the shared cleaning decisions.

Five-fold stratified cross-validation compared 24 configurations, including a prespecified baseline. The search covered tree depth, boosting rounds, learning rate, minimum child weight, row/column subsampling, regularization and positive-class weight [2]. Mean average precision (AP) was the selection criterion. AP is the recall-increment-weighted average of precision, rather than trapezoidal PR area [3]. The selected configuration used 150 trees, depth 4, learning rate 0.03, minimum child weight 10 and positive-class weight 3; both sampling fractions and L2 regularization were 1, with no L1 penalty. Both baseline and selected models were fitted to the same 18,000 observations.

Thresholds were selected using validation predictions alone [4], minimizing

\[
L_r(t)=FP(t)+r\,FN(t),\qquad r\in\{1,3,5,10\}.
\]

The primary scenario, specified before test evaluation, was r=5. These ratios describe hypothetical relative costs, not measured bank losses. All distinct score cutoffs were evaluated, including predicting everyone or nobody positive; ties favored the largest cutoff. Models and thresholds were frozen before loading the test observations, with no subsequent refitting.

## Results

Mean cross-validation AP increased from 0.5598 for the baseline to 0.5620 for the selected configuration. This small selection-stage improvement did not translate into improved test ranking: baseline AP/ROC-AUC were 0.5544/0.7773, compared with 0.5516/0.7762 for the selected model. The paired 95% bootstrap interval for the AP difference was [-0.0106, 0.0054], providing no clear evidence of improved discrimination.

| Test decision rule | Threshold | Precision | Recall | Accuracy | FP | FN | FP + 5 FN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline XGBoost | 0.500 | 0.6565 | 0.3557 | 0.8163 | 247 | 855 | 4,522 |
| Selected XGBoost | 0.500 | 0.5134 | 0.5486 | 0.7852 | 690 | 599 | 3,685 |
| Selected XGBoost, r=5 threshold | 0.315 | 0.3276 | 0.8252 | 0.5867 | 2,248 | 232 | 3,408 |

For the same selected model, changing the cutoff from 0.5 to the validation-selected 0.3150 reduced hypothetical test cost by 277 units (7.52%). It identified 367 additional defaults but produced 1,558 additional false positives. Recall increased by 27.66 percentage points, while the fraction of customers flagged increased from 23.63% to 55.72%. The lower accuracy is consistent with deliberately assigning greater cost to missed defaults. Threshold adjustment leaves AP and ROC-AUC unchanged because it does not alter score ordering.

The paired cost difference was -46.17 units per 1,000 observations, with a 95% interval of [-74.34, -18.00]. Intervals used 1,000 stratified bootstrap resamples of fixed test predictions and therefore exclude training and threshold-selection uncertainty. Sensitivity analysis also showed that improvement is not guaranteed: under r=3, validation threshold selection slightly increased test cost from 2,487 to 2,489 units.

## Interpretation and limitations

Validation permutation importance identified PAY_0 as the dominant predictor: permuting it reduced AP by approximately 0.199, followed by PAY_2 and LIMIT_BAL [5]. This indicates predictive reliance, not causation; correlated repayment variables limit the interpretation of individual importances. The class-weighted model was not probability-calibrated and had a higher test Brier score than the baseline (0.1690 versus 0.1358). Its 0.315 cutoff should not be interpreted as a calibrated 31.5% default probability.

The primary policy would flag over half the sample and may be unsuitable under limited review capacity. Costs omit exposure size, recovery, customer effects and operational constraints. The historical Taiwanese cohort does not establish performance in a current banking population. Fifteen test feature vectors also occurred in the development data; these were retained under the shared protocol because identical features alone do not establish duplicate customers. Finally, other members' models may use different fitting allocations, which must be stated in the group comparison. The evidence supports evaluating the decision rule separately from the ranking model, without claiming general superiority of the tuned estimator.

## References

1. Yeh, I. (2009). *Default of Credit Card Clients*. UCI Machine Learning Repository. https://doi.org/10.24432/C55S3H.
2. XGBoost documentation. *XGBoost Parameters*. https://xgboost.readthedocs.io/en/stable/parameter.html.
3. scikit-learn documentation. *average_precision_score*. https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html.
4. scikit-learn documentation. *Tuning the decision threshold for class prediction*. https://scikit-learn.org/stable/modules/classification_threshold.html.
5. scikit-learn documentation. *Permutation feature importance*. https://scikit-learn.org/stable/modules/permutation_importance.html.

## Integration notes

This is one member's section, not the complete group report. Keep the group's combined report, including references, within seven pages. If space is limited, merge the data/method description into the shared methods section and retain the three-row results table plus the decision-cost finding. Figures 01 and 03 in `results/xgboost/figures/` illustrate ranking and threshold effects; the other figures can support the presentation or repository discussion. Adjust contribution percentages to reflect the work actually performed and reviewed by each member.
