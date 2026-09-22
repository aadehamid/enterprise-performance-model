# Business Process Architecture Playbook — Downstream Process Definitions

**Status:** Living document. Updated as each review batch completes; final update when Step 3c closes.
**Owner:** Hamid
**Started:** 2026-09-21 (covering work from 2026-09-17)

## 1. About this document

The [ontology playbook](ontology-playbook.md) records how the downstream process map becomes an ontology — the standards chosen and the build decisions. This playbook is its sibling: it records how the **process definitions themselves** were decided — the method that authored 477+ definitions across 39+ review batches, the durable architecture rules those batches locked, the ownership boundaries between functions, and the external sources that inform each part of the business process. Together the two playbooks make the whole business process architecture reproducible: the ontology playbook answers *how the structure was built*, this one answers *how the content was decided and why it can be trusted*.

**How to maintain it:** when a review batch merges, append its entry to §5 (Batch log) and move any new durable rule into §6 (Decision log). After the final batch, regenerate the traceability appendix (§8) and record completion here. Never rewrite history — correct with dated amendments.

**Companion files:**
- `step3c-review-handoff.md` — the operational manual for running a review batch (the *how-to*; this document is the *what-and-why*)
- `step3c-reviewer-instructions.md` — the locked reviewer gate rules
- `build/output/step3c-definition-authoring-workbook.xlsx` — the artifact all of this governs
- `build/scripts/step3c-source-traceability.py` → `build/output/source-to-process-traceability.md` — the generated source-to-process appendix (§8)
- `ontology-playbook.md`, `competency-questions.md`, `apqc-scope-decisions.md`

---

## 2. Why every workbook field is captured — useful *and* rich

A taxonomy alone (names in a hierarchy) is *useful*: people can navigate it. The workbook captures much more per concept, deliberately, because the ontology formed from it must also be *rich* — able to answer competency questions, carry evidence, bound automated agents and KPIs, and survive contact with real organizational authority. Every column earns its place by what it becomes in the ontology:

| Workbook field | Ontology role | Why it makes the ontology rich, not just useful |
|---|---|---|
| `name` | `skos:prefLabel` | The locked identity anchor. Never edited during review, so every downstream artifact (TTL, identity map, KPIs) stays joinable. |
| `alt_labels` | `skos:altLabel` | Retrieval and synonym richness: search, RAG, and humans find the concept under the words they actually use. Also carries the naming queue's normalized labels without breaking identity. |
| `definition` | `skos:definition` | The core semantic payload — what the concept *is*, written to downstream oil & gas reality, not generic business prose. |
| `scope_note` | `skos:scopeNote` | The single richest field: boundaries, the durable rules (§6), fact-dependent legal statements, and who-decides assignments. This is what lets an agent or analyst use a concept *safely* — knowing what the process may and may not do. |
| `in_scope` / `out_of_scope` | boundary assertions | Explicit inclusion/exclusion lists, with every exclusion naming its owning process. Disambiguation becomes machine-checkable instead of implied. |
| `related_concepts` | typed non-hierarchical relations (enables, uses-input, governed-by, precedes, …) | Turns a tree into a graph. Value chains, control dependencies, and hand-offs become traversable — the difference between a org-chart-like list and an ontology that can answer "what breaks downstream if this process fails?" |
| `concept_type_check` | class discrimination (process vs capability) | Lifecycles and standing control clusters behave differently for modeling, KPIs, and simulation; the type test (§7) keeps them honest. |
| `primary_purpose` | teleology | One sentence of *why the process exists* — the seed for outcome KPIs and the test for scope drift. |
| `key_inputs` / `primary_output` | input/output flow semantics | Makes the value chain explicit end to end (evidence → bill → cash → close), enabling lineage and data-product design. |
| `process_horizon` | temporal dimension | Strategic through intraday: aligns each process to the planning/monitoring cadence it actually runs on, so KPI frequency and operating rhythm can be derived, not guessed. |
| `responsible_domain` | accountability dimension | Who operates it — including cross-functional forms where authority genuinely spans functions. Placement in the taxonomy deliberately does *not* assign ownership; this field does. |
| `reference_sources` | provenance (register IDs) | Every claim that leans on a regulator, statute, or standard is traceable to a registered source with scoped permitted use (§8). Evidence-linked, not vibes-linked. |
| `terminology_notes` | decision provenance | The batch-stamped record of what was decided, what Hamid corrected, which labels are queued, and which open issues exist — the audit trail that makes the content defensible. |
| `open_questions` / `status` / `parked_children` | workflow governance | Review-state machinery: approved rows carry no open questions; nothing parks silently; parked tree changes bind to the PTC register. |
| `apqc_*` columns | external mapping evidence | The APQC cross-check that seeded each row — kept as comparison evidence, never as authority (APQC informs, local decisions govern). |

