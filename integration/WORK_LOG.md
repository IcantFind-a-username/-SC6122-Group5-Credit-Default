# Integration record — 2026-09-07

## Initial evidence and gaps
- Clean working tree at start; fetched all remote branches. Main: 15c6d1c. No other local branches/worktrees with unpublished work.
- Integration branch: integration/final-submission-20260907; never merge/force-push main.
- ae99b01 contributes only four absent Part 4 documentation/notebook files; cherry-picked preserving authorship.
- Logistic regression notebook empty; existing CSVs insufficient to establish training provenance. Investigate all refs, then label any supplement honestly.
- Templates/course attachments search in progress. Names, IDs, contribution percentages and platform deadline require confirmation.

## Existing-tool inventory (verified with grep)
- part4/evaluation.py:12 feature_target — ID exclusion and labels.
- part4/evaluation.py:25 split_development — shared stratified development split.
- part4/evaluation.py:43 metrics — AP, ROC-AUC, >= decisions, confusion counts and costs.
- part4/evaluation.py:63,83 threshold_table/select_threshold — validation-only cost selection.
- part4/experiment.py:48,52,56 write_json/file_hash/save_predictions — serialization, SHA256 and float-preserving predictions.
- part4/experiment.py:63 paired_bootstrap — conditional paired intervals.
- part3/misclassification.py:29,38,62 derive_features/compute_profiles/case_snapshots.
- The benchmark/artifacts.py, report.py, metrics.py, matcher.py and review/executor.py mentioned in supplied generic instructions do not exist in this repository; do not invent imports.
- Existing duplicate JSON/hash helpers across experiment modules will be consolidated by controller.

## Exclusive ownership
- audit worker: integration/audit.py; integration/AUDIT_FINDINGS.md; results/final/audit*; results/final/model_comparison.csv; results/final/cost_comparison.csv.
- logistic worker: part1/; integration/LOGISTIC_PROVENANCE.md; results/logistic_supplement/; tests/test_part1.py.
- controller: all other files, shared helpers, dependencies, existing tests, report/slides/notes/checklist and final integration.

Workers reuse the above tools; no duplicate utilities. Propose new utilities before implementing. Every measurement script must be committed before execution. Workers request controller commit when ready; final report includes diff --stat, reused tools and new tools.

## Completed experiment integration
- Official UCI fresh-source cleaning replay exact; original download bytes were not preserved.
- Frozen experiment audit: 223/223 checks passed. Original CV fit jobs were not rerun.
- Legacy LR source was unrecoverable across refs/reflogs/unreachable objects; separate supplement predeclared in dd6f673 and run once.
- Historical train/test and RF metadata hashes explained with LF/CRLF evidence; RF environment-regeneration chronology retained.
- XGBoost platform probability drift at most 5.96e-8, with frozen decisions identical; reporting retains original probabilities.
- RF per-threshold case exports and group profiles are correct, including legitimately repeated extreme errors.
- Shared artifact writer/hash/prediction serializer and paired bootstrap now each have one implementation. DT retains only an adapter that computes model probabilities. No re-export __init__ modules added.
- Four artifact-reading notebooks executed in unified environment; source-writing notebooks retained with only redundant imports removed.
- Integration gate: 70 pytest tests passed, ruff all files passed, mypy 28 source files passed. Subsequent nonbehavioral DT serializer adapter is covered by the final gate.
- Six-page report rendered including all references, using 11pt body and normal math scripts. Teacher template missing, standard LaTeX fallback declared. Contact sheet and pages 3/6 visually inspected: no truncation/overlap, clear tables/charts.
- New test fixture structure replaces repeated setup; existing test files only, no new setup-heavy test file.

## Final delivery acceptance
- Report: six pages including references, 11pt body; actual PDF rendered with Tectonic. Full contact and detailed comparison/reference pages inspected.
- Presentation: 16 pages (12 main + 4 backup), five editable native charts, all 144 text boxes match the actual PPTX-rendered PDF. Explicit transitions and scripts agree across manifest, native notes and Markdown.
- Talk timing: 720 seconds, 180 per role; Q&A 180 seconds. Backup slides do not count in the main talk.
- Official signed LibreOffice 26.8.0.3 used to render the original PPTX after native Office/Keynote access failures. One backup card overflow was corrected and re-rendered; final dense slides/contact inspected.
- Final gate after document/precision changes: 70 tests passed (1.29s), full Ruff passed, mypy passed on 28 source files.
- Final main remote recheck: 15c6d1c, unchanged. All changes stay on integration branch. No course upload, teacher email, force-push or main merge.
- Remaining human information: member identities/actual contribution percentages, teacher template, final course platform deadline/date/upload fields, any original LR code outside the searched repository.

## Presentation and member details revision (2026-09-07)

- Applied user-supplied identities: Lei Peng G2509090C (part 1), Zhang Hanyu G2509091L (part 2), Zhou Xinzhe G2509033F (part 3), Xu Yiqun G2509092H (part 4). Equal contributions of 25% each are stored in `submission/team.json` and displayed in final materials.
- Replaced the report's three decorative partition cards with an ordinary partition/use table; removed the unused card image. The report remains six pages with three numbered figures.
- Redesigned the slide cover and body layouts with open chart space, a real partition table, an editable tree-rule diagram, thin rules and no theme shadows. Audience slides contain no rehearsal timing labels; timing remains in notes.
- Main slide ownership: Lei 1–3, Zhang 4–6, Zhou 7–9, Xu 10–12. All sixteen native PPTX note sections contain the full script, named speaker, student ID and transition. Four backup leads and 22 bilingual Q&A priorities are named explicitly.
- Rendered the actual PPTX with the official hash-verified, signed LibreOffice runtime. Inspected the report first/contribution pages, the slide contact sheet and detailed cost/uncertainty slides. Delivery validation checks all 182 nonempty text boxes against PDF, all scripts against native notes, and names/IDs against report/cover/Q&A. Experiment CSVs and frozen artifacts were not changed.
- Full repository gate after layout/identity changes: 70 pytest tests passed; Ruff passed; mypy passed for 28 source files. Subsequent rendering refinements were checked with Ruff/mypy and the delivery validator.

