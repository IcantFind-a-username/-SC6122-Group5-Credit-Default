# Group 5 答辩问答：22 个重点问题

使用方式：先用英文短答给出结论，再按追问补充中文理解中的证据。下列数值来自最终核验工件；展示时允许四舍五入，实际分类始终使用完整精度。LR* 专指事后可复现补充实验。

| 角色 | 优先准备 | 共同接答 |
|---|---|---|
| Part 1：数据与 LR | Q1–Q6 | Q7、Q15、Q22 |
| Part 2：决策树与比较 | Q7–Q11 | Q2、Q3、Q13 |
| Part 3：随机森林与审计 | Q12–Q16 | Q3、Q19、Q21 |
| Part 4：XGBoost 与决策 | Q17–Q22 | Q8、Q10、Q15 |

## Q1. 数据是什么？清洗有没有根据结果挑选样本？

**中文理解：** 数据包含台湾信用卡客户的 30,000 条记录、23 个预测变量，2005 年 4–9 月的历史付款信息，以及二元违约标签。正例为 6,636 条，占 22.12%。原数据无缺失；EDUCATION 的 0/5/6 合并为 4，涉及 345 条；MARRIAGE 的 0 合并为 3，涉及 54 条。没有删除异常值、重复记录或任何行，也没有修改负还款状态码。整合时重新下载官方 UCI 数据，重放清洗后与现有 clean 文件在值、类型及顺序上完全一致；原始那次下载的字节并未保存。

**English answer:** “We use 30,000 historical Taiwan credit-card records with 23 predictors. Cleaning only consolidates undocumented education and marriage categories; no observations are removed. A fresh official-source replay reproduces the committed clean data exactly, although the original download bytes were not preserved.”

## Q2. 到底用了多少行训练？五折 CV 与 validation 有什么区别？

**中文理解：** 最初分层划分为 24,000 development、6,000 test；development 再分成 18,000 fit、6,000 validation。三者正例数依次为 3,982、1,327、1,327。只在 18,000 fit 内进行五折 CV，每折 14,400 行拟合、3,600 行评估，用于选超参数。最终模型用全部 18,000 fit 行重新拟合；6,000 validation 选阈值，没有再并入模型训练。所有四个可复现实验的实际 row_id 及 CV 折成员完全一致，随机种子为 42。

**English answer:** “The final fitting, validation and test sets contain 18,000, 6,000 and 6,000 rows. Five-fold CV runs only inside the 18,000 fitting rows, using 14,400 training and 3,600 held-out rows per fold. Final models use 18,000 rows, and validation selects thresholds without a later refit.”

## Q3. 你们如何防止数据泄漏？能保证绝对没有泄漏吗？

**中文理解：** row_id、原始 ID、标签不进入特征；每个 CV 训练折独立拟合编码及 LR 标准化；参数只由 fit-CV 选、阈值只由 validation 选，test 仅用于既定规则的评估。核验还做了一对一 row_id 对齐和真实标签检查。但不能声称绝对无泄漏：clean 数据保留 35 条首次出现以外的完全相同“特征＋标签”记录，15 条 test 的特征向量在 development 出现；相同特征不等于确认是同一客户，却可能形成跨分区依赖。代码与冻结时间也不能证明团队从未提前见过 test 结果。

**English answer:** “IDs and outcomes are excluded, preprocessing is fitted inside each training fold, and thresholds use validation only. We verified row-level alignment and disjoint IDs. However, repeated feature vectors and historical test exposure remain limitations, so we do not claim that all possible leakage or dependence has been ruled out.”

## Q4. 为什么不能只看 accuracy？你们如何处理类别不平衡？

**中文理解：** 测试集正例率为 22.1167%，全部预测不违约就能达到 77.8833% accuracy，但 recall 为 0。在 r=5 下，这种规则成本为 6,635。我们以 AP 作为 CV 选择指标，另报 ROC-AUC、precision、recall、F1、混淆计数和成本。没有对数据做 SMOTE 或重采样；RF 的选中配置对正类赋权 3，XGBoost 的 scale_pos_weight 为 3。LR* 的搜索包含 balanced，但最终选中无类别权重。训练权重不会改变真实测试集违约率。

