# Ontology playbook

**What this is.** A method for building a business ontology from scratch, step
by step, with the rules that keep it trustworthy and the reasons for each
rule. Anyone can follow it for their own domain.
**Owner:** The decision owner. **Built with:** Kailey and Claude Code.
**Started:** 2026-09-17. **Rewritten as a company-neutral method:** 2026-10-05.

## About this document

This playbook tells a team how to build an ontology, in order, from an empty
repository to a published, tested release. It comes from a real build: the
downstream oil and gas process-map ontology in this repository. That build
is the proof that the method works. It is not the subject of the document.

**Who it is for.** A data architect, ontologist or business analyst who must
turn a business's processes, parties and measures into a governed,
machine-readable model. You need to know what a triple is. Section 4 explains
each standard the method uses.

**How to read it.**

| Section | What it gives you | When to read it |
|---|---|---|
| §0 Foundations | The modeling discipline everything else assumes | Before you start |
| §1 The method | Steps 0 to 12, each with a purpose, a procedure and a "done when" gate | Step by step, as you build |
| §2 Policies | The rules, each with its reason | Before any modeling choice |
| §3 Promoting provisional data | How to turn rough source data into governed facts without corrupting it | When you build the relationship layer |
| §4 Standards guide | Which W3C standards to use, for what, and what to set aside | When you choose a vocabulary |
| §5 Soundness checks | The checks to run on every change | On every change |
| §6 Working agreements | How the team works together | When you set up the team |
| §7 Worked example | How the method played out on the downstream process-map ontology | When a rule needs a concrete case |
| Appendices | Parking, versioning, and an example predicate set | When you need the detail |

**How to maintain it.** This document changes only when the method changes:
a new rule, a better procedure, a check that caught a new kind of failure.
Add the change to the section a reader would look in, with the reason. A
decision about one project (an IRI, a scope call, a ruling on one row) does
not belong here. Record it in the project's decision log and worklog. A
project example can go in §7.

**In this repository** this rule is EPM-DEC-001-0024 (decided 2026-10-06),
which amends EPM-DEC-001-0002. Project decisions get an EPM-DEC-001 record
and a dated worklog pointer. This playbook changes only when the method
changes.

**Companion files in this repository.** These hold the worked example's
project record. You do not need them to follow the method.

- `step4/playbook/ontology-worklog.md`: the worklog. It has the plan table with
  step statuses, the step log and the dated decision journal.
- `../domain/decisions/`: the project's decision records (EPM-DEC-001).
- `step4/step4-decisions.md`: the project's relationship-layer design
  decisions.
- `step4/evidence-discipline.md`: the project's approved wording of the §3
  rules, with its counts and precedents.
- `competency-questions.md`: the project's competency questions.
- `lpg-projection/`: the property-graph projection guideline used in Step 12.

---

## 0. Foundations

These ideas come from Juha Korpela, "Building Semantics with Conceptual
Models" (Common Sense Data, 2026). Get them right and the rest of the method
is execution. Get them wrong and no tool will fix the result.

### 0.1 Context is the product

People used to fill gaps in data by asking each other what a field meant.
Agents cannot do that. Every consumer of your data, human or machine, needs
to know what it is reading. The ontology makes that knowledge durable, shared
and machine-readable.

Rule: build the foundation before anything consumes it, so that everything
built later connects to something trustworthy. A foundation with no
consumers yet is not unfinished. It is ready for them.

### 0.2 Model the business, not the storage

Conceptual modeling captures what the business means. Databases, data lakes,
pipelines and ETL are not part of it. The same model can inform solution
design later, but that is not its job.

Rule: never let a storage concern shape a concept. If a distinction exists
only because of a table, a feed or a system boundary, leave it out of the
conceptual model.

### 0.3 Two building blocks

A conceptual model has two kinds of thing:

1. **Entities**: things that exist in real life and that you have data about.
2. **Relationships**: associations between two entities.

That structure is what the model captures. Add attributes later. Teams that
start with attributes get stuck in them and lose the structure.

### 0.4 Entities are singular nouns

Name each entity as a singular noun: "Customer", not "Customers", and never
"Customer Data". Test each name in a plain sentence about how the business
works. The entity must be able to be the subject or the object. It will play
exactly those roles in your triples.

Rule: if you cannot write a plain business sentence with the entity as
subject or object, rename it until you can.

### 0.5 Every entity gets a definition

A definition answers "what do you mean by <entity>?" in simple business
language. Terms plus definitions are your semantics, and they become your
glossary. Capture a definition for every entity, with no exceptions, in
whatever tool you have.

### 0.6 Relationships are verbs

Name every relationship with a verb that says why entity A relates to
entity B in the real business. A shared foreign key is not a reason.

The verb pays off twice:

1. The verbs become the predicates of your triples.
2. Naming forces distinctions. "Owns" a bank account and "has access to" a
   bank account are two different relationships, and your consumers will
   depend on the difference.

Rule: if two verbs describe two different business realities between the
same pair of entities, model two relationships.

### 0.7 Subtypes where they matter

A subtype is a kind of something. A car is a kind of vehicle. Add subtypes
only where the business distinguishes the kinds in practice. Too much
generalization makes a model unreadable. When people talk about "two kinds
of accounts", model the two kinds and their supertype.

### 0.8 Declare, don't suggest

A mind map helps a workshop reach agreement, but it only suggests. A
conceptual model declares, and it stays true until the business changes.
That extra rigor is what lets you convert the model into an ontology. A mind
map left in a project folder is a model nobody finished.

### 0.9 From conceptual model to ontology

With the discipline above, the conversion is mechanical:

- Each entity becomes a class (`owl:Class`) or a SKOS concept (§2, Modeling
  discipline, says which).
- Each entity-relationship-entity statement becomes a triple.
- Each definition becomes `skos:definition`.
- Each noun becomes the preferred label (`skos:prefLabel`).
- Each subtype link becomes `skos:broader` or `rdfs:subClassOf`.
- Each verb becomes a predicate (`owl:ObjectProperty`).

Use the conceptual-modeling phase to build shared understanding with
business stakeholders before you write any syntax.

---

## 1. The method

Follow the steps in order. Each step has a purpose, a procedure and a "done
when" gate. Do not start a step until the previous gate is met. The order
matters: identity before taxonomy, taxonomy before relationships,
relationships before responsibilities, responsibilities before interfaces,
integration before validation, and validation before publication. The one
exception is Step 8, the scope review. Do it early, right after Step 0.

Two principles run through every step:

- **Write the exam before the coursework.** The business owner approves the
  competency questions (Step 1) before any modeling. They become the
  regression tests (Step 11). A question the model cannot answer is a
  modeling gap, not a bad question.
- **One step at a time, with a gate.** Finish a step before you start the
  next. Record each decision in the decision log as you make it. Update the
  source of truth with one consolidated proposal per step, not one change
  per decision.

### Step 0. Align the reference framework and survey existing ontologies

**Purpose.** Find what already exists before you invent anything. A
published reference framework becomes your consistency check. Existing
ontologies and code lists give you terms to link to.

**Procedure.**

1. Find the reference framework for your domain, such as an industry process
   classification. Adopt the official, current version. Check every cited
   element ID against the published workbook, not a third-party mirror or an
   older citation.
2. Store the framework in your repository with its attribution and license
   notice intact.
3. Compare every local node with the framework. Record each divergence as a
   boundary note with a reason. Do not hide divergences, and do not quietly
   conform to the framework.
4. Decide the direction once: your local model is the source of truth, and
   the framework is the check. Framework IDs attach by reference
   (`dcterms:references`). They never replace local IDs.
5. Survey public ontologies, vocabularies and code lists that cover parts of
   your scope. Look in four places: industry standards bodies (for code
   lists and data exchange standards), published domain ontologies (search
   GitHub, ontology portals, and Linked Open Vocabularies), legal and
   financial registries (for organizations and ownership), and W3C
   vocabularies.
6. Assess each candidate on five points: how much of your scope it covers;
   its license; whether it is maintained (date of the last release); whether
   it brings an upper ontology you would also have to take on; and its size.
7. Choose one treatment per source, and default to mapping:
   - **Map** (the default). Keep your own terms and link them to the external
     terms with `skos:exactMatch` or `skos:closeMatch`. You get the external
     source's authority without its structure.
   - **Import.** Bring the external terms into your ontology. Do this only
     when the source is small, stable and openly licensed, and you would
     otherwise rebuild it term for term.
   - **Ignore.** Record why, so nobody repeats the search.
8. Record each source in a register: what it covers, its license, its
   treatment, and the step where you will apply it. Apply each mapping at
   that step, not all at once.

**Done when:** every cited framework ID is checked against the published
source; every divergence has a boundary note; every surveyed source has a
recorded treatment and a target step.

**Pitfall.** Expect gaps. Public ontologies often cover one part of an
industry well (equipment, or the upstream end) and leave the rest bare. A
gap is a finding. Record it, and do not stretch a nearby ontology to fill it.

### Step 1. Foundations

**Purpose.** Fix the policies that everything else assumes. Changing them
later is expensive.

**Procedure.** Decide and record each of these:

1. **Competency questions.** Draft the questions the ontology must answer.
   Get the business owner to approve them, then lock them. They are the
   acceptance test for the whole build (Step 11).
2. **Data scope.** State what the ontology holds. The recommended rule:
   concepts, definitions, relationships, and public reference facts about
   real organizations and assets, each with a cited source and an as-of
   date. No records of events or transactions, and no observed values of a
   measure over time. Those belong to the systems that use the ontology.
   Section 2 gives the reason.
3. **Evidence order.** Rank your sources. Put the anchor organization's own
   filings and publications first, then direct peers, then
   industry-specific sources. Generic frameworks support a decision but
   never settle one alone.
4. **URI policy.** Choose a persistent base behind a redirect, scoped to the
   organization. Never tie it to a person (usernames change) or a project
   name (projects get renamed). Keep local IDs as `skos:notation`. Put no
   version number in term URIs.
5. **Language policy.** Declare the primary language and tag every literal.
   Allow one `skos:prefLabel` per language per concept, and require
   `skos:definition` on every concept.
6. **Version policy.** Use semantic versioning per module and per release.
   Deprecate, never delete. Appendix B has the detail.
7. **License policy.** Decide before you publish anything. A closed artifact
   can be opened later. An open one cannot be closed again.
8. **Module policy.** Split the ontology into modules with one-way
   dependencies and no cycles. Plan a separate module for reference
   instances of real organizations, so the core stays neutral and reusable.
