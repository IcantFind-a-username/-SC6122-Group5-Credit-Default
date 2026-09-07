# Group 5 — English speaker notes

12-minute talk + 3-minute Q&A. Each member: 180 seconds.

Timing is a rehearsal guide and appears only in notes, not on audience slides.

Finish the main talk on slide 12 (Conclusions & Q&A) and stay there for questions. Slides 13–16 are supporting material: open one only when a question calls for it; do not present them in sequence.

All scripts below are also embedded in the PPTX speaker notes for Presenter View.

## Speaker assignments

| Speaker / student ID | Section | Slides | Contribution |
|---|---|---|---|
| Lei Peng / G2509090C | Part 1: Data checks and preprocessing; logistic baseline; data characteristics and baseline performance | 1–3 | 25% |
| Zhang Hanyu / G2509091L | Part 2: Decision-tree tuning; learned rules and overfitting control | 4–6 | 25% |
| Zhou Xinzhe / G2509033F | Part 3: Random-forest tuning; feature importance and illustrative misclassification cases | 7–9 | 25% |
| Xu Yiqun / G2509092H | Part 4: XGBoost tuning; threshold trade-offs between missed defaults and false alarms | 10–12 | 25% |

Shared by all four members: agree splits, preprocessing and metrics; write individual report/slides; jointly integrate, check results and rehearse. Q15–Q16 audit questions are shared preparation.

Q&A backup leads: slide 13 Zhang Hanyu; slide 14 Xu Yiqun; slide 15 Lei Peng; slide 16 Zhou Xinzhe. Other members support questions in their model area.

Integration and LR supplement prepared with AI assistance for member review.

## Slide 1: Credit Card Default Prediction

**Lei Peng (G2509090C) | Part 1: Data and logistic regression | Contribution 25%**

Target: 45 seconds

Our question is how to identify default risk while balancing predictive ranking, interpretability, and the cost of taking action. We compare logistic regression, a decision tree, random forest, and XGBoost on shared historical records. A model score ranks accounts, but a threshold decides which accounts receive attention. Those are different questions, and our results will show why the distinction matters. I am Lei Peng, and I will begin with the data and logistic regression. Zhang Hanyu will cover the decision tree, Zhou Xinzhe the random forest, and Xu Yiqun XGBoost and decision costs.

**Transition:** First, let us see how the shared data supports a fair comparison.

UCI Default of Credit Card Clients; group experiment artifacts.

## Slide 2: How we split and use the data

**Lei Peng (G2509090C) | Part 1: Data and logistic regression | Contribution 25%**

Target: 70 seconds

The UCI dataset contains thirty thousand Taiwan credit card clients and twenty-three predictors. About twenty-two percent default, so an always-negative classifier can appear accurate while detecting nobody. We retain the supplied stratified split: eighteen thousand fitting rows, six thousand validation rows, and six thousand historical test rows. Five shared folds inside fitting data select configurations by average precision. Each fold learns its own category encoding, and logistic regression also learns scaling there. Validation selects thresholds without a later refit. The audit confirms identical memberships across the reproducible models. This random historical holdout is not temporal or external validation.

**Transition:** With the data roles fixed, we can introduce the logistic reference and its caveat.

Source: data/splits; protocol_frozen.json; results/final/audit.json

## Slide 3: Logistic regression: the linear reference

**Lei Peng (G2509090C) | Part 1: Data and logistic regression | Contribution 25%**

Target: 65 seconds

Logistic regression offers a linear reference whose coefficients describe regularized associations. We used fold-trained scaling and categorical encoding, then compared twelve declared combinations of regularization strength and class weighting. Cross-validation selected C equal to zero point one without class weighting. The test AP is 0.4967, versus 0.4970 for the baseline, so selection did not improve ranking here. Crucially, the original logistic notebook was empty, and its original procedure cannot be verified. We preserve those artifacts and label our reproducible run as a post-hoc supplement after earlier test results existed. Part two now examines how tree regularization changes performance.

