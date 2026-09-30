# Ontology Playbook

**Status:** Living playbook. Prescriptive guidelines for building an ontology
end-to-end; the worked example is the downstream process-map ontology.
**Owner:** Hamid · **Built with:** Kailey
**Started:** 2026-09-17

## About this document

This is a **playbook, not a project journal**. It tells any team how to build
a good ontology from scratch, step by step. The guidance is distilled from a
real build — the downstream process-map ontology (the "worked example") — and
that build is the proof the guidance works, not the subject of the document.

**How to read it.** §0–§6 are the method: foundations, the end-to-end
sequence, the locked policies, the Step 4 evidence discipline, the
standards guide, soundness, and the working agreements. Follow them in order. §7 is
the worked example — the
instantiation of the playbook on a real build. It stays in this document
by design: the example is how a reader checks that the guidance is real.
Read it when a prescription needs a concrete illustration, not as the main
text.

**How to maintain it.** When the method improves, update the guidance
section a teammate would look in, dated, with the reason — never in chat
history. When a build step completes, extend the worked example (§7) and
move any new durable decision into §2 (Policies). Never rewrite history:
correct with a dated amendment so the team can see what changed and why.

**Companion files:**
- `step4/playbook/ontology-playbook.md` — the **working record** of the
  build: plan table with current statuses, per-step log, and the dated
  decision journal. This file (the method) decides; the working record
  narrates (see §2, Playbook maintenance).
- `competency-questions.md` — the merged competency-question baseline (the
  acceptance test for the whole build)
- `apqc-scope-decisions.md` — the per-candidate
  APQC scope review record
- `build/` — reproducible build scripts (`step2-identity-map.py`,
  `apqc_crosscheck.py`) and their generated outputs under `build/output/`

---

## 0. Foundations — the discipline everything else rests on

*Distilled from Juha Korpela, "Building Semantics with Conceptual Models"*
*(Common Sense Data, 2026). These are the load-bearing ideas: get them right
and the rest of the playbook is execution; get them wrong and no amount of
tooling will save the result.*

### 0.1 Context is the product

In the agentic era, context is king. It used to be that Bob from Accounting
could walk over and ask Juliet from Procurement what a field meant — human
communication networks papered over our failure to capture data context.
Agents cannot do that. Every consumer of your data, human or machine, needs
to understand what it is consuming. The ontology is how you make that
understanding durable, shared, and machine-readable.

**Guideline:** build the foundation *before* anything consumes it, so that
everything built later connects to something trustworthy. A foundation with
no consumers yet is not unfinished — it is the whole point.

### 0.2 Model the business, not the storage

Conceptual modeling is semantic work, not solution design. When you model
for actual business concepts and the semantic structure of data, you do not
care about databases, data lakes, warehouses, pipelines, or ETL. The same
model can inform solution design later, but it does not have to — its job is
to capture what the business *means*.

**Guideline:** never let a physical storage concern shape a concept. If a
distinction exists only because of a table, a feed, or a system boundary, it
does not belong in the conceptual model.

### 0.3 The two primitives

In the end there are only two things of importance in a conceptual model:

1. **Entities** — things that exist in real life, that you have data about.
2. **Relationships** — associations between two entities; assertions that
   they have something to do with each other.

That is the structure of reality the model captures. Attributes can come
later; do not start there. People get stuck in attributes and lose the
structure.

### 0.4 Entities are singular nouns

Name each entity as a singular noun: "Customer", not "Customers", and never
"Customer Data". The test is a sentence test — each entity must be a noun in
a sentence that describes how the business works, able to play the role of
subject or object. Those nouns will soon need to play exactly those roles in
your triples.

**Guideline:** if you cannot write a plain business sentence with the entity
as subject or object, the entity is not well-formed. Rename it until you can.

### 0.5 Every entity gets a definition. No exceptions.

A good definition answers the question "what do you mean by
<entityname>". Write it in simple business language. This is the basis of
your glossary: **terms + definitions = semantics.** Capture definitions in
whatever tool you have — an integrated glossary feature, a spreadsheet if
necessary — but capture them, for every entity, with no deviations.

### 0.6 Relationships are verbs

Every relationship — every line between two boxes — must be named with a
verb that describes the nature of the association: *why* is entity A related
to entity B? Not because they share a foreign key in some table. Look at the
real business and describe the real-life association.

This has two decisive benefits:

1. The verbs become the **predicates** in your subject–predicate–object
   triples when you construct the graph.
2. Naming forces distinctions that unnamed lines hide: "owning" a bank
   account is a completely different relationship from "having access to" a
   bank account. Two verbs means two relationships — and two different
   semantic facts your consumers will depend on.

**Guideline:** an unnamed relationship is an undeclared meaning. If two
different verbs describe two different business realities between the same
pair of entities, model two relationships.

### 0.7 Subtypes where they matter

A subtype is a "kind of" thing; a supertype is the higher-level thing. A car
is a kind of vehicle; a cat is a kind of mammal. Include sub/supertype
structure where it is relevant — and only where it is relevant. Over-
generalization makes models unreadable, but when people genuinely talk about
"two kinds of accounts", model the two kinds and their supertype. These
taxonomies are what your knowledge graph will need.

**Guideline:** subtype only on a genuine "kind of" relationship, and only
when the business distinguishes the kinds in practice.

### 0.8 Declare, don't vibe

A mindmap can help workshop participants reach an understanding, and that has
value. But a mindmap has vibes, whereas a good conceptual model has
structure. A mindmap is temporary, tied to a situation and a discussion; a
good conceptual model is universally true until the business itself changes.
A mindmap suggests; a good conceptual model **declares**.

**Guideline:** do the extra rigor. It is precisely what makes the model
convertible into an ontology later. A mindmap left in a project folder is a
wasted opportunity to build semantic architecture.

### 0.9 The conversion ladder (conceptual model → ontology)

With the discipline above, turning a conceptual model into a formal ontology
is mechanical:

- Every entity becomes a class (`owl:Class`).
- Every entity–relationship–entity pair becomes a triple.
- Entity definitions become class definitions (`skos:definition`).
- Subtypes/supertypes become `skos:broader` / `skos:narrower` or
  `rdfs:subClassOf`.
- The noun becomes the class name (`skos:prefLabel`).
- The verb becomes the predicate (`owl:ObjectProperty`).

Use the conceptual-modeling phase for what it is strongest at: building
shared understanding with business stakeholders *before* formalizing syntax.
Then continue building the ontology on that verified basic structure. The
discipline is the handoff — without it, the diagram cannot become the graph.

---
## 1. The method — the end-to-end sequence

Follow the steps in order. Each step has a purpose, a procedure, and a
"done when" acceptance gate. Do not start a step until the previous step's
gate is met — the sequence is load-bearing: identity before taxonomy,
taxonomy before relationships, relationships before responsibilities,
responsibilities before interfaces, integration before validation,
validation before publication.

Two principles govern the whole sequence:

- **Write the exam before the coursework.** The competency questions (Step 1)
  are approved before any modeling, and they become the executable
  regression tests (Step 11). A question the model cannot answer is a
  modeling gap, not a bad question.
- **One step at a time, with a gate.** Work a single step to its acceptance
  criteria before moving on. Scope decisions accumulate in the decision log;
  the source of truth is updated by one consolidated proposal per step, never
  churned per decision.

### Step 0 — Align the reference framework

**Purpose.** If your domain has a published reference framework, align to it
first. It becomes your consistency reference — the thing you check against,
not the thing you copy.

**Procedure.**
1. Adopt the official, current version of the framework. Verify any cited
   element IDs against the actual published workbook — never trust
   third-party mirrors or older citations.
2. Vendor the reference into your repo with its required attribution and
   license notice intact.
3. Cross-check every local node against the framework. Record every
   divergence as a boundary note with a reason — never hide it, never
   silently conform to it.
4. Decide the direction of the relationship once: the local model is the
   source of truth; the framework is the consistency check. Framework IDs
   attach by reference; they never replace local identities.

**Done when:** every cited ID is verified against the published source; all
divergences are recorded as boundary notes.

**Pitfall (from the worked example):** a repo-cited ID was stale across
framework versions (10006 in the mirror vs 20085 in the official release).
Verification against the workbook caught it. Trust, but verify — against the
workbook, not the mirror.

### Step 1 — Foundations

**Purpose.** Lock the policies everything else will assume. Changing these
later is expensive, so decide them before any modeling.

**Procedure.**
1. **Competency questions.** Draft the questions the ontology must answer,
   get them approved by the business owner, and lock them. They are the
   acceptance test for the whole build (see Step 11).
2. **URI policy.** Choose a persistent, redirect-backed base. It must be
   company-scoped — never tied to a person (usernames change, people change
   roles) and never tied to a project name (projects get rebranded). Preserve
   local source IDs as `skos:notation`; never replace them with reference-
   framework IDs. No version segment in URIs — versions ride on
   `owl:versionInfo`.
3. **Language policy.** Declare the primary language. Tag every literal
   (untagged and tagged literals are different RDF terms — tag everything or
   face silent SPARQL mismatches). One `skos:prefLabel` per language per
   concept; aliases in `skos:altLabel`; `skos:definition` required on every
   concept.
