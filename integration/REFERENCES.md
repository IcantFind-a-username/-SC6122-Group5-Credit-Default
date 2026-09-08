# Sources checked on 2026-09-07 (Singapore)

The September 7 entries below document the earlier four-reference version. The September 9 source-verification table documents the expanded seven-source version. The final APA 7 conversion is recorded at the end of this file; earlier numeric labels are historical verification identifiers, not current report citations.

- UCI primary dataset page: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients ; DOI https://doi.org/10.24432/C55S3H. Verified 30,000 observations, 23 features, positive default label, no missing values, Taiwan sample, April–September 2005 predictors, NT-dollar units and CC BY 4.0 license.
- scikit-learn official `average_precision_score`: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html . AP is recall-increment weighted precision, without trapezoidal interpolation. The production environment remains pinned to 1.8.0; the live stable documentation currently displays 1.9.0.
- Chen and Guestrin (2016), XGBoost: A Scalable Tree Boosting System, https://arxiv.org/abs/1603.02754 ; published DOI https://doi.org/10.1145/2939672.2939785. Verified authors/title and boosted-tree system scope.
- Model configuration, outcomes and rule interpretations in final materials cite this repository's frozen artifacts, not externally reported performance numbers.

Teacher Word/LaTeX templates and sample report/slides were not found in repository or filename searches under Documents, Downloads, NTU and Desktop. No teacher platform deadline or upload requirement has been independently verified. User-supplied explicit requirements govern the checklist.

## Additional verification using Consensus and Crossref

Checked on 2026-09-07 at the user's request. The four references in the final report are distinct source types; they are not four peer-reviewed papers.

| Report reference | Source type | Verification and supported use |
| --- | --- | --- |
| [1] Yeh (2009), Default of Credit Card Clients | Dataset citation | The UCI primary page supplies this citation and DOI `10.24432/C55S3H`. Supports data provenance, variables and license. This is not the DOI of the associated research paper. |
| [2] scikit-learn, average_precision_score | Official software documentation | The official documentation defines the AP calculation. It is not a journal paper. The documented experiment version remains 1.8.0. |
| [3] Chen and Guestrin (2016), XGBoost: A Scalable Tree Boosting System | Conference paper | Consensus search followed by record fetch confirms title, authors, 2016 and KDD proceedings. Crossref independently confirms DOI `10.1145/2939672.2939785`, authors, proceedings and pages 785–794. The previously checked author preprint supplies the full title and published DOI. |
| [4] Group 5 project repository (2026) | Project primary evidence | The Git remote and committed artifacts are the source for this group's experimental outcomes. This is not external peer review or independent replication. |

