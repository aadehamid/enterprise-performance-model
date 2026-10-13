# The organization module (Step 5)

Roles, RACI assignments, and control between legal entities. The module depends on `core` only. Its namespace is `https://w3id.org/lsc/ontology/modules/organization/`. The design is EPM-DEC-001-0030; the role register is EPM-DEC-001-0031.

- `vocabulary.ttl`: `orgm:ResponsibilityAssignment` (one process, one role, one RACI level, with the source's role text and a source), the `orgm:RaciLevel` code list, and `orgm:ControlRelationship` (controlling and controlled entity, share, as-of date, source). W3C ORG terms are used by IRI, not imported.
- `shapes.ttl`: the SHACL shapes, with a stated cardinality on every property.
- `role-register.csv`, `roles.csv`, `build_roles.py`, `roles.ttl`: the role register. Each role string in the process map's RACI lists maps to one or more roles; `build_roles.py` checks the register against the source and writes `roles.ttl`. Run `python3 build_roles.py` for the figures. `test_roles.py` tests it.
- `test_vocabulary.py`: checks one kind and one range per property, and a cardinality on each. It also checks that SHACL accepts a valid assignment and control relationship and rejects broken ones. `scripts/check.sh` runs it.

The `ref-mpc` reference module (`../ref-mpc/`) uses this module's control relationship. Later Step 5 slices add, in order:
1. The assignments for the 153 processes with RACI.
2. The links from `core:responsibleDomain` to org units, which wait for Hamid: the source does not show which of its values are org units.
