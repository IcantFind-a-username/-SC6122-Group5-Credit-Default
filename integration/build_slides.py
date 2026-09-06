"""Build editable 16-slide presentation and native notes from audited artifacts.

Commit before execution. Run: PYTHONDONTWRITEBYTECODE=1 python -m integration.build_slides
Charts remain editable PowerPoint charts. PowerPoint exports the companion PDF.
"""
from dataclasses import dataclass
from pathlib import Path
import json
import subprocess

import fitz
from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

from integration.artifacts import file_hash, write_json
from integration.audit import read_csv

ROOT = Path(__file__).resolve().parents[1]
NAVY, TEAL, ORANGE = "142C43", "127D88", "DD843D"
LIGHT, GRAY, WHITE = "EFF5F7", "526575", "FFFFFF"


@dataclass
class Slide:
    title: str
    role: str
    seconds: int
    bullets: list[str]
    headline: str
    detail: str
    source: str
    script: str
    chart: dict | None = None


def textbox(slide, x, y, w, h, text, size=22, color=NAVY, bold=False):
    """Presentation layout helper; does not rasterize editable text."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(.03)
    frame.margin_top = frame.margin_bottom = Inches(.02)
    for index, line in enumerate(text.split("\n")):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = line
        paragraph.font.name = "Arial"
        paragraph.font.size = Pt(size)
        paragraph.font.bold = bold
        paragraph.font.color.rgb = RGBColor.from_string(color)
        paragraph.space_after = Pt(12)
    return box


def panel(slide, x, y, w, h, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(color)
    shape.line.fill.background()


def editable_chart(slide, spec):
    """Native chart with embedded workbook, direct values and a zero baseline."""
    data = CategoryChartData()
    data.categories = spec["categories"]
    for name, values in spec["series"]:
        data.add_series(name, values)
    chart_type = XL_CHART_TYPE.BAR_CLUSTERED if spec.get("horizontal") else XL_CHART_TYPE.COLUMN_CLUSTERED
    chart = slide.shapes.add_chart(chart_type,
        Inches(6.8), Inches(2.15), Inches(5.95), Inches(3.6), data).chart
    chart.has_legend = len(spec["series"]) > 1
    if chart.has_legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
        chart.legend.font.size = Pt(15)
    chart.category_axis.tick_labels.font.size = Pt(16)
    chart.value_axis.tick_labels.font.size = Pt(14)
    chart.value_axis.minimum_scale = 0
    chart.value_axis.maximum_scale = spec.get("maximum", 1)
    chart.value_axis.has_major_gridlines = True
    chart.value_axis.tick_labels.number_format = spec.get("format", "0.0")
    plot = chart.plots[0]
    plot.has_data_labels = True
    plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    plot.data_labels.font.size = Pt(17)
    plot.data_labels.number_format = spec.get("format", "0.000")
    for index, series in enumerate(chart.series):
        series.format.fill.solid()
        series.format.fill.fore_color.rgb = RGBColor.from_string((TEAL, ORANGE)[index % 2])
        series.format.line.fill.background()


def make_slides(frame):
    def row(family, model):
        selected = frame[(frame.Family == family) & (frame.Partition == "test") & (frame.Model == model)]
        if len(selected) != 1:
            raise ValueError(f"Expected one audited row for {family}/{model}")
        return selected.iloc[0]

    lr = row("Logistic Regression", "Tuned LR supplement")
    lb = row("Logistic Regression", "Baseline LR supplement")
    dt = row("Decision Tree", "Tuned Decision Tree")
    db = row("Decision Tree", "Baseline Decision Tree")
    rf = row("RF", "Tuned RF")
    rb = row("RF", "Baseline RF")
    rc = row("RF", "Tuned RF / cost ratio 5")
    xg = row("XGBoost", "Tuned XGBoost")
    xb = row("XGBoost", "Baseline XGBoost")
    xc = row("XGBoost", "Tuned XGBoost / cost ratio 5")
    rf_parameters = json.loads((ROOT / "results/rf/protocol_frozen.json").read_text())["Selected_parameters"]
    xg_parameters = json.loads((ROOT / "results/xgboost/protocol_frozen.json").read_text())["Selected_parameters"]
    xg_interval = read_csv(ROOT / "results/xgboost/bootstrap_intervals.csv").set_index("Quantity").loc["AP difference: tuned - baseline"]
    source = "Source: results/final/model_comparison.csv | Historical test n=6,000; default=1"
    note = "LR* = post-hoc reproducibility supplement after historic test results existed."
    comparison = {"categories": ["LR*", "Tree", "RF", "XGBoost"],
                  "series": [("Baseline", [lb.AP, db.AP, rb.AP, xb.AP]),
                             ("CV-selected", [lr.AP, dt.AP, rf.AP, xg.AP])],
                  "maximum": .65, "format": "0.000", "horizontal": True}
    slides = [
        Slide("Credit default: rank risk, then choose an action", "Part 1", 45,
          ["How well can we identify default risk?", "What changes when missed defaults cost more?", "Four models. One auditable comparison."],
          "12 MIN + 3 MIN Q&A", "SC6122 • Group 5\nFour speakers × three minutes\nNAME / ID / SHARE TO CONFIRM", "UCI Default of Credit Card Clients; group experiment artifacts.",
          "Our question is how to identify default risk while balancing predictive ranking, interpretability, and the cost of taking action. We compare logistic regression, a decision tree, random forest, and XGBoost on shared historical records. A model score ranks accounts, but a threshold decides which accounts receive attention. Those are different questions, and our results will show why the distinction matters. Each of our four roles has three minutes, followed by three minutes for questions. Member names, student IDs, and contribution shares remain visibly marked for confirmation. I will begin with the data and the evidence boundary."),
        Slide("One split, shared folds, distinct responsibilities", "Part 1", 70,
          ["30,000 clients • 23 predictors • 22.12% default", "Categories learned within each training fold", "Validation selects policies; historical test reports outcomes"],
          "18,000 → 6,000 → 6,000", "FIT: five CV folds, seed 42\nVALIDATION: threshold selection\nTEST: fixed historical holdout", "Source: data/splits; protocol_frozen.json; results/final/audit.json",
          "The UCI dataset contains thirty thousand Taiwan credit card clients and twenty-three predictors. About twenty-two percent default, so an always-negative classifier can appear accurate while detecting nobody. We retain the supplied stratified split: eighteen thousand fitting rows, six thousand validation rows, and six thousand historical test rows. Five shared folds inside fitting data select configurations by average precision. Each fold learns its own category encoding, and logistic regression also learns scaling there. Validation selects thresholds without a later refit. The audit confirms identical memberships across the reproducible models. This random historical holdout is not temporal or external validation."),
        Slide("Logistic regression: a transparent reference, with a caveat", "Part 1", 65,
          ["L2 model + fold-trained scaling + one-hot categories", "12 declared settings; CV selected C=0.1, unweighted", "Historic LR notebook is empty; original process unverified"],
          f"AP {lr.AP:.4f}", f"Baseline AP {lb.AP:.4f}\nNo ranking improvement from selection\nLR* is a separate post-hoc supplement", source + " | " + note,
          f"Logistic regression offers a linear reference whose coefficients describe regularized associations. We used fold-trained scaling and categorical encoding, then compared twelve declared combinations of regularization strength and class weighting. Cross-validation selected C equal to zero point one without class weighting. The test AP is {lr.AP:.4f}, versus {lb.AP:.4f} for the baseline, so selection did not improve ranking here. Crucially, the historical logistic notebook is empty, and its original procedure cannot be verified. We preserve those artifacts and label our reproducible run as a post-hoc supplement after earlier test results existed. Part two now examines how tree regularization changes performance."),
        Slide("Decision tree: constrain leaves to reduce overfitting", "Part 2", 65,
          ["21 configurations: depth × minimum leaf size", "Unrestricted baseline fits training folds almost perfectly", "Selected minimum leaf size: 100 observations"],
          "Test average precision", "A large baseline gap signals overfitting.\nCV selection improves this tree's ranking.", source,
          f"A decision tree can fit very detailed partitions, which makes overfitting easy. Our baseline achieves nearly perfect fitting-fold AP but only about zero point three in cross-validation. The declared grid searches seven depth limits and three minimum leaf sizes, giving twenty-one configurations. The selected model requires at least one hundred observations in each leaf, although it has no explicit depth cap. Test AP rises from {db.AP:.4f} to {dt.AP:.4f}. This is a substantial change for this model and split. It supports regularization as an explanation, rather than treating training performance as evidence of generalization. Next, we inspect what the tree actually uses.",
          {"categories": ["Baseline", "Selected"], "series": [("AP", [db.AP, dt.AP])], "maximum": .65}),
        Slide("Tree rules make a predictive association inspectable", "Part 2", 60,
          ["Root rule: recent repayment status PAY_0 ≤ 1.5", "Selected tree: depth 18, with 134 leaves", "Node proportions describe this fitting sample"],
          "16.51%  |  70.13%", "Fit-row default proportions\nLeft branch | Right branch\nAssociation, not a causal effect", "Source: saved decision-tree model; integration audit/report evidence.",
          "The selected tree begins with recent repayment status, PAY zero. Its root separates values at one point five. In the fitting sample, the default proportions are sixteen point five one percent on the left and seventy point one three percent on the right. This provides a concise description of an important predictive pattern. It does not mean repayment status causes the outcome, and node proportions are not a substitute for calibration analysis. The full selected tree still has depth eighteen and one hundred thirty-four leaves. We therefore use a representative rule rather than claiming the whole tree is a small explanation."),
        Slide("Compare ranking point estimates without declaring a winner", "Part 2", 55,
          ["AP emphasizes positive-class retrieval", "AP is not trapezoidal PR-AUC", "CV selection precedes these test comparisons"],
          "Test average precision", "Baseline and selected models are both retained.\nSmall ensemble differences do not establish superiority.", source + " | " + note,
          f"This comparison retains both the baseline and the cross-validation-selected model for each family. Average precision is a recall-increment weighted sum of precision, not the trapezoidal area sometimes also called PR-AUC. Our positive prevalence is approximately zero point two two, which gives useful context for these scores. The selected forest has AP {rf.AP:.4f}, and selected XGBoost has {xg.AP:.4f}. Those close point estimates do not establish superiority. The XGBoost baseline is numerically higher, but this retrospective observation does not authorize another selection round on test results. Part three will examine the forest and the fairness of our comparison.", comparison),
        Slide("Random forest: average trees, then tune complexity", "Part 3", 70,
          ["Baseline + 23 seeded candidate settings", f"Selected: {rf_parameters['n_estimators']} trees, depth {rf_parameters['max_depth']}, minimum leaf {rf_parameters['min_samples_leaf']}", f"Positive-class weight {rf_parameters['class_weight']['1']}; feature fraction {rf_parameters['max_features']}"],
          "Test average precision", "Averaging reduces dependence on one tree.\nWeights also change the score distribution.", source + " | results/rf/protocol_frozen.json",
          f"Random forest averages many trees, reducing dependence on any single partition. We evaluated a baseline and twenty-three seeded candidate configurations using the same five fitting folds and average-precision objective. The selected configuration uses five hundred trees, maximum depth eight, a minimum leaf size of two, and half the features at each split. It also weights the positive class three times as heavily. Test AP changes from {rb.AP:.4f} to {rf.AP:.4f}. Class weighting affects the learned score distribution, so we should not assume these scores are calibrated probabilities. We next inspect the operating threshold and the resulting workload rather than relying on ranking alone.",
          {"categories": ["Baseline", "Selected"], "series": [("AP", [rb.AP, rf.AP])], "maximum": .65}),
        Slide("Forest policy: fewer misses, more review alerts", "Part 3", 60,
          [f"Validation selected r=5 threshold: {rc.Threshold:.4f}", f"Recall: {rf.Recall:.1%} → {rc.Recall:.1%}", f"Alert rate: {rf.Alert_rate:.1%} → {rc.Alert_rate:.1%}"],
          f"{int(rf.Cost_5):,} → {int(rc.Cost_5):,}", "Test cost = FP + 5 × FN\nError cases checked under each policy\nSame extreme cases can legitimately recur", source + " | RF misclassification audit; costs hypothetical.",
          f"For the forest, validation selected a threshold of {rc.Threshold:.4f} under the hypothetical assumption that a missed default costs five times a false-positive review. On the historical test set, recall rises from {rf.Recall:.1%} to {rc.Recall:.1%}, but the alert rate also rises from {rf.Alert_rate:.1%} to {rc.Alert_rate:.1%}. Cost falls from {int(rf.Cost_5)} to {int(rc.Cost_5)} units. We independently checked the saved error profiles and case rules for both policies. The most confident errors can appear in both exports because they remain errors at both thresholds. Identical extreme examples alone therefore do not demonstrate an export mistake."),
        Slide("What the audit establishes—and what it cannot", "Part 3", 50,
          ["Identical fit / validation / five-fold memberships", "Metrics recomputed after row-ID alignment", "Frozen thresholds use score ≥ threshold at full precision"],
          "COMPARABLE ≠ IDENTICAL", "Shared data and objective\nDifferent search budgets\nHistorical exposure and LR* caveat remain", "Source: results/final/audit.json; integration/LOGISTIC_PROVENANCE.md",
          "Our audit checks that comparisons use the same clients, labels, development partitions, and five-fold memberships. It recomputes metrics from row-aligned saved predictions and applies the exact greater-than-or-equal decision rule before rounding. Saved-model replay reproduces frozen decisions; minor floating-point differences are documented. These checks make the comparison traceable, but they do not make every aspect identical: search budgets differ, and the logistic supplement has a distinct evidence history. Nor can a repository audit prove everything performed outside the repository. With those boundaries explicit, part four now separates XGBoost's ranking result from its threshold-policy result."),
        Slide("XGBoost: tuning did not improve test ranking", "Part 4", 60,
          ["Baseline + 23 seeded configurations; select by CV AP", f"Selected: {xg_parameters['n_estimators']} trees, depth {xg_parameters['max_depth']}, rate {xg_parameters['learning_rate']}", f"Selected ROC-AUC: {xg['ROC-AUC']:.4f}"],
          "Test average precision", f"Tuned − baseline AP: {xg_interval.Estimate:.4f}\nConditional 95% interval: [{xg_interval.CI_low:.4f}, {xg_interval.CI_high:.4f}]", source + " | results/xgboost/bootstrap_intervals.csv",
          f"XGBoost builds trees sequentially with regularization. We retained the baseline and searched twenty-three additional seeded configurations using the shared CV objective. The selected configuration has test AP {xg.AP:.4f}, compared with {xb.AP:.4f} for the baseline. The paired bootstrap interval for the difference spans zero, so we do not claim a ranking improvement. This bootstrap resamples the fixed predictions and does not include model retraining or selection uncertainty. The useful next question is separate: given the selected model's scores, how does a validation-chosen action threshold change missed defaults, false positives, and the stated hypothetical cost?",
          {"categories": ["Baseline", "Selected"], "series": [("AP", [xb.AP, xg.AP])], "maximum": .65}),
        Slide("A lower threshold trades review capacity for fewer misses", "Part 4", 80,
          [f"Validation r=5 cutoff: {xc.Threshold:.4f}", f"Recall {xg.Recall:.1%} → {xc.Recall:.1%}; alerts {xc.Alert_rate:.1%}", f"Cost {int(xg.Cost_5):,} → {int(xc.Cost_5):,}: {(1-xc.Cost_5/xg.Cost_5):.1%} reduction"],
          "Test confusion trade-off", "Same ranking scores, different action policy.\nReview costs are hypothetical; capacity is unmeasured.", source + " | FP + 5×FN; threshold selected only on validation.",
          f"At a cost ratio of five, validation selects XGBoost's threshold at {xc.Threshold:.4f}. Applying it unchanged to the historical test set reduces false negatives from {int(xg.FN)} to {int(xc.FN)}, while false positives rise from {int(xg.FP)} to {int(xc.FP)}. Recall reaches {xc.Recall:.1%}, but {xc.Alert_rate:.1%} of clients are flagged. The total hypothetical cost falls from {int(xg.Cost_5)} to {int(xc.Cost_5)}, about {(1-xc.Cost_5/xg.Cost_5):.1%}. This is not an improvement in AP or ROC-AUC; the scores have not changed. The policy may be impractical if review capacity is limited. Real exposure, loss severity, and intervention benefits are unavailable, so these cost units are a sensitivity analysis.",
          {"categories": ["False positives", "False negatives"], "series": [("Threshold 0.5", [xg.FP, xg.FN]), ("Validation r=5", [xc.FP, xc.FN])], "maximum": 2700, "format": "0"}),
        Slide("Choose the decision question before choosing the policy", "Part 4", 40,
          ["Ranking, explanations, and workload need separate evidence", "No clear ensemble winner from these small differences", "Next: fresh temporal data, calibration, subgroup errors"],
          "QUESTIONS • 3 MIN", "Freeze realistic costs and capacity first.\nValidate a new policy on new data.\nNAME / ID / SHARE TO CONFIRM", "Historical educational study; no causal or deployment-readiness claim.",
          "Our main conclusion is that ranking and action policy answer different questions. Tree regularization improves its baseline substantially, while the ensembles have similar selected-model ranking estimates. Lower thresholds can reduce the stated cost by creating many more reviews. We cannot turn those observations into a production recommendation without realistic costs and capacity constraints. The study is also limited by historical data, retained duplicates, random splitting, and the logistic provenance gap. A next study should freeze a new protocol on fresh temporal or external data and evaluate calibration and subgroup errors. Thank you; we now have three minutes for questions."),
        Slide("Backup A • AP, ROC-AUC and threshold metrics", "Q&A", 0,
          ["AP = sum of recall increments × precision", "ROC-AUC measures positive/negative score ordering", "Precision, recall, F1 and accuracy require a threshold"],
          "AP ≠ TRAPEZOIDAL PR-AUC", "Saved continuous scores supply ranking metrics.\nChanging the cutoff changes decisions only.", "Source: scikit-learn average_precision_score documentation; part4/evaluation.py",
          "If asked about the ranking metric, explain that average precision weights each precision value by the associated increase in recall. It does not linearly interpolate the precision-recall curve with trapezoids, so similarly named PR-AUC values need not agree. ROC-AUC instead summarizes positive-versus-negative score ordering. Neither metric changes when we apply a different operating threshold to the same saved scores. Precision and recall do change because the decision set changes. The historical logistic CSV uses a PR-AUC label whose computation cannot be verified, which is one reason it is excluded from our verified ranking table."),
        Slide("Backup B • Cost ratios and fixed-prediction uncertainty", "Q&A", 0,
          ["Predeclared ratios: r = 1, 3, 5, 10", "Validation minimum cost; ties prefer largest cutoff", "1,000 stratified paired bootstrap resamples"],
          "CONDITIONAL UNCERTAINTY", "Fixed models, thresholds and class counts\nExcludes retraining and selection uncertainty\nExcludes new-population and prevalence shifts", "Source: frozen protocols; integration/uncertainty.py; bootstrap_intervals.csv",
          "The cost experiment declares four ratios rather than searching for a convenient ratio after viewing test results. At each ratio, the validation table includes all distinct score-based decision sets, with tied scores moving together. Equal costs select the largest threshold and therefore fewer alerts. The paired bootstrap samples the same test-row indices for each compared prediction vector, stratified by outcome. Its intervals are conditional on frozen models, thresholds, and class counts. They do not include uncertainty from refitting, hyperparameter search, threshold search, or a shift to another population. Real operational costs would require information that this dataset does not provide."),
        Slide("Backup C • Data provenance and evidence boundaries", "Q&A", 0,
          ["UCI cleaning reproduced exactly from downloaded source", "EDUCATION 0/5/6 → 4; MARRIAGE 0 → 3", "Retained duplicate vectors can span partitions"],
          "HISTORICAL TEST REUSED", "Original LR process remains unverified.\nLR* source was committed before its one run.\nNo new unseen-test claim is made.", "Sources: results/final/source_audit.json; integration/LOGISTIC_PROVENANCE.md",
          "The integration audit redownloaded the official source and reproduced the committed cleaned dataset in values, types, order, and schema. Undocumented education categories are consolidated, and marriage category zero is mapped to other. The original download bytes were not preserved, so the new download and its hash are documented separately. Duplicate feature vectors remain under the established protocol and may create dependence across partitions. For logistic regression, all available notebook history contains an empty model notebook. The supplement's code and search declaration were committed before execution, but previous team test results already existed. This makes the supplement reproducible without making it independent external evidence."),
        Slide("Backup D • Sources, responsibilities and reproducibility", "Q&A", 0,
          ["UCI: doi.org/10.24432/C55S3H", "scikit-learn: average_precision_score documentation", "XGBoost paper: doi.org/10.1145/2939672.2939785"],
          "FOUR ROLES • REVIEW REQUIRED", "P1 data/LR • P2 tree/ranking\nP3 forest/audit • P4 XGBoost/costs\nNAME / ID / SHARE TO CONFIRM", "Sources: Group 5 repository, frozen protocols, row-level predictions and integration audit.",
          "The numerical source for this editable presentation is the audited final comparison CSV, with model-specific protocols and bootstrap artifacts supplying supporting context. The UCI dataset, scikit-learn average-precision documentation, and the XGBoost paper are the core external references. The role plan assigns three minutes each to data and logistic regression, decision trees and ranking, random forest and audit, and XGBoost and costs. Member identities and contribution percentages must be confirmed by the group; we have not invented them. Integration and the logistic supplement were prepared with AI assistance for member review. Reproducing artifacts is distinct from retraining and selecting new models."),
    ]
    return slides


def run():
    output = ROOT / "submission"
    output.mkdir(exist_ok=True)
    frame = read_csv(ROOT / "results/final/model_comparison.csv")
    slides = make_slides(frame)
    assert len(slides) == 16 and sum(s.seconds for s in slides) == 720
    for role in ["Part 1", "Part 2", "Part 3", "Part 4"]:
        assert sum(s.seconds for s in slides if s.role == role) == 180
    deck = Presentation()
    deck.slide_width, deck.slide_height = Inches(13.333), Inches(7.5)
    notes = ["# Group 5 — English speaker notes", "12-minute talk + 3-minute Q&A. Each role: 180 seconds.",
             "Member identities and contribution shares: NAME / ID / SHARE TO CONFIRM.",
             "Integration and LR supplement prepared with AI assistance for member review."]
    for index, spec in enumerate(slides, 1):
        slide = deck.slides.add_slide(deck.slide_layouts[6])
        panel(slide, 0, 0, 13.333, .12, TEAL)
        textbox(slide, .55, .32, 12.2, .37,
                f"GROUP 5  /  {spec.role.upper()}  /  {str(spec.seconds)+' SEC' if spec.seconds else 'BACKUP'}", 13, TEAL, True)
        textbox(slide, .55, .92, 12.2, 1.0, spec.title, 30, NAVY, True)
        for bullet_index, bullet in enumerate(spec.bullets):
            panel(slide, .6, 2.25 + bullet_index * 1.13, .08, .55, TEAL)
            textbox(slide, .85, 2.2 + bullet_index * 1.13, 5.35, 1.03, bullet, 22)
        if spec.chart:
            textbox(slide, 6.85, 1.85, 5.8, .45, spec.headline, 20, TEAL, True)
            editable_chart(slide, spec.chart)
            textbox(slide, 6.85, 5.82, 5.8, .82, spec.detail, 16, GRAY)
        else:
            panel(slide, 6.7, 2.12, 6.05, 3.9, LIGHT)
            textbox(slide, 7.0, 2.6, 5.4, 1.02, spec.headline, 28, TEAL, True)
            textbox(slide, 7.0, 3.95, 5.4, 1.8, spec.detail, 21, NAVY)
        panel(slide, 0, 6.86, 13.333, .64, NAVY)
        textbox(slide, .55, 6.98, 11.9, .4, spec.source, 11, WHITE)
        textbox(slide, 12.65, 6.96, .4, .4, f"{index:02}", 14, WHITE, True)
        native = f"{spec.role} | {spec.seconds} seconds | NAME / ID / SHARE TO CONFIRM\n\n{spec.script}\n\n{spec.source}"
        slide.notes_slide.notes_text_frame.text = native
        notes += [f"## Slide {index}: {spec.title}",
                  f"**{spec.role} — {spec.seconds} seconds** | NAME / ID / SHARE TO CONFIRM", spec.script, spec.source]
    pptx_path = output / "Group5_Presentation.pptx"
    pdf_path = output / "Group5_Presentation.pdf"
    deck.save(str(pptx_path))
    notes_path = output / "Group5_Speaker_Notes.md"
    notes_path.write_text("\n\n".join(notes) + "\n", encoding="utf-8")
    export_script = '''on run argv
tell application "Microsoft PowerPoint"
open (POSIX file (item 1 of argv))
set d to active presentation
save d in (POSIX file (item 2 of argv)) as save as PDF
close d saving no
end tell
end run'''
    subprocess.run(["osascript", "-e", export_script, str(pptx_path), str(pdf_path)], check=True, timeout=180)
    assets = output / "slide_assets"
    assets.mkdir(exist_ok=True)
    document = fitz.open(pdf_path)
    assert len(document) == 16
    contact = Image.new("RGB", (1920, 1080), "white")
    for index, page in enumerate(document):
        assert page.get_text().strip(), f"PDF slide {index + 1} has no text"
        pixmap = page.get_pixmap(matrix=fitz.Matrix(.5, .5), alpha=False)
        tile = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        tile.thumbnail((480, 270))
        contact.paste(tile, ((index % 4) * 480, (index // 4) * 270))
        if index in [2, 5, 10]:
            page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2), alpha=False).save(str(assets / f"slide_{index+1:02}.png"))
    contact.save(assets / "contact_sheet.jpg", quality=85)
    write_json(output / "slide_manifest.json", {
        "slides": slides, "main_slides": 12, "backup_slides": 4,
        "rendered_pdf_pages": len(document),
        "talk_seconds": 720, "qa_seconds": 180,
        "role_seconds": {role: 180 for role in ["Part 1", "Part 2", "Part 3", "Part 4"]},
        "editable": "Native PowerPoint text, shapes and charts with embedded workbooks",
        "source_csv_sha256": file_hash(ROOT / "results/final/model_comparison.csv"),
        "generator_sha256": file_hash(Path(__file__)),
        "artifacts": {p.name: file_hash(p) for p in [pptx_path, pdf_path, notes_path]}})
    print(f"Created {len(slides)} editable slides, PDF, English notes and manifest.")


if __name__ == "__main__":
    run()
