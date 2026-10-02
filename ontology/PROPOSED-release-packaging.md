# Proposed ontology release packaging and validation

**Status:** Proposed (Candidate). Not machine SoT. No ontology file has been changed.
**Origin:** [EPM-PPC-UPDATE-PLAN](../ARCHIVE/EPM-PPC-UPDATE-PLAN_Existing_Artifacts.md), section "ontology/"; [EPM-ARCH-PPC-001](../architecture/EPM-ARCH-PPC-001_Publishable_EPM_Consumer_Contract.md).
**Last updated:** 2026-10-02

## Principle

Turtle in git is the machine ontology SoT. The current enterprise file is `ontology/stage2_enterprise_kpi_ontology.ttl`. Release packaging wraps that file. It does not move authority to a release artifact, a tool, or a consumer.

## Recommended outputs

| Output | Purpose |
|---|---|
| Versioned Turtle | An immutable snapshot of `stage2_enterprise_kpi_ontology.ttl` at a tag or commit |
| SHACL shapes | Governance and consistency constraints released with that version (FOUND-004 recommended path, step 4) |
| Release manifest | Version, checksums or commit, and authority and lifecycle status for each artifact, using the lifecycle in EPM-FOUND-000 |
| Competency queries and tests | Machine-testable questions with fixtures (FOUND-004 competency questions; process questions from EPM-ARCH-PPC-003) |
| Change and deprecation notes | What changed, which terms are deprecated, replacements, and migration guidance |

## Automated validation (proposed)

Run on every change to the Turtle, and again when cutting a release:

1. Parse check of the Turtle.
2. SHACL validation (pySHACL, ADR-HL-003).
3. OWL consistency check (Owlready2 / HermiT, ADR-HL-019).
4. Competency queries return the expected results against the fixtures.
5. Manifest check: checksums match, and every artifact carries an authority and lifecycle status.

## Versioning

Semantic versioning. A breaking change (a removed or re-meant term) bumps the major version. A deprecated term names its replacement and carries a migration note.

## Boundaries

- A named KPI is one individual, 1:1 with its catalog row. Do not add CandidateKPI or ApprovedKPI classes.
- Consumers extend in their own namespace and do not edit this Turtle. Reusable extensions are proposed back and reviewed.
- Fuseki, Neo4j, and other runtimes load from released Turtle. They are not SoT.

## Open questions

- Where released bundles are stored (git tags only, or also a package registry).
- Who approves a release (EPM Lead, per EPM-FOUND-000 roles, until named holders exist).
