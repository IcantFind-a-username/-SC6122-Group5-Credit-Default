# Member 2: three-minute presentation content

## Slide 1 — Decision tree and complexity control (about 55 seconds)
Visual: figures/01_overfitting.png.
- Same supplied data and development/CV membership as Part 4.
- 21 combinations; select by five-fold Average Precision.
- Selected max_depth=unlimited (None), min_samples_leaf=100.
- CV AP: unrestricted 0.297; selected 0.531.

Speaker notes: My part focuses on the decision tree. It learns a sequence of conditions to divide customers into groups. An unrestricted tree can memorize training examples, so a strong training score does not necessarily mean it will work well on new customers. I tested maximum depth and minimum leaf size using the same cross-validation membership as Part Four. I selected the model using Average Precision. This figure fixes the minimum leaf size at one, so it isolates the effect of increasing depth. The final model was selected from the joint search over both parameters.

## Slide 2 — What the tree learned (about 55 seconds)
Visual: figures/02_tree_top_levels.png.
- First split: PAY_0 ≤ 1.5.
- Fit-data default share: left 16.5%; right 70.1%.
- Lower nodes add further conditions; displayed branches are truncated.
- Rules describe predictive associations, not causality.

Speaker notes: The tree is interpretable because we can follow the actual conditions it learned. Its first split uses PAY_0. The two branches contain customers with very different observed default rates in the fitting data. Later splits refine those groups using additional information. These proportions help explain the model, but they are not proof that a feature causes default. The figure shows only the upper levels; the dots represent further branches. Complete leaf rules and sample counts are included in my results.

## Slide 3 — Final test results and limitations (about 60 seconds)
Visual: figures/03_test_confusion.png; add a small two-row metric table.
- Selected tree: AP 0.522; ROC-AUC 0.754.
- Accuracy 81.7%; precision 65.8%; recall 35.7%.
- False negatives 853; false positives 246.
- Fixed threshold 0.5; threshold optimization is addressed in Part 4.

Speaker notes: After selecting the parameters, I froze both fitted models and evaluated them on the same six thousand test customers. The selected model achieved an AP of 0.522 and a ROC-AUC of 0.754. At the fixed threshold of zero point five, recall was 35.7%, so there were still 853 missed defaults. There were also 246 false alarms among normal customers. This shows why we need several metrics instead of accuracy alone. My conclusion is that complexity control helps the tree generalize, while the remaining false negatives make the threshold trade-off relevant to the next part of our project.

## 问答准备
Q：你做了什么？ A：接公共数据，训练和调参决策树，核对开发集划分，分析过拟合和实际规则，完成固定阈值最终测试。
Q：为什么 AP？ A：违约是少数类，AP 关注 precision–recall 表现，并与第四位选参标准一致。
Q：为什么不是把树越长越好？ A：过细规则会拟合训练样本中的偶然情况，训练分高但验证分低。
Q：为什么不用验证集一起重训？ A：为了与第四位实际使用的 18,000 人拟合方案对齐，避免混入训练规模差异。
Q：为什么不挑测试集上最好的参数？ A：那会让测试数据参与选择，失去独立评价意义。
Q：代码是自己手写算法吗？ A：采用 scikit-learn 的决策树实现；本部分工作是实验设计、参数搜索、评价和解释。

这份是可编辑展示文案，不是已排版的 PPT。根据实际语速排练并控制在约三分钟。
