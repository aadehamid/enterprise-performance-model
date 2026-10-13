# EPM-DEC-001-0030: The organization module's vocabulary: RACI assignments, control between legal entities, RACI levels

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-13 |
| Questions | Step 5, slice 1: the classes and properties the organization module needs before roles and assignments are emitted |
| Source | Claude Code session, 2026-10-13, under Hamid's extension of the delegation to Steps 5 to 12 (EPM-DEC-001-0028 amended in #252, merged) |

## Context

Step 5 models organizations, roles and responsibilities (`ontology-playbook.md`, Step 5). Earlier decisions already fix much of it:
- The module policy (`step4/playbook/ontology-worklog.md`, "Module policy — decided 2026-09-18") makes `organization` the module for roles and RACI assignments, depending on `core` only.
- EPM-DEC-001-0015 puts MPC reference instances in a separate `ref-mpc` module, and models MPC's control of MPLX as a relation separate from `org:subOrganizationOf`, with share, as-of date and source on a qualified-relation node (EPM-DEC-001-0020).
- EPM-DEC-001-0023 maps to public ontologies and does not import them.

The process authority, `business_architecture/business_process/downstream_process_map.json`, carries a `raci` object (responsible, accountable, consulted and informed, each a list of role names) on 153 processes.

## Decision

The organization module's namespace is `https://w3id.org/lsc/ontology/modules/organization/` (the `…/modules/{module}` pattern of the URI policy). Its vocabulary, in `business_architecture/ontology/organization/vocabulary.ttl`:

- **`orgm:ResponsibilityAssignment`.** A node binding one process (`orgm:forProcess`, a concept of the core scheme), one role (`orgm:assignedRole`, an `org:Role`) and one RACI level (`orgm:raciLevel`). It also keeps the role as the source wrote it (`orgm:sourceRoleText`) and cites its source (`dcterms:source`). One node per process, role and level, because a single property cannot carry the three-way binding (playbook Step 5).
- **`orgm:RaciLevel`.** A code list of four members (responsible, accountable, consulted, informed), the levels the process map uses.
- **`orgm:ControlRelationship`.** A node with the controlling and controlled legal entities (`org:FormalOrganization`), the ownership share (0 to 1), the as-of date and the source.
- **W3C ORG terms by IRI.** `org:Role`, `org:FormalOrganization` and `org:OrganizationalUnit` are used by IRI. ORG is not imported (EPM-DEC-001-0023).

`shapes.ttl` states a cardinality on every property (EPM-DEC-001-0020, rule 2):
- **Assignment:** exactly one process, role, level and source text, and at least one source.
- **Role:** exactly one English name. A definition is optional until the role register supplies definitions.
- **Control relationship:** exactly one of each entity, at most one share, exactly one as-of date, and at least one source.

Left to later slices: the roles themselves and their normalization from the source's 91 role strings; the assignments; the `ref-mpc` instances; the links from `core:responsibleDomain` to org units; and the relation for who owns a meaning (competency question 17).

## Alternatives considered

- **A property per RACI level from process to role** (`responsibleRole`, `accountableRole`, …). Rejected: the playbook requires the n-ary node, and a node can carry its source text and citation.
- **Import W3C ORG.** Rejected by EPM-DEC-001-0023: map, don't import.
- **Make a role definition required now.** Rejected for this slice: the source gives role names only. Definitions come with the role register.

## Hamid's recorded words

Hamid extended the delegation in the Claude Code session on 2026-10-13 (saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-steps-5-12.md`; also added in #252, merged): "yes, extend the delegation to steps 5 to 12." Hamid did not make the choices above himself. Claude made them under that delegation, and Hamid can reverse any of them.

## Evidence

`ontology-playbook.md`, Step 5; EPM-DEC-001-0015, 0020, 0023; the module and URI policies in `step4/playbook/ontology-worklog.md`; `downstream_process_map.json` (`raci` on 153 processes).

## Consequences

- Competency questions 3 to 5 become answerable once the roles and assignments are emitted (later slices).
- Every assignment traces to its source entry through `orgm:sourceRoleText` and `dcterms:source`.
