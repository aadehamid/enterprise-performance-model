# The organization module (Step 5)

Roles, RACI assignments, and control between legal entities. The module depends on `core` only. Its namespace is `https://w3id.org/lsc/ontology/modules/organization/`. The design is EPM-DEC-001-0030.

- `vocabulary.ttl`: `orgm:ResponsibilityAssignment` (one process, one role, one RACI level, with the source's role text and a source), the `orgm:RaciLevel` code list, and `orgm:ControlRelationship` (controlling and controlled entity, share, as-of date, source). W3C ORG terms are used by IRI, not imported.
- `shapes.ttl`: the SHACL shapes, with a stated cardinality on every property.
- `test_vocabulary.py`: checks one kind and one range per property, and a cardinality on each. It also checks that SHACL accepts a valid assignment and control relationship and rejects broken ones. `scripts/check.sh` runs it.

Later Step 5 slices add, in order:
1. The role register, normalized from the 91 role strings in the process map.
2. The assignments for the 153 processes with RACI.
3. The `ref-mpc` reference module.
4. The links from `core:responsibleDomain` to org units.