**English answer:** “Always predicting no default already gives 77.88% test accuracy but misses every default. We therefore select by AP and report recall, precision, confusion counts and costs. Class weighting is searched where declared; we do not resample the dataset or alter test prevalence.”

## Q5. 为什么 LR 要标准化，树模型不用？类别编码会不会有泄漏？

**中文理解：** LR 使用 L2 正则化，数值量纲会影响惩罚和优化，因此将数值变量 StandardScaler 标准化。SEX、EDUCATION、MARRIAGE 使用完整 one-hot；树模型保留数值原尺度。编码器及 scaler 均放入 pipeline，在每一 CV 训练折中学习，避免提前利用 held-out 分布。LR* 选中 C=0.1、无类别权重。数值系数表示标准化后的关联；完整 one-hot 与相关账单变量也使单个系数难以独立解释。

**English answer:** “Scaling matters for regularized logistic regression because feature units affect the penalty and optimization. Tree models retain numeric scales. Category encoding and logistic scaling are learned within each training fold through pipelines, and coefficients are interpreted as regularized associations rather than causal effects.”

## Q6. 原始 LR 结果为什么没有直接纳入？现在的 LR 是补出来的吗？

**中文理解：** 原始 LR 的若干汇总 CSV 被保留，但所有可用分支及历史中的 notebook 为空，缺少可验证的模型、逐行预测和完整训练过程，连其中“PR-AUC”的定义也无法确认。因此原始 CSV 不进入已核验的排名表。当前 LR* 是在已有团队测试结果可见后完成的、单独记录的事后可复现补充实验；它按预先写入脚本的搜索规则运行，以同一 fit-CV 和 validation 选参数与阈值。测试 AP 为 baseline 0.4970、tuned 0.4967，不能把它说成恢复了原始实验或获得了全新未见测试集。

**English answer:** “The original logistic summaries lack enough provenance to verify their training process or PR-AUC definition. We preserve them but exclude them from the verified comparison. LR* is an explicitly labelled post-hoc reproducibility supplement on the historic holdout, not a recovered original run or a new unseen-test result.”

## Q7. 四个模型的调参比较公平吗？

**中文理解：** 相同数据成员、CV 折、正类定义、mean-CV-AP 目标和分类规则提高了可比性。CV 均按平均 AP 最大选择，完全同分时取最小候选编号。但搜索预算不相同：DT 穷举 21 个配置，RF/XGBoost 各为 baseline 加 23 个固定种子的随机候选，LR* 穷举 12 个配置。不能将结果表述为相同计算预算下的算法普遍胜负，也不能忽略 LR* 的事后证据边界。所有测试图只用于描述，不继续驱动搜索。

**English answer:** “The models share exact splits, CV folds, evaluation definitions and the mean-CV-AP objective. Their search budgets differ: 21 tree, 24 forest, 24 XGBoost and 12 logistic configurations. This supports a controlled empirical comparison, but not a claim of equal computational budgets or universal algorithm superiority.”

## Q8. AP 到底是什么？是不是 PR 曲线下面积？

**中文理解：** 本项目调用 sklearn 的 average_precision_score：AP = Σ(ΔRecall × Precision)，即按召回率增量加权的 precision。它不是对 PR 曲线直接做梯形积分的面积，因此不能把定义未知的历史“PR-AUC”直接拿来比较。AP 与 ROC-AUC 使用连续分数，不依赖我们最终选定的一个分类阈值；AP 的解释依赖正例率，此测试集的 prevalence 参考值约为 0.2212。改阈值能改变 precision/recall，但不会改变同一组分数的 AP。

**English answer:** “Our AP is scikit-learn average precision: precision weighted by increments in recall, not trapezoidal PR-AUC. It summarizes continuous risk scores independently of the selected operating threshold. The positive prevalence is about 0.2212, and changing only the cutoff does not improve AP.”

## Q9. 什么证据说明原始决策树过拟合？没有 depth cap 的 tuned 树为什么更好？

**中文理解：** baseline 是不限深度、叶节点至少 1 条记录的树，平均 CV 训练折 AP 约 1.0000，held-out CV AP 只有 0.2970。选中模型同样没有显式深度上限，但 min_samples_leaf=100，限制每个叶节点的样本量，CV AP 为 0.5307。测试 AP 从 0.2843 上升到 0.5221；这些测试数用于确认最终结果，不是选择叶大小的依据。“不限深度”不意味着“没有正则化”。