9. **Consumers.** Record who will consume the ontology and whether any
   consumer is active yet. Release rules depend on it: while no consumer is
   active, you can retire provisional data in one release.
10. **Target formats.** If the ontology will be projected into a labelled
    property graph (Step 12), adopt that projection's design rules now:
    Rules 1, 2, 3 and 5 of the guideline in `lpg-projection/`, and for its
    Rule 4 the qualified-relation option (4a), unless every tool in your
    pipeline reads RDF 1.2. Rules adopted late force you to remodel.

**Done when:** all ten policies are recorded with their reasons; the
business owner has approved and locked the competency questions.

### Step 2. Identity normalization

**Purpose.** Give every node a stable identity before you say anything
about it.

**Procedure.**

1. Keep existing local IDs as `skos:notation` and derive URI slugs from
   them.
2. Mint a slug for each node that has no ID. A slug is the URL-safe
   identifier you create where none existed.
3. Fix the rule: slugs and IRIs are identity, and labels are presentation.
   Never use a label as a join, lookup, access-control or API key. Labels
   change. Identity does not.

**Done when:** every node has a stable HTTP URI; nothing in the build
identifies a node by its label.

### Step 3. SKOS taxonomy

**Purpose.** Build the controlled vocabulary: the hierarchy of names, with
labels and definitions. It is a vocabulary of names, not a class hierarchy.
Use SKOS first, not OWL.

**Procedure.**

1. Create one `skos:ConceptScheme`. Use `skos:broader` and `skos:narrower`
   for the hierarchy, `skos:prefLabel` and `skos:altLabel` for names,
   `skos:notation` for local IDs, and `skos:definition` on every concept.
2. Write definitions to the quality bar in §6.
3. Collect candidate definitions from references, but send each one through
   a human gate. Reference text informs a definition. Never copy it
   verbatim.
4. Do not turn each hierarchy level into OWL classes and subclasses. That
   asserts logical commitments, such as disjointness and inherited
   restrictions, that a naming hierarchy does not support.

**Done when:** every concept has a definition and a label; every concept
except the scheme's top concepts (`skos:topConceptOf`) has exactly one
parent; the mechanical checks (labels present, hierarchy integrity, no label
collisions) pass.

### Step 4. The relationship layer

**Purpose.** Turn the verbs between concepts into governed relationships:
the predicates of your triples.

**Procedure.**

1. List every verb used between concepts. Write a definition for each
   predicate you will emit before you look at any rows. Appendix C has an
   example set.
2. Review one predicate family at a time, one row at a time. For each row,
   settle identity first, then direction, then the definition test, then
   the verdict.
3. Hold a row whose meaning is unclear. It emits no fact and keeps its
   reason, and it reaches the source author only if the release gate puts it
   on the source-correction backlog (below). Never change its meaning when
   you emit it.
4. Keep a conservation ledger: emitted plus held plus deferred equals the
   total, reconciled row by row.
5. Run the promotion script last, after every verdict is recorded.

Section 3 is the full discipline for this step.

**Done when:** every row has a recorded verdict (APPROVE, STAND or HOLD);
the ledger reconciles; the evidence gate passes; the promotion preconditions
(re-pin, attestation, regression run, blast-radius proof) are met. A HOLD
completes the row for this step: it emits no fact, and its reason is
recorded. Whether it goes on the source-correction backlog is a separate
decision (below).

**Then release the first module.** First decide which held rows go back to
the source author for correction, and record that list: the
source-correction backlog. Release the core module only when every row on
that list has a fresh verdict after its correction. The fresh verdict may be
HOLD again; the row then stays out of the release with its reason recorded.
Held rows that are not on the list stay held with their recorded reason.
They emit nothing, and they wait in a backlog for a later release. Then
release the core module: serialize the governed facts, retire the
provisional layer in one release, and add the first version header. If you
release before the backlog rows are settled, they lose their provisional
form and need a second release. Build a small SHACL slice first (Step 9) so the release is checked
by shapes, not only by scripts. Appendix B covers release mechanics.

**Working the source-correction backlog.** A backlog of a few hundred rows
goes fastest as one answer register, built and checked in batches:

1. Draft an answer for every backlog row in one register: the corrected
   verb or target, or "no relationship", the stored fact, and one sentence
   the source author would put in the source's scope note. Flag the rows
   that need the owner's judgement. The owner approves the register as a
   whole and answers the flagged rows.
2. When an approved fact runs opposite to its row's direction, first add a
   mirror raw verb ("provides input to" for "uses input") to the direction
   table and to the correction tool's known verbs, with a decision record.
   Do not move the assertion to the other process's row: moving it
   renumbers every later row.
3. Correct the source in place. Change a row's verb or target where it
   stands; never add, remove or move a relationship, because row IDs
   usually follow position. A correction tool should refuse, before it
   writes anything, a missing, duplicated or converging segment, a verb the
   direction table does not know, or a target containing the cell's
   delimiter. A "no relationship" answer is a fresh HOLD: leave the row as
   it is, keep it held with the answer as its reason, and emit nothing.
4. Add each answer's sentence to the source's scope note. It becomes the
   affirmative citation that rule 5 of Section 3 asks for.
5. Rebuild, re-pin, then re-run the whole pipeline in a copy. Adopt its
   output only if every changed row belongs to the batch, and keep the
   review notes the pipeline does not reproduce. Files that list the rows
   of one verb must move with a corrected verb.
6. Check each batch against the approved register in the evidence gate:
   exactly the batch's rows, each decided field, the stored fact, the
   sentence in the published scope note, and the corrected relationship as
   the classifier will read it. Require the published taxonomy to equal
   the pinned copy. One such check can replace many per-row hold checks.
7. Watch the grouping heuristics. When a corrected row's reverse is still
   held, a heuristic that merges "enables" into an output dependency can
   turn the corrected verb into another predicate. Use a row-level verdict
   to keep the approved predicate (rule 11).

### Step 5. Organizations, roles and responsibilities

**Purpose.** Say who is responsible, and describe the real organizations the
model refers to. Roles are positions people hold, not people. The same
person can be Accountable for one process and only Informed on another.

**Procedure.**

1. Model roles as `org:Role`. Bind role, process and RACI level with an
   explicit n-ary `ResponsibilityAssignment` node. A single property cannot
   carry a three-way binding. RACI is design-time responsibility.
2. Model party roles (customer, supplier, carrier) on the relationship or
   account, not as subclasses of the party. The same organization can be a
   customer in one deal and a supplier in another.
3. Put public reference instances of real organizations and sites in their
   own module (for example `ref-<company>`). Cite a source and an as-of date
   for each fact.
4. Keep a legal entity apart from a reporting segment. A segment is how a
   company reports. A subsidiary is a separate legal entity, and it may
   publish its own filings.
5. Model control and ownership between legal entities as a relation of its
   own, not as `org:subOrganizationOf`, which means a unit inside one
   organization. If the link carries a share or a date, use a
   qualified-relation node (§2, Modeling discipline).
6. Map organization concepts to a public registry vocabulary where one
   exists (Step 0).
7. Normalize the source's role strings through a role register: one row
   per string as the source spells it, mapped to one or more roles. Merge
   two strings only when they differ in case, plural, punctuation or "&".
   Split a compound string ("Planner / Scheduler") into its roles, keep a
   qualifier ("for crude") on the assignment, not in the role, and model a
   team as a role with a scope note. A build script checks the register
   against the source, so a new or changed string stops the build. Put a
   possible misspelling or an unexplained acronym to the owner. Do not
   correct it yourself.
8. Emit one assignment per source entry and per role the entry names, and
   keep the source's role text on each assignment. Reconcile entries in
   with assignments out in a conservation table: the entries, plus the
   extra roles that compound strings add, equal the assignments, at every
   RACI level.
9. Get a recorded scope before you test the gate. "Every in-scope process"
   needs a decision on which processes are in scope. Processes outside it
   go on the source author's backlog. Do not invent RACI for them.

**Done when:** every in-scope process has its RACI assignments, under a
recorded scope; no responsibility is implied by position in the
hierarchy; every reference instance cites its source.

### Step 6. Interfaces and provenance

**Purpose.** Separate what is planned from what happened.

**Procedure.**

1. Model planned inputs and outputs on the process definitions. Take
   them only from a source field whose meaning the owner has confirmed. A
   field with an unclear name (a misspelled acronym, for example) gets a
   question to the owner before any term is named after it. Carry each
   input and output as a governed literal until a use case needs to trace
   one flow as a node of its own. Processes the source gives no inputs or
   outputs go on the source author's backlog. Do not draft them.
2. Define the bridge from a definition to its runs with P-Plan, the PROV-O
   extension for plans and their steps. A run of a process is a
   `prov:Activity`. Never type a definition as an activity: the recipe is
   not the meal.
3. Decide who holds the run records. Under the data scope rule (Step 1),
   the ontology defines the pattern and the consuming systems hold the
   runs.
4. Use PROV-O's second job, trust, to record which source asserted a
   mapping, when, and under what authority.
5. Ship the pattern as shapes, not new terms: a run is a `prov:Activity`
   with one qualified association whose `prov:hadPlan` points at a live
   process definition. Add a shape that fails any definition typed as an
   activity, and an example run that passes, so a consumer can test its
   own records.

**Done when:** no definition is typed as an occurrence; the definition-to-run
pattern is defined; every occurrence a consumer records can link to its
definition.

### Step 7. Cross-model integration

**Purpose.** Link the models to each other: processes to value streams,
capabilities, systems, measures and data products.

**Procedure.**

1. Bring back the overlay layer you parked (Appendix A), one overlay at a
   time. Overlays reference process nodes. They never duplicate them,
   because a value stream cuts across the hierarchy and cannot be a parent.
