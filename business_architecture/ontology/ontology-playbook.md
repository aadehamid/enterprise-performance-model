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

**How to read it.** §0–§4 are the method: foundations, the end-to-end
sequence, the locked policies, the standards guide, and the working
agreements. Follow them in order. §5 is the worked example — the
instantiation of the playbook on a real build. It stays in this document
by design: the example is how a reader checks that the guidance is real.
Read it when a prescription needs a concrete illustration, not as the main
text.

**How to maintain it.** When the method improves, update the guidance
section a teammate would look in, dated, with the reason — never in chat
history. When a build step completes, extend the worked example (§5) and
move any new durable decision into §2 (Policies). Never rewrite history:
correct with a dated amendment so the team can see what changed and why.

**Companion files:**
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
(§5).

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

---
## 3. Standards guide — why each standard earned its place

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
## 4. Working agreements — how the team operates

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
## 5. Worked example — the downstream process-map ontology

How the method played out on a real build. Illustrative, not normative: the
prescriptions are in §0–§4; this is what following them looked like.

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
`owl:versionIRI`:

```turtle
<https://w3id.org/lsc/ontology/core>
    a owl:Ontology ;
    dcterms:title "Enterprise Performance Model Core Process Ontology"@en ;
    dcterms:description "…"@en ;
    owl:versionIRI <https://w3id.org/lsc/ontology/core/1.0.0> ;
    owl:versionInfo "1.0.0" ;
    dcterms:issued "2026-09-22"^^xsd:date ;
    dcterms:creator <…> ;
    dcterms:license <…> .
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
