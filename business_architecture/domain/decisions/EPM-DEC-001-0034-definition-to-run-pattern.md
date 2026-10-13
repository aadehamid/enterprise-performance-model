# EPM-DEC-001-0034: Step 6: a run links to the process definition it followed through prov:hadPlan

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-13 |
| Questions | Step 6: how a consumer's record of a process run links to the process definition, and what the ontology checks |
| Source | Claude Code session, 2026-10-13, under Hamid's extension of the delegation to Steps 5 to 12 (EPM-DEC-001-0028, amended in #252) |

## Context

EPM-DEC-001-0016 adopts P-Plan as the bridge from definitions to runs. The ontology defines the pattern and holds no occurrence records, and consumers such as PPC hold the runs. The playbook's Step 6 is done when no definition is typed as an occurrence, the definition-to-run pattern is defined, and every occurrence a consumer records can link to its definition.

The core 1.0.0 process concepts are `skos:Concept`s, and none is a `prov:Activity`. P-Plan (release 17 September 2013, revision 1.1, http://purl.org/net/p-plan#) states that the association of a whole plan with its execution "can be modeled with PROV (with the prov:hadPlan property)". PROV-O is a W3C Recommendation of 30 April 2013.

## Decision

1. **A run is a `prov:Activity` held by the consumer.** It has exactly one `prov:qualifiedAssociation`, whose `prov:hadPlan` names exactly one core process concept: the definition the run followed. It states `prov:startedAtTime`, and may state `prov:endedAtTime` and `prov:agent`.
2. **The definition must be a live process.** It is in the core scheme, not retired, not a structural anchor, and not a capability (the worklog's `conceptKind` decision of 2026-09-22: a capability is an ability that processes realize, so no one runs it). The capability exclusion was added on 2026-10-13, after #258 merged; see the amendment below.
3. **No new terms.** The pattern uses PROV-O as published. P-Plan's steps and variables are not used now. The process taxonomy is a naming hierarchy, not a plan's step structure (playbook: SKOS first), and the 2026-09-22 flow decision keeps inputs and outputs as governed values, not nodes.
4. **The ontology publishes the shapes.** `business_architecture/ontology/provenance/run-shapes.ttl` holds the shapes a consumer's run must meet, plus one that fails any core concept typed as a `prov:Activity`. `example-run.ttl` illustrates a run; it is not data.

Step 6's first procedure, planned inputs and outputs on the definitions, is not done here. The only source for them is the process map's `sioc` field, which holds suppliers, inputs, outputs and customers on 153 processes. The playbook says to confirm that field's business meaning before naming a term after it. That question goes to Hamid. Competency question 8 waits for the answer.

### For Hamid: the `sioc` field

Does `sioc` in the process map mean SIPOC (suppliers, inputs, process, outputs, customers), with the process being the node itself? Recommendation: yes. All 153 objects hold exactly those four lists. If confirmed, the inputs and outputs become planned input and output values on those 153 processes, as governed literals under the 2026-09-22 flow decision. Suppliers and customers stay parked.

## Amendment, 2026-10-13

#258 merged with a shape that let a run follow a concept of kind capability. `core` 1.0.0 holds 23 of them. A capability is realized by processes and is not performed, so a run cannot follow one. The live-process shape now rejects a capability, decided under the same delegation. Concepts with no kind stay allowed: the shape rejects only the two kinds it names.

## Alternatives considered

- **Type each process concept as a `p:Plan` and its children as `p:Step`s.** Rejected: it changes the released core 1.0.0, and it reads the naming hierarchy as an execution structure.
- **A direct property from the run to the definition** (for example `core:runOf`). Rejected: PROV-O's `prov:hadPlan` already says it, and consumers that speak PROV-O read it without a mapping.
- **Mint planned input and output nodes from `sioc` now.** Rejected: the field's meaning is unconfirmed, and the 2026-09-22 decision defers flow nodes.

## Hamid's recorded words

Hamid extended the delegation in the Claude Code session on 2026-10-13 (saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-steps-5-12.md`): "yes, extend the delegation to steps 5 to 12." Hamid did not make the choices above himself. Claude made them under that delegation, and Hamid can reverse any of them.

## Evidence

`ontology-playbook.md`, Step 6 and the PROV-O and P-Plan entry; EPM-DEC-001-0005, 0016; the worklog's flow-modeling and `conceptKind` decisions of 2026-09-22; the P-Plan specification (https://www.opmw.org/model/p-plan/, release 17 September 2013, revision 1.1); PROV-O (https://www.w3.org/TR/2013/REC-prov-o-20130430/); `downstream_process_map.json` (`sioc` on 153 processes).

## Consequences

- `scripts/check.sh` runs `provenance/test_run_shapes.py`. A core release that types a definition as an activity fails it.
- A consumer validates its runs against `run-shapes.ttl` together with the core release.