XGBoost verification links:
- [Fetched Consensus record](https://consensus.app/papers/xgboost-a-scalable-tree-boosting-system-chen-guestrin/9181a8aeb69a57b185bd063877d7a733/?utm_source=chatgpt)
- [Crossref publisher-deposited metadata](https://api.crossref.org/works/10.1145/2939672.2939785)
- [Published paper DOI](https://doi.org/10.1145/2939672.2939785)

The dataset's associated original paper was also authenticated as supplementary provenance (it is not an additional numbered citation in the current final report):

I-Cheng Yeh and Che-hui Lien (2009). “The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients.” *Expert Systems with Applications*, 36(2), 2473–2480. DOI: [10.1016/j.eswa.2007.12.020](https://doi.org/10.1016/j.eswa.2007.12.020).

- [Fetched Consensus record](https://consensus.app/papers/the-comparisons-of-data-mining-techniques-for-the-yeh-lien/aa697ed50f545f2aa4aed01813a846a1/?utm_source=chatgpt) confirms authors, 2009, journal, volume and pages. Its fetch response has no abstract; no claim of full-text review is made.
- [Crossref publisher-deposited metadata](https://api.crossref.org/works/10.1016/j.eswa.2007.12.020) independently confirms the exact title, full author names, March 2009 publication, volume 36, issue 2 and pages 2473–2480. The `2007` embedded in the DOI is not the journal publication year.

No fabricated or mismatched citation was found among the four current report references. This check establishes bibliographic identity and appropriate source type, not validation of every claim in the cited papers. External benchmark results are not substituted for this group's audited predictions. No report, slide or experimental value needed correction from this check.

## Current bibliography — checked on 2026-09-09 (Singapore)

The supplied teacher LaTeX template has now been received and applied. The revised report has seven pages including references, using the original template typography. Descriptive links and DOI strings replace long raw URLs. The project repository is linked in the result-reconciliation paragraph rather than listed as external literature. All seven numbered entries have corresponding in-text citations.

| Current reference | Verification and supported use |
| --- | --- |
| [1] Yeh (2009), *Default of Credit Card Clients* | [Official UCI record](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) supplies the citation year, author, DOI `10.24432/C55S3H` and CC BY 4.0 license. Dataset provenance, not a journal article. |
| [2] Yeh and Lien (2009), *The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients* | UCI identifies the associated paper; [Crossref metadata](https://api.crossref.org/works/10.1016/j.eswa.2007.12.020) confirms both authors, title, *Expert Systems with Applications* 36(2), 2473–2480 and 2009 publication. Supports the dataset's research context, not our model scores. |
| [3] Pedregosa et al. (2011), *Scikit-learn: Machine Learning in Python* | [Official JMLR article](https://jmlr.org/papers/v12/pedregosa11a.html) confirms title, authors, 12(85), 2825–2830 and 2011. Software citation; current API behavior is documented separately in [7]. |
| [4] Hastie, Tibshirani and Friedman (2009), *The Elements of Statistical Learning: Data Mining, Inference, and Prediction*, second edition | [Springer book record](https://link.springer.com/book/10.1007/978-0-387-84858-7) confirms three authors, edition, year and DOI. Its linear classification and tree chapters support method background. |
| [5] Breiman (2001), *Random Forests* | [Crossref metadata](https://api.crossref.org/works/10.1023/A:1010933404324) confirms Leo Breiman, *Machine Learning* 45, 5–32, 2001. The [author-hosted paper](https://www.stat.berkeley.edu/users/breiman/randomforest2001.pdf) supports randomized tree ensembles. |
| [6] Chen and Guestrin (2016), *XGBoost: A Scalable Tree Boosting System* | [Author preprint](https://arxiv.org/abs/1603.02754) confirms full title, authors and published DOI. [Crossref metadata](https://api.crossref.org/works/10.1145/2939672.2939785) confirms the KDD proceedings and pages 785–794; its shorter title field is “XGBoost.” |
| [7] scikit-learn developers, *average_precision_score* | [Version-pinned 1.8 API documentation](https://scikit-learn.org/1.8/modules/generated/sklearn.metrics.average_precision_score.html), accessed September 9, defines non-interpolated average precision. The experiment environment is pinned to 1.8.0. |

Crossref records for [2], [5] and [6] were retrieved successfully during this revision. Consensus was also searched for the dataset paper, but this search returned related papers rather than the target; none of those results was used. The earlier successful Consensus record checks remain documented above. Bibliographic checking does not imply a full-text review of every source or independent validation of this project's experiments.

## APA 7 conversion — 2026-09-09

Corrected the missed user requirement: both in-text citations and references now use APA 7 conventions. The teacher's original style still governs the overall course-paper layout.

- Author–date parenthetical citations replace numeric citations. Three or more authors use “et al.” in text; two-author parenthetical citations use an ampersand.
- The unnumbered reference list is sorted Breiman, Chen, Hastie, Pedregosa, scikit-learn developers, Yeh alone, Yeh and Lien. It starts on page 7 with a centered bold heading, 0.5-inch hanging indents, double spacing and the same 10pt text as the body.
- Journal titles and volume numbers are italicized; article/book titles use sentence case. DOI links use the `https://doi.org/` form, without a concluding period. The data reference uses `[Data set]`; its license remains in the source records rather than as a nonstandard citation suffix.
- All 16 authors of the scikit-learn paper are listed, in the order confirmed by the [official JMLR record](https://jmlr.org/papers/v12/pedregosa11a.html). “Et al.” is limited to its in-text citation. The version-pinned API document has no reliable publication date, so it uses “n.d.”; an access date is unnecessary for this version-specific reference.
- Formatting was checked against the APA-authored [student-paper formatting guidance](https://www.apa.org/ed/precollege/psn/2020/09/apa-style-student-papers) and the University of Canterbury's [APA reference-list guide](https://www.canterbury.ac.nz/study/study-support-info/citations-and-referencing/apa-style/creating-a-reference-list). APA's detailed reference-example pages returned an iframe in the text reader; no claim is made that inaccessible content was reviewed.

The original seven sources and experimental values are unchanged. The final PDF and self-contained source ZIP supersede the numeric-reference revision.
