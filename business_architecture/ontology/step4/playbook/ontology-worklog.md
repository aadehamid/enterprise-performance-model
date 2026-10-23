# Ontology Worklog — Downstream Process Map

> **Renamed 2026-09-30** from `ontology-playbook.md` to `ontology-worklog.md`,
> so the name says what this file is: the running log of this build. The
> method keeps the playbook name (`business_architecture/ontology/ontology-playbook.md`).
> Earlier entries and PR bodies refer to this file by its old name.

**Status:** Living document. Updated as each plan step completes.
**Owner:** The decision owner · **Built with:** Kailey
**Started:** 2026-09-17

## About this document

This is the working record of how the downstream process map becomes an
ontology. It captures the plan, the decision at every step, the answer each
step produced, and — most importantly for handover — *why* each standard was
chosen and what was deliberately rejected.

**How to maintain it:** when a plan step completes, append its entry to
§3 (Step log) and move any new durable decision into §4 (Decision log).
*Decided 2026-10-05 (EPM-DEC-001-0002), amended 2026-10-06
(EPM-DEC-001-0024, decided):* the playbook (`business_architecture/ontology/ontology-playbook.md`)
is now a company-neutral method. A project
decision gets an EPM-DEC-001 record (`business_architecture/domain/decisions/`)
and a dated pointer in §4 here; the playbook changes only when the method
changes.
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
`<owner>/enterprise-performance-model` repo (680 nodes, levels L0–L6).
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
| 3d-b | PTC-001 Tree Remediation Log — PR #86 (Commercial Development tombstone + 2 reparented L3s + 2 Candidate L2s); PR #87 definition mini-batch; PTC-001-B confirmed as intentional strategy-ownership hold (the decision owner, 2026-09-22). PTC-001 stays open until PTC-001-B closes. | ✅ Partially resolved; hold by design |
| 3d-c | R1 Refining Structural Reclassification — decision package approved as Candidate 2026-09-22 (tombstone re-anchor confirmed); implementation PR #108 merged 2026-09-22 (merge b75fd991). 42 concepts reparented with stable slugs/IRIs/notations; two promoted L2s (Refinery Planning and Optimization; Refinery Production Planning and Scheduling); new Candidate R&T L2; tombstone re-anchored under Planning & Scheduling; reviewed RO→Refining interface relation materialized. 683 concepts, 14,496 triples (+15), 681 broader links. | ✅ Candidate → Implemented 2026-09-22 |
| 3d-d | R2 backlog (open by design) — operating-execution layer (unit operations, line-ups, blend execution, process control); maintenance/turnaround ownership question; R2 Refinery Vocabulary and Operating-Lifecycle package (turnaround/shutdown/startup/plan/schedule distinctions); Energy & Utility Management temporary-placement review trigger. *2026-10-19:* decided, each item out with its trigger or answered for the map's scope (EPM-DEC-001-0063). | ✅ Decided 2026-10-19 (EPM-DEC-001-0063) |
| 4 | Process-definition ontology (ProcessDefinition/ProcessType; systems, variants, lanes, flags, capabilities, value streams) | PROMOTED 2026-09-30 |
| P1 | Phase 1: source-workbook corrections for the held Step 4 rows (G3 Section B, G1b pairs, S&T, triggers, precedes/follows, governed-by). One GitHub issue per backlog section; batches of about 12 rows grouped by target process (EPM-DEC-001-0003) | ✅ Done 2026-10-13: six sweep batches merged (#239, #241, #243, #244, #247, #248); 51 rows stay held with reasons |
| R1 | `core` 1.0.0 release, after Phase 1: canonical facts to Turtle, zero `intake:`, fresh attestation, SHACL release slice, LPG design Rules 1, 2, 3 and 5 (EPM-DEC-001-0013, 0014, 0020). MPC-P02 IDs proposed before it (EPM-DEC-001-0011, 0012) | ✅ Released 2026-10-13 (#249, tag `core-v1.0.0`), approved by the decision owner |
| 5 | ORG + RACI (roles as `org:Role`; explicit n-ary ResponsibilityAssignment); `ref-mpc` reference module; MPLX control relation as a qualified-relation node (EPM-DEC-001-0015). Customer roles wait (EPM-DEC-001-0004); *2026-10-21:* the Customer work resumes (EPM-DEC-001-0067); the `party` module holds the party roles as dated nodes (EPM-DEC-001-0068) | ✅ Done 2026-10-22 (EPM-DEC-001-0083). Forecaster stays apart from the Local Refinery Forecaster until the refinery Economics and Planning process owner confirms they are the same (EPM-DEC-001-0045, decision 2), and PSM stays unresolved (decision 6). Started 2026-10-13: vocabulary and shapes (EPM-DEC-001-0030), the role register (EPM-DEC-001-0031) and the RACI assignments (EPM-DEC-001-0032) in `organization/`, with the RACI scope set by the decision owner to the 153 processes with source RACI; `ref-mpc` reference instances (EPM-DEC-001-0033); the `core:responsibleDomain` values are business domains (the decision owner), carried by core 2.0.0 (approved by the decision owner 2026-10-13) (EPM-DEC-001-0038); the decision owner's role answers in organization 2.0.0, 2026-10-18 (EPM-DEC-001-0045) |
| 6 | Interfaces and PROV-O (planned inputs/outputs vs observed executions; `prov:Activity` only for occurrences); P-Plan bridge; occurrences held by consumers (EPM-DEC-001-0016) | ✅ Done 2026-10-22 (EPM-DEC-001-0083). By design, runs stay with the consumers (EPM-DEC-001-0016); `provenance/run-shapes.ttl` checks them there (EPM-DEC-001-0034). Started 2026-10-13: the definition-to-run pattern in `provenance/` (EPM-DEC-001-0034); planned inputs and outputs from the SIPOC field (the decision owner confirmed) in core 2.0.0 (approved by the decision owner 2026-10-13) (EPM-DEC-001-0038) |
| 7 | Cross-model integration (link processes, value streams, capabilities, systems, data products; resolve empty O2C outputs, Loss Control ownership). Order: Pricing KPI definitions (seeded from the decision owner's planner measure list since 2026-10-18, EPM-DEC-001-0040), Market Data and Commercial Risk, data products, MPC-P01 and P03 to P09 (EPM-DEC-001-0017, 0010, 0011); external mappings (EPM-DEC-001-0023) | ✅ Done 2026-10-22 (EPM-DEC-001-0083). PIDX and OEO wait for product values and IOF Supply Chain is parked, each with its trigger (EPM-DEC-001-0064); MPC-P10 is the decision owner's (EPM-DEC-001-0070); the four codes and TID Nbr wait for the business (EPM-DEC-001-0072). Started 2026-10-18: the `kpi` module, 41 measure definitions classified by kind, released as `kpi` 1.0.0 on 2026-10-19 with the decision owner's approval (EPM-DEC-001-0040, 0042, 0043). 2026-10-19: the `data-product` module, 48 data products from the portfolio, 15 defined and 33 parked for lack of a description; Loss Control's owning process is CM 1.1.3.7.13, its link waiting for `core` 2.2.0 (EPM-DEC-001-0053); not released. 2026-10-19: the `value-stream` module, the Commercial Hydrocarbon Lifecycle and Order to Cash, with 58 value-stream processes, their capabilities, data product links and the MPC-P09 measure links (EPM-DEC-001-0054); not released. 2026-10-19: the `system` module, 32 systems from the map's 37 system strings, merged on spelling, linked to 150 processes (EPM-DEC-001-0055); not released. 2026-10-19: the `lane` module, the four office lanes and the seven processes the map places in them (EPM-DEC-001-0056); not released. 2026-10-19: the `market-data` module, five crack-spread series of one measure, from MPC's FY2025 Form 10-K, Item 7, and CME Group ("Trading Crack Spreads", 2024; "Introduction to Crack Spreads", 2017; "Fresh from the Trading Room", 2026-07-14) (EPM-DEC-001-0057); not released. 2026-10-20: MPC Economics' definition made the primary source; the module now has 13 series, adding its six regional ex-RIN series, the NYMEX 3-2-1's ID and two MPC-weighted blends (EPM-DEC-001-0066); not released. 2026-10-19: the placement kinds, which say what each placing property claims (EPM-DEC-001-0058); not released. 2026-10-19: the external mappings decided (EPM-DEC-001-0064): GLEIF and DCAT mapped; PIDX and OEO wait for a product dimension; IOF Supply Chain parked. *2026-10-21:* the `party` module (EPM-DEC-001-0068); not released. *2026-10-21:* the `party` module's systems, data flow and attributes (EPM-DEC-001-0069) and lifecycle linked to core processes and systems (EPM-DEC-001-0070); not released. *2026-10-22:* released as `party` 1.0.0 (EPM-DEC-001-0074). *2026-10-22:* `data-product`, `value-stream`, `system`, `lane` and `market-data` released as 1.0.0 (EPM-DEC-001-0077). *2026-10-22:* the placement kinds, source tiers and consumer rules released in `integration` 1.0.0 (EPM-DEC-001-0078). *2026-10-22:* the PIDX, OEO and IOF triggers re-checked on the released packages; none is met (EPM-DEC-001-0064). |
| 8 | APQC scope review (seven candidates, one at a time) | ✅ Done 2026-09-17 |
| 9 | SHACL (labels, identifier policy, hierarchy integrity, controlled values, references, profiles) | ✅ Done 2026-10-22 (EPM-DEC-001-0081). The release slice ships in `core` 1.0.0 (EPM-DEC-001-0014); controlled values in `validation/` (EPM-DEC-001-0035), 2026-10-13; `core` 2.1.0 carries the controlled-value shapes and one evidence node per canonical fact, with the evidence-link shapes (EPM-DEC-001-0044), 2026-10-18; every module's shapes run together on the whole graph with zero violations (EPM-DEC-001-0065), 2026-10-19; *2026-10-22:* every release package conforms to its own shapes over the packages it requires (EPM-DEC-001-0081). Exception by design: `provenance/run-shapes.ttl` checks consumers' runs (EPM-DEC-001-0016, 0034) |
| 10 | DCAT publication (catalog → versioned dataset → distributions) | ✅ Done 2026-10-22 (EPM-DEC-001-0083). "Catalog resolves" stays parked: the namespace is not hosted (EPM-DEC-001-0039). Started: `core` 1.0.0 packaged with its DCAT record (EPM-DEC-001-0029); organization 1.0.0 and ref-mpc 1.0.0, approved by the decision owner and issued 2026-10-13 (EPM-DEC-001-0037); `core` 2.0.0, approved by the decision owner and issued 2026-10-13 (EPM-DEC-001-0038); `core` 2.1.0, issued 2026-10-18 with the decision owner's approval (EPM-DEC-001-0044); organization 2.0.0 (2026-10-18) and ref-mpc 1.1.0 (2026-10-19), approved by the decision owner (EPM-DEC-001-0045); kpi 1.0.0 (2026-10-19), approved by the decision owner, and kpi 1.0.1, a patch naming the list's source VCO DSV (EPM-DEC-001-0043); not hosted, the namespace a placeholder (the decision owner, EPM-DEC-001-0039); under the delegation, no w3id registration, so the gate's "catalog resolves" is parked until a domain is decided; the licence is proprietary (the decision owner, EPM-DEC-001-0041, 2026-10-18); *2026-10-22:* `party` 1.0.0, the module's first release, approved by the decision owner (EPM-DEC-001-0074); *2026-10-22:* `core` 2.2.0 (EPM-DEC-001-0076), `data-product`, `value-stream`, `system`, `lane` and `market-data` 1.0.0 (EPM-DEC-001-0077), `integration` 1.0.0 (EPM-DEC-001-0078) and `kpi` 1.1.0 (EPM-DEC-001-0079), each under the release plan the decision owner approved, and `ref-mpc` 1.2.0, approved by the decision owner on its own (EPM-DEC-001-0080); *2026-10-22:* `releases/catalog.ttl`, one DCAT catalog of all 19 releases, checked in `check.sh` (EPM-DEC-001-0082) |
| 11 | SPARQL regression tests (missing RACI, systems, products, orphans, lanes, ownership); coverage re-run after each module (EPM-DEC-001-0019) | ✅ Done 2026-10-22 (EPM-DEC-001-0083): 43 answerable, 0 partial, 1 waiting. Q17 waits on the decision owner (EPM-DEC-001-0045, decision 7). Started 2026-10-13: harness in `regression/`, run by `check.sh`; on core 2.1.0 with the organization and kpi modules, 17 answerable, 6 partial, 21 waiting (2026-10-18); with the data-product module, 17 answerable, 7 partial, 20 waiting (2026-10-19); with the value-stream module, 18 answerable, 7 partial, 19 waiting (2026-10-19); with the system module, 19 answerable, 7 partial, 18 waiting (2026-10-19); with the lane module, 20 answerable, 7 partial, 17 waiting (2026-10-19); with Q15 answerable, 21 answerable, 7 partial, 16 waiting (2026-10-19); with the market-data module, 23 answerable, 7 partial, 14 waiting (2026-10-19); with the placement kinds, 26 answerable, 5 partial, 13 waiting (2026-10-19); with the source tiers, 27 answerable, 4 partial, 13 waiting (2026-10-19); with the APQC element list, 30 answerable, 1 partial (Q7), 13 waiting (2026-10-19); with the consumer rules, 33 answerable, 1 partial (Q7), 10 waiting (2026-10-19); with the measure populations, 34 answerable, 1 partial (Q7), 9 waiting (2026-10-19); *2026-10-21:* the `party` module made Q19 to Q26 answerable: 42 answerable, 1 partial (Q7), 1 waiting (Q17) (EPM-DEC-001-0071); *2026-10-22:* on core 2.2.0, Loss Control's producer is linked and Q7 is answerable: 43 answerable, 0 partial, 1 waiting (Q17) (EPM-DEC-001-0076). |
| 12 | LPG projection to Neo4j after the build, per `lpg-projection/` with the qualified-relation deviation (EPM-DEC-001-0020) | ✅ Done 2026-10-22 (EPM-DEC-001-0083). 16 rule gaps in released modules are listed, each to close at that module's next release (EPM-DEC-001-0036, amendment of 2026-10-22). Started 2026-10-13: the pipeline in `projection/` (EPM-DEC-001-0036) passes on core 2.1.0 with organization 2.0.0 and the ref-mpc module, with no listed release gap (2.0.0 closed core 1.0.0's two Rule 1 gaps); *2026-10-22:* rerun on core 2.2.0: 2,834 nodes, 14,934 relationships, no in-graph violation, empty round-trip diff, equal determinism hashes; *2026-10-22:* widened to every released package: 3,925 nodes, 19,692 relationships, no in-graph violation, empty round-trip diff, equal determinism hashes, 16 release gaps listed with their fixes (EPM-DEC-001-0036, amendment of 2026-10-22) |

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
  `The decision owner's account` — **merged 2026-09-18**.

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

**Competency questions** — reviewed and approved by the decision owner; merged
baseline of 44 questions in `competency-questions.md`, locked 2026-09-18.
These double as the Step 11 SPARQL regression tests: the exam is written
before the coursework. Constraints section removed at the decision owner's direction —
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
  *Amendment 2026-10-14:* The decision owner decided not to host the namespace and to
  keep it as a placeholder, because the domain may change. Under the
  delegation, it is not registered, so no redirect is in place and the
  sentence above about w3id.org redirects describes the plan, not the
  current state (EPM-DEC-001-0039).

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
  the decision owner is the IP owner. Rationale: the ontology describes LSC's actual
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
  independently; minor/patch approved by module owner, majors by the decision owner.

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
  **Step 3c** (2026-09-18) human-authored the 14 L1–L3 gaps with the decision owner.
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
at a time with the decision owner: 10 L1 enabling/value-chain functions (Commercial
& Marketing, Refining, Midstream, Supply Chain Management, Finance,
Shared Services, Process Excellence & IT, Human Resources, Legal &
Corporate Communications, EHS & Government Reporting) and 4 commercial
planning stubs under C&M › Planning & Scheduling (Regional
Optimization, Regional Backcasting, Refinery Planning, Distribution
Backcasting).

- **Working method:** draft → the decision owner's wording (most L1s are theirs, verbatim
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
  the decision owner, dated) per concept; validation asserts hold. Taxonomy now:
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
  the decision owner: regen now (parallel to review batches) → finish 3c → 3d tree
  reconciliation → Step 4 design together.

- **Closeout (2026-09-21, batch 42, PR #82).** Step 3c is finished:
  approved=498, pending=1 (`CM-1-1-3-5-3`, the intentional business-evidence
  hold from batch 05 — not forced), blocked=3 (PTC-001), retired=1
  (`CM-1-1-4-6`); gate blocking=0, questions=0, notes=15, open_ptc=1.
  the decision owner's **option A** decision admitted the two L0 scheme roots
  (`L0-downstream-operations`, `L0-enabling-functions`) as the only approved
  `not-process` rows via a frozen `SCHEME_ROOT_APPROVED` whitelist, mirroring
  the `PRE_INTAKE_APPROVED` pattern. Batches 23–41 covered Offer/Pricing/
  Channel (23), Network/Communications/Operating Model (24), Visioning/Concept/
  Product Development (25), Order Management, SCM, Finance/Accounting, Service
  & Support, and Terminal Commercial Operations (41).
- **Final TTL regen (2026-09-21, PR #83).** Per the decision owner's sequencing decision
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
  itself — proposals go to the decision owner for review like any batch.

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
  no renames by itself — proposals go to the decision owner for review like any
  batch, and each executed rename promotes the queued label to prefLabel
  with the old name kept as alt label (subject to the collision and
  refinement rules recorded 2026-09-21, below), then sweeps the workbook,
  TTL regen, identity map, and cross-references, and re-runs the gate.
- **Phase 1 executed and merged 2026-09-21 — all 9 critical collisions.** All 9
  critical collisions renamed per the decision owner's approval (2026-09-21), with two
  refinements over the queued labels: `CM-1-1-1-1` → **Produce Demand
  Forecast** (verb-led; `Demand Forecasting` is NOT kept as an altLabel
  because the L3 parent keeps it as prefLabel) and the six
  `Define KPI Framework` rows take domain-specific labels with the
  shared generic label NOT kept as an ontology altLabel (scoped
  historical aliases such as `Define KPI Framework (Offer)` recorded in
  the identity/migration map). The sixth KPI row (`CM-1-3-3-5-7`,
  Marketing Communications) was discovered after the initial 8-rename
  execution and renamed in a follow-up commit per the decision owner's decision
  the same day. PR #84 (8 renames) and PR #85 (9th rename) both merged
  by the decision owner 2026-09-21 — **nothing merged on assumption**.
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
  by the decision owner 2026-09-21 — **nothing merged on assumption**. The taxonomy is
  unpublished with no external consumers (the decision owner, 2026-09-21), so no
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
  the decision owner approved the revised consolidated proposal
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
  cleanups were applied before merge per the decision owner's call: (1) the risk L3's
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
  mandate, renamed per the decision owner's approval 2026-09-21 — `CM-1-2-4-2-12` →
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
  wording left the process scope ambiguous, renamed per the decision owner's approval
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
  whose wording left the process scope ambiguous, renamed per the decision owner's
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
  distinction, renamed per the decision owner's approval 2026-09-21. Claims lifecycle
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
  renamed per the decision owner's approval 2026-09-21. Terminal commercial
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
  Service Delivery (the decision owner's approved plural refinement of the queued
  singular); `Fulfill Service Event` -> Fulfill Service Events. Workforce
  (`CM-1-3-9-3-2`): `Measure Service Employees` -> Measure Service
  Workforce Performance. Ten old labels retained as `skos:altLabel`; the
  bare `Manage Customer` kept only as `prior_name`/`name_change_note` in
  the identity map — not a live `skos:altLabel` — because it is a prefix
  of live labels (Manage Customer Portal, Manage Customer Invoicing and
  Billing, Manage Customer Requests and Inquiries) and would reintroduce
  search ambiguity; the queued singular near-duplicate `Manage Customer
  Interaction in Service Delivery` was also dropped (the decision owner approved the
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
  per the decision owner's approved sequencing (mechanical first, judgment second):
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
  naming batch: 12 renames per the decision owner's approved judgment proposal 2026-09-22
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
  reparenting chore, and it needs the decision owner's explicit scope expansion.
- **How it gets picked up.** Not by memory. The gate reads the register
  every run, prints `open_ptc=N` in its summary line (which lands in
  every batch PR body), and raises BLOCKING `step-3c-not-complete` if the
  definition queue reaches zero while any entry is open. Step 3c cannot
  be declared finished with a tree change outstanding.
- **Done when.** Every PTC entry closed with its checklist worked, parked
  rows re-statused to `pending` under real parents, identity map and TTL
  regenerated, and the gate reporting `open_ptc=0`.
- **R1 Refining structural reclassification — IMPLEMENTED 2026-09-22 (PR #108 merged).**
  the decision owner approved the Candidate package and, after two review rounds, merged PR #108
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
- **R1 review rounds (2026-09-22).** Round 1: The decision owner returned "approve after one
  required correction" — the taxonomy-report generator still hard-coded "680
  broader links" in its validation prose; fixed to the derived count, report
  regenerated, gates rerun. Round 2: The decision owner requested (a) the report prose fix
  be completed, (b) the reviewed RO→Refining interface relation materialized in
  the TTL behind a reviewed-interface allowlist (any unreviewed pending-row
  `related_concepts` entry fails the build loudly instead of emitting), and
  (c) softened triple-delta wording; all applied and re-verified before merge.
  Pre-merge the decision owner caught one workbook-only regression the gates had missed: the
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
  the decision owner's explicit approval. PR #30 remains parked. The consumer-inventory
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

### Step 4 — verb-predicate mapping ✅ (verb review on main 2026-09-29; PROMOTED 2026-09-30)

Promoting the workbook's raw relationship verbs to canonical ontology
predicates — with every row earning its verdict and every figure earning
its place.

**The approach.** The workbook's `verb` column is a claim, not a fact.
Step 4 treats each of the 1,318 relationship mentions as a candidate that
must pass a semantic test before it becomes a canonical fact — or be
held with a recorded reason. The approach, in five parts:

1. **Predicates have definitions, not vibes.** Each canonical predicate
   carries a precise semantic test, decided with the decision owner before any row
   was judged: `core:requires` = the source cannot validly proceed
   without the target (not merely "the target later uses related
   info"); `core:assuredBy` = a defined governance/compliance/quality/
   review/control-testing oversight role (not "supports" or "is
   necessary for"); `core:constrainedBy` = the bounded activity points
   to its binding constraint source; `core:triggeredBy` = a defined
   invoking event, exception, detection, or handoff (not "feeds" or
   "precedes"); `core:enabledBy` = the source supplies a maintained,
   governed, or operationally necessary base, passing a six-part test
   (identity, capability effect, independence, authority, predicate
   integrity, provenance). Precedes/follows Rule 5: siblings need only
   structural nearness; non-siblings need an affirmative sequence
   citation or a two-way route.
2. **Buckets, not beliefs.** Every mention lands in exactly one bucket:
   emitting (on a canonical fact), held (verdict-recorded, off the
   fact), deferred, external governance, structured flow, or scoped
   sequence (a scoped-sequence node, EPM-DEC-001-0026). Counts move
   only when a row changes bucket — approving an already-emitting row
   changes its basis, never the totals. Every count change names the
   row, the old bucket, the new bucket, and the reason.
3. **No emission-time remapping.** Semantic plausibility never
   authorizes reclassification. A row that reads like "requires" but
   was proposed as "uses-input" stays where its evidence puts it; the
   fix goes to the source workbook, not the mapping.
4. **Figure discipline.** When a figure is wrong in one place, assume it
   is wrong in others: sweep the file, recompute every total, ground
   each CSV-derived number against the actual CSV, and report a
   discrepancy instead of fudging it. Blank `match_type` is deliberate —
   never invent a default.
5. **Two-agent review.** The decision owner reviews section by section ("one at a
   time to make sure I get it"). Cursor EPM pre-reviews every section
   against the repo; an independent verification re-checks every figure
   against the actual artifacts. Nothing merges on assumption.

**What we did.** Mapped 1,318 mentions to 457 canonical facts:
617 emitting / 686 held / 12 deferred / 1 external governance /
2 structured flow (conservation: 617+686+12+1+2 = 1,318). Per-predicate:
uses-input 101, informed-by 44, informs 1, requires 5, precedes 137,
follows 157, governed-by 18, constrained-by 10, triggers 7, assures 5,
enabledBy 84. The G1a duplicate-evidence merge (36 attached, 35
emitting), G1b workbook-correction holds (29), G2 no-separate-fact
(13), and the G3 genuine-enablement review (84 approved, 96 held) each
got row-level verdicts. `contradictions.csv` is header-only — zero
reciprocal pairs across all predicates. Review instruments, per-verb
batches, and the supersession register live under
`business_architecture/ontology/step4/review-evidence/`; the mapping
document (`verb-predicate-mapping-v2.md`) received two figure corrections
against the artifacts (PRs #178, #181); the mapping-document sign-off
itself (release-checklist.md L51) was completed 2026-09-29 (16/16 sections, the decision owner).

**Status.** Ten of ten checklist items green 2026-09-30: every row
verdict-recorded, ledger reconciled, methodology approved (PR #159),
evidence gate 433 PASS, evidence pinned, regression tests 17/17,
blast-radius proof CLEAN, fresh no-consumer attestation ("no downstream
consumer is consuming the ontology yet… the very first build out"),
mapping-document sign-off (16/16 sections, the decision owner), explicit promotion
approval (the decision owner: "I approved the promotion" (2026-09-30 03:26 UTC, recorded on PR #190)). Step 4 PROMOTED.
Mapping-document sign-off was completed 2026-09-29. The provisional `intake:`
namespace stays until a future step promotes intake annotations to real
properties and retires those predicates.

**Standing principles established.**
- A verb is a claim; a predicate is a verdict. Never promote on
  structural closeness or semantic plausibility alone.
- Held is a first-class outcome with a recorded reason — not a failure.
- The reviewer merges; the agents verify. Router ≠ merge.

---

## 4. Decision log

Locked decisions. Newest first within each group. Nothing here changes
without a dated amendment and the decision owner's explicit agreement.

### Phase E is closed (2026-10-22)
- Under the delegation (EPM-DEC-001-0083), Steps 5, 6, 7, 9, 10, 11
  and 12 are marked done, each with its listed exceptions. 462 held rows
  stay held with their reasons. The open items are listed, each with
  who it waits on, in the record and in the ontology README's Status
  section.

### The projection covers every release (2026-10-22)
- Under the delegation (EPM-DEC-001-0036, amendment of 2026-10-22), the
  Step 12 pipeline projects every released package at its newest
  version, with each package's own shapes, and passes. 16 rule gaps in
  value-stream, kpi, party and integration are listed, each to close at
  that module's next release.

### One catalog of every release (2026-10-22)
- Under the delegation (EPM-DEC-001-0082), `releases/catalog.ttl` lists
  all 19 releases, built from the packages' own catalog records and
  checked in `check.sh`. The Step 10 row lists every release.

### Step 9 is done (2026-10-22)
- Under the delegation (EPM-DEC-001-0081), a test runs every release
  package's own shapes over the package and the released packages it
  requires; all 19 conform. Step 9 is done; the run shapes stay with
  consumers by design.

### `ref-mpc` 1.2.0 (2026-10-22)
- With the decision owner's own approval (EPM-DEC-001-0080), `ref-mpc`
  1.2.0 is released, a minor: MPC and MPLX as parties join the reference
  module, 180 triples, requiring organization 2.0.0 and party 1.0.0.

### `kpi` 1.1.0 (2026-10-22)
- With the decision owner's approval of the release plan (EPM-DEC-001-0079),
  `kpi` 1.1.0 is released, a minor requiring core 2.2.0: the eight measure
  populations join the package with their `pop:` IRIs, and the measure
  shape is closed, so no value hangs off a measure. The released
  value-stream, market-data and integration packages stay on 1.0.1.

### `integration` 1.0.0 (2026-10-22)
- With the decision owner's approval of the release plan (EPM-DEC-001-0078),
  `integration` 1.0.0 is released: the placement, authority and consumer
  vocabularies, 280 triples, each in its own namespace. Under the
  delegation, the population statements ship in `kpi` 1.1.0, and the APQC
  element list stays a reference file, since a package would drop the
  licence notice that must travel with every copy.

### The Step 7 modules' first releases (2026-10-22)
- With the decision owner's approval of the release plan (EPM-DEC-001-0077),
  `data-product`, `value-stream`, `system`, `lane` and `market-data` are
  released as 1.0.0. Each requires `core` 2.2.0 or `kpi` 1.0.1 and the
  modules whose IRIs it uses; the 33 parked data products ship as parked
  items.

### Everything that reads core moves to 2.2.0 (2026-10-22)
- Following the release (EPM-DEC-001-0076, item 8): the regression, the
  Step 9 gate, the projection and the builds of the apqc, data-product,
  value-stream, system and lane modules read `core` 2.2.0. The released
  `kpi` and `party` builds stay on 2.1.0 until their next release. The
  data-product module emits Loss Control's link to CM 1.1.3.7.13
  (EPM-DEC-001-0048), and Q7 is answerable: 43 answerable, 0 partial,
  1 waiting (Q17). The projection reran on 2.2.0 and passed.

### `core` 2.2.0 (2026-10-22)
- With the decision owner's approval of the release plan (EPM-DEC-001-0076),
  `core` 2.2.0 is released, a minor built from 2.1.0 and the process map at
  8259354: 23 new concepts, IDs on four stubs, eight changed descriptions as
  scope notes; 19,810 triples, 706 process concepts. The APQC 19948
  references are checked (14 confirmed, 2 corrected to Rejected) and RF 1.2
  is no longer a Candidate node.

### The reference parties move into ref-mpc (2026-10-22)
- At the decision owner's word (EPM-DEC-001-0075), MPC and MPLX as parties
  move from `party/` to `ref-mpc/reference-parties.ttl`. Under the
  delegation, their roles and agreement take ref-mpc's namespace, and no
  `party` release is needed. The `ref-mpc` 1.2.0 release that will carry
  the move is pending, in its own pull request. *2026-10-22:* released
  (EPM-DEC-001-0080).

### The decision owner's answers on the codes and TABS Seller ID (2026-10-22)
- HOLDORDIND, Taboot, MPA_Flag, CR_Incentive_Flag and the reading of TID Nbr
  stay as they are until the ontology is shared for consumption, when the
  business confirms what each means; the decision owner confirmed the
  reading of TABS Seller ID (EPM-DEC-001-0072, amendment of 2026-10-22).
  No module file changes.

### The `party` module's first release (2026-10-22)
- With the decision owner's approval (EPM-DEC-001-0074), `party` 1.0.0 is
  released: the vocabulary, code lists, systems and lifecycle, 3,405
  triples, requiring core 2.1.0. The reference parties MPC and MPLX stay
  outside the package, as reference instances of real companies.

### The playbook's Customer domain lessons (2026-10-21)
- At the decision owner's request (EPM-DEC-001-0073), the playbook takes the
  method lessons of the Customer domain's reviews: in Steps 5, 9 and 11, in
  §2 and §5.6, and a §7 paragraph naming the findings behind them.

### Competency questions 19 to 26 (2026-10-21)
- Under the delegation (EPM-DEC-001-0071): the `party` module answers
  questions 19 to 26, each with a query. A customer-grained measure binds
  to the customer account by default; core 2.1.0's wording (the scope
  notes of CM 1.3.7.4.2 and CM 1.3.7.4.3, the definition of CM 1.3.7.2.5)
  rules out the collapsed customer, and the default is Claude's choice.
  For section VII's done-when the decision owner chose MPC and MPLX as the
  real organisations: their public roles toward each other, from MPLX's
  FY2025 Form 10-K, are described both ways. The regression stands at 42 answerable, 1 partial (Q7) and
  1 waiting (Q17).

### The decision owner's answers on the customer systems (2026-10-21)
- The decision owner gave four answers on three of EPM-DEC-001-0069's five
  open points (EPM-DEC-001-0072): input 6's CBS is assumed to be FuelFacs; the Terminal
  Margin Ranking System is the process map's TMR, a fourth customer system
  matched to the system module; TDS Seller ID is the seller's ID; and
  HOLDORDIND, Taboot, MPA_Flag and CR_Incentive_Flag stay undefined until
  they define them.

### The customer lifecycle (2026-10-21)
- Under the delegation (EPM-DEC-001-0070): the six business stages of the
  customer lifecycle link to the core processes that do their work, and
  the five system stages to the systems that hold the record. Three gaps
  go to the decision owner as proposal MPC-P10: onboarding coordination
  for every customer, the Order to Cash credit review's missing link, and
  a customer master data product.

### The customer systems and attributes (2026-10-21)
- Under the delegation (EPM-DEC-001-0069): the customer's 42 systems are
  the module's own class, three matched to the system module (*2026-10-21:*
  four, EPM-DEC-001-0072); the six
  core systems carry the entities they implement; 35 data flows and 24
  customer sourcings record the data flow and the origin patterns; and
  275 system attributes, 43 Create and 232 Enrich, each describe an
  entity of the model or, for fields about a system's own record, the
  system record; 48 of them carry one of nine shared attributes, such as
  the SAP customer number.

### The `party` module (2026-10-21)
- Under the delegation (EPM-DEC-001-0068): the decision owner's conceptual
  model becomes the `party` module, with fifteen entity classes, party roles as
  dated nodes (14 role types), Ship-To as a site, dated class assignments,
  and 14 customer classes in four groups carrying MPC's C1 to C8, which
  gives MPC-P06's channel dimension its values. The lubricants and marine evidence
  is parked until the product line has values.

### Customer domain resumes (2026-10-21)
- The decision owner shared their customer information in seven inputs.
  By their decisions (EPM-DEC-001-0067): the inputs stay out of the
  repository; derived definitions go in, from repository and MPC public
  information, and peer data does not go in, for the Customer domain;
  nothing in their conceptual model is out of scope; two roles are to be
  added;
  the repository stays private (later: public until the goal is
  achieved); the plan goes ahead.
- Claude's follow-through, under the delegation (EPM-DEC-001-0067, What
  follows): four customer classes from the repository's MPC customer
  classification, making 14 with the
  ten Claude read in the decision owner's model, and the Position Holder
  and Loading-Authorized Party roles are to be added in the `party`
  module's pull request; four more pull requests follow, five in all.

### Crack spread's primary source (2026-10-20)
- The decision owner set MPC Economics' 3-2-1 Crack Spread KPI Definition
  as the primary source, then MPC's public filings, peers and other
  references (EPM-DEC-001-0066). The market-data module takes its six
  regional ex-RIN series, the NYMEX 3-2-1 and two MPC-weighted blends,
  13 series in all. An ex-RIN series deducts the RVO cost; MPC's 10-K
  cracks do not, which corrects 0057 item 3.

### Step 9 gate on the whole graph (2026-10-19)
- Under the delegation (EPM-DEC-001-0065): every module's shapes now run
  together on the whole graph, with zero violations. The first run found
  two defects, both fixed at their source: the lane shape targeted every
  concept in any scheme, and the consumer rules gave `dcterms:source` a
  text value.

### External mappings (2026-10-19)
- Under the delegation (EPM-DEC-001-0064): PIDX's terms are checked
  (royalty free, for use without modification); PIDX and OEO wait for
  product concepts, from the Customer module's product-line facet or
  another product dimension (*2026-10-21:* that facet is in the `party`
  module, EPM-DEC-001-0067, and its values are not yet defined); IOF Supply Chain is parked until a concept
  layer for logistics assets or movements, or a consumer that needs IOF
  terms. GLEIF and DCAT are mapped.

### R2 backlog decided (2026-10-19)
- Under the delegation (EPM-DEC-001-0063): the operating-execution layer
  and the R2 vocabulary package are out until the map gains an
  operating-execution L2; turnaround ownership is answered for the map's
  scope by RF 1.2 (P02b), with maintenance execution outside the map;
  Energy & Utility Management stays where it is until its trigger occurs.

### Measure populations (2026-10-19)
- Under the delegation (EPM-DEC-001-0062): what eight MPC-defined
  measures include and exclude, from MPC's own wording, on the kpi
  module's measure IRIs. The other 33 measures' populations are parked:
  no source states them. A seventh may-answer rule joins the consumer
  rules: what a measure includes and excludes. Q28 is answerable. Every question still
  waiting now waits on the decision owner (Q17, Q19 to Q26). *2026-10-21:* Q19 to
  Q26 now wait on the plan's pull request 5, which answers them after the `party` module and its data (pull requests 2 to 4; EPM-DEC-001-0067, item 13); only Q17 waits
  on the decision owner. The plan's pull request 5
  then answered them (EPM-DEC-001-0071).

### Consumer rules (2026-10-19)
- Under the delegation (EPM-DEC-001-0061): the catalog binding
  (`con:publishesMeasure`, both ends defined first), six things an agent
  may answer from the graph and five it must refuse, each naming the terms
  it relies on. Q35, Q41 and Q42 are answerable. No binding is recorded,
  because no source says which data product publishes which measure.

### APQC element list (2026-10-19)
- Under the delegation (EPM-DEC-001-0060): the full APQC Downstream
  Petroleum PCF 7.2.2 element list (2,012 elements) is in the graph as a
  reference, so Q11 lists the 1,761 elements with no local counterpart.
  Q40 and Q43 are answerable by their graph part (EPM-DEC-001-0019). In
  core 2.1.0, 16 concepts reference element 19948, among them CM 1.2.4.1.10
  and CM 1.2.4.1.18, whose notes say no APQC candidate; the next core
  release checks them. *2026-10-22:* checked in core 2.2.0: 14 confirmed,
  2 corrected to Rejected (EPM-DEC-001-0076).

### Source authority (2026-10-19)
- Under the delegation (EPM-DEC-001-0059): every one of the 63 cited
  sources (64 since 2026-10-20, EPM-DEC-001-0066; 65 since 2026-10-21, EPM-DEC-001-0071) has an evidence tier, from the order in AGENTS.md (process
  authority, MPC, peers, industry and regulators, generic frameworks).
  Where two sources of a concept disagree, the best tier wins. Q44 is
  answerable.

### Placement kinds (2026-10-19)
- Under the delegation (EPM-DEC-001-0058): each property that places a
  measure, data product, system or lane on a process now says what it
  claims. Only producing a data product certifies (the owning process);
  every other placement, every measure's included, is context. Q37, Q38
  and Q39 are answerable.

### Benchmark series (2026-10-19)
- Under the delegation (EPM-DEC-001-0057): a new `market-data` module
  defines five series of the crack-spreads measure: MPC's Gulf Coast,
  Mid-Continent, West Coast and blended 3-2-1 (MPC FY2025 10-K, Item 7)
  and the NYMEX 3:2:1 (CME Group, "Trading Crack Spreads", 2024;
  "Introduction to Crack Spreads", 2017; "Fresh from the Trading Room",
  2026-07-14). The planner's "USGC 3-2-1 MEH ex-RIN"
  and "Chicago WTI 3-2-1 ex-RIN" resolve to MPC's Gulf Coast and
  Mid-Continent series. Recipes, not prices. Q31 and Q34 are answerable.
  *2026-10-20:* the decision owner made MPC Economics' definition the
  primary source; those two names are its ex-RIN series 43870 and 37438,
  which deduct the RVO cost (EPM-DEC-001-0066).

### Q15, the same-word test (2026-10-19)
- Under the delegation (EPM-DEC-001-0028), Q15 is answerable: when one
  word names more than one IRI, the graph says whether they are one thing
  (a retired IRI's `dcterms:isReplacedBy`) or how they relate (a link such
  as `vs:realizes`); with neither, they are different things. 61 words name
  more than one IRI across the modules.
  *2026-10-21:* `skos:exactMatch` is a link of the first kind too: the
  `party` module's RightAngle, KittyHawk and Profisee are the system
  module's nodes of the same name, and q15b reports them (EPM-DEC-001-0069).
  *2026-10-21:* a fourth pair, the Terminal Margin Ranking System and the
  system module's TMR; q15b now compares alternative labels on both sides
  (EPM-DEC-001-0072).

### Lane module (2026-10-19)
- Under the delegation (EPM-DEC-001-0056): a new `lane` module holds the
  four office lanes from `office_lanes.json`, linked to the map's
  `officeLane` values by their keys, and places the seven CM 1.2 processes
  that name a lane. Nothing is inherited by their children. Front, middle
  and back office have one process each, operations four. Q9 is
  answerable. This closes the worklog's data gap that `office_lanes.json`
  was not linked by ID.

### System module (2026-10-19)
- Under the delegation (EPM-DEC-001-0055): a new `system` module turns
  the process map's 37 system strings into 32 systems through a register,
  merged on spelling only and split on "/". Manual, TBD and two plans name
  no system. Each system has a kind (application, office tool, working
  document) and no definition, because no source defines one. 285 links to
  150 processes. Q6 is answerable.

### Value-stream module (2026-10-19)
- Under the delegation (EPM-DEC-001-0054): a new `value-stream` module
  holds the two value streams, 12 stages, 21 capabilities and 58
  value-stream processes. 57 of the 58 realize process-map processes by
  IRI, without duplicating them; 20 produce or consume data products. The seven MPC-P09 measure links are
  qualified links with their basis, context only. The files' domain
  "Commercial" stays as written, because `core`'s Commercial code does
  not cover Order to Cash. Q10 is answerable; Q7 stays partial until `core` 2.2.0 holds Loss Control's producer. *2026-10-22:* it does, and Q7 is answerable (EPM-DEC-001-0076).

### Data-product module (2026-10-19)
- Step 7 item 3 (EPM-DEC-001-0017), under the delegation (EPM-DEC-001-0053):
  a new `data-product` module holds the portfolio's 3 segments, 19 lines
  and 48 data products as definitions. The 15 Commercial data products are
  defined from the portfolio's descriptions; the 33 Midstream and Corporate
  ones are parked, because the portfolio names them without a description.
  `dp:DataProduct` is mapped to `dcat:Dataset`, not imported. Loss Control
  ownership is settled: CM 1.1.3.7.13 produces it (EPM-DEC-001-0048); the
  link waits for `core` 2.2.0. Process links from the value streams come
  with Phase B. Q7 is partial. *2026-10-22:* `core` 2.2.0 adds CM 1.1.3.7.13,
  the link is emitted, and Q7 is answerable (EPM-DEC-001-0076).

### Order of the remaining work (2026-10-19)
- The decision owner chose Claude's recommended order for completing the
  ontology (EPM-DEC-001-0052): Phase A data products, Phase B the
  Commercial Lifecycle and Order to Cash value streams, Phase C the
  Customer domain (waits for their customer information; *2026-10-21:* it
  arrived, EPM-DEC-001-0067), Phase D a
  `core` release, Phase E the remaining steps, and Phase F the `ontology`
  skill rebuilt. Ambiguity is resolved by external search, MPC first and
  the downstream peers second.

### Repository visibility rule (2026-10-19)
- The decision owner set a standing rule: the repository may be public
  while work needs it, so ruleset 25440735 gates every pull request, and
  it goes back to private at the end of each session or goal. Recorded as
  an amendment to EPM-DEC-001-0050. Their words are saved in
  `answers-2026-10-19-completion-order.md` and
  `answers-2026-10-19-completion-goal.md`.
  *2026-10-21:* for the Customer work the repository stays private
  (EPM-DEC-001-0067, item 12); later that day the decision owner made it
  public until the goal is achieved (EPM-DEC-001-0067, decision 12).

### Process-authority integrity checks (2026-10-20)
- `business_process/test_business_process.py`, run by `check.sh`, now checks
  the process authority. The data product portfolio and both value streams
  validate against their schemas. Process-map node ids (696) and data
  product and line ids (67) are unique. These references resolve: a value stream's
  linkedProcessIds and gapAnalysis closestProcessIds to process-map nodes,
  its produces and consumes to data products or lines, its capabilityId to
  a capability and its flows to processes in the same file, and each
  process-map officeLane to a lane in `office_lanes.json`. Every reference
  resolved when the test was added. The value-stream
  schema test moved here from `kpi/test_measures.py`. The process map has no
  schema file, so its check is parse and id uniqueness.

### The decision owner named by role (2026-10-19)
- The repo names no person: every current file says "the decision owner".
  Git history, commit authors and tags are unchanged. Released packages
  are edited in place, with the same versions and dates, and pass
  `--verify`. Two kinds of IRI change, and only these: the kpi source
  `src:planner-measure-list-2026-10-18`, and the two scoped-sequence
  sources, now `urn:epm:issue:205:comment:…` URNs. The answers folder is
  `review-evidence/decision-owner-answers/`. `epm_facts.py names` in
  `scripts/check.sh` fails on any tracked file that names the person.
  EPM-DEC-001-0049, with their words in
  `review-evidence/decision-owner-answers/answers-2026-10-19-after-run.md`.

### MPC-P03 coverage check closed (2026-10-19)
- The decision owner chose to widen CM 1.2.5.1 for the quality of
  transferred intermediates (EPM-DEC-001-0051). CM 1.2.5.1 gets its first
  description, cited to MPC's FY2025 10-K, Item 1, and CM 1.1.7 points to
  it. No process is added.

### MPC-P09 applied (2026-10-19)
- Price Management and Performance Management & Backcasting are capabilities
  in `value_stream_commercial_lifecycle.json`, each realized by one process.
  Those processes now name five `kpi` measures, each with a relationship
  (informs, benchmarks or measures performance) and its MPC source. The
  schema gains a `measures` field. A test validates both value streams
  against the schema for the first time (both pass) and checks that every
  named measure is defined. A link does not make a measure a KPI.

### Package 1 and the measure categories approved (2026-10-19)
- The decision owner approved decision package 1 and the eight measure
  categories (EPM-DEC-001-0050). PRs #262, #266 and #269 stand as merged,
  with a dated note in EPM-DEC-001-0036 and 0038. GitHub refuses the approved
  ruleset on `main` while the repository is private (HTTP 403), so the
  decision owner had the repository made public temporarily, for the current
  goal; the ruleset is added after the record merges. *Later
  that day:* ruleset 25440735 was created and gated #300 and #301; once
  they merged the repository went private again, and GitHub no longer
  enforces the ruleset. MPC-P09 is unblocked and goes in its own pull
  request. *Amended 2026-10-19:* public while work needs it, private at
  the end of each session or goal. *2026-10-21:* kept private for the
  Customer work, then public until the goal is achieved (EPM-DEC-001-0067).

### Process-map gaps addressed (2026-10-19)
- The decision owner said to address the two gaps the MPC-P03 and MPC-P04 checks
  found from high-quality references, MPC's public information first.
  Under the delegation: CM 1.1.3.7.13 Reconcile Movement Losses and Gains
  (MPLX's imbalances policy) and CM 1.2.5.1.5 Manage Renewable Feedstock
  Traceability and Carbon-Intensity Evidence (MPC's supplier feedstock
  commitment; EPA, CARB and IRS record rules), each in its own pull
  request; the feedstock step lands after the loss and gain step.
  EPM-DEC-001-0048, with their
  words in `review-evidence/decision-owner-answers/answers-2026-10-19-morning.md`.

### MPC process-map proposals ruled (2026-10-18)
- The decision owner accepted MPC-P01, P03 to P09 and P02b, with conditions, and said
  to apply them to the process map itself (EPM-DEC-001-0047). Under the
  delegation, each map change is its own pull request, and none is applied
  by the record itself. With this record's pull request, `core` 2.0.0
  builds from the map at its pinned commit, so released packages do not
  move; new nodes reach the ontology in a later `core` release.

### kpi module (2026-10-18)
- The decision owner's planner measures and MPC's public measures are classified by kind
  (EPM-DEC-001-0042): most are operational metrics, two are KPIs (MPC's
  bonus measures) and six are KPI candidates. The `kpi` module defines the
  41 measures (EPM-DEC-001-0043). It is built and checked, and released:
  1.0.0, a major, was approved by the decision owner and cut on 2026-10-19. Coverage: 17 answerable, 6 partial,
  21 waiting.

### Role answers and organization 2.0.0 (2026-10-18)
- The decision owner answered the seven role questions and approved organization 2.0.0.
  Three roles are deprecated into their successors, never deleted; their
  three assignments keep their IRIs. Forecaster and PSM stay open, and Q17
  waits for a separate governance decision. ref-mpc 1.1.0 (2026-10-19,
  approved by the decision owner) requires organization 2.0.0; organization 2.0.0
  requires core 2.1.0. The projection on both loads 2,811 nodes and
  14,865 relationships. EPM-DEC-001-0045, with their
  words in `review-evidence/decision-owner-answers/answers-2026-10-18.md` and
  `answers-2026-10-18-night.md`.

### core 2.1.0: evidence on canonical facts (2026-10-18)
- The decision owner answered the Step 9 walkthrough "1a, 2a" and approved cutting the
  release. `core` 2.1.0 adds one `core:CanonicalFact` node per canonical
  fact (640), each with its subject, predicate, object and every
  supporting REL row (812), and keeps the direct triples. The eleven
  controlled-value shapes and the evidence-link shapes join the release
  shapes; a build check matches each node's rows to the mapping, which
  ships in the package. The header's licence IRI gives way to an
  all-rights-reserved statement. Projection and regression read 2.1.0.
  EPM-DEC-001-0044; their words in `review-evidence/decision-owner-answers/`.

### KPI measure classification (2026-10-18)
- Most measures on the decision owner's planner list are operational metrics. A KPI
  is a designation with a target and an owner, not a kind of measure.
  41 measures classified: 15 operational metrics (6 KPI candidates),
  7 market indicators, 6 plan-variance diagnostics, 6 trackers or
  reports, 2 alerts, 2 KPIs (MPC's bonus measures), 1 decision-support
  indicator, 2 parked capabilities. Delegated under EPM-DEC-001-0028;
  EPM-DEC-001-0042, table in `ontology/kpi/measure-classification.csv`.

### Market Data and Commercial Risk (2026-10-18)
- The decision owner accepted the domain split with explicit distinctions, gave both
  definitions, and named the Risk Group as owner (Market Data
  provisionally). Trading-counterparty credit is in Commercial Risk;
  volatilities are risk-model parameters, vendor-supplied volatility
  observations are Market Data. EPM-DEC-001-0046.

### Licence and KPI seed (2026-10-18)
- The decision owner decided the ontology stays proprietary, all rights reserved
  (EPM-DEC-001-0041). The GitHub repository is private since 2026-10-18. *2026-10-19:* public temporarily, for the current goal, and private again once PRs #298 to #301 merged (EPM-DEC-001-0050). *2026-10-19, amendment of EPM-DEC-001-0050:* public while work needs it, private at the end of each session or goal. *2026-10-21:* kept private for the Customer work, then public until the goal is achieved (EPM-DEC-001-0067).
- The `kpi` module is seeded from the decision owner's planner measure list, with
  personas as planning roles and no person's name; their files stay out
  of the repo (EPM-DEC-001-0040, amending EPM-DEC-001-0017). Their words
  are in `review-evidence/decision-owner-answers/answers-2026-10-18.md`.

### Namespace is a placeholder (2026-10-14)
- The decision owner decided not to host the namespace, because the domain may change,
  and to keep `https://w3id.org/lsc/ontology/` as a placeholder. Under the
  delegation, nothing is registered with w3id.org, and no release changes. Step 10's
  "catalog resolves" gate is parked until a domain is decided. The licence
  is still open (*2026-10-18:* decided, proprietary; see the group above,
  EPM-DEC-001-0041). EPM-DEC-001-0039, with their words in
  `review-evidence/decision-owner-answers/namespace-hosting.md`.

### LPG guideline v2.2 (2026-10-14)
- `lpg-projection/` is re-pinned to `8ce9ada`, guideline v2.2
  (enterprise-people-graph PR #3). v2.2 takes in what the projection's
  first full run found: SHORTEN naming, the in-graph shape subset, no OWL
  API declarations in `inferred.nt`, the round-trip value rules and the CI
  report check (EPM-DEC-001-0036). The pipeline already followed them.
  The playbook's decimal rule now matches the guideline's print test.
  EPM-DEC-001-0021.

### Playbook updated for Steps 5 to 12 (2026-10-13)
- The playbook's method gains what Steps 5 to 12 taught: the role
  register and RACI conservation (Step 5), confirmed source fields and the
  run-pattern shapes (Step 6), shape coverage tests (Step 9), one package
  shape per module (Step 10), early harness and population checks
  (Step 11), and the loader, reasoner and round-trip rules for the
  projection (Step 12). Appendix B adds the cut's `dcterms:modified` and
  approval pin, and building the next major from the released graph. §7
  replaces the Step 5 and Step 12 plans with how Steps 5 to 12 ran. The
  projection README gains the n10s and ROBOT download steps with
  checksums. EPM-DEC-001-0024 (the playbook changes when the method does).

### Projection and regression on core 2.0.0 (2026-10-13)
- The projection (`projection/pipeline.py`) and the regression (`regression/run.py`)
  now run on core 2.0.0. 2.0.0 gives `earlierProcess` and `laterProcess` a
  range, so the pipeline lists no release gap. The rerun loaded 2,166 nodes
  and 12,290 relationships, with no SHACL violation in the graph, an empty
  round-trip diff and equal determinism hashes. Q8 is answerable: 153
  processes carry planned inputs and outputs, and 504 live processes have
  neither (`q08a`, `q08b`). The decision owner decided those 504 are the source
  author's backlog: the ontology drafts no SIPOC for them
  (`review-evidence/decision-owner-answers/sipoc-scope.md`). Coverage: 9 answerable,
  5 partial, 30 waiting.
  EPM-DEC-001-0036 and EPM-DEC-001-0038.

### core 2.0.0 released (2026-10-13)
- The decision owner approved core 2.0.0 and stated that no one uses the ontology yet,
  so on that date the deprecation of `core:responsibleDomain` broke no
  consumer. The
  release is the 2.0.0-rc.1 candidate with the issued and modified dates
  set and the stage removed. The merge commit gets the tag `core-v2.0.0`.
  The projection and the regression moved to 2.0.0 in their own change
  ("Projection and regression on core 2.0.0" above).
  EPM-DEC-001-0038, with their words in
  `review-evidence/decision-owner-answers/core-2-0-0-release.md`.

### Step 7 groundwork: MPLX FY2025 10-K read for MPC-P01 (2026-10-13)
- EPM-DEC-001-0011 asks for the MPLX 10-K read before the ruling on
  MPC-P01 (the empty Midstream L1). `reference/mpc/mplx-fy2025-10k-fact-sheet.md`
  records it: MPLX's two segments, Crude Oil and Products Logistics and
  Natural Gas and NGL Services; MPC is 48 percent of MPLX's 2025 total revenues and other income,
  mostly in the first, under fee-based agreements with minimum volumes.
  It supports P01's recommended scope (the fuels logistics that serves
  Refining & Marketing). The ruling is the decision owner's.

### core 2.0.0 candidate: business domains and SIPOC (2026-10-13)
- The decision owner confirmed the process map's `sioc` field is SIPOC, and decided the
  `responsibleDomain` values are business domains: Commercial & Marketing
  splits into Marketing (CM 1.3) and Commercial (CM 1.1, CM 1.2), with
  CM 1.4 IT Services its own domain. `release/build_core_next.py` built
  core 2.0.0-rc.1 from the released 1.0.0: a business domain code list and
  `core:businessDomain` (205 Commercial, 251 Marketing), `responsibleDomain`
  deprecated, planned inputs and outputs (362 and 219 on 153 processes),
  and ranges for `earlierProcess` and `laterProcess`. A deprecation makes
  it a major, so it waited for the decision owner's approval (given the same day; see
  "core 2.0.0 released" above). EPM-DEC-001-0038.

### organization 1.0.0 and ref-mpc 1.0.0 released (2026-10-13)
- The decision owner approved both modules as 1.0.0. The releases are the 1.0.0-rc.1
  candidates with the issued date set and the stage removed; ref-mpc
  requires organization 1.0.0. The merge commit gets the tags
  `organization-v1.0.0` and `ref-mpc-v1.0.0`. EPM-DEC-001-0037, with their words in
  `review-evidence/decision-owner-answers/answers-2026-10-13-session2.md`.

### Step 5 RACI scope decided by the decision owner (2026-10-13)
- The decision owner chose the 153 processes with RACI in the source as this release's
  RACI scope; the other live concepts that Q4 lists are the source
  author's backlog. All 153 have RACI and an accountable role, so the
  Step 5 gate's RACI condition holds. Recorded in EPM-DEC-001-0032, with
  their words in `review-evidence/decision-owner-answers/raci-scope.md`.

### Step 10 module release candidates (2026-10-13)
- `release/build_module.py` packages the organization and ref-mpc modules
  in the shape of the core 1.0.0 package: Turtle, JSON-LD, shapes, a DCAT
  record, a changelog and a manifest with SHA-256s. Both were built as
  1.0.0-rc.1 with no issued date: a first release is a major, which is
  the decision owner's; they approved 1.0.0 the same day (entry above). The candidate
  ref-mpc required the organization candidate it shipped with. The
  design is EPM-DEC-001-0037, decided under EPM-DEC-001-0028; the w3id
  registration and the hosting waited for the decision owner (on 2026-10-14 they decided
  against hosting; registration is not pursued, under the delegation;
  EPM-DEC-001-0039).

### Step 12 projection pipeline (2026-10-13)
- `projection/pipeline.py` runs the guideline's five steps over core
  1.0.0, the organization module and ref-mpc. The last run loaded 2,154
  nodes and 11,778 relationships into Neo4j 2025.06.2 with n10s 2025.06.1:
  no SHACL violation in the graph, an empty round-trip diff, equal hashes
  for the sorted and shuffled loads. n10s names terms in SHORTEN mode; a
  subset of the shapes runs in the graph and the rest in Step 1; ELK adds
  no domain inferences. Core 1.0.0 gives `earlierProcess` and
  `laterProcess` no range (Rule 1); the pipeline lists both gaps for the
  next core release. The design is EPM-DEC-001-0036, decided under
  EPM-DEC-001-0028.

### Step 9 controlled values (2026-10-13)
- `validation/controlled-values.ttl` requires every code-list property of
  `core` to take its values from its own list (the 1.0.0 release shapes
  checked at most `sh:class skos:Concept`, except `sh:in` on the concept
  kind), and the same of the RACI level. `core`
  1.0.0 conforms. A test fails when a code-list property has no shape; it
  found `evidenceBasis` and `sequenceScope`. The evidence-link shape waits
  for the next `core` release, which must carry each fact's evidence in
  the graph (*2026-10-18:* done in `core` 2.1.0, EPM-DEC-001-0044). The design is EPM-DEC-001-0035, decided under
  EPM-DEC-001-0028.

### Step 6 definition-to-run pattern (2026-10-13)
- `provenance/run-shapes.ttl` defines how a consumer's run links to its
  definition: a `prov:Activity` whose single qualified association has
  `prov:hadPlan` pointing at a live core process concept (P-Plan's
  whole-plan link). No new terms. A shape fails any core concept typed as
  a `prov:Activity`; core 1.0.0 passes. Planned inputs and outputs waited
  for the decision owner to confirm what the process map's `sioc` field means; they
  confirmed it is SIPOC on 2026-10-13 (EPM-DEC-001-0038). The
  design is EPM-DEC-001-0034, decided under EPM-DEC-001-0028.

### Step 5 ref-mpc module (2026-10-13)
- `ref-mpc/` holds MPC and MPLX, MPC's control of MPLX (about 64 percent,
  as of 2025-12-31), MPC's three reportable segments and its 13 refineries,
  each citing MPC's FY2025 10-K with an as-of date. The filing names three
  segments: Refining & Marketing, Midstream and Renewable Diesel. Refinery
  capacity waits for Step 7's measure pattern.
  The design is EPM-DEC-001-0033, decided under EPM-DEC-001-0028.

### Step 5 RACI assignments (2026-10-13)
- `organization/build_assignments.py` emits one
  `orgm:ResponsibilityAssignment` per RACI entry in the process map and per
  role the entry names, keeping the entry's text. Nothing is inferred from
  the hierarchy. `raci-conservation.csv` reconciles entries in with
  assignments out. Competency questions 3 to 5 are answerable. Q4 lists
  the live, non-anchor concepts (processes, capabilities and concepts with
  no kind) with no RACI in the source; whether they need RACI was
  a scope question for the decision owner, recorded in EPM-DEC-001-0032, which is
  decided under EPM-DEC-001-0028 (the decision owner answered it the same day; see
  the RACI scope entry).

### Step 5 role register (2026-10-13)
- `organization/role-register.csv` maps each RACI role string in the
  process map to one or more of the roles in `organization/roles.csv`;
  `build_roles.py` checks it against the source and writes `roles.ttl`.
  Strings merge only on case, plural, punctuation or "&"; a qualifier stays
  with the entry; a compound string splits; a team becomes a role with a
  scope note. The design is EPM-DEC-001-0031, decided under
  EPM-DEC-001-0028. Its open questions for the decision owner (likely misspellings and
  the acronyms) are listed there. Run `build_roles.py` for the figures.

### Step 5 organization vocabulary (2026-10-13)
- `organization/` holds the module's vocabulary and shapes:
  `orgm:ResponsibilityAssignment` (one process, role and RACI level, with
  the source's role text and a source), the RACI level list and
  `orgm:ControlRelationship` (share, as-of date, source). The design is
  EPM-DEC-001-0030, decided under EPM-DEC-001-0028, whose scope
  amendment for Steps 5 to 12 merged in #252. The process map holds RACI on 153 processes, with 91 role
  strings to normalize in the next slice.

### Step 11 competency regression started (2026-10-13)
- `regression/` holds one SPARQL query per answerable part of the 44
  competency questions, a status for each question (`expected.csv`), and a
  runner that `check.sh` runs. On core 1.0.0: 5 answerable (Q1, Q2, Q12,
  Q16, Q18), 5 partial (Q11, Q39, Q40, Q43, Q44), 34 waiting for Steps 5, 6
  and 7 or for EPM-DEC-001-0004 (Customer). Each module PR moves its questions to
  answerable. The status assignments are delegated under EPM-DEC-001-0028,
  whose Steps 5 to 12 amendment merged in #252.

### core 1.0.0 released (EPM-DEC-001-0029, 2026-10-13)
- After the six Phase 1 sweep batches, `release/build_core.py` builds
  `releases/core/1.0.0/` from the pinned evidence: the taxonomy with every
  `intake:` field migrated (5,571 of 5,571), the 640 canonical facts as direct
  triples, the scoped sequences, eight code lists, IRIs for the 1,003 former
  blank nodes, the SHACL slice (conforms), JSON-LD, a DCAT record and a
  manifest. The design choices are in EPM-DEC-001-0029, drafted under the
  delegation in EPM-DEC-001-0028 (merged in #242).
- Released 2026-10-13. The decision owner approved the design, the ledger and the release,
  and attested: "Merge #242. I approve the release design in EPM-DEC-001-0029. No one uses the ontology yet. I approve the conservation ledger and the core 1.0.0 release."
  The builder dropped the `-rc.1` stage and set the issue date.
- Merged in #249 as d8b16e1 and tagged `core-v1.0.0`. The release lessons
  (a release candidate until the owner approves, tests that check the
  builder independently, a stated cardinality on every property) are in the
  playbook, Appendix B.

### Playbook method update (2026-10-13)
- Three practices are now in the playbook. Working a source-correction
  backlog as one approved answer register built in batches (Step 4), proved
  by the Phase 1 sweep. Building a release with a checked, deterministic
  builder (Appendix B, "Releasing a module"), from the core 1.0.0 build
  (released in #249). Delegated decisions,
  with what stays with the owner (Section 6), from the decision owner's delegation of
  2026-10-12. Project records: EPM-DEC-001-0025 and -0027 (merged); -0028
  (merged in #242).

### Phase 1 sweep register approved; #206 built (2026-10-12)
- The decision owner delegated drafting of all 245 remaining Phase 1 answers: Claude and
  Codex drafted from MPC and industry research briefs, each model reviewed
  the other's half, and the decision owner approved the register as a whole: "approve
  register, Q1 yes, Q2 yes, Q3 yes, flagged: yes to all." (#207 comment
  6133390674). The register and its evidence are in
  `review-evidence/phase1-sweep/`, not in the ontology.
- Corrections go into the workbook in place (`relation-correct.py`), so REL
  IDs stay stable. EPM-DEC-001-0027 adds two mirror raw verbs for the 101
  rows stored opposite to their workbook direction (#238).
- #206 is the first batch: 10 governed-by rows emit, REL-00190 names its
  DOA child, 4 rows close with no relationship. Merged in #239.
- #203 is the second batch: 10 S&T advisory rows emit `informedBy`, 2 emit
  `dependsOnOutputOf` through `provides-input-to`, REL-01122 names
  Production Scheduling, and 3 rows close with no relationship. Merged in
  #241.
- #210 is the third batch: 6 rows emit `informedBy`, REL-01053 `dependsOnOutputOf`, REL-01312 `governedBy` through `governs`, and 14 rows close with no relationship. Merged in #243.
- #202 is the fourth batch: 41 G1b and informed-by rows emit (24 new facts, 5 existing facts gain a contributor) after their verbs were corrected in the source, and 3 rows close with no relationship. Merged in #244.
- #209 is the fifth batch: 41 G3 Section A rows emit (40 new facts, 1 existing fact gains a contributor; 33 through `provides-input-to` or `governs`, 6 as `informs`, 2 as `triggers`) and 6 close with no relationship. Merged in #247.
- #201 is the sixth and last batch: 84 G3 Section B rows emit (78 new facts, 6 existing facts gain a contributor; 49 through `provides-input-to`, `governs` or `constrains`; 9 confirm `enables`, REL-00243 through the row-level override) and 18 close with no relationship. Merged in #248.

### Mirror raw verbs (EPM-DEC-001-0027, 2026-10-12)
- The decision owner: "yes, add both verbs and record the decision." `provides-input-to`
  (S, T) is stored as T core:dependsOnOutputOf S and `governs` (S, T) as T
  core:governedBy S, so a Phase 1 correction that reverses a row's direction
  rewrites the segment in place and keeps its REL ID. Each follows the rules
  of the verb it mirrors. Record:
  `business_architecture/domain/decisions/EPM-DEC-001-0027-mirror-raw-verbs.md`.

### #204 triggers batch 1 (2026-10-12)
- The decision owner answered all 11 held `triggers` rows on #204 (comment 6130380041):
  seven conditional triggers, four unconditional. They agreed that "a
  conditional trigger fits the locked core:triggeredBy definition where the
  condition identifies a specific event, finding, or authorized handoff that
  invokes the target", and that "No new relation or design round is needed
  merely because a trigger has a condition." Merged in #235 (c892ac9): the
  sentences went into ten source scope notes and all 11 rows emit (628
  emitting / 658 held / 468 facts at that merge); #204 closed with it.

### Scoped sequence relation built (2026-10-12)
- EPM-DEC-001-0026: The decision owner approved the #226 design (comment 6123946413:
  "Approved: Q1–Q18 as recommended in the comment above"). A scoped sequence
  is a qualified-relation node in `core` (`core:ScopedSequence`) from an
  earlier to a later process, with a scope unit from a 10-value list, an
  optional condition, an evidence basis and the approved scope-note sentence
  as its definition. The 17 scoped #205 rows emit 17 nodes (16 handoffs);
  the ledger gives them their own bucket. `core` 1.0.0 also needs the
  relation's SHACL shapes to pass. Amends 0013 and 0025. Built in
  `step4/scoped-sequence/`.

### Scoped sequence relation before core 1.0.0 (2026-10-12)
- #205 batch 1 answers describe sequences per trade, delivery, settlement
  period, claim or posting, "not completion of an entire organizational
  process", so `core:precedes` (process-level finish-to-start) cannot carry
  them and all 13 rows closed as not emitted. The decision owner on PR #225 (comment
  6115615577): "Option 1: close all 13 batch 1 rows as not emitted. Keep
  core:precedes locked as a process-level finish-to-start. Define a scoped
  sequence relation for these answers before the core 1.0.0 release,
  tracked in its own issue under #207." Tracked in #226; its decision
  record will amend EPM-DEC-001-0013 and 0025.

### Phase 1 batch mechanics (2026-10-11)
- The five batch process choices proposed on #205 (2026-10-07) are read as
  agreed with the recommendation (a): one PR per batch with a merge commit,
  a re-pin in every batch that edits the workbook, one reusable tested
  workbook-edit script, (b) answers leave the workbook relationship in place,
  and row verdicts go in the batch review file and the backlog with no
  decision record per row. The decision owner did not comment on them, and their recorded
  rule is "If i dont comment on a question, it means I am aligned"
  (EPM-DEC-001-0001). They then authorized batch 1 on #205 (comment
  6115309253, 2026-10-11: "Take this as my authorization").
  The script is `build/scripts/scope-note-append.py`. First used for #205
  batch 1 (`step4/source-workbook-backlog.md`, "Batch 1 fresh verdicts").

### Phase 1 scope (2026-10-06)
- EPM-DEC-001-0025: Phase 1 is the source-correction backlog (eight issues,
  parent #207; 276 rows, 275 held). The 411 held mentions outside it stay held with
  their recorded reasons and wait for a later release. Amends 0013; the
  playbook's release gate now names the source-correction backlog.

### LPG guideline v2.1 (2026-10-06)
- The `lpg-projection/` snapshot is re-pinned to enterprise-people-graph
  `e7b09e8` (guideline v2.1). v2.1 makes qualified-relation nodes Rule 4
  option 4a, the default, which is what EPM-DEC-001-0020 chose. Notes added
  to 0020 and 0021; three older pipeline defects are tracked in
  enterprise-people-graph issue #2.

### Grilling session on the handover plan (2026-10-05)
The decision owner answered Q1 to Q34 and confirmed the full list. Each decision has a
record in `business_architecture/domain/decisions/` (index in its README):
- PPC is planned, not active; build as if no consumer (EPM-DEC-001-0001).
- Playbook maintenance rule decided (0002), then amended (0024): the
  playbook is a company-neutral method and project decisions live in
  EPM-DEC-001 (0024, decided 2026-10-06: "Playbook holds the method, yes.").
  The playbook was rewritten on this basis;
  the approved Step 4 evidence text moved word for word to
  `step4/evidence-discipline.md`.
- Phase 1 tracking and batches (0003); Customer work waits (0004).
- Data scope: concepts, definitions, relationships and cited public
  reference facts; no event records, no observed measure values (0005).
- Pricing D1 to D4 decided (0006 to 0009); Market Data and Commercial Risk
  defined at Step 7 (0010).
- MPC-P02 now, the rest at Step 7 (0011, 0012).
- `core` 1.0.0 after Phase 1 (0013); SHACL release slice and Step 9 order
  (0014).
- Step 5 reference instances in `ref-mpc`, MPLX modeling (0015); Step 6
  P-Plan (0016); Step 7 order and KPI seed (0017); Step 10 (0018); Step 11
  (0019).
- LPG projection guideline adopted as Step 12, Rules 1, 2, 3 and 5 from
  `core` 1.0.0, qualified-relation nodes instead of reifiers (0020);
  guideline snapshot in `lpg-projection/` (0021); ontology skill in
  personal-agent-skills (0022); public ontologies mapped, not imported
  (0023).

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
  *Amendment 2026-10-13:* The decision owner decided the values are business domains,
  not org units, and split Commercial & Marketing into Commercial and
  Marketing; core 2.0.0 links the concepts that carry these
  values (processes and capabilities) to a business domain list instead
  (EPM-DEC-001-0038).
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
- **Step 4 Q9: lifecycle model (2026-09-22; revised to three dimensions
  on review the same day).** Status is three independent dimensions —
  the original single chain (Candidate → Approved → Deprecated →
  Retired) conflated them and is withdrawn:
  - **Concept lifecycle** (`core:lifecycleStatus`, object property to a
    SKOS scheme): Active, Deprecated, Retired. No conflict with OWL:
    Deprecated ⇒ `owl:deprecated true` (required); Retired ⇒
    `owl:deprecated true` (retired implies deprecated); Active ⇒
    `owl:deprecated` absent or false — agreement enforced by SHACL in
    Step 9. "Superseded" is not a fourth state: it is Deprecated +
    `dcterms:isReplacedBy` pointing at the successor. Retired is
    terminal for active use; the concept remains resolvable for
    lineage, and restoration requires a new governance decision with
    recorded provenance — never a silent flip.
  - **Governance approval status** (`core:governanceStatus`, object
    property to a SKOS scheme): the project's existing artifact-control
    vocabulary, now formalized — Exploratory, Draft, Candidate,
    ApprovedBaseline, Implemented. A concept can be Active while its
    definition is still Draft (488 taxonomy concepts currently lack
    authored definitions); a proposal can be Candidate while its
    concepts are not yet Active.
  - **Hold status** (`core:holdStatus`, object property to a SKOS
    scheme): independent of the other two — NoHold, EvidenceHold,
    OwnershipHold, DecisionHold, ImplementationHold. A hold applies in
    any non-retired lifecycle state without disturbing it, with the
    reason in `core:holdReason` and the evidence linked via the
    decision-log reference convention. Live cases: CM-1-1-4-6-1 carries
    OwnershipHold (PTC-001-B strategy-ownership decision);
    CM-1-1-3-5-3 carries EvidenceHold (business-evidence hold).
  - Worked examples:
    - R1 reliability/turnaround L2: lifecycle Active, governance
      Implemented, hold NoHold (it was a Candidate *proposal*;
      Candidate was never the concept's lifecycle state).
    - CM-1-1-4-6 tombstone: lifecycle Retired, `owl:deprecated true`,
      governance Implemented, hold NoHold.
- **Step 4 Q10: terminology-note migration (2026-09-22).**
  Selective-alias policy — a prior name becomes `skos:altLabel` only if
  it is unique, non-misleading, non-colliding, and useful for retrieval
  (`altLabel` is a live search commitment, not an archive field).
  Generic, ambiguous, authority-overstating, case/punctuation-only, or
  scope-limited former names are preserved in migration history via
  `core:priorPreferredLabel` (annotation property) but are **not**
  searchable. Scoped aliases (e.g. valid only in APQC-comparison
  context) keep their context in the migration map and are never
  flattened into `skos:altLabel`. One-line rename rationale →
  `skos:editorialNote`; migration event and source →
  `dcterms:provenance`; full reviewer reasoning stays in the decision
  log / naming queue by reference. Conservation rule — extends the Q2
  ledger and gates the `intake:` cutover: every non-null `prior_name`
  gets exactly one recorded disposition; every non-empty
  `name_change_note` has a recorded disposition — a concise rationale
  plus migration provenance, consolidation into a canonical migration
  event, formatting-only migration history, or explicit
  supersession/duplication; every `scoped_historical_alias` has a
  context or is explicitly rejected. Minimal Step 4 vocabulary: only
  `core:priorPreferredLabel` is added; a reified historical-label
  record is deferred until a real need appears. A 92-row
  historical-label disposition report is the tracked pre-cutover
  instrument for this rule.
- **Step 4 Q11: relationship target dispositions (2026-09-22; item
  dispositions corrected the same day).** Governing rule: every
  relationship mention gets a governed disposition; only mentions
  classified as process-to-process become Step 4 object-property
  triples. Structured-flow values, external governance references,
  and parked future concepts are retained through their approved
  disposition mechanisms and may receive separately approved
  properties in future; they are excluded only from the initial
  process-dependency migration. Five disposition types:
  ResolvedToConcept, ParkedFutureConcept, StructuredFlowValue,
  ExternalGovernanceReference, DroppedAsNonProcessProse. Matching
  principle: **labels aren't identity** — parenthetical qualifiers
  (`(DOA)`, `(Advertising)`, `(Non-Retail)`, `(CVP)`, `(Retail)`) are
  part of the label that resolves the mention to its concept; the
  first-cut "unmatched" report was wrong on six of the nine because
  it matched bare phrases. Corrected dispositions, verified against
  the identity map and the committed TTL:
  - Establish & Maintain Delegation Of Authority →
    ResolvedToConcept `CM-1-2-2-3-2`
    ("Establish & Maintain Delegation Of Authority (DOA)").
  - Integrated Marketing Planning → ResolvedToConcept `CM-1-3-5-2`
    (all four mentions are the qualified
    "Integrated Marketing Planning (Advertising)").
  - Serve to Customer → ResolvedToConcept `CM-1-3-6-2-6` (the only
    mention is the qualified "Serve to Customer (Non-Retail)").
  - Develop/Update Strategy → ResolvedToConcept `CM-1-3-2-2-4`
    (the remaining mention is the CVP-context
    "Develop/Update Strategy (CVP)"); the no-global-lexical-
    replacement rule stands for any future bare mentions.
  - Manage Trading Books & Strategies Structure →
    ResolvedToConcept `CM-1-2-2-3-1`
    ("Establish And Maintain Book Structure", per the batch 12
    split).
  - Network Design → ResolvedToConcept `CM-1-3-3-4`
    ("Network Design (Retail)") for all qualified mentions; the
    single bare `informed-by: Network Design` mention (Brand
    Imaging row) is genuinely unmatched → ParkedFutureConcept,
    do not guess which network.
  - The Regional Backcasting assumption basis →
    StructuredFlowValue (unchanged; it is a `produces:` value,
    per Q5).
  - Monthly Operating Plan → StructuredFlowValue (unchanged; plan
    artifact, per the R1 plan-vs-artifact distinction).
  - Data Governance → ExternalGovernanceReference (unchanged;
    cross-cutting enterprise domain, never a `proc:` node under
    Commercial).
  DroppedAsNonProcessProse remains a valid disposition type with no
  current members. The repo-wide stale-target watch stays in place.
  New properties for governance references are deferred to
  implementation design. The row-level target-disposition report
  (subject, verb, phrase, disposition, rationale, emit-triple-or-not)
  is the tracked pre-cutover instrument.
- **Step 4 Q12: ambiguous relationship targets (2026-09-22).** A
  lexical match is not a semantic resolution: resolve a relationship
  target only where stable identifier evidence, or approved
  contextual evidence sufficient to identify exactly one governed
  target, exists; otherwise record `AmbiguousDeferred` with the raw
  phrase, candidate set, evidence considered, reason, and review
  trigger, and emit no process-dependency triple. Decision ladder, in
  order: stable identifier → approved contextual evidence sufficient
  to identify exactly one governed target → scoped historical alias
  (valid context established) → defer. A label match — even an exact,
  unique, qualified one — is a candidate filter, not a ladder step: it
  may narrow the candidate set inside the contextual-evidence step,
  but the resolution is recorded as the concept's slug. Labels are
  never joined on, per the standing 2026-09-21 identity lock. Phrases that are not process
  concepts fall back to the Q11 dispositions rather than forcing an
  ambiguous process match. `AmbiguousDeferred` is the sixth
  disposition type, extending Q11's five. Amendment to Q11: the single
  bare `informed-by: Network Design` mention (Brand Imaging row) moves
  from ParkedFutureConcept to AmbiguousDeferred — the network type is
  uncertain, not merely unmodeled — with retail/supply/distribution/
  terminal/channel candidates and review trigger at the R2
  network-design decomposition or the first consumer need. The
  row-level disposition report carries: source slug and label,
  branch/domain, raw verb, raw target text, disposition, candidate
  slugs/labels, resolution evidence, confidence
  (Resolved/Contextual/Deferred), emission decision, reason, review
  trigger, decision reference. Emission rules for the future promotion
  script: ResolvedToConcept emits the approved triple;
  StructuredFlowValue, ExternalGovernanceReference, ParkedFutureConcept,
  and AmbiguousDeferred are retained through their disposition
  mechanisms with no process triple; DroppedAsNonProcessProse retains
  only its disposition record.
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
- **License: proprietary, all rights reserved** (2026-09-18). The decision owner is
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
  versioning/validation; minor/patch by module owner, majors by the decision owner.
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
- **Worklog renamed (2026-09-30).** This file was renamed from
  `step4/playbook/ontology-playbook.md` to `step4/playbook/ontology-worklog.md`,
  so only the method keeps the playbook name. The entry below refers to it
  as "this working record". In the same change,
  `step4/playbook/manifest.json` was retired: it mapped this file onto the
  method's path, so a sync could have overwritten the method. The stale
  snapshot `step4/playbook/ontology-playbook.remote-main.md` was removed.
  Both remain in git history (added in PR #124).
- **Playbook maintenance rule (proposed 2026-09-30; decided 2026-10-05
  and amended 2026-10-06, see the note at the end of this entry).** Two playbook copies
  with two roles: the method (`business_architecture/ontology/ontology-playbook.md`,
  normative) and this working record. A decision change lands in the
  method's §2 Policies first; this log carries the dated entry pointing at
  it. The copies are never updated independently on the same decision.
  `business_architecture/ontology/README.md` is the single entry point.
  Proposed in the method at §2 "Playbook maintenance". *Superseded:*
  decided 2026-10-05 as EPM-DEC-001-0002 and amended 2026-10-06 by
  EPM-DEC-001-0024 (project decisions live in EPM-DEC-001).
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
  the decision owner's decision): the graph is a snapshot and may lag the workbook
  mid-pass; the final regen (PR #83, 14,403 triples, 675/680 defined)
  is the handoff into Step 3d.
- **Naming normalization is a Step 3d activity, not a Step 3c one**
  (2026-09-21). 92 queued renames live in `step3c-naming-pass-queue.md`;
  duplicate-prefLabel collisions gate semantic-model publication.
  Queued labels stay alt labels until the pass executes, then sweep the
  workbook, TTL, identity map, and cross-references.
- **Confirm the `sioc` JSON field's meaning** (SIPOC/SIOC?) before
  naming ontology terms; do not confuse it with the W3C SIOC vocabulary
  (2026-09-17). *Resolved 2026-10-13:* The decision owner confirmed it is SIPOC
  (EPM-DEC-001-0038).

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
**Decisions (2026-09-21, Step 3d Phase 1, the decision owner):** 8 critical-collision
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
**Decisions (2026-09-21, Step 3d Phase 1 follow-up, the decision owner):** the sixth
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
**Taxonomy unpublished (2026-09-21, the decision owner):** no external consumers, so
renames need no deprecation period or consumer notice.
**Decisions (2026-09-22, Step 3d naming pass Batch 7, the decision owner):** the 12
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
**Step 3d closure (2026-09-22, the decision owner):** Step 3d closed as "Completed with
explicit open exceptions" on the decision owner's approval of the closeout recommendation.
Naming normalization fully executed (92/92 queue entries); evidence-supported
tree remediation complete (PTC-001 partial resolution: tombstone + 2 reparented
L3s + 2 Candidate L2s).
**PTC-001-B confirmed as intentional governance hold (2026-09-22, the decision owner):**
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
**Refining Architecture Scoping Decision (2026-09-22, the decision owner):** approved in
principle with refinements; R1 is a controlled re-homing and normalization
pass, not a greenfield refinery model. R0 inventory complete (2026-09-22):
the Refining L1 holds only 3 concepts; the substantive refinery estate —
Refinery Planning (26 concepts) and Refinery Scheduling (16 concepts) —
sits under Commercial & Marketing → Planning & Scheduling. R1 therefore
promotes existing approved concepts with stable slugs/IRIs rather than
duplicating or recreating ~40 concepts.
**Structural framing (the decision owner's correction, 2026-09-22):** the change is a
**controlled structural reclassification and reparenting with stable
identity** — NOT label-only. Parent-child relationships, concept levels,
`skos:broader` links, hierarchy navigation, query paths, and
hierarchy-dependent consumption (reports, RLS/OLS, Power BI) all change;
only identity is stable. This framing makes the consumer-impact scan
mandatory.
Priority L2s: **Refinery Planning and Optimization** (promote `CM-1-1-4`,
approved in principle subject to the consolidated hierarchy map and the
Optimization-coverage evidence check); **Refinery Production Planning and
Scheduling** (narrower R1 label for the promoted `CM-1-1-7` estate — the decision owner's
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
**R&T L2 definition (owner-authored, 2026-09-22):** "The Refining capability
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
operating model. *2026-10-19:* the ownership question is answered for the
map's scope (EPM-DEC-001-0063); the next `core` release reviews the Candidate
status. *2026-10-22:* reviewed in `core` 2.2.0: no longer a Candidate node
(EPM-DEC-001-0076).
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
**R1 structural decision package (approved as Candidate, 2026-09-22, the decision owner):**
delivered as a no-change proposal and approved as **Candidate** on the decision owner's independent review:
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
**R1 implementation — merged (2026-09-22, the decision owner):** PR #108 merged as
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
the R&T L2 remains Candidate until the ownership question is answered. *2026-10-19:* the backlog is decided (EPM-DEC-001-0063): items 1 and 3 are out until the map gains an operating-execution L2; item 2 is answered for the map's scope by RF 1.2 (P02b), and the next `core` release reviews its Candidate status (*2026-10-22:* done in `core` 2.2.0, EPM-DEC-001-0076); item 4 waits for its trigger.

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
  the repo JSON's `sioc` field is SIPOC (the decision owner, 2026-10-13;
  EPM-DEC-001-0038) and must not be confused with it.
- **ODPS family** (Open Data Product Specification / ODPC / ODPV / ODPG):
  mapped for awareness (ODPC→DCAT, ODPV→SKOS, ODPG→RDF) but not adopted —
  the W3C stack covers our needs without adding a second modeling
  idiom. Revisit if the data-product catalog work demands it.

---

## 6. Repo-specific notes for the team

Facts about the source material that are easy to get wrong:

- **Scale:** ~680 nodes, levels L0–L6 (L0: 2, L1: 10, L2: 4, L3: 24,
  L4: 117, L5: 502, L6: 21). 669 nodes have IDs at the Step 2 run (later additions are dated in `build/output/step2-identity-report.md`); **11 roots/stubs do
  not** (Downstream Operations, Refining, Midstream, Enabling Functions,
  Supply Chain Mgmt., Finance, Shared Services, Process Excellence & IT,
  Human Resources, Legal & Corp Comm, EHS & Gov Reporting). Step 2 mints
  IDs for all 11.
- **Codes like `CM 1.2.1.3` are `skos:notation`**, not APQC identifiers
  and not globally unique outside this map.
- **`officeLane` values:** `front_office`, `middle_office`,
  `back_office`, `operations`. Not declared disjoint.
- **The `sioc` JSON field is SIPOC** (suppliers, inputs, outputs,
  customers; the process is the node). The decision owner confirmed it on 2026-10-13
  (EPM-DEC-001-0038).
- **Known data gaps to resolve in Step 7:** all 46 Order-to-Cash
  processes have empty `produces` arrays; no AR credit/receivables/
  collections portfolio exists (do not reuse `dp-commercial-risk`);
  `office_lanes.json` is not linked by ID (*2026-10-19:* linked by its keys in
  the `lane` module, EPM-DEC-001-0056); Loss Control was a
  data-product concern with no owning process (*2026-10-19:* produced by
  CM 1.1.3.7.13, EPM-DEC-001-0048).
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
   locked, follow it; if you believe it's wrong, raise it with the decision owner
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
   the decision owner or a designated reviewer fills the 6-sheet semantic-intake
   workbook `step3c-definition-authoring-workbook.xlsx` and returns it
   to the decision owner or commits it to a reviewer branch — never `main` directly.
   The assistant pulls it, runs `step3c-workbook-validate.py`
   (mechanical gate), then performs a full semantic review. Every doubt
   comes back to the decision owner as a question. Only `approved` rows whose
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
10. **Provenance-clean** — `dcterms:source` records human authorship, the decision owner's approval, and date.

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
    dcterms:creator "The decision owner" ;
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
   per APQC scope decision 2. Approved: The decision owner, 2026-09-18.`
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
The decision owner. No exceptions — majors change the meaning of published truth.
