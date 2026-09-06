# Group 5 — English speaker notes

12-minute talk + 3-minute Q&A. Each role: 180 seconds.

Member identities and contribution shares: NAME / ID / SHARE TO CONFIRM.

Integration and LR supplement prepared with AI assistance for member review.

## Slide 1: Credit default: rank risk, then choose an action

**Part 1 — 45 seconds** | NAME / ID / SHARE TO CONFIRM

Our question is how to identify default risk while balancing predictive ranking, interpretability, and the cost of taking action. We compare logistic regression, a decision tree, random forest, and XGBoost on shared historical records. A model score ranks accounts, but a threshold decides which accounts receive attention. Those are different questions, and our results will show why the distinction matters. Each of our four roles has three minutes, followed by three minutes for questions. Member names, student IDs, and contribution shares remain visibly marked for confirmation. I will begin with the data and the evidence boundary.

**Transition:** First, let us see how the shared data supports a fair comparison.

UCI Default of Credit Card Clients; group experiment artifacts.

## Slide 2: One split, shared folds, distinct responsibilities

**Part 1 — 70 seconds** | NAME / ID / SHARE TO CONFIRM

The UCI dataset contains thirty thousand Taiwan credit card clients and twenty-three predictors. About twenty-two percent default, so an always-negative classifier can appear accurate while detecting nobody. We retain the supplied stratified split: eighteen thousand fitting rows, six thousand validation rows, and six thousand historical test rows. Five shared folds inside fitting data select configurations by average precision. Each fold learns its own category encoding, and logistic regression also learns scaling there. Validation selects thresholds without a later refit. The audit confirms identical memberships across the reproducible models. This random historical holdout is not temporal or external validation.

**Transition:** With the data roles fixed, we can introduce the logistic reference and its caveat.

Source: data/splits; protocol_frozen.json; results/final/audit.json

## Slide 3: Logistic regression: a transparent reference, with a caveat

**Part 1 — 65 seconds** | NAME / ID / SHARE TO CONFIRM

Logistic regression offers a linear reference whose coefficients describe regularized associations. We used fold-trained scaling and categorical encoding, then compared twelve declared combinations of regularization strength and class weighting. Cross-validation selected C equal to zero point one without class weighting. The test AP is 0.4967, versus 0.4970 for the baseline, so selection did not improve ranking here. Crucially, the original logistic notebook was empty, and its original procedure cannot be verified. We preserve those artifacts and label our reproducible run as a post-hoc supplement after earlier test results existed. Part two now examines how tree regularization changes performance.

**Transition:** Part two now explains what changes when we regularize a decision tree.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1 | LR* = post-hoc reproducibility supplement after historic test results existed.

## Slide 4: Decision tree: constrain leaves to reduce overfitting

**Part 2 — 65 seconds** | NAME / ID / SHARE TO CONFIRM

A decision tree can fit very detailed partitions, which makes overfitting easy. Our baseline achieves nearly perfect fitting-fold AP but only about zero point three in cross-validation. The declared grid searches seven depth limits and three minimum leaf sizes, giving twenty-one configurations. The selected model requires at least one hundred observations in each leaf, although it has no explicit depth cap. Test AP rises from 0.2843 to 0.5221. This is a substantial change for this model and split. It supports regularization as an explanation, rather than treating training performance as evidence of generalization. Next, we inspect what the tree actually uses.

**Transition:** Next, we inspect one rule to understand the tree's predictive pattern.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1

## Slide 5: Tree rules make a predictive association inspectable

**Part 2 — 60 seconds** | NAME / ID / SHARE TO CONFIRM

The selected tree begins with recent repayment status, PAY zero. Its root separates values at one point five. In the fitting sample, the default proportions are sixteen point five one percent on the left and seventy point one three percent on the right. This provides a concise description of an important predictive pattern. It does not mean repayment status causes the outcome, and node proportions are not a substitute for calibration analysis. The full selected tree still has depth eighteen and one hundred thirty-four leaves. We therefore use a representative rule rather than claiming the whole tree is a small explanation.

**Transition:** We can now place the tree beside the other models using a common ranking metric.

Source: saved decision-tree model; integration audit/report evidence.

## Slide 6: Compare ranking point estimates without declaring a winner

**Part 2 — 55 seconds** | NAME / ID / SHARE TO CONFIRM