**Transition:** I will now hand over to Zhang Hanyu to explain decision-tree regularization.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1 | LR* = post-hoc reproducibility supplement after historic test results existed.

## Slide 4: Decision tree: controlling overfitting

**Zhang Hanyu (G2509091L) | Part 2: Decision tree and overfitting | Contribution 25%**

Target: 50 seconds

A decision tree can create very detailed splits, so it can easily overfit.
In our baseline model, the tree fits the training folds almost perfectly, but its cross-validation performance is much lower.
We therefore tested 21 combinations of maximum depth and minimum leaf size. The selected model requires at least 100 observations in each leaf, while keeping no explicit depth limit.
On the test set, average precision improves from 0.284 to 0.522.
So the key point is that controlling leaf size greatly improves the decision tree’s held-out performance on this split.
Next, I’ll show one of the main rules learned by this model.

**Transition:** Next, we inspect one rule to understand the tree's predictive pattern.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1

## Slide 5: Reading the tree’s first decision

**Zhang Hanyu (G2509091L) | Part 2: Decision tree and overfitting | Contribution 25%**

Target: 55 seconds

The selected tree starts with recent repayment status, PAY zero.
The root split is at 1.5. In the fitting sample, the default rate is about 16.5% on the left branch, compared with about 70.1% on the right branch.
This shows that recent repayment status is one of the strongest predictive signals used by the tree.
However, this is only an association in our fitted data. It does not mean repayment status directly causes default.
The full tree is still quite large, with depth 18 and 134 leaves, so this rule is just one representative example rather than a complete explanation of the model.
Next, we compare the tree with the other models using the same ranking metric.

**Transition:** We can now place the tree beside the other models using a common ranking metric.

Source: saved decision-tree model; integration audit/report evidence.

## Slide 6: Ranking performance across four models

**Zhang Hanyu (G2509091L) | Part 2: Decision tree and overfitting | Contribution 25%**

Target: 75 seconds

Finally, we compare the effect of tuning across all four model families using test average precision.
The most noticeable result is the decision tree. Its AP increases substantially from 0.284 to 0.522 after tuning. In comparison, logistic regression stays around 0.497, and random forest improves only moderately. XGBoost changes very little.
In this comparison, the decision tree benefits the most from hyperparameter tuning, which is consistent with what we saw earlier: controlling tree complexity is especially important for reducing overfitting.
In terms of final ranking performance, the selected XGBoost and random forest models achieve AP values of 0.552 and 0.551 respectively. These values are extremely close, so we should not claim that one is clearly superior.
Also, model selection was based on cross-validation before evaluating the test set, so we do not re-select a model simply because a baseline happens to perform slightly better on the test data.
LR remains a separately labelled post-hoc supplement. Zhou Xinzhe will now explain random-forest tuning, feature importance and error cases.

**Transition:** I will now hand over to Zhou Xinzhe for random forest, feature importance, and error cases.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1 | LR* = post-hoc reproducibility supplement after historic test results existed.

## Slide 7: Random forest: averaging and regularization

**Zhou Xinzhe (G2509033F) | Part 3: Random forest and error analysis | Contribution 25%**

Target: 70 seconds

Random forest averages many trees, reducing dependence on any single partition. We evaluated a baseline and twenty-three seeded candidate configurations using the same five fitting folds and average-precision objective. The selected configuration uses five hundred trees, maximum depth eight, a minimum leaf size of two, and half the features at each split. It also weights the positive class three times as heavily. Test AP changes from 0.5312 to 0.5508. Class weighting affects the learned score distribution, so we should not assume these scores are calibrated probabilities. We next examine which features the fitted forest relies on and where it makes errors.

**Transition:** We next examine which features the forest uses to rank risk.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1 | results/rf/protocol_frozen.json

## Slide 8: Random forest: which features matter?

**Zhou Xinzhe (G2509033F) | Part 3: Random forest and error analysis | Contribution 25%**

