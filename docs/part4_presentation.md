# Part 4 presentation notes

Aim for about three minutes across three slides. Keep the main group presentation within 12 minutes, leaving approximately three minutes for questions.

## Slide 1 — Did tuning improve the ranking?

- 18,000 fitting / 6,000 validation / 6,000 untouched test observations.
- 24 configurations, five-fold stratified CV, selected by mean AP.
- Test AP: baseline 0.5544; selected 0.5516.
- Paired AP difference interval includes zero: no clear ranking improvement.

Visual: `results/xgboost/figures/01_ranking_curves.png`. Explain AP and ROC-AUC briefly; do not spend the slide listing all search parameters.

## Slide 2 — What changes when a missed default costs more?

- Predeclared example: cost = FP + 5 FN.
- Threshold selected on validation: 0.3150; test was not used to choose it.
- Same selected model: recall 54.86% → 82.52%.
- Missed defaults 599 → 232; false alarms 690 → 2,248.

Visual: `results/xgboost/figures/03_confusion_matrices.png`. Point to the two bottom-left cells, then the two top-right cells. Explain both sides of the trade-off.

## Slide 3 — Is the trade-off worthwhile?

- Hypothetical cost 3,685 → 3,408: reduction 7.52%.
- 367 more defaults found, but 1,558 additional false alarms.
- The policy flags 55.72% of customers; operational capacity matters.
- Costs are assumptions; scores are uncalibrated; historical data limit generalization.

Visual: `results/xgboost/figures/05_cost_sensitivity.png`. At r=3, the selected threshold does slightly worse on test: validation choices are not guaranteed to improve every future sample.

## English talk

My part examines XGBoost and the threshold used to flag a customer as likely to default. I separated model selection from decision selection. From the group's training data, I reserved six thousand observations for validation and used eighteen thousand for fitting. The common six-thousand-row test set was kept separate.

I compared twenty-four configurations using five-fold cross-validation and average precision. The selected configuration scored slightly better in cross-validation, but this did not translate into better test ranking. Test average precision was about point five five four for the baseline and point five five two after tuning. The paired confidence interval includes zero, so I cannot claim that tuning improved discrimination.

The next question is whether the default threshold of point five matches our objective. For an illustrative scenario, I assigned a missed default five times the cost of a false alarm. I chose the threshold using validation predictions only, then froze it before test evaluation. The selected threshold was about point three one five.

These two confusion matrices show the effect on the same tuned model. Recall increased from about fifty-five to eighty-three percent. Missed defaults fell from five hundred and ninety-nine to two hundred and thirty-two. However, false positives increased from six hundred and ninety to two thousand two hundred and forty-eight. So the improvement in recall has a substantial price.

Under the assumed cost ratio, total test cost fell by seven and a half percent. That means three hundred and sixty-seven additional defaults were identified at the cost of one thousand five hundred and fifty-eight additional false alarms. Whether this is acceptable depends on the bank's actual costs and its capacity to review customers. This policy flags more than half of the sample.

My conclusion is that ranking quality and the decision threshold need separate evaluation. This experiment supports a lower-cost decision under one stated assumption, rather than a general claim that the tuned model is better. The scores are also not calibrated default probabilities, and the historical dataset limits real-world conclusions.

## 中文答辩准备

### 1. 调参后测试表现没提高，为什么仍然保留？
交叉验证选中了训练数据上更好的配置，但这种小幅提升没有在测试集得到支持。测试AP差值的区间包含0，所以结论是没有明确排名改善。保留预先确定的模型，才能避免根据测试结果反复挑模型。

### 2. AP是什么，为什么不用Accuracy选模型？
AP把PR曲线上每一段召回率增加对应的精确率加权汇总，越大通常代表越能把违约客户排在前面。数据中约22%违约，全部预测不违约也有约78%的准确率，因此Accuracy不足以评价违约识别能力。AP不等于梯形积分版PR-AUC，合并组内结果时要核对实现。

### 3. 为什么用0.315，怎么保证没有看测试集选阈值？
在独立的6,000条验证数据上枚举不同分数阈值，计算FP+5FN，选成本最小的阈值。同成本时取更高阈值，减少告警。代码先保存冻结参数、模型和阈值，再读取测试数据。

### 4. 为什么不是直接用1/(5+1)=0.167？
这个公式要求分数是适用人群下校准的违约概率，并且损失假设成立。这里选出的模型用了正类权重3，输出没有校准，不能直接当作真实概率，所以用验证数据实证选阈值。0.315不等于已经证明客户有31.5%的违约概率。

### 5. 为什么召回率提高，准确率却掉到了58.67%？
我们提高了漏掉违约的代价，模型因此会多报风险。虽然多识别367个违约客户，却多误报1,558个正常客户，正确分类总数下降。在FP+5FN这个目标下，少367个漏报节省1,835个假设成本单位，多误报增加1,558，净减少277。

### 6. 为什么AP和ROC-AUC在调整阈值后完全一样？
阈值只改变哪些样本被判为正类，没有改变预测分数和排序。AP和ROC-AUC使用分数计算，混淆矩阵、召回率和精确率则取决于具体阈值。

### 7. 5倍成本有现实依据吗？
它是预先声明的课堂情景假设，不是从银行经营数据估出来的。我们同时给出1、3、10倍的敏感性分析。实际部署需要真实的损失、回收率、人工审核成本和客户影响，不能把277个单位直接说成节约277元。

### 8. 为什么不用全部24,000条训练数据拟合？
留出6,000条是为了独立选择阈值。基准和调参后XGBoost都用相同18,000条拟合，因此内部比较公平。组员模型如果拟合24,000条，应明确这个差异。选完阈值后直接用更多数据重训会改变分数分布，原阈值不一定继续适合。

### 9. 什么特征最重要？能说它导致违约吗？
验证集置换重要性中PAY_0最突出，其次是PAY_2和LIMIT_BAL。把PAY_0打乱后AP平均下降约0.199，说明模型依赖它。这个分析不是因果检验，多个还款状态变量之间也可能高度相关。

### 10. 置信区间代表什么？
对固定测试集预测做1,000次分层、有放回重采样，同一次抽样同时比较两个模型或两条决策规则，所以是配对比较。它反映在固定模型、阈值和类别数量下的测试抽样不确定性，不包括重新训练和重新选择阈值产生的变化。

### 11. 为什么3倍成本场景反而稍微变差？
阈值是在验证集上选的，不是测试集上的最优阈值。验证集更好的选择可能在测试集上稍差，这里成本从2,487变成2,489，差异很小。不能为了让每个场景都改善而回头调测试阈值。

### 12. 这个模型可以直接上线吗？
目前只能支持课程中的实证分析。数据来自历史台湾客户；我们没有验证当前人群、时间漂移、校准和公平性。主情景会标记55.72%的客户，审核量也很大。应先明确实际成本和容量，再用更新数据做独立验证。

## 小组对接

共享测试集没有改动。合并结果时使用 `results/xgboost/test_metrics.csv`，其中 `Tuned XGBoost` 是0.5阈值，`Tuned XGBoost / cost ratio 5` 是验证集选出的成本阈值。不要把二者的AP/ROC-AUC当成不同模型的排名提升。第四部分的分析覆盖调参、阈值选择、成本敏感性和不确定性；报告中的个人贡献比例按实际完成和共同审阅的工作填写。
