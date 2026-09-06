# Decision Tree: Methods and Findings

## Methods
We used the team-supplied cleaned data and fixed 24,000/6,000 training–test split. To match Part 4, the development data were further split into 18,000 fitting and 6,000 validation observations. The fitting/validation membership and five stratified cross-validation folds were verified against Part 4's saved row-level files. SEX, EDUCATION and MARRIAGE were one-hot encoded within each training fold; other features retained their cleaned numeric values. The row identifier and outcome were excluded from predictors.

An unrestricted decision tree was compared with 21 combinations of maximum depth (2, 3, 4, 5, 6, 8, unlimited) and minimum leaf size (1, 20, 100). Parameters were selected by mean five-fold Average Precision (AP); ROC-AUC was also recorded. The selected setting was maximum depth **unlimited (None)** and minimum leaf size **100**. Both models were fitted on the 18,000 fitting observations and kept unchanged for validation and final test evaluation. Consistent with Part 4, no refit used the validation rows. The fixed classification rule was probability ≥0.5; thresholds were not tuned in this contribution.

## Overfitting and final evaluation
The unrestricted model's mean CV training AP was 1.0000, versus 0.2970 on CV holdout folds. For the selected tree, the corresponding values were 0.5845 and 0.5307 (holdout-fold SD 0.0185). The reduced training–validation gap supports controlling tree complexity. The selected tree has no explicit depth cap, but its minimum leaf size still limits complexity: the fitted tree has 18 levels of splits and 134 leaves. The depth curve fixes minimum leaf size at 1 and isolates the effect of depth; it is distinct from the joint parameter search.

| Model | AP | ROC-AUC | Accuracy | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline Decision Tree | 0.2843 | 0.6076 | 0.7213 | 0.3783 | 0.4039 | 0.3907 |
| Tuned Decision Tree | 0.5221 | 0.7538 | 0.8168 | 0.6583 | 0.3572 | 0.4631 |

The final test results above use the same 6,000 clients for both trees. At threshold 0.5, the selected tree produced 474 true positives, 853 false negatives, 246 false positives and 4427 true negatives. AP and ROC-AUC assess ranking; accuracy and the default-class precision/recall/F1 use the fixed threshold. All-negative prediction would achieve 77.88% accuracy, illustrating why accuracy alone is insufficient.

## Interpretable rules
The root split was `PAY_0 <= 1.5`. Within the fitting data, the default proportions were 16.51% on the left and 70.13% on the right. These are observed node proportions, not causal effects or externally validated individual probabilities. The top-level figure is truncated: its intermediate nodes must not be described as final predictions. Exact root-to-leaf rules, support counts and default fractions are recorded in `leaf_rules.csv`; `representative_rules.csv` contains the largest-support leaf for each predicted class present.

## Limitations and integration
Hyperparameter selection uses CV scores and can introduce selection optimism; final claims therefore use held-out test metrics. The test data were first loaded by this runner after parameters and fitted models were frozen. Other team members' test results were already visible; this is not a new globally untouched dataset. No additional parameter changes were made after this decision-tree test evaluation. No confidence intervals or significance claims are supplied. The historical Taiwan sample and retained identical feature vectors limit generalization claims. Model rules describe associations, not causal explanations.

The integration now includes verified RF results and a separately labelled post-hoc logistic supplement. Legacy logistic CSVs remain unverified: their original training procedure and PR-AUC definition were not recoverable. The complete comparison and submission materials are in results/final/ and submission/. Shared splits do not imply identical search budgets or globally unseen historical test data.

## Sources
- Team repository, reviewed base commit `0188f4a0df4e46140c8aa8ebfef4ba4a54403255`: https://github.com/IcantFind-a-username/-SC6122-Group5-Credit-Default
- UCI dataset: Yeh, I. (2009). Default of Credit Card Clients. https://doi.org/10.24432/C55S3H (CC BY 4.0).
- Decision-tree implementation: https://scikit-learn.org/stable/modules/tree.html
