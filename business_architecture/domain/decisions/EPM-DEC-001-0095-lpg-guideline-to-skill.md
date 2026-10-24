# EPM-DEC-001-0095: The ontology-to-LPG guideline moves into the `ontology-to-lpg` skill; EPM's copy points to it

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-23, for making the guideline a skill, moving it into the skill, testing it and the skill's design; the skill's contents and EPM's pointers delegated under EPM-DEC-001-0028) |
| Date | 2026-10-23 |
| Questions | Where the method for projecting a W3C ontology into a labelled property graph lives (EPM-DEC-001-0021); how the lessons of the close-out releases reach it |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md`, blocks 12 to 32 |

## Context

Since 2026-10-05 this repository has kept a pinned copy of the decision owner's guideline for projecting the ontology into a Neo4j labelled property graph (LPG), in `business_architecture/ontology/lpg-projection/`. The master copy was in the enterprise-people-graph repository, and the copy was last re-pinned to v2.2, commit `8ce9ada`, on 2026-10-14 (EPM-DEC-001-0021). Step 12 follows it (EPM-DEC-001-0020, 0036).

Projecting every released package, through the close-out releases, taught lessons v2.2 does not hold: the inputs are released packages, each with its own shapes; every namespace used for predicates or classes needs a fixed prefix; release gaps need a checked list, each with its fix; and a Rule 4a node may count an inverse link as one of its ends (EPM-DEC-001-0036, 0090, 0092 to 0094). While the close-out releases were in review, the decision owner asked whether the projection documents were being updated, and whether the guideline should become a skill.

## Decision

**The decision owner's decisions:**

1. The guideline becomes a skill, `ontology-to-lpg`, in the personal-agent-skills repository.
2. The guideline moves into the skill. The enterprise-people-graph repository and this repository point to it rather than keep copies.
3. The skill is tested before it is relied on (block 18).
4. The skill's design is "Read from engine": its in-graph SHACL gate reads what n10s says it compiled (`n10s.validation.shacl.listShapes()`), its Python subset of the shapes is only an advisory dry run, and S3PG and PG-Schema are cited as background.

**What follows (Claude, under EPM-DEC-001-0028):**

- **How the skill was tested.** Claude chose the method: a fresh agent ran the skill on its own library example and on EPM's released packages. Before the skill merged, test runs on 2026-10-23 and 2026-10-24 also used the current release set, a Neo4j Aura Free instance and a local Apache Jena Fuseki, and deleted the test data afterwards, as block 27 allows (the results are in personal-agent-skills #46 and the skill's `SOURCES.md`). Those runs tested the skill. Loading the ontology for the decision owner to explore, and the Databricks steps, are the separate later task (EPM-DEC-001-0096).

1. **The skill** is `skills/data/ontology-to-lpg` in personal-agent-skills, merged in personal-agent-skills #46 as `da75164`. It is the guideline's version 2.3, and its `references/versions.md` lists what 2.3 adds over 2.2. It keeps the five design rules, options 4a and 4b for Rule 4, and add-ons A to G, so the playbook's references to them still hold.
2. **The enterprise-people-graph guideline folder** points to the skill (enterprise-people-graph #4).
3. **EPM's `lpg-projection/`** README points to the skill at `da75164`. The two v2.2 files stay in the folder as superseded evidence of what Steps 1 and 12 followed until 2026-10-23. They are not deleted and are not copied again. This amends EPM-DEC-001-0021: the repository no longer keeps a copy of the current method.
4. **Current references point to the skill:** the ontology README's contents table, the playbook (its file list, Step 1, item 10, and Step 12's procedure), the worklog's Step 12 row and the glossary's LPG projection entry. Dated history, earlier records and the worked example in the playbook's §7 keep their references to `lpg-projection/`, because they describe what was done then.
5. **`projection/pipeline.py` stays on v2.2.** The skill says a project pinned to an earlier version keeps its own scripts (`SKILL.md`, "First, find where the projection stands", item 2). The pipeline, its manifest and its report still name "v2.2 (lpg-projection/, pin 8ce9ada)", which is what the pipeline implements. Moving the pipeline onto the skill's scripts would be a separate change, and no record asks for it.
6. **Neo4j Aura.** At the decision owner's request, Claude installed the neo4j-contrib/neo4j-skills plugin, 1.0.1, at user scope. n10s is not available on Aura (the Neosemantics documentation, "Availability & Installation"), so the projection validates on a local Neo4j with n10s, and copying the verified graph to Aura is an add-on. The Aura credentials are in a local credentials file outside the repository and never enter it.
7. **Triple stores.** The decision owner asked whether the skill should also load the ontology into any triple store (block 28) and chose "Add it now (Recommended)" (block 29): the skill loads the same validated files into any SPARQL 1.1 store through the W3C Graph Store HTTP Protocol, one named graph per package, and checks per-predicate counts against the files and the Neo4j export.

## Alternatives considered

- **Update the guideline only,** in enterprise-people-graph, as v2.3, and copy it again. Not chosen by the decision owner.
- **Fold the guideline into the `ontology` skill.** Not chosen by the decision owner: the projection is its own gated method, and the `ontology` skill's Step 12 hands over to it.
- **Keep the guideline in enterprise-people-graph, with the skill pointing to it.** Not chosen by the decision owner.
- **Keep fixing the skill's own subset of the shapes.** Not chosen by the decision owner: n10s decides which shapes it compiles, so the gate reads that answer from the engine.
- **Add the triple-store loading later, or put it in a separate skill.** Not chosen by the decision owner (block 29).

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`:

- "By the way are updating RDF to LPG projection documents/playbook... I am not sure what we call it."
- "Do you think we should make a skill out of this projection guidline/playbook?" The choice: "Make it a skill (Recommended)".
- "Actually do you think we should move the guideline / playbook to personal skill repo from people graph?" The choice: "Move it into the skill (Recommended)".
- "add that as part of the goal"
- "let us make sure we test the skill to ensure it works . The guideline gives what should be done to prepare for the projection and the skill do the projection with the user. correct?"
- "Are there any high quality external refreces either from Neo4j or somewhere else that can further guide us?" The choice: "Read from engine (Recommended)".
- On Neo4j's skills and Aura: "Also let us install https://github.com/neo4j-contrib/neo4j-skills And further see where any of the skills from Neo4j may help." and "We will eventual test projection to Aura."

## Evidence

- EPM-DEC-001-0020, 0021, 0036, 0090, 0092, 0093, 0094.
- The skill's `SKILL.md` and `references/versions.md`, in personal-agent-skills at `da75164`.
- Neo4j Labs, Neosemantics (n10s) documentation, "Availability & Installation" (neo4j.com/labs/neosemantics), read 2026-10-23.

## Consequences

- `lpg-projection/README.md` names the skill as the current method and carries a dated note that the v2.2 files are superseded.
- EPM-DEC-001-0021 carries a dated note and is amended by this record.
- The store tests are a separate task after the ontology closes (EPM-DEC-001-0096; blocks 26 to 32): load the ontology into Apache Jena and into a Databricks Delta triple table, project it to a local Neo4j and to Aura, rebuild both from the Databricks store and check that no data is lost, then use OntoBricks to link Unity Catalog metric views to the processes.