The consequence: the ontology built from this workbook can answer not only "what processes exist?" (useful) but "who is allowed to decide X, on what evidence, under which rule, informed by which source, feeding which downstream process?" (rich). That is what makes it a foundation for KPIs, agents, data products, and governance rather than a diagram.

---

## 3. The operating model of the review

Human-in-the-loop, batch-based, evidence-first:

1. **Batches are hierarchy-led and parent-first** — an L4 with its L5 children (5–26 rows), so every child is defined inside an already-agreed parent frame.
2. **Package before edit** — the full proposed content (every field, every row) plus explicit questions (Q1–Q6) is delivered for Hamid's review *before* any cell changes. The package always recommends; it never surveys.
3. **Approve with refinements** — every batch. Hamid's wording is applied verbatim; his corrections become precedents for all later batches.
4. **Apply → validate → verify → draft PR** — scripted apply touching only the workbook; validation gate to the healthy baseline (`blocking=0 questions=0 notes=15 open_ptc=1`); cell-level diff proving only the intended rows changed and no name moved; draft PR that only Hamid merges.
5. **Every rule cites its batch** ("the b14 payment-authority rule"), so any definition can be traced to the decision that shaped it and the PR that recorded it.

Full operational detail (scripts, validator behavior, git mechanics, package format) lives in `step3c-review-handoff.md`; this playbook does not duplicate it.

---

## 4. Research and evidence standards

- **Downstream oil & gas is the frame** for every definition — rack, terminal, fleet card, franchise, excise reality, not generic business-process boilerplate.
- **High-quality sources only:** regulators (EPA, FTC, IRS, OFAC, CFPB, U.S. Treasury), statutes (PMPA, ECOA), standards bodies (API, FASB, PCI SSC), each verified at review time (via web-search metadata where direct fetch is blocked, with access dates recorded).
- **Need-driven registration:** a source enters the Reference register only when a definition leans on it. If a specific statute/standard is *named* in canonical row text, it is registered with scoped permitted use; if a legal statement stays generic or jurisdiction-undefined, it is recorded as an open issue instead (no generic sources).
- **Sources are evidence, never authority:** every register entry's permitted-use text states what the source may inform and which internal owner makes the determinations it does not — the same discipline the ontology playbook applies to standards.
- **Fact-dependent statement pattern** for law: "where <condition>, <obligation> may apply depending on <facts>; applicability and required procedures are <Legal/Compliance/Tax/Finance>'s determination." The workbook never states a legal conclusion.

---

## 5. Batch log

