# EPM-DEC-001-0045: Hamid's role answers, carried by organization 2.0.0

| Field | Value |
|---|---|
| Status | Decided (Hamid, 2026-10-18: the seven role answers and the 2.0.0 release; the build choices delegated under EPM-DEC-001-0028) |
| Date | 2026-10-18 |
| Questions | The seven questions of `decision-packages/2026-10-14/role-questions.md`, left open by EPM-DEC-001-0031 |
| Source | Claude Code session, 2026-10-18 |

## Context

EPM-DEC-001-0031 merged role strings on spelling only and left seven questions for Hamid. Organization 1.0.0 was released with those roles on 2026-10-13. A merge cannot delete a released role: the playbook deprecates it and points it at its successor, in a major release only (`ontology-playbook.md`, Appendix B, "Deprecation (never delete)").

## Decision

**Hamid's decisions:**
1. RCVO Advisor and RVCO Advisor are one role; "RCVO" is a misspelling.
2. Forecaster stays apart from Local Refinery Forecaster until the refinery Economics and Planning process owner confirms they are the same.
3. Refinery Technical Service Representative is the Refinery Technical Representative.
4. Of the two long VP strings, the one with "RVCO" survives. VP RVCO stays its own role.
5. Crude RFC stays its own role. RFC is read as Refinery Feedstock Coordinator, as a contextual reading pending confirmation.
6. The acronym expansions with evidence are adopted: CP (Clean Products, in these roles), CPVC (Clean Products Value Chain), GFVC (Global Feedstocks Value Chain), RVCO (Refinery Value Chain Optimization), CCI (Continual Commercial Improvement), E&P (Economics and Planning, in the refinery-planning context), BP&A (Business Planning and Analysis) and RO (Regional Optimization). PSM stays unresolved. An expansion is not a merge.
7. Who owns a concept's meaning is a separate governance decision, not answered by process RACI.
8. Organization 2.0.0 is approved for these merges.

**What follows (Claude, under EPM-DEC-001-0028):**
1. **Deprecate, never delete.** `role:rcvo-advisor`, `role:refinery-technical-service-representative` and `role:vp-clean-products-crude-trading-ngls-asphalt-petchem` keep every 1.0.0 triple and gain `owl:deprecated true` and `dcterms:isReplacedBy` their successor. The misspelling becomes a `skos:hiddenLabel` of RVCO Advisor; the other two source spellings become `skos:altLabel`s of their successors. 60 roles, 57 live.
2. **Assignments keep their IRIs.** The three assignments that named a deprecated role now name its successor. Each keeps its IRI, which names the role the source string was registered to, and its source text. 940 assignments, as before; the ledger adds a row for the 3 moved. A SHACL shape rejects an assignment that names a deprecated role.
3. **Labels.** `roles.csv` keeps the source spelling in `label`, which the surface rules of EPM-DEC-001-0031 check. An expanded `preferred_label` becomes the `skos:prefLabel`, and the source spelling an `skos:altLabel`. Nine roles take an expanded name.
4. **Evidence.** Each answered role carries an editorial note with its evidence and its status: inferred from the process map (CP), or externally corroborated by MPC material. The corroborating sources are an MPC newsroom article for CPVC (2023-04-20) and for GFVC (2021-06-02), both read through a search index because the site blocks automated reads, and MPC job postings on third-party hosts for RVCO, CCI, E&P and BP&A, each read on 2026-10-18. A job posting on a third-party host is weaker evidence than a filing. A 2021 source supports the term, not today's structure.
5. **Definitions.** Four roles take a working definition from Hamid's answer: Refinery Value Chain Optimization Advisor, Refinery Technical Representative, Crude Refinery Feedstock Coordinator and Business Planning and Analysis. They are EPM working definitions, not MPC position descriptions.
6. **Not merged on an expansion.** E&P Supervisor and Refinery Econ & Planning Supervisor stay apart; CP Manager and the Global Feedstocks Manager stay apart.
7. **Competency question 17** stays waiting, now on this record. The proposed design, not built: a qualified governance assignment that names a concept or scheme, a role, a responsibility (semantic owner, business data steward, technical data custodian or process owner), a scope, dates, evidence and an approval status.
8. **Release.** Organization 2.0.0 (issued 2026-10-18) requires `core` 2.0.0. `ref-mpc` 1.0.0 is not re-released: it still requires organization 1.0.0, which 2.0.0 keeps intact because nothing is deleted. A `ref-mpc` release that requires 2.0.0 waits for its next change.

## Alternatives considered

- **Delete the merged roles.** Not chosen: the playbook forbids it; a deleted IRI orphans every reference.
- **Mint new assignment IRIs for the moved assignments.** Not chosen: it would remove three released IRIs.
- **Put the expanded name in `label`.** Not chosen: the surface rules check `label` against the source spelling.

## Hamid's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/answers-2026-10-18.md`: "1 yes. Merge RCVO Advisor into RVCO Advisor as a source-label correction.", "2 no for now. Retain Forecaster separately until the refinery Economics and Planning process owner confirms that it denotes the Local Refinery Forecaster.", "3 yes. Merge the technical-service representative into Refinery Technical Representative and retain both source labels.", "For queston 4 choose the string with "RVCO" in the list", "5 b. Retain Crude RFC as a distinct crude-specific role.", "Q6: RO = Regional Optimization", "Keep PSM unresolved.", "7 a. Address concept-meaning ownership through a separate governance decision and explicit assignments, independent of process RACI." Saved in `answers-2026-10-18-night.md`: "Yes, approve 2.0.0 (Recommended)". Items 1 to 8 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and Hamid can reverse them.

## Evidence

`decision-packages/2026-10-14/role-questions.md`; EPM-DEC-001-0031; `organization/roles.csv` (the editorial notes name each source); `releases/organization/2.0.0/`; `ontology-playbook.md`, Appendix B.

## Consequences

- `organization/build_roles.py` and `build_assignments.py` read the new columns; `test_roles.py`, `test_assignments.py` and `release/test_build_module.py` test the merges, the kept IRIs and the untouched 1.0.0 package.
- EPM-DEC-001-0031's questions are answered here.
