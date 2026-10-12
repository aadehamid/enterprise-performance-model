<!-- Hamid's words, verbatim from https://github.com/aadehamid/enterprise-performance-model/issues/205#issuecomment-6115309253 (fetched 2026-10-12). Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

Take this as my authorization

## Copy-paste response for issue #205

Please record the following as my source-author responses to Batch 1’s 13 questions.

For each **a** response, use the revised wording below instead of the original blanket “finishes before … starts” sentence. These sequences concern the relevant trade, delivery, settlement period, claim, or posting—not completion of an entire organizational process. Apply the source corrections and perform the fresh reviews; do not silently broaden conditional or activity-specific statements into unconditional process-wide relationships.

For Questions 6 and 10, record the sequence as an industry-informed reference-model assumption, not a publicly verified MPC procedure. Close the source-author questions without opening another evidence question. If the existing predicate cannot preserve the stated scope, close the row as not emitted with the semantic reason recorded.

### 1. REL-00193 — Capture Physical Trades → Confirmations Management

**a, with revised wording.**

“Capture Physical Trades (CM-1-2-1-3-3) records the agreed commercial terms and makes the required trade data available to Confirmations Management (CM-1-2-2-2) for prompt counterparty confirmation. Initial capture precedes submission for confirmation; discrepancies may require controlled correction of the captured record.”

This is an initial trade-level sequence, not permanent completion of all capture activity.

### 2. REL-00206 — Capture Financial (OTC) Trades → Confirmations Management

a, with revised wording.

“Capture Financial (OTC) Trades (CM-1-2-1-3-7) records the agreed transaction terms and makes the required trade data available to Confirmations Management (CM-1-2-2-2) for prompt counterparty confirmation. Initial capture precedes submission for confirmation; discrepancies and subsequent amendments are handled through controlled correction and confirmation procedures.”

This is an initial trade-level sequence, not permanent completion of all capture activity.

### 3. REL-00184 — Report Trades to SDR → Report Confirmation To SDR

b for the blanket finish-to-start sequence as written.

Swap creation reporting is triggered by execution, while applicable subsequent reporting is triggered by reportable events and changes. The existing scope note establishes a responsibility boundary, not a mandatory process-level handoff.

Do not add “Hands off … when complete.” Close the source-author review with a fresh HOLD verdict and the rationale “mandatory sequence not established.” Verify the scope of Report Confirmation To SDR against the applicable current reporting requirements; do not equate confirmation-related reporting with all continuation reporting automatically.

### 4. REL-01227 — Confirmations Management → Settlements

b for the blanket finish-to-start sequence as written.

Confirmation of the applicable trade terms is a settlement control, but settlement preparation, calculation, and reconciliation need not wait for all Confirmations Management activity to finish.

Suggested clarification:

“Confirmations Management (CM-1-2-2-2) establishes the agreed transaction terms used by Settlements (CM-1-2-4-1). Settlement preparation may proceed in parallel; unresolved confirmation discrepancies are subject to the applicable settlement approval and exception controls.”

Do not add “Hands off … when complete.” Close the source-author review with a fresh HOLD verdict and the rationale “mandatory process-level sequence not established.”

### 5. REL-00200 — Capture Storage Deals → Settle Terminal/Storage

a, with revised wording.

“Capture Storage Deals (CM-1-2-1-3-5) records the agreed storage-service terms before those terms are used by Settle Terminal/Storage (CM-1-2-4-1-14) to calculate and validate applicable charges. Settlement follows the agreement’s billing schedule and may occur periodically or in advance while the contract and storage operations remain active.”

The sequence concerns initial availability of the required terms, not completion of the storage contract or all physical activity.

### 6. REL-00188 — Capture Transmission Deals → Settle Power

a, with narrowed wording, adopted as a reference-model assumption rather than a verified MPC procedure.

“Where a power transaction involves a separately captured transmission arrangement, Capture Transmission Deals (CM-1-2-1-3-11) records the applicable terms before Settle Power (CM-1-2-4-1-15) calculates or validates the associated transmission-related charges. Other power-settlement activities may proceed independently.”

