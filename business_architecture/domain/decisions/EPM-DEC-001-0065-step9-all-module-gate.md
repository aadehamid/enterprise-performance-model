# EPM-DEC-001-0065: Step 9 gate: every module's shapes run together on the whole graph, with zero violations

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Step 9's "done when" (zero unexplained violations) for the modules added in Step 7; Phase E of EPM-DEC-001-0052, its Step 9 item (SHACL shapes for the new modules) |
| Source | Claude Code session, 2026-10-19 |

## Context

Each module's tests validate its own data with its own shapes and the few graphs it points to. No test ran every shape file on the whole graph, so a shape that reaches too far, or a value one module's shape forbids in another module, went unseen. The first combined run found two such defects: the lane module's shape targeted every subject of `skos:inScheme`, so it demanded a notation and a definition of every concept in the graph (143 violations); and the consumer rules gave `dcterms:source` a plain-text value, which `core`'s shapes forbid (22 violations).

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **One gate for the whole graph.** `validation/test_all_module_shapes.py` loads the graph the regression loads and runs the shape files of `core` 2.1.0 and of the organization, ref-mpc, kpi, data-product, value-stream, system, lane, market-data and consumer modules, plus the controlled-value shapes. It must find zero violations. `scripts/check.sh` runs it.
2. **A negative test** adds a cross-module break (a value-stream process producing an undefined data product) and must fail.
3. **Both defects are fixed at their source:** the lane shapes now target a `lane:OfficeLane` class (EPM-DEC-001-0056's module), and the consumer rules cite their questions with `dcterms:bibliographicCitation` (EPM-DEC-001-0061's module).

## Alternatives considered

- **Keep per-module validation only.** Not chosen: it is how both defects passed.

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/ontology/validation/test_all_module_shapes.py`; EPM-DEC-001-0035, 0044, 0056, 0061.

## Consequences

- Step 9 has zero violations on the whole graph. The new modules' shapes join their release packages when each is released.