> Entries 21–39 were authored in the current working period and are recorded in full. Entries 1–20 predate this playbook; their durable outputs are captured in §6 (each rule keeps its bNN citation), and their full entries are to be backfilled from PR history (#\<57) — *dated amendment welcome*.

**Batches 1–20 (summary, to backfill):** covered the strategy, planning, supply, trading, logistics, and early commercial branches. Durable outputs still governing later work: conditional-relation handling for vocabulary-missing types (b10); trading counterparty credit risk cluster (b11); the payment-authority rule and Trading Settlements (b14); `responsible_domain` as free text (b15); enterprise compliance boundaries (b16); the alt-label collision lesson (b18); early source registrations (APQC, OSHA, EPA, EIA, CFTC, ISDA, CCRO, API MPMS, FMCSA, IRS P510, FASB ASC 815 and peers).

| # | Cluster (slugs) | PR | What was decided |
|---|---|---|---|
| 21 | Marketing Analysis (CM-1-3-1, 26 rows) | #57 | Durable analysis rule (analyze-and-inform); Insight & Metrics as first marketing capability; personal-data governance statement; competitor-information prohibition; KPI Store metric boundary; SRC-EIA-PMM-001. |
| 22 | Marketing Strategy (CM-1-3-2, 22 rows) | #58 | Canonical three-layer rule (Analysis informs → Strategy develops/recommends/maintains → Execution operationalizes); governance-safe wording (never "decides"); fact-dependent PMPA statement; SRC-PMPA-001 with provision traceability. |
| 23 | Pricing Strategy & related (CM-1-3-3-1/-2/-3, 17) | #60 | Measurement-framework rule (nominate, never approve/publish KPIs); pricing governance under delegated approvals; fact-dependent Robinson-Patman; competition-information rule; rebate-design guardrail; SRC-FTC-RP-001. |
| 24 | Network, Communications, Operating Model (CM-1-3-3-4/-5/-6, 18) | #62 | Network Design as blueprint (never investment owner); communications control statement; contactability rule (consume, never create consent); POS/price-display exclusions; SRC-FTC-ADM-001. |
| 25 | Innovation & Change (CM-1-3-4-1/-2/-3, 12) | #63 | Innovation-consumes-analysis rule; regulated-party EPA fuels gate (fact-dependent); stage gates coordinate-never-clear; development ≠ launch; SRC-EPA-FF-001. |
| 26 | Licensing & IP, Collaboration, Portfolios (CM-1-3-4-4/-5/-6, 17) | #64 | First cross-functional `responsible_domain`; legal-determination exclusion; Finance valuation lock (transfer/tax/royalty excluded); no-implied-obligations rule; SRC-USPTO-001. |
| 27 | Sales & Communications Planning (CM-1-3-5, 26) | #65 | Forecast-versus-targets rule + glossary (forecast/target/quota/plan/actual); prepare-and-release recast of "Implement" rows + release-authority statement; promotion-readiness framework; no-causality-overclaim. |
| 28 | Channel, Sales & Pricing Execution (CM-1-3-6-1/-2/-3, 16) | #66 | Partner-onboarding coordination model (each control keeps its owner); non-binding quote statement + content spec; no-self-exception pricing rule; price changes *submitted to* Price Master Data, never deployed into it; first `daily` horizon. |
| 29 | Rebates, Plan Execution, Loyalty & Cards (CM-1-3-6-4/-5/-6, 24) | #67 | Loyalty-vs-card internal split; fact-dependent PCI DSS scope (architecture/data-handling, not branding); four cards financial boundaries; fraud/chargeback boundary; refined Robinson-Patman; SRC-PCI-DSS-001. |
| 30 | Brand Standards & Commercial Compliance (CM-1-3-6-7/-8, 5) | #68 | Conformance-not-enforcement wording; technical-standards exclusion; narrow Commercial Agreement Compliance reading; commercial audit ≠ Internal Audit; completed the Execution L3. |
| 31 | Master Data (CM-1-3-7-1, 7) | #69 | **Governed Submission and Stewardship Rule** (durable); cross-functional stewardship capability; Party/Account customer-domain model; consent separation; location-master gap logged as open taxonomy issue. |
| 32 | Commercial Terms, Quoting & Portal (CM-1-3-7-2, 7) | #70 | Sales-motion vs O2C splits (Develop vs Issue Quote; deal vs framework contracting); Contract Management (b09) boundary; qualified quote legal status; portal channel-not-process rule; payment-method offering model. |
| 33 | Order Fulfillment (CM-1-3-7-3, 7) | #71 | Commercial-order vs physical-logistics split; order/custody/title/billing/payment status model; allocation rules applied-not-made; fulfillment evidence received-linked-validated, never created; returns as authorization & coordination. |
| 34 | Credit & Risk (CM-1-3-7-4, 7) | #72 | **Credit authority rule** (delegated model); policy-qualified exposure aggregation over the credit hierarchy; mandatory-criteria rule (finance never overrides Compliance/Legal); KYC as framework execution only; SRC-OFAC-001, SRC-REG-B-001. |
| 35 | Customer Requests & Inquiries (CM-1-3-7-5, 7) | #73 | **Resolution-routing rule** (one case record, one loop; substance to owners); immediate safety/security incident escalation; case records ≠ master data; governed-answer safeguard; completed CM-1-3-7. |
| 36 | Customer Invoicing & Billing (CM-1-3-8-1, 6) | #74 | **Billing Integrity Rule** (durable); channel-dependent billing evidence; transaction-time vs compliance-time taxability split; self-billing conditions; single controlled credit-memo instrument. |
| 37 | Cash Application, A/R & Revenue Accounting (CM-1-3-8-2, 7) | #75 | **Cash Application Integrity Rule** (durable); recording-not-receiving Treasury boundary; unapplied cash as owned aged exception; revenue-evidence model (approved unbilled bases); SRC-FASB-ASC606-001. |
| 38 | Collection & Disputes (CM-1-3-8-3, 5) | #76 | **Receivables Resolution Separation Rule** (durable); disputed-portion-only holds; payment plans vs concessions; Finance-authority write-offs (accounting event ≠ forgiveness); SRC-FASB-ASC326-001. |
| 39 | Accounting, Reporting & Compliance (CM-1-3-8-4, 8) | #77 | **Accounting Execution Rule** (durable) with governed close exceptions; compliance = O2C control-operation evidence only; taxability recommendations for Tax approval; intercompany execution per approved transfer-pricing basis; royalty/fee stream administration; completed CM-1-3-8. |
| 40 | Service & Support (CM-1-3-9, 15 rows) | #80 | Enablement and Delivery as continuous capabilities (Delivery reclassified in review); canonical request/enable/deliver/measure rule with case-to-service-event linkage; HR/IT/Facilities/contact-center corporate boundaries; five-way service data distinction; service-event outcome taxonomy + billable-evidence rule; workforce-data and formal-research controls; five generic-name alt labels. |
| 41 | Terminal commercial operations (CM-1-3-10, 4 rows) | #81 | **Final intake batch.** Dual book-ownership/system-of-record boundary between Trade Capture and terminal sales-deal capture (durable); terminal authorization record-versus-decision rule with explicit lifecycle; Tax/Legal-approved rack-tax status consumed, not determined; customer lifting nominations vs shipper-side nominations (b33 split completed); rack allocation enforcement with title/rights limitation and four-way control separation; controlled deal-capture corrections; four preferred labels queued (Capture Terminal Sales Deal high-priority). |
| 42 | L0 scheme roots + Step 3c closeout (2 rows) | #82 | **Closeout batch.** Downstream Operations and Enabling Functions approved as scheme roots (taxonomy/navigation anchors, `not-process`, no authority conferred by grouping); Midstream scoped to the downstream enterprise model, no categorical industry claim; gate amended with the frozen SCHEME_ROOT_APPROVED whitelist (option A, Hamid); naming-pass queue committed as controlled Draft artifact EPM-BA-NAMING-QUEUE-001 (`step3c-naming-pass-queue.md`, 92 entries in six categories); `CM-1-1-3-5-3` retained as the sole intentional pending business-evidence hold. Final state: approved=498 pending=1 blocked=3 retired=1. |

---

## 6. Decision log — durable architecture rules

These rules were locked by explicit review decisions and govern all content, present and future. Each cites the locking batch; canonical wording lives verbatim in the cited rows' scope notes.

**Named integrity/authority rules (Decision-Log grade):**
1. **Governed Submission and Stewardship Rule (b31).** Accountable processes decide business content; stewardship validates authority and completeness, applies via controlled workflows, effective-dates, versions, preserves lineage, and distributes. Submitters never write directly; stewardship never self-authorizes. Generalizes to KPI Store content, measurement catalogs, reference data, and semantic controlled terms.
2. **Billing Integrity Rule (b36).** Bills only from validated, linked, governed inputs; every correction is a controlled successor document with linkage, reason code, authorization, and audit trail; nothing edited in place or deleted.
3. **Cash Application Integrity Rule (b37).** Receipts apply only per remittance evidence and approved rules; every exceptional amount is an owned, aged exception item; a payment changes nothing it pays against; reversals/offsets/refunds/write-offs only as controlled authorized events.
4. **Receivables Resolution Separation Rule (b38).** Disputes adjudicate on the evidence chain; collections recover without adjudicating, adjusting, crediting, or writing off; Finance owns allowances and write-offs; nothing is netted, absorbed, forgiven, or reclassified outside authority.
5. **Accounting Execution Rule (b39).** O2C accounting executes under Finance/Tax-approved policy, calendars, and delegations; close proceeds only on evidenced feeds or a documented Finance-approved exception (compensating control, owner, plan, aging/true-up); everything prepared keeps evidence lineage.
6. **Credit authority rule (b34, refining b11).** Finance owns appetite, reserves, impairment; Credit decides limits, risk codes, holds, releases, and credit-driven closure under policy and delegation; every consuming process applies without waiver or override; exceptions follow delegation/escalation.
7. **Payment-authority rule (b14).** Commercial processes prepare, validate, and submit authorized payment/settlement/reimbursement instructions; they never move funds. Treasury owns instruments, banking, and movement.
8. **Resolution-routing rule (b35).** The service capability owns the commercial customer-request experience (intake through closure coordination), answers only from governed data or confirmed owner outcomes, and routes all substance to owning processes. Safety/quality/environmental/security signals escalate immediately, outside normal prioritization.
9. **No-self-exception (b28, generalized).** No process waives, overrides, or bypasses a control it applies; implementers submit through governed controls (price and rebate changes to Price Master Data; portal transactions to owning-process validation; order desks never release credit holds).
10. **Release-authority rule (b27).** Planning prepares and releases approved deliverables; execution executes what is released and approves nothing (no creative, claims, budgets, prices).
11. **Marketing analysis rule (b21) + three-layer rule (b22).** Analysis informs; Strategy develops, recommends, and maintains approved direction under delegation (never "decides" unilaterally); Design/Planning/Execution operationalize.
12. **Measurement/KPI rule (b21/b23).** All process metrics are evidence-layer; candidate KPIs route only through the KPI Store (Enterprise Measurement Catalog → Candidate KPI Register → Enterprise KPI Catalog); no process approves or publishes KPIs.
13. **Forecast–target–plan glossary (b27, extended b32/b33).** Forecast = unbiased expectation; target/quota = leadership commitment; plan = monetized/operating intent; operational signals (order book, revenue plan) are non-committal and never override forecasts or allocations.
14. **Consent/contactability rule (b24, hardened b31/b35).** Processes consume permissioned contactability data under the separately governed consent framework; the existence of contact data never creates marketing permission; suppression processes "without undue delay."
15. **Evidence rules for physical operations (b33).** Physical processes create custody-transfer/measurement evidence; commercial processes receive, link, validate for commercial completeness, and retain it — never create or restate quantities. Order, fulfillment, inventory, custody, title, billing, and payment statuses are distinct states with distinct owners.
16. **Deal-capture boundary rule (b41).** Trade Capture vs terminal sales-deal capture is a dual test: trading-book governance AND commercial system-of-record. A deal is captured in the terminal-commercial record only where the approved operating model names the commercial/O2C terminal sales record as system of record; where an arrangement has both representations, the authoritative record, interface, and reconciliation responsibility must be explicitly defined, and neither process may create duplicate uncontrolled deal records. A trading-book deal creating terminal lifting rights is referenced by governed deal identifier and consumed through controlled integration, never re-created.
17. **Terminal authorization rule (b41).** Terminal-loading authorization and credential records enforce approved upstream decisions (master identity, credit, KYC, Tax, safety/carrier, Security, commercial agreement) and never decide them; the authorization lifecycle is explicit (configuration → activation → monitoring of upstream status → suspension/revocation → audit-trailed reactivation only on approved restoration); Loading-Authorized Party is a governed role/relationship, not merely an access-control flag.
18. **Loading control-separation rule (b41).** Allocation, credit, tax, and terminal/safety controls are separate questions answered by separate owners; a successful allocation does not imply a successful loading authorization if another control fails. Rack allocation enforcement applies commercial supply-position and lifting limits only — never title transfer, tax liability, custody, quality, driver safety, or terminal sequence.

**Ownership locks (who decides, everywhere):** Finance — accounting/revenue-recognition/costing policy, appetite, reserves, write-offs, valuation, close, consolidation. Treasury — instruments, banking/acquirer arrangements, funds movement. Tax — positions, interpretations, filings, taxability rules, transfer-pricing policy. Legal/Compliance — all legal determinations (PMPA franchise remedies, Robinson-Patman, ECOA/Reg B, sanctions/AML frameworks, consumer-collection conduct, competition information). Credit — the credit envelope. Security — card-data/PCI scope, identity/access standards, fraud investigation. IT — platforms, deployment, integration operations (business owns configuration content). Quality/EHS/Operations — product disposition, incidents, physical work. Data Governance — the customer-domain (Party/Account/role) model and data standards.

**Structural distinctions that keep look-alike rows apart:** compose-vs-issue quotes and deal-vs-framework contracting (b32); transaction-time vs compliance-time taxability (b36/b39); operational performance reporting vs reported-sales audit (b30); case records vs master data (b35); receivables reconciliation "settlement" vs Trading Settlement (b37); royalty-stream administration vs collections execution (b39); loyalty program vs card program within one capability (b29); customer lifting nominations vs shipper-side carrier nominations (b41, completing the b33 split); confirmed commercial lifting outlook vs physical loading schedule (b41); scheme roots vs business concepts — the two L0 roots are taxonomy/navigation anchors (`not-process`, definition and scope only, no authority conferred by grouping), approved under the frozen SCHEME_ROOT_APPROVED gate whitelist (b42).

---

## 7. Modeling conventions

- **Process vs capability test:** children that are heterogeneous *concurrent controls* over an ongoing operation → `capability` (Insight & Metrics, Licensing & IP, Loyalty & Cards, Master Data, Commercial Terms, Credit & Risk, Service, Receivables Resolution, Accounting & Compliance). Children forming a *lifecycle with variants* → `process` (Order Fulfillment, Billing, Cash Application, Rebates). All capabilities are `continuous`.
- **Horizons** reflect the true operating signal; `daily` is used sparingly and only where the cycle is genuinely daily (sales pricing, card acceptance, billing runs, receipt recording/application/reconciliation, order-book refresh). "Event-driven with daily/intraday cycles" and "continuous with periodic cycles within" are recorded patterns.
- **`responsible_domain`** defaults to the operating branch; L4s whose control authority genuinely spans functions carry a cross-functional value (in Hamid's exact framing per batch), with children keeping the operating home and the L4 scope note stating that taxonomy placement assigns no single owner.
- **Naming:** locked names are never edited; preferred normalized labels accumulate as alt labels (word-level changes only — case/punctuation-only normalizations queue without alt labels) plus the naming-pass queue for a future taxonomy cycle.

---

## 8. Source-to-process traceability (generated appendix)

The complete mapping of **every registered external source → the process areas and rows it informs**, with each source's permitted-use limits, is generated from the workbook itself so it can never drift:

```
python3 business_architecture/ontology/build/scripts/step3c-source-traceability.py
```

Output: [`build/output/source-to-process-traceability.md`](build/output/source-to-process-traceability.md). Regenerate after every batch and at completion. As of 2026-09-21 it maps 46 cited sources across 462 citing rows (4 registered sources currently uncited from workbook rows, retained as earlier-step evidence; zero citations without a register entry).

Reading guide: each entry shows the source's organization, reference, access/verification record, authority type, the permitted-use limitation (what the source may inform and which internal owner makes every determination it does not), and the process areas and rows citing it. This is the register's promise made visible: **evidence, traceable to exactly the parts of the business process it informs — and no further.**

---

## 9. Completion checklist (fill in when Step 3c closes)

- [x] Final batches (CM-1-3-9, CM-1-3-10) merged (#80, #81); batch log entries appended above.
- [x] Held rows dispositioned with Hamid (b42): the two L0 roots approved as scheme roots; `CM-1-1-3-5-3` retained pending as the intentional business-evidence hold (batch 05 decision) — do not force it approved; pre-intake backfill remains a Step 3d authored pass (do not grow PRE_INTAKE_APPROVED).
- [x] PTC-001 partially resolved in Step 3d; PTC-001-B confirmed as intentional strategy-ownership hold 2026-09-22 (Hamid) — Step 3d closed with that exception; PTC register updated.
- [x] Traceability appendix regenerated against the finished workbook (#81).
- [x] Naming-pass queue extracted into the controlled Draft artifact `step3c-naming-pass-queue.md` (EPM-BA-NAMING-QUEUE-001, b42). Execution is the first Step 3d activity: Critical semantic collision category gates semantic publication; the queue itself authorizes no renames.
- [ ] Batches 1–20 log entries backfilled from PR history (dated amendment).
