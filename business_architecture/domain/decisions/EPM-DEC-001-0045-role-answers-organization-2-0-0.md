# EPM-DEC-001-0045: Hamid's role answers, carried by organization 2.0.0

| Field | Value |
|---|---|
| Status | Decided (Hamid, 2026-10-18 and 2026-10-19: the seven role answers, organization 2.0.0 and ref-mpc 1.1.0; the build choices delegated under EPM-DEC-001-0028) |
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
4. Of the two long VP strings, the one with "RVCO" survives.
5. Crude RFC stays its own role. RFC is read as Refinery Feedstock Coordinator, as a contextual reading pending confirmation.
6. The acronym expansions with evidence are adopted: CP (Clean Products), CPVC (Clean Products Value Chain), GFVC (Global Feedstocks Value Chain), RVCO (Refinery Value Chain Optimization), CCI (Continual Commercial Improvement), E&P (Economics and Planning), BP&A (Business Planning and Analysis) and RO (Regional Optimization). PSM stays unresolved. An expansion is not a merge.
7. Who owns a concept's meaning is a separate governance decision, not answered by process RACI.
8. Organization 2.0.0 is approved for these merges, and a `ref-mpc` release if one is needed.

**What follows (Claude, under EPM-DEC-001-0028):**
1. **Deprecate, never delete.** `role:rcvo-advisor`, `role:refinery-technical-service-representative` and `role:vp-clean-products-crude-trading-ngls-asphalt-petchem` keep every 1.0.0 triple and gain `owl:deprecated true` and `dcterms:isReplacedBy` their successor. The misspelling becomes a `skos:hiddenLabel` of RVCO Advisor; the other two source spellings become `skos:altLabel`s of their successors. 60 roles, 57 live.
2. **Assignments keep their IRIs.** The three assignments that named a deprecated role now name its successor. Each keeps its IRI, which names the role the source string was registered to, and its source text. 940 assignments, as before; the ledger adds a row for the 3 moved. A SHACL shape rejects an assignment that names a deprecated role. The `owl:deprecated` shape checks a boolean datatype; `test_roles.py` checks every value is true. (`sh:in ( true )` was tried first; in the projection run of 2026-10-19 the in-graph n10s validation reported each deprecated role's `true` as not in the list, while pyshacl accepted it. That is what this repo observed, not a documented n10s behaviour.)
3. **Labels.** `roles.csv` keeps the source spelling in `label`, which the surface rules of EPM-DEC-001-0031 check. An expanded `preferred_label` becomes the `skos:prefLabel`, and the source spelling an `skos:altLabel`. Ten roles take an expanded name: nine from question 6 and Crude RFC from question 5. CP is expanded only in CP Manager, and E&P only in the refinery-planning roles. VP RVCO stays its own role, as the package proposed: it is Accountable where the long VP is Informed.
4. **Evidence.** Each answered role carries an editorial note with its evidence and its status: inferred from the process map (CP), or externally corroborated by MPC material. The corroborating sources are an MPC newsroom article for CPVC (2023-04-20) and for GFVC (2021-06-02), both read through a search index because the site blocks automated reads, and MPC job postings on third-party hosts for RVCO, CCI, E&P and BP&A, each read on 2026-10-18. A job posting on a third-party host is weaker evidence than a filing. A 2021 source supports the term, not today's structure.
5. **Definitions.** Four roles take a working definition, written by Claude: Refinery Value Chain Optimization Advisor, Refinery Technical Representative and Crude Refinery Feedstock Coordinator carry EPM working definitions, not MPC position descriptions. Business Planning and Analysis carries a definition adapted from an MPC job posting, which its note quotes. Hamid's answers chose which roles expand; they do not word the definitions.
6. **Not merged on an expansion.** E&P Supervisor and Refinery Econ & Planning Supervisor stay apart; CP Manager and the Global Feedstocks Manager stay apart.
7. **Competency question 17** stays waiting, now on this record. The proposed design, not built: a qualified governance assignment that names a concept or scheme, a role, a responsibility (semantic owner, business data steward, technical data custodian or process owner), a scope, dates, evidence and an approval status.
8. **Release.** Organization 2.0.0 (issued 2026-10-18) requires `core` 2.0.0. `ref-mpc` 1.1.0 (issued 2026-10-19) requires organization 2.0.0. It is a minor release: only its requirement changes, and every query on 1.0.0 gives the same answer on 1.1.0, because ref-mpc uses only the control relationship, which organization 2.0.0 keeps unchanged. The 1.0.0 packages of both modules stay on disk as released.

## Alternatives considered

- **Delete the merged roles.** Not chosen: the playbook forbids it; a deleted IRI orphans every reference.
- **Leave `ref-mpc` on organization 1.0.0.** Considered first; not chosen once Hamid approved a `ref-mpc` release, because a consumer loading the current releases would otherwise mix two organization versions.
- **Mint new assignment IRIs for the moved assignments.** Not chosen: it would remove three released IRIs.
- **Put the expanded name in `label`.** Not chosen: the surface rules check `label` against the source spelling.

## Hamid's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/answers-2026-10-18.md`: "1 yes. Merge RCVO Advisor into RVCO Advisor as a source-label correction.", "2 no for now. Retain Forecaster separately until the refinery Economics and Planning process owner confirms that it denotes the Local Refinery Forecaster.", "3 yes. Merge the technical-service representative into Refinery Technical Representative and retain both source labels.", "For queston 4 choose the string with "RVCO" in the list", "5 b. Retain Crude RFC as a distinct crude-specific role.", "Q6: RO = Regional Optimization", "Keep PSM unresolved.", "7 a. Address concept-meaning ownership through a separate governance decision and explicit assignments, independent of process RACI." Saved in `answers-2026-10-18-night.md`: "Yes, approve 2.0.0 (Recommended)". Saved in `answers-2026-10-19-ref-mpc.md`: "Approve the ref-mpc release too if needed"; and in `answers-2026-10-19-releases.md`: "You have my approval to keep going and release things as needed. while I am out". Items 1 to 8 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and Hamid can reverse them.

## Evidence

`decision-packages/2026-10-14/role-questions.md`; EPM-DEC-001-0031; `organization/roles.csv` (the editorial notes name each source); `releases/organization/2.0.0/`; `ontology-playbook.md`, Appendix B.

## Consequences

- `organization/build_roles.py` and `build_assignments.py` read the new columns; `test_roles.py`, `test_assignments.py` and `release/test_build_module.py` test the merges, the kept IRIs and the untouched 1.0.0 package.
- EPM-DEC-001-0031's questions are answered here.