4. **Version policy.** SemVer per module and per release. URIs are immutable;
   deprecate with `owl:deprecated` + `dcterms:isReplacedBy`, never delete.
   The meaning-change test: would every query and answer produced under the
   old definition still be correct under the new one? Yes → patch. No →
   major. When in doubt, it is major — a false major costs a version bump; a
   false patch corrupts downstream consumers silently.
5. **License policy.** Decide before publishing anything. A proprietary
   artifact can be opened later; an open artifact cannot be un-opened.
   Reference-framework licenses coexist with your own — carry attribution on
   every distribution.
6. **Module policy.** Carve the ontology into modules with one-way
   dependencies, no cycles (CI-enforced). Cross-module use is by URI
   reference, never by redefinition: define once, reference everywhere.
   Modules version and validate independently.

**Done when:** all six policies are recorded in the decision log with
rationale; the competency questions are approved and locked.

### Step 2 — Identity normalization

**Purpose.** Every node gets a stable identity before anything is said about
it.

**Procedure.**
1. Preserve existing local IDs as `skos:notation` and derive URI slugs from
   them.
2. Mint stable slugs for ID-less nodes — a slug is the URL-friendly
   identifier coined where none existed.
3. Lock the rule: **slugs/IRIs are identity; labels are presentation.**
   Never use a label as a join, lookup, access-control, or API key. Labels
   change; identity does not.

**Done when:** every node has a stable HTTP URI; no node is identified by
label anywhere in the build.

### Step 3 — SKOS taxonomy

**Purpose.** Build the controlled vocabulary: the hierarchy of names, with
labels and definitions. This is a vocabulary of names, not a class hierarchy
— SKOS first, not OWL.

**Procedure.**
1. One `ConceptScheme`. `skos:broader`/`skos:narrower` for hierarchy,
   `skos:prefLabel`/`skos:altLabel` for names, `skos:notation` for local IDs,
   `skos:definition` on every concept.
2. Author definitions against the quality bar (§4): define the activity, not
   the label; state the primary purpose; bound the scope; pass the parent
   test ("this is a way of carrying out [parent]"); keep siblings disjoint;
   keep terminology stable; park future concepts instead of smuggling them in;
   evidence every claim; keep provenance clean.
3. Triangulate candidate definitions from references, but put every adoption
   through a human gate — reference text informs, it is never copied
   verbatim.
4. Rejected: mechanically converting each hierarchy level into OWL
   classes/subclasses. That asserts logical commitments (disjointness,
   inheritance of restrictions) that a naming hierarchy does not support.

**Done when:** every concept has a definition, a label, and a parent; the
mechanical gate (labels present, hierarchy integrity, no label collisions) is
clean.

### Step 4 — The relationship layer

**Purpose.** Turn the verbs between concepts into governed semantic
relationships — the predicates of your triples.

**Procedure.**
1. Inventory every verb used between concepts. Write a locked definition for
   each predicate you will emit (e.g. *enables*: the target is made capable
   of operating; *informs*: provides context or planning input;
   *dependsOnOutputOf*: consumes a specific needed output; *requires*: needs
   an approved prerequisite).
2. Map verbs to predicates in review batches, one predicate family at a
   time, one row at a time. For each row: direction first, then the
   definition test, then the verdict.
3. **Hold ambiguous rows for source correction — never remap meaning at
   emission.** A verb that seems better expressed as another predicate is
   held and routed to the source author; semantic plausibility never
   authorizes reclassification.
4. Keep a conservation ledger: emitted + held + deferred = total, reconciled
   mention by mention. Every count change gets a row-level entry (row ID,
   old bucket, new bucket, reason).
5. Keep promotion blocked until every verdict is recorded. The promotion
   script is the last thing to run, not the first.

**Locked rules (distilled from the worked example):**
- Emission never changes a row's meaning: it emits, holds, or defers.
  Workbook corrections return through reviewed authoring.
- Approving an already-emitting row changes only its basis; counts move
  only when a row changes bucket.
- No reciprocal two-cycles for directional dependencies.
- No semantic relationship emitted solely from hierarchy position — hold
  unless independent evidence establishes it.
- Duplicate merges are provenance-only: they never create facts, change
  predicates, or change direction.
- Evidence discipline: tests assert stored canonical facts, not source verb
  strings.

**Done when:** every row has a recorded verdict; the ledger reconciles; the
evidence gate is green; the promotion preconditions (re-pin, attestation,
regression, blast-radius proof) are met.

### Step 5 — ORG and RACI

**Purpose.** Say who is responsible. Roles are positions people hold, not
people themselves — the same person can be Accountable for one process and
merely Informed on another.

**Procedure.** Model roles as `org:Role`; bind role + process + RACI level
with an explicit n-ary `ResponsibilityAssignment` — a single property can
never carry a three-way binding. RACI is design-time responsibility.

**Done when:** every in-scope process has its RACI assignments; no
responsibility is implied by hierarchy position.

### Step 6 — Interfaces and PROV-O

**Purpose.** Separate what is planned from what happened.

**Procedure.** Model planned inputs/outputs on the definitions. Model actual
occurrences as `prov:Activity` — and only occurrences. Never auto-type a
definition as an activity: the recipe is not the meal. Use PROV-O's second
job — trust — to record which source asserted a mapping, when, and under
what authority.

**Done when:** no definition is typed as an occurrence; every occurrence
links to its definition.

### Step 7 — Cross-model integration

**Purpose.** Link the models to each other: processes to value streams,
capabilities, systems, and data products.

**Procedure.** Resolve the gaps the earlier steps exposed (empty output
sets, ownership orphans, unlinked systems) one at a time, each as a recorded
decision. Do not invent ownership to fill a gap — an explicit "unowned,
parked" beats a guessed owner.

**Done when:** every integration gap has a decision (linked or explicitly
parked).

### Step 8 — Scope review (do it early)

**Purpose.** Decide what is in and out before the foundations harden.

**Procedure.** Take each candidate area one at a time. In scope only with a
genuine hook into the ontology's purpose (a value-chain link, a RACI feed, a
data-product dependency). Out-of-scope gets a boundary note with a reason —
"ERP-native, nothing depends on it" beats silent omission. Revisit triggers
are recorded, not forgotten.

**Done when:** every candidate has an in/out call with rationale and a
revival trigger.

### Step 9 — SHACL validation

**Purpose.** Turn every locked decision that can be checked mechanically
into a shape.

**Procedure.** Core SHACL first; SHACL-SPARQL only where Core cannot express
the constraint. Cover: labels present, identifier policy, hierarchy
integrity (one parent per concept), controlled values, references present
where alignment is claimed. Validation reports are data, not verdicts — a
failing shape is a question for a human, not proof of a bad model.

**Done when:** the shapes graph runs against the data graph with zero
unexplained violations.

### Step 10 — DCAT publication

**Purpose.** Ship a published, versioned artifact — not a file on a disk.

**Procedure.** `dcat:Catalog` → `dcat:Dataset` → `dcat:Distribution` /
`dcat:DataService`. The dataset-vs-distribution distinction is load-bearing:
one dataset, many serializations (Turtle, JSON-LD, SHACL shapes, HTML docs).
Every release records its module versions, issued/modified dates, and
changelog.

**Done when:** the catalog resolves; the current release is retrievable as
versioned distributions.

### Step 11 — SPARQL regression tests

**Purpose.** Prove the ontology keeps answering its exam.

**Procedure.** Convert the Step 1 competency questions into executable
SPARQL. Run them against every release. A failing test is a regression or a
deliberate, recorded change — never a surprise.

**Done when:** all competency questions execute green against the published
release.

---
## 2. Policies — the locked decisions

Prescriptive policies. Each states the rule and the reason it exists. They
change only by dated amendment with the owner's explicit agreement — never
by silent override. Project-specific applications live in the worked example
(§7).

### Source of truth and scope
- **Model your own business; use references as checks.** The local source
  (your process map, your system inventory) is the source of truth. A
  reference framework is a consistency reference — nothing in your model may
  contradict it, and deliberate divergences are recorded as boundary notes,
  never hidden.
- **Cover enabling functions, not just the value chain** — but only where
  the ontology has a genuine hook (a RACI feed, a data-product dependency).
  Functions with no hook stay out, with a boundary note.
- **The ontology defines; it does not calculate.** It answers what things
  *are*. Computation, execution, and storage belong to the systems that point
  at the ontology — they never become a second ontology.

### Identity
- **URIs are persistent, company-scoped, and person- and
  project-independent.** People change roles and usernames; projects get
  rebranded. Only the organization sits behind the redirect — a future
  rebrand updates one redirect, not every identity.
- **Preserve local IDs; never replace them with reference IDs.** Existing
  codes are `skos:notation` and the basis of URI slugs. Reference-framework
  IDs attach via `dcterms:references` only. Most local concepts have no
  reference counterpart and vice versa — the local model leads.
- **No version segment in URIs.** Identity survives definition changes;
  versions ride on `owl:versionInfo`. A consumer who bookmarked a URI years
  ago must still get a correct answer.
- **Slugs/IRIs are identity; labels are presentation.** Never use a label
  as a join, lookup, access-control, or API key. Labels change; identity
  does not.