**English answer:** “The baseline tree has almost perfect training-fold AP but only 0.2970 held-out CV AP. Requiring at least 100 samples per leaf raises CV AP to 0.5307 and test AP from 0.2843 to 0.5221. Minimum leaf size regularizes the tree even without an explicit depth cap.”

## Q10. XGBoost baseline 的测试 AP 最高，为什么不直接宣布它最好？

**中文理解：** 展示的测试点估计中，XGBoost baseline AP=0.5544，tuned XGBoost=0.5516，tuned RF=0.5508。tuned 指按照预定 CV 规则选出的配置，不保证在另一个样本上一定更优。XGBoost tuned-minus-baseline AP 差为 -0.0028，条件 bootstrap 95% 区间约 [-0.0106, 0.0054]，包含 0。测试后再以最高值更换模型会形成新的选择步骤；RF 与 XGBoost 之间也没有由这组区间直接建立显著胜负。

**English answer:** “Baseline XGBoost has the highest displayed AP point estimate, but tuning was selected by CV, not test performance. Its tuned-minus-baseline AP interval includes zero. We report that outcome honestly and do not start another selection round or claim a statistically established winner between RF and XGBoost.”

## Q11. 决策树提供了什么可解释性？能说拖欠导致违约吗？

**中文理解：** 路径可以显示一个预测是如何产生的。例如选中树的根节点是 PAY_0 ≤ 1.5，在 fit 样本中左右节点的违约比例约为 16.51% 和 70.13%。这说明该历史样本中存在较强的预测关联，不等于因果效应。选中树有 134 个叶、深度 18，因此适合展示少量代表性路径，不能把整个模型描述为只有几条规则；节点比例也不是已验证校准的个人违约概率。

**English answer:** “The tree exposes explicit decision paths. Its root separates recent repayment status, with fitting-sample default rates of about 16.51% and 70.13% in the two branches. These are descriptive associations, not causal effects, and the full selected tree remains substantial at 134 leaves.”

## Q12. Random Forest 的作用是什么？选中的配置是什么？

**中文理解：** RF 对多棵利用样本及特征随机性的树进行平均，减轻对单一划分的依赖，但不保证完全消除过拟合。选中配置为 500 棵树、max_depth=8、min_samples_split=5、min_samples_leaf=2、max_features=0.5、class_weight={0:1,1:3}。测试 AP 从 baseline 的 0.5312 增至 0.5508；阈值 0.5 下 recall 从 38.06% 增至 52.00%，同时 FP 从 279 增至 573。权重对学习和分数尺度有影响，不能直接当作成本阈值。

**English answer:** “Random Forest averages many randomized trees and reduces dependence on one partition. Our selected model uses 500 depth-eight trees with positive-class weight three. Test AP improves from 0.5312 to 0.5508, while higher recall at 0.5 comes with more false positives.”

## Q13. Feature importance 能说明什么？为什么使用 validation permutation importance？

**中文理解：** 在 validation 上置换一个变量，再看 AP 下降多少，衡量的是已拟合模型对该变量的预测依赖。RF 中 PAY_0 的平均 AP 下降约 0.1971，明显高于其他单个变量。相比单纯 Gini importance，这种指标直接对应我们的 AP 目标；但相关特征可以互相替代，置换还可能产生不真实的组合，不能据此判断因果、独立贡献或公平性。图中的误差棒是五次置换的标准差，不是置信区间。

**English answer:** “Permutation importance measures the drop in validation AP when a feature is shuffled. It describes predictive reliance, not causality. Correlated features can substitute for one another, and permutation can create unrealistic combinations; the error bars show variation across five shuffles, not confidence intervals.”

## Q14. RF 在 0.5 和 r=5 下的代表性错误样本相同，是不是导出错了？

**中文理解：** 不一定。case 文件挑的是分数最低的 FN 与分数最高的 FP；降低阈值后，这些最极端错误可能仍属于同一错误组。真正要检查的是各文件是否满足各自阈值的分组条件。已按完整精度分数、真实标签和 row_id 重新核验，两份代表性案例与总体分组均正确。RF 在 0.5 下 FN=637、FP=573；在验证选定的 0.32288101060928226 下 FN=304、FP=1,884，说明整体分组确实发生变化。

