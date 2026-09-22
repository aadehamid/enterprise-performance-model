# Ontology Playbook — Downstream Process Map

**Status:** Living document. Updated as each plan step completes.
**Owner:** Hamid · **Built with:** Kailey
**Started:** 2026-09-17

## About this document

This is the working record of how the downstream process map becomes an
ontology. It captures the plan, the decision at every step, the answer each
step produced, and — most importantly for handover — *why* each standard was
chosen and what was deliberately rejected.

**How to maintain it:** when a plan step completes, append its entry to
§3 (Step log) and move any new durable decision into §4 (Decision log).
Never rewrite history — correct it with a dated amendment so the team can
see what changed and why.

**Companion files:**
- `competency-questions.md` — the merged competency-question baseline (the
  acceptance test for the whole build)
- `apqc-scope-decisions.md` — the per-candidate
  APQC scope review record
- `build/` — reproducible build scripts (`step2-identity-map.py`,
  `apqc_crosscheck.py`) and their generated outputs under `build/output/`

The copies under `business_architecture/ontology/` in the repo are the
published versions; `~/workspace/ontology-build/` holds working copies.

---

## 1. What we are building

**Source of truth.** The business processes in
`business_architecture/business_process/downstream_process_map.json` in the
`aadehamid/enterprise-performance-model` repo (680 nodes, levels L0–L6).
We model *those* processes — we do not copy a reference framework into the
model.

**Consistency reference.** The APQC Process Classification Framework for
Downstream Petroleum, v7.2.2. Every local process is checked against APQC;
nothing in our model may contradict it. Where we deliberately diverge, the
divergence is recorded as a boundary note, not hidden.

**End state.** A standards-based ontology (RDF) published as a versioned
DCAT catalog: a SKOS taxonomy of the process hierarchy, process definitions
separated from executions, explicit RACI responsibility assignments, system
and data-product linkages, SHACL validation shapes, and SPARQL regression
tests derived from the competency questions.

**Non-goals.** The ontology defines what things *are* — it does not
calculate KPIs, does not execute processes, and does not replace the ERP,
the KPI store ("the Store"), or the in-platform assistant (Genie). One
ontology; everything else points at it.

---

## 2. The plan

| Step | Name | Status |
|------|------|--------|
| 0 | APQC reference alignment (v7.2.2, vendored workbook, ID corrections) | ✅ Done 2026-09-17 |
| 1 | Foundations: competency questions; URI, language, version, license, module policies | ✅ Done 2026-09-18 |
| 2 | Identity normalization (680 nodes; preserve IDs as notation; mint IDs for 11 ID-less stubs) | ✅ Done 2026-09-18 |
| 3 | SKOS taxonomy (one ConceptScheme, broader/narrower, labels, definitions, notation) | ✅ Done 2026-09-18 |
| 3b | Definition triangulation (APQC candidates + EIA/web agreement; 1 adopted, 10 rejected at the human gate) | ✅ Done 2026-09-18 |
| 3c | Human definition authoring — semantic-intake workbook; 42 review batches → **498/503 approved** (2026-09-21); 1 pending (intentional business-evidence hold, batch 05), 3 blocked (PTC-001), 1 retired; taxonomy regenerated from the closed workbook via PR #83 (675/680 defined, 14,403 triples; Phase-1 capture under provisional `intake:` annotations) | ✅ Done 2026-09-21 |
| 3d | Tree reconciliation — naming pass first, then the consolidated repo-JSON tree pass (PTC-001). Summary of the completed step; the sub-logs below break it down. | ✅ Completed with explicit open exceptions 2026-09-22 |
| 3d-a | Naming Pass Closure Log — 92/92 queued renames executed across 7 batches (PR #84, #85, #89, #91, #92, #94, #96, #98, #100, #103): critical collisions, authority-risk, scope-ambiguity, directionality-missing, generic-operational, normalization-only (mechanical then judgment). Final naming state 682 concepts, 14,481 triples, 317 altLabels. | ✅ Closed 2026-09-22 |
| 3d-b | PTC-001 Tree Remediation Log — PR #86 (Commercial Development tombstone + 2 reparented L3s + 2 Candidate L2s); PR #87 definition mini-batch; PTC-001-B confirmed as intentional strategy-ownership hold (Hamid, 2026-09-22). PTC-001 stays open until PTC-001-B closes. | ✅ Partially resolved; hold by design |
| 3d-c | R1 Refining Structural Reclassification — decision package approved as Candidate 2026-09-22 (tombstone re-anchor confirmed); implementation PR #108 merged 2026-09-22 (merge b75fd991). 42 concepts reparented with stable slugs/IRIs/notations; two promoted L2s (Refinery Planning and Optimization; Refinery Production Planning and Scheduling); new Candidate R&T L2; tombstone re-anchored under Planning & Scheduling; reviewed RO→Refining interface relation materialized. 683 concepts, 14,496 triples (+15), 681 broader links. | ✅ Candidate → Implemented 2026-09-22 |
| 3d-d | R2 backlog (open by design) — operating-execution layer (unit operations, line-ups, blend execution, process control); maintenance/turnaround ownership question; R2 Refinery Vocabulary and Operating-Lifecycle package (turnaround/shutdown/startup/plan/schedule distinctions); Energy & Utility Management temporary-placement review trigger. | ⏳ Open |
| 4 | Process-definition ontology (ProcessDefinition/ProcessType; systems, variants, lanes, flags, capabilities, value streams) | Planned |
| 5 | ORG + RACI (roles as `org:Role`; explicit n-ary ResponsibilityAssignment) | Planned |
| 6 | Interfaces and PROV-O (planned inputs/outputs vs observed executions; `prov:Activity` only for occurrences) | Planned |
| 7 | Cross-model integration (link processes, value streams, capabilities, systems, data products; resolve empty O2C outputs, Loss Control ownership) | Planned |
| 8 | APQC scope review (seven candidates, one at a time) | ✅ Done 2026-09-17 |
| 9 | SHACL (labels, identifier policy, hierarchy integrity, controlled values, references, profiles) | Planned |
| 10 | DCAT publication (catalog → versioned dataset → distributions) | Planned |
| 11 | SPARQL regression tests (missing RACI, systems, products, orphans, lanes, ownership) | Planned |

Note: Step 8 was completed early (it was originally sequenced after
integration) because the scope decisions shape the foundations. The plan
order is otherwise unchanged.

---

## 3. Step log

### Step 0 — APQC reference alignment ✅ (2026-09-17)

**What we did.**
- Aligned to APQC Downstream Petroleum PCF **v7.2.2** (Excel + PDF,
  published 2025-05-30). Verified the workbook: 2,012 PCF elements,
  13 top-level categories, every Difference Index = 0 (no material
  element changes vs 7.2.1).
- Updated repo references from the v5.0.3 third-party mirror to the
  official APQC v7.2.2 listings.
- Vendored the official workbook at
  `business_architecture/reference/APQC-PCF-Downstream-Petroleum-v7.2.2.xlsx`
  with the required APQC/IBM attribution in `reference/README.md`.
  License check: APQC/IBM grant perpetual, worldwide, royalty-free use,
  copying, publishing, modification, and derivative works provided the
  copyright notice and attribution travel with copies.
- Ran a cross-check of all 680 process-map nodes against APQC
  (report: `business_architecture/ontology/apqc-crosscheck-report.md`).
  Five of six repo-cited PCF IDs verified; one was stale:
  **Manage Customer Service cited as 10006 (v5.0.3) is 20085 in v7.2.2**
  — corrected.
- Delivered via PR #25
  (`update/apqc-pcf-7.2.2`), commits authored as
  `aadehamid <aadehamid@gmail.com>` — **merged 2026-09-18**.

**Decisions.** APQC is a consistency reference, not the source model
(§4). Cited APQC IDs are verified against the workbook, not trusted
from older references.

### Step 8 — APQC scope review ✅ (2026-09-17)

**What we did.** Reviewed seven APQC gap candidates one at a time.
Each got an in-scope/out-of-scope call with rationale and connection
points, recorded in
`business_architecture/ontology/apqc-scope-decisions.md`.

| # | APQC area | Call |
|---|-----------|------|
| 1 | 6.4 Product recalls / regulatory audits | **In scope** — downstream equivalent is off-spec/contaminated product events; connects to claims chain, finished-product quality, EHS |
| 2 | 7.2/7.3/7.5 Human capital | **In scope** — fills the empty HR L1 stub; feeds the RACI layer |
| 3 | 8.4 Data/analytics governance | **In scope** — the map maintains master data but governs none of it; required for a knowledge-graph effort |
| 4 | 9.4 Fixed-asset project accounting | **Out** — ERP-native; nothing in the ontology depends on it (boundary note; revisit if turnaround accounting surfaces) |
| 5 | 11.3 Remediation efforts | **In scope** — spill/release response; environmental-incident flavor |
| 6 | 12.2/12.3/12.5 External relationships | **Out** — corporate affairs; no hook into value chain, RACI, or data products (boundary note) |
| 7 | 10.x Asset-maintenance depth | **In scope** — turnarounds are nine-figure events with no home in the map |

**Standing principle established:** the ontology covers enabling functions,
not only the hydrocarbon value chain — but only where the ontology has a
genuine hook (HR→RACI, data governance→knowledge graph). ERP-native finance
and corporate-affairs processes stay out.

**How scope decisions are applied:** they accumulate in the decision log;
they are *not* applied to `downstream_process_map.json` one at a time.
After the modeling pass, one consolidated proposal (new nodes with parent
and level) goes to the repo. Every new process gets an L0–L6 level from
the existing hierarchy — no level-less nodes.

### Step 1 — Foundations ✅ (complete)

**Competency questions** — reviewed and approved by Hamid; merged
baseline of 44 questions in `competency-questions.md`, locked 2026-09-18.
These double as the Step 11 SPARQL regression tests: the exam is written
before the coursework. Constraints section removed at Hamid's direction —
constraints are not being modeled; the Customer/Party domain is.

**URI policy — decided 2026-09-18.**
- Base: `https://w3id.org/lsc/ontology/` (w3id.org persistent-identifier
  service; `lsc` = Lagos Specialty Chemicals).
- Patterns: `…/process/{slug}` for taxonomy concepts;
  `…/modules/{module}` for module namespaces
  (`core`, `party`, `kpi`, `organization`).
- **Not tied to a person or a project.** Rationale: usernames change and
  people change roles; project names get rebranded (this repo already
  went through one). Only the company abbreviation appears, and even
  that sits behind w3id.org redirects — a future rebrand updates one
  redirect, not 680 identities.
- **Local IDs are preserved, never replaced by APQC IDs.**
  `CM 1.2.1.3` → slug `CM-1-2-1-3`, recorded as `skos:notation`. APQC
  element IDs (e.g. `20110`) attach via `dcterms:references` only.
  Rationale: the repo is the source of truth; most local processes have
  no APQC counterpart and vice versa.
- **The 11 ID-less stubs get minted slugs** (`L1-human-resources`,
  `L0-downstream-operations`, …) — a slug is simply the URL-friendly
  identifier coined where none existed.
- **No version in the URI.** Identity survives definition changes;
  versions ride on `owl:versionInfo` (answers competency question A-18
  structurally).
- Open action: register `w3id.org/lsc` (small request to the w3id.org
  repo; does not block modeling).

**Language policy — decided 2026-09-18.**
- Primary language: English. Every human-readable literal carries `@en`
  (`"Create Claim"@en` — untagged and tagged literals are different RDF
  terms; tagging everything avoids silent SPARQL mismatches).
- One `skos:prefLabel` per language per concept (the official name);
  aliases in `skos:altLabel`.
- `skos:definition` required on every concept, in English.
- Additional languages later slot in as `@fr`, `@ar`, … — no remodeling.

**Version policy — decided 2026-09-18.** SemVer per module and per
release; URIs never change; deprecation via `owl:deprecated` +
`dcterms:isReplacedBy`, never delete. Full operational detail in
Appendix B.

**License policy — decided 2026-09-18.**
- The ontology artifacts are **proprietary, all rights reserved**.
  Hamid is the IP owner. Rationale: the ontology describes LSC's actual
  operations (commercial processes, refinery planning, systems) —
  competitively sensitive. Can be opened later; cannot be un-opened.
- **APQC content remains usable.** The APQC/IBM license grants
  perpetual, worldwide, royalty-free use, copying, publishing,
  modification, and derivative works provided the copyright notice and
  attribution travel with copies. Attribution ≠ open licensing — the
  two coexist.
- Team guidance: reference PCF IDs freely (`dcterms:references`);
  quote element names/descriptions sparingly, each marked APQC-sourced;
  adapt wording openly where downstream context needs it (derivative
  works allowed); carry the APQC/IBM notice on every distribution via
  `dcterms:rights` on the dataset. Do not republish whole APQC branches
  as LSC's own — the repo's processes lead (source-of-truth principle).

**Module policy — decided 2026-09-18.**
- Four modules, each with its own namespace, version, SHACL shapes,
  and owner:
  - `core` — process taxonomy + process definitions. Depends on nothing.
  - `party` — Party, CustomerAccount, PartyRole,
    TransactionPartyParticipation. Depends on nothing.
  - `kpi` — Named KPI definitions. Depends on `core` and `party`.
  - `organization` — roles and RACI ResponsibilityAssignments. Depends
    on `core` only — `org:Role` (internal positions) and
    `party:PartyRole` (external commercial roles) are different beasts;
    no `organization` → `party` dependency.
- Rules: dependencies point one way, no cycles (enforced by CI);
  cross-module use is by URI reference, never by redefinition
  (define once, reference everywhere); modules version and validate
  independently; minor/patch approved by module owner, majors by Hamid.

- **`party` is the sole concept-owning module for the Customer domain.**
  There is no `customer` module by design. Customer-domain *processes*
  live in `core` (O2C chain), customer-grained KPIs in `kpi` (bound to
  Party/Account/Role), RACI over customer-facing processes in
  `organization` — the domain is a view across modules, its concepts
  anchored in `party` (2026-09-18).

### Step 2 — Identity normalization ✅ (2026-09-18)

All 680 nodes now have exactly one URI slug; zero collisions, zero
orphans (verified by script, not by eye).

- **669 ID'd nodes:** slug derived mechanically — `CM 1.2.1.3` →
  `CM-1-2-1-3` (spaces and dots become hyphens). All 669 IDs were unique
  and all matched the strict `CM <dotted-number>` pattern, so the
  derivation is injective. Original codes preserved as `skos:notation`.
- **11 ID-less stubs:** minted `L{level}-{name}` slugs
  (`L0-downstream-operations`, `L1-refining`, `L1-midstream`,
  `L0-enabling-functions`, `L1-supply-chain-mgmt`, `L1-finance`,
  `L1-shared-services`, `L1-process-excellence-it`,
  `L1-human-resources`, `L1-legal-corp-comm`, `L1-ehs-gov-reporting`).
  Minted slugs double as the proposed repo `id` values for the
  consolidated repo-JSON proposal (after the modeling pass).
- **Artifacts** (in `business_architecture/ontology/build/`):
  `step2-identity-map.py` (reproducible script),
  `output/step2-identity-map.json` (680 rows: uri, slug, level, name,
  skos_notation, parent_slug, minted, proposed_repo_id),
  `output/step2-identity-report.md`.
- **Delivered** via PR #26 (`ontology/foundations`), with the playbook,
  competency questions, APQC scope decisions, cross-check report, and
  all build scripts/outputs under `business_architecture/ontology/` —
  **merged 2026-09-18** (main, as of today, also carries PR #25's APQC
  v7.2.2 work).

### Step 3 — SKOS taxonomy ✅ (2026-09-18)

The core module's taxonomy as Turtle: 680 `skos:Concept`s, 3,660
triples, in stable document order.

- **ConceptScheme:** the core module namespace URI itself —
  `https://w3id.org/lsc/ontology/modules/core` — doubles as the
  scheme (one URI, one thing: the module's entire current content *is*
  the taxonomy). Carries `dcterms:title`/`description` and
  `skos:hasTopConcept` for the two L0 roots.
- **Per concept:** `skos:inScheme`, exactly one `skos:prefLabel` (`@en`),
  `skos:notation` on all 669 ID'd nodes (codes correctly untagged —
  notations are identifiers, not prose), `skos:definition` where the
  repo provides one, `skos:broader` on all 678 non-root concepts.
  `skos:narrower` not materialized (entailed via `owl:inverseOf`).