### Language and versioning
- **Tag every literal with its language.** Untagged and tagged literals are
  different RDF terms — tag everything or face silent SPARQL mismatches. One
  `skos:prefLabel` per language per concept; aliases in `skos:altLabel`;
  `skos:definition` required on every concept.
- **SemVer per module and per release; URIs immutable.** Major = breaking
  (URI change, removal, redefined meaning — the test is whether existing
  queries and answers stay correct). Minor = additive. Patch = wording.
  **Deprecate, never delete** (`owl:deprecated` + `dcterms:isReplacedBy`) —
  storage is cheap; broken references are expensive. Full operational detail
  in Appendix B.
- **Ontology identity (2026-09-22; IRI corrected to the locked Step 1
  policy the same day).** The `core` module's ontology IRI is
  `https://w3id.org/lsc/ontology/modules/core` — the locked
  `…/modules/{module}` namespace pattern, which also doubles as the
  module's ConceptScheme. Each release gets a version IRI of the form
  `https://w3id.org/lsc/ontology/modules/core/1.0.0`. Every release ships
  an explicit `owl:Ontology` header carrying `dcterms:title`,
  `dcterms:description`, `owl:versionIRI`, `owl:versionInfo`,
  `dcterms:issued`, `dcterms:creator`, and `dcterms:license`. Term IRIs
  stay stable and unversioned — `core:ProcessDefinition` is
  `https://w3id.org/lsc/ontology/modules/core/ProcessDefinition`,
  never `…/modules/core/1.0.0/…`. (The Q1 decision text originally used
  the shorthand `…/ontology/core`; corrected on review — the Step 1 lock
  was never changed, the shorthand never shipped, nothing is published,
  so no supersession record is needed.)

### Licensing
- **Decide the license before publishing anything.** A proprietary artifact
  can be opened later; an open artifact cannot be un-opened. If the ontology
  describes competitively sensitive operations, proprietary with the owner
  as IP holder is the safe default.
- **Reference-framework licenses coexist with your own.** Carry the
  framework's attribution on every distribution; reference its IDs freely;
  quote sparingly and marked; adapt openly where your context needs it —
  but never republish whole reference branches as your own.

### Modules
- **Carve modules with one-way dependencies, no cycles** (CI-enforced).
  Cross-module use is by URI reference, never by redefinition: define once,
  reference everywhere. Modules version and validate independently; minor and
  patch by the module owner, majors by the ontology owner.
- **One module owns each domain's concepts.** Deliberately avoid duplicate
  domain modules (no `customer` module alongside a `party` module) — the
  domain is a view across modules, its concepts anchored in exactly one of
  them.

### Modeling discipline
- **SKOS-first taxonomy.** A naming hierarchy is a controlled vocabulary,
  not a class hierarchy. Never mechanically convert hierarchy levels into
  OWL classes — that asserts logical commitments (disjointness, inheritance
  of restrictions) the hierarchy does not support.
- **Separate definitions from occurrences.** A process definition is not an
  activity that happened. `prov:Activity` is reserved for actual occurrences
  on dates.
- **RACI is design-time responsibility** and needs an explicit n-ary model
  binding role + process + level — a single property cannot carry a
  three-way binding.
