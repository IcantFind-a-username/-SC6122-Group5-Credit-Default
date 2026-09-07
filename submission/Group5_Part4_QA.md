# Xu Yiqun — 第四部分答辩速查

**G2509092H · XGBoost 与阈值取舍 · PPT 第 10–12 页**

先练 Q1–Q6，再看 Q7–Q10。每题先用英文短答给出结论，被追问时再用中文解释中的证据展开。数字与当前最终 PPT 一致；成本均为假设单位，不是真实金额。

## 最重要的一句话

**调参没有证明排序能力提高；同一模型降低验证集选择的阈值，用更多误报换取更少漏报，从而降低了假设成本。**

“XGBoost tuning did not improve test ranking. With the same model scores, a validation-selected threshold reduced hypothetical cost by accepting more false positives to miss fewer defaults.”

## 数字速记

| 要点 | 数值 |
|---|---|
| Baseline → tuned 测试 AP | 0.5544 → 0.5516：没有明确改善 |
| Tuned 测试 ROC-AUC | 0.7762 |
| r=5 验证阈值 | 约 0.3150；计算用完整精度 |
| 漏报 FN | 599 → 232 |
| 误报 FP | 690 → 2,248 |
| Recall | 54.86% → 82.52% |
| 假设成本 FP+5FN | 3,685 → 3,408，下降 7.52% |
| 降阈值后的告警比例 | 55.72%，审查负担很高 |

## Q1. XGBoost 调了什么参数，最后选了什么？

**中文理解：** 使用 18,000 条 fitting 数据里的五折 CV，按 mean AP 选配置。共 24 个配置，即 baseline 加 23 个固定种子候选。选中 150 棵树、max_depth=4、learning_rate=0.03、min_child_weight=10、scale_pos_weight=3；subsample 和 colsample_bytree 均为 1，reg_lambda=1，reg_alpha=0。树数、深度和学习率控制模型容量与学习步幅；正类权重影响学习目标和分数分布，不等于最终采用的 FN:FP 成本比。最终在全部 18,000 条 fitting 数据上拟合，validation 不并回训练。

**English answer:** “We compared 24 configurations using five-fold CV on the fitting set and selected by mean AP. The chosen model uses 150 trees, depth four, learning rate 0.03, minimum child weight ten and positive-class weight three. Hyperparameter selection uses CV, while the decision threshold is selected separately on validation.”

## Q2. 调参后 AP 反而低了，怎么解释？

**中文理解：** 展示的测试点估计中，XGBoost baseline AP=0.5544，tuned XGBoost=0.5516，tuned RF=0.5508。tuned 指按照预定 CV 规则选出的配置，不保证在另一个样本上一定更优。XGBoost tuned-minus-baseline AP 差为 -0.0028，条件 bootstrap 95% 区间约 [-0.0106, 0.0054]，包含 0。测试后再以最高值更换模型会形成新的选择步骤；RF 与 XGBoost 之间也没有由这组区间直接建立显著胜负。

**English answer:** “Baseline XGBoost has the highest displayed AP point estimate, but tuning was selected by CV, not test performance. Its tuned-minus-baseline AP interval includes zero. We report that outcome honestly and do not start another selection round or claim a statistically established winner between RF and XGBoost.”

## Q3. 超参数和阈值分别在哪个数据集上选？

**中文理解：** 超参数由 fit 内五折 mean AP 选；LR*、RF、XGBoost 的阈值由独立 validation 的 FP+rFN 最小值选，r∈{1,3,5,10}。测试时使用原样阈值。DT 历史实验仅定义了固定 0.5 策略，看到 test 结果后不能补出一个“历史冻结”的 DT 成本策略。若未来需要完整政策比较，应先制定新协议，再在新的可用验证与独立评估数据上执行。

**English answer:** “Hyperparameters use fitting-fold CV; cost thresholds use validation only and are applied unchanged to test. The historical tree experiment specifies only a 0.5 cutoff. We do not invent an additional frozen tree policy after seeing the results.”

## Q4. 降低阈值的收益和代价是什么？

**中文理解：** 对同一个 tuned XGBoost，从 0.5 改为验证选定的 r=5 阈值 0.31501567363739014，FN 从 599 降至 232，FP 从 690 增至 2,248；假设成本从 3,685 降至 3,408。Recall 从 54.86% 升到 82.52%，precision 从 51.34% 降至 32.76%，提醒比例升至 55.72%。RF 的对应成本为 3,404、提醒比例 48.45%、recall 77.09%；它只比 XGBoost 少 4 个假设单位，不能支持强烈的成本优越性结论。AP 与 ROC-AUC 都不因单纯改阈值而提高。

**English answer:** “Lowering the XGBoost cutoff reduces missed defaults but increases false positives and flags 55.72% of accounts. Its r=5 cost falls from 3,685 to 3,408. RF costs 3,404 with fewer alerts and lower recall; a four-unit difference does not justify a strong superiority claim.”

## Q5. 为什么假设漏报成本是误报的五倍？容量只有 10% 怎么办？

**中文理解：** r=5 是预先声明的假设情景之一，不是从真实贷款损失估计的金额。我们还展示 r=1/3/10 的敏感性；没有贷款敞口、违约损失率、干预效果及审查成本，不能称为实际利润提升。若存在 10% 审查容量，现有高提醒率策略显然不满足；应先把容量写入政策目标，再在 validation 上评估排序截断、并列分数处理及成本，最后用新的独立数据检验。不能在看过 test 后临时调阈值使结果好看，也不能假定未校准分数适用理论阈值 1/(1+r)。

