# Step 4 Deferred, External-Governance, and Structured-Flow Dispositions (2026-09-29)

The 15 rows outside both the emitting and held buckets, reconciled from
`target-report/target-dispositions-v2.csv` on main `dcf95ab4`
(pin `d7310c9a`).

Conservation: 615 emitting + 688 held + 12 deferred + 1 external-governance
+ 2 structured-flow = 1,318.

## 12 deferred (AmbiguousDeferred)

Target identity cannot be resolved from the source text; deferred for
source-workbook clarification. No fact emitted; no hold verdict recorded.

| Row | Source | Raw target |
|---|---|---|
| REL-00194 | Capture Physical Trades | Actualizations |
| REL-00312 | Manage Actualization Disputes | Actualizations |
| REL-00336 | Settle Intermediates | Actualizations |
| REL-00338 | Settle Other Commodities | Actualizations |
| REL-00340 | Settle Products | Actualizations |
| REL-00360 | Manage Accruals | Actualizations |
| REL-00363 | Manage Taxes | Actualizations |
| REL-00490 | Manage Product Exchange Agreements | Actualizations |
| REL-01128 | Crude/Feed Transportation Management | Actualizations |
| REL-01316 | Settlements | Actualizations |
| REL-00909 | Manage Brand Imaging | Network Design |
| REL-00921 | Maintain Tax Master Data | Determine Taxability |

Ten share the raw target "Actualizations" — the source text does not
identify which actualization process is meant.

## 1 external-governance (ExternalGovernanceReference)

| Row | Source | Raw target | Reason |
|---|---|---|---|
| REL-00022 | Maintain Supply Planning Master Data | Data Governance | Data Governance is an enterprise governance domain, never a process node under Commercial. |

## 2 structured-flow (StructuredFlowValue)

| Row | Source | Raw target | Reason |
|---|---|---|---|
| REL-00095 | Capture Product/Crude/Feedstock Price | contemporaneous assumption basis for Regional Backcasting | Information flowing into Regional Backcasting, not an activity; governed structured flow value per Q5. |
| REL-00104 | Capture Monthly Operating Plan | Monthly Operating Plan | Plan artifact, not a process, per the R1 plan-vs-artifact distinction. |

## Status

All 15 formally recorded. The 12 deferred rows await source-workbook
clarification (Hamid's domain). The structured-flow and external-governance
rows are correctly classified; no further action required.

Pre-reviewed by Cursor EPM on Slack (naming correction: the three
disposition values, not "non-held").