## Align final materials with the group's confirmed scope (2026-09-07)

- Confirmed the user's detailed four-part responsibility statement. Part 3 now focuses on RF tuning, validation permutation importance and illustrative error cases; protocol agreement, individual writing, final integration/checking and rehearsal are shared work.
- Replaced main slides 8–9 with an editable RF importance chart and two pre-existing extreme errors from `misclassification_cases_05.csv`. The cases are explicitly illustrative, not average clients; no model or threshold was trained/selected after this inspection.
- Reused `integration.audit.read_csv` for round-trip parsing and `integration.artifacts` for hashes/serialization. Added one shared presentation-only reader, `integration/presentation_evidence.py`, used by report, slides and delivery validation; it checks the selected examples against frozen row-level predictions and the 0.5 error rules.
- Report Figure 3 now covers RF validation permutation importance with SD bars; the interpretation text, member contribution table, native PPTX scripts, Markdown notes, README and bilingual Q&A agree with the updated scope. RF Q12–Q14 are primary; Q15–Q16 audit preparation is shared.
- Acceptance: report six pages; deck/PDF sixteen pages; 182 nonempty slide text boxes verified; all native scripts and named leads match. New chart values/categories and example scores/IDs are checked against frozen artifacts. Rendered RF slides and report interpretation/contribution pages inspected. 70 pytest tests passed, Ruff passed, mypy passed for 29 source files.

## Member-upload review and selective integration (2026-09-07)

Fetched and fast-forwarded the integration branch to preserve member commits cafec5f/6bde3bd. The two uploaded PPTX files are byte-identical copies based on the older pre-redesign master. Reviewed the member's actual changes against that base: slide 6 bullets plus notes 4–6. Imported those changes into the current generator with scoped comparison language, LR evidence qualifier and current RF handoff. Restored named speaker metadata, source lines and transitions around the imported script. Changed only slides 4–6; all other slide text/notes and all chart series remain unchanged. Rebalanced Part 2 to 50/55/75 seconds. Uploaded source files remain intact; README/checklist identify the canonical master. Regenerated PPTX, PDF, notes and package, with full delivery checks and repository gate passing. Details: `integration/PART2_EDIT_REVIEW.md`.

## Clear presentation ending (2026-09-07)

Changed main slide 12 to “Conclusions & Q&A”, retaining its three conclusions and adding “Thank you / Questions & discussion” with all four member names. Notes instruct speakers to finish there and use slides 13–16 only for relevant questions. Main timing remains 720 seconds and each role 180 seconds. Added the previously delivered focused Part 4 Q&A to version control and the checklist. Regenerated the missing canonical PPTX from the saved current generator, exported the actual PPTX to PDF, checked the closing page visually and passed full document/notes validation. Report and experiment results remain unchanged.

## 2026-09-09 — supplied teacher template

Preserved the three supplied NeurIPS files in `course_materials/latex_template/`; loaded the unmodified style in named-author mode and replaced only conference metadata with the course notice. Migrated title, abstract, sections, table/figure captions and references to native template conventions. Kept the course seven-page total over the generic conference exemptions. Condensed repeated prose rather than reducing template type or margins. Replotted the same frozen numbers for the narrower text block; no model training or new threshold choice. Report validates at six pages with matching metrics, US Letter, embedded non-Type-3 fonts and no overfull boxes. Added a self-contained report-source packaging mode and preserved the user-modified PPTX.

The final source ZIP was extracted into an independent temporary directory and compiled successfully with Tectonic. All six pages' extracted text matched the delivered PDF exactly. The final ranking legend is outside the plot; exact values remain in the adjacent performance table. Report-only validation and Ruff passed.

## 2026-09-09 — bibliography and disclosure revision

Replaced long raw bibliography URLs with concise DOI/descriptive links. Added the dataset's associated paper, the scikit-learn software paper, the second edition of Elements of Statistical Learning and Breiman's Random Forests paper, each cited in the relevant body text. Moved the project repository into the reconciliation paragraph. The seven current sources and primary verification records are mapped in `integration/REFERENCES.md`; no experimental values were changed.

The disclosure now describes language polishing, grammar guidance and selected technical tasks, without describing the document or the entire codebase as AI-produced. Retained study-level evaluation limitations and artifact history. The revised report renders to seven pages including references, with the unmodified teacher style, embedded fonts, matching comparison numbers and no overfull boxes. Inspected the rendered conclusions/disclosure and reference pages. Rebuilt the self-contained report archive; the separately modified PPTX remains untouched.

## 2026-09-09 — correct missed APA 7 requirement

Converted all seven source citations to author–date format through natbib. References are unnumbered and alphabetized, with 0.5-inch hanging indents, double spacing, 10pt body-matching type, sentence-case work titles, appropriate italics and DOI URLs. Expanded the scikit-learn reference to its 16 verified authors. Retained the teacher style byte-for-byte, all experiment numbers and the existing disclosure. Report-only validation passes at seven pages with no overfull boxes; inspected the rendered methods and reference pages. Rebuilt the report-source archive. The separate local PPTX edit is preserved.
