# EPM-DEC-001-0113: A logical-model module: ER Studio's export kept as it is, an annotation layer linking it to the ontology, and the customer logical model only in the release

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-11-02, for the module, its two views, the customer model's place and the five competency questions; the build choices delegated under EPM-DEC-001-0028; the module's `1.0.0` stays with the decision owner) |
| Date | 2026-11-02 |
| Questions | Claude asked thirteen questions in two rounds, each with a recommendation, about a logical data model the decision owner exported from ER Studio Data Architect |
| Source | Claude Code session of 2026-11-02; `answers-2026-11-02-logical-model.md`, blocks 1 to 6 |

## Context

The decision owner exported a logical data model of the customer domain from ER Studio Data Architect, a relational data modelling tool, as Turtle, and asked for it to become part of the release (block 1). ER Studio writes each entity as an `owl:Class` and each attribute as an `owl:DatatypeProperty`, in its own namespace, `https://www.erstudio.com/semanticmodel/`, with its own SHACL shapes. The export names the source systems its entities come from, which the `system` and `party` modules already hold. The file arrived through email inside an RTF document, which had rewritten its namespace IRIs into mail-filter links; Claude restored the eight IRIs from their original targets and kept the rest as written, and the cleaned file sits in a folder Git ignores (`release-cut/`, never committed).

## Decision

**The decision owner's decisions** (blocks 4 to 6: "yes to all", twice, then "go ahead"):

1. **Sharing.** The model goes to the same colleagues as the release.
2. **The source stays out of `main`.** The export lives in a gitignored folder, `release-cut/augment/logical-model/`, which `cut.sh --augment <folder>` reads. The decision owner: "it is okay if this stays in my .gitignore and cut.sh will provide an option to read it" and "this logical model I only wants it to show up in the release and not the main for now".
3. **One module, `logical-model`; the customer model is one model inside it.** The decision owner named both (block 4). A future logical model joins the same module as another named model, not a new module.
4. **Two views of one model** (Q9, superseding Q4 and Q5 of round one). ER Studio's export is kept exactly as it is, in its own graph, with ER Studio's namespace, classes, properties and shapes: "I want to keep all the namespaces that ER STudio used in that export". The module adds a layer of annotations, in its own namespace, onto ER Studio's IRIs: the model an entity belongs to, its source system (`system`), the `party` concept it describes and the `data-product` table that builds it. Nothing is re-minted or duplicated, and ER Studio's classes stay classes.
5. **Two safeguards** (Claude's answer to the decision owner's "I want to make sure this is the best design decsiosion", then "go ahead"). The layer keys each entity on ER Studio's numeric `dcterms:identifier`, not on its IRI, which ER Studio builds from the entity's name; the builder finds the current IRI at each build and fails when an annotated entity has gone. Each model has its own named graph, and the builder fails on an IRI two models both define, since every ER Studio export uses the same namespace and the same model node.
6. **`main` holds the machinery; the release holds the customer model.** `main` holds the module's small vocabulary and shapes, the builder, tests on a made-up two-entity sample (*2026-11-02:* the landed example holds three entities; the third exercises the identifier space entities share with attributes), `cut.sh --augment` and the blueprint; the package `logical-model 1.0.0` is built only during the cut. So the release holds one module more than `main` releases: `main` releases twelve modules and the release holds thirteen (*2026-11-02:* technical-graph 1.0.0 merged (#472); until then `main` released eleven), while `main` holds the logical-model module's machinery, unreleased. The builder takes the export's location as an input, so the same build runs from `main` if the decision owner later moves a generalised model there: "we must also have the options to also build logical model from original main".
7. **The blueprint.** The method for adding any logical model is a reference of the `ontology` skill; the guide, the walkthrough and `MODULES.md` apply it, with the customer model as the worked example in the release. The decision owner: "Let us have a section in the Guide, playbook, and walkthrough and any other relevant documents to decribe how we handle this logical model as a blue print".
8. **The links Claude drafts.** The source system comes from the entity's name; the `party` and `data-product` links are drafted from names and descriptions, each with its evidence, and only clear ones are asserted. The doubtful ones go on a list in the one page the decision owner approves `1.0.0` from.
9. **Five competency questions, 51 to 55:** which logical entities hold data about a party concept; which source system each entity comes from and which entities each system feeds; which attributes identify a customer in each system (primary and alternate keys); which attributes stand for a business term and which have none; which data product or platform table implements each entity, and which have none.
10. **This release.** The module ships in the follow-up release as `logical-model 1.0.0`, approved by the decision owner from one page; the cut waits for it.
11. **The IRIs.** The module's own terms are minted under `https://w3id.org/lsc/ontology/modules/logical-model/` in `main`, which the cut rewrites to `w3id.org/mpc` in the release, as for every module (EPM-DEC-001-0110, decision 7 and "What follows", item 4). ER Studio's namespace is not ours and is not rewritten.

## Alternatives considered

- **Re-mint every entity and attribute under the module's namespace, with `skos:exactMatch` to ER Studio's IRIs** (round one's Q5). Rejected for two views: it doubles about 1,700 terms (47 classes and 1,634 datatype properties) and every re-export would need the copies brought back into step.
- **Model the entities as SKOS concepts of the module's own classes** (round one's Q4). Rejected with Q5: the decision owner wants the model as ER Studio sees it.
- **Commit the export to `main`.** Rejected by the decision owner for now.
- **A release of `data-product`.** Rejected: a logical model is a design one level above the platform tables `data-product` holds.

## The decision owner's recorded words

> I only wants this to be part of the release and not part of the main. I am thinking this can be another module in the ontology, making it 13 modules with the new tech graph.

> By the way, it is okay if this stays in my .gitignore and cut.sh will provide an option to read it. is it a good option to have. Be able to cut from original main and augment the release by taking file outside of the release.

> I want to keep all the namespaces that ER STudio used in that export. What is the best way to orgainze it in such a way that we can alos see things the way ER Studio sees it . Is it going to be its own modules with connection to other modules?

> Let us call that inside the "logical-model" will sit "customer-logical-modle", which will be this one. corrrect?

> Q11. Yes . But we must also have the options to also build logical model from original main. if that is the case in the future. Because in the future we may want to generalize the logical model that is .gitignore and use it to update original main.

> go ahead

## Consequences

- The release is no longer built from `main` alone: the cut records each outside file's hash in the release manifest, the leak gate scans the module built from it, and the clean-room test needs the folder too.
- Documents in `main` count the modules `main` releases, twelve; the release's documents count one more, the logical-model module, thirteen in all (*2026-11-02:* technical-graph 1.0.0 merged (#472); until then `main` released eleven).
- EPM-DEC-001-0110's "What follows" items 1 and 8 and its index row carry dated notes for the augment folder.
- The module's `1.0.0` waits for the decision owner's approval from one page.
