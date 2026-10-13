# EPM-DEC-001-0035: Step 9: code-list values come from their own list; evidence links wait for the next core release

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-13 |
| Questions | Step 9: how the controlled-value shapes are added after the `core` 1.0.0 release, and what the evidence-link shape needs |
| Source | Claude Code session, 2026-10-13, under Hamid's extension of the delegation to Steps 5 to 12 (EPM-DEC-001-0028, amended in #252) |

## Context

EPM-DEC-001-0014 orders the Step 9 shapes after the release slice: every relationship fact links to its source evidence; controlled values come from their allowed lists; no definition is typed as an occurrence. The third is in EPM-DEC-001-0034 (Step 6).

The `core` 1.0.0 release shapes check `sh:in` on `core:conceptKind` only. Seven other code-list properties are checked only with `sh:class skos:Concept`. `core:evidenceBasis` and `core:sequenceScope` have no release shape; their build-time shapes in `step4/scoped-sequence/` check them. Either way, a value from the wrong list passes release validation: for example, a cadence used as an operating mode.

The 640 canonical facts in `core` 1.0.0 are direct triples. (The 17 scoped-sequence nodes do carry their source rows.) Their evidence (the REL row IDs) is in the release's `canonical-facts.csv`, not in the graph.

## Decision

1. **A controlled-value shape for every code-list property.** `business_architecture/ontology/validation/controlled-values.ttl` requires each value of the ten coded properties of `core` (APQC mapping decision, operating mode, cadence, planning level, lifecycle status, governance status, hold status, concept kind, evidence basis, sequence scope) to be in its own code list. It applies the same rule to the organization module's RACI level. `core` 1.0.0 and the organization module's RACI assignments (EPM-DEC-001-0032) conform.
2. **The shapes run against the released core without changing it.** `scripts/check.sh` runs them. They join the release shapes at the next `core` release.
3. **A test keeps the list complete.** It fails when a core property takes values from a core code list and no shape covers it. That test found `evidenceBasis` and `sequenceScope` while this slice was built.
4. **The evidence-link shape waits for the next `core` release.** EPM-DEC-001-0014 orders it first; this slice takes the second item first because today every canonical fact would fail it: no canonical fact carries its evidence in the graph. Adding that is a change to the released module.

### For Hamid: evidence on the facts

EPM-DEC-001-0014 says I walk you through each shape and its violation report. Two things to approve:
- **The controlled-value shapes.** `core` 1.0.0 has no violations.
- **How the next `core` release carries evidence.** Recommendation: one qualified-relation node per canonical fact (EPM-DEC-001-0020, rule 4 as decided), naming the subject, the predicate, the object and the REL rows from `canonical-facts.csv`. That adds 640 nodes. The evidence-link shape then requires one such node per fact.

## Alternatives considered

- **Add the shapes to `core` 1.0.0.** Rejected: the release is fixed; its shapes change only in a new release.
- **Check the evidence links against `canonical-facts.csv` in a script.** Rejected as the Step 9 shape: the rule is that the graph itself links each fact to its evidence. The release's build already checks the CSV.

## Hamid's recorded words

Hamid extended the delegation in the Claude Code session on 2026-10-13 (saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-steps-5-12.md`): "yes, extend the delegation to steps 5 to 12." Hamid did not make the choices above himself. Claude made them under that delegation, and Hamid can reverse any of them.

## Evidence

EPM-DEC-001-0014, 0020, 0026, 0029, 0030, 0032, 0034; `releases/core/1.0.0/shapes.ttl`, `core.ttl` and `canonical-facts.csv`; `release/core-vocabulary.ttl`.

## Consequences

- `scripts/check.sh` runs `validation/test_controlled_values.py`.
- A new code-list property in `core` fails the check until it has a shape.