Target: 60 seconds

We measure importance by shuffling one feature on validation data and observing the fall in average precision. The forest relies most strongly on recent repayment status, PAY zero: its mean AP decrease is 0.1971. Earlier repayment status, PAY two, follows at 0.0196. These values come from five saved permutations of each feature. They describe the fitted forest's predictive reliance, not a causal effect or a feature's isolated contribution. Correlated predictors can substitute for one another, and shuffling may create combinations that do not occur naturally. The chart shows mean decreases; variation across shuffles is recorded in the report. Even an influential variable cannot explain every customer's outcome.

**Transition:** We now look at two saved errors to understand the limits of these patterns.

Source: results/rf/validation_importance.csv | Five validation permutations; frozen model.

## Slide 9: Random forest: two illustrative errors

**Zhou Xinzhe (G2509033F) | Part 3: Random forest and error analysis | Contribution 25%**

Target: 50 seconds

At the fixed threshold of zero point five, the selected forest misses 637 defaults and falsely flags 573 non-defaults. Consider two examples already present in the saved error export. Row 982 actually defaults but receives a score of 0.1012; its recent repayment code is -2. Row 28747 does not default but scores 0.9415; its recent repayment code is 3. These examples show that repayment history is informative but not deterministic. They are the most confident errors from the existing export, not representative average customers. We do not change the model after inspecting them. Xu Yiqun will now examine the separate trade-off created by changing a validation-selected threshold.

**Transition:** I will now hand over to Xu Yiqun for XGBoost and the cost of acting on its scores.

Source: results/rf/misclassification_cases_05.csv | Tuned RF; score ≥ 0.5 predicts default.

## Slide 10: XGBoost: no gain in test ranking

**Xu Yiqun (G2509092H) | Part 4: XGBoost and threshold trade-offs | Contribution 25%**

Target: 60 seconds

XGBoost builds trees sequentially with regularization. We retained the baseline and searched twenty-three additional seeded configurations using the shared CV objective. The selected configuration has test AP 0.5516, compared with 0.5544 for the baseline. The paired bootstrap interval for the difference spans zero, so we do not claim a ranking improvement. This bootstrap resamples the fixed predictions and does not include model retraining or selection uncertainty. The useful next question is separate: given the selected model's scores, how does a validation-chosen action threshold change missed defaults, false positives, and the stated hypothetical cost?

**Transition:** The next slide holds scores fixed and changes only the validation-selected threshold.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1 | results/xgboost/bootstrap_intervals.csv

## Slide 11: XGBoost: fewer misses, more reviews

**Xu Yiqun (G2509092H) | Part 4: XGBoost and threshold trade-offs | Contribution 25%**

Target: 80 seconds

At a cost ratio of five, validation selects XGBoost's threshold at 0.3150. Applying it unchanged to the historical test set reduces false negatives from 599 to 232, while false positives rise from 690 to 2248. Recall reaches 82.5%, but 55.7% of clients are flagged. The total hypothetical cost falls from 3685 to 3408, about 7.5%. This is not an improvement in AP or ROC-AUC; the scores have not changed. The policy may be impractical if review capacity is limited. Real exposure, loss severity, and intervention benefits are unavailable, so these cost units are a sensitivity analysis.

**Transition:** This trade-off leads to our main conclusion about ranking, costs, and workload.

Source: results/final/model_comparison.csv | Historical test n=6,000; default=1 | FP + 5×FN; threshold selected only on validation.

## Slide 12: Conclusions & Q&A

**Xu Yiqun (G2509092H) | Part 4: XGBoost and threshold trade-offs | Contribution 25%**

Target: 40 seconds

Ranking and action policy answer different questions. Tree regularization improves its baseline, while the selected ensembles have similar ranking estimates. Lower thresholds reduce the stated cost by creating more reviews. Operational recommendations require realistic costs and capacity constraints. Historical data, duplicates, random splitting, and logistic provenance remain limitations. A new study should use fresh temporal or external data and examine calibration and subgroup errors. Thank you. We welcome your questions.