2. Model measures as definitions: what a named measure is, its population,
   its grain, and what it is not. Cite the public filing or source that uses
   each measure. Values stay out (Step 1). Before you define them, classify
   them:
   - **A KPI is a designation, not a kind of measure.** A measure is a KPI
     only when the business names it as one of the few measures of a stated
     objective, with a target and an accountable owner. Most measures
     on a team's list are operational metrics. Record the target and owner
     before you call a measure a KPI. Mark an operational metric a KPI
     candidate only where the evidence makes it a strong one, such as a
     headline measure the company reports or a peer targets.
     Never invent a target or an owner to fill the field.
   - **Classify each measure by kind, with tests in a fixed order.** No
     formula, unit or grain: a tracker or report, or not a measure at all
     for a capability request. Fires only on a
     condition: an alert. Set by a market the business cannot influence: a
     market indicator; computed from market prices and a planning model to
     start or rank a decision, with no performance target: a
     decision-support indicator. Actual or plan against
     a plan, forecast, version or history for one period: a plan-variance
     diagnostic. Otherwise an operational metric, unless designated a KPI.
     Record the test that assigned each class and the reason.
   - **A comparison is part of a variance measure, and only a view of any
     other.** "Demand against forecast" is defined by its comparison.
     Utilization against plan, or against five years of history, is the
     same measure asked against different references, not a second one.
   - **Name the basis.** A ratio names its denominator (calendar-day or
     stream-day capacity; net or gross throughput). A definition that
     changes between filings gets a version, not a silent edit.
   - **People become roles.** The people on a measure list become the roles
     they hold, defined by plan type and horizon. No person's name enters
     the ontology.
   - **Link measures to processes as context.** A link says which process a
     measure informs. It does not certify the process.
3. Apply the external mappings you assigned to this step in Step 0.
4. Resolve the gaps earlier steps exposed, such as empty output sets or
   missing owners, one at a time, each as a recorded decision. Do not invent
   an owner to fill a gap. "Unowned, parked" is better than a guess.
5. Define only what a source describes. An item an overlay names without
   describing (a data product, a system) gets a note saying its definition
   waits for its owners, never a definition written from its name. A shape
   requires one of the two, never both.
6. Say what each placing link claims, in a form a query can read. Mark each
   property that places a measure, data product or system on a process as
   as certification (the link names one end's owning
   process) or context (it says only where one thing is used or placed with
   another). Only an owning link certifies.
7. Separate a measure from its published series. A series is one form of a
   measure, identified by what it is built from: region, legs and their
   ratio, and what it leaves out. Store the recipe, never the prices. Two
   series that differ in any of these are two series of one measure.
8. Rank the sources. Give every cited source a tier from the project's
   evidence order, so that when two sources of one concept disagree, the
   best tier wins, and a query can say which.
9. Write down the rules for the graph's consumers: how a catalog row binds a
   measure (both ends defined first), what an agent may answer from the
   graph alone, and what it must refuse, such as computing a value or
   building a benchmark from its legs. Each rule names the terms it relies
   on, so a test can check that they exist.

**Done when:** every integration gap has a decision: linked, or explicitly
parked.

### Step 8. Scope review (do it early)

**Purpose.** Decide what is in and out before the foundations harden.

**Procedure.** Take each candidate area one at a time. Put it in scope only
if it has a real hook into the ontology's purpose: a value-chain link, a
RACI feed, a data-product dependency. Give each out-of-scope area a
boundary note with a reason ("ERP-native, nothing depends on it") and a
revival trigger.

**Done when:** every candidate has an in or out call, a reason and a
revival trigger.

### Step 9. SHACL validation

**Purpose.** Turn every rule that can be checked mechanically into a shape.

**Procedure.**

1. Build a small slice before the first release: labels present, IDs
   present, no provisional namespace left, references resolve. If you
   project to a property graph, add meta-shapes for its design rules (Step
   12).
2. Then add, in order: every relationship fact links to its source
   evidence; controlled values come from their allowed lists; no definition
   is typed as an occurrence.
3. Use SHACL Core first. Use SHACL-SPARQL only where Core cannot express the
   constraint.
4. Treat a validation report as data. A failing shape is a question for a
   person, not proof of a bad model.
5. Test the shapes' coverage, not only their results. A test that fails
   when a code-list property has no shape finds the properties a
   hand-written shapes file missed. Prove each shape can fail: change one
   value in a copy of the data and require a violation.
6. Shapes written after a release run against that release without
   changing it. They join the release's own shapes at the next release.
7. Run every module's shapes together on the whole graph, in one test. A
   shape that targets too broadly (every subject of `skos:inScheme`), or a
   value one module's shape forbids in another module, passes each module's
   own tests and fails only there.

**Done when:** the shapes run against the data with zero unexplained
violations.

### Step 10. Publication

**Purpose.** Ship a published, versioned artifact, not a file on a disk.

**Procedure.**

1. Describe the release with DCAT: a catalog, a dataset, and its
   distributions. One dataset has many serializations (Turtle, JSON-LD,
   SHACL shapes, HTML docs).
2. Record the module versions, issued and modified dates, and a changelog
   on every release.
3. If consumers will validate against the release, ship a release package
   with a manifest: immutable version, checksums, and the dependencies.
4. Give every module the same package shape (Turtle, JSON-LD, shapes, a
   DCAT record, a changelog and a manifest with SHA-256s), built by one
   script. A module that depends on another names that module's version,
   and the build fails if that version does not exist. Appendix B covers
   release candidates, the cut and the next major.

**Done when:** the catalog resolves; the current release is retrievable as
versioned distributions.

### Step 11. SPARQL regression tests

**Purpose.** Prove the ontology keeps answering its exam.

**Procedure.**

1. Convert the Step 1 competency questions into SPARQL.
2. Re-run coverage after each module lands, not only at the end.
3. Run the full suite on every release. A failing test is a regression or a
   recorded, deliberate change. It is never a surprise.
4. Where a question depends on a system outside the ontology (a catalog
   page, an assistant), test only the part the graph supplies.
5. Start the harness early, before most questions can pass. Give each
   question a status: answerable (its queries run), partial (the graph
   part runs and the rest is named), or waiting on a named step or
   decision. A module's pull request moves its questions to answerable.
6. A query either must return rows or, marked "(must be none)", must
   return none. Test the harness with mutated graphs: remove the fact a
   query needs and require it to fail.
7. Check a query's population against the whole before you trust its
   count. A filter on one concept kind silently drops concepts that carry
   no kind. Count the population the query selects, the rows it returns
   and the rows it leaves out, and confirm they add up.
8. Pin the counts a harness test checks by hand, and expect each new query
   to change them. A test that pins how many queries fail on an empty
   graph, or which question serves as the example of a waiting one, must
   move with every module that adds a query or answers that question.

**Done when:** every competency question passes on the published release,
or is parked by a recorded decision.

### Step 12. Property-graph projection (optional)

**Purpose.** Load the finished ontology into a labelled property graph, such
as Neo4j, for applications that query in Cypher. The Turtle files stay the
master copy.

**Procedure.** Follow the conversion guideline in `lpg-projection/`, with
its Rule 4 set to option 4a. Apply its design Rules 1, 2, 3 and 5 from the
first release (Step 1, item 10). For Rule 4, give a relationship its own
properties with a qualified-relation node (option 4a, the guideline's
default; §2, Modeling discipline), not an RDF 1.2 reifier (4b), unless every
tool in the pipeline reads RDF 1.2. A qualified-relation node loads as an
ordinary node, so the guideline's flatten queries are not needed. Its pipeline runs here:

1. **Check.** Run the meta-shapes and the data shapes. Any violation stops
   the build.
2. **Reason.** Run an OWL 2 EL reasoner once, upstream. A property graph
   cannot reason.
3. **Serialise.** Write two sorted N-Triples files: `loadable.nt`, the
   asserted data, and `inferred.nt`, the inferred `rdf:type` and
   `rdfs:subClassOf` triples, built as the difference between the
   reasoner's output and its input. Keeping them in two files keeps
   assertions and inferences apart.
4. **Load.** Load the schema, the shapes, `loadable.nt` and `inferred.nt`
   in a fixed order, with names and multi-valued properties generated from
   the ontology, never written by hand. Inside Neo4j the asserted and
   inferred triples are merged, because the loader keeps no graph names. If
   the graph itself must tell them apart, use the guideline's Add-on F.
5. **Verify.** Run SHACL validation inside the graph with zero violations,
   a round-trip diff back to RDF (against the two files together) with zero
   differences, and a determinism test: two loads in different orders
   produce the same graph hash.

Materialize inverse relations before the load if consumers need them. OWL 2
EL has no inverse properties, and a property graph does not infer them.

What the loader and the reasoner do. Guideline v2.1 did not say these; v2.2 does:

- **Pick the loader's naming mode by what validates.** With Neo4j's n10s
  plugin, SHACL validation inside the graph needs a namespace-aware graph.
  Use the SHORTEN mode with fixed prefixes, not MAP. In SHORTEN, each
  name is the prefix plus the local name, so two terms cannot share a name
  (Rule 5).
- **Run the full shapes upstream and a subset in the graph.** Check every
  shape with pySHACL, SHACL-AF included, over the asserted and the
  inferred triples before the load. Load only the constraints the loader
  can run, and record which ones it leaves out and why. An empty
  round-trip diff then shows the graph holds the triples that passed the
  full shapes. Prove the in-graph check can fail: remove one value in the
  graph and require a violation.
- **Filter the reasoner's declarations.** The OWL API writes declarations
  such as `owl:NamedIndividual` and `owl:Class` into the reasoner's
  output. They are not inferences about the domain. Drop any triple whose
  object is an OWL or RDFS built-in before you write `inferred.nt`.
- **Compare values, not spellings, in the round trip.** A plain literal
  equals an `xsd:string` literal. Integers return as `xsd:long` and
  decimals as `xsd:double`. A language tag may come back inside the
  string. Refuse, at build time, any source value that would not survive
  the trip: a string that ends like a language tag, or a decimal whose
  value, printed as a double, is not its own lexical form (0.64 passes;
  0.1000000000000000055 does not).
- **List the release's known rule gaps, and fail on a stale list.** When a
  released module breaks a design rule that only its next release can
  fix, name the gap and its fix in the pipeline. Fail on any gap not
  listed, and on a listed gap that no longer occurs.
- **Make the committed report go stale.** Record a fingerprint of the
  loaded files and of every shape file in the report. The check script
  rebuilds them, so a changed input fails the check until someone reruns
  the pipeline. CI runs the check and serialise steps. The reason step
  needs Java, and the load and verify steps need a Neo4j container, so
  they run on a workstation.
- **Pin the tools by version and checksum.** Record the Neo4j, plugin and
  reasoner versions in the manifest, and the download URL and SHA-256 of
  each plugin jar in the pipeline's README.

**Done when:** the three checks in the verify step pass on the published
release.

---

## 2. Policies

Each policy states a rule and the reason for it. A project records its own
applications of these rules in its decision log. A policy changes only when
the method improves, by a dated amendment with the owner's agreement.

