# 从理解项目到讲清第四部分

Xu Yiqun · G2509092H · SC6122 Group 5

这是个人学习与答辩准备材料，不是要提交的七页小组报告。你已有 ML 基础，重点是把这个项目的实际流程和结果连起来。先读第 1–4 节，再练第 5–8 节；不用先背完整源码或所有参数。

## 1. 整组到底在研究什么？

银行有一批信用卡客户，知道他们过去的还款状态、账单、还款金额、额度和基本资料。我们想用这些信息判断：哪些客户更可能在接下来的目标月份违约？

输入 X 是 23 个特征；标签 y=1 表示违约，y=0 表示未违约。这是有标签的二分类问题，不是检测信用卡盗刷，也不是证明某个因素导致违约。

项目实际上回答两个不同的问题：

- **谁更危险？** 模型给每人一个分数，考察违约客户能否排在前面。这是排序能力，用 AP 和 ROC-AUC 衡量。
- **决定关注谁？** 在分数上设一个阈值，把一部分客户标记出来。考察漏报、误报和审查负担。这是决策规则，用 Precision、Recall 和假设成本衡量。

你的第四部分最重要的工作，是把这两个问题分开。即使同一模型的排序没有变，调整阈值也能改变业务取舍。

### 四个人的内容如何接起来

| 成员 | 各自主要负责 | 这一部分给整组提供什么 |
|---|---|---|
| Lei Peng | 数据检查、预处理、逻辑回归 | 确认输入与标签，建立线性参照 |
| Zhang Hanyu | 决策树、调参、规则和过拟合 | 展示复杂度控制以及可读的判断规则 |
| Zhou Xinzhe | 随机森林、调参、重要性和误判 | 用集成树提高稳定性，并分析依赖和错误 |
| Xu Yiqun | XGBoost、调参、阈值取舍 | 区分排序效果与行动成本，完成总结 |

数据划分、评价规则、最终整合、检查和排练是共同工作。25% 的贡献分配与老师“个人评分占 75%”是两个不同概念；后者意味着你仍需能解释自己负责的内容。

### 全组结论，先用这三句理解

1. 数据里有可用于预测的信号；正则化后的决策树明显好于其不受约束的基准。
2. RF 和 XGBoost 的选中模型排序结果接近，没有充分依据宣布一个普遍优胜者。
3. 阈值降低可以抓住更多违约客户，但会误报更多正常客户；是否值得取决于成本假设和审查容量。

一句英文介绍项目：

“We compare four models for credit-card default prediction, then examine the trade-off between ranking performance, interpretability and decision cost.”

<!-- pagebreak -->

## 2. 数据怎么用，为什么要分这么多份？

真实数据来自 UCI：30,000 名台湾信用卡客户，23 个预测变量，6,636 条违约记录，违约率 22.12%。历史还款变量覆盖 2005 年 4–9 月，金额单位是新台币。这是旧时期、单一地区的历史样本。

### 把 CV、validation 和 test 的职责分清

| 数据部分 | 人数 | 做什么 | 不能做什么 |
|---|---|---|---|
| Fitting | 18,000 | 用内部五折 CV 选参数，然后拟合最终模型 | 不能把内部 CV 当作最终独立测试 |
| Validation | 6,000 | 给选定模型选择成本阈值 | 不并回最终模型训练 |
| Test | 6,000 | 对已经确定的模型和阈值做报告中的评估 | 不拿来继续选参数或阈值 |

仓库里的 train.csv 有 24,000 行：它是 development 数据，还会拆成 18,000 fitting 和 6,000 validation。**不能因为文件叫 train，就说最终模型训练用了 24,000 人。**

五折 CV 只发生在 18,000 人内部：每次用 14,400 人拟合、3,600 人评价，轮流做五次。每个参数配置得到五个 AP，取平均来选配置。这个 CV 中的 holdout，与外面的 6,000 validation 不是同一批数据。

可以把流程读成两条线：

- 18,000 fitting → 内部五折 CV 比较参数 → 用全部 18,000 人拟合选中模型。
- 固定该模型 → 6,000 validation 选阈值 → 固定阈值 → 6,000 test 报结果。

### 预处理具体做了什么？

原数据无缺失。EDUCATION 的 0/5/6 合并为 4，MARRIAGE 的 0 合并为 3；这些是固定类别映射。没有删行、做 SMOTE 或删除重复记录。

SEX、EDUCATION、MARRIAGE 做 one-hot；编码器在每个 CV 训练折内拟合。LR 还在每个训练折内做标准化，树模型保留数值原尺度。row_id 和原始 ID 只是对齐记录的编号，绝不作为特征。

