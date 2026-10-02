# EPM-ARCH-REL-001 — EPM Consumer Release Contract

**Artifact ID:** EPM-ARCH-REL-001
**Version:** 0.1 Draft
**Status:** Draft (Candidate). Not Approved Baseline.
**Owner:** Enterprise Performance Model Lead
**Last updated:** 2026-10-02
**Derived from:** [EPM-ARCH-PPC-001](EPM-ARCH-PPC-001_Publishable_EPM_Consumer_Contract.md) (Candidate)

**Purpose:** The small governed contract between an EPM release and an executable consumer such as PPC. EPM-ARCH-PPC-001 explains the principle. This document states the obligations a release and a consumer each accept.

## 1. Scope

A consumer is any executable implementation that depends on EPM meaning: a proving ground such as PPC, a reference implementation, or an enterprise build. This contract does not make a consumer an authority. See EPM-FOUND-000, section "Downstream consumers and the PPC proving ground", and decision D-18.

## 2. Release identity

- A release is a git tag on this repository, named `epm-release-<MAJOR>.<MINOR>.<PATCH>`.
- A release records an immutable commit and a checksum for every artifact in its manifest.
- Semantic versioning. A breaking change (a removed or re-meant term, or a changed process or portfolio identifier) bumps MAJOR. An additive change bumps MINOR. A correction bumps PATCH.
- A deprecated term or identifier names its replacement and carries a migration note.

## 3. Release manifest

Each release carries a manifest. The paths below are the current repository locations. Any artifact marked "gap" does not exist as a release-ready artifact today, and the manifest must say so rather than omit it.

```yaml
epm_release: epm-release-0.1.0   # example only; no release has been cut
generated_from_commit: <sha>
artifacts:
  principles:
    path: EPM_Project_Enablement_Pack_Markdown_HTML/EPM-FOUND-000A_Architectural_Principles.md
    authority: Draft (working baseline)
  business_architecture:
    path: EPM_Foundation_v2_Markdown_HTML/EPM-FOUND-001.md
    authority: Draft (working baseline)   # pattern document, not the instance SoT
  process_authority:
    paths:
      - business_architecture/business_process/downstream_process_map.json
      - business_architecture/business_process/value_stream_order_to_cash.json
      - business_architecture/business_process/value_stream_commercial_lifecycle.json
      - business_architecture/business_process/office_lanes.json
      - business_architecture/schema/value_stream.schema.json
    authority: Process authority (instance files)
  semantic_model:
    path: EPM_Foundation_v2_Markdown_HTML/EPM-FOUND-003.md
    authority: Draft (working baseline)   # human-readable, not machine SoT
  ontology:
    path: ontology/stage2_enterprise_kpi_ontology.ttl
    authority: Machine ontology SoT
  shacl:
    path: null
    authority: gap   # no SHACL shapes released yet (see ontology/PROPOSED-release-packaging.md)
  measurement_kpi_model:
    path: EPM_Foundation_v2_Markdown_HTML/EPM-FOUND-005.md
    authority: Draft (working baseline)
  data_product_portfolio:
    paths:
      - business_architecture/business_process/data_product_portfolio.json
      - business_architecture/schema/data_product_portfolio.schema.json
    authority: Process authority (instance files)
  kpi_store_contract:
    path: null
    authority: gap   # EPM-KPI-013 KPI Metadata Schema is "To be located" in EPM-FOUND-000
  competency_questions:
    path: null
    authority: gap   # not yet packaged
  deprecation_notes:
    path: null
    authority: gap
```

Authority values come from the artifact lifecycle in EPM-FOUND-000. A release does not promote any artifact. Including an artifact in a release is not approval.

## 4. Release obligations

1. Publish the manifest with every artifact's path, checksum, and authority status.
2. State known gaps explicitly.
3. Do not change the source-precedence hierarchy or the SoT assignments (process authority folders, Turtle in git, KPI Store status on `dim_kpi_metadata`).
4. Record deprecations and migrations for each release.

## 5. Consumer obligations

1. Declare the EPM release it was built against, using the dependency manifest in EPM-ARCH-PPC-001, section 8.
2. Do not infer approval from file presence. Read authority status from the manifest and, for KPIs, from the KPI Store row.
3. Preserve Meaning vs Compute: **ontology IRI → KPI Store row → Metric View → `MEASURE()`**. No second meaning store. No formula authored in the graph.
4. Own its instances and runtimes. Process instances are consumer-owned.
5. Define local extensions in its own namespace. Do not edit EPM artifacts.
6. Report gaps as EPM issues or ADRs. Do not fork silently.

## 6. Extension and feedback process

A reusable concept found by a consumer is proposed to EPM, reviewed through EPM governance, and included in a later release. Until then it stays in the consumer's namespace.

## 7. Open items

- Cutting a first release requires closing the manifest gaps above (SHACL, KPI Store contract, competency questions, deprecation notes), or releasing with them explicitly marked as gaps.
- Who approves a release. Until named role holders exist, this is the EPM Lead.
- Where released bundles are stored beyond git tags.
