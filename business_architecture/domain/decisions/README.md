# Decision records (EPM-DEC-001)

One file per decision: `EPM-DEC-001-NNNN-<slug>.md`, with context, decision,
alternatives, Hamid's recorded words, evidence, status and date. A record says
**Decided** only when Hamid has recorded the decision. A PR merge alone does
not decide it. See `docs/agents/domain.md` for the format.

Records 0001 to 0024 come from the grilling session on the handover plan
(2026-10-05).

| Record | Decision | Status | Questions |
|---|---|---|---|
| [EPM-DEC-001-0001](EPM-DEC-001-0001-ppc-consumer-status.md) | PPC is a planned consumer, not an active one | Decided | Q1 |
| [EPM-DEC-001-0002](EPM-DEC-001-0002-playbook-maintenance-rule.md) | Playbook maintenance rule | Decided (an amendment is proposed in EPM-DEC-001-0024) | Q2 |
| [EPM-DEC-001-0003](EPM-DEC-001-0003-phase1-tracking-and-batches.md) | Phase 1 tracking and batch format | Decided | Q3, Q4 |
| [EPM-DEC-001-0004](EPM-DEC-001-0004-customer-work-deferred.md) | Customer domain work waits for Hamid's additional details | Decided | Q5, Q6 |
| [EPM-DEC-001-0005](EPM-DEC-001-0005-ontology-data-scope.md) | What the ontology holds: concepts and public reference facts, no records of what happened | Decided | Q6, Q11, Q19, Q26 |
| [EPM-DEC-001-0006](EPM-DEC-001-0006-pricing-d1-market-data.md) | Pricing D1: Market Data is a separate domain | Decided | Q7 |
| [EPM-DEC-001-0007](EPM-DEC-001-0007-pricing-d2-commercial-risk.md) | Pricing D2: Commercial Risk owns price risk and hedging | Decided | Q8 |
| [EPM-DEC-001-0008](EPM-DEC-001-0008-pricing-d3-margin-measures.md) | Pricing D3: margin indicators are KPI measure definitions | Decided | Q16 |
| [EPM-DEC-001-0009](EPM-DEC-001-0009-pricing-d4-domain-name.md) | Pricing D4: the domain name | Decided | Q9 |
| [EPM-DEC-001-0010](EPM-DEC-001-0010-market-data-risk-definition-timing.md) | Define Market Data and Commercial Risk at Step 7 | Decided | Q17 |
| [EPM-DEC-001-0011](EPM-DEC-001-0011-mpc-gap-proposals-triage.md) | MPC-P01 to P09: rule on P02 now, the rest at Step 7 | Decided | Q10, Q14, Q18 |
| [EPM-DEC-001-0012](EPM-DEC-001-0012-mpc-p02-scope.md) | MPC-P02: propose IDs now, turnaround lifecycle later | Decided | Q15 |
| [EPM-DEC-001-0013](EPM-DEC-001-0013-core-release-timing.md) | Release `core` 1.0.0 after Phase 1 | Decided | Q12, and Q3 of the handover plan |
| [EPM-DEC-001-0014](EPM-DEC-001-0014-shacl-release-slice.md) | Build a small SHACL slice before the release; Step 9 order | Decided | Q13, Q23 |
| [EPM-DEC-001-0015](EPM-DEC-001-0015-step5-scope-reference-instances.md) | Step 5: classes plus public reference instances in a separate module; MPLX | Decided | Q19, Q27, Q28 (and Q21 of the handover plan) |
| [EPM-DEC-001-0016](EPM-DEC-001-0016-step6-p-plan.md) | Step 6: adopt P-Plan; occurrences belong to consumers | Decided | Q20 |
| [EPM-DEC-001-0017](EPM-DEC-001-0017-step7-overlay-order-kpi-seed.md) | Step 7: overlay order and KPI module seed | Decided | Q21, Q22 |
| [EPM-DEC-001-0018](EPM-DEC-001-0018-step10-publication.md) | Step 10: publication target | Decided | Q24 |
| [EPM-DEC-001-0019](EPM-DEC-001-0019-step11-all-green.md) | Step 11: what "all green" means | Decided | Q25 |
| [EPM-DEC-001-0020](EPM-DEC-001-0020-lpg-projection-guideline.md) | Adopt the ontology-to-LPG guideline: Step 12, design Rules 1, 2, 3 and 5, no reifiers | Decided | Q24, Q29, Q30, Q33 |
| [EPM-DEC-001-0021](EPM-DEC-001-0021-lpg-guideline-snapshot.md) | Where the LPG guideline lives in this repo | Decided | Q31 |
| [EPM-DEC-001-0022](EPM-DEC-001-0022-ontology-skill.md) | A company-neutral ontology skill in personal-agent-skills | Decided | Q32 |
| [EPM-DEC-001-0023](EPM-DEC-001-0023-external-ontologies-map-not-import.md) | Public ontologies: map to them, do not import them | Decided | Q34 |
| [EPM-DEC-001-0024](EPM-DEC-001-0024-playbook-is-a-method.md) | The playbook is a method; project decisions live in EPM-DEC-001 | Proposed | Follow-up to Q2 |