为什么要把预处理放进 pipeline？因为不能先用所有数据计算均值、类别或其他统计，再声称后面的 held-out 数据没参与训练。这里的固定清洗映射和需要从数据学习的预处理统计要区别开。

### 为什么不能只报 accuracy？

测试集 6,000 人中有 1,327 人违约。全部预测未违约，也能得到约 77.88% accuracy，但一个违约客户都找不到。所以我们用 AP 选模型，并同时报告 Recall、Precision 和成本。

需要承认的边界：虽然不同分区的 row_id 互斥，15 条测试特征向量在 development 中也出现过，可能形成依赖。另外，历史测试结果已经存在；此次整合不是一份全新未见的外部测试。

<!-- pagebreak -->

## 3. 你的第四部分做了什么实验？

### XGBoost 与另外三个模型的区别

LR 用一个线性函数加 sigmoid 给分数；决策树通过条件分支给分数；随机森林训练许多随机化的树，再综合它们的结果。XGBoost 也是多棵树，但它一轮一轮地加树，让新树沿损失函数的改进方向修正已有预测。

“后一棵树纠正前面的错误”是方便理解的说法。更准确地说，模型根据当前损失的梯度、二阶信息和正则项构建新树；不是只把分错的样本挑出来重新训练。

此处实现的训练目标是 binary:logistic，内部 eval_metric 是 logloss；**外层选参数的指标却是五折 mean AP**。训练损失和选模型的评价指标可以不同。

### 第一步：保留一个基准配置，再做调参

共比较 24 个配置：一个预先定义的 baseline，加 23 个固定随机种子的候选。这里的 baseline 是项目定义的参照，不等于 XGBoost 的所有库默认参数。

| 关键参数 | Baseline | CV 选中配置 | 直观含义 |
|---|---|---|---|
| n_estimators | 200 | 150 | 加多少轮树 |
| max_depth | 3 | 4 | 每棵树最多能分多复杂 |
| learning_rate | 0.1 | 0.03 | 每轮树的贡献幅度 |
| min_child_weight | 1 | 10 | 限制过于轻的子节点；不是最少十个样本 |
| scale_pos_weight | 1 | 3 | 训练时增加正类样本的损失权重 |

选中配置的 subsample、colsample_bytree 都是 1，reg_lambda=1、reg_alpha=0。没必要先把这四个背熟；优先记住 150 棵树、深度 4、学习率 0.03，以及训练权重 3 与成本比 5 不是一回事。

### 第二步：解释为什么选中了它，但不能说测试变好了

- Baseline 的 mean CV AP 约为 0.5598，选中配置约为 0.5620。因此，按预先确定的 CV 规则选择后者是有依据的。
- 换到测试集，AP 却从 0.5544 变成 0.5516，略低。调参只是在有限候选和 CV 样本中选择，并不保证另一个样本上必然更优。
- 固定预测的 bootstrap 差值区间包含 0，所以没有明确证据证明调参提升了测试排序。也不能由此证明两者完全相同。

正确说法是 **CV-selected model**，而不是无条件的 **better model**。我们保留并报告这个结果，不根据已经看到的测试结果再开一轮搜索。

### 第三步：固定选中模型，研究阈值

到这一步没有再训练另一套模型。使用同一组分数，比较固定阈值 0.5 与在 validation 上选出的成本阈值；测试时原样应用。第四部分的价值主要体现在这里。

<!-- pagebreak -->

## 4. 把阈值、误报和成本真正算明白

假设一个客户得分为 0.40。这只是说明规则的例子，不是新增实验结果：

- 阈值 0.5：0.40 不够高，预测未违约。
- 阈值约 0.315：0.40 达标，预测违约，需要关注。

客户的分数没变，客户之间的排序也没变。我们只是扩大了被标记的范围。若这个人确实违约，就少一个 FN；若他并未违约，就多一个 FP。

### 四个格子的意思

| 真实情况 | 预测未违约 | 预测违约 |
|---|---|---|
| 实际未违约 | TN：放过正常客户 | FP：误报正常客户 |
| 实际违约 | FN：漏掉违约客户 | TP：识别到违约客户 |

Recall = TP / (TP + FN)：在真正违约的人里面找到了多少。Precision = TP / (TP + FP)：在你标记的人里面，真正违约的比例是多少。

### 我们的实际结果：同一个 tuned XGBoost