- **Validation (rdflib, mechanical):** parses clean; 680 concepts; one
  `@en` prefLabel each; every concept in scheme; 678 broader links, no
  dangling targets, no self-references; 2 top concepts; zero untagged
  prose literals; Turtle round-trip lossless.
- **Known gap, not invented:** 503 concepts had no `skos:definition`
  (the repo describes only 177 nodes). The language policy requires one
  per concept — Step 3b (2026-09-18) triangulated 1 adoption;
  **Step 3c** (2026-09-18) human-authored the 14 L1–L3 gaps with Hamid.
  192/680 concepts now carry definitions; 488 gaps remain (all L4–L6),
  for future authoring passes. A Step 9 SHACL shape can flag the
  unfilled ones.
- **Deliberately excluded:** RACI, systems, lanes, and all other node
  fields — Steps 4/5. This file is the taxonomy, nothing more.
- **Artifacts:** `~/workspace/ontology-build/step3-skos-taxonomy.py`,
  `step3-taxonomy.ttl`, `step3-taxonomy-report.md`.
- **Delivered** via PR #28 (`ontology/taxonomy-definitions`, opened and
  merged 2026-09-18, together with Step 3b) — `downstream_process_map.json`
  untouched.

### Step 3c — human definition authoring ✅ (2026-09-18, complete)

The 14 L1–L3 definition gaps from the Step 3b workqueue, authored one
at a time with Hamid: 10 L1 enabling/value-chain functions (Commercial
& Marketing, Refining, Midstream, Supply Chain Management, Finance,
Shared Services, Process Excellence & IT, Human Resources, Legal &
Corporate Communications, EHS & Government Reporting) and 4 commercial
planning stubs under C&M › Planning & Scheduling (Regional
Optimization, Regional Backcasting, Refinery Planning, Distribution
Backcasting).

- **Working method:** draft → Hamid's wording (most L1s are his, verbatim
  or near-verbatim) → approved definition + scope note recorded in
  `step3c-authored-definitions.json` with parked child concepts,
  planned Step 8 children, and terminology notes.
- **Boundary rules locked in the decision log:** primary-purpose (not
  asset-location) classification; domain placement questions for SCM,
  C&M, Refining, Midstream, Distribution, Finance, PE&IT, HR, Legal,
  EHS; Finance owns financial governance/transactions while domains own
  the operational event; Shared Services executes but never replaces
  the accountable functional owner; "Shared Services delivers IT
  support on behalf of Process Excellence & IT"; the commercial
  planning loop (Optimization → Refinery Planning → Refining execution
  → Backcasting) and its distribution mirror.
- **APQC candidates:** 5 more false matches rejected at the human gate
  during authoring (total 10 rejected): "Process returns"→PE&IT,
  "Develop human resources strategy"→HR function, "Determine corporate
  incentives"→Legal & Corp Comm, "Manage reporting processes"→EHS,
  "Supply chain resilience"→Regional Optimization.
- **Merge:** `step3-skos-taxonomy.py --authored` adds `skos:definition`
  + `skos:scopeNote` + `dcterms:source` (human-authored, approved by
  Hamid, dated) per concept; validation asserts hold. Taxonomy now:
  **680 concepts, 678 broader links, 192 definitions, 3,660 triples.**
- **Delivered** via the Step 3c PR (new branch off main, after PR #28
  merged 2026-09-18) — `downstream_process_map.json` untouched.

### Step 3c — semantic intake + L4 review batches ✅ (2026-09-21, complete)

The L1–L3 pass above is closed. Authoring continues on L4–L6 against a
workbook whose contract changed after that pass. This log records why
the gate was rewritten before the next batch.

- **#31 (2026-09-18) — workbook contract.**
  `step3c-definition-authoring-workbook.xlsx` became a 6-sheet
  semantic-intake workbook: Start Here, Review & authoring, Column
  guide, Controlled vocabularies, Reference register, External
  mappings. Nine Phase 1/2 columns sit before `status`. Status vocab
  is now `pending | approved | blocked | retired`. No RDF emission,
  no taxonomy/JSON/script change.
- **#32 (2026-09-19) — review batch 01.**
  Five L4 children of Regional Optimization / Refinery Planning
  approved with Phase 1 + Phase 2 filled. `CM-1-1-4-6` Commercial
  Development left `pending` (`mixed/needs-review`); accepted tree
  move parked as **PTC-001** in `step3c-parked-tree-changes.md`.
  Workbook counts: 20 approved / 483 pending. Taxonomy still 192/680
  — the five new rows have not been `--authored` yet.
- **This follow-up — gate sync (v2026-09-19).**
  Same move as #30 after #29: retarget the locked reviewer guide and
  `step3c-workbook-validate.py` to the live workbook. Phase 1 is
  required on new approvals. The 15 #29 rows are listed in
  `PRE_INTAKE_APPROVED` and flagged as NOTE when Phase 1 is empty —
  not silently waived, not blocked, not backfilled here.
  `CM-1-3-3-5-6` missing `scope_note` stays BLOCKING.
- **Still not in scope.** ~~Emitting the new fields as RDF; merging
  batch 01 into the TTL;~~ backfilling Phase 1 onto the 15; applying
  PTC-001 to `downstream_process_map.json` (now Step 3d, below).
