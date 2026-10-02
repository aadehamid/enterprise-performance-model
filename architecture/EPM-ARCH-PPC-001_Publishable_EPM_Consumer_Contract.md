# EPM-ARCH-PPC-001 — Publishable EPM Consumer Contract

**Status:** Proposed  
**Purpose:** Define the versioned EPM artifact bundle that executable consumers such as PPC should depend on.

## 1. Principle
EPM is not only documentation. It publishes governed business, performance, semantic and process contracts that downstream implementations can validate against.

## 2. Consumer bundle
A release should expose immutable versions/checksums/commits for:
- architectural principles;
- business architecture definitions;
- process-authority JSON and schemas;
- human-readable semantic model;
- machine ontology Turtle;
- SHACL shapes;
- measurement/KPI model;
- data-product portfolio/schema;
- KPI Store metadata contract;
- competency questions/test fixtures;
- deprecation/migration notes.

## 3. Authority metadata
Each artifact in a release records authority/lifecycle such as canonical, process authority, machine ontology SoT, approved, draft/candidate, existing-unlinked, superseded or retired.

Consumers must not infer approval from file presence.

## 4. Meaning versus Compute
The release preserves EPM's existing contract:

> **Meaning does not compute.**

One governed semantic IRI identifies the KPI; one KPI Store row owns identity/approval/formula pointer; compute runs against the governed Metric View. Consumers may implement different runtimes but must preserve this boundary.

## 5. Process conformance
Process-authority artifacts should be consumable as designed-process contracts. Executable consumers can generate or observe process instances and compare them with the EPM design.

EPM owns the designed meaning. Consumers own their instances.

## 6. Competency questions
EPM releases should package machine-testable competency questions where practical. Questions should cover business architecture, KPI/data-product relationships, ontology semantics and process relationships.

## 7. Extension process
Consumers can define local extensions in their own namespace. Reusable downstream concepts are proposed to EPM, reviewed, then included in a later EPM release.

## 8. Example dependency manifest
```yaml
epm_release: <tag>
principles: <version>
process_authority: <version>
ontology: <version>
shacl: <version>
measurement_kpi_model: <version>
data_product_portfolio: <version>
kpi_store_contract: <version>
competency_questions: <version>
```

## 9. Why PPC matters
PPC is the first large integrated proving ground for this consumer contract. It should reveal missing EPM concepts, ambiguous process definitions, untestable relationships and migration issues without becoming EPM's semantic authority.