- **Classify by primary purpose, not by location or asset.** A tank, a
  system, or a team can participate in multiple contexts without being
  forced into one category. When a concept could live in two domains, ask
  each domain's primary question and place it where the question it answers
  is asked. Technique: write one primary question per domain ("what is the
  financial position, performance, obligation, and exposure?" for Finance)
  and use the table as the placement test for every new concept.
- **Do not declare disjointness without evidence.** Lanes, categories, and
  classifications stay non-disjoint until the business guarantees they are.

### Scope and change control
- **Every new concept is slotted into the existing hierarchy** — no
  level-less nodes.
- **Scope decisions accumulate in the log; the source of truth is updated
  by one consolidated proposal** after the modeling pass — never churn the
  source per decision.
- **Park, don't smuggle.** Future concepts go in an explicit parked list;
  no data fields, systems, KPIs, controls, or thresholds as concepts.
- **Confirm ambiguous source fields before naming ontology terms.** A field
  named `sioc` is not the W3C SIOC vocabulary until proven — verify the
  business meaning first.
- **Do not invent ownership to fill a gap.** An explicit "unowned, parked"
  beats a guessed owner every time.

### Playbook maintenance (decided 2026-09-30, Hamid)
- **Two copies, two roles.** This file is the **method** (normative):
  `business_architecture/ontology/ontology-playbook.md`. The **working
  record** is `business_architecture/ontology/step4/playbook/ontology-playbook.md`:
  the plan table, the step log and the decision journal. It's current on
  build status.
- **One place decides, one place narrates.** A decision change lands here in
  §2 first. The working record's decision log carries the dated journal
  entry pointing at it. The copies are never updated independently on the
  same decision.
- **One entry point.** `business_architecture/ontology/README.md` is the
  single "Start here". Agent instructions defer to that README rather than
  naming a copy, so there's exactly one pointer to maintain.

### Step 4 design locks — Q1–Q12 (decided 2026-09-22)

These twelve decisions fixed the Step 4 design. They are locks: do not
re-litigate them without a new decision recorded the same way.

- **Q1 — Vocabulary namespace (corrected on review the same day).**
  `core:` (`https://w3id.org/lsc/ontology/modules/core/`) for reusable
  vocabulary — classes and properties. `proc:` stays instance-only.
  Term IRIs are stable and unversioned
  (`core:ProcessDefinition` =
  `https://w3id.org/lsc/ontology/modules/core/ProcessDefinition`,
  never `…/modules/core/1.0.0/…`). The module namespace doubles as the
  module's ConceptScheme. Module-boundary rule: `core:` = foundational
  planned-process semantics only; org → Step 5, kpi → kpi module,
  observed execution → PROV-O in Step 6. `core:ProcessDefinition` typing
  rule (narrower than the proposal; supersedes F1): apply to approved
  process + capability concepts, candidate structural/capability nodes
  with authored definitions, blocked/retired only when retaining a
  meaningful record. Do NOT apply to L0 scheme roots, pure structural
  anchors, tombstones, or not-process roots. NOT adopted: the `data:`
  module from the external review's boundary rule — the module policy
  has four modules (core, party, kpi, organization); adding `data:`
  needs its own decision. Correction: the Q1 decision text
  originally used the shorthand `…/ontology/core`; corrected on review
  2026-09-22 — the Step 1 lock was never changed, the shorthand never
  shipped, nothing is published, so no supersession record is needed.
  The ontology IRI is `https://w3id.org/lsc/ontology/modules/core` and
  the version IRI `…/modules/core/1.0.0` — the `…/ontology/core`
  shorthand is recorded on main as rejected; do not use it.
- **Q2 — intake: retirement mode.** Flag-day: all `intake:` triples go in
  one Step 4 release — no deprecated-alias transition (~5,571 dead staging
  triples is not worth carrying). Preconditions: re-confirm the
  no-consumer attestation; per-predicate conservation ledger (emitted +
  held = source total for every `intake:` predicate — "zero `intake:`
  triples" proves deletion, not replacement); explicit merge/release
  approval still required.
- **Q3 — first formal version.** Step 4 ships as `core` 1.0.0 — the first
  formal release of the core module, first with governed properties
  instead of provisional annotations, first with an explicit version
  header (`owl:versionInfo`, issued date, license,
  `owl:versionIRI https://w3id.org/lsc/ontology/modules/core/1.0.0`).
  1.0.0 is the baseline Step 5, Step 6, and later modules version
  against.
- **Q4 — uses-input.** Step 4 models inputs as direct process-to-process
  edges: `core:dependsOnOutputOf` (inverse `core:providesInputTo`) — a
  process is not an input; its output is. No new nodes. The edge preserves
  the dependency chain ("what does this process depend on; what breaks if
  it fails") that the competency questions need. `core:consumes` /
  `core:produces` are reserved for future identified InformationObject
  instances.
- **Q5 — flow depth.** Flows are governed structured values on the
  input/output links — controlled, consistently-spelled flow names, no new
  nodes. The workbook's flow information is preserved and queryable
  ("which processes consume the demand forecast?"). Minting
  InformationObject nodes (~1,900) is deferred: identity, dedup,
  ownership, and lifecycle for flows is a data-governance project no Step
  4 competency question or consumer requires. Revisit trigger: a real use
  case that needs to trace a specific artefact (e.g. audit lineage of the
  approved operating plan) — then mint that flow as a node deliberately,
  one at a time.
- **Q6 — processHorizon facet split.** `intake:processHorizon` conflated
  three dimensions (evidence: 8 distinct workbook values across 485 rows —
  event-driven/periodic/continuous are operating modes; daily/weekly/
  monthly are cadences; tactical/strategic are planning levels; "periodic"
  alone (107 rows) records no cadence). Split into three controlled
  fields: `core:operatingMode` (event-driven | periodic | continuous),
  `core:cadence` (daily | weekly | monthly | quarterly | annual),
  `core:planningLevel` (strategic | tactical | operational). Rows with
  only "periodic" are recorded as cadence-unspecified — honest about the
  gap rather than pretending "periodic" is a cadence.
- **Q7 — responsibleDomain interim.** Kept as a governed literal on the
  process, explicitly interim. No org nodes minted — Step 5 (ORG/RACI)
  designs the org model and replaces these labels with references to real
  org units/roles, where the operating model evidences the relationship
  (some labels are business domains, not org units). Evidence: 10
  distinct workbook values across 485 rows, 456 of them "Commercial &
  Marketing"; the 6 free-text cross-functional entries normalize to a
  governed "Cross-functional" value with detail preserved in a note. The
  controlled list makes the Step 5 migration mechanical.
- **Q8 — conceptKind controlled scheme.** `core:conceptKind` is an object
  property to a controlled SKOS scheme, not a string. Kinds: Process
  (real business process with inputs/outputs/cadence), Capability (an
  ability the organization has, realized by processes), StructuralAnchor
  (navigation/grouping node — L0 roots, empty stubs, tombstones — not
  work anyone performs). Rationale: consumers treat kinds differently
  ("all processes" must not return navigation nodes; no RACI/cadence on
  anchors). Deliberate boundary: this does NOT classify CM-1-3-1-6
  ('Marketing Insight and Metrics Stewardship') — that stays a parked
  modeling question. The shelf is built; classification comes later.
  `core:taxonomyLevel` is documented derived metadata ("current rendered
  depth") — never for security, KPI ownership, criticality, domain
  assignment, or level-assuming queries.
- **Q9 — lifecycle model, three dimensions (revised).** The single-chain
  model (Candidate → Approved → Deprecated → Retired) was WITHDRAWN — it
  conflated concept lifecycle with approval status. Three independent
  dimensions instead:
  - `core:lifecycleStatus`: Active / Deprecated / Retired (Superseded =
    Deprecated + `dcterms:isReplacedBy`, not a state).
  - `core:governanceStatus`: Exploratory / Draft / Candidate /
    ApprovedBaseline / Implemented (existing vocabulary, formalized).
  - `core:holdStatus`: NoHold / EvidenceHold / OwnershipHold /
    DecisionHold / ImplementationHold + `core:holdReason`.
  OWL alignment: Deprecated/Retired ⇒ `owl:deprecated` true;
  Active ⇒ `owl:deprecated` absent or false. Agreement
  enforced by SHACL in Step 9; the rule is stated now. Retired is
  terminal for active use — restorable only via a new governance
  decision + provenance, never by silent un-retirement. Blocked/held are
  NOT lifecycle states — a Candidate can be blocked; an Approved concept
  can be put on hold without losing its state.
- **Q10 — terminology-note migration.** Selective-alias policy (blanket
  "every prior name becomes altLabel" rejected — altLabel is a live
  search commitment): safe former names → `skos:altLabel`, only if
  unique, non-misleading, non-colliding, and useful for retrieval;
  generic/ambiguous/authority-overstating/case-only/scope-limited former
  names → preserved in migration history via `core:priorPreferredLabel`
  (annotation property), NOT searchable; scoped aliases keep their
  context in the migration map, never flattened into altLabel; one-line
  rename rationale → `skos:editorialNote`; migration event and source →
  `dcterms:provenance`; full reviewer reasoning stays in the decision log
  by reference. Conservation rule (extends the Q2 ledger): every
  non-null prior_name gets exactly one recorded disposition; every
  name_change_note maps to rationale + provenance; every
  scoped_historical_alias has a context or is explicitly rejected. A
  92-row historical-label disposition report is a tracked pre-cutover
  gate.
- **Q11 — relationship target dispositions.** Every relationship mention
  gets a governed disposition; ONLY mentions classified as
  process-to-process become Step 4 object-property triples. Six
  disposition types: ResolvedToConcept, ParkedFutureConcept,
  StructuredFlowValue, ExternalGovernanceReference, DroppedAsNonProcessProse,
  and AmbiguousDeferred (added by Q12). Item dispositions for the 9
  unmatched targets (corrected after the bare-phrase matching error):
  DOA → CM-1-2-2-3-2; Integrated Marketing Planning → CM-1-3-5-2; Serve
  to Customer → CM-1-3-6-2-6; Develop/Update Strategy → CM-1-3-2-2-4
  (CVP context confirmed); Trading Books → CM-1-2-2-3-1 (batch 12
  split); Network Design → CM-1-3-3-4 for qualified mentions, with ONE
  genuinely unmatched bare mention (Brand Imaging row) moved to
  AmbiguousDeferred by Q12; backcasting basis + Monthly Operating Plan →
  StructuredFlowValue; Data Governance → ExternalGovernanceReference.
  DroppedAsNonProcessProse currently has no members. Recorded principle:
  **labels aren't identity**.
- **Q12 — ambiguous relationship targets.** A lexical match is not a
  semantic resolution. Resolve a target only when stable identifier
  evidence or approved contextual evidence (source definition,
  branch/domain, verb, scope, decision record) identifies ONE governed
  concept; otherwise record AmbiguousDeferred with raw phrase, candidate
  set, evidence considered, reason, and review trigger — emit no triple.
  Decision ladder: stable ID → approved contextual evidence sufficient
  to identify exactly one governed target (**label match is a candidate
  filter, never a join**; resolution recorded as the concept's slug, per
  the 2026-09-21 identity lock) → scoped historical alias (valid
  context) → defer; non-process phrases fall back to Q11 dispositions.
  The row-level disposition report gains: candidate slugs/labels,
  resolution evidence, confidence (Resolved/Contextual/Deferred),
  emission decision, review trigger.

---
## 3. Step 4 evidence discipline — promoting intake data without corrupting it

> Status: APPROVED 2026-09-24. Canonical. Restore note: this section was
> dropped in the prescriptive rewrite's first pass and restored in full
> 2026-09-26 — the rewrite's distilled bullets in §1 Step 4 are a summary
> of this section, not a replacement.

Step 4 promotes the provisional `intake:` annotations to real ontology
properties. The intake layer is the only copy of facts like "which
process uses which input" and "which process the workbook says this one
follows." If the promotion is sloppy, those facts are corrupted silently
— the triples look fine, but they no longer say what the business said.
The eleven rules below are how we keep that from happening. They were
developed promoting 5,571 intake triples and 1,318 relationship
mentions, and several of them exist because an earlier, weaker version of
the check failed and we fixed the premise instead of patching the row.

### The eleven rules

1. **Pin all evidence to one approved `main` SHA.** Every evidence file
   (dispositions, reviews, ledgers) carries `baseline_sha`, and the byte
   hashes of the baseline inputs are recorded. Before the eventual
   release, re-pin to the then-current approved `main`; all build and
   evidence artifacts must cite the same SHA.
2. **Regenerate old review packages after the taxonomy evolves.** A review
   package built against last month's taxonomy is a review of last
   month's data. After any rename/reparent/reclassification, regenerate
   the package from the pinned baseline and diff it field-by-field
   against the old one — do not merely re-validate the old CSV.
3. **Carry approvals only for field-equivalent rows, except where an
   evidence-strengthening change adds a stable identifier or source
   citation while the source, verb, resolved target, and disposition
   remain unchanged. The exception must be recorded explicitly.** An
   approval granted against v1.1 carries to v2 only if the row is
   identical on every evidence field (same concept, same label key, same
   candidate) — or qualifies under the recorded strengthening exception.
   Anything else goes back for review — only the differences, not the
   whole package.
4. **Treat labels as candidate filters, never as identity evidence.** A
   matching label proposes a candidate; it never proves the target. Slugs
   and IRIs are identity.
5. **Structural nearness alone is sufficient only for approved local
   sequence-pattern relations between sibling processes. For enables,
   governed-by, requires, assures, and dependency relations, it must be
   combined with independent definition, scope, reciprocal, or approved
   decision evidence.** A unique label match earns a candidacy, not a
   triple. Promotion needs at least one of: an explicit citation of the
   target in the source's definition or scope note; a consistent two-way
   mention (strict inverse pairs only); structural nearness inside the
   same decomposition branch (siblings for sequences; shared L2/L3 branch
   and no ancestor/descendant relation otherwise) *plus* one of the
   independent evidence types above for non-sequence relations. Label
   match alone = held for domain-batch review.
6. **Sample every batch of automatic promotions per domain, and stop at
   the first wrong resolution.** Sample `max(10, ceil(5%))` per domain
   (seeded, so it is reproducible). A human reads each sampled row's
   definitions and records OK or FLAG. One wrong resolution stops the
   line: tighten the rule and re-run — never patch the single row.
7. **Conserve every source predicate and every relationship mention
   through migration.** The Q2 ledger accounts for all 5,571 intake
   triples across 13 predicates and all 1,318 relationship mentions:
   emitted, held, merged, or redirected. No source record leaves the
   migration without a recorded disposition. DroppedAsNonProcessProse is
   a governed disposition, not unaccounted loss. Conservation is proved
   by arithmetic, not asserted; the exact counts live in the ledger's
   evidence section, not in this rule.
8. **Store one canonical direction per fact; derive inverses, never store
   mirrors.** `A precedes B` and `B follows A` are one fact stored as
   `A core:precedes B`. Mirrored rows inflate the fact count and let
   contradictions hide. Pairs that contradict one another under a
   property that does not allow mutual relation are held, not emitted.
9. **Keep raw verb and source-row evidence outside RDF reification for
   1.0.0.** The evidence (which workbook verb, which row, which test
   promoted it) lives in versioned CSVs beside the build, not as reified
   triples. Revisit after 1.0.0 if consumers need provenance in-graph.
10. **Release gate: same-SHA evidence plus a fresh no-consumer
    attestation.** The release build, the evidence package, and the
    consumer-impact scan must all cite one SHA. And immediately before
    flag-day, re-confirm the foundation-stage attestation (no consumers
    yet) — a stale attestation is not an attestation.
11. **Emission never changes source meaning.** Promotion may emit, hold,
    defer, or reclassify a source relationship; it may not replace a
    verb, invent a target, or reinterpret business meaning. Corrections
    are made in the workbook through a reviewed authoring change.

### Why each rule exists (the failures that taught them)

- **Stale baselines silently approve different data.** The v1.1→v2
  comparison found 53 rows whose raw target labels changed under them
  (Step 3d renames), 1 genuinely new relationship row (the approved R1
  interface), and 35 rows whose evidence got *stronger* (slug
  parentheticals added to mentions). None of that is visible without the
  SHA pin and the field-by-field diff (rules 1–3). Reviewing v2 rows
  against v1.1 approvals without the diff would have approved renames
  nobody re-read.
- **Labels drift and collide.** "Refinery Planning" became "Refinery
  Planning and Optimization"; "Determine Taxability" names two different
  concepts in two decompositions; the CVP strategy labels split four
  ways in Step 3d. Any pipeline that joins on labels inherits every one
  of those events as a silent misresolution (rule 4).
- **The first context pass was confidently wrong.** It promoted 915 rows
  on tests that did not test what they claimed: "explicit reference"
  read terminology notes instead of definitions, any backlink counted
  as two-way confirmation, and hierarchy proximity counted as
  relationship evidence. The corrected pass promotes 852 and holds
  169 — including rows the old pass had blessed. The lesson was not
  "fix the 63 rows" but "the premise was untested": we wrote the failing
  checks first, watched them fail, then fixed the implementation
  (rule 5, and the attack-the-premise trigger below).
- **Zero `intake:` triples proves deletion, not migration.** A build
  that drops the intake namespace and shows no intake triples has proved
  the annotations are gone. Migration is proved only by the ledger:
  every triple and every mention accounted for, each with a recorded
  disposition (rule 7).
- **Mirrored rows inflate facts.** 386 mentions collapse into 193 facts
  once mirrors merge. Mirrored relationship mentions materially inflate
  the raw mention count; the conservation ledger reports the exact
  mention-to-canonical-fact reconciliation for each release (rule 8).
- **Release evidence from mixed commits is invalid.** A consumer-impact
  scan run against one SHA and a build cut from another is theater. One
  SHA for build, evidence, and scan — re-pinned at release time
  (rule 10).
- **Promotion logic must not author meaning.** A mistyped workbook verb
  ("assures" where the business meant "satisfies") cannot be repaired by
  the promotion script choosing a nicer predicate — that would launder
  an authoring error into the ontology. The script emits, holds, or
  defers; the correction goes through reviewed workbook authoring
  (rule 11).

### Standing triggers

- **Attack the premise:** two failed fixes on the same gate, or two "the
  checker never asserted that" moments on one class of check → stop
  writing fixes; census what the check does *not* cover and fix the
  premise.
- **Write the failing check first:** every regression fix starts with a
  gate assertion watched failing on the broken state, then the fix,
  then the pass.
- **Reviewer verdicts:** every evidence package gets the interrogate
  pass (Act On / Consider / Noted / Dismissed) before Hamid reviews it.


### Verb review methodology — how to judge a predicate family

Each verb gets its own review pass: one predicate, one batch, one set of
verdicts. The pass has four phases.

**Phase 1 — Lock the definition.** Write the predicate definition before
looking at rows. The definition must be falsifiable: it should be possible
to read a row and say "this fails the definition." A definition that every
row passes is not a definition. Each definition below is shaped by a
specific confusion it exists to prevent.

**Phase 2 — Build the review batch.** Pull every row asserting the verb.
For each row, record: source and target (by slug, never label alone),
both definitions, the raw verb string, the evidence tier, and the
pipeline's proposed disposition. The reviewer reads the definitions, not
the pipeline's recommendation.

**Phase 3 — Verdict each row.** For each row: identity first (record the
match type — stable ID or label only — and the rule 4/5 route; label-only
rows need an affirmative citation, a strict two-way pair, or a recorded
architecture decision; exception: for `core:precedes` siblings, structural
nearness alone suffices per Rule 5), then direction (is the arrow pointing the right
way?), then the definition test (does the source-target pair satisfy the
locked definition on the evidence in their definitions?), then the
verdict: APPROVE, HOLD, or STAND.
- **APPROVE** means the row satisfies the definition and the fact is
  stored (or its basis is updated if already emitting).
- **HOLD** means the row fails the definition or the evidence is
  insufficient. The fact is not emitted. The row is routed for source
  correction. A hold is never a remap: if the row seems better expressed
  as a different predicate, that is a source-meaning question, not an
  emission-time decision.
- **STAND** means the row was already correctly emitting and the review
  confirms it. Approving an already-emitting row changes only its basis;
  counts move only when a row changes bucket.

**Phase 4 — Sample and reconcile.** For large batches, sample per the
evidence discipline (Rule 6): draw samples only from promotions, record
outcomes as pending until Hamid reviews them. One wrong sample stops the
pass. Reconcile counts: every row has a verdict, every verdict is
recorded, the ledger balances.

**Exclusion citations (all verbs).** Exclusion, boundary, "owned by", and
"may be handled by" wording is never a route — for any verb. This is the
REL-00009 precedent, applied across all predicates. A citation that only
states where a boundary lies, who owns something, or what is excluded
does not establish the relationship the verb asserts.

**Approved-decision evidence.** Row-level verdicts are not
approved-decision evidence. Only recorded architecture decisions count —
for example, PR #110 and PR #119. A verdict recorded in a review batch
documents the reviewer's judgment; it does not constitute an architecture
decision.

**Per-verb guidance.** Each entry: the locked definition, what counts as
evidence, the common pitfall the definition guards against, and why the
boundary is drawn where it is.

- **`core:enabledBy` (source is enabled by target).** *The target supplies a
  maintained operating base, required control, governed mechanism,
  capability, resource, or prerequisite condition that makes the source
  able to operate.* Stored: `enables (S, T)` → `T core:enabledBy S` —
  the triple reads with the enabled thing as subject, the enabler as
  object, the same stored-direction convention as `informedBy`,
  `assuredBy`, and `triggeredBy`. Evidence: the target definition names
  the capability or control the source depends on. Pitfall: confusing
  enablement with sequence (the source happens after the target), with
  information flow (the target informs the source), or with hierarchy
  (the target is the parent). The test is capability: would the source
  be unable to operate without what the target supplies? If the answer
  is "it would just be less informed" or "it would happen later," that
  is not enablement.
  - **Disposition split (enables only).** Not every enables row becomes
    an `enabledBy` triple. G1a: merge as duplicate evidence on the
    existing `dependsOnOutputOf` fact — no new `enabledBy` triple.
    G1b: HOLD, no verb change. G2: no triple. Only G3 emits
    `core:enabledBy`.

- **`core:informedBy` (source is informed by target).** *The target
  provides context, planning input, or situational awareness the source
  uses. Information flows from target to source.* Evidence: the source
  definition names the information or the target as an input. Pitfall:
  promoting every data flow to informedBy. The definition requires that
  the information actually shapes the source's behavior, not merely that
  data moves between them. **Hold label:** "counterpart, opposite flow"
  — when the citation shows information flowing from source to target,
  the direction is reversed; hold, do not flip at emission time.

- **`core:dependsOnOutputOf` (source consumes target's output).**
  *The source consumes a specific, identifiable output the target
  produces.* Evidence: the source definition names the output or the
  target as its producer. Pitfall: confusing consumption with
  enablement. If the source needs the target's output to function, that
  is a dependency; if the source needs the target's capability to exist,
  that is enablement. The distinction matters because the remediation
  differs: a broken output is a data problem, a missing capability is an
  operating-model problem.

- **`core:requires` (source requires target).** *The source cannot
  validly start, complete, proceed, or reach its controlled state
  without the target, its completed control, or its required condition.*
  Evidence: the source definition states the prerequisite as a gate —
  "once required approvals are complete," "validating X before Y."
  Pitfall: inferring a requirement because the target later consumes or
  calculates related information. A downstream consumer does not create
  an upstream requirement. The requirement must be stated as a
  precondition in the source, not inferred from the target's behavior.

- **`core:assuredBy` (source is assured by target).** *The target
  performs defined governance, compliance, quality, review,
  control-testing, or equivalent oversight over the source or its
  outcome.* Evidence: the target definition describes the oversight
  activity and names the source (or its domain) as the assured thing.
  Pitfall: promoting support, documentation, or evidence-supply to
  assurance. A process that produces the workpapers is not assuring the
  process that uses them. Assurance requires an explicit oversight role,
  not merely involvement in the control environment.

- **`core:constrainedBy` (source is constrained by target).**
  *The target is a binding constraint source for the bounded activity,
  decision, or outcome.* Stored from the constrained thing to the
  constraint. Evidence: the source definition names the constraint or
  the target as imposing it. Pitfall: confusing constraints with advice,
  ownership, sequencing, or broad association. A target that the source
  "considers" or "coordinates with" is not a constraint. The constraint
  must bind: the source cannot validly exceed, ignore, or waive it.

- **`core:governedBy` (source is governed by target).** *The target
  exercises governance authority over the source — policy-setting,
  approval rights, or compliance enforcement.* Evidence: the target
  definition states the governance relationship. Pitfall: structural
  closeness. A process is not governed by its parent merely because the
  parent exists in the hierarchy. Governance requires an explicit
  authority relationship, not a position on the org chart. **Hierarchy
  exception (approved text, verb-predicate-mapping-v2.md §5):** Permitted
  only if all six hold: (1) documented relationship beyond containment;
  (2) the definition identifies distinct governance, control,
  decision-right, output-consumption, or externally reusable enablement
  semantics; (3) the rationale identifies that independent semantic
  evidence rather than the hierarchy path; (4) the evidence ledger
  preserves the hierarchy path and the exception rationale; (5) a
  reviewer approves the row explicitly — no automatic promotion; (6) the
  target is identified by source-backed evidence under the identity rule
  as finally scoped. Each exception is recorded as "not a precedent"
  for automatic emission.

- **`core:triggeredBy` (source is triggered by target).** *The target
  generates, detects, manages, or records the event, exception,
  monitoring outcome, change, referral, or handoff that initiates the
  source.* Evidence: the source definition names the triggering
  condition and the target as its origin, and the citation must tie the
  source's event to the target — the target is where the event comes
  from, not merely a process the source interacts with. Pitfall:
  "feeds," "informs," "supports," "uses," or "precedes" do not become
  triggers without an invoking event. A trigger is a discrete initiating
  condition, not a standing relationship.

- **`core:precedes` (source precedes target).** *The source completes
  before the target begins, as a sequence the business asserts.*
  Evidence (Rule 5): for siblings, structural nearness alone is
  sufficient — sibling sequence-pattern relations do not need an
  additional citation; for non-siblings, an affirmative sequence link
  in the source definition ("arrives from," "routes to," "executes
  through," "comes from," an explicit handoff) or a strict two-way
  mention. The citation must be an affirmative sequence assertion, not
  merely a mention of both processes. Pitfall: exclusion, boundary, or
  owned-by wording is not a sequence route. "Excludes X" tells you where
  the boundary is, not what happens first. A non-sibling row with only
  boundary wording is held.

**Why one verb per pass.** Verdicts require the reviewer to hold one
definition in mind and apply it uniformly. Mixing verbs in a batch
invites definition drift: the reviewer starts judging "requires" rows by
"enables" instincts. The cost of separate passes is linear; the cost of
a corrupted predicate is unbounded, because every downstream consumer
inherits the misclassification.

**Why holds are not remaps.** When a row fails its verb's definition but
seems to satisfy another's, the temptation is to reclassify at emission
time. This launders an authoring decision into the pipeline. The source
author chose the verb; if the verb is wrong, the correction belongs in
the source, reviewed as an authoring change. The pipeline emits, holds,
or defers — it never authors.

---

## 4. Standards guide — why each standard earned its place

Each entry: what the standard is, why it belongs in an ontology build, what
it is *not* for, and what was deliberately rejected. The rejections matter as
much as the adoptions — they are what keep a model honest.

### RDF — the grammar
**What:** the subject–predicate–object triple model; everything else here is
a vocabulary written in RDF.
**Why:** it is the only layer the whole stack shares. Every statement the
ontology makes is an RDF statement; every other standard is just an agreed
set of predicates.
**Not for:** carrying meaning by itself — RDF without a vocabulary is
punctuation without words.

### SKOS — the taxonomy backbone
**What:** a vocabulary for governed concept systems: `ConceptScheme`,
`prefLabel`/`altLabel`, `broader`/`narrower`, `notation`, `exactMatch`.
**Why:** a process hierarchy is a *controlled vocabulary of names*, not a
class hierarchy of types. SKOS gives labels, aliases, hierarchy, and
crosswalks (to a reference framework) without pretending each node is an
ontological class.
**Rejected:** mechanically converting hierarchy levels into OWL
classes/subclasses — that asserts logical commitments (disjointness,
inheritance of restrictions) a naming hierarchy cannot support.

### Dublin Core Terms — describing the sources
**What:** `dcterms:title`, `dcterms:references`, `dcterms:license`,
`dcterms:provenance`, etc.
**Why:** the ontology constantly talks *about* its sources — the reference
workbook version, the source JSON, the license terms. Dublin Core is how a
concept says "I was checked against framework vX" and how a dataset says
"you may reuse me under these terms."
**Not for:** describing the domain (that is SKOS and the domain classes).

### RDFS / OWL — the schema layer, used sparingly
**What:** classes, properties, subclass/subproperty, domain/range (RDFS);
equivalence, disjointness, inverses, cardinality (OWL).
**Why:** you need *some* real classes — process definitions,
responsibility assignments, named KPIs — and the relations between them.
RDFS/OWL defines those precisely.
**Constrained:** RDFS/OWL is *inference*, not validation. Domain and range
do not check data; they generate new triples. Never use OWL to "fix" the
taxonomy; assert disjointness or cardinality only where the business
actually guarantees it.

### PROV-O — what happened and who vouches for it
**What:** `prov:Entity`, `prov:Activity`, `prov:Agent`.
**Why:** two jobs. (1) *Occurrences vs definitions:* a planned process is a
definition; a run of it on a date is a `prov:Activity`. The split keeps the
model from confusing the recipe with the meal. (2) *Trust:* which source
asserted this mapping, when, under what authority.
**Rejected:** typing taxonomy concepts as `prov:Activity` by default. A
process definition is not an activity that happened.

### ORG — roles for RACI
**What:** `org:Role`, `org:Membership`, posts and organizations.
**Why:** RACI needs roles that people hold, not people themselves. `org:Role`
gives that indirection; the n-ary assignment then binds role + process +
RACI level, which a single property never could.
**With:** FOAF for the actual people and teams behind the roles, and
`dcat:contactPoint` for ownership surfacing.

### SHACL — the checking layer
**What:** a shapes graph of constraints, written in RDF, run against the
data graph to produce a validation report.
**Why:** every locked decision that can be checked mechanically becomes a
shape: labels present, identifier policy followed, hierarchy integrity (one
parent per concept), controlled values, references present where alignment
is claimed.
**Constrained:** Core SHACL first; SHACL-SPARQL only where Core cannot
express the constraint. Validation reports are data, not verdicts — a
failing shape is a question for a human, not proof of a bad model.

### DCAT — publishing
**What:** `dcat:Catalog` → `dcat:Dataset` → `dcat:Distribution` /
`dcat:DataService`.
**Why:** the end state is a *published, versioned artifact*, not a file on
a disk. The dataset-vs-distribution distinction is load-bearing: one
dataset, many serializations (Turtle, JSON-LD, SHACL shapes, HTML docs).
**With:** DQV for quality measurements on data products, and
`dcterms:license` / ODRL where rights need expressing beyond a license URI.

### What to evaluate and set aside
- **W3C SIOC** (social/online-community vocabulary): not applicable to a
  process ontology — and a source field named `sioc` must not be confused
  with it (§2).
- **ODPS family** (Open Data Product Specification / ODPC / ODPV / ODPG):
  mapped for awareness (ODPC→DCAT, ODPV→SKOS, ODPG→RDF) but not adopted —
  the W3C stack covers the need without a second modeling idiom. Revisit if
  the data-product catalog work demands it.

---
## 5. Soundness — how to build an ontology you can trust

Soundness is not a standard you adopt; it is a set of checks you run on
every change. Each check below is a practice this build actually follows,
with the concrete action a newcomer takes. When a new failure teaches a new
check, add it here, dated, with the reason — never in chat history.

### 5.1 Identity — know what you are talking about before you relate it

Identity is evaluated before direction and before predicate meaning. A
relationship between two things you cannot identify is not a candidate; it
is a guess.

- **Slugs/IRIs are identity; labels are presentation.** A label suggests a
  candidate; it never confirms one. Never use a label as a join key, lookup
  key, RLS key, or API key.
- **Stable IDs survive renames.** When a label changes, the slug stays. The
  rename is recorded as overlay fields (`name`, `prior_name`,
  `name_change_note`, `scoped_historical_alias`) on the identity map — and
  after any regeneration of the identity map, those overlays are restored
  from the pre-regen version before the TTL is rebuilt, or the TTL silently
  reverts to stale labels.
- **Label-only identity needs an affirmative basis.** A label match alone
  identifies a target only with an affirmative citation, a strict two-way
  pair, or a recorded architecture decision. Anything weaker is a candidate,
  not an identification. **Exception (Phase 3, Rule 5):** for `core:precedes`
  siblings, structural nearness alone suffices — no added sequence assertion
  required. A non-sibling row needs an affirmative sequence citation or a
  two-way route.
- **Exclusion wording is never an identity route.** Exclusion, boundary,
  "owned by," and "may be handled by" wording is never a Rule 5 route. A slug
  named in that wording still identifies the concept; the row stays held
  because the wording is not a route.
- **No emission-time remapping.** A row's meaning is fixed at review time.
  Semantic plausibility discovered later never authorizes reclassification;
  hold the row and send the meaning correction to the source-workbook
  backlog.

### 5.2 Taxonomy — keep the tree well-formed

The taxonomy is a SKOS concept scheme: a controlled vocabulary of names,
not a class hierarchy of types. Every structural claim below is checked
mechanically (SHACL shapes, build scripts); the semantic ones need a human.

- **One parent per concept** (except roots). No cycles. The build fails on
  either.
- **Every process sits at a level L0–L6 with its parent shown.** No
  level-less nodes. Concepts without source IDs get minted slugs; they do
  not float.
- **One `skos:prefLabel` per language per concept; `@en` on every literal.**
  Untagged and tagged literals are different RDF terms — an untagged label
  is a data bug, not a stylistic choice.
- **Aliases go in `skos:altLabel`.** Local process IDs are preserved as URI
  slugs and recorded as `skos:notation`. External framework IDs attach via
  `dcterms:references` only — they never replace local IDs.
- **`skos:definition` is required on every concept**, plus a scope note on
  every approved concept. A concept you cannot define is a concept you do
  not understand; it stays parked.
- **Siblings are disjoint.** No two siblings claim the same primary
  activity. The parent test must hold: "this process is a way of carrying
  out [parent process]."
- **Never convert hierarchy levels into OWL classes mechanically.** That
  asserts logical commitments (disjointness, inheritance of restrictions) a
  naming hierarchy cannot support. Use OWL classes only where the business
  actually guarantees the commitment.

### 5.3 Definitions — say what each thing is, completely

Every authored definition must meet all ten points of the quality bar
(§6). In short: define the recurring activity and its intended outcome,
name the primary purpose (the decision or responsibility served, not the
department or data source), bound it with a scope note, keep one meaning
per term across the scheme, park future concepts instead of smuggling them
in, and record who wrote it, who approved it, and when. Human-authored text
passes through the same human gate as machine-triangulated text: nothing
merges on assumption.

### 5.4 Predicates — use verbs honestly

The four verbs are a promotion rule, not a thesaurus:

- **enables** — the source supplies a maintained operating base, required
  control, governed mechanism, capability, resource, or prerequisite
  condition that makes the target able to operate. Stored direction:
  `enables (S, T)` → `T core:enabledBy S` (the enabled thing is the
  subject). APPROVE stores `core:enabledBy` only for G3; G1a merges as
  duplicate evidence on `dependsOnOutputOf`; G1b is HOLD, no verb change;
  G2 emits no triple.
- **informs** — the source provides context the target uses.
- **dependsOnOutputOf** — the target consumes a specific output of the
  source.
- **requires** — the source cannot validly start, complete, proceed, or
  reach its controlled state without the target, its completed control, or
  its required condition.

Related verbs with adopted definitions: **assuredBy** (the assurance
activity performs a defined governance, compliance, quality, review, or
control-testing role over the assured thing — not merely supports,
documents, or feeds it); **constrainedBy** (stored from the bounded
activity/decision/outcome to the binding constraint source — not
informed-by, sequencing, governance/ownership, broad association, or
advice); **triggeredBy** (stored from the activity initiated by a defined
event, exception, monitoring outcome, change, referral, detection, or
handoff to the activity that generates the trigger condition — "feeds /
informs / supports / precedes" never become triggers without an invoking
event).

Locked verbs beyond the four: **precedes** / **follows** (sequence;
`core:precedes` siblings promote on structural nearness alone per Rule 5)
and **governedBy** (hierarchy; structural closeness alone never promotes —
recorded hierarchy exceptions are not precedents).

- **Never silently translate a verb.** If the source means "informs" and the
  pattern wants "requires," hold the row and send the meaning correction to
  the workbook backlog. Ambiguity stays visible as deferred; it is never
  resolved by rewording.
- **Predicate integrity:** the relationship must stand as stated, without
  silent conversion into another predicate. Judge each candidate row in
  Phase 3 order — identity first (including the Rule 5 sibling exception),
  then direction, then the locked per-verb definition above. A row failing
  its per-verb definition is held, its fact removed if currently emitted, no
  substitute emitted.
- **A row-level verdict is not architecture-decision evidence.** Only
  recorded architecture decisions qualify. The classifier column on review
  rows is triage only — never a decision basis.

### 5.5 Evidence — trace every claim to its ground

- **Every verdict carries its basis.** Approvals cite the evidence test
  (D:hamid-verdict): what was checked, what passed, who decided, when.
- **Ground every match type in the actual evidence file.** Never copy a
  match type from memory or from a sibling row's table. If the CSV says
  `nearness-only`, the table says `nearness-only`.
- **Approving an already-emitting row changes its evidence basis only.**
  Counts move only when a row changes bucket.
- **Held rows carry their disposition in the source itself** — the review
  CSV, the mapping document — not in a write-only side file. A hold states
  the row ID, the reason, and what would reopen it.
- **Supersessions are explicit and non-destructive.** Format: `HOLD /
  D:hamid-verdict / Reason / Supersedes<date>Approval`. The prior rationale
  is preserved in provenance. Ledger history is never rewritten — restore
  the original wording and append a dated note.
- **No guessed relationships, targets, citations, or match types.** If the
  evidence does not establish it, the cell stays empty and the row stays
  held.

### 5.6 Counts — make the arithmetic close, every time

- **Conservation is an equation, not a narrative.** Emitting + held +
  deferred + external-governance + structured-flow equals the total. Every
  figure in every governed doc is recomputed from the CSVs and gates before
  it is written. Never copy a number from memory, from a sibling doc, or
  from a closed PR's branch — a closed PR's numbers stay dead.
- **Every count change names four things:** the row ID, the old bucket, the
  new bucket, and the reason. No exceptions.
- **Held facts get knock-on checks:** holding a fact requires checking
  uniqueness and shared-fact effects before the counts are restated.
- **Figure-update discipline:** when a figure is wrong in one place, assume
  it is wrong in others. Grep the whole file for the old number; recompute
  every table total after every edit; ground every CSV-derived figure
  against the actual CSV; if figures do not reconcile, report the
  discrepancy and stop — never invent or adjust a number to make the
  arithmetic work. When a figure changes, sweep all governed docs in the
  package, not just the file being edited.
- **Pre-push verification:** before pushing a figure update, extract all
  figures from the doc and check each against its source.

### 5.7 Changes — prove safety before pushing

- **Every push gets a blast-radius proof.** Name the one safety fact the
  push depends on, prove it by running code against the real artifacts, and
  mark anything unproven as unproven — never write it up as settled.
- **Regression fixes start with a failing check.** Write the check, watch
  it fail, fix the cause, watch it pass. A fix without a failing check
  first is a guess.
- **Attack the premise, not the symptom.** When a gate fails twice on the
  same premise — or the checker is twice found never to have asserted what
  was assumed — stop writing one-off fixes. Census what the check does
  *not* cover, fix the premise, and record the new check here.
- **Re-pin evidence to the current `main` SHA before promotion.** A pin to
  a superseded commit is a stale pin; it proves nothing about the current
  tree. The re-pin is blocked on the promotion preconditions, not on
  closed PRs.
- **Migration PRs prove replacement, not deletion:** a per-predicate
  conservation ledger (emitted == planned, computed from the source at
  cutover time), a held-for-review report reconciled mention-by-mention,
  and a dry-run census reviewed before emission is approved.

### 5.8 Sampling — verify by spot-check, honestly

- Rule 6 samples come **only from promotions**, drawn with **seed 42**.
- Samples remain **pending until the owner reviews them**. A sample is not
  evidence until a human confirms it.
- **One wrong sample stops the pass.** A failed sample invalidates the
  batch; it does not get averaged away.

### 5.9 Review — let a human decide, and make it easy for them

- **Evidence package first.** No ontology application, promotion, or
  cleanup without the owner's verdict on the evidence. The owner is the
  senior reviewer of machine output: every batch ships with definitions,
  branch context, recommendations, and blank decision columns; verdicts are
  recorded row-level, per-row tables over summary lines.
- **Adversarial review before owner review.** Every implementation PR and
  design proposal gets an independent pass first (correctness, structural
  fit, evidence), with verdicts Act On / Consider / Noted / Dismissed.
  Reviewers never auto-apply changes.
- **One major update per PR.** One verb or the checklist — never stacked.
  Base every PR on the exact merged `main`; never restack from a sibling
  branch. Never open a fix, cleanup, or review-response PR without explicit
  go-ahead.
- **Present the status; let the owner decide.** Do not self-impose "DO NOT
  MERGE." Report holds and blockers plainly, fix what you can, report what
  you can't.
- **Decisions land in the decision log first**, dated, with the reason.
  The playbook learns the same week a practice is proven — in the section a
  teammate would look in, not in chat history.

---
## 6. Working agreements — how the team operates

### Read the playbook before deciding
Before making any modeling choice, check §2. If the decision is locked,
follow it; if you believe it is wrong, raise it with the owner and record a
dated amendment. Never silently override.

### Definition quality bar
Every authored definition must meet all ten — this is the merge gate for
human-written text, and the human gate from triangulation applies here too:
1. **Define, don't label** — state the recurring activity and intended
   outcome.
2. **Primary purpose** — the decision, outcome, or responsibility served;
   not the asset, department, or data source. No duplicated concepts for
   multi-purpose activities.
3. **Bounded** — a scope note is required on every approved concept;
   exclusions name an owner only when that owner is established in the
   taxonomy.
4. **Parent test** — "this process is a way of carrying out [parent
   process]" must hold.
5. **Sibling-disjoint** — no two siblings claim the same primary activity.
6. **Terminology-stable** — one meaning per material term across the scheme.
7. **Park, don't smuggle** — future processes in `parked_children`; no data
   fields, systems, KPIs, controls, or thresholds as concepts.
8. **Evidence-based** — high-quality references inform; nothing is copied
   verbatim.
9. **Planning baseline preserved** — backcasting compares against the
   approved plan and its contemporaneous assumptions, not a later
   reforecast.
10. **Provenance-clean** — record human authorship, the approver, and the
    date.

### Human-gated authoring workflow
Subject-matter text (definitions, scope notes) is authored in a controlled
workbook and merged only through a gate:
1. The reviewer fills the intake workbook and returns it on a reviewer
   branch — never directly to `main`.
2. A mechanical validator runs first (required fields, controlled values,
   no label collisions, no empty open questions on approved rows).
3. A semantic review follows: parent test, sibling disjointness,
   primary-purpose classification, terminology stability, no invented
   owners, no smuggled constraints.
4. Every doubt returns to the owner as a question. **Nothing merges on
   assumption** — the human gate applies to human-authored text exactly as
   it applies to triangulated text.

### Review like an adversary before asking for review
Every implementation PR and design proposal gets an adversarial pass before
the owner sees it: independent review angles (correctness, structural fit,
evidence), with verdicts Act On / Consider / Noted / Dismissed — reviewers
never auto-apply changes.

### Every push proves its safety
Name the one safety fact the push depends on, prove it by running code
against the real artifacts, and mark anything unproven as unproven — never
write it up as settled. After a repeated checker failure on the same
premise, **attack the premise** (census what the check does *not* cover)
instead of writing another one-off fix. Every regression fix starts with a
failing check, watched fail, then fixed, then watched pass.

### Migrations prove replacement, not deletion
Any migration that retires predicates or moves data ships with:
- a per-predicate conservation ledger (emitted == planned, computed from
  the source at cutover time — never from a stale snapshot);
- a held-for-review report reconciled mention-by-mention (emitted + held ==
  total), every held item carrying a recorded disposition in the source
  itself, not a write-only side file;
- a dry-run census (parseable / held / malformed counts) reviewed before
  emission is approved.
Ordering dependencies become structural assertions (fail fast on known
stale state), not list-order conventions. Reruns on unchanged input
reproduce identical output.

### The playbook learns the same week
A new best practice lands in the section a teammate would look in, dated,
with the reason — not in chat history. Re-check this file's freshness
whenever a step closes.

---
## 7. Worked example — the downstream process-map ontology

How the method played out on a real build. Illustrative, not normative: the
prescriptions are in §0–§6; this is what following them looked like.

**The build.** Source of truth: `downstream_process_map.json` in the
`aadehamid/enterprise-performance-model` repo — ~680 process nodes across
levels L0–L6. Consistency reference: the APQC Process Classification
Framework for Downstream Petroleum, v7.2.2 (official release, vendored with
attribution; delivered via PR #25). The published taxonomy reached 683
concepts, 681 broader links, 14,496 triples.

**Step 0 in practice.** Five of six repo-cited APQC IDs verified against the
workbook; one was stale across versions (10006 in the old mirror, 20085 in
v7.2.2) and corrected. The stale-ID catch is why the playbook says verify
against the workbook, not the mirror.

**Step 8 in practice (done early).** Seven APQC gap candidates, one at a
time: product recalls, human capital, data governance, fixed-asset project
accounting, remediation, external relationships, asset-maintenance depth.
Five in scope, two out — fixed-asset accounting (ERP-native, no ontology
hook) and external relationships (corporate affairs, no hook) got boundary
notes with revival triggers instead of silent omission. The standing rule
that emerged: cover enabling functions, not just the value chain, but only
where the ontology has a genuine hook.

**Steps 1–2 in practice.** URI base `https://w3id.org/lsc/ontology/`
(company-scoped, redirect-backed; chosen because the repo had already
rebranded once — person- and project-tied bases would not have survived).
Local codes preserved as `skos:notation` and slugified
(`CM 1.2.1.3` → `CM-1-2-1-3`); 11 ID-less stubs got minted slugs. The
label-governance rule (slugs are identity, labels are presentation) was
written after a regeneration script silently reverted hand-applied labels —
the tooling lesson is in §4's working agreements.

**Step 3 in practice.** SKOS-first: one ConceptScheme, broader/narrower,
prefLabel/altLabel, definitions on every concept. Candidate definitions
were triangulated from APQC and web sources — 1 adopted, 10 rejected at the
human gate, which is why the playbook insists reference text informs but is
never copied. Human authoring ran through the gated workbook workflow (§4);
a tree pass reparented Finance and Refining subtrees with minimal new
coordination nodes, tombstoned one node as `owl:deprecated` (never deleted),
and left one strategy-ownership question explicitly blocked rather than
forced into the wrong parent.

**Step 4 in practice (the relationship layer).** Every inter-process verb
was inventoried; each predicate got a locked business definition
(*requires*: the source cannot validly proceed without the target;
*assuredBy*: the assurance activity performs defined governance/oversight;
*constrainedBy*: stored from the bounded activity to the binding source;
*triggeredBy*: stored from the invoked activity to the trigger source;
*enabledBy*: a maintained, governed, necessary base that makes the target
able to function). Review ran one predicate family at a time, row by row:
direction first, definition test, verdict. Ambiguous rows were held for
source correction — never remapped at emission. The conservation ledger
(1,094 emitting / 209 held / 894 canonical facts) reconciled mention by
mention, and promotion stayed blocked until every verdict was recorded.
The locked rules in §1, Step 4 are the distilled output of this pass.

**The domain-question technique in practice.** Each L1 domain got one
primary question, used as the placement test for every new concept:
- Supply Chain Management — "what should move, be made, held, or
  replenished, where and when?" (orchestrates; does not own execution)
- Commercial & Marketing — "for which customer/market, under what offer,
  price, contract, or margin?" (market-facing value optimization; does not
  subsume physical operations)
- Refining — "how is feedstock transformed into compliant products?"
  (transformation; maintenance enables but does not refine)
- Midstream — "how are bulk feedstocks and products physically received,
  stored, transferred, and transported?" (movement and storage)
- Finance — "what is the financial position, performance, obligation,
  exposure, and control requirement?" (records, controls, settles, reports;
  business domains own the operational event)
- Process Excellence & IT — "how should the enterprise operate, and what
  technology enables it?" (does not own business outcomes)
- Human Resources — "what workforce is needed, and how is it planned,
  attracted, developed, rewarded, engaged, retained, and transitioned?"
- Legal & Corporate Communications — "what legal obligation, advice, or
  official internal message applies?"
- EHS & Government Reporting — "is this safe, environmentally compliant,
  correctly managed when events occur, and properly reported?"
- Shared Services — executes designated services; never replaces the
  accountable functional owner.

**Known source-material facts** (easy to get wrong; verify before modeling):
codes like `CM 1.2.1.3` are local notation, not APQC identifiers;
`officeLane` values are not declared disjoint; a JSON field named `sioc`
is unconfirmed — verify its business meaning before minting terms; 46
Order-to-Cash processes shipped with empty output sets and several
ownership gaps, resolved in Step 7 as explicit decisions, not guesses.

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

### Ontology IRI vs version IRI
Term IRIs never carry versions (`core:ProcessDefinition`, not
`core/1.0.0/consumes`). Each module is an explicit `owl:Ontology`
resource at a stable ontology IRI; the release is identified by
`owl:versionIRI`. Locked (Lock 3, 2026-09-18; reaffirmed by the Q1/Q3 IRI
fork correction 2026-09-22): module namespaces are
`https://w3id.org/lsc/ontology/modules/{module}`. The `…/ontology/core`
shorthand was proposed in error, never shipped, and is recorded on main
as rejected — do not use it.

```turtle
<https://w3id.org/lsc/ontology/modules/core>
    a owl:Ontology ;
    dcterms:title "LSC Core Process Ontology"@en ;
    dcterms:description "Governed definitions of LSC's business processes: identity, hierarchy, relationships, and lifecycle."@en ;
    owl:versionIRI <https://w3id.org/lsc/ontology/modules/core/1.0.0> ;
    owl:versionInfo "1.0.0" ;
    dcterms:issued "2026-09-22"^^xsd:date ;
    dcterms:creator "Hamid" ;
    dcterms:license <https://w3id.org/lsc/ontology/modules/core/license> .
```

Consumers who need currency use the ontology IRI; consumers who need
reproducibility pin the version IRI (or the versioned distribution
below). Term stability and release versioning are separate concerns —
do not mix them in one URI.

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