| 测试集 6,000 人 | 阈值 0.5 | 验证集选定阈值约 0.315 |
|---|---|---|
| TP：抓到违约 | 728 | 1,095 |
| FN：漏判违约 | 599 | 232 |
| FP：误报正常客户 | 690 | 2,248 |
| TN：未被误报的正常客户 | 3,983 | 2,425 |
| Recall | 54.86% | 82.52% |
| Precision | 51.34% | 32.76% |
| 告警比例 | 23.63% | 55.72% |
| 假设成本 FP + 5 × FN | 3,685 | 3,408 |

### 7.52% 是怎么来的？

假设误报一次花 1 单位，漏报一次花 5 单位。

旧成本 = 690 + 5 × 599 = 3,685。
新成本 = 2,248 + 5 × 232 = 3,408。
下降比例 = (3,685 − 3,408) / 3,685 ≈ 7.52%。

另一种算账方法更容易解释：少漏掉 367 人，按每人 5 单位节省 1,835；但多误报 1,558 人，多花 1,558。净减少 277 单位。**在这个成本假设下，收益超过了代价。**

这不是银行真实省了 7.52% 的钱：数据没有真实贷款敞口、损失率和干预效果。标记超过一半客户是否可执行，也要看审查容量。

<!-- pagebreak -->

## 5. 你在台上第 10–12 页分别说什么？

不要把每个数字都念出来。每页先说它要回答的问题，再说一个结果，最后说结论的边界。

### 第 10 页：XGBoost 调参有没有帮助？

你要讲：用相同的 fitting-CV 规则比较 24 个配置；CV 选中的配置在测试 AP 上没有改进，所以不宣称调参成功提升排序。

一个简短英文版本：

“We compared 24 XGBoost configurations using five-fold CV. The selected model had slightly lower test AP than the baseline: 0.5516 versus 0.5544. So we do not claim a ranking improvement. We then ask a different question: can a validation-selected threshold reduce the stated decision cost?”

理解检查：老师问“为什么不直接用测试 AP 最高的模型”，你要回答这是看过测试后新增的选择步骤，不能把 test 再当作调参集。

### 第 11 页：降低阈值，具体换来了什么？

你要讲：固定同一个模型，validation 在 r=5 下选出约 0.315；测试 FN 减少、FP 增加，假设成本下降 7.52%，但 55.72% 客户会被标记。

一个简短英文版本：

“With a hypothetical five-to-one cost ratio, validation selected a threshold of about 0.315. Missed defaults fell from 599 to 232, while false positives rose from 690 to 2,248. The hypothetical cost fell by 7.52%, but 55.72% of clients were flagged. This is a decision trade-off, not a change in ranking performance.”

理解检查：多抓到违约不等于没有代价。Recall 提高的同时，Precision 降低，审查数量也显著增加。

### 第 12 页：如何收尾？

你要讲：排序、解释、业务行动是三个不同层次；结果还不能支持直接部署。说完谢谢，停在结束页接受提问。

一个简短英文版本：

“Our main conclusion is that ranking and action policy need separate evaluation. A lower threshold can reduce the assumed cost, but it creates more reviews. Before operational use, we would need realistic costs, review-capacity limits and fresh validation data. Thank you. We welcome your questions.”

这些是帮助理解的缩短版，不强制替换 PPT 中较完整的备注讲稿。你可以按自己的语速复述；不要为了凑时间增加没有证据的说法。

### Backup 怎么用？

第 13 页解释 AP 等指标，第 14 页解释成本与条件置信区间，第 15 页解释数据和证据限制，第 16 页解释来源和分工。它们是问到才打开的材料，不是接着讲完的四页正文。你最可能用到第 14 页。

<!-- pagebreak -->

## 6. 最优先练的四个答辩问题

### Q1. What did your section investigate?

中文思路：不要只说“我用了 XGBoost”。说清楚两步：先按 CV 规则选配置，再固定模型比较阈值对错误和成本的影响。

“My assigned section is XGBoost and threshold trade-offs. The analysis compares baseline and CV-selected XGBoost, then evaluates how a validation-selected threshold changes missed defaults, false alarms and hypothetical cost.”

如果问的是你个人的实际实现贡献，而不只是部分内容，参见第 9 节；不要把 AI 辅助完成的操作说成自己独立完成。

### Q2. Why did tuning make the test AP slightly worse?

中文思路：它在 CV 上略好，所以被选中；CV 和 test 是不同样本。调参不是“保证改进”的开关。一个诚实的负结果仍然是结果。

“The selected configuration had higher mean CV AP, but that does not guarantee higher test AP. On test, AP changed from 0.5544 to 0.5516. We report the result honestly and do not claim that tuning improved ranking.”

