# The organization module (Step 5)

Roles, RACI assignments, and control between legal entities. The module depends on `core` only. Its namespace is `https://w3id.org/lsc/ontology/modules/organization/`. The design is EPM-DEC-001-0030; the role register is EPM-DEC-001-0031; the assignments are EPM-DEC-001-0032.

- `vocabulary.ttl`: `orgm:ResponsibilityAssignment` (one process, one role, one RACI level, with the source's role text and a source), the `orgm:RaciLevel` code list, and `orgm:ControlRelationship` (controlling and controlled entity, share, as-of date, source). W3C ORG terms are used by IRI, not imported.
- `shapes.ttl`: the SHACL shapes, with a stated cardinality on every property.
- `role-register.csv`, `roles.csv`, `build_roles.py`, `roles.ttl`: the role register. Each role string in the process map's RACI lists maps to one or more roles; `build_roles.py` checks the register against the source and writes `roles.ttl`. Run `python3 build_roles.py` for the figures. `test_roles.py` tests it.
- `build_assignments.py`, `assignments.ttl`, `raci-conservation.csv`: the RACI assignments. One assignment per RACI entry in the process map and per role it names, with the entry's text and the process map as its source. Nothing is inferred from the hierarchy. The ledger reconciles entries in with assignments out. `test_assignments.py` tests it.
- `test_vocabulary.py`: checks one kind and one range per property, and a cardinality on each. It also checks that SHACL accepts a valid assignment and control relationship and rejects broken ones. `scripts/check.sh` runs it.

Later Step 5 slices add, in order:
1. The `ref-mpc` reference module.
2. The links from `core:responsibleDomain` to org units.
