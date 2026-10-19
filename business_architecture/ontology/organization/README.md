# The organization module (Step 5)

Roles, RACI assignments, and control between legal entities. The module depends on `core` only. Its namespace is `https://w3id.org/lsc/ontology/modules/organization/`. The design is EPM-DEC-001-0030; the role register is EPM-DEC-001-0031; the assignments are EPM-DEC-001-0032.

- `vocabulary.ttl`: `orgm:ResponsibilityAssignment` (one process, one role, one RACI level, with the source's role text and a source), the `orgm:RaciLevel` code list, and `orgm:ControlRelationship` (controlling and controlled entity, share, as-of date, source). W3C ORG terms are used by IRI, not imported.
- `shapes.ttl`: the SHACL shapes, with a stated cardinality on every property.
- `role-register.csv`, `roles.csv`, `build_roles.py`, `roles.ttl`: the role register. Each role string in the process map's RACI lists maps to one or more roles; `build_roles.py` checks the register against the source and writes `roles.ttl`. Run `python3 build_roles.py` for the figures. `test_roles.py` tests it.
- `build_assignments.py`, `assignments.ttl`, `raci-conservation.csv`: the RACI assignments. One assignment per RACI entry in the process map and per role it names, with the entry's text and the process map as its source. Nothing is inferred from the hierarchy. The ledger reconciles entries in with assignments out. `test_assignments.py` tests it.
- Organization 2.0.0 (EPM-DEC-001-0045) carries the decision owner's role answers: three roles deprecated into their successors (never deleted), their three assignments moved with their IRIs kept, expanded names with the acronyms as alternative labels, and an editorial note with the evidence on each answered role. `roles.csv` holds the columns `preferred_label`, `replaced_by`, `replaced_label_kind`, `definition` and `note`.
- `test_vocabulary.py`: checks one kind and one range per property, and a cardinality on each. It also checks that SHACL accepts a valid assignment and control relationship and rejects broken ones. `scripts/check.sh` runs it.

The `ref-mpc` reference module (`../ref-mpc/`) uses this module's control relationship. The decision owner decided that the `core:responsibleDomain` values are business domains, not org units, so no org units are made for them; `core` 2.0.0 links each concept that carries one of those values to a business domain code list instead (EPM-DEC-001-0038).