被追问“是不是过拟合”：可能涉及 CV 选择噪声和泛化差异，但不能凭这么小的测试差值就断定具体原因。不要擅自声称已证明过拟合。

### Q3. Where did the 0.315 threshold come from?

中文思路：不是拍脑袋，不是测试集挑出来，也不是必然等于 1/(1+5)。是选定模型在 validation 上的分数与标签，按 FP+5FN 最小来选的。

“The threshold was selected on the separate validation set by minimizing FP plus five times FN. We then applied it unchanged to the test set. Test outcomes were not used to choose the cutoff.”

补充：搜索按不同分数对应的决策集合处理，同分一起移动；成本并列时选较大的阈值，减少告警。计算用完整阈值 0.31501567363739014；展示才写 0.3150。

### Q4. Why is lower cost possible with many more false positives?

中文思路：老师在考你是否真正理解成本权重。把第 4 节的“少漏 367、多误报 1,558”算出来即可。

“We avoid 367 missed defaults but add 1,558 false positives. At five units per missed default, the benefit is 1,835 units, larger than the extra 1,558 units. Net cost falls by 277 units under that assumption.”

如果老师说“那就全部预测违约”：也要算成本。全部预测违约时 FP=4,673、FN=0，成本为 4,673，比当前策略的 3,408 更高；Recall 达到 100% 并不代表成本最好。

<!-- pagebreak -->

## 7. 再练四个概念问题

### Q5. Why does Recall improve while AP stays unchanged?

中文思路：Recall 看某一个阈值的结果；AP 看连续分数形成的排序表现。相同模型只移动阈值，没有改分数。

“Recall measures one operating point, while AP summarizes the continuous scores. Lowering the cutoff changes which clients are flagged, but not their scores or ordering. So Recall can rise without any AP improvement.”

别把 AP=0.55 说成“准确率 55%”。AP 是按召回增量加权的 Precision，不是 accuracy，也不是我们随意对 PR 曲线做梯形积分。ROC-AUC 是另一种基于正负样本分数排序的指标。

### Q6. Why assume false negatives cost five times more?

中文思路：这是敏感性分析场景，不是从数据估出来的真实贷款损失。还预先考虑 r=1、3、10。不能用 7.52% 包装成真实利润提升。

“Five-to-one is a hypothetical sensitivity scenario, not an estimate of actual bank losses. We also considered other predeclared ratios. Real costs would require exposure, loss severity, review cost and intervention information that this dataset does not provide.”

### Q7. Are the comparisons fair? Is there any leakage?

中文思路：相同成员划分、CV 折、正类与 AP 定义，提高可比性；但预算和证据历史不同。明确预处理在哪拟合，同时承认保留重复特征和历史测试暴露的限制。

“The models share splits, CV folds and metric definitions, with preprocessing fitted inside training folds. Search budgets differ, and repeated feature vectors and historical test exposure remain limitations. This is a traceable comparison, not proof that every possible dependence has been eliminated.”

若追问 LR：原训练过程无法恢复，当前 LR* 是单独标记的事后补充实验，不能称为恢复了原实验或新的未见测试。

### Q8. Can the bank use this policy now?

中文思路：旧数据、随机切分、未验证校准、未评估群体公平性；而且要审查超过一半客户。先验证可执行性，再谈部署。

“Not on this evidence alone. This is a historical educational study, and the policy flags more than half the clients. We would need fresh temporal or external validation, calibration and subgroup checks, plus realistic costs and review-capacity constraints.”

如果只能审查 10% 客户：先把容量写入目标，再用合适验证数据制定有并列处理的策略，最后在新的评估数据上检验；不能临时在旧 test 上挑出最好看的阈值。

<!-- pagebreak -->

## 8. 有 ML 基础的你可以再准备这些追问

### 训练权重 3 和成本比 5，为什么不一样？

scale_pos_weight=3 参与模型训练，改变学习目标，可能改变分数甚至排序。r=5 用于训练完成后的政策选择，只决定如何评价 FP 与 FN 的代价。两者在不同阶段发挥作用，没有必须相等的规则。

“Class weight affects learning. The cost ratio defines the decision objective after training. They serve different purposes and do not have to be equal.”

### 为什么树更深了，却还在说控制复杂度？

选中 XGBoost 的 max_depth 从 3 变 4，但树数从 200 变 150、学习率从 0.1 变 0.03，min_child_weight 从 1 变 10。复杂度由多个参数共同影响，不能只看深度；这些是 CV 选出来的组合，而不是根据测试结果逐个手工解释成最优。