This comparison retains both the baseline and the cross-validation-selected model for each family. Average precision is a recall-increment weighted sum of precision, not the trapezoidal area sometimes also called PR-AUC. Our positive prevalence is approximately zero point two two, which gives useful context for these scores. The selected forest has AP 0.5508, and selected XGBoost has 0.5516. Those close point estimates do not establish superiority. The XGBoost baseline is numerically higher, but this retrospective observation does not authorize another selection round on test results. Part three will examine the forest and the fairness of our comparison.

**Transition:** Part three will explain the forest result and the evidence behind our comparison.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1 | LR* = post-hoc reproducibility supplement after historic test results existed.

## Slide 7: Random forest: average trees, then tune complexity

**Part 3 — 70 seconds** | NAME / ID / SHARE TO CONFIRM

Random forest averages many trees, reducing dependence on any single partition. We evaluated a baseline and twenty-three seeded candidate configurations using the same five fitting folds and average-precision objective. The selected configuration uses five hundred trees, maximum depth eight, a minimum leaf size of two, and half the features at each split. It also weights the positive class three times as heavily. Test AP changes from 0.5312 to 0.5508. Class weighting affects the learned score distribution, so we should not assume these scores are calibrated probabilities. We next inspect the operating threshold and the resulting workload rather than relying on ranking alone.

**Transition:** We next move from the forest's ranking to its decision threshold.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1 | results/rf/protocol_frozen.json

## Slide 8: Forest policy: fewer misses, more review alerts

**Part 3 — 60 seconds** | NAME / ID / SHARE TO CONFIRM

For the forest, validation selected a threshold of 0.3229 under the hypothetical assumption that a missed default costs five times a false-positive review. On the historical test set, recall rises from 52.0% to 77.1%, but the alert rate also rises from 21.1% to 48.4%. Cost falls from 3758 to 3404 units. We independently checked the saved error profiles and case rules for both policies. The most confident errors can appear in both exports because they remain errors at both thresholds. Identical extreme examples alone therefore do not demonstrate an export mistake.

**Transition:** Before comparing policies, we should check that the underlying evidence aligns.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1 | RF misclassification audit; costs hypothetical.

## Slide 9: What the audit establishes—and what it cannot

**Part 3 — 50 seconds** | NAME / ID / SHARE TO CONFIRM

Our audit checks that comparisons use the same clients, labels, development partitions, and five-fold memberships. It recomputes metrics from row-aligned saved predictions and applies the exact greater-than-or-equal decision rule before rounding. Saved-model replay reproduces frozen decisions; minor floating-point differences are documented. These checks make the comparison traceable, but they do not make every aspect identical: search budgets differ, and the logistic supplement has a distinct evidence history. Nor can a repository audit prove everything performed outside the repository. With those boundaries explicit, part four now separates XGBoost's ranking result from its threshold-policy result.

**Transition:** Part four now separates XGBoost's ranking result from its action-policy result.

Source: results/final/audit.json; integration/LOGISTIC_PROVENANCE.md

## Slide 10: XGBoost: tuning did not improve test ranking

**Part 4 — 60 seconds** | NAME / ID / SHARE TO CONFIRM

XGBoost builds trees sequentially with regularization. We retained the baseline and searched twenty-three additional seeded configurations using the shared CV objective. The selected configuration has test AP 0.5516, compared with 0.5544 for the baseline. The paired bootstrap interval for the difference spans zero, so we do not claim a ranking improvement. This bootstrap resamples the fixed predictions and does not include model retraining or selection uncertainty. The useful next question is separate: given the selected model's scores, how does a validation-chosen action threshold change missed defaults, false positives, and the stated hypothetical cost?

**Transition:** The next slide holds scores fixed and changes only the validation-selected threshold.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1 | results/xgboost/bootstrap_intervals.csv

## Slide 11: A lower threshold trades review capacity for fewer misses

**Part 4 — 80 seconds** | NAME / ID / SHARE TO CONFIRM

At a cost ratio of five, validation selects XGBoost's threshold at 0.3150. Applying it unchanged to the historical test set reduces false negatives from 599 to 232, while false positives rise from 690 to 2248. Recall reaches 82.5%, but 55.7% of clients are flagged. The total hypothetical cost falls from 3685 to 3408, about 7.5%. This is not an improvement in AP or ROC-AUC; the scores have not changed. The policy may be impractical if review capacity is limited. Real exposure, loss severity, and intervention benefits are unavailable, so these cost units are a sensitivity analysis.

