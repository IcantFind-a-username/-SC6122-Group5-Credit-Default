# Group 5 submission checklist

Prepared for **NTU SC6122 Emerging Topics in FinTech**. Dates are provisional: report **7 September 2026**, presentation **Tuesday 8 September 2026**. No exact submission time or platform upload field has been verified. The group makes the final course-platform submission; no upload or email has been performed.

## Teacher requirements supplied by the group

| Requirement | Evidence / current status |
|---|---|
| Real data and an applied ML problem | UCI credit-card default data; source, CC BY 4.0 attribution, raw/clean files and source audit included. |
| Reasonable hyperparameters, comparisons and interpretation | Four reproducible model workflows; explicit baseline/selected settings and search budgets; AP, ROC-AUC and threshold metrics; association-only interpretations. |
| Test excluded from training/tuning/threshold choice | Shared fit/validation/CV membership; pipeline fit boundaries and validation-only thresholds checked. Historical test exposure, original LR gap and RF regeneration are explicitly disclosed. No new independent unseen-test claim. |
| Entire English report, including references, ≤7 pages | **6 pages**, `Group5_Final_Report.pdf`; normal 11pt body; three figures, four numbered result tables and a plain partition table. Math subscripts are smaller glyphs, not reduced body type. |
| Required report sections | Background/problem, data/target, objectives, methods, findings/comparison, conclusions/discussion and member contribution roles are included. All four names, student IDs and equal 25% shares are confirmed. |
| Preferred teacher Word/LaTeX template | Repository and Documents/Downloads/NTU/Desktop filename search found no teacher template or named samples. Complete standard LaTeX fallback provided; swap to the actual template if supplied and recheck ≤7 pages. |
| Report + applicable dataset submitted day before presentation | Files ready locally; **group must confirm 7 September deadline time/portal and upload**. Data are in `data/`, also included in reproduction archive when packaged. |
| 15 minutes including Q&A; all four speak | 12 main slides: 720 seconds speaking; four roles ×180 seconds; 180 seconds Q&A. Four backup slides outside main talk. Rehearse actual speaking pace. |
| 25% group / 75% individual assessment | Four substantive role assignments; per-slide English scripts and 22 bilingual Q&A items with role priorities. Named assignments and equal 25% contribution shares are recorded in `team.json`. |

## Actual deliverables

- [Report PDF](Group5_Final_Report.pdf); [editable LaTeX](Group5_Final_Report.tex); [report prose template](report_template.tex).
- [Editable PPTX](Group5_Presentation.pptx); [PDF backup](Group5_Presentation.pdf).
- [English speaker notes](Group5_Speaker_Notes.md): each slide, named speaker, student ID, target time, script and transition; the same text is embedded in native PPTX notes for Presenter View.
- [Bilingual Q&A](Group5_QA.md): 22 questions, role-priority map and evidence links.
- [Model comparison](model_comparison.csv), [cost comparison](cost_comparison.csv), [README](../README.md), [dataset provenance](../data/README.md).
- [Experiment audit](../results/final/audit.json), [audit interpretation](../integration/AUDIT_FINDINGS.md), [source audit](../results/final/source_audit.json), [notebook execution status](../results/final/notebook_status.json).
- `Group5_Dataset.zip` (data-only) and `Group5_Reproduction.zip` (code/data/results/materials), with `package_manifest.json`: suggested backup; packaged Git commit and archive SHA256 recorded after final build.
- `delivery_validation.json`: PDF page counts, bounds/content checks and document hashes. Visual report inspection covers the full contact sheet and detailed table/reference pages. Final slide export/visual acceptance is recorded below.

## Reproducibility acceptance

- **223/223 artifact checks passed** across DT, RF, XGBoost and the separately labelled LR supplement.
- **70 pytest tests passed**; Ruff repository check and mypy source check passed. Final gate results retained in `results/final/integration_gate.txt`.
- LR original notebook was empty across available refs/history; legacy CSVs retained without asserting their AP/PR-AUC definition or training provenance. Supplement was declared/committed before one run and uses separate artifacts.
- All published comparison metrics recomputed from saved scores after one-to-one row-ID alignment. Score/threshold parsing uses round-trip precision; decisions use `>=` before rounding.
- Historical LF/CRLF hash differences explained; parsed values/types/order equal. Fresh UCI raw bytes and exact cleaning replay preserved.
- XGBoost cross-platform probability difference ≤5.96e-8; all frozen decisions match. Original saved probabilities remain the reporting source.
- RF threshold-specific misclassification cases/profiles are correct; identical extreme cases can legitimately recur.
- Bootstrap is conditional on fixed models, predictions, thresholds and class counts; no retraining/selection uncertainty or external validity is claimed.
- 03–06 reading notebooks executed in unified Python environment. 01/02 are historical data-writing workflows, not rerun over frozen files; their transformation/split logic is independently audited.
- Verification/redraw commands and separate retraining commands are distinguished in README. Retraining requires a new output directory and cannot overwrite a frozen protocol.

## Suggested backups, not independently confirmed upload requirements

Prepare the editable source, PPTX/PDF, notes/Q&A, code/data/models/results and environment pins. The course screenshots supplied in the task did **not** establish that code or slides must be uploaded. The reproduction ZIP excludes Git internals, virtual environments, caches, render scratch files and unrelated personal files. Optional rendered preview images are evidence/backup, not extra report pages.

## Confirmed members

| Member | Student ID | Responsibility | Slides | Share |
|---|---|---|---|---|
| Lei Peng | G2509090C | Data and logistic regression | 1–3 | 25% |
| Zhang Hanyu | G2509091L | Decision tree, rules and overfitting | 4–6 | 25% |
| Zhou Xinzhe | G2509033F | Random forest, feature importance and error cases | 7–9 | 25% |
| Xu Yiqun | G2509092H | XGBoost tuning and threshold trade-offs | 10–12 | 25% |

Shared work: all four agree data splits, preprocessing and metrics; write individual sections; jointly integrate, verify results and rehearse. Audit preparation is shared, rather than the main Part 3 topic.

## Human confirmation before upload

1. Course announcement: final presentation date, report deadline **time/timezone**, submission portal/field, dataset packaging rules, and whether code/PPT must also be uploaded.
2. Teacher `Word Template.docx` or `Latex Template.zip`; named sample report/slides if available. Samples never override the explicit seven-page cap.
3. Team review of substantive contribution statements, source attribution, AI-assisted integration/supplement, and historical-exposure limitations; practice all four sections aloud.
4. If any additional original LR training source exists outside the searched repository/workspace, supply it for provenance reconciliation; do not silently substitute it for the labelled supplement.

## Final presentation acceptance

Actual PPTX exported by official LibreOffice 26.8.0.3 to a 16-page PDF. All nonempty slide text boxes are checked against the rendered PDF; scripts and explicit transitions match Markdown, native speaker notes and the manifest. The revised cover, open chart layouts, partition table and backup pages are rendered for visual inspection. Main talk: 720 seconds; Q&A: 180 seconds. Report is complete and visually inspected at 6 pages. `slide_manifest.json` and `delivery_validation.json` record hashes and counts.

Integration branch only: `integration/final-submission-20260907`. No force-push, main merge, course upload or teacher email.
