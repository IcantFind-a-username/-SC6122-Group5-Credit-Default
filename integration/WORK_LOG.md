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