min_child_weight 约束子节点的二阶导数统计量之和，不等于决策树 min_samples_leaf 那样直接约束样本个数。

### 置信区间是什么意思？

把已经保存的测试预测反复抽样，观察某个差值在这些重抽样里怎么变。Paired 表示两组预测使用同一批抽样行；stratified 表示正负类分别抽样，固定类别数量。

它不包含重训练、重选参数、重选阈值以及新地区/新时期的变化。XGBoost 的 AP 差值区间约为 [−0.0106, 0.0054]，包含 0；成本差值每千人约 −46.17，条件区间约为 [−74.34, −18.00]。这两个区间估计的量不同，不能混用，也不能用前者证明 RF 与 XGBoost 之间的显著差异。

“Our intervals resample fixed predictions. They are conditional on the fitted models and selected thresholds, so they exclude fitting, selection and population-shift uncertainty.”

### 什么叫校准？

校准关心“一群分数约 0.3 的人，是否真的约有 30% 违约”。排序好不保证分数就是可信的违约概率，尤其做过类别加权后。好 AP 或一个 Brier 数值，都不能独自证明已经校准。

### 特征重要性能说明原因吗？

把某个特征打乱后 AP 下降，说明模型依赖它做预测；不说明改变这个特征就会让同一个客户避免违约。相关变量可以互相替代，置换也可能产生不真实的组合。RF 的具体重要性和案例由 Zhou Xinzhe 主讲；你了解原则即可。

### 被问没做过的实验怎么办？

说清楚现有证据和缺口即可。不要临时猜一个数值，也不要把未来想做的实验说成已经做过。

“We did not evaluate that setting, so I would not claim a result. It would need a separately specified experiment and fresh evaluation data.”

<!-- pagebreak -->

## 9. 如何说明自己的工作，以及今晚怎样准备

### 分工范围和实际完成方式要分开说

项目中，第四部分完成了 XGBoost 的配置比较、验证集成本阈值选择、测试错误与成本比较及结果解释。按组内分工，这部分由你负责展示。

但你说实现和材料主要交给 AI 完成，目前还在理解阶段。因此不要照背“我独立编写并运行了全部实验”或“我亲自验证了所有结果”。当前材料已有 AI 辅助说明；若被问到个人实际贡献，按事实说明工具的使用与自己的学习、解释和展示范围。

一个符合你目前描述的说法是：

“My assigned section is XGBoost and threshold trade-offs. I used AI assistance for the implementation and preparation of the materials. I am preparing to explain the experimental protocol, results and limitations.”

完成实际复习或检查之后，才把你确实做过的工作加入回答。你无需声称自己发明了算法；能解释决策依据、复核一组算账并识别限制，就是有价值的理解。

### 先把这六件事做一遍

1. 不看材料，用中文说清“模型排序”和“阈值决策”的区别。
2. 画出 18,000 / 6,000 / 6,000，标出 CV 在哪里，阈值在哪里选。
3. 亲手算一遍 690+5×599 与 2,248+5×232。
4. 打开 PPT 第 10–12 页，对着图用自己的话讲；讲不通时回看本指南，而不是增加更难的英文。
5. 用英文回答第 6、7 节八个问题，每次先给一到两句直接答案。
6. 检查第 12 页怎么停下、第 14 页备份怎么打开，并和下一位/前一位确认交接。

### 三个自测题

- 阈值降低后，AP 为什么没变？若你回答“模型更重视违约了”，再区分一下训练权重与分类阈值。
- 如果 FP 变多，成本为什么还能下降？请不用“算法更好”这类笼统解释，而是直接算账。
- CV 选了 tuned，但测试 baseline 更好，为什么不立刻换？请说明 test 的职责。

这三个都能独立解释后，再去记忆参数和英文措辞。你应该能用中文解释英文答案中的每个关键术语。

### 文件定位：被追问时知道证据在哪

| 文件 | 能证明/查看什么 |
|---|---|
| results/xgboost/protocol_frozen.json | 24 个配置、选中参数、数据量和选型指标 |
| results/xgboost/cv_results.csv | Baseline 与选中配置的 CV AP |
| results/xgboost/validation_thresholds.csv | 验证集上的候选阈值及成本 |
| results/final/model_comparison.csv | 最终测试指标与混淆计数 |
| part4/experiment.py | fitting-CV 搜索、pipeline 和拟合流程 |
| part4/evaluation.py | score ≥ threshold、指标与成本公式 |

只查看文件或运行既有核验入口，不会提高模型分数；明天展示前也不需要重新搜索参数或改变阈值。现有数字足够支持一次诚实、完整的讨论。