MPC’s disclosed electricity generation and grid sales support the power-business context, but do not establish its specific transmission-deal workflow. Close the source-author question with this conditional sequence and preserve its scope in the fresh review.

### 7. REL-01291 — Actualizations → Settlements

a, with revised wording.

“For each physical delivery or settlement period, Actualizations (CM-1-2-3-1) records and validates the relevant actual quantities and movement facts before Settlements (CM-1-2-4-1) uses those inputs to calculate or validate the corresponding charges. Settlement preparation and contractually permitted provisional billing may proceed before every input is final; subsequent corrections are handled through controlled true-ups.”

This is a delivery- or period-specific sequence, not completion of all actualization activity.

### 8. REL-01289 — Trade Capture → Actualizations

a, with revised wording.

“For trade-linked physical movements, Actualizations (CM-1-2-3-1) follows initial Trade Capture (CM-1-2-1-3), using the captured trade and associated movement references to record and validate actual quantities and other applicable movement facts. Subsequent amendments and corrections remain controlled.”

This does not require completion of all trade-capture activity and does not imply that every internal movement must belong to a commercial trade.

### 9. REL-00307 — Manage Lease Contract → Perform Lease Actualization

a, with revised wording.

“Perform Lease Actualization (CM-1-2-3-1-6) follows establishment of the applicable effective lease-contract terms and required division-of-interest references maintained under Manage Lease Contract (CM-1-2-1-2-8), applying them to the relevant delivery or production period. Subsequent changes and corrections are handled through controlled updates.”

Manage Lease Contract remains ongoing; the agreement does not have to expire or all contract-management activity finish before actualization begins.

### 10. REL-00351 — Capture Transmission Deals → Settle ISO/Power Pools

a, with narrowed wording, adopted as a reference-model assumption rather than a verified MPC procedure.

“Where ISO/power-pool settlement includes items arising from a captured transmission arrangement, initial capture of the relevant arrangement under Capture Transmission Deals (CM-1-2-1-3-11) precedes validation of those items under Settle ISO/Power Pools (CM-1-2-4-1-7). Other settlement activities may proceed independently.”

Use the same reasoning as Question 6. Close the source-author question with this conditional sequence; do not imply that all ISO/power-pool settlement depends on transmission-deal capture.

### 11. REL-00319 — Capture Financial (OTC) Trades → Settle Financial OTC Trades

a, with revised wording.

“Settle Financial OTC Trades (CM-1-2-4-1-11) follows initial Capture Financial (OTC) Trades (CM-1-2-1-3-7), using the captured transaction terms and applicable settlement-period inputs to calculate and validate payment obligations, subject to the required confirmation, reconciliation, and authorization controls.”

Settlement may occur periodically while the trade remains active. Subsequent amendments and corrections are handled through controlled updates.

### 12. REL-00374 — Settlements → Manage AR/AP & Actuals

a, with revised wording.

“Manage AR/AP & Actuals (CM-1-2-4-2-4) follows the applicable settlement calculation and invoice validation under Settlements (CM-1-2-4-1) when posting the corresponding receivable, payable, or adjustment. Accruals and other financial-actuals activities may proceed independently; subsequent settlement changes are reflected through controlled adjustments.”

The prerequisite is the relevant calculation and validation—not payment completion or the end of all settlement activity.

### 13. REL-01294 — Demurrage Management → Manage AR/AP & Actuals

a, with revised wording.

“Demurrage Management (CM-1-2-4-4) precedes the claim-specific posting activities within Manage AR/AP & Actuals (CM-1-2-4-2-4) by providing the calculated, validated, and authorized demurrage amount and supporting references. Subsequent claim revisions are reflected through controlled accounting adjustments; unrelated AR/AP activity proceeds independently.”

This does not require closure of the entire demurrage lifecycle or prevent policy-compliant accruals and disputed-item accounting.