**English answer:** “The most confident errors can remain identical when the cutoff changes: the lowest-scoring defaults and highest-scoring non-defaults remain errors. We verified each case against its own threshold. Overall RF counts change from 637 FN and 573 FP to 304 FN and 1,884 FP, so identical extreme examples do not indicate a faulty export.”

## Q15. SHA256 不一致是否说明用了不同的数据？模型重放也要逐位一样吗？

**中文理解：** SHA256 对字节敏感，Windows 的 CRLF 与 LF 换行会产生不同哈希，即使解析后的表完全相同。RF 的训练/测试来源及部分文本元数据哈希差异都能由精确的 CRLF 版本解释；还比对了 git 历史中的数据值、dtype、行列顺序和成员。保存模型的哈希与协议一致。XGBoost 在当前平台重放概率最多相差 5.96×10⁻⁸；审计允许 10⁻⁷ 的绝对误差，但额外要求所有冻结阈值下的分类完全相同，报告继续使用原始保存分数。

**English answer:** “A byte-hash difference can come from LF versus CRLF line endings. We verified the exact newline variants and identical parsed values, types and order. Model hashes reconcile; XGBoost shows only float32-scale replay drift, with identical frozen decisions and original saved scores retained for reporting.”

## Q16. RF 曾重新生成冻结文件，这会不会破坏实验可信度？

**中文理解：** git 中能看到较早的 RF 运行 3da46a6，以及后来为统一 sklearn 1.8.0 环境进行的再生成 421b0e1。时间戳、软件版本和模型文件哈希发生改变；当前元数据相符，test prediction CSV 的历史内容没有改变。应该公开这段沿革，不重写旧协议以制造“从未重跑”的印象，也不把较晚冻结时间理解为首次见到 test。审计确认当前工件可复现，不能独立证明团队在仓库之外的所有操作。

**English answer:** “The repository records an earlier RF run and a later environment regeneration. We preserve that history: versions, timestamps and model hashes changed, while stored test predictions remained unchanged. Current artifacts reconcile, but the later freeze does not establish that the test set was newly unseen.”

## Q17. 超参数和阈值分别在哪里选？为什么不对 DT 也找一个更低成本的阈值？

**中文理解：** 超参数由 fit 内五折 mean AP 选；LR*、RF、XGBoost 的阈值由独立 validation 的 FP+rFN 最小值选，r∈{1,3,5,10}。测试时使用原样阈值。DT 历史实验仅定义了固定 0.5 策略，看到 test 结果后不能补出一个“历史冻结”的 DT 成本策略。若未来需要完整政策比较，应先制定新协议，再在新的可用验证与独立评估数据上执行。

**English answer:** “Hyperparameters use fitting-fold CV; cost thresholds use validation only and are applied unchanged to test. The historical tree experiment specifies only a 0.5 cutoff. We do not invent an additional frozen tree policy after seeing the results.”

## Q18. 分数等于阈值怎么算？四舍五入会不会改变结果？

**中文理解：** 全组统一使用 score ≥ threshold，因此相等时判正类。阈值表考虑所有不同验证分数，重复分数作为整体移动；最低成本并列时选最大的阈值，优先减少提醒。保存 CSV 后要使用 float_precision='round_trip' 恢复浮点数，不能把报告中的 0.3150 代替完整阈值 0.31501567363739014。DT 的 predict 在概率 0.5 时也可能与统一规则不同，因此我们从概率显式构造分类。审计验证了这些边界情况。

**English answer:** “We classify a score equal to the cutoff as positive. Tied scores move together, and equal validation costs prefer the largest threshold. Decisions use full-precision round-trip values, not the rounded cutoffs shown on slides or the classifier’s default tie behavior.”

## Q19. 降低阈值有什么真实代价？RF 与 XGBoost 谁的成本更低？

**中文理解：** 对同一个 tuned XGBoost，从 0.5 改为验证选定的 r=5 阈值 0.31501567363739014，FN 从 599 降至 232，FP 从 690 增至 2,248；假设成本从 3,685 降至 3,408。Recall 从 54.86% 升到 82.52%，precision 从 51.34% 降至 32.76%，提醒比例升至 55.72%。RF 的对应成本为 3,404、提醒比例 48.45%、recall 77.09%；它只比 XGBoost 少 4 个假设单位，不能支持强烈的成本优越性结论。AP 与 ROC-AUC 都不因单纯改阈值而提高。