**English answer:** “The cost ratio is a hypothetical sensitivity assumption, not measured monetary loss. A 10% review limit would require a separately validated capacity-constrained policy, including tie handling. We would not adjust the cutoff on the existing test set or assume that uncalibrated scores justify a theoretical cost cutoff.”

## Q6. AP 是什么？为什么 Recall 提高不代表模型排序变好？

**中文理解：** 本项目调用 sklearn 的 average_precision_score：AP = Σ(ΔRecall × Precision)，即按召回率增量加权的 precision。它不是对 PR 曲线直接做梯形积分的面积，因此不能把定义未知的历史“PR-AUC”直接拿来比较。AP 与 ROC-AUC 使用连续分数，不依赖我们最终选定的一个分类阈值；AP 的解释依赖正例率，此测试集的 prevalence 参考值约为 0.2212。改阈值能改变 precision/recall，但不会改变同一组分数的 AP。

**English answer:** “Our AP is scikit-learn average precision: precision weighted by increments in recall, not trapezoidal PR-AUC. It summarizes continuous risk scores independently of the selected operating threshold. The positive prevalence is about 0.2212, and changing only the cutoff does not improve AP.”

## Q7. 置信区间包含哪些不确定性？

**中文理解：** 现有 1,000 次 bootstrap 对已固定的测试预测做重抽样。Paired 表示比较两模型或两阈值时抽同一批行，保留同一客户上的差异；stratified 分别在正负类内抽样，固定 1,327/4,673 的数量。XGBoost r=5 相对 0.5 的每千人成本差为 -46.17，95% 区间约 [-74.34,-18.00]。这只是给定模型、阈值与类别数量的条件区间；不覆盖重训练、参数/阈值搜索、正例率变化、潜在重复记录依赖和新地区/新时期的分布变化。

**English answer:** “The paired bootstrap resamples the same rows for each comparison, and stratification holds class counts fixed. XGBoost’s cost difference is −46.17 units per 1,000, with a conditional 95% interval of about [−74.34, −18.00]. This excludes model fitting, selection and population-shift uncertainty.”

## Q8. 分数等于阈值怎么办？为什么不能先四舍五入？

**中文理解：** 全组统一使用 score ≥ threshold，因此相等时判正类。阈值表考虑所有不同验证分数，重复分数作为整体移动；最低成本并列时选最大的阈值，优先减少提醒。保存 CSV 后要使用 float_precision='round_trip' 恢复浮点数，不能把报告中的 0.3150 代替完整阈值 0.31501567363739014。DT 的 predict 在概率 0.5 时也可能与统一规则不同，因此我们从概率显式构造分类。审计验证了这些边界情况。

**English answer:** “We classify a score equal to the cutoff as positive. Tied scores move together, and equal validation costs prefer the largest threshold. Decisions use full-precision round-trip values, not the rounded cutoffs shown on slides or the classifier’s default tie behavior.”

## Q9. 怎么避免数据泄漏？还能有哪些限制？

**中文理解：** row_id、原始 ID、标签不进入特征；每个 CV 训练折独立拟合编码及 LR 标准化；参数只由 fit-CV 选、阈值只由 validation 选，test 仅用于既定规则的评估。核验还做了一对一 row_id 对齐和真实标签检查。但不能声称绝对无泄漏：clean 数据保留 35 条首次出现以外的完全相同“特征＋标签”记录，15 条 test 的特征向量在 development 出现；相同特征不等于确认是同一客户，却可能形成跨分区依赖。代码与冻结时间也不能证明团队从未提前见过 test 结果。

**English answer:** “IDs and outcomes are excluded, preprocessing is fitted inside each training fold, and thresholds use validation only. We verified row-level alignment and disjoint IDs. However, repeated feature vectors and historical test exposure remain limitations, so we do not claim that all possible leakage or dependence has been ruled out.”

## Q10. 这些结果能直接用于银行放贷吗？

**中文理解：** 不能据本研究作这种结论。样本来自单一历史地区与时期，使用随机划分而非时间外或外部机构测试，且存在重复特征和历史 test 暴露限制。好的 AP 只表示排序能力，不证明某个 0.3 分数对应 30% 违约率；类别加权更可能改变概率尺度。虽然报告了 Brier，仍不能据单一总体数值宣布已校准。尚未进行分组错误率或公平性评估，包含性别、年龄等变量也需要治理审查。下一步应使用新的时间外/外部数据评估校准、分组表现及真实容量和成本，再讨论部署。

**English answer:** “This is a historical educational study, not evidence of deployment readiness. Ranking performance does not establish calibration, and subgroup fairness has not been evaluated. We need fresh temporal or external validation, calibration and subgroup checks, plus realistic costs and review capacity before considering operational use.”

## 回答时避免这四句话

- 不说 “Tuning made XGBoost the best model.”：测试 AP 没有改善，也没建立跨模型显著胜负。
- 不说 “We chose 0.315 because it worked best on the test set.”：阈值来自 validation。
- 不说 “We saved the bank 7.52% of its money.”：下降的是假设成本，不是实际利润或损失。
- 不说 “A score of 0.3 means a 30% default probability.”：尚未验证校准，类别权重也会改变分数尺度。

来源：[完整小组 QA](Group5_QA.md)、[最终比较表](model_comparison.csv)、[XGBoost 冻结配置](../results/xgboost/protocol_frozen.json)。
