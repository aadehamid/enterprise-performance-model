# Decision records (EPM-DEC-001)

One file per decision: `EPM-DEC-001-NNNN-<slug>.md`, with context, decision,
alternatives, Hamid's recorded words, evidence, status and date. A record says
**Decided** only when Hamid has recorded the decision. A PR merge alone does
not decide it. A decision recorded as "delegated under EPM-DEC-001-0028" counts as Hamid's recorded decision, within that record's scope. See `docs/agents/domain.md` for the format.

Records 0001 to 0024 come from the grilling session on the handover plan
(2026-10-05). Later records come from follow-up decisions in Claude Code sessions.

| Record | Decision | Status | Questions |
|---|---|---|---|
| [EPM-DEC-001-0001](EPM-DEC-001-0001-ppc-consumer-status.md) | PPC is a planned consumer, not an active one | Decided | Q1 |
| [EPM-DEC-001-0002](EPM-DEC-001-0002-playbook-maintenance-rule.md) | Playbook maintenance rule | Decided; amended by EPM-DEC-001-0024 | Q2 |
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
| [EPM-DEC-001-0013](EPM-DEC-001-0013-core-release-timing.md) | Release `core` 1.0.0 after Phase 1 | Decided; amended by 0025 and 0026 | Q12, and Q3 of the handover plan |
| [EPM-DEC-001-0014](EPM-DEC-001-0014-shacl-release-slice.md) | Build a small SHACL slice before the release; Step 9 order | Decided | Q13, Q23 |
| [EPM-DEC-001-0015](EPM-DEC-001-0015-step5-scope-reference-instances.md) | Step 5: classes plus public reference instances in a separate module; MPLX | Decided | Q19, Q27, Q28 (and Q21 of the handover plan) |
| [EPM-DEC-001-0016](EPM-DEC-001-0016-step6-p-plan.md) | Step 6: adopt P-Plan; occurrences belong to consumers | Decided | Q20 |
| [EPM-DEC-001-0017](EPM-DEC-001-0017-step7-overlay-order-kpi-seed.md) | Step 7: overlay order and KPI module seed | Decided; order item 1 amended by 0040 | Q21, Q22 |
| [EPM-DEC-001-0018](EPM-DEC-001-0018-step10-publication.md) | Step 10: publication target | Decided | Q24 |
| [EPM-DEC-001-0019](EPM-DEC-001-0019-step11-all-green.md) | Step 11: what "all green" means | Decided | Q25 |
| [EPM-DEC-001-0020](EPM-DEC-001-0020-lpg-projection-guideline.md) | Adopt the ontology-to-LPG guideline: Step 12, design Rules 1, 2, 3 and 5, no reifiers | Decided | Q24, Q29, Q30, Q33 |
| [EPM-DEC-001-0021](EPM-DEC-001-0021-lpg-guideline-snapshot.md) | Where the LPG guideline lives in this repo | Decided | Q31 |
| [EPM-DEC-001-0022](EPM-DEC-001-0022-ontology-skill.md) | A company-neutral ontology skill in personal-agent-skills | Decided | Q32 |
| [EPM-DEC-001-0023](EPM-DEC-001-0023-external-ontologies-map-not-import.md) | Public ontologies: map to them, do not import them | Decided | Q34 |
| [EPM-DEC-001-0024](EPM-DEC-001-0024-playbook-is-a-method.md) | The playbook is a method; project decisions live in EPM-DEC-001 | Decided (2026-10-06) | Follow-up to Q2 |
| [EPM-DEC-001-0025](EPM-DEC-001-0025-phase1-scope.md) | Phase 1 covers the source-correction backlog; other held rows wait | Decided; amended by 0026 | Follow-up to Q12 |
| [EPM-DEC-001-0026](EPM-DEC-001-0026-scoped-sequence-relation.md) | A scoped sequence relation in `core`, before 1.0.0 | Decided | Q1 to Q18 of the #226 design round |
| [EPM-DEC-001-0027](EPM-DEC-001-0027-mirror-raw-verbs.md) | Two mirror raw verbs, `provides-input-to` and `governs` | Decided | One question, 2026-10-12 |
| [EPM-DEC-001-0028](EPM-DEC-001-0028-delegated-decisions.md) | Claude decides the open questions of emitting the ontology on Hamid's behalf, from evidence; amended to Steps 5 to 12 | Decided | One instruction, 2026-10-12; amended 2026-10-13 |
| [EPM-DEC-001-0029](EPM-DEC-001-0029-core-1-0-0-release-design.md) | How `core` 1.0.0 is built: intake: targets, provenance, IRIs and the release package | Decided | Release implementation questions, 2026-10-13 |
| [EPM-DEC-001-0030](EPM-DEC-001-0030-organization-module-vocabulary.md) | The organization module's vocabulary: RACI assignments, control between legal entities, RACI levels | Decided (delegated under EPM-DEC-001-0028) | Step 5, slice 1, 2026-10-13 |
| [EPM-DEC-001-0031](EPM-DEC-001-0031-role-register.md) | The role register: the process map's 91 RACI role strings become 60 roles, merged on spelling only | Decided (delegated under EPM-DEC-001-0028) | Step 5, slice 2, 2026-10-13 |
| [EPM-DEC-001-0032](EPM-DEC-001-0032-raci-assignments.md) | The RACI assignments: one per source entry and role, nothing inferred from the hierarchy | Decided (delegated under EPM-DEC-001-0028; RACI scope by Hamid, 2026-10-13) | Step 5, slice 3, 2026-10-13 |
| [EPM-DEC-001-0033](EPM-DEC-001-0033-ref-mpc-module.md) | The ref-mpc module: MPC, MPLX, the control relationship, three segments and 13 refineries, each with a source and an as-of date | Decided (delegated under EPM-DEC-001-0028) | Step 5, slice 4, 2026-10-13 |
| [EPM-DEC-001-0034](EPM-DEC-001-0034-definition-to-run-pattern.md) | Step 6: a run links to the process definition it followed through prov:hadPlan; the ontology holds no runs | Decided (delegated under EPM-DEC-001-0028) | Step 6, 2026-10-13 |
| [EPM-DEC-001-0035](EPM-DEC-001-0035-step9-controlled-values.md) | Step 9: code-list values come from their own list; evidence links wait for the next core release | Decided (delegated under EPM-DEC-001-0028) | Step 9, 2026-10-13 |
| [EPM-DEC-001-0036](EPM-DEC-001-0036-lpg-projection-pipeline.md) | Step 12: the property-graph projection pipeline, with SHORTEN names, a SHACL subset in the graph, and listed release gaps | Decided (delegated under EPM-DEC-001-0028) | Step 12, 2026-10-13 |
| [EPM-DEC-001-0037](EPM-DEC-001-0037-module-release-candidates.md) | Step 10: the organization and ref-mpc modules, released as 1.0.0 after Hamid's approval; hosting decided against by Hamid, registration not pursued under the delegation (EPM-DEC-001-0039) | Decided (delegated under EPM-DEC-001-0028); Hamid approved the 1.0.0 releases, 2026-10-13 | Step 10, 2026-10-13 |
| [EPM-DEC-001-0038](EPM-DEC-001-0038-core-2-business-domains-and-sipoc.md) | core 2.0.0: business domains as a code list (Commercial, Marketing, IT Services, …), SIPOC planned inputs and outputs, two ranges; released as 2.0.0 | Decided (Hamid, 2026-10-13: SIPOC, the domain split, the 2.0.0 release and the SIPOC backlog; the build choices delegated under EPM-DEC-001-0028) | Hamid's answers, 2026-10-13 |
| [EPM-DEC-001-0039](EPM-DEC-001-0039-namespace-placeholder.md) | The w3id namespace is a placeholder and is not hosted (Hamid); under the delegation, nothing is registered and Step 10's "catalog resolves" gate is parked | Decided (Hamid, 2026-10-14: not hosted, placeholder; the follow-on items delegated under EPM-DEC-001-0028) | Hamid's message, 2026-10-14 |
| [EPM-DEC-001-0040](EPM-DEC-001-0040-kpi-module-seed.md) | The `kpi` module is seeded from Hamid's planner measure list, with personas as roles; the files stay out of the repo; amends 0017 | Decided (Hamid, 2026-10-18; the build choices delegated under EPM-DEC-001-0028) | Hamid's answers, 2026-10-18 |
| [EPM-DEC-001-0041](EPM-DEC-001-0041-licence-proprietary.md) | The ontology stays proprietary, all rights reserved; closes 0037 item 3 | Decided (Hamid, 2026-10-18; the follow-on items delegated under EPM-DEC-001-0028) | Hamid's answers, 2026-10-18 |
| [EPM-DEC-001-0042](EPM-DEC-001-0042-kpi-measure-classification.md) | Most planner measures are operational metrics; a KPI is a designation with a target and an owner; Crude Value to Breakeven is a decision-support indicator; mid-term turnaround work is optimization | Decided (delegated under EPM-DEC-001-0028) | Step 7, 2026-10-18 |
| [EPM-DEC-001-0043](EPM-DEC-001-0043-kpi-module-vocabulary.md) | The kpi module's vocabulary: measure definitions, the measure-kind code list, planning personas as roles, process links as context; built, not released | Decided (delegated under EPM-DEC-001-0028) | Step 7, 2026-10-18 |
