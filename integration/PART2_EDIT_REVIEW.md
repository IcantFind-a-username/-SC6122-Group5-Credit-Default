# Review of Zhang Hanyu's uploaded Part 2 edit

Reviewed on 2026-09-07. Member commits `cafec5f` and `6bde3bd` each add the same PPTX bytes, respectively at the repository root and `submission/Group5_Presentation_new.pptx`. The original uploads are preserved.

Comparison against the pre-redesign master at `e93211b` establishes that the member changed only slide 6 bullet text and slides 4–6 speaker notes. All other slide text and notes match that older deck. The uploaded full deck therefore predates the confirmed names/IDs/shares, redesigned cover, removal of timing labels and revised RF importance/error pages. It must not replace the current master wholesale.

## Content assessment and integration

- Slide 4: the shorter oral explanation correctly describes 21 depth/leaf configurations, minimum leaf size 100, unlimited depth and test AP rounded from 0.2843/0.5221 to 0.284/0.522. Scope the improvement to this split, rather than an unrestricted claim about generalization.
- Slide 5: the 1.5 root threshold, 16.5%/70.1% fitting-node proportions and depth 18/134 leaves agree with the saved tree evidence. The member retains the association-not-causation caveat.
- Slide 6: the new focus on tuning outcomes is useful. The decision tree has the largest AP gain among these tested configurations; selected RF/XGBoost lead the point estimates and are very close. CV-before-test selection remains explicit. Add the LR post-hoc qualifier and update the handoff to Zhou's current importance/error-case scope.
- Import the revised scripts and comparison bullets into `integration/build_slides.py`, preserving the current titles, member metadata, layout, chart data, source lines and explicit transitions. Rebalance Part 2 rehearsal targets to 50/55/75 seconds (three minutes total) to allow the longer comparison explanation.
- Keep the AP-definition explanation in report, Q&A Q8 and backup slide 13; it need not be repeated in the main comparison bullets.

The current editable master is `submission/Group5_Presentation.pptx`; its PDF and Markdown notes are regenerated together. Other members' slide content and scripts are retained. No report metrics, model outputs or frozen experimental protocols are changed.
