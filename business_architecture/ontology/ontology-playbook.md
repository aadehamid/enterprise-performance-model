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
| 3 | SKOS taxonomy (one ConceptScheme, broader/narrower, labels, definitions, notation) | Planned |
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
  `aadehamid <aadehamid@gmail.com>`.

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
  went Marathon → LSC). Only the company abbreviation appears, and even
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
  all build scripts/outputs under `business_architecture/ontology/`.

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

### Validation and process
- **Core SHACL where sufficient; SHACL-SPARQL only when Core cannot
  express a constraint** (2026-09-17).
- **Record APQC v7.2.2 with `dcterms:references`**; preserve source,
  version, license, and provenance (2026-09-17).
- **Decisions accumulate in the log; the repo JSON gets one
  consolidated proposal** after the modeling pass — never churn the
  source of truth per decision (2026-09-17).
- **Every new process gets an L0–L6 level** slotted from the existing
  hierarchy — no level-less nodes (2026-09-17).
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
