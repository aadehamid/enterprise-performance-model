# APQC Scope Decisions

One decision per APQC gap candidate, taken with Hamid one at a time (2026-09-17).
Decisions accumulate here; they are applied to the model in a single pass later
(Step 3/4 of the ontology plan), followed by one consolidated proposal to update
`downstream_process_map.json` in the repo — not one edit per decision.

## Decision 1 — APQC 6.4 Manage product recalls and regulatory audits → IN SCOPE

Rationale: downstream-equivalent is off-spec/contaminated product events and
regulatory audits (EPA fuel programs/RIN, PHMSA, OSHA PSM), not consumer recalls.

To model (new, APQC-referenced):
- Finished-product quality management (counterpart to CM 1.2.5.1 feed quality)
- Product hold / quarantine and release
- Recall communications and effectiveness monitoring (20113, 20115)
- Regulatory report submission (20114)
- Trigger linking a quality failure to the CM 1.2.4.4.x claims chain
- Regulatory audit management, homed under EHS & Gov Reporting / CM 1.3.8.4

APQC source: PCF IDs 20110–20116, APQC Downstream Petroleum PCF v7.2.2,
`dcterms:references` on each new concept.

## Decision 2 — APQC 7.2/7.3/7.5 Human capital (recruit, onboard/develop/train, reward/retain) → IN SCOPE

Standing principle established: the ontology covers enabling functions, not only
the hydrocarbon value chain.

To model (new, APQC-referenced), filling the empty Human Resources L1 stub:
- 7.2 Recruit, source, and select employees (requisitions, sourcing, screening,
  new-hire/re-hire, applicant information) — PCF 10410, 10439–10444, 20123
- 7.3 Manage employee on-boarding, development, and training (orientation,
  performance, development, training delivery) — PCF 20599, 10469–10473
- 7.5 Reward and retain employees (rewards programs, benefits, assistance/
  retention, payroll) — PCF 10412, 10494–10497

Connections: org:Role / RACI layer (HR owns role definitions, competency,
certification); CM 1.3.6.1.4 Train and Certify AMPM Manager (governed by 7.3);
EHS & Gov Reporting (safety-training compliance); Finance (payroll).

## Decision 3 — APQC 8.4 Manage information (data/analytics governance) → IN SCOPE

Rationale: the map maintains master data but nothing governs it; conspicuous
for a knowledge-graph / data-product effort.

To model (new, APQC-referenced):
- Data, information, and analytic governance (20768), strategy and objectives
  (20766–20767)
- Enterprise data models and information architecture (20770–20775)
- Data ownership and stewardship responsibilities (20774)
- Information lifecycle planning, policies/standards, data administration
  (20776–20778)
- Content management: monitoring, feeds/repositories, usage audits, access
  control (20779–20784)

Connections: CM 1.3.7.1 master-data processes (governed by 8.4); data product
portfolio catalog; DQV quality measurements.

## Decision 4 — APQC 9.4 Manage fixed-asset project accounting → OUT OF SCOPE (boundary note)

Rationale: ERP/finance-system territory (capital planning, project codes,
capitalization, returns measurement); nothing in the ontology depends on it
(unlike HR→RACI and data governance→knowledge graph); map's Finance stub
deliberately thin.

Boundary note: refinery turnarounds blur capital projects and maintenance
expense — revisit if the 10.x asset-maintenance review surfaces turnaround
accounting.

## Decision 5 — APQC 11.3 Manage remediation efforts → IN SCOPE

Rationale: spill/release response and site cleanup are core downstream reality;
connects to the 6.4 work already scoped in (regulatory reports, effectiveness
monitoring) and to the EHS & Gov Reporting stub. Scoped to the
environmental/incident flavor, not the full enterprise-resiliency apparatus.

To model (new, APQC-referenced):
- Remediation plans, expert consultation, resource dedication (11201–11203)
- Legal investigation and damage-cause investigation (11204–11205)
- Policy amendment/creation post-incident (11206)

Connections: EHS & Gov Reporting L1 stub; CM 1.3.8.4 regulatory reporting;
6.4 regulatory-report submission.

## Decision 6 — APQC 12.2/12.3/12.5 External relationships → OUT OF SCOPE (boundary note)

Rationale: corporate-affairs processes (government/industry relations, board
relations, PR program) with no connection to the value chain, the RACI layer,
or the data products. Furthest from the operational core of all candidates.

Boundary note: the empty Legal & Corp Comm L1 stub remains as the recorded
home if scope ever expands; community relations around refinery sites is the
most likely future trigger.

## Decision 7 — APQC 10.x Asset-maintenance depth → IN SCOPE

Rationale: refinery/terminal maintenance is the operational core; turnarounds
are nine-figure events with no home in the map. Also gives the Decision 4
(9.4) turnaround capex-vs-expense boundary a home on the maintenance side.

To model (new, APQC-referenced):
- 10.3 Maintain productive assets: plan (19239), manage (19245), perform (19253)
- Turnaround planning and execution (downstream extension, no direct APQC
  equivalent at this depth)

Connections: Refining L1 area; Decision 5 (11.3) remediation (incidents drive
maintenance); Decision 4 boundary (turnaround capex vs. maintenance expense).

---

## Summary (2026-09-17)

| # | APQC area | Decision |
|---|-----------|----------|
| 1 | 6.4 Product recalls / regulatory audits | IN SCOPE |
| 2 | 7.2/7.3/7.5 Human capital | IN SCOPE |
| 3 | 8.4 Data/analytics governance | IN SCOPE |
| 4 | 9.4 Fixed-asset project accounting | OUT — boundary note |
| 5 | 11.3 Remediation efforts | IN SCOPE |
| 6 | 12.2/12.3/12.5 External relationships | OUT — boundary note |
| 7 | 10.x Asset-maintenance depth | IN SCOPE |

Standing principle: the ontology covers enabling functions, not only the
hydrocarbon value chain — but only where the ontology has a genuine hook
(HR→RACI, data governance→knowledge graph). ERP-native finance and
corporate-affairs processes stay out.
