# Formal review evidence — Step 4 (pinned baseline `6ab2197ba3fe6246bdb501391d22b71d0338d2c7`)

These batches are formal review evidence, not working files. Every row carries
`baseline_sha`. Decisions are recorded in the `decision` / `reviewer_rationale`
columns; blank means pending Hamid's review. The 53 and 14 rows' decisions
must complete before Step 4 promotion.

| file | rows | status 2026-09-24 |
|---|---|---|
| `53-changed-label-rows-for-review.csv` | 53 rows whose raw target label changed v1.1→v2 (Step 3d renames) | 35 approval-carried under the evidence-strengthening exception; 18 pending review |
| `14-new-historical-label-rows-for-review.csv` | 14 new historical-label rows (v1.2) | 2 R1 labels approved MigrationOnly; 12 pending (expected dispositions in `proposed_disposition`) |
| `11-slug-ancestor-descendant-rows-for-review.csv` | 11 slug-carried rows whose target is an ancestor/descendant of the source | REL-01309 approved (procedures-govern-parent); 10 held with `AncestorDescendantGovernanceAmbiguity` |
| `enabledby-mutual-review-batch.csv` | 4 rows: the two mutual-`enabledBy` pairs | All held (Hamid 2026-09-24: enablement not automatically reciprocal) |
| `nearness-sample-review-batch.csv` | 55-row stratified nearness-only sample (seed 20260924) | 50 approved; REL-01143 error-held; 4 held by governed-by stratum stop |