**English answer:** “Lowering the XGBoost cutoff reduces missed defaults but increases false positives and flags 55.72% of accounts. Its r=5 cost falls from 3,685 to 3,408. RF costs 3,404 with fewer alerts and lower recall; a four-unit difference does not justify a strong superiority claim.”

## Q20. 为什么用 FP+5FN？银行只能审查 10% 客户怎么办？

**中文理解：** r=5 是预先声明的假设情景之一，不是从真实贷款损失估计的金额。我们还展示 r=1/3/10 的敏感性；没有贷款敞口、违约损失率、干预效果及审查成本，不能称为实际利润提升。若存在 10% 审查容量，现有高提醒率策略显然不满足；应先把容量写入政策目标，再在 validation 上评估排序截断、并列分数处理及成本，最后用新的独立数据检验。不能在看过 test 后临时调阈值使结果好看，也不能假定未校准分数适用理论阈值 1/(1+r)。

**English answer:** “The cost ratio is a hypothetical sensitivity assumption, not measured monetary loss. A 10% review limit would require a separately validated capacity-constrained policy, including tie handling. We would not adjust the cutoff on the existing test set or assume that uncalibrated scores justify a theoretical cost cutoff.”

## Q21. Bootstrap 区间到底覆盖哪些不确定性？为什么要 paired、stratified？

**中文理解：** 现有 1,000 次 bootstrap 对已固定的测试预测做重抽样。Paired 表示比较两模型或两阈值时抽同一批行，保留同一客户上的差异；stratified 分别在正负类内抽样，固定 1,327/4,673 的数量。XGBoost r=5 相对 0.5 的每千人成本差为 -46.17，95% 区间约 [-74.34,-18.00]。这只是给定模型、阈值与类别数量的条件区间；不覆盖重训练、参数/阈值搜索、正例率变化、潜在重复记录依赖和新地区/新时期的分布变化。

**English answer:** “The paired bootstrap resamples the same rows for each comparison, and stratification holds class counts fixed. XGBoost’s cost difference is −46.17 units per 1,000, with a conditional 95% interval of about [−74.34, −18.00]. This excludes model fitting, selection and population-shift uncertainty.”

## Q22. 这些模型能直接用于今天的放贷吗？校准和公平性做了吗？

**中文理解：** 不能据本研究作这种结论。样本来自单一历史地区与时期，使用随机划分而非时间外或外部机构测试，且存在重复特征和历史 test 暴露限制。好的 AP 只表示排序能力，不证明某个 0.3 分数对应 30% 违约率；类别加权更可能改变概率尺度。虽然报告了 Brier，仍不能据单一总体数值宣布已校准。尚未进行分组错误率或公平性评估，包含性别、年龄等变量也需要治理审查。下一步应使用新的时间外/外部数据评估校准、分组表现及真实容量和成本，再讨论部署。

**English answer:** “This is a historical educational study, not evidence of deployment readiness. Ranking performance does not establish calibration, and subgroup fairness has not been evaluated. We need fresh temporal or external validation, calibration and subgroup checks, plus realistic costs and review capacity before considering operational use.”

## 证据定位

- [统一指标与政策表](../results/final/model_comparison.csv)：逐模型、partition、baseline/tuned 及原有阈值政策；LR* 带独立证据标签。
- [成本敏感性表](../results/final/cost_comparison.csv)：r=1/3/5/10 的 FP、FN 与假设成本。
- [审计说明](../integration/AUDIT_FINDINGS.md)与[审计明细](../results/final/audit.json)：数据身份、实际划分、浮点精度、模型重放及历史限制。
- [官方数据重放](../results/final/source_audit.json)：来源、清洗与重复记录证据。
- [RF 区间](../results/rf/bootstrap_intervals.csv)、[XGBoost 区间](../results/xgboost/bootstrap_intervals.csv)、[LR* 区间](../results/logistic_supplement/bootstrap_intervals.csv)：条件 paired bootstrap，不能扩大为完整建模不确定性。
- [报告模板](report_template.tex)：与报告、图表及演讲口径保持一致。答辩时若被问到尚未验证的结论，直接说明证据边界，不补造实验、身份或历史记录。