- **Taxonomy regen from the workbook (2026-09-20, PR #59).**
  The "still not in scope" RDF emission above is now done, mechanically:
  `build/step3-skos-taxonomy.py` gained a `--workbook` overlay and the
  TTL was regenerated from the 281 approved rows — 680 concepts, 9,999
  triples, 458/680 definitions, 239 altLabels, 281 APQC references. Definition precedence:
  workbook-approved > human-authored L1–L3 > step3b adoption > repo
  description (all 14 authored + the 1 adoption are now approved workbook
  rows; non-workbook concepts verified triple-identical — no regression).
  Phase-1 capture is preserved verbatim under the provisional `intake:`
  namespace (see decision log); Step 4 promotes it to real properties.
  Blocked rows are definition-less; the retired row is `owl:deprecated`
  (`dcterms:isReplacedBy` waits for Step 3d). Sequencing agreed with
  Hamid: regen now (parallel to review batches) → finish 3c → 3d tree
  reconciliation → Step 4 design together.

- **Closeout (2026-09-21, batch 42, PR #82).** Step 3c is finished:
  approved=498, pending=1 (`CM-1-1-3-5-3`, the intentional business-evidence
  hold from batch 05 — not forced), blocked=3 (PTC-001), retired=1
  (`CM-1-1-4-6`); gate blocking=0, questions=0, notes=15, open_ptc=1.
  Hamid's **option A** decision admitted the two L0 scheme roots
  (`L0-downstream-operations`, `L0-enabling-functions`) as the only approved
  `not-process` rows via a frozen `SCHEME_ROOT_APPROVED` whitelist, mirroring
  the `PRE_INTAKE_APPROVED` pattern. Batches 23–41 covered Offer/Pricing/
  Channel (23), Network/Communications/Operating Model (24), Visioning/Concept/
  Product Development (25), Order Management, SCM, Finance/Accounting, Service
  & Support, and Terminal Commercial Operations (41).
- **Final TTL regen (2026-09-21, PR #83).** Per Hamid's sequencing decision
  (regen once at the end of Step 3c, not per batch): 680 concepts, 14,403
  triples, 675/680 defined (498 workbook + 177 repo descriptions); the 5
  definition-less are the 3 blocked, 1 retired, 1 pending hold. 182
  non-workbook concepts verified triple-identical to the PR #59/#61 snapshot.
  L0 roots defined; naming queue (92 renames) NOT applied — labels stay as
  locked in Step 3c.
- **Carried forward.** `step3c-naming-pass-queue.md` (EPM-BA-NAMING-QUEUE-001,
  Draft): 92 queued renames in six categories; the **Critical semantic
  collision** category (duplicate prefLabels) gates semantic-model
  publication and runs first in Step 3d. The queue authorizes no renames by
  itself — proposals go to Hamid for review like any batch.

### Step 3d — tree reconciliation 🔄 (PTC-001 partially resolved 2026-09-21)

The successor to Step 3c, registered here as a numbered step rather than a
note, so it can be scheduled rather than remembered.

Definition batches are forbidden from editing
`downstream_process_map.json`, the TTL, or the build scripts. Structural
problems found while authoring are therefore parked in
`step3c-parked-tree-changes.md` as PTC entries. Step 3d is the single
consolidated pass that applies them.

- **First 3d activity — the naming pass (added 2026-09-21, batch 42).**
  The Step 3c intake completed with 498 approved rows (PR #82) and a
  controlled rename backlog: `step3c-naming-pass-queue.md`
  (EPM-BA-NAMING-QUEUE-001, Draft), 92 queued renames in six categories.
  The **Critical semantic collision** category (duplicate prefLabels)
  gates semantic-model publication and runs first; the queue authorizes
  no renames by itself — proposals go to Hamid for review like any
  batch, and each executed rename promotes the queued label to prefLabel
  with the old name kept as alt label (subject to the collision and
  refinement rules recorded 2026-09-21, below), then sweeps the workbook,
  TTL regen, identity map, and cross-references, and re-runs the gate.
- **Phase 1 executed and merged 2026-09-21 — all 9 critical collisions.** All 9
  critical collisions renamed per Hamid's approval (2026-09-21), with two
  refinements over the queued labels: `CM-1-1-1-1` → **Produce Demand
  Forecast** (verb-led; `Demand Forecasting` is NOT kept as an altLabel
  because the L3 parent keeps it as prefLabel) and the six
  `Define KPI Framework` rows take domain-specific labels with the
  shared generic label NOT kept as an ontology altLabel (scoped
  historical aliases such as `Define KPI Framework (Offer)` recorded in
  the identity/migration map). The sixth KPI row (`CM-1-3-3-5-7`,
  Marketing Communications) was discovered after the initial 8-rename
  execution and renamed in a follow-up commit per Hamid's decision
  the same day. PR #84 (8 renames) and PR #85 (9th rename) both merged
  by Hamid 2026-09-21 — **nothing merged on assumption**.
  Approved labels:
  `CM-1-1-1-1` → Produce Demand Forecast; `CM-1-1-3-7` → Inventory
  Management (`Inventory` kept as altLabel); `CM-1-1-3-7-12` → Monitor
  and Control Inventory Positions (`Manage Inventory` kept as altLabel);
  `CM-1-3-3-1-4` → Define Offer Measurement Framework;
  `CM-1-3-3-2-5` → Define Pricing Measurement Framework;
  `CM-1-3-3-3-5` → Define Channel Measurement Framework;
  `CM-1-3-3-4-4` → Define Network Measurement Framework;
  `CM-1-3-3-6-5` → Define Operating Model Measurement Framework;
  `CM-1-3-3-5-7` → Define Marketing Communications Measurement Framework.
  No definitions, hierarchy, process identities, authority boundaries,
  source evidence, slugs, or IRIs change. The 9th rename lived on branch
  `step3d/naming-kpi6-marcomms` (from merged main `86d6fbb`); PR #85 merged
  by Hamid 2026-09-21 — **nothing merged on assumption**. The taxonomy is
  unpublished with no external consumers (Hamid, 2026-09-21), so no
  deprecation period or consumer notice is needed; the repository-wide
  cross-reference sweep was still run (workbook, identity map,
  terminology notes; TTL regenerated with the exact PR #83 invocation —
  byte-identical reproduction verified before the edits). The follow-up
  9th rename regenerated again with the same invocation: 680 concepts,
  14,397 triples (the expected −1: the promoted altLabel removed,
  prefLabel changed in place), 675/680 definitions, 678 broader links.
- **Label-governance policy (standing, 2026-09-21).** Labels are governed
  presentation metadata; stable slugs/IRIs are concept identity. Never
  use a prefLabel or workbook name as a join key, DAX lookup key, RLS
  condition, contract key, API key, KPI identity, or logic condition —
  use stable identifiers for technical relationships. Retain historical
  labels as altLabel only when uniquely resolvable and semantically
  safe.
- **PTC-001 partial resolution — executed and merged 2026-09-21 (PR #86).**
  Hamid approved the revised consolidated proposal
  (`files/ptc-001-tree-proposal.md`, four review adjustments adopted):
  new Candidate L2 **Financial Planning and Performance Management** under
  Finance hosting **Plan Budgets** (L3); new Candidate L2 **Refinery
  Performance and Risk Coordination** under Refining hosting **Coordinate
  Site Business Risk Management** (renamed, L3); **Commercial Development**
  tombstoned as `owl:deprecated` (kept in JSON/identity map/TTL, removed
  from active navigation); **Develop Strategic Business Plan** stays
  `blocked` under the named **PTC-001-B** strategy-ownership decision.
  682 concepts, 13 minted stubs. PTC-001 stays open until PTC-001-B closes.
- **PTC-001 definition mini-batch — authored and merged 2026-09-21 (PR #87).**
  The four rows left `pending` by the tree pass got full Phase 1 + Phase 2
  authoring, parent-first: the two Candidate L2 stubs and the two
  reparented L3s (Plan Budgets; Coordinate Site Business Risk Management).
  The independent review came back APPROVE-WITH-NOTES; two non-blocking
  cleanups were applied before merge per Hamid's call: (1) the risk L3's
  scope note now states the hybrid cadence — event-driven for new/changed
  risks, incidents, breaches, and escalations, with periodic monitoring
  and review of ownership, treatment plans, and status; (2) the Refining
  L2's scope note states that refinery performance oversight remains at
  capability level pending the future Refining-domain decomposition, so
  the risk-coordination child is never misread as the owner of
  throughput/yield/performance management. The `approve` wording in Plan
  Budgets is retained deliberately — the terminology note fences it to the
  budget-review workflow the process administers while final approval stays
  with the delegated authority. Workbook: 505 rows, 502 approved
  (1 intentional pending hold, 1 blocked PTC-001-B, 1 retired); gate
  blocking=0, questions=0. TTL: 682 concepts, 14,472 triples, 679/682
  defined. No new duplicate prefLabel groups; tombstone and blocked row
  untouched.
- **Authority-risk naming batch — executed and merged 2026-09-21 (PR #89).**
  The second naming-pass category: 6 labels that overstated each concept's
  mandate, renamed per Hamid's approval 2026-09-21 — `CM-1-2-4-2-12` →
  Maintain Trading Accounting Procedures and Guidance; `CM-1-2-5-2-3` →
  Recommend Feedstock Slate And Run Rate (protects the PTC-002
  decide-vs-advise boundary: S&T recommends, Refinery Planning decides);
  `CM-1-2-6-1` → Supply Network Participation Analysis; `CM-1-2-6-3-1` →
  Coordinate S&T Source-Point Supply Operations; `CM-1-3-4-5-4` → Develop
  Portfolio Recommendations and Track Decisions; `CM-1-3-5-1` → Sales
  Planning. Old labels retained as safe altLabels (plus two
  workbook-recorded alternatives); 16 `related_concepts` cross-references
  swept to the new labels with slug annotations; workbook
  breadcrumb/parent display columns refreshed for the renamed rows and
  their descendants; identity-map `prior_name`/`name_change_note` overlays
  added with all 10 pre-existing overlays intact. Independent review
  APPROVE-WITH-NOTES (both notes addressed before merge: identity-map
  indentation normalized, breadcrumbs refreshed). Workbook: 505 rows, 502
  approved; gate blocking=0, questions=0. TTL: 682 concepts, 14,473
  triples (+1: the added second R&D altLabel), 679/682 defined. No new
  duplicate prefLabel groups; zero definition changes; IRIs/slugs
  unchanged; `downstream_process_map.json` untouched. Naming queue: 78 of
  93 entries remaining (categories 3–6).
- **Scope-ambiguity naming batches 1 & 2 — executed and merged 2026-09-21
  (PR #91, PR #92).** The third naming-pass category: 21 labels whose
  wording left the process scope ambiguous, renamed per Hamid's approval
  2026-09-21 in two batches. Batch 1 (A+B+C, 10 renames, PR #91, merged
  2026-09-21): `CM-1-1-3-6-2` → Administer Scheduled Shipment Loading;
  `CM-1-1-3-8-3` → Maintain Secondary Distribution Scheduling Basis;
  `CM-1-2-4-1-8` → Settle Environmental Instruments; `CM-1-2-4-2-2` →
  Manage Production & Inventory Accounting; `CM-1-2-6-2-3` → Forecast
  Operational Refined Product Demand; `CM-1-2-6-3-2` → Fulfill
  Replenishment From Trading Sources; `CM-1-2-6-3-3` → Coordinate
  S&T-Sourced Primary Transportation; `CM-1-3-6-6-2` → Manage Card
  Program Billing Coordination; `CM-1-3-6-6-6` → Manage Card Delinquency
  and Collections Referral; `CM-1-3-6-8-1` → Conduct Commercial Audit to
  Validate Reported Sales. Batch 2 (D, 11 renames, PR #92, merged
  2026-09-21): `CM-1-3-7-1` → Manage Commercial Master Data Stewardship;
  `CM-1-3-7-1-1` → Maintain Customer and Commercial Account Master Data;
  `CM-1-3-7-1-3` → Maintain Product and Service Master Data;
  `CM-1-3-7-1-5` → Maintain Commercial Workflow Configuration;
  `CM-1-3-7-1-6` → Maintain Commercial Policy Content and Approved
  Parameters; `CM-1-3-7-2` → Manage Commercial Terms, Quoting, and
  Customer Commercial Services; `CM-1-3-7-3-6` → Manage Commercial
  Returns Authorization and Coordination; `CM-1-3-7-4-5` → Perform
  Credit-Driven Customer Closure and Reinstatement; `CM-1-3-7-4-6` → KYC
  Process → Perform KYC Due Diligence; `CM-1-3-7-5-1` → Prioritize
  Customer Requests and Inquiries; `CM-1-3-7-5-2` → Maintain Customer
  Request and Inquiry Records. Old labels retained as `skos:altLabel`;
  `prior_name`/`name_change_note` recorded in the identity map;
  `scoped_historical_alias` stays null; slugs, IRIs, hierarchy, and
  definitions unchanged; workbook cross-references and breadcrumbs swept;
  `downstream_process_map.json` untouched. Batch 2 independent review
  APPROVE-WITH-NOTES (KYC scope confirmed under the approved boundary:
  Commercial/Credit executes KYC due diligence and escalates
  discrepancies; Compliance/Legal own the sanctions-compliance and
  financial-crime frameworks — no definition change authorized or made).
  Workbook: 505 rows, 502 approved; gate blocking=0, questions=0,
  notes=18, open_ptc=1. TTL: 682 concepts, 14,474 triples, 679/682
  defined, 680 broader links. Naming queue: 57 of 93 entries remaining
  (12 scope-ambiguity, 8 directionality-missing, 11 generic-operational,
  26 normalization-only).
- **Scope-ambiguity naming batch 3 — executed and merged 2026-09-21
  (PR #94).** The last of the third naming-pass category: 12 labels (E+F)
  whose wording left the process scope ambiguous, renamed per Hamid's
  approval 2026-09-21: `CM-1-3-1-6` → Marketing Insight and Metrics
  Stewardship; `CM-1-3-8-1-2` → Perform Self-Billing Accounting;
  `CM-1-3-8-1-5` → Manage Invoice Exceptions, Reversals, and Rebilling;
  `CM-1-3-8-2-1` → Record Customer Receipts and Payment Notifications;
  `CM-1-3-8-2-4` → Manage Unapplied Receipts and Exceptions;
  `CM-1-3-8-2-5` → Perform Cash, Acquirer, and Receivables
  Reconciliations; `CM-1-3-8-3` → Manage Receivables Resolution;
  `CM-1-3-8-3-1` → Manage Receivables Disputes; `CM-1-3-8-3-2` → Manage
  Receivables Collections; `CM-1-3-8-3-3` → Determine Bad Debt
  Allowance; `CM-1-3-8-3-4` → Develop Root-Cause Analyses and Action
  Plans; `CM-1-3-8-4-7` → Administer Royalty, Brand Fee, and Contribution
  Streams. Old labels retained as `skos:altLabel`; existing valid aliases
  preserved; `prior_name`/`name_change_note` recorded in the identity map;
  `scoped_historical_alias` stays null; slugs, IRIs, hierarchy unchanged.
  TTL diff: 102 replacement hunks, zero inserted/deleted hunks; all IRIs,
  notation, and broader links unchanged; exactly 4 definition literals
  touched only to replace the "Insight and Metrics" cross-reference with
  the new `CM-1-3-1-6` label — no substantive definition change; workbook
  cross-references and breadcrumbs swept; `downstream_process_map.json`
  untouched. Independent review APPROVE (all 11 pre-existing duplicate
  prefLabel groups confirmed; Finance authority over bad-debt allowance
  and reconciliation-without-settlement boundaries verified; workbook
  `parent` column still carries the locked old label for `CM-1-3-8-3`
  children — established behavior from prior batches). Workbook: 505
  rows, 502 approved; gate blocking=0, questions=0, notes=18,
  open_ptc=1. TTL: 682 concepts, 14,474 triples, 679/682 defined, 680
  broader links. Naming queue: 45 of 93 entries remaining
  (8 directionality-missing, 11 generic-operational, 26
  normalization-only) — the scope-ambiguity category is closed; whether
  `CM-1-3-1-6` is a capability or a process stays an exploratory modeling
  follow-up, out of the label-only pass.
- **Directionality-missing naming batch — executed and merged 2026-09-21
  (PR #96).** The fourth naming-pass category: 11 labels whose wording
  hid the direction of economic exposure or the Consumer-versus-B2B
  distinction, renamed per Hamid's approval 2026-09-21. Claims lifecycle
  (`CM-1-2-4-4-2..8`): Create Claim → Create Outbound Delay
  Compensation Claim; Receive Demurrage Claim → Receive Inbound Delay
  Compensation Claim; Assess Claim → Assess Inbound Claim; Communicate
  and Negotiate Claim → Negotiate Outbound Claim; Validate and Negotiate
  Claim → Validate and Negotiate Inbound Claim; Send Claim Invoice →
  Invoice Agreed Outbound Claim; Receive Claim Invoice → Process Invoice
  for Agreed Inbound Claim. Consumer value-proposition children of
  `CM-1-3-2-3`: `CM-1-3-2-3-1` → Test Consumer Value Proposition;
  `CM-1-3-2-3-2` → Formulate and Evaluate Consumer Value Proposition
  Alternatives; `CM-1-3-2-3-3` → Establish Consumer Value Proposition
  Principles and Objectives; `CM-1-3-2-3-4` → Develop and Update
  Consumer Value Proposition Strategy (workbook queued label; the
  chat-table "Develop/Update" slash form retained as the historical
  alias). Old labels retained as `skos:altLabel`;
  `prior_name`/`name_change_note` recorded in the identity map;
  `scoped_historical_alias` stays null; slugs, IRIs, hierarchy, and
  definitions unchanged. The B2B siblings `CM-1-3-2-2-1..4` are
  untouched — they legitimately keep the Customer/CVP labels — with all
  consumer-row replacements scoped to `CM-1-3-2-3*` rows; 4 of the 11
  pre-existing duplicate prefLabel pairs resolved (7 remain). TTL diff:
  47 replacement hunks, zero inserted/deleted; one scopeNote change is
  label-text only; workbook cross-references and breadcrumbs swept;
  `downstream_process_map.json` untouched. Independent review
  APPROVE-WITH-NOTES: the 4 historic consumer aliases retained despite
  overlapping the B2B siblings' live prefLabels — non-blocking validator
  questions kept intentionally as controlled exceptions (labels are
  presentation metadata; identity is by slug/IRI), recorded for future
  consumer-impact review; the "Develop and Update" form stands.
  Workbook: 505 rows, 502 approved; gate blocking=0, questions=4,
  notes=18, open_ptc=1. TTL: 682 concepts, 14,474 triples, 679/682
  defined, 680 broader links. Naming queue: 37 of 93 entries remaining
  (11 generic-operational, 26 normalization-only) — the
  directionality-missing category is closed.
- **Generic-operational naming batch — executed and merged 2026-09-21
  (PR #98).** The fifth naming-pass category: 11 labels whose wording was
  generic (scope implied by the parent) rather than self-describing,
  renamed per Hamid's approval 2026-09-21. Terminal commercial
  (`CM-1-3-10-1..4`): `Setup and Maintain Customer In Terminal` -> Set Up
  and Maintain Terminal Customer Authorization; `Process Forecast and
  Nominations` -> Process Customer Lifting Forecasts and Nominations;
  `Manage Allocation` -> Manage Terminal Lifting Allocation; `Capture
  Deal` -> Capture Terminal Sales Deal. Commercial compliance
  (`CM-1-3-6-8`): `Compliance Management` -> Commercial Agreement
  Compliance Management. Service reviews (`CM-1-3-7-5-5`): `Conduct
  Quarterly Review Meeting` -> Conduct Customer Service Reviews
  (quarterly stays an adjustable default cadence in the definition/scope
  note, not hard-coded in the label). Service operations
  (`CM-1-3-9-1-2`): `Manage Operations` -> Manage Service Operations.
  Service delivery (`CM-1-3-9-2-1..3`): `Manage Data` -> Manage Service
  Delivery Data; `Manage Customer` -> Manage Customer Interactions in
  Service Delivery (Hamid's approved plural refinement of the queued
  singular); `Fulfill Service Event` -> Fulfill Service Events. Workforce
  (`CM-1-3-9-3-2`): `Measure Service Employees` -> Measure Service
  Workforce Performance. Ten old labels retained as `skos:altLabel`; the
  bare `Manage Customer` kept only as `prior_name`/`name_change_note` in
  the identity map — not a live `skos:altLabel` — because it is a prefix
  of live labels (Manage Customer Portal, Manage Customer Invoicing and
  Billing, Manage Customer Requests and Inquiries) and would reintroduce
  search ambiguity; the queued singular near-duplicate `Manage Customer
  Interaction in Service Delivery` was also dropped (Hamid approved the
  drop 2026-09-21 on the reviewer's recommendation). Generic-alias
  migration-map-only treatment is now the reusable naming-pass precedent
  for the remaining normalization-only rows. Slugs, IRIs, hierarchy,
  definitions, and authority boundaries unchanged; workbook
  cross-references, breadcrumbs, and scopeNote prose swept;
  `downstream_process_map.json` untouched; taxonomy report regenerated
  alongside the TTL (14,473 triples, 309 altLabels). Independent review
  APPROVE-WITH-NOTES (all 11 labels verified verbatim in workbook and
  TTL; guarded stale-reference sweep clean; identity-map overlays exact;
  semantic TTL diff contains only batch-5 changes; stale local repo HEAD
  flagged and ignored — commit based directly on remote main). Workbook:
  505 rows, 502 approved; gate blocking=0, questions=4 (pre-existing
  Batch 4 consumer/B2B controlled exceptions), notes=18, open_ptc=1.
  TTL: 682 concepts, 14,473 triples (-1: the deliberate `Manage
  Customer` alias drop), 679/682 defined, 680 broader links; 7 duplicate
  prefLabel groups, all pre-existing. Naming queue: 26 of 93 entries
  remaining (26 normalization-only) — the generic-operational category is
  closed.
- **Normalization-only mechanical batch — executed and merged 2026-09-22
  (PR #100).** The first half of the sixth naming-pass category, executed
  per Hamid's approved sequencing (mechanical first, judgment second):
  13 normalization-only renames approved 2026-09-21. `CM-1-1-7-3-3` →
  Manage and Support Emissions Trading; `CM-1-2-2-3-9` → Perform Position
  & P&L Analysis; `CM-1-2-4-2-7` → Manage Financial Information
  Documentation and Reporting; `CM-1-2-5-1-1` → Manage Feedstock Data
  Quality; `CM-1-3-2-1-1` → Formulate and Evaluate Strategic Operating
  Alternatives; `CM-1-3-6-5-2` → Manage Promotions and Events Execution;
  `CM-1-3-6-6` → Loyalty and Cards Management (Marketing); `CM-1-3-6-6-1`
  → Set Up Prospect; `CM-1-3-6-6-12` → Manage Additional Card Services;
  `CM-1-3-6-6-4` → Manage Card Administration; `CM-1-3-7-3-3` → Change or
  Cancel Order; `CM-1-3-7-5-4` → Perform Customer Follow-Up; `CM-1-3-8-1-1`
  → Create and Distribute Bill. Ten old labels retained as `skos:altLabel`
  (all passed uniqueness/semantic-safety checks); the two parenthetical
  card labels (`Manage Additional Card Services (On Road Services)`,
  `Manage Cards Administration (Order New Cards, Change Card Data)`)
  migration-map-only — kept as `prior_name`/`name_change_note` in the
  identity map, not live aliases (generic-alias precedent from Batch 5);
  the case-only `Manage feedstock Data Quality` not retained as an
  altLabel either — the workbook validator flags case-only altLabels as
  collisions (queue rule: case/punctuation-only changes carry no alt
  label), so it lives only as `prior_name`. Cross-reference sweep: 31
  asserted scoped replacements across `related_concepts`, breadcrumbs,
  parent display names, and prose (guarded matching for PNL/P&L,
  Setup/Set Up, singular/plural, case-only); final sweep found no stale
  references outside intentional terminology-note and retained-alias
  locations. Slugs, IRIs, hierarchy, definitions, and authority
  boundaries unchanged; `downstream_process_map.json` untouched;
  taxonomy report regenerated alongside the TTL. Independent review
  APPROVE-WITH-NOTES (all 13 rows verified in workbook, TTL, identity
  map, and queue; per-row altLabel triple deltas traced against the
  pre-batch TTL: +1 × 6 rows, net 0 × 4 rows, −1 × 2 migration-map-only
  rows, net 0 × 1 case-only row; the one actionable note — a stale queue
  annotation for `CM-1-2-5-1-1` — corrected before merge). Workbook: 505
  rows, 502 approved; gate blocking=0, questions=4 (pre-existing Batch 4
  consumer/B2B controlled exceptions), notes=18, open_ptc=1. TTL: 682
  concepts, 14,477 triples (+4 altLabel triples, fully accounted), 679/682
  defined, 680 broader links, 313 altLabels; 7 duplicate prefLabel groups,
  all pre-existing. Naming queue: 12 of 92 entries remaining (12
  normalization-only judgment rows) — mechanical normalization is closed;
  the judgment batch is proposed in chat before any repo changes.
- **Normalization-only judgment batch — executed and merged 2026-09-22
  (PR #103).** The second half of the sixth naming-pass category and the final
  naming batch: 12 renames per Hamid's approved judgment proposal 2026-09-22
  (proposal review: approve 11 as recommended, 1 with the concise refinement
  — `Track Order Book and Forecast Order Volumes`, timing kept in the
  definition — 1 conditional on the AR-compliance scope note, verified narrow).
  `CM-1-1-2-10` → Allocate Crude and Feedstock; `CM-1-1-2-11` → Allocate
  Finished Products; `CM-1-2-4-2-6` → Reconcile Economic PNL to Accounting
  PNL; `CM-1-3-6-6-7` → Analyze, Report, and Confirm Card Transactions;
  `CM-1-3-6-6-9` → Plan Card Stock Consumption and Monitor Inventory;
  `CM-1-3-6-7` → Brand Standards Management; `CM-1-3-6-7-1` → Manage
  Brand Standards and Inspections; `CM-1-3-7-2-3` → Develop and Monitor
  Commercial Revenue Plan; `CM-1-3-7-3-5` → Track Order Book and Forecast
  Order Volumes; `CM-1-3-8-4-1` → Perform Period-End Processing;
  `CM-1-3-8-4-2` → Perform AR Reconciliation and Compliance;
  `CM-1-3-8-4-3` → Analyze and Calculate Accruals. Eleven old labels
  retained as `skos:altLabel` (all passed uniqueness/semantic-safety checks);
  the PNL row's old label is migration-map-only — it differs from the new
  label by case only (`To` vs `to`), which the validator flags as an
  altlabel-collision (queue rule: case/punctuation-only changes carry no alt
  label), so it lives only as `prior_name`/`name_change_note`. The two queued
  near-miss variants (`Analyze and Confirm Card Transactions`, `Track Orders
  and Forecast Order Book`) legitimately stay as second altLabels; 7 queued
  labels were promoted out. Cross-reference sweep: 37 asserted scoped
  replacements across `related_concepts` (+slug annotation), breadcrumbs,
  parent display names, and prose (guarded matching for the Brand-Standards
  singular/plural edge and the PNL case-only edge); final sweep found no stale
  references outside intentional terminology-note and retained-alias
  locations. Slugs, IRIs, hierarchy, definitions, and authority boundaries
  unchanged; `downstream_process_map.json` untouched; taxonomy report
  regenerated alongside the TTL. Independent review APPROVE (all 12 rows
  verified in workbook, TTL, identity map, and queue; the +4 triple delta
  fully reconciled: +11 old-label altLabels, −7 promoted queued altLabels).
  Workbook: 505 rows, 502 approved; gate blocking=0, questions=4
  (pre-existing altlabel-collision questions, unchanged), notes=18,
  open_ptc=1. TTL: 682 concepts, 14,481 triples, 679/682 defined, 680
  broader links, 317 altLabels; 7 duplicate prefLabel groups, all
  pre-existing. **The naming queue is closed: all 92 entries executed.**
- **Preconditions — the open PTC entries.** Currently **PTC-001**
  (`CM-1-1-4-6` Commercial Development does not belong under Refinery
  Planning; partially resolved 2026-09-21 — 1 row retired (tombstoned),
  1 blocked (PTC-001-B), 2 rehomed and definition-approved via PR #87).
  PTC-002 closed 2026-09-18 with no tree change needed. The register is
  the live list; this line will go stale, the register will not.
- **Known scope beyond the moves.** PTC-001 cannot be applied as
  accepted. Only Commercial & Marketing is decomposed — 492 of 503 rows
  sit under it, and the other nine L1s have no children. There is no
  destination for any parked child, so Step 3d includes decomposing at
  least one undecomposed L1. That is a domain-architecture pass, not a
  reparenting chore, and it needs Hamid's explicit scope expansion.
- **How it gets picked up.** Not by memory. The gate reads the register
  every run, prints `open_ptc=N` in its summary line (which lands in
  every batch PR body), and raises BLOCKING `step-3c-not-complete` if the
  definition queue reaches zero while any entry is open. Step 3c cannot
  be declared finished with a tree change outstanding.
- **Done when.** Every PTC entry closed with its checklist worked, parked
  rows re-statused to `pending` under real parents, identity map and TTL
  regenerated, and the gate reporting `open_ptc=0`.
- **R1 Refining structural reclassification — IMPLEMENTED 2026-09-22 (PR #108 merged).**
  Hamid approved the Candidate package and, after two review rounds, merged PR #108
  (merge `b75fd991e243248e60ecc832b3ad2c4f5c91740a`, 2026-09-22T12:51:35Z).
  Status change: R1 moves from **Candidate** to **Implemented**; the Refining L1 now
  carries four L2s — Refinery Planning and Optimization, Refinery Production
  Planning and Scheduling, Refinery Performance and Risk Coordination (existing
  candidate), and Refinery Asset Reliability and Turnaround Coordination (new
  Candidate, unpopulated, coordination-only). Final counts: **683 concepts,
  14,496 triples (+15 vs 14,481 baseline), 681 broader links.** The +15 delta is
  fully accounted: +14 from the new R&T L2 and its generated metadata, +1 from the
  approved `informs` interface relation on Publish Local Refinery Targets
  (`proc:CM-1-1-2-9-1 intake:relatedConcepts "informs: Refinery Planning and
  Optimization (CM-1-1-4)"@en`). Identity stable: slugs, IRIs, notations
  unchanged; tombstone re-anchored under Planning & Scheduling; PTC-001-B still
  blocked; PTC-002 and the S&T feedstock-quality cluster untouched.
- **R1 review rounds (2026-09-22).** Round 1: Hamid returned "approve after one
  required correction" — the taxonomy-report generator still hard-coded "680
  broader links" in its validation prose; fixed to the derived count, report
  regenerated, gates rerun. Round 2: Hamid requested (a) the report prose fix
  be completed, (b) the reviewed RO→Refining interface relation materialized in
  the TTL behind a reviewed-interface allowlist (any unreviewed pending-row
  `related_concepts` entry fails the build loudly instead of emitting), and
  (c) softened triple-delta wording; all applied and re-verified before merge.
  Pre-merge Hamid caught one workbook-only regression the gates had missed: the
  one-shot script rebuilt breadcrumbs from stale process-JSON names, reverting
  `CM-1-1-7-3-3`'s leaf to "Manage and Support Emission Trading". A systematic
  re-scan found 25 more stale-label breadcrumb cells (26 total, all corrected;
  zero remaining across 522 rows). The checker now permanently locks this:
  `CM-1-1-4-6-1` status `blocked` asserted in TTL and workbook, every breadcrumb
  leaf must equal the executed `name`, and the full breadcrumb must equal the
  identity-map naming-authority path. The one-shot script now rebuilds
  breadcrumbs from identity-map names, with JSON names only as fallback.
- **R1/R2 boundary wording (docs sync, 2026-09-22):** the planning/scheduling
  estate **supports and governs refinery planning and scheduling; it does not
  execute refinery operations** (unit operation, line-ups, blend execution,
  process control, and operating execution remain unmodeled and belong to R2).
  This phrasing supersedes the earlier PR-body wording.
- **Standing after merge:** Step 4 (process-definition ontology; retirement of
  the provisional `intake:` predicates) is NOT started — it still requires
  Hamid's explicit approval. PR #30 remains parked. The consumer-inventory
  checklist reactivates before the first hierarchy-dependent consumer connects.

### Step 3b — definition triangulation ✅ (2026-09-18, complete)

Filling the 503 definition gaps without inventing text: APQC element
descriptions triangulated against public industry definitions.

- **Part 1 — APQC candidates (done):** every definition-less node
  matched to the best APQC PCF v7.2.2 element by name-token F1 (name-only
  and name+context scored, best kept), with APQC hierarchy depth recorded
  so level-equivalence is judged. Triage: 131 strong (≥0.6), 291 weak,
  81 no candidate. Review sheet: `step3b-definition-review.csv`
  (all 503 rows; also copied to the goal's files dir).
- **Part 2 — public-source agreement (done 2026-09-18):** EIA glossary
  leg finished first: 2,641 terms fetched across all 26 letter pages,
  exact + verb-stripped matching → 5 broad noun hits, **0 adoptions**
  (final verdict, none precise enough). Web leg then ran over the 131
  strong rows: 111 automated validations (5 workers; 20 rows deliberately
  omitted as too generic for any authoritative definition) + 11 human-vetted
  manual records. Result: **1 ADOPTED** — "Define Internal Marketing
  Communications Strategy" ← APQC 16852, validator TechTarget "Internal
  marketing" (agreement 0.625), human-inspected as a genuine match.
  **5 REJECTED** at the human gate: "Perform Inventory Reconciliation"→
  benefit reconciliation (0.667 name similarity, HR vs inventory),
  CVP strategy→KM strategy (different "strategy" senses), "Manage M&A
  Activity"→IT activity risk ("manage"+"activity" token overlap), plus 2
  circular APQC-validating-APQC records. Merge: `step3b-merge-validations.py`
  (replaces the truncated, retired `step3b-adopt-definitions.py`).
- **Adoption rule (locked):** ADOPTED = strong APQC link + independent
  source agrees + human semantic inspection → APQC text adopted with
  `dcterms:source` provenance. REVIEW LINK = weak link, human confirms.
  NO AGREEMENT / NO SOURCE / NO CANDIDATE → author an LSC definition.
  Nothing is adopted on a heuristic match alone; APQC may never validate
  itself.
- **Final tally (after Step 3c):** 192/680 definitions (177
  repository-authored + 1 triangulated + 14 human-authored);
  10 APQC candidates rejected at the human gate; 488 definition
  gaps remain (all L4–L6) for future authoring passes.
- **Provenance:** every adopted definition carries `dcterms:source` →
  per-source `dcterms:BibliographicResource` blank nodes (element ID +
  title), themselves `dcterms:isPartOf` registry resources
  `…/source/apqc-pcf-7.2.2` and `…/source/eia-glossary` (title, publisher,
  issued, rights). Wired via `step3-skos-taxonomy.py --adoptions`;
  base build without adoptions reproduces byte-identical output.
- **Delivered** via PR #28 (`ontology/taxonomy-definitions`, opened and
  merged 2026-09-18, together with Step 3) — review CSV, adoptions,
  validation records, and both build scripts included.

---

## 4. Decision log

Locked decisions. Newest first within each group. Nothing here changes
without a dated amendment and Hamid's explicit agreement.

### Scope and source-of-truth
- **Repo processes are the source of truth.** We model the business
  processes in the repo's process map (2026-09-17).
- **APQC is a consistency reference**, not the source we copy from. We
  check that nothing is inconsistent with the published framework
  (2026-09-17).
- **APQC extensions come later.** Once the base model is built, we may
  extend with additional APQC information (2026-09-17).
- **Enabling-functions principle.** The ontology covers enabling
  functions, not only the hydrocarbon value chain — but only where the
  ontology has a genuine hook (2026-09-17, Step 8).
- **The ontology defines; it does not calculate.** It answers what a
  Named KPI *is*; the Store computes it. Genie and other agents point at
  the ontology — they do not become a second one (2026-09-18).

### Modeling
- **Provisional `intake:` namespace for workbook Phase-1 capture
  (2026-09-20).** Approved workbook rows are preserved verbatim in the
  graph under `https://w3id.org/lsc/ontology/intake/` (keyInputs,
  primaryOutput, relatedConcepts, responsibleDomain, processHorizon,
  primaryPurpose, referenceSources, terminologyNotes, conceptTypeCheck,
  parkedChildren, level, apqcDecision, status) so nothing the reviewer
  captured is lost between the workbook and the ontology. This is
  explicitly NOT the Step 4 model: Step 4 promotes these annotations to
  real properties between concept URIs. `intake:level` carries the locked
  L0–L6 taxonomy level; `intake:apqcDecision` records the mapping call
  (REVIEW LINK / ADOPTED / REJECTED / NO CANDIDATE / NO SOURCE) —
  REJECTED rows are the deliberate APQC divergences (competency Q12).
- **Workbook definition precedence (2026-09-20):** workbook-approved >
  human-authored L1–L3 > step3b adoption > repo description.
- **Parked rows in the graph (2026-09-20):** blocked rows appear with
  `intake:status "blocked"` and no `skos:definition` (the locked rule: a
  parked row must not carry one); retired rows are `owl:deprecated`, not
  deleted — `dcterms:isReplacedBy` is left for the Step 3d tree pass, when
  destinations are decided.
- **PTC-001 definition batch (2026-09-21, PR #87).** The four rows left
  `pending` by the PTC-001 tree pass are authored and approved: the two
  Candidate L2s (Financial Planning and Performance Management; Refinery
  Performance and Risk Coordination) and the two reparented L3s (Plan
  Budgets; Coordinate Site Business Risk Management). Reviewer-driven
  refinements baked in: the risk L3's scope note states the hybrid
  event-driven/periodic cadence, and the Refining L2's scope note keeps
  performance oversight at capability level pending future Refining
  decomposition. `approve` in Plan Budgets means administering the
  budget-review workflow — final approval stays with the delegated
  authority. Workbook: 502/505 approved, gate blocking=0 questions=0;
  TTL: 679/682 defined, 14,472 triples. PTC-001 stays open until
  PTC-001-B (Develop Strategic Business Plan) closes.
- **SKOS-first taxonomy.** Do not mechanically convert each process /
  hierarchy level into an OWL class/subclass (2026-09-17).
- **URI base is `https://w3id.org/lsc/ontology/`** — company-scoped,
  person- and project-independent, redirect-backed (2026-09-18).
- **Local process IDs are preserved, never replaced by APQC IDs.**
  Existing codes are `skos:notation` and the basis of URI slugs; APQC
  IDs attach via `dcterms:references` only (2026-09-18).
- **No version segment in URIs.** Identity is stable across definition
  changes; versions ride on `owl:versionInfo` (2026-09-18).
- **Language: English primary** (`@en` on every literal; one
  `skos:prefLabel` per language; aliases in `skos:altLabel`;
  `skos:definition` required per concept) (2026-09-18).
- **Versioning: SemVer, URIs immutable.** Major = breaking (URI
  change, removed concept, redefined meaning); minor = new concepts /
  modules / hierarchy changes; patch = label/definition wording fixes.
  Deprecate, never delete. Full detail in Appendix B (2026-09-18).
- **Ontology identity (2026-09-22; IRI corrected to the locked Step 1
  policy the same day).** The `core` module's ontology IRI is
  `https://w3id.org/lsc/ontology/modules/core` — the locked
  `…/modules/{module}` namespace pattern, which also doubles as the
  module's ConceptScheme. Each release gets a version IRI of the form
  `https://w3id.org/lsc/ontology/modules/core/1.0.0`.
  Every release ships an explicit `owl:Ontology` header carrying
  `dcterms:title`, `dcterms:description`, `owl:versionIRI`,
  `owl:versionInfo`, `dcterms:issued`, `dcterms:creator`, and
  `dcterms:license`. Term IRIs stay stable and unversioned —
  `core:ProcessDefinition` is
  `https://w3id.org/lsc/ontology/modules/core/ProcessDefinition`,
  never `…/modules/core/1.0.0/…`. (The Q1 decision text originally used
  the shorthand `…/ontology/core`; corrected on review — the Step 1
  lock was never changed, the shorthand never shipped, nothing is
  published, so no supersession record is needed.)
- **First formal version: 1.0.0 (2026-09-22).** Step 4 ships `core`
  1.0.0 — the first versioned release. It is the first release with
  governed properties instead of provisional `intake:` annotations and
  the first to carry the version header. 1.0.0 is the baseline that
  Step 5 (organization), Step 6 (PROV-O), and later modules version
  against. Recorded in Appendix B's version history.
- **Flow modeling depth (2026-09-22).** Step 4 captures flows as
  governed structured values on the input/output links — controlled,
  consistently-spelled flow names (e.g. "demand forecast"), no new
  nodes. The workbook's flow information is preserved and queryable
  ("which processes consume the demand forecast?"). Minting
  InformationObject nodes for every distinct flow (~1,900) is deferred:
  it is a data-governance project — identity, dedup ("is the demand
  forecast in 12 processes one thing or twelve?"), ownership, lifecycle
  — that no Step 4 competency question or consumer requires. Revisit
  trigger: a real use case that needs to trace a specific artefact
  (e.g. audit lineage of the approved operating plan) — then mint that
  flow as a node deliberately, one at a time. Composes with the Q4
  decision: `core:dependsOnOutputOf` links consumer to producer
  process; the structured value says
  what travels on the link.
- **Responsible-domain interim treatment (2026-09-22).** Step 4 keeps
  `responsible_domain` as a governed literal on the process, explicitly
  interim — no org nodes are minted. Step 5 (ORG/RACI) will map these
  interim values to governed organization, role, and
  ResponsibilityAssignment references where the operating model
  evidences the relationship — some current labels are
  business-architecture domains, not org units; the controlled list
  makes that migration mechanical.
  The workbook's 10 distinct values (456 of 485 rows "Commercial &
  Marketing") are nearly controlled already — the value is in the
  exceptions (Finance-enabled Supply & Trading, Finance, Refining, and
  6 cross-functional combos, normalized to a governed
  "Cross-functional" value with detail preserved in a note).
- **Step 4 Q8: controlled `conceptKind` scheme (2026-09-22).**
  `core:conceptKind` is an object property to a controlled SKOS scheme,
  not a string. Kinds: Process (real business process — inputs,
  outputs, cadence), Capability (an ability the organization has,
  realized by processes), StructuralAnchor (navigation/grouping node —
  L0 roots, empty stubs, tombstones — not work anyone performs).
  Consumers treat kinds differently: "all processes" must not return
  navigation nodes; no RACI or cadence on anchors. Deliberate boundary:
  this does NOT classify CM-1-3-1-6 ('Marketing Insight and Metrics
  Stewardship') — that stays a parked modeling question. We build the
  shelf; classification comes later. Composes with the parked
  value-stream layer (Appendix A): `core:CapabilityKind` classifies a
  concept as capability-like; actual business capabilities are a future
  `core:BusinessCapability` class — architecture entities, not
  classification values — linked to processes via `core:realizedBy`.
- **Step 4 Q9: lifecycle model (2026-09-22).**
  `core:lifecycleStatus` is an object property to a controlled SKOS
  scheme with four states: Candidate → Approved → Deprecated →
  Retired. Blocked/held are **not** states: a separate hold flag
  applies to a concept in any lifecycle state, with a recorded reason
  (a Candidate can be blocked; an Approved concept can be put on hold
  without losing its state). The scheme does not conflict with OWL:
  Deprecated ⇒ `owl:deprecated true` (required); Retired ⇒
  `owl:deprecated true` (retired implies deprecated);
  Candidate/Approved ⇒ `owl:deprecated` absent or false. Agreement is
  enforced by SHACL in Step 9; the rule is stated now. Allowed
  transitions: Candidate→Approved, Candidate→Retired (rejected before
  publication), Approved→Deprecated, Deprecated→Approved
  (undeprecation, governed), Deprecated→Retired. Retired is terminal —
  never resurrect; mint a new concept instead. `dcterms:isReplacedBy`
  points to the successor where one exists.
- **Step 4 Q1 design refinements (2026-09-22).** Module-boundary rule:
  `core:` carries foundational planned-process semantics only —
  organization → Step 5, KPI semantics → `kpi`, observed execution →
  PROV-O in Step 6; no `data:` module (adding one needs its own
  decision). `core:ProcessDefinition` typing rule: approved processes +
  capabilities, candidate structural/capability nodes with authored
  definitions, blocked/retired only when retaining a meaningful record —
  never L0 roots, pure structural anchors, tombstones, or not-process
  roots. `core:conceptKind` and `core:lifecycleStatus` are object
  properties to controlled SKOS schemes, not strings; three status
  layers stay distinct (architecture artifact status vs concept
  lifecycle vs authoring/review status). `core:taxonomyLevel` is derived
  metadata ("current rendered depth") — never for security, KPI
  ownership, criticality, or identity. Terminology notes migrate by
  kind: authoring history → `skos:editorialNote`, migration history →
  `dcterms:provenance`, review evidence → decision-log reference.
- **Step 4 Q2: `intake:` retirement mode (2026-09-22).** Flag-day: all
  `intake:` triples go in one Step 4 release — no deprecated-alias
  transition (carrying ~5,571 dead staging triples is not worth it).
  Preconditions before the release ships: reconfirm the no-consumer
  attestation; per-predicate conservation ledger (`emitted + held =
  source total`) — "zero `intake:` triples" proves deletion, not
  replacement; explicit merge/release approval still required.
- **Step 4 Q4: process dependency links (2026-09-22; property name
  revised on review the same day).** When a workbook relation identifies
  another process as the source of a needed input, model the
  relationship as `core:dependsOnOutputOf` from the consumer process to
  the producer process, with inverse `core:providesInputTo`. No new
  nodes — the edge preserves the dependency chain ("what does this
  process depend on; what breaks if it fails") that the competency
  questions need. Governed structured flow values state what is
  exchanged on that dependency. `core:consumes` and `core:produces`
  remain reserved for future identified InformationObject instances.
  (The Q4 decision originally named the property `core:usesInput`;
  review corrected it — a process is not an input, its *output* is.)
- **Step 4 Q6: `processHorizon` facet split (2026-09-22).** The workbook
  field conflated three dimensions (8 distinct values across 485 rows:
  event-driven/periodic/continuous are operating modes; daily/weekly/
  monthly are cadences; tactical/strategic are planning levels). Step 4
  splits it into `core:operatingMode` (event-driven | periodic |
  continuous), `core:cadence` (daily | weekly | monthly | quarterly |
  annual), and `core:planningLevel` (strategic | tactical |
  operational) — each independently queryable. The 107 "periodic"-only
  rows are recorded as cadence-unspecified: honest about the gap rather
  than pretending "periodic" is a cadence.
- **License: proprietary, all rights reserved** (2026-09-18). Hamid is
  the IP owner. Rationale: the ontology describes LSC's actual
  operations — competitively sensitive; can be opened later, cannot be
  un-opened. APQC/IBM terms separately permit use, copying, publishing,
  modification, and derivatives with attribution carried on every
  distribution — attribution coexists with proprietary.
- **Module policy** (2026-09-18): four modules, each with its own
  namespace, version, SHACL shapes, and owner. `core` and `party` depend
  on nothing; `kpi` depends on `core` + `party`; `organization` depends
  on `core` only — `org:Role` (internal positions) and
  `party:PartyRole` (external commercial roles) are different beasts.
  Rules: dependencies point one way, no cycles (CI-enforced);
  cross-module use by URI reference, never redefinition; independent
  versioning/validation; minor/patch by module owner, majors by Hamid.
- **`party` is the sole concept-owning module for the Customer domain** (2026-09-18). There is deliberately no `customer` module — it would reintroduce the overloading the August Party model eliminated. Customer-domain processes live in `core` (O2C), customer-grained KPIs in `kpi` bound to Party/Account/Role, RACI in `organization`; the domain is a view across modules, its concepts anchored in `party`.
- **Separate definitions from occurrences.** Process types/definitions
  are distinct from execution occurrences (2026-09-17).
- **Do not auto-type taxonomy concepts as `prov:Activity`.**
  `prov:Activity` is reserved for actual occurrences (2026-09-17).
- **RACI is design-time responsibility** and needs an explicit n-ary
  `ResponsibilityAssignment` model — not a simple property
  (2026-09-17).
- **Existing codes (e.g. `CM 1.2.1.3`) are `skos:notation`**, not
  official APQC identifiers (2026-09-17).
- **Mint stable HTTP URIs and persistent local IDs for every node**,
  including the 11 ID-less roots/stubs (2026-09-17).
- **Do not declare office lanes mutually disjoint** without evidence
  (2026-09-17).
- **Constraints are not modeled.** The constraints module and its
  competency questions are parked; the "reference, don't subclass"
  principle is parked with them (2026-09-18).
- **Classify activities by primary purpose, not asset location**
  (2026-09-18, from definition authoring): a tank, berth, pipeline,
  rack, or laboratory can participate in multiple contexts without
  being forced into one category. E.g. crude unloaded into refinery
  tanks is Midstream receipt even when co-located with a refinery;
  an intermediate transferred between refinery process units is
  Refining even though it physically moves.
- **Midstream/Refining conceptual split** (2026-09-18): Midstream
  moves, stores, receives, transfers, and dispatches material;
  Refining transforms material into different products or
  specifications. Maintenance and turnarounds enable refining but do
  not themselves refine — they live in scope notes, not definitions.
- **Commercial & Marketing is the market-facing value-optimization
  function** (2026-09-18): it creates, manages, and optimizes the
  commercial value of products and services. It coordinates with
  refining, midstream, distribution, finance, and IT — and spans the
  commercial hydrocarbon lifecycle as an overlay — but does not
  subsume their underlying physical operations or enterprise-wide
  technology services.
- **Domain placement rule — each L1 domain's primary question**
  (2026-09-18): Supply Chain Management — "what should move, be
  made, held, or replenished, where and when?" (orchestrates, does
  not own execution); Commercial & Marketing — "for which
  customer/market, under what offer, price, contract, or margin?";
  Refining — "how is feedstock transformed into compliant
  products?"; Midstream — "how are bulk feedstocks and products
  physically received, stored, transferred, and transported?";
  Distribution — "how are products fulfilled and delivered into
  channels or to end customers?" Use this table as the placement
  test when new processes are modeled.
- **Finance owns financial governance and financial transactions;
  business domains own the operational or commercial event that
  creates them** (2026-09-18): Finance's primary question is "what is
  the organization's financial position, performance, obligation,
  exposure, and control requirement?" Commercial defines/negotiates
  economic activity; Finance records, controls, settles, reports, and
  analyzes it. SCM governs physical/inventory decisions; Finance
  measures working capital, costs, valuation, cash consequences, and
  financial performance. Procurement owns sourcing; Finance owns
  invoice processing, payment, accounting, tax treatment, and
  financial control. HR owns workforce policy and inputs; Finance
  owns pay calculation, payment, withholding, and payroll accounting.
- **Process Excellence & IT's primary question** (2026-09-18): "how
  should the enterprise operate, and what technology enables it?" —
  improve, standardize, govern, measure, automate, and digitally
  enable how the enterprise operates. It does not own business
  outcomes or physical execution in the other domains. IT Service
  Management design belongs here; a centralized service desk or
  transactional IT-admin team under Shared Services is a delivery
  model — "Shared Services delivers IT support on behalf of Process
  Excellence & IT", not a second IT domain (parked for Step 4/5).
- **Human Resources' primary question** (2026-09-18): "what
  workforce is needed, and how is it planned, attracted, developed,
  rewarded, engaged, retained, and transitioned?" HR owns workforce
  policies, people processes, employee experience, and workforce
  information — including authorized payroll inputs; Finance owns
  pay calculation, payment, withholding, and payroll accounting.
- **Legal & Corporate Communications' primary question**
  (2026-09-18): "what legal obligation, advice, contract support,
  governance matter, or official internal message applies?" Legal
  provides counsel, legal-risk management, and regulatory/compliance
  advice; owns internal corporate communications and approved
  enterprise messaging. Government/industry relations, investor
  relations, and public/media/community relations are out of scope
  (Step 8) — as are commercial incentives, which belong with
  Commercial & Marketing.
- **EHS & Government Reporting's primary question** (2026-09-18):
  "is this safe, environmentally compliant, correctly managed when
  events occur, and properly reported to regulators?" EHS defines
  standards, assurance, reporting obligations, incident-management
  methods, governance, and oversight — the functional or asset owner
  operates, executes containment, and closes assigned actions.
  Legal advises on privilege, exposure, and disclosure.
- **Commercial planning vs. SCM planning** (2026-09-18, Regional
  Optimization): commercial planning (e.g. Regional Optimization)
  selects the *economically preferred* plan — which demand to serve,
  how to allocate constrained molecules, buy/sell/exchange,
  inventory positioning, margin subject to service commitments.
  Supply Chain Management coordinates the cross-functional
  *executable* plan. Operators execute production, storage,
  transfers, blending, transport, and delivery. Generalizes to the
  other commercial planning stubs.
- **Optimization vs. Backcasting** (2026-09-18, regional planning
  loop): Optimization asks "what is the best commercially feasible
  regional plan?" Backcasting asks "what actually happened versus
  that plan, why did it happen, what decision or constraint drove
  it, and what should change next cycle?" Backcasting compares
  against the approved plan *and its contemporaneous assumptions*,
  not a later reforecast or rewritten baseline.
- **Commercial planning loop — four-node boundary** (2026-09-18):
  Regional Optimization → the integrated regional commercial plan
  (best commercially feasible regional plan). Refinery Planning →
  crude/feedstock slate, operating-mode, throughput, yield,
  quality, and availability targets (what should this refinery
  buy, run, make, and target). Refining → detailed
  operating/scheduling decisions, unit operations, control,
  maintenance, turnaround work (how is the refinery safely and
  reliably operated — including authority to depart from plan).
  Regional Backcasting → reconciled plan-vs-actual variance
  explanations and learning.
- **Distribution planning loop — four-node boundary**
  (2026-09-18): Distribution planning/optimization → the approved
  distribution plan, allocations, shipment/replenishment targets,
  and constraints (what inventory moves through which route, mode,
  source, and destination). Distribution Backcasting → reconciled
  plan-vs-actual performance, variance drivers, preserved decision
  context, planning improvements. Distribution execution →
  executed movements, delivery confirmations, exceptions, operating
  records (how today's shipments and deliveries are safely carried
  out). Finance → invoices, accruals, settlements, official
  financial results (freight, inventory, revenue, cost).
- **Shared Services executes designated services; it does not replace
  the accountable functional owner** (2026-09-18): Shared Services is
  the delivery model and shared organization (standardized processes,
  common platforms, defined service levels), not a second Finance, HR,
  IT, or Procurement. Functional policy, strategy, design,
  governance, and domain outcomes stay with the accountable owner.

### Validation and process
- **Competency-question coverage is the acceptance gate (2026-09-20).**
  First coverage check against the 44 baseline questions: 4 answerable,
  10 partial, 30 not answerable — the 30 map exactly to unbuilt plan
  scope (Step 4 relations/systems/lanes/capabilities, party/kpi/
  organization modules, SHACL, DCAT, agent contracts), not to capture
  failures. Re-run after Step 4 and after each module lands; nothing is
  "done" until its questions flip to answerable. (Report:
  `competency-coverage-2026-09-20.md`.)
- **Core SHACL where sufficient; SHACL-SPARQL only when Core cannot
  express a constraint** (2026-09-17).
- **Record APQC v7.2.2 with `dcterms:references`**; preserve source,
  version, license, and provenance (2026-09-17).
- **Decisions accumulate in the log; the repo JSON gets one
  consolidated proposal** after the modeling pass — never churn the
  source of truth per decision (2026-09-17).
- **Every new process gets an L0–L6 level** slotted from the existing
  hierarchy — no level-less nodes (2026-09-17).
- **Step 3c closed 2026-09-21 with 498/503 approved** (2026-09-21).
  Batches 01–42. 1 pending is an intentional business-evidence hold
  (`CM-1-1-3-5-3`, batch 05), 3 blocked await the Step 3d tree pass
  (PTC-001), 1 retired (`CM-1-1-4-6`). Gate: 0 blocking, 0 questions.
- **Taxonomy TTL regenerates once at the end of Step 3c** (2026-09-20,
  Hamid's decision): the graph is a snapshot and may lag the workbook
  mid-pass; the final regen (PR #83, 14,403 triples, 675/680 defined)
  is the handoff into Step 3d.
- **Naming normalization is a Step 3d activity, not a Step 3c one**
  (2026-09-21). 92 queued renames live in `step3c-naming-pass-queue.md`;
  duplicate-prefLabel collisions gate semantic-model publication.
  Queued labels stay alt labels until the pass executes, then sweep the
  workbook, TTL, identity map, and cross-references.
- **Confirm the `sioc` JSON field's meaning** (SIPOC/SIOC?) before
  naming ontology terms; do not confuse it with the W3C SIOC vocabulary
  (2026-09-17).

---

## 5. Standards and why we chose them

Each entry: what the standard is, why it earned its place in this build,
and what we deliberately do *not* use it for. The rejections matter as
much as the adoptions — they are what keep the model honest.

### RDF — the grammar
**What:** the subject–predicate–object triple model; everything else here
is a vocabulary written in RDF.
**Why:** it is the only layer the whole stack shares. Every statement the
ontology makes is an RDF statement; every other standard is just an
agreed set of predicates.
**Not for:** carrying meaning by itself — RDF without a vocabulary is
punctuation without words.

### SKOS — the taxonomy backbone
**What:** a vocabulary for governed concept systems: `ConceptScheme`,
`prefLabel`/`altLabel`, `broader`/`narrower`, `notation`, `exactMatch`.
**Why:** the 680-node process hierarchy is a *controlled vocabulary of
process names*, not a class hierarchy of process types. SKOS gives us
labels, aliases, hierarchy, and crosswalks (to APQC) without pretending
each node is an ontological class.
**Rejected:** mechanically converting each process/hierarchy level into an
OWL class/subclass. That would assert logical commitments (disjointness,
inheritance of restrictions) that a naming hierarchy does not support —
and that no reasoner could then be trusted to check.
**Decisions (2026-09-21, Step 3d Phase 1, Hamid):** 8 critical-collision
renames approved — `CM-1-1-1-1` → Produce Demand Forecast (verb-led;
`Demand Forecasting` not retained as altLabel since the L3 parent keeps
it as prefLabel); `CM-1-1-3-7` → Inventory Management (`Inventory` kept
as altLabel); `CM-1-1-3-7-12` → Monitor and Control Inventory Positions
(`Manage Inventory` kept as altLabel); the five shared
`Define KPI Framework` rows → Define Offer / Pricing / Channel /
Network / Operating Model Measurement Framework (the shared generic
label retired from ontology aliases; scoped historical aliases such as
`Define KPI Framework (Offer)` recorded in the identity/migration map).
No definitions, hierarchy, process identities, slugs, or IRIs change.
**Decisions (2026-09-21, Step 3d Phase 1 follow-up, Hamid):** the sixth
`Define KPI Framework` row (`CM-1-3-3-5-7`, under Marketing Communications
Strategy) — discovered after the 8-rename execution — renamed to
Define Marketing Communications Measurement Framework, matching the five
siblings; the generic label is retired from ontology aliases
(scoped historical alias `Define KPI Framework (Marketing Communications)`
in the identity/migration map). No cross-references to the row existed
in the workbook, so the rename is row-local.
**Label governance (standing, 2026-09-21):** labels are governed
presentation metadata; stable slugs/IRIs are concept identity. Never use
a prefLabel or workbook name as a join key, DAX lookup key, RLS
condition, contract key, API key, KPI identity, or logic condition — use
stable identifiers for technical relationships. Retain historical labels
as altLabel only when uniquely resolvable and semantically safe.
**Taxonomy unpublished (2026-09-21, Hamid):** no external consumers, so
renames need no deprecation period or consumer notice.
**Decisions (2026-09-22, Step 3d naming pass Batch 7, Hamid):** the 12
normalization-only judgment renames approved as proposed, with three
judgment calls: (1) the allocation pair stays together as verb-led
`Allocate Crude and Feedstock` / `Allocate Finished Products`, bounded by
the existing definitions — no authority expansion into production planning,
policy, commercial-priority setting, or physical movement; (2) the
card-transaction label keeps all three definition verbs — `Analyze, Report,
and Confirm Card Transactions`; (3) the concise `Track Order Book and
Forecast Order Volumes`, with timing kept in the definition, not the label.
PNL stays the technical-label convention (`P&L` in prose); `card stock` is
scoped to blank cards, secure card media, carriers, mailers, and issuance
materials — not petroleum inventory. The `Reconcile Economic PNL To
Accounting PNL` case-only variant is migration-map-only (no altLabel), and
the queue rule now codified is: case/punctuation-only changes carry no alt
label. No definitions, hierarchy, process identities, slugs, or IRIs change.
**Step 3d closure (2026-09-22, Hamid):** Step 3d closed as "Completed with
explicit open exceptions" on Hamid's approval of the closeout recommendation.
Naming normalization fully executed (92/92 queue entries); evidence-supported
tree remediation complete (PTC-001 partial resolution: tombstone + 2 reparented
L3s + 2 Candidate L2s).
**PTC-001-B confirmed as intentional governance hold (2026-09-22, Hamid):**
`Develop Strategic Business Plan` remains `blocked` under the retired
`Commercial Development` tombstone until evidence establishes whether
enterprise strategic-business planning is owned by (A) Corporate Planning
within Finance, (B) Corporate Strategy / Corporate Development, or (C) an
executive cross-functional governance process. Do not place it under Finance
as a side effect; no new Strategy L1 without a charter-level decision.
Evidence required: operating model, corporate-planning charter, executive and
Board planning calendar, delegated authority, planning / portfolio /
capital-allocation / business-plan artifacts. Review trigger: strategy
operating-model definition, corporate-planning charter approval, or enterprise
architecture/charter revision. A blocked row with a named decision, explicit
options, evidence requirement, and review trigger is governance maturity —
not incomplete work.
**Refining Architecture Scoping Decision (2026-09-22, Hamid):** approved in
principle with refinements; R1 is a controlled re-homing and normalization
pass, not a greenfield refinery model. R0 inventory complete (2026-09-22):
the Refining L1 holds only 3 concepts; the substantive refinery estate —
Refinery Planning (26 concepts) and Refinery Scheduling (16 concepts) —
sits under Commercial & Marketing → Planning & Scheduling. R1 therefore
promotes existing approved concepts with stable slugs/IRIs rather than
duplicating or recreating ~40 concepts.
**Structural framing (Hamid correction, 2026-09-22):** the change is a
**controlled structural reclassification and reparenting with stable
identity** — NOT label-only. Parent-child relationships, concept levels,
`skos:broader` links, hierarchy navigation, query paths, and
hierarchy-dependent consumption (reports, RLS/OLS, Power BI) all change;
only identity is stable. This framing makes the consumer-impact scan
mandatory.
Priority L2s: **Refinery Planning and Optimization** (promote `CM-1-1-4`,
approved in principle subject to the consolidated hierarchy map and the
Optimization-coverage evidence check); **Refinery Production Planning and
Scheduling** (narrower R1 label for the promoted `CM-1-1-7` estate — Hamid's
lean; the broader "Refinery Operations and Production Management" is NOT
auto-approved and waits on the CM-1-1-7 evidence review, else arrives in R2
when operating-execution concepts exist); **Refinery Asset Reliability and
Turnaround Coordination** (new L2, created in R1 as a Candidate structural
anchor, initially unpopulated, coordination-only — see definition below);
**Refinery Performance and Risk Coordination** (existing Candidate L2,
unchanged). Re-anchored under Planning & Scheduling (confirmed 2026-09-22): Commercial Development
tombstone — it does **not** ride the promotion into Refining; PTC-001-B blocked row stays beneath
it with status unchanged. Untouched in R1: PTC-002 feedstock-quality ownership, Supply & Trading
quality cluster. `Publish Local Refinery Targets` stays under Regional Optimization;
its relationship to Refining is modeled as an interface, not a reparenting.
Energy & Utility Management follows its parent in R1 under Temporary/inherited placement status
(review trigger: R2 Refinery Energy, Utilities, and Environmental Performance scope decision) —
not a final ownership decision. EHS / process safety, enterprise risk, maintenance
authority, Finance, Supply & Trading, Midstream, Commercial, Legal, Security,
and IT boundaries stay explicit.
**R&T L2 definition (Hamid-authored, 2026-09-22):** "The Refining capability
that coordinates refinery availability, asset-condition and integrity inputs,
maintenance and turnaround windows, production-plan impacts, readiness, and
recovery interfaces so refinery performance objectives can be planned and
managed against approved maintenance, integrity, and turnaround commitments."
Scope note: coordinates the refinery-operating impact of asset reliability,
inspections, integrity findings, planned maintenance, and turnaround work,
including availability assumptions, outage-window integration,
production-plan and schedule impacts, readiness dependencies,
return-to-service coordination, and escalation of material risks or
constraints. Does not own maintenance strategy, engineering design authority,
inspection execution, process-safety policy, work permits, contractor
management, capital approval, or maintenance/turnaround execution unless
separately assigned by the enterprise operating model. Status: Candidate;
review trigger: R2 evidence package / refinery maintenance and turnaround
operating model.
**Terminology governance (2026-09-22):** R1 resolves terminology only to the
minimum required for an accurate hierarchy and non-misleading labels
(stale parent/label/path references updated mechanically). Unresolved
semantic distinctions (refinery plan vs monthly operating plan vs schedule
vs unit-operation schedule; turnaround vs planned vs emergency shutdown;
startup/restart; production vs operations management) go to an explicit R2
Refinery Vocabulary and Operating-Lifecycle package — not settled silently
in scope notes.
**R1 authoring workflow — mini-batch control (2026-09-22):** new-L2
definition + scope note authored in chat with explicit in/out-of-scope
boundaries and source references; independent wording review; workbook row
inserted/updated through an asserted one-shot script; cell diff generated;
validation gate rerun; TTL regenerated; PR open for approval. Promoted L2s
inherit/reframe their existing approved definitions — no substantive rewrite
unless the move exposes a genuine scope conflict.
**R1 merge gate (2026-09-22):** hierarchy-sensitive consumer-impact
validation is a formal merge gate, not an execution task — ontology
hierarchy integrity, semantic consumption (queries, navigation, Power BI,
RLS/OLS, catalog, data products), governance/traceability (identity-map
migration overlay, historical paths, PTC-001-B/tombstone/PTC-002 unchanged),
and generation (workbook, JSON, TTL, gate, diffs) must pass before any
structural change merges.
**R1 structural decision package (approved as Candidate, 2026-09-22, Hamid):**
delivered as a no-change proposal and approved as **Candidate** on Hamid's independent review:
(1) current-to-target hierarchy map for 40 concepts with old/new parent and level, (2) candidate
L2 definitions, (3) R1/R2 boundary, (4) terminology decision ledger, (5) impact analysis with the
four-gate merge framework, (6) evidence (internal definitions, OSHA/Cal-OSHA/API context, APQC
comparative structure). Review corrections incorporated: (a) scope-note wording — definitions,
authority boundaries, sources, and business substance remain unchanged; scope notes are updated
only where a parent-path, ownership-reference, or execution-interface statement would otherwise
become factually stale, all enumerated in the cell diff; (b) transitive-path migration register
(§1g) — direct broader IRIs are stable but ancestor paths and depths change, recorded for the
consumer-impact scan. Tombstone re-anchor confirmed: `CM-1-1-4-6` (deprecated) and `CM-1-1-4-6-1`
(PTC-001-B, blocked) move under `CM-1-1` Planning & Scheduling rather than riding the promotion
into Refining. Energy & Utility Management subtree tagged Temporary/inherited through its
scheduling parent (review trigger: R2 energy scope decision). Gate 2 requires a formal old→new
path-mapping compatibility table for all 42 affected paths plus the externally supplied
hierarchy-consumer and RLS/OLS inventory. No JSON or workbook modification until the
implementation PR is explicitly approved.
**Definition-authoring process for new L2s (decided, 2026-09-22):** mini-batch
control above (replaces the open workbook-round-vs-direct-authoring
question).
**SemVer treatment for Refining changes (2026-09-22):** new L2 nodes are
additive (minor); reparenting existing concepts changes broader links and is
validated by the consumer-impact merge gate before merge.
**R1 implementation — merged (2026-09-22, Hamid):** PR #108 merged as
`b75fd991` (2026-09-22T12:51:35Z). R1 status **Candidate → Implemented**. Final
state: 683 concepts, 14,496 triples, 681 broader links. Gate results at merge:
hierarchy 42/42 checks (incl. the new blocked-status and breadcrumb-label locks),
workbook validator 0 blocking, TTL regen verified byte-identical before the fix
commits. Documentation-only follow-up opened as a separate PR — no further
ontology-artifact changes.
**R2 backlog (open by design, 2026-09-22):** (1) operating-execution layer —
unit-operation scheduling, tank and transfer line-ups, blend execution, process
control, operating procedures; (2) maintenance/turnaround ownership — which
process or function owns maintenance strategy, inspection execution, reliability
engineering, turnaround planning/execution in the enterprise operating model;
(3) R2 Refinery Vocabulary and Operating-Lifecycle package — first-class
distinctions for turnaround vs normal shutdown vs emergency shutdown,
startup/restart, plan vs schedule vs unit-operation schedule, production vs
operations management; (4) Energy & Utility Management temporary-placement
review, triggered by the R2 Refinery Energy, Utilities, and Environmental
Performance scope decision. PTC-001-B remains open (strategy-ownership hold);
the R&T L2 remains Candidate until the ownership question is answered.

### Dublin Core Terms — describing the sources
**What:** `dcterms:title`, `dcterms:references`, `dcterms:license`,
`dcterms:provenance`, etc.
**Why:** the ontology constantly talks *about* its sources — the APQC
workbook version, the repo JSON, the license terms. Dublin Core is how a
concept says "I was checked against APQC v7.2.2" (`dcterms:references`)
and how a dataset says "you may reuse me under these terms."
**Not for:** describing the domain (that's SKOS/domain classes).

### RDFS / OWL — the schema layer, used sparingly
**What:** classes, properties, subclass/subproperty, domain/range (RDFS);
equivalence, disjointness, inverses, cardinality (OWL).
**Why:** we need *some* real classes — `ProcessDefinition`,
`ResponsibilityAssignment`, `NamedKPI` — and the relations
between them. RDFS/OWL defines those precisely.
**Constrained:** RDFS/OWL is *inference*, not validation. Domain and range
do not check data; they generate new triples. We never use OWL to "fix"
the taxonomy, and we assert disjointness or cardinality only where the
business actually guarantees it (cf. the office-lanes decision).

### PROV-O — what happened and who vouches for it
**What:** `prov:Entity`, `prov:Activity`, `prov:Agent` — provenance of
how something came to be.
**Why:** two jobs. (1) *Occurrences vs definitions:* a planned process
is a definition; a run of it on a date is a `prov:Activity`. The split
keeps the model from confusing the recipe with the meal. (2) *Trust:*
which source asserted this mapping, when, under what authority.
**Rejected:** typing taxonomy concepts as `prov:Activity` by default. A
process definition is not an activity that happened.

### ORG (Organization Ontology) — roles for RACI
**What:** `org:Role`, `org:Membership`, posts and organizations.
**Why:** RACI needs roles that people hold, not people themselves — the
same person can be Accountable for one process and merely Informed on
another. `org:Role` gives us that indirection; the n-ary
`ResponsibilityAssignment` then binds role + process + RACI level, which
a single property never could.
**With:** FOAF (`foaf:Agent`/`foaf:Person`) for the actual people and
teams behind the roles, and `dcat:contactPoint` for ownership surfacing.

### SHACL — the checking layer
**What:** a shapes graph of constraints, written in RDF, run against the
data graph to produce a validation report.
**Why:** every locked decision that can be checked mechanically becomes a
shape: labels present, identifier policy followed, hierarchy integrity
(one parent per concept), controlled values (lanes, RACI levels),
`dcterms:references` present where APQC alignment is claimed.
**Constrained:** Core SHACL first; SHACL-SPARQL only where Core cannot
express the constraint. Validation reports are data, not verdicts — a
failing shape is a question for a human, not proof of a bad model.

### DCAT — publishing
**What:** `dcat:Catalog` → `dcat:Dataset` → `dcat:Distribution` /
`dcat:DataService`.
**Why:** the end state is a *published, versioned artifact*, not a file
on a disk. DCAT gives us the catalog record: what the dataset is, which
version, which distributions (Turtle, JSON-LD, SHACL shapes, HTML docs),
where it lives, who to contact. The dataset-vs-distribution distinction
is load-bearing: one dataset, many serializations.
**With:** DQV for quality measurements on the data products, and
`dcterms:license` / ODRL where rights need expressing beyond a license
URI.

### What we evaluated and set aside
- **W3C SIOC** (social/online-community vocabulary): not applicable;
  the repo JSON's `sioc` field is still unconfirmed and must not be
  confused with it.
- **ODPS family** (Open Data Product Specification / ODPC / ODPV / ODPG):
  mapped for awareness (ODPC→DCAT, ODPV→SKOS, ODPG→RDF) but not adopted —
  the W3C stack covers our needs without adding a second modeling
  idiom. Revisit if the data-product catalog work demands it.

---

## 6. Repo-specific notes for the team

Facts about the source material that are easy to get wrong:

- **Scale:** ~680 nodes, levels L0–L6 (L0: 2, L1: 10, L2: 4, L3: 24,
  L4: 117, L5: 502, L6: 21). 669 nodes have IDs; **11 roots/stubs do
  not** (Downstream Operations, Refining, Midstream, Enabling Functions,
  Supply Chain Mgmt., Finance, Shared Services, Process Excellence & IT,
  Human Resources, Legal & Corp Comm, EHS & Gov Reporting). Step 2 mints
  IDs for all 11.
- **Codes like `CM 1.2.1.3` are `skos:notation`**, not APQC identifiers
  and not globally unique outside this map.
- **`officeLane` values:** `front_office`, `middle_office`,
  `back_office`, `operations`. Not declared disjoint.
- **The `sioc` JSON field is unconfirmed.** Verify whether it means
  SIPOC/SIOC in the business sense before minting any ontology term.
- **Known data gaps to resolve in Step 7:** all 46 Order-to-Cash
  processes have empty `produces` arrays; no AR credit/receivables/
  collections portfolio exists (do not reuse `dp-commercial-risk`);
  `office_lanes.json` is not linked by ID; Loss Control exists as a
  data-product concern with no owning process.
- **Systems vocabulary in the map:** XPIMS, DPO, PPIMS, MPR, Profisee,
  KittyHawk, RightAngle. System-specific jargon depresses naive
  term-overlap scores — coverage triage is human work.
- **Local extensions to keep** even without APQC equivalents:
  renewables/RINs, emissions trading, crude-allocation decisions,
  XPIMS/DPO/PPIMS-specific processes.

## 7. How the team should work from this playbook

1. **Read §1–§2** for the shape of the whole build; **§5** before
   touching any standard.
2. **Check §4** before making any modeling choice — if the decision is
   locked, follow it; if you believe it's wrong, raise it with Hamid
   and record a dated amendment. Do not silently override.
3. **Work one plan step at a time**, in order, appending the step's
   entry to §3 with: what was done, what was decided, and what remains
   open.
4. **Run the competency questions** (`competency-questions.md`) against
   the model early and often — a question the model can't answer is a
   modeling gap, not a bad question.
5. **Boundary notes are decisions too.** "Out of scope" with a recorded
   reason beats silent omission; future-you will thank present-you.
6. **Definition authoring workflow (Step 3c, locked 2026-09-19).**
   Hamid or a designated reviewer fills the 6-sheet semantic-intake
   workbook `step3c-definition-authoring-workbook.xlsx` and returns it
   to Hamid or commits it to a reviewer branch — never `main` directly.
   The assistant pulls it, runs `step3c-workbook-validate.py`
   (mechanical gate), then performs a full semantic review. Every doubt
   comes back to Hamid as a question. Only `approved` rows whose
   questions are resolved merge into the taxonomy via
   `step3-skos-taxonomy.py --authored`. Nothing merges on assumption —
   the human gate from Step 3b applies to human-authored text too.
   The locked reviewer guide is
   `business_architecture/ontology/step3c-reviewer-instructions.md`
   (v2026-09-19b, PTC parking rule after #35); its 10-point quality bar
   is the merge gate. Hard
   requirements enforced mechanically: every approved row has a
   non-empty `definition` and a non-empty `scope_note` with at least
   one meaningful boundary; `status` is `pending`, `approved`,
   `blocked`, or `retired` (only `approved` merges); new approvals
   also require `concept_type_check` ∈ {process, capability},
   `primary_purpose`, and `reference_sources` that resolve to the
   Reference register; `open_questions` must be empty on `approved`;
   no `altLabel` collides with another concept's `prefLabel`. The 15
   rows approved in #29 are explicitly grandfathered for Phase 1
   (`PRE_INTAKE_APPROVED` → NOTE, not BLOCKING). Semantic checks done
   by the reviewer: parent test, sibling disjointness, primary-purpose
   classification, terminology stability, no invented owners, no
   smuggled constraints. Tree moves accepted during review go in
   `step3c-parked-tree-changes.md`; affected rows are `blocked` or
   `retired` until the Step 3d JSON/TTL pass.

### Enterprise-grade definition review bar (summary; authoritative text in the reviewer guide)
1. **Define, don't label** — state the recurring activity and intended outcome.
2. **Primary purpose** — the decision/outcome/responsibility served, not asset, department, or data source; no duplicated concepts for multi-purpose activities.
3. **Bounded** — scope note required on every approved row; exclusions name the owner only when established in the taxonomy.
4. **Parent test** — "this process is a way of carrying out [parent process]" must hold.
5. **Sibling-disjoint** — no two siblings claim the same primary activity.
6. **Terminology-stable** — one meaning per material term across the scheme.
7. **Park, don't smuggle** — future processes in `parked_children`; no data fields, systems, KPIs, controls, or thresholds as concepts.
8. **Evidence-based** — high-quality references inform; nothing copied verbatim.
9. **Planning baseline preserved** — backcasting compares against the approved plan and contemporaneous assumptions.
10. **Provenance-clean** — `dcterms:source` records human authorship, Hamid's approval, and date.

---

## Appendix A — Parked items

Things deliberately deferred, with what it takes to revive them.

### Constraints module (parked 2026-09-18)
Not being modeled. The removed competency questions are preserved here so
a future pass can pick them up unchanged:
- What is a Constraint vs a Threshold vs a Breach vs a Binding?
- Does a KPI *have* a constraint, or *is* it a constraint?
- Who owns a constraint family (HSE, quality, commercial, planning) vs
  who owns the KPI?
- Can the same limit value be reused by more than one KPI without copying
  the meaning?
- How does a breach *occurrence* (something that happened on a date)
  relate to the constraint *definition*?
- *Done when:* Store KPIs reference constraints; they do not subclass
  them.
Revival trigger: the Store or Genie needs to reason about limits, not
just KPIs.

---

### Value-stream / capability / activity / event / decision / KPI / data-product layer (parked 2026-09-22)
Not in 1.0.0. The fuller business-architecture hierarchy — domain >
value stream > stages, value stream > capability > business process >
activity, plus events, decisions, KPIs, and data products — is real and
will be represented, but as **governed overlays over the process
backbone, not as a second hierarchy inside it**. A value stream cuts
across the tree (Order to Cash touches commercial, finance, credit,
legal); the taxonomy gives every concept exactly one parent, so value
streams cannot be parents — they are views. The existing JSON overlays
already follow the right pattern: they *reference* process nodes via
`linkedProcessIds` instead of duplicating them
(`business_architecture/business_process/value_stream_*.json`,
`business_architecture/schema/value_stream.schema.json`), and the data
product portfolio links processes to data products with sparse
produces/consumes relations (`business_architecture/business_process/
data_product_portfolio.json`, dp-\*/dpl-\*). Where each layer lives:
- Domain / value stream / stages / capabilities-as-views → parked
  overlays (this item).
- Capability kind → Q8 `conceptKind` (Step 4): `core:CapabilityKind`
  classifies a concept as capability-like. Actual business capabilities
  are a future `core:BusinessCapability` class (architecture entities,
  not classification values), linked to processes via
  `core:realizedBy` when the value-stream overlay is designed.
- Business process → `core` 1.0.0 (Step 4).
- Activity → future decomposition below L6.
- Events → occurrences, Step 6 PROV-O.
- Decisions → future decision modeling.
- KPI → `kpi` module (Named KPIs bound to processes/capabilities; the
  KPI Store on Databricks is the delivery side).
- Data products → portfolio JSON now; ontology produces/consumes links
  (critical-path only) when promoted.
*Done when:* a consumer needs value-stream, capability, activity, event,
decision, KPI, or data-product reasoning — then promote the overlays to
governed ontology views, one at a time, against the stable 1.0.0
backbone.
Revival trigger: someone asks the model a question like "show me the
Order-to-Cash value stream end to end" and the backbone alone cannot
answer it.

---

## Appendix B — Versioning in detail

### The rule in one sentence
**URIs are forever; versions describe what changed around them.**
A consumer who bookmarked `…/process/CM-1-2-4-4-2` in 2026 must get a
correct answer in 2030. That is the entire policy.

### Version numbers
SemVer `MAJOR.MINOR.PATCH`, applied **per module** and to the **release
as a whole**. The release version records exactly which module versions
it bundles (e.g. release `1.2.0` = core 1.0.2 + party 1.3.0 + kpi 1.1.0
+ organization 1.0.0).

### What counts as what

**Major (breaking)** — anything that can make an existing consumer
wrong:
- A concept's URI changes (should never happen; if it does, it's major).
- A concept is removed.
- A definition's *meaning* changes, not just its wording. Example: the
  `3-2-1 Crack Spread` population changes from "all USGC CBOB" to "all
  PADD 3" — every historical query using the old meaning is now wrong.
- A `skos:broader`/`narrower` change that alters what a concept *means*
  (e.g. moving a process under a different parent changes its inherited
  context).

**Minor (additive)** — anything new that breaks nothing:
- New concepts (e.g. adding the 7.2/7.3/7.5 HR processes under
  `L1-human-resources`).
- New modules, new `altLabel`s, new `dcterms:references`.
- Hierarchy additions that don't redefine existing concepts.

**Patch (clarifications)** — nothing semantic changes:
- Typo fixes in labels.
- Definition *wording* clarified with the meaning intact.
- Adding an example or scope note.

**The meaning-change test.** Ask: *would every query, report, and Genie
answer produced under the old definition still be correct under the new
one?* Yes → patch. No → major. When in doubt, it's major — a false major
costs a version bump; a false patch corrupts downstream consumers
silently.

### Deprecation protocol (never delete)
1. Mark the concept `owl:deprecated true`.
2. Add `dcterms:isReplacedBy` pointing at the successor concept.
3. Keep all existing triples (labels, definitions, references) intact —
   the concept becomes a tombstone that still answers "what did this
   used to mean?"
4. Record the deprecation in the changelog with the reason.
5. Only a **major** release may introduce deprecations.

Rationale: deleting a URI orphans every catalog row, RACI assignment,
and KPI binding that pointed at it. Storage is cheap; broken references
are expensive.

### Ontology identity and header
The ontology is named, not anonymous. Each module ships one
`owl:Ontology` resource that carries the release metadata:

```turtle
<https://w3id.org/lsc/ontology/modules/core>
    a owl:Ontology ;
    dcterms:title "LSC Core Process Ontology"@en ;
    dcterms:description "Governed definitions of LSC's business processes: identity, hierarchy, relationships, and lifecycle."@en ;
    owl:versionIRI <https://w3id.org/lsc/ontology/modules/core/1.0.0> ;
    owl:versionInfo "1.0.0" ;
    dcterms:issued "2026-09-22"^^xsd:date ;
    dcterms:modified "2026-09-22"^^xsd:date ;
    dcterms:creator "Hamid" ;
    dcterms:license <https://w3id.org/lsc/ontology/modules/core/license> ;
    dcterms:rights "© LSC. All rights reserved. APQC PCF content used with attribution per APQC/IBM terms."@en .
```

Rules:
- **Ontology IRI is stable** (`…/ontology/modules/core`). It names the module,
  not the release.
- **Version IRI is per release** (`…/ontology/modules/core/1.0.0`). Consumers
  who pin a release cite the version IRI; consumers who want currency
  use the ontology IRI.
- **Term IRIs never carry a version** (`core:ProcessDefinition`, not
  `core/1.0.0/ProcessDefinition`). Versioning a term IRI would fork
  identity — the exact thing this policy forbids.

### Version history
- **Pre-1.0.0 (before 2026-09-22).** Unversioned working builds. No
  `owl:versionInfo` was shipped; the taxonomy iterated through Steps
  1–3d and the R1 reclassification without a formal release.
- **1.0.0 (Step 4, decided 2026-09-22).** First formal release of
  `core`. Retires the provisional `intake:` namespace, promotes intake
  annotations to governed properties, and ships the first explicit
  version header. Baseline for everything after.

### What every release ships
- `owl:versionInfo` on each module and on the release (`"1.2.0"`).
- `dcterms:issued` (first publication) and `dcterms:modified` (this
  release) dates.
- A changelog entry per change: what changed, why, who approved, and
  the SemVer classification. Format:
  `[minor] Added skos:Concept L1-human-resources children 7.2/7.3/7.5
   per APQC scope decision 2. Approved: Hamid, 2026-09-18.`
- The DCAT catalog records the release as a new `dcat:Dataset` version
  with its distributions (Turtle, JSON-LD, SHACL shapes, HTML docs).

### Version-agnostic vs versioned access
- **Canonical URIs carry no version** (`…/process/CM-1-2-4-4-2`).
  They always resolve to the *current* meaning.
- **Snapshots are versioned at the distribution level**, not the
  concept level: `…/releases/1.2.0/ontology.ttl` gives you the whole
  graph as of 1.2.0. Consumers who need reproducibility pin the
  distribution; consumers who need currency use the canonical URI.

### APQC version changes
When APQC publishes v7.3 or v8:
1. Our URIs do not move (they're ours, not APQC's).
2. Each `dcterms:references` annotation is reviewed against the new
   workbook; stale ones (like the 10006→20085 case) are corrected.
3. Newly relevant APQC elements go through the scope-review process
   (Step 8) before any modeling.
4. The APQC version underpinning the alignment is recorded on the
   release (`dcterms:references` on the dataset, plus a line in the
   changelog). This is a **minor** release at most — usually a patch.

### Who approves a release
Minor and patch: the module owner. Major (including any deprecation):
Hamid. No exceptions — majors change the meaning of published truth.
