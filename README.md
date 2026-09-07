# SC6122 Group 5 · Credit Card Default Prediction

Final integration branch: `integration/final-submission-20260907`. Main and member histories are preserved. **Course upload is performed by the group.** Planned report date: 7 September 2026; presentation: 8 September 2026. Exact deadline and upload fields must be confirmed. Member identities and equal 25% shares are recorded in `submission/team.json`.

## Deliverables

- [Final report PDF](submission/Group5_Final_Report.pdf), with editable [LaTeX](submission/Group5_Final_Report.tex) and [template source](submission/report_template.tex); no separate cover.
- [Editable presentation](submission/Group5_Presentation.pptx), [PDF backup](submission/Group5_Presentation.pdf), [speaker notes](submission/Group5_Speaker_Notes.md), [bilingual Q&A](submission/Group5_QA.md).
- [Submission checklist](submission/SUBMISSION_CHECKLIST.md).
- [Final comparison](results/final/model_comparison.csv) and [cost scenarios](results/final/cost_comparison.csv). Corresponding submission copies are generated from these files.
- [Acceptance findings](integration/AUDIT_FINDINGS.md), [machine-readable evidence](results/final/audit.json), [source audit](results/final/source_audit.json), [LR provenance](integration/LOGISTIC_PROVENANCE.md).

The presentation to rehearse and submit is **`submission/Group5_Presentation.pptx`**. The root-level `Group5_Presentation.pptx` and `submission/Group5_Presentation_new.pptx` are preserved member uploads based on an earlier layout. Their Part 2 content has been selectively integrated into the current master; do not substitute either full upload for the master. See [member-edit review](integration/PART2_EDIT_REVIEW.md).

## Environment