**Transition:** We welcome your questions; the following slides provide supporting details.

Historical educational study; no causal or deployment-readiness claim.

## Slide 13: Backup A • AP, ROC-AUC and threshold metrics

**Zhang Hanyu (G2509091L) | Part 2: Decision tree and overfitting | Contribution 25%**

Q&A backup — use when relevant

If asked about the ranking metric, explain that average precision weights each precision value by the associated increase in recall. It does not linearly interpolate the precision-recall curve with trapezoids, so similarly named PR-AUC values need not agree. ROC-AUC instead summarizes positive-versus-negative score ordering. Neither metric changes when we apply a different operating threshold to the same saved scores. Precision and recall do change because the decision set changes. The historical logistic CSV uses a PR-AUC label whose computation cannot be verified, which is one reason it is excluded from our verified ranking table.

**Transition:** If useful, we can next explain the cost rule and the scope of its uncertainty.

Source: scikit-learn average_precision_score documentation; part4/evaluation.py

## Slide 14: Backup B • Cost ratios and fixed-prediction uncertainty

**Xu Yiqun (G2509092H) | Part 4: XGBoost and threshold trade-offs | Contribution 25%**

Q&A backup — use when relevant

The cost experiment declares four ratios rather than searching for a convenient ratio after viewing test results. At each ratio, the validation table includes all distinct score-based decision sets, with tied scores moving together. Equal costs select the largest threshold and therefore fewer alerts. The paired bootstrap samples the same test-row indices for each compared prediction vector, stratified by outcome. Its intervals are conditional on frozen models, thresholds, and class counts. They do not include uncertainty from refitting, hyperparameter search, threshold search, or a shift to another population. Real operational costs would require information that this dataset does not provide.

**Transition:** We can also explain where the source data and evidence boundaries come from.

Source: frozen protocols; integration/uncertainty.py; bootstrap_intervals.csv

## Slide 15: Backup C • Data provenance and evidence boundaries

**Lei Peng (G2509090C) | Part 1: Data and logistic regression | Contribution 25%**

Q&A backup — use when relevant

The integration audit redownloaded the official source and reproduced the committed cleaned dataset in values, types, order, and schema. Undocumented education categories are consolidated, and marriage category zero is mapped to other. The original download bytes were not preserved, so the new download and its hash are documented separately. Duplicate feature vectors remain under the established protocol and may create dependence across partitions. For logistic regression, the original notebook history contained an empty model notebook. The supplement's code and search declaration were committed before execution, but previous team test results already existed. This makes the supplement reproducible without making it independent external evidence.

**Transition:** The last backup lists the references and each member’s contribution.

Sources: results/final/source_audit.json; integration/LOGISTIC_PROVENANCE.md

## Slide 16: Backup D • Sources, responsibilities and reproducibility

**Zhou Xinzhe (G2509033F) | Part 3: Random forest and error analysis | Contribution 25%**

Q&A backup — use when relevant

The numerical source for this editable presentation is the audited final comparison CSV, with model-specific protocols and bootstrap artifacts supplying supporting context. The UCI dataset, scikit-learn average-precision documentation, and the XGBoost paper are the core external references. The role plan assigns three minutes each to data and logistic regression, decision trees and ranking, random forest with feature importance and error cases, and XGBoost with threshold trade-offs. Lei Peng covers part one, Zhang Hanyu part two, Zhou Xinzhe part three, and Xu Yiqun part four. The group has confirmed equal contributions of twenty-five percent each. Data-split and metric agreement, final integration, checking and rehearsal are shared by all four members. Integration and the logistic supplement were prepared with AI assistance for member review. Reproducing artifacts is distinct from retraining and selecting new models.

**Transition:** We can return to the main conclusion or discuss a specific model or policy.

Sources: Group 5 repository, frozen protocols, row-level predictions and integration audit.