**Transition:** This trade-off leads to our main conclusion about ranking, costs, and workload.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1 | FP + 5×FN; threshold selected only on validation.

## Slide 12: Choose the decision question before choosing the policy

**Part 4 — 40 seconds** | NAME / ID / SHARE TO CONFIRM

Ranking and action policy answer different questions. Tree regularization improves its baseline, while the selected ensembles have similar ranking estimates. Lower thresholds reduce the stated cost by creating more reviews. Operational recommendations require realistic costs and capacity constraints. Historical data, duplicates, random splitting, and logistic provenance remain limitations. A new study should use fresh temporal or external data and examine calibration and subgroup errors. Thank you; we now have three minutes for questions.

**Transition:** We welcome your questions; the following slides provide supporting details.

Historical educational study; no causal or deployment-readiness claim.

## Slide 13: Backup A • AP, ROC-AUC and threshold metrics

**Q&A — 0 seconds** | NAME / ID / SHARE TO CONFIRM

If asked about the ranking metric, explain that average precision weights each precision value by the associated increase in recall. It does not linearly interpolate the precision-recall curve with trapezoids, so similarly named PR-AUC values need not agree. ROC-AUC instead summarizes positive-versus-negative score ordering. Neither metric changes when we apply a different operating threshold to the same saved scores. Precision and recall do change because the decision set changes. The historical logistic CSV uses a PR-AUC label whose computation cannot be verified, which is one reason it is excluded from our verified ranking table.

**Transition:** If useful, we can next explain the cost rule and the scope of its uncertainty.

Source: scikit-learn average_precision_score documentation; part4/evaluation.py

## Slide 14: Backup B • Cost ratios and fixed-prediction uncertainty

**Q&A — 0 seconds** | NAME / ID / SHARE TO CONFIRM

The cost experiment declares four ratios rather than searching for a convenient ratio after viewing test results. At each ratio, the validation table includes all distinct score-based decision sets, with tied scores moving together. Equal costs select the largest threshold and therefore fewer alerts. The paired bootstrap samples the same test-row indices for each compared prediction vector, stratified by outcome. Its intervals are conditional on frozen models, thresholds, and class counts. They do not include uncertainty from refitting, hyperparameter search, threshold search, or a shift to another population. Real operational costs would require information that this dataset does not provide.

**Transition:** We can also explain where the source data and evidence boundaries come from.

Source: frozen protocols; integration/uncertainty.py; bootstrap_intervals.csv

## Slide 15: Backup C • Data provenance and evidence boundaries

**Q&A — 0 seconds** | NAME / ID / SHARE TO CONFIRM

The integration audit redownloaded the official source and reproduced the committed cleaned dataset in values, types, order, and schema. Undocumented education categories are consolidated, and marriage category zero is mapped to other. The original download bytes were not preserved, so the new download and its hash are documented separately. Duplicate feature vectors remain under the established protocol and may create dependence across partitions. For logistic regression, the original notebook history contained an empty model notebook. The supplement's code and search declaration were committed before execution, but previous team test results already existed. This makes the supplement reproducible without making it independent external evidence.

**Transition:** The last backup lists our references and the responsibilities still to confirm.

Sources: results/final/source_audit.json; integration/LOGISTIC_PROVENANCE.md

## Slide 16: Backup D • Sources, responsibilities and reproducibility

**Q&A — 0 seconds** | NAME / ID / SHARE TO CONFIRM

The numerical source for this editable presentation is the audited final comparison CSV, with model-specific protocols and bootstrap artifacts supplying supporting context. The UCI dataset, scikit-learn average-precision documentation, and the XGBoost paper are the core external references. The role plan assigns three minutes each to data and logistic regression, decision trees and ranking, random forest and audit, and XGBoost and costs. Member identities and contribution percentages must be confirmed by the group; we have not invented them. Integration and the logistic supplement were prepared with AI assistance for member review. Reproducing artifacts is distinct from retraining and selecting new models.

**Transition:** We can return to the main conclusion or discuss a specific model or policy.

Sources: Group 5 repository, frozen protocols, row-level predictions and integration audit.
