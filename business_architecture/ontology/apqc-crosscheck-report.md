# APQC Downstream PCF v7.2.2 — Consistency Cross-Check

**Date:** 2026-09-17
**APQC source:** `business_architecture/reference/APQC-PCF-Downstream-Petroleum-v7.2.2.xlsx` (official Excel, downloaded 2026-09-17;
2,012 elements, 13 L1 categories, sheets 1.0–13.0 + Combined)
**Repo source:** `business_architecture/business_process/downstream_process_map.json` (680 nodes, L0–L6)
**Method note:** Part A is mechanical (exact ID lookup). Part B is a first-pass heuristic —
term-overlap between APQC element names and repo node names + breadcrumbs. It is a
*triage* signal, not a verdict: the repo's nodes are system-named (XPIMS, DPO, PPIMS…),
so vocabulary mismatch depresses scores even where the concept is covered. Every GAP
below needs human review before becoming a modeling decision. Raw scores:
`apqc_crosscheck_results.json`.

## Part A — Cited PCF ID verification (mechanical)

The repo's only genuine PCF citations are the six in the Modeling Guide's
"Process grounding" line. (Other 5-digit hits from a repo-wide grep were false
positives: an Ollama port, a Shell job-posting URL, a SQL row count, IRS document
numbers, and Turtle decimal literals.)

| Cited ID | Claimed as | v7.2.2 status |
|---|---|---|
| 12894 | wholesale/rack accounts | ✓ FOUND — [3.5.3] Manage wholesale/rack accounts |
| 12895 | lifting agreements | ✓ FOUND — [3.5.3.1] Establish lifting agreements |
| 12897 | rack clearances | ✓ FOUND — [3.5.3.3] Establish rack clearances |
| 12893 | credit adjudication | ✓ FOUND — [3.5.2.6] Adjudicate credit |
| 10153 | customer-management measures | ✓ FOUND — [3.3.5] Track customer management measures |
| 10006 | Manage Customer Service | ✗ **NOT FOUND** — in 7.2.2 "Manage Customer Service" is **20085** [6.0] |

**Result: 5 of 6 confirmed. One stale ID: 10006 → 20085.**
The v7.2.2 workbook's Difference Index is 0 on every row, so no element changed
between 7.2.1 and 7.2.2 — this renumbering is v5.0.3-era drift, not a recent change.
Fix already landed in PR #25 (the Modeling Guide now cites 20085).

## Part B — Coverage scan (heuristic triage)

Category averages (score = mean best term-overlap per L2 group; <0.34 GAP, 0.34–0.60 THIN):

| APQC L1 | Category | Avg | Read |
|---|---|---|---|
| 3.0 | Market and Sell Products and Services | ~0.42 | THIN — vocabulary artifact likely; repo covers trading/nominations deeply but in system terms |
| 4.0 | Deliver Physical Products | ~0.40 | THIN — same artifact; refining/logistics present under different names |
| 6.0 | Manage Customer Service | ~0.40 | THIN |
| 8.0 | Manage Information Technology (IT) | ~0.38 | THIN |
| 9.0 | Manage Financial Resources | ~0.40 | THIN |
| 13.0 | Develop and Manage Business Capabilities | ~0.40 | THIN |
| 1.0 | Develop Vision and Strategy | ~0.41 | THIN — likely deliberate: enterprise strategy is above this map's operational scope |
| 2.0 | Develop and Manage Products and Services | ~0.42 | THIN — likely deliberate: downstream sells commodities, not engineered products |
| 10.0 | Acquire, Construct, and Manage Assets | ~0.39 | THIN — partial real gap: no asset-maintenance depth beyond "Model and System Maintenance" |
| 11.0 | Manage Enterprise Risk, Compliance, Remediation, Resiliency | ~0.38 | THIN — 11.3 remediation (0.33) is a real candidate gap |
| 7.0 | Develop and Manage Human Capital | ~0.35 | GAP-leaning — "Human Resources" exists only as an ID-less L1 stub with no depth |
| 12.0 | Manage External Relationships | ~0.32 | GAP-leaning — 12.2 gov/industry relations, 12.3 board, 12.5 PR all ≤0.33 |
| 5.0 | Deliver Services | ~0.45 | THIN — likely deliberate: products business, not services |

### Review-first candidates (likely real gaps, not vocabulary)

1. **6.4 Manage product recalls and regulatory audits** (0.26) — no recall process in the map; fuel-quality events make this downstream-relevant.
2. **7.2 / 7.3 / 7.5 Recruit, on-board, reward employees** (0.27–0.34) — HR is an empty L1 stub.
3. **8.4 Manage information / data & analytics governance** (0.29) — the map names *systems* (XPIMS, DPO…) but has no information-management processes; notable given the data-product portfolio work.
4. **9.4 Manage fixed-asset project accounting** (0.30).
5. **11.3 Manage remediation efforts** (0.33).
6. **12.2 / 12.3 / 12.5 Government, board, and public relations** (0.27–0.33).
7. **10.x asset maintenance depth** — "Manage Site Assets (Tank, Rack, Etc.)" exists; preventive-maintenance planning does not.

### Likely deliberate scope boundaries (confirm, don't "fix")

- 1.0 strategy, 2.0 product development, 5.0 services — enterprise/commodity realities, not omissions.
- 3.x/4.x commercial core — covered in system-specific language; a mapping pass (not new processes) would raise these scores.

## Reverse direction (repo → APQC) — local extensions to keep

Not yet scored, but visible by inspection: renewables/RINs handling, emissions trading,
crude allocation decisions, and XPIMS/DPO/PPIMS-specific planning processes have no
APQC counterpart. Per the locked decision, these stay as deliberate local extensions;
the ontology should tag them as such (e.g. `dcterms:source` = repo, no `skos:closeMatch`).

## Recommended next single step

Human review of the 7 review-first candidates above, one at a time: for each, decide
**in scope → model it**, or **out of scope → record the boundary**. That decision log
becomes the `skos:scopeNote` / exclusion rationale in the ontology.