### Source of truth and scope

- **Model your own business. Use references as checks.** Your local source
  (process map, system inventory) is the source of truth. A reference
  framework checks it. Record each deliberate divergence as a boundary note.
- **Reuse public ontologies by mapping, not importing.** Link your terms to
  external terms with `skos:exactMatch` or `skos:closeMatch`. Import only a
  small, stable, openly licensed source that you would otherwise rebuild
  term for term. Reason: importing usually brings an upper ontology or a
  large model you must then keep consistent, and the extra structure answers
  none of your competency questions.
- **The ontology defines. It does not record.** It holds concepts,
  definitions, relationships, and public reference facts with a source and
  an as-of date. Stable attributes of an entity (a refinery's capacity, an
  ownership share) are reference facts. Event records ("Customer A bought 5
  barrels") and observed measure values ("the crack spread was $5") are not.
  Reason: records and values change every day and belong to the systems
  that compute and store them. An ontology that holds them becomes a second,
  stale copy of those systems.
- **Cover enabling functions, not only the value chain**, but only where the
  ontology has a real hook (a RACI feed, a data-product dependency).
- **Rank evidence and cite every fact.** Use the evidence order from Step 1.
  A fact without a citation stays out.

### Identity

- **URIs are persistent and scoped to the organization**, never to a person
  or a project. A rename then changes one redirect, not every identity.
- **Keep local IDs. Never replace them with reference IDs.** Local codes
  become `skos:notation` and the basis of URI slugs. Reference IDs attach by
  `dcterms:references`.
- **No version segment in term URIs.** Identity survives a definition
  change. Versions sit on the ontology header (`owl:versionInfo`,
  `owl:versionIRI`). Appendix B shows the pattern.
- **Slugs and IRIs are identity. Labels are presentation.**
- **No blank nodes in released data.** Every node that something can point
  at gets an IRI, including n-ary and qualified-relation nodes. Reason: a
  blank node has no stable identity across builds, so a consumer cannot
  reference it and a property-graph load cannot reproduce it.

### Language and versioning

- **Tag every literal with its language.** Untagged and tagged literals are
  different RDF terms, and SPARQL treats them as different values.
- **Semantic versioning per module and per release. URIs never change.**
  Deprecate with `owl:deprecated` and `dcterms:isReplacedBy`. Never delete.
  Appendix B has the detail.

### Licensing

- **Decide the license before you publish anything.** If the ontology
  describes competitively sensitive operations, proprietary is the safe
  default.
- **Respect each reference's license.** Carry its attribution on every
  distribution. Reference its IDs freely. Quote sparingly. Never republish
  whole reference branches as your own.

### Modules

- **One-way dependencies, no cycles**, checked in CI. Cross-module use is by
  URI reference, never by redefinition.
- **One module owns each domain's concepts.** Do not create a `customer`
  module next to a `party` module. A domain is a view across modules.
- **Reference instances live in their own module.** Keep instances of real
  companies, sites and assets out of the core modules. Reason: the core then
  stays company-neutral and reusable, and the reference module can be
  versioned as filings change.

### Modeling discipline

- **SKOS first for taxonomies.** A naming hierarchy is a controlled
  vocabulary, not a class hierarchy.
- **Separate definitions from occurrences.** A process definition is not an
  activity that happened. Reserve `prov:Activity` for runs.
- **Use an n-ary or qualified-relation node when a relationship has its own
  properties.** A link that carries a share, a date, a level or a source
  becomes a node with its own IRI that points at both ends. Examples are the
  RACI `ResponsibilityAssignment`, `org:Membership`, and PROV-O's qualified
  relations. Reason: plain RDF, plain SHACL and every common tool handle the
  pattern today, and it loads into a property graph as an ordinary node.
  RDF 1.2 reifiers do the same job but need tooling that is not yet
  widespread (§4). A link the business tracks as a thing in its own right
  (its own lifecycle or identity, referred to by other records) is a domain
  class instead, such as a `Transfer`. The arcs that define a qualified
  relation, including an inverse such as `prov:qualifiedAssociation`, do not
  make it one.
- **Give every property one kind and a concrete range.** It is an object,
  datatype or annotation property, never a bare `rdf:Property`, with a
  concrete `xsd` type for literals.
- **Declare cardinality in SHACL for every property.** `sh:maxCount 1` means
  one value. No maximum means a list.
- **Split a field that mixes dimensions.** One source field holding
  "event-driven", "monthly" and "tactical" holds three dimensions (operating
  mode, cadence, planning level). Model three controlled fields, and record
  "unspecified" honestly where a value is missing.
- **Keep lifecycle, governance status and hold status separate.** A concept
  can be a Candidate and on hold at the same time. One status chain cannot
  say that.
- **Add aliases selectively.** `skos:altLabel` is a live search commitment.
  Make a former name an alias only if it is unique, accurate and useful.
  Keep other former names in history (an annotation property), not search.
- **A lexical match is not a resolution.** A matching label proposes a
  candidate. Resolve a target only on a stable ID or approved contextual
  evidence. Otherwise defer it, with the raw phrase, the candidates and a
  review trigger.
- **Give every source mention a disposition.** Only mentions that resolve
  to a concept become relationship triples. Others become a parked future
  concept, a structured value, an external reference, a dropped mention, or
  a deferred ambiguity, each recorded.
- **Classify by primary purpose, not by location or asset.** Write one
  primary question per domain ("what is the financial position,
  performance, obligation and exposure?" for Finance) and use it as the
  placement test for every new concept.
- **Do not declare disjointness without evidence.** Categories stay
  non-disjoint until the business guarantees they are.

### Scope and change control

- **Slot every new concept into the existing hierarchy.** No floating nodes.
- **Decisions go in the decision log. The source of truth changes by one
  consolidated proposal per step.**
- **Park, don't smuggle.** Future concepts go in an explicit parked list
  (Appendix A). Do not model data fields, systems, KPIs, controls or
  thresholds as process concepts.
- **Confirm an ambiguous source field before you name a term after it.** A
  field called `sioc` is not the W3C SIOC vocabulary until someone confirms
  its business meaning.
- **Do not invent ownership to fill a gap.**

### Decisions and this playbook

- **The playbook holds the method. The decision log holds the project's
  decisions.** A project decision gets a decision record and a dated worklog
  entry. When a decision also improves the method, add the improvement here,
  in the same change. In this repository this is EPM-DEC-001-0024,
  decided 2026-10-06.

---

## 3. Promoting provisional data without corrupting it

Most builds start from rough source data: a workbook, a spreadsheet, an
export. A common pattern is to capture it first as provisional annotations
in a staging namespace (for example `intake:`), then promote it to governed
properties. The staging layer may be the only copy of facts such as "which
process uses which input". A careless promotion corrupts those facts
silently: the triples look fine but no longer say what the business said.
The rules below prevent that.

### The eleven rules

1. **Pin all evidence to one commit.** Every evidence file records the
   commit it was built from and the hashes of its inputs. Before release,
   re-pin to the current approved commit. Build and evidence must cite the
   same commit.
2. **Regenerate review packages after the taxonomy changes.** After any
   rename, move or reclassification, rebuild the package from the pinned
   baseline and diff it field by field against the old one.
3. **Carry an approval forward only for an unchanged row.** An approval
   given on one version carries to the next only if the row is identical on
   every evidence field. The one exception: a change that only adds a
   stable identifier or a source citation, with source, verb, target and
   disposition unchanged. Record each use of the exception.
4. **Labels propose candidates. They never prove identity.**
5. **Structural nearness is not evidence by itself.** Two processes being
   siblings is enough for a sequence relation between them ("A precedes
   B"). For every other relation (enables, governed by, requires, assured
   by, depends on) it must be combined with independent evidence: the
   target named in the source's definition or scope note, a strict two-way
   mention, or a recorded architecture decision.
6. **Sample automatic promotions, and stop at the first wrong one.** Sample
   `max(10, ceil(5%))` per domain with a fixed, recorded seed. A person
   reads each sampled row's definitions. One wrong resolution stops the
   line: fix the rule and re-run. Never patch the single row.
7. **Conserve every source predicate and every mention.** A ledger accounts
   for every staging triple and every relationship mention: emitted, held,
   merged or redirected. Prove conservation with arithmetic.
8. **Store one direction per fact. Derive inverses.** "A precedes B" and "B
   follows A" are one fact. Mirrored rows inflate the fact count and hide
   contradictions.
9. **Keep row-level evidence outside the graph at first.** Which source
   verb, which row and which test promoted a fact can live in versioned CSV
   files beside the build. Bring provenance into the graph later, if a
   consumer needs it, as qualified-relation nodes.
10. **Release on one commit, with a fresh consumer attestation.** The
    release build, the evidence and the consumer-impact scan cite one
    commit. Right before release, confirm again who consumes the ontology.
    A stale attestation is not an attestation.
11. **Promotion never changes source meaning.** The pipeline may emit, hold,
    defer or reclassify a disposition. It may not replace a verb, invent a
    target or reinterpret meaning. Corrections go back to the source through
    a reviewed authoring change.

### Why each rule exists

These failures happened in the worked example. Each one taught a rule.

- **Stale baselines approve different data (rules 1 to 3).** Between two
  package versions, 53 rows had their target labels renamed underneath
  them. Only the commit pin and the field-by-field diff showed it.
- **Labels drift and collide (rule 4).** One process was renamed during the
  build, and another label named two different concepts in two branches. A
  pipeline that joined on labels would have misresolved both without any
  error.
- **The first evidence pass was wrong and confident (rule 5).** It counted
  terminology notes as citations, any back-link as two-way confirmation,
  and hierarchy closeness as evidence. The fix was not to correct the bad
  rows. It was to write checks that fail on the broken premise, watch them
  fail, and then fix the implementation.
- **Zero staging triples proves deletion, not migration (rule 7).** Only a
  ledger that accounts for every triple proves the facts moved.
- **Mirrored rows inflate facts (rule 8).** In the worked example, 386
  mentions collapsed into 193 facts once mirrors were merged.
- **Mixed-commit evidence is invalid (rule 10).** A scan run on one commit
  says nothing about a build cut from another.
- **A script must not author meaning (rule 11).** A mistyped source verb
  ("assures" where the business meant "satisfies") cannot be repaired by a
  script that picks a nicer predicate. That would hide an authoring error
  inside the ontology.

### Standing triggers

- **Attack the premise.** If a gate fails twice on the same premise, or a
  check is twice found never to have tested what you assumed, stop writing
  fixes. List what the check does not cover and fix the premise.
- **Write the failing check first.** Every regression fix starts with a
  check you watched fail on the broken state.
- **Review adversarially first.** Every evidence package gets an
  independent review pass (Act On / Consider / Noted / Dismissed) before
  the owner sees it.

### How to review a predicate family

Review one predicate at a time, in four phases.

1. **Fix the definition.** Write it before you look at rows. It must be
   falsifiable: you must be able to read a row and say "this fails". A
   definition every row passes is not a definition.
2. **Build the batch.** Pull every row that asserts the verb. For each, show
   the source and target by slug, both definitions, the raw verb, the
   evidence tier and the proposed disposition. The reviewer reads the
   definitions, not the pipeline's recommendation.
3. **Give each row a verdict.** Settle identity first (stable ID or label
   only, and the rule 4 and 5 route), then direction, then the definition
   test. Then record one verdict:
   - **APPROVE**: the row meets the definition, and the fact is stored.
   - **HOLD**: the row fails the definition or the evidence is too weak. No
     fact is emitted, and the reason is recorded. The row joins the
     source-correction backlog only by a recorded decision (Step 4, "Then
     release the first module"); a hold left off that list keeps its reason
     and waits for a later release. A hold is never a remap to another
     predicate.
   - **STAND**: the row was already emitting correctly, and the review
     confirms it. Counts change only when a row changes bucket.
4. **Sample and reconcile.** Sample per rule 6. Reconcile: every row has a
   verdict and the ledger balances.

Two citation rules apply to every verb:

- **Boundary wording is never a route.** "Excludes X", "owned by" and "may
  be handled by" say where a boundary lies. They do not establish the
  relationship a verb asserts.
- **A row verdict is not an architecture decision.** Only a recorded
  architecture decision counts as decision evidence.

**Why one verb per pass.** A reviewer who holds one definition applies it
consistently. Mixing verbs lets the definitions drift into each other.

**Why a hold is not a remap.** The source author chose the verb. If it is
wrong, the fix belongs in the source, as a reviewed change.

---

## 4. Standards guide

Each entry says what the standard is, why it belongs in the build, and what
it is not for. The rejections matter as much as the adoptions.

### RDF: the grammar
**What:** the subject-predicate-object triple model.
**Why:** every other standard here is a vocabulary written in RDF.
**Not for:** carrying meaning alone. RDF without a vocabulary has no words.

### SKOS: the taxonomy and the mappings
**What:** `ConceptScheme`, `prefLabel`, `altLabel`, `broader`, `narrower`,
`notation`, and the mapping properties `exactMatch` and `closeMatch`.
**Why:** a process hierarchy is a vocabulary of names. SKOS gives labels,
aliases, hierarchy, and links to external sources without claiming each node
is a class.
**Rejected:** converting hierarchy levels into OWL classes mechanically.

### Dublin Core Terms: describing sources
**What:** `dcterms:title`, `references`, `license`, `provenance`, `source`.
**Why:** the ontology constantly describes its sources: which framework
version, which filing, which license.
**Not for:** describing the domain itself.

### RDFS and OWL: the schema layer, used sparingly
**What:** classes, properties, subclass and subproperty, domain and range,
equivalence, disjointness, inverses.
**Why:** you need some real classes (process definition, responsibility
assignment, named KPI) and precise property kinds.
**Constrained:** RDFS and OWL infer. They do not validate. Domain and range
create new triples; they do not check data. Assert disjointness or
cardinality only where the business guarantees it. Keep to the OWL 2 EL
profile if you will project to a property graph.

### PROV-O and P-Plan: plans, runs and trust
**What:** `prov:Entity`, `prov:Activity`, `prov:Agent`, and P-Plan's plans
and steps.
**Why:** two jobs. P-Plan and PROV-O separate a planned process from its
runs. PROV-O also records who asserted what, when, and on what authority.
**Rejected:** typing taxonomy concepts as `prov:Activity` by default.

### ORG: organizations and roles
**What:** `org:Organization`, `org:Role`, `org:Membership`, sites and
units.
**Why:** RACI needs roles, not people, and reference instances need
organizations and sites. `org:Membership` is the model for qualified
relations.
**With:** FOAF for the people and teams behind roles, `dcat:contactPoint`
for ownership, and a registry vocabulary for legal-entity relations, such as
GLEIF Level 2 for accounting consolidation, by mapping.

### SHACL: the checking layer
**What:** shapes, run against the data to produce a validation report.
**Why:** every rule that a machine can check becomes a shape, including
cardinality and the property-graph design rules.
**Constrained:** Core first. Reports are questions for a person.

### DCAT: publishing
**What:** catalog, dataset, distribution, data service.
**Why:** the end state is a published, versioned artifact with many
serializations.
**With:** DQV for quality measurements, and ODRL where rights need more
than a license URI.

### Property-graph projection
**What:** loading the ontology into a labelled property graph (Neo4j with
the n10s plugin) by a fixed pipeline.
**Why:** some applications query in Cypher. The projection gives them the
ontology without making the graph database the master copy.
**Constrained:** a property graph does no OWL reasoning. Reason upstream and
load the results.

### Reusing external ontologies
**What:** public domain ontologies, registry vocabularies and industry code
lists.
**Why:** they give your terms external authority and help others integrate
with you.
**Constrained:** map by default (§2). Check the license, the maintenance
status and any upper ontology before you rely on one.

### What to evaluate and set aside
- **RDF 1.2 reifiers.** They attach properties to a single triple. As of
  October 2026, the W3C specification is a Candidate Recommendation. Apache
  Jena 6.1.0+ and RDF4J 6.0.0+ read and write it; rdflib and pySHACL do not.
  Use qualified-relation nodes (§2) unless every tool in your pipeline
  supports it.
- **W3C SIOC.** An online-community vocabulary. It does not apply to a
  process ontology.
- **The Open Data Product Specification family.** The W3C stack covers the
  need without a second modeling style. Revisit if data-product catalog work
  demands it.

---

## 5. Soundness checks

Soundness is a set of checks you run on every change. When a new failure
teaches a new check, add it here with the reason.

### 5.1 Identity

- Settle identity before direction and before predicate meaning. A
  relationship between two things you cannot identify is a guess.
- A label suggests a candidate. It never confirms one.
- When a label changes, the slug stays. Record the rename as overlay fields
  on the identity map (current name, prior name, note, scoped alias). After
  any rebuild of the identity map, restore those overlays before you rebuild
  the Turtle, or the Turtle silently reverts to old labels.
- A label-only match identifies a target only with an affirmative citation,
  a strict two-way pair, or a recorded architecture decision. The sibling
  sequence case in rule 5 is the one exception.
- Boundary wording is never an identity route.
- A row's meaning is fixed at review time. If a better reading appears
  later, hold the row and record the better reading as its reason. A
  source correction goes through the source-correction backlog (Step 4).

### 5.2 Taxonomy

- Exactly one parent per concept, except the scheme's top concepts
  (`skos:topConceptOf`), which have none. No cycles. The build fails on
  either.
- Every concept sits at a level, with its parent shown.
- One `skos:prefLabel` per language per concept, and a language tag on every
  literal.
- Aliases go in `skos:altLabel`. Local IDs are `skos:notation`. External IDs
  attach by `dcterms:references`.
- Every concept has `skos:definition`. Every approved concept also has a
  scope note.
- Siblings are disjoint in purpose. The parent test holds: "this is a way
  of carrying out [parent]".

### 5.3 Definitions

Every authored definition meets the ten-point quality bar in §6. Text a
person wrote goes through the same human gate as text a tool collected.
Nothing merges on assumption.

### 5.4 Predicates

- Judge each row against its predicate's written definition (Appendix C has
  examples).
- Never translate a verb silently. If the source says "informs" and the
  pattern wants "requires", hold the row with that reason. A source
  correction goes through the source-correction backlog (Step 4).
- A row that fails its definition is held. If it was emitting, its fact is
  removed. No substitute fact is emitted.

### 5.5 Evidence

- Every verdict records what was checked, what passed, who decided, and
  when.
- Take every match type from the evidence file, never from memory or a
  neighboring row.
- Held rows carry their disposition in the source record itself: the row
  ID, the reason, and what would reopen it.
- A supersession is explicit and keeps the earlier reason. Never rewrite
  ledger history. Append a dated note.
- If the evidence does not establish something, the cell stays empty and
  the row stays held.

### 5.6 Counts

- Conservation is an equation. Recompute every figure from the source files
  before you write it.
- Every count change names the row ID, the old bucket, the new bucket and
  the reason.
- When a figure is wrong in one place, assume it is wrong in others. Search
  every governed document for the old number, and recompute every table
  total.
- If the figures do not reconcile, report the gap and stop. Never adjust a
  number to make the arithmetic work.

### 5.7 Changes

- Every push names the one safety fact it depends on and proves it by
  running code against the real artifacts. Mark anything unproven as
  unproven.
- A migration proves replacement, not deletion: a per-predicate ledger, a
  held-items report reconciled row by row, and a dry-run count reviewed
  before emission.
- Re-pin evidence to the current commit before promotion.
- Turn ordering dependencies into assertions that fail fast on known stale
  state. A rerun on unchanged input reproduces identical output.

### 5.8 Sampling

- Draw samples only from promotions, with a fixed, recorded seed.
- A sample is pending until the owner reviews it.
- One wrong sample stops the pass. It is not averaged away.

---

## 6. Working agreements

### Check the policies before deciding
Before any modeling choice, check §2 and the project's decision log. If a
rule seems wrong, raise it with the owner and record a dated amendment.
Never override it silently.

### Definition quality bar
Every authored definition meets all ten points:

1. **Define, don't label.** State the recurring activity and its intended
   outcome.
2. **Primary purpose.** Name the decision, outcome or responsibility served,
   not the asset, department or data source.
3. **Bounded.** Give every approved concept a scope note. Name an owner in
   an exclusion only when that owner exists in the taxonomy.
4. **Parent test.** "This is a way of carrying out [parent]" holds.
5. **Sibling-disjoint.** No two siblings claim the same primary activity.
6. **Stable terms.** Each material term has one meaning across the scheme.
7. **Park, don't smuggle.** Future processes go in a parked list. No data
   fields, systems, KPIs, controls or thresholds as concepts.
8. **Evidence-based.** Good references inform the text. Nothing is copied.
9. **Baseline preserved.** A comparison (for example, actual against plan)
   uses the approved plan and its assumptions at the time, not a later
   forecast.
10. **Clean provenance.** Record who wrote it, who approved it, and when.

### Human-gated authoring
Subject-matter text is written in a controlled workbook and merged through a
gate:

1. The author fills the workbook and returns it on a review branch, never
   directly to the main branch.
2. A validator runs first: required fields, controlled values, no label
   collisions, no open questions on approved rows.
3. A person reviews the meaning: parent test, sibling disjointness, primary
   purpose, stable terms, no invented owners.
4. Every doubt goes back to the owner as a question.

### One change per pull request
Every change goes through a pull request, and a reviewer merges or holds it.
Keep one major update per pull request. Base each one on the current main
branch. Review it adversarially yourself before you ask for review. Report
holds and blockers plainly, and let the owner decide.

### Decisions need the owner's recorded words
Nothing is decided or approved until the owner has recorded it. A merge
alone does not decide anything. Quote the owner's words in the decision
record.

Under the owner's decisions, write only what the owner's saved words say
and the option text the owner chose. Everything the agent adds (names it
proposed, rules it applies, detail from an analysis the owner pasted but
did not adopt word for word) goes under what follows, as the agent's. A
reviewer reads the decisions against the saved words line by line, and an
added phrase reads as the owner's.

The owner can delegate open questions in recorded words. A delegated
decision names the delegation and its evidence, so the owner can audit or
reverse it. Some things stay with the owner even then: a statement of fact
only the owner can make (who consumes the ontology), and the approvals the
versioning policy reserves for the owner (a major release).

### A process description says only what its source says
A description in the process map is the definition of the process. When it
cites a filing, every claim in it must be in that filing, with the item
that holds it. A fact with no primary source stays out of the description,
however plausible.

### Merging a branch with main
When a merge conflicts in a table, merge the row: keep one row per key,
carrying both sides' changes. Keeping both sides of a table conflict
duplicates rows. Keeping both sides is safe only for entries that are
separate by design, such as decision-log groups and index rows; then put
the rows back in their order.

### The playbook learns the same week
When a practice is proven, add it to the section a reader would look in,
with the reason. Re-check this document whenever a step closes.

---

## 7. Worked example: the downstream process-map ontology

How the method played out on a real build. This section illustrates. The
rules are in §0 to §6. The project's own decisions are in the decision
records (`../domain/decisions/`, EPM-DEC-001) and `step4/step4-decisions.md`.
Current counts and step statuses are in the worklog.

**The build.** The source of truth is
`business_architecture/business_process/downstream_process_map.json`, about
680 process nodes on levels L0 to L6. The reference framework is the APQC
Process Classification Framework for Downstream Petroleum, v7.2.2, stored
with attribution. The anchor company for evidence is Marathon Petroleum
(MPC), using its SEC filings and public materials, then U.S. refining peers'
filings.

**Step 0.** Five of six repository-cited APQC IDs matched the workbook. One
was stale across versions (10006 in an old mirror, 20085 in v7.2.2). That
catch is why the method says to check against the published workbook.

The survey of public ontologies (2026-10-05) found no public business
architecture or process ontology for downstream oil and gas. Public oil and
gas ontologies cover upstream (OSDU, offshore production) or plant equipment
(ISO 15926 and its successor IDO, ISO/FDIS 23726-3). Five sources each cover
a piece of the scope, and each is mapped, not imported (EPM-DEC-001-0023):

| Source | Covers | Step |
|---|---|---|
| GLEIF Level 2 ontology | Accounting consolidation between legal entities | Step 5 |
| PIDX standards | Downstream product and terminal codes | Step 7, Customer product line |
| Open Energy Ontology | Energy carriers and fuels | Step 7 |
| IOF Supply Chain ontology | Supply chain and logistics | Step 7, if logistics is in scope (in EPM, logistics came in with MPC-P01, and the mapping is parked until a concept layer for logistics assets or movements, or a consumer that needs IOF terms, EPM-DEC-001-0064) |
| FIBO | Ownership and control | Only if GLEIF is not enough |

**Step 8 (done early).** Seven APQC gap candidates were reviewed one at a
time. Five went in. Fixed-asset project accounting (ERP-native, no ontology
hook) and external relationships (corporate affairs, no hook) went out with
boundary notes and revival triggers.

**Steps 1 and 2.** The URI base is `https://w3id.org/lsc/ontology/`. It is
scoped to the organization and meant to sit behind a redirect, because the
repository had already been renamed once. No redirect is registered: the base
is a placeholder until a domain is decided (EPM-DEC-001-0039). Module namespaces follow
`https://w3id.org/lsc/ontology/modules/{module}`. Local codes became
`skos:notation` and slugs (`CM 1.2.1.3` became `CM-1-2-1-3`), and 11 nodes
without IDs got minted slugs. The labels-are-presentation rule was written
after a regeneration script silently reverted hand-applied labels.

The data scope rule came later, during planning for Step 5
(EPM-DEC-001-0005). Public facts about MPC, its refineries and MPLX are in
scope as reference facts. Records of what happened and observed measure
values are not.

**Step 3.** One concept scheme, with definitions on every concept. Of the
candidate definitions collected from APQC and web sources, the human gate
adopted 1 and rejected 10. Human authors wrote the rest through the gated
workbook. A tree pass moved the Finance and Refining subtrees, deprecated
one node (never deleted), and left one ownership question openly blocked
rather than forced under the wrong parent.

**Step 4.** The relationship layer was built one predicate family at a time
under the rules in §3. Appendix C lists the predicates and their
definitions. The project's design choices for this step are recorded in
`step4/step4-decisions.md`. They include the namespace, the release mode for
the staging layer, the three-way split of a mixed horizon field, the
three-dimension lifecycle, the selective alias policy, and the six
disposition types. Held rows went to a source-correction backlog
(`step4/source-workbook-backlog.md`), and the `core` 1.0.0 release follows
their correction (EPM-DEC-001-0013).

**The domain-question technique.** Each L1 domain got one primary question,
used as the placement test:

- Supply Chain Management: "what should move, be made, held, or
  replenished, where and when?"
- Commercial & Marketing: "for which customer or market, under what offer,
  price, contract, or margin?"
- Refining: "how is feedstock transformed into compliant products?"
- Midstream: "how are bulk feedstocks and products physically received,
  stored, transferred, and transported?"
- Finance: "what is the financial position, performance, obligation,
  exposure, and control requirement?"
- Process Excellence & IT: "how should the enterprise operate, and what
  technology enables it?"
- Human Resources: "what workforce is needed, and how is it planned,
  attracted, developed, rewarded, engaged, retained, and transitioned?"
- Legal & Corporate Communications: "what legal obligation, advice, or
  official internal message applies?"
- EHS & Government Reporting: "is this safe, environmentally compliant,
  correctly managed when events occur, and properly reported?"
- Shared Services: executes designated services and never replaces the
  accountable functional owner.

**How Steps 5 to 12 ran.** The owner delegated the build choices for
Steps 5 to 12 to the agent (EPM-DEC-001-0028). The owner kept the
decisions the method reserves for the owner: scope, the meaning of a source
field, and every major release. Each choice below has its decision record.
Steps 5, 6 and 9 to 12 ran on 2026-10-13. Step 7 ran on 2026-10-18 and
2026-10-19.

**Step 5, organizations and roles.**

- *Vocabulary* (EPM-DEC-001-0030). The `organization` module holds
  `orgm:ResponsibilityAssignment`, one process, one role and one RACI
  level, with the source's role text and a source. It also holds a RACI
  level code list and `orgm:ControlRelationship`, a qualified-relation node
  with a share, an as-of date and a source.
- *Role register* (EPM-DEC-001-0031). The process map spells roles 91
  ways. The register maps each string to one or more of 60 roles.
  `build_roles.py` checks the register against the source and writes
  `roles.ttl`. Likely misspellings and unexplained acronyms went to the
  owner as open questions.
- *Assignments* (EPM-DEC-001-0032). `build_assignments.py` turns the 913
  RACI entries on 153 processes into 940 assignments: 27 extra roles come
  from compound strings. `raci-conservation.csv` reconciles every RACI
  level. Nothing is inferred from the hierarchy.
- *Scope.* The owner set the RACI scope to the 153 processes with RACI in
  the source. The other live concepts are the source author's backlog.
  Competency questions 3 to 5 became answerable.
- *Reference instances* (EPM-DEC-001-0033). `ref-mpc` holds MPC and MPLX,
  MPC's control of MPLX (about 64 percent, as of 2025-12-31) as a control
  relationship node, MPC's three reportable segments, and its 13
  refineries as sites. Each fact cites MPC's FY2025 10-K with an as-of
  date. Refinery capacity waits for Step 7's measure pattern.
- *Domains.* The process map's `responsibleDomain` values looked like org
  units. The owner decided they are business domains, and split "Commercial
  & Marketing" by branch. No org units were made for them (EPM-DEC-001-0038).

**Step 6, plans and runs** (EPM-DEC-001-0034, EPM-DEC-001-0038).
`provenance/run-shapes.ttl` defines the run pattern with no new terms: a
`prov:Activity` whose qualified association has `prov:hadPlan` pointing at
a live process. A shape fails any core concept typed as an activity. The
process map had a field named `sioc`. The agent did not guess its meaning.
The owner confirmed it is SIPOC, and core 2.0.0 carries its inputs and
outputs as `core:plannedInput` and `core:plannedOutput`: 362 inputs and
219 outputs on 153 processes. The other 504 live processes have none. The
owner made them the source author's backlog.

**Step 7, integration** (EPM-DEC-001-0040 to 0043, 0046).

- *The KPI seed.* The owner's list of a planning team's measures was the
  seed, not a list of KPI categories (EPM-DEC-001-0040, amending 0017). The
  list stays outside the repository. Its four personas became planning
  roles, and no person's name entered the ontology; a test checks every
  tracked file against hashed name tokens.
- *Most of the list is not KPIs* (EPM-DEC-001-0042). The owner said so,
  and the evidence agreed. Of 41 measures (32 from the list, 8 that MPC
  publishes, 1 from industry practice), 15 are operational metrics, 7
  market indicators, 6 plan-variance diagnostics, 6 trackers or reports, 2
  alerts, 2 KPIs, 1 a decision-support indicator and 2 future capabilities. The
  only KPIs are MPC's two annual-bonus refining measures, because only they
  have a published target and owner. Six operational metrics are KPI
  candidates, among them crude utilization and margin capture. MPC itself
  files prices and crack spreads under "Market indicators", which settled
  that class.
- *The module* (EPM-DEC-001-0043). The `kpi` module holds the 41
  definitions with their kind, grain, basis, aliases, "not to be confused
  with" links, personas and process links. It took regression from 9 to 17
  answerable questions, and was released as 1.0.0 on the owner's approval.
- *Market Data and Commercial Risk* (EPM-DEC-001-0046). The owner defined
  both domains and named the Risk Group as owner, Market Data
  provisionally.
- *The measure list's source* (kpi 1.0.1). The owner named the product
  the list belongs to, Value Chain Optimization Decision Support and
  Visualization (VCO DSV); the source keeps its IRI and carries that title.
- *MPC process-map proposals* (EPM-DEC-001-0047, 0048). The owner accepted
  the proposals and said to apply them to the map. Each landed in its own
  pull request: Midstream as fuels logistics (`MS 1`), the Refining IDs and
  turnaround coordination children (`RF 1`), scope notes on retail nodes,
  environmental compliance credits kept apart from the clean-fuel tax
  credit, renewables by reuse of existing processes, affiliate fees, and the
  transfer coverage check. Two gaps the checks found went to the owner as
  proposals; the owner said to address them, Marathon's public information
  first, and each is one step in its own pull request: movement losses and
  gains (CM 1.1.3.7.13, merged) and renewable feedstock traceability
  (CM 1.2.5.1.5, merged). A third, the quality of transferred intermediates, was
  answered on 2026-10-19: CM 1.2.5.1's description now covers intermediates
  received as feed from another refinery (EPM-DEC-001-0051). P06 waits for the customer work. P09 waited for
  the owner's approval of the measure categories, which came on 2026-10-19
  (EPM-DEC-001-0050), and is applied: two value-stream processes name
  five measures, each with its relationship and MPC source.
- *The overlays* (EPM-DEC-001-0053 to 0062, 2026-10-19). Each layer came
  in as its own module: data products (15 defined, 33 parked because the
  portfolio names them without a description), the two value streams, the
  map's systems through a spelling-only register, the office lanes, five
  crack-spread series of one measure from MPC's 10-K and CME Group, the
  placement kinds, the source tiers, the full APQC element list, the
  consumer rules and the measure populations. Regression went from 17 to
  34 answerable questions; the nine still waiting all wait on the owner.
- *What the whole-graph gate caught* (EPM-DEC-001-0065). Every module's
  own tests passed, yet running all the shapes together found a lane shape
  that targeted every concept in any scheme and rules that gave
  `dcterms:source` a text value. Both were fixed where they started.
- *What the reviews caught.* Most review holds in Step 7 were attribution:
  a record listed the agent's wording (role names, a rule, detail from a
  pasted analysis) under the owner's decisions. Working agreements now say
  where that wording goes. On the process map the holds were source
  fidelity: a description said more than its filing (customer terms given
  to third parties, a "physical or apparent" analysis no cited standard
  states, "oils and fats" where the filing names soybean oil). Each was cut
  back to what the source says.

**Step 9, controlled values** (EPM-DEC-001-0035). The release slice in
`core` 1.0.0 checked `conceptKind` against its own list and the other
code-list values only as `skos:Concept`.
`validation/controlled-values.ttl` requires each code-list property to
take its values from its own list. Its coverage test found two properties
with no shape. `core` 2.1.0 carries each fact's evidence in the graph,
one node per fact with the direct triple kept, and its release shapes
hold the controlled-value shapes and the evidence-link shapes
(EPM-DEC-001-0044).

**Step 10, publication** (EPM-DEC-001-0029, EPM-DEC-001-0037,
EPM-DEC-001-0038, EPM-DEC-001-0044, EPM-DEC-001-0045, EPM-DEC-001-0043).
Nine releases, each issued on the owner's written approval. The first
four were built as candidates first; the last five (`core` 2.1.0,
`organization` 2.0.0, `ref-mpc` 1.1.0, `kpi` 1.0.0 and `kpi` 1.0.1) were
cut directly on the owner's approval of each cut:

| Release | What it holds | Builder |
|---|---|---|
| `core` 1.0.0 | The taxonomy, the 640 canonical facts, the scoped sequences and eight code lists | `release/build_core.py`, from the pinned evidence |
| `organization` 1.0.0 | The vocabulary, the roles and the RACI assignments | `release/build_module.py` |
| `ref-mpc` 1.0.0 | MPC and MPLX reference instances; requires `organization` 1.0.0 | `release/build_module.py` |
| `core` 2.0.0 | The business domain list, planned inputs and outputs, two ranges; `core:responsibleDomain` deprecated, its values kept | `release/build_core_next.py`, from the released 1.0.0 |
| `core` 2.1.0 | One evidence node per canonical fact, the controlled-value and evidence-link shapes, a rights statement | `release/build_core_2_1.py`, from the released 2.0.0 |
| `organization` 2.0.0 | The decision owner's role answers: three roles deprecated into their successors, their assignments moved; requires `core` 2.1.0 | `release/build_module.py` |
| `ref-mpc` 1.1.0 | The same reference instances; requires `organization` 2.0.0 | `release/build_module.py` |
| `kpi` 1.0.0 | 41 measure definitions classified by kind, the planning personas and the processes each measure informs; requires `core` 2.1.0 | `release/build_module.py` |
| `kpi` 1.0.1 | A patch: the measure list's source is named, Value Chain Optimization Decision Support and Visualization (VCO DSV) | `release/build_module.py` |

Deprecating a property made 2.0.0 a major. Before approving it, the owner
stated that no one used the ontology yet. The 2.0.0 cut found that the
candidate had copied 1.0.0's `dcterms:modified`. The builder now sets it
at the cut. The owner decided not to host the namespace, because the
domain may change, and to keep it as a placeholder. Under the delegation,
nothing is registered with w3id.org either, and Step 10's "catalog
resolves" gate is parked (EPM-DEC-001-0039).

**Step 11, regression.** `regression/` holds one SPARQL query per tested
part of the 44 competency questions and a status for each question. It
started on `core` 1.0.0 with 5 answerable. On `core` 2.0.0 with the
organization module, 9 were answerable, 5 partial and 30 waiting. With
the kpi module (2026-10-18), 17 are answerable, 6 partial and 21 waiting.
With the data-product module (2026-10-19), Q7 became partial: 17, 7 and 20.
With the value-stream module (2026-10-19), Q10 became answerable: 18, 7 and 19.
With the system module (2026-10-19), Q6 became answerable: 19, 7 and 18.
With the lane module (2026-10-19), Q9 became answerable: 20, 7 and 17.
Q15, the same-word test, then became answerable across the modules: 21, 7 and 16.
With the market-data module (2026-10-19), Q31 and Q34 became answerable: 23, 7 and 14.
With the placement kinds (2026-10-19), Q37, Q38 and Q39 became answerable: 26, 5 and 13.
With the source tiers (2026-10-19), Q44 became answerable: 27, 4 and 13.
With the full APQC element list (2026-10-19), Q11 became answerable, and Q40 and Q43 count by their graph part: 30, 1 and 13.
With the consumer rules (2026-10-19), Q35, Q41 and Q42 became answerable: 33, 1 and 10.
With the measure populations (2026-10-19), Q28 became answerable: 34, 1 and 9. Every waiting question then waits on the decision owner.
The waiting questions are the meaning owners (Q17) and the customer questions (Q19 to
Q26); all wait on the decision owner. The first query for Q8 filtered on the "process"
kind. It reported all 463 process-kind concepts as having no inputs or
outputs, because the 153 processes that do have them carry no kind.
Counting the query's population against the whole caught it.

**Step 12, projection** (EPM-DEC-001-0020, EPM-DEC-001-0036).
`projection/pipeline.py` runs the guideline in `lpg-projection/` with
Rule 4 set to option 4a, qualified-relation nodes, because the build's
Python tools cannot read RDF 1.2. It uses Neo4j 2025.06.2, n10s 2025.06.1,
APOC, and ELK through ROBOT 1.9.10. The first run on `core` 1.0.0 found
three things guideline v2.1 did not cover, and one defect. v2.2 now covers
all three:

- n10s would not import the shapes in MAP mode ("The graph is not
  namespace aware"), so the pipeline names terms in SHORTEN mode.
- n10s cannot run every shape, so a subset runs in the graph and Step 1
  runs all of them.
- ELK's output carried OWL API declarations, which the pipeline drops.
  That leaves no inferences, because the ontology is SKOS-first.
- The defect: `ref-mpc`'s source nodes linked their URLs through
  `dcterms:source`, which core's source shape forbids. It was fixed in
  `ref-mpc`.

Core 1.0.0 gave `earlierProcess` and `laterProcess` no range, which breaks
Rule 1. The pipeline listed both as release gaps until core 2.0.0 added the
ranges. The run on core 2.1.0, organization 2.0.0 and `ref-mpc` loads
2,811 nodes and 14,865 relationships, with no SHACL violation in the
graph, an empty round-trip diff and equal hashes for two load orders
(`projection/projection-report.json`).

**Source facts that are easy to get wrong.** Codes like `CM 1.2.1.3` are
local notation, not APQC identifiers. Office-lane values are not declared
disjoint. A JSON field named `sioc` is SIPOC, as the owner confirmed. The `responsibleDomain` values are business
domains, not org units. Several Order-to-Cash processes have empty output
sets, to be resolved in Step 7 as explicit decisions.

---

## Appendix A. Parked items

A parked item is something you deliberately defer. Record it with what it
would cover, the competency questions it would answer, a "done when", and a
revival trigger. Never delete a parked item. Revive it or close it with a
decision. The worked example's two parked items show the pattern.

### Constraints module (worked example, parked 2026-09-18)

Not modeled yet. The removed competency questions are kept so a later pass
can use them unchanged:

- What is a Constraint, a Threshold, a Breach and a Binding?
- Does a KPI have a constraint, or is it one?
- Who owns a constraint family (HSE, quality, commercial, planning), and who
  owns the KPI?
- Can more than one KPI reuse the same limit value without copying its
  meaning?
- How does a breach occurrence (something that happened on a date) relate
  to the constraint definition?

Done when: KPIs reference constraints and do not subclass them.
Revival trigger: a consumer needs to reason about limits, not only KPIs.

### Value-stream, capability, activity, event, decision, KPI and data-product layer (worked example, parked 2026-09-22)

Not in `core` 1.0.0. These layers will exist, but as overlays over the
process backbone, not as a second hierarchy inside it. A value stream cuts
across the tree (Order to Cash touches commercial, finance, credit and
legal), and every concept has exactly one parent, so a value stream cannot
be a parent. The existing JSON overlays already follow this pattern: they
reference process nodes through `linkedProcessIds`
(`business_architecture/business_process/value_stream_*.json`,
`business_architecture/schema/value_stream.schema.json`), and the data
product portfolio links processes to data products
(`business_architecture/business_process/data_product_portfolio.json`).

Where each layer goes:

- Domain, value stream, stages, and capabilities as views: overlays.
- Capability kind: a classification value in `core`. Actual business
  capabilities become a future class linked to processes.
- Business process: `core` 1.0.0.
- Activity: a future decomposition below L6.
- Events: occurrences, defined by the Step 6 pattern and recorded by
  consumers.
- Decisions: future decision modeling.
- KPI: the `kpi` module, as definitions only.
- Data products: the portfolio JSON now, ontology links when promoted.

Done when: a consumer needs one of these layers. Then promote that overlay,
one at a time, against the released backbone.
Revival trigger: someone asks for, say, the Order-to-Cash value stream end
to end, and the backbone alone cannot answer. The worked example revives
this layer at Step 7 (EPM-DEC-001-0017). *2026-10-18:* the KPI layer is
revived as the `kpi` module (EPM-DEC-001-0043), released as 1.0.0.
*2026-10-19:* the data-product and value-stream layers parked here, and
the systems and lanes deferred as node-field overlays (EPM-DEC-001-0052,
Phase B), are revived as modules (EPM-DEC-001-0053 to 0056); they are not
yet released.

---

## Appendix B. Versioning in detail

### The rule
URIs are permanent. Versions describe what changed around them. A consumer
who bookmarked a concept URI must still get a correct answer years later.

### Version numbers
Use `MAJOR.MINOR.PATCH` per module and for the release as a whole. A release
records exactly which module versions it bundles. Example: release 1.2.0 =
core 1.0.2 + party 1.3.0 + kpi 1.1.0 + organization 1.0.0.

### What counts as what

**Major (breaking).** Anything that can make an existing consumer wrong:

- A concept's URI changes. This should never happen.
- A concept is removed.
- A definition's meaning changes, not only its wording. Example: a crack
  spread's population changes from one product grade to a whole region.
- A hierarchy change that alters what a concept means.

**Minor (additive).** New concepts, new modules, new aliases, new
references, and hierarchy additions that do not redefine existing concepts.

**Patch (clarification).** Typo fixes, clearer wording with the same
meaning, an added example or scope note.

**The meaning-change test.** Would every query, report and assistant answer
produced under the old definition still be correct under the new one? Yes
means patch. No means major. When in doubt, it is major. A false major costs
a version number. A false patch corrupts consumers silently.

### Deprecation (never delete)

1. Mark the concept `owl:deprecated true`.
2. Add `dcterms:isReplacedBy` pointing at the successor.
3. Keep all existing triples, so the concept still answers "what did this
   use to mean?"
4. Record the deprecation in the changelog with the reason.
5. Introduce deprecations only in a major release.

Deleting a URI orphans every catalog row, RACI assignment and KPI binding
that pointed at it.

### Releasing a module

Before a release:

- Every row on the source-correction backlog has a fresh verdict after its
  correction (a fresh HOLD keeps it out of the release, with its reason
  recorded). Every other held row keeps its recorded hold reason. The ledger
  reconciles.
- The build, the evidence and the consumer-impact scan cite one commit.
- The consumer attestation is fresh.
- The SHACL slice passes.
- The owner has approved the release in writing.

Build the release with a script, never by hand. The builder reads only the
pinned evidence. It stops if any staging triple or blank node is left, or
if a staging predicate has no target. It writes the after half of the
conservation ledger, one row per staging predicate with its source and
migrated counts. It runs the SHACL slice before it writes, and records
each file's checksum and the evidence commit in a manifest. Its output is
deterministic, so the check script can confirm that the committed package
equals a fresh build. Where a draft ledger and an approved decision
disagree about a target, settle it before the build: record the approved
target in a decision record, update the ledger to match, and let the
builder follow that record. The record is the builder's only source of
targets; the builder never chooses between sources at write time, and it
fails if a staging predicate has no recorded target. Mark the ledger where
it disagrees, pointing to the record, so no reader follows the old target.

Test the builder from outside. Conservation counts balance even when a
field lands on the wrong property, so they cannot catch a swapped target.
Write tests that read each staging value from the source themselves and
check it sits on its recorded target in the built graph, with the full set
of values a rule produces (a value that sets two facets checks both). Prove
the tests: change the builder to send one field to the wrong target, and
confirm the suite fails. Pin measured splits (for example, how many notes
are provenance and how many are editorial), so that routing every value
one way fails.

State a cardinality on every property in the SHACL slice: `sh:maxCount 1`
on a single-valued property, `sh:minCount 0` with no maximum on a
multi-valued one. Test that every property has one, including properties
the release declares but does not use yet.

Until the owner approves, build the release as a release candidate
(`1.0.0-rc.1`): the candidate label in `owl:versionInfo`, the version IRI,
the catalog and the manifest, and no `dcterms:issued`. The cut is one commit after the
approval: drop the stage, set the issue date, update the test that pins
the version, and rebuild. Tag the merge commit after the merge. Records
written before the merge say the tag comes at merge, never that it exists.
At the cut, set `dcterms:modified` from the cut date. Do not keep one
copied from the earlier release. Remove the candidate package, so only the
release is left. Pin the sentence that approved the release in the
manifest and in a test that reads it from the saved answer, so the
release cannot be issued without it.

Build the next release from the released graph, not from the evidence
again. The builder reads the released package, applies the decided
changes, and records a hash of the released manifest, so the check fails
if the released package changes. The earlier release
stays reproducible from its own pinned evidence. Test that every triple
of the earlier release is kept, except the version header and anything a
decision changed.

Every release ships:

- `owl:versionInfo` on each module and on the release.
- `dcterms:issued` and `dcterms:modified` dates, set at the cut.
- A changelog entry per change: what changed, why, who approved, and the
  version classification.
- A new dataset version in the DCAT catalog, with its distributions.

### Ontology IRI and version IRI

Term IRIs never carry a version. Each module is an `owl:Ontology` with a
stable ontology IRI. Each release has an `owl:versionIRI`. The worked
example's header looks like this:

```turtle
<https://w3id.org/lsc/ontology/modules/core>
    a owl:Ontology ;
    dcterms:title "LSC Core Process Ontology"@en ;
    dcterms:description "Governed definitions of LSC's business processes: identity, hierarchy, relationships, and lifecycle."@en ;
    owl:versionIRI <https://w3id.org/lsc/ontology/modules/core/1.0.0> ;
    owl:versionInfo "1.0.0" ;
    dcterms:issued "2026-09-22"^^xsd:date ;
    dcterms:creator "The decision owner" ;
    dcterms:license <https://w3id.org/lsc/ontology/modules/core/license> .
```

When the module's concepts are `skos:inScheme` the module IRI, type it
`skos:ConceptScheme` as well as `owl:Ontology`. Without the scheme type, the
concepts sit in a scheme the release never declares.

Consumers who need the current meaning use the ontology IRI. Consumers who
need reproducibility pin the version IRI or a versioned distribution
(`…/releases/1.2.0/ontology.ttl`).

### When the reference framework changes

1. Your URIs do not move.
2. Review each `dcterms:references` link against the new version and
   correct stale ones.
3. Send newly relevant framework elements through the scope review (Step 8)
   before modeling them.
4. Record the framework version on the release. This is a minor release at
   most, and usually a patch.

### Who approves a release
The module owner approves minor and patch releases. The ontology owner
approves major releases, including any deprecation.

---

## Appendix C. Example predicate set

The worked example's process-to-process predicates, with their definitions.
Use them as a starting point and write your own definitions to your
evidence. Each definition is shaped by the confusion it prevents. "Source"
is the subject of the stored triple.

- **`enabledBy`.** The target supplies a maintained operating base,
  required control, governed mechanism, capability, resource or
  prerequisite condition that makes the source able to operate. "A enables
  B" is stored as `B enabledBy A`. Pitfall: confusing enablement with
  sequence, information flow or hierarchy. Test: would the source be unable
  to operate without what the target supplies?
- **`informedBy`.** The target provides context, planning input or
  awareness that shapes what the source does. Pitfall: promoting every data
  flow. If the citation shows information flowing the other way, hold the
  row. Do not flip it at emission.
- **`dependsOnOutputOf`.** The source consumes a specific output the target
  produces. Pitfall: confusing consumption with enablement. A broken output
  is a data problem. A missing capability is an operating-model problem.
- **`requires`.** The source cannot validly start, complete, proceed or
  reach its controlled state without the target, its completed control or
  its required condition. Pitfall: inferring a requirement because the
  target later uses related information. The precondition must be stated in
  the source.
- **`assuredBy`.** The target performs governance, compliance, quality,
  review, control testing or similar oversight over the source or its
  outcome. Pitfall: treating support or evidence supply as assurance.
- **`constrainedBy`.** The target is a binding constraint on the source's
  activity, decision or outcome. Pitfall: treating advice, coordination or
  sequence as a constraint. A constraint binds: the source cannot exceed,
  ignore or waive it.
- **`governedBy`.** The target holds governance authority over the source:
  policy-setting, approval rights or compliance enforcement. Pitfall:
  structural closeness. A parent in the hierarchy does not govern its
  children by position alone. An exception needs documented semantics
  beyond containment, explicit reviewer approval, and a record that it is
  not a precedent.
- **`triggeredBy`.** The target generates, detects or records the event,
  exception, change or handoff that starts the source. Pitfall: "feeds",
  "informs", "supports" and "precedes" are not triggers without an invoking
  event.
- **`precedes`.** The source completes before the target begins, as a
  sequence the business states. For siblings, structural nearness is
  enough. For non-siblings, the source definition must state the sequence
  ("arrives from", "routes to", an explicit handoff), or the rows must form
  a strict two-way pair.

The worked example also uses a disposition split for "enables" rows: a row
whose fact is already carried by `dependsOnOutputOf` merges as extra
evidence on that fact and emits no new triple.