Use Python 3.12. The accepted environment is Python 3.12.2, numpy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, scipy 1.17.0, matplotlib 3.10.8, joblib 1.5.3, and XGBoost 3.0.5. `requirements.txt` unifies the previously separate member dependency files; OS markers choose the appropriate XGBoost distribution. The report build uses Tectonic; editable slides use python-pptx. Actual slide PDF rendering uses official LibreOffice 26.8.0.3; PowerPoint is also supported by the generator on macOS. Native Keynote/PowerPoint export encountered local application access problems during integration, so an official portable LibreOffice runtime was used. Recheck layout after exporting with another renderer.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-delivery.txt
python -m ipykernel install --prefix .venv --name sc6122 --display-name "SC6122 unified environment"
```

No virtual environment or cache is included in submission. Linux installs xgboost-cpu; macOS uses xgboost and may need the usual OpenMP runtime. Never load untrusted joblib files; supplied files are verified against the recorded model hashes. Historical models were built on different operating systems; audit accepts XGBoost replay drift no larger than 1e-7 only if every frozen policy decision still agrees.

## Verification / redraw only (no model fitting)

Run from repository root with the environment activated:

```bash
python -m integration.reproduce verify
python -m pytest -q
ruff check .
mypy part1 part2 part3 part4 integration tests conftest.py
python -m integration.reproduce figures
python -m integration.reproduce notebooks
python -m integration.reproduce report
python -m integration.reproduce slides --soffice /Applications/LibreOffice.app/Contents/MacOS/soffice
```

`verify` replays official-source cleaning from the included cached raw CSV, checks hashes/values/types/order, split and CV memberships, saved model predictions, CSV metrics, validation thresholds, tied-score decisions, bootstrap intervals, and RF error cases. It writes `results/final/`, never the historical experiment directories. CV scores and selection are reconciled; the original CV fits are not repeated. Raw data download occurs only if `data/source/uci_350_raw.csv` is absent. Score/threshold CSVs use `float_precision="round_trip"`; classification always uses `score >= threshold`. AP means `average_precision_score`, not trapezoidal PR-AUC.

`figures` redraws the final report figures and generates its LaTeX from accepted CSVs; it does not select models. `report` also runs Tectonic. `slides` creates the PPTX, native/Markdown notes and actually exports the same PPTX to PDF. Supply `--soffice /path/to/soffice` for LibreOffice (on Linux this is commonly `/usr/bin/soffice`); without it the generator uses macOS PowerPoint. Install a native renderer separately; it is not a pip dependency. `notebooks` executes 03–06 in the local `sc6122` kernel. 01/02 are retained historical inspection/source-writing notebooks: do not run them over the frozen data. Their cleaning and membership logic is independently verified by `verify`. The previously empty 03 is now an honest reader for the supplement, and 05 displays frozen RF evidence.

## Retraining (different commands; separate output directory required)

Only run if explicitly reproducing training. These commands can take substantially longer and create a **new reproduction**, not a replacement frozen experiment. Even though each runner selects only on CV/validation, all existing historical test results have already been seen. Do not optimize further on this test or backdate a freeze.

```bash
python -m part1.experiment --output-dir results/reproductions/lr
python -m part2.experiment --output-dir results/reproductions/decision_tree
python -m part3.experiment --output-dir results/reproductions/rf --candidates 24 --threads 2
python -m part4.experiment --output-dir results/reproductions/xgboost --candidates 24 --threads 2
```

All runners reject a directory containing `protocol_frozen.json`. Shared fitting rows: 18,000; validation: 6,000; historical test: 6,000. Five CV folds each train on 14,400 rows and hold out 3,600. LR evaluates 12 exhaustive settings; DT 21 exhaustive settings; RF/XGBoost each include a baseline plus 23 seeded random settings. One-hot encoders and LR scaling fit within training folds. No oversampling, imputation or test-driven threshold selection is used. Full configurations/search ranges are in the saved protocol JSONs; models fit 18,000 rows without refitting on validation.

## Evidence limitations

Original logistic CSVs remain in `results/logistic_regression_*.csv`; no original training source or saved row predictions were recoverable across local/remote refs. They are not silently relabelled as verified AP. `results/logistic_supplement/` is a once-run, predeclared **post-hoc reproducibility supplement** after historical test results existed. Its exact training script is stored at commit `dd6f673`; the frozen script hash is preserved. RF's environment-regeneration history is documented in the acceptance findings. Frozen timestamps cannot prove earlier results were never viewed outside the runner.

Historical source-train/test hashes differ due to LF/CRLF line endings; parsed data match exactly. The fresh official raw CSV uses `.gitattributes -text` to preserve its downloaded bytes. Retained equal feature vectors, a single old Taiwan sample, missing external/temporal/fairness/calibration validation and hypothetical costs limit generalization. Bootstrap intervals condition on fitted models, frozen thresholds and fixed class counts; they omit training/selection uncertainty. Feature importance and rules are associative.

## Editing / package

Update report prose in `submission/report_template.tex`, then regenerate; generated tables come from the final comparison. Slide editable content lives in `integration/build_slides.py` and the PPTX. Confirmed member names, IDs, roles and equal 25% shares are maintained in `submission/team.json`; native PPTX notes include each named speaker’s script. An edit to source requires rebuilding and rechecking PDF/PPT consistency.

```bash
python -m integration.reproduce package
```

The reproduction archive contains committed repository files only, under `Group5/`. A separate `Group5_Dataset.zip` contains only the committed `data/` folder and its source/license documentation, for a platform that requests the dataset separately. `.gitattributes` excludes the archive itself and temporary render logs. No `.git`, `.venv`, caches or unrelated local files are included. Check `submission/package_manifest.json` for the packaged commit and SHA256 when using the prepared archive.

### Confirmed presentation responsibilities

Lei Peng: data checks/preprocessing and logistic baseline (slides 1–3). Zhang Hanyu: decision-tree tuning, rules and overfitting (4–6). Zhou Xinzhe: random-forest tuning, validation feature importance and saved error examples (7–9). Xu Yiqun: XGBoost tuning and threshold trade-offs (10–12). All four share protocol agreement, their own writing, final integration, result checking and rehearsal; each contributes 25%.
