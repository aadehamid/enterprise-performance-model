# EPM–PPC Update Plan for Existing EPM Artifacts

> **Archived — executed 2026-10-02. Provenance only, not a canonical artifact.** The changes below were applied in FOUND-000 v2.5 and FOUND-001 to 006 v2.1. See the v2.5 change note in the [Master Index](../EPM-FOUND-000.md). Do not use this file as a to-do list.

**Purpose:** Identify targeted EPM changes after the PPC comparison. This is a change plan, not a replacement for canonical EPM artifacts.

## EPM-FOUND-000 — Master Index
Add:
- PPC as a downstream proving-ground consumer;
- a planned/published EPM consumer-contract/release concept;
- distinction between EPM release authority and consumer instances;
- process-conformance as an implementation/use case of process authority;
- links to the proposed EPM-ARCH-PPC documents.

Do not change existing source-precedence or authority rules.

## EPM-FOUND-001 — Enterprise Business Architecture
Add:
- explicit statement that machine-readable process authority can be consumed as a designed-process contract;
- process-instance/conformance relationship;
- optional stable transition/exception semantics where process schemas support them.

Do not make PPC instances part of EPM business architecture.

## EPM-FOUND-002 — Performance and Data Architecture
Add:
- process-conformance metrics as possible diagnostic inputs;
- consumer-release mapping for KPI/data-product contracts;
- stronger statement that downstream implementations can vary while KPI semantic identity remains governed.

## EPM-FOUND-003 — Semantic Model
Add:
- `conforms to designed process` / process-instance semantics if approved;
- consumer-extension namespace pattern;
- release/deprecation semantics for external consumers.

Review the existing CandidateKPI wording against the Master Index's machine-ontology rule before making changes; do not create ontology classes merely from the narrative taxonomy.

## EPM-FOUND-004 — Ontology Design
Add:
- publishable ontology/SHACL release packaging;
- semantic-version/deprecation/migration guidance;
- competency-question bundle;
- external consumer extension pattern.

Preserve Turtle-in-Git as machine SoT.

## EPM-FOUND-005 — Measurement and KPI Model
Add:
- explicit machine-consumable promotion/validation contract for external implementations;
- KPI dependency manifest fields expected by consumers;
- process-conformance/diagnostic metric classification guidance.

## EPM-FOUND-006 — Data Product and Consumption Model
Add:
- versioned data-product portfolio contract for consumers;
- implementation mapping: EPM product concept vs consumer implementation;
- optional OpenMetadata reference implementation without making it enterprise authority.

## business_architecture/business_process and schema
Evaluate schema extensions for:
- stable activity/event IDs;
- transition/precedence;
- trigger/end conditions;
- decisions;
- valid exception/alternate paths;
- measurement hooks.

Only add fields that are reusable EPM semantics, not PPC-specific simulation details.

## ontology/
Add release packaging and automated validation around `stage2_enterprise_kpi_ontology.ttl`.
Recommended outputs:
- versioned Turtle;
- SHACL;
- release manifest;
- competency-query/tests;
- change/deprecation notes.

## architecture/README.md
Keep Meaning-vs-Compute unchanged.
Add PPC as an example consumer that must preserve:
`ontology IRI → KPI Store row → Metric View → MEASURE()`.

## EPM Homelab
Do not move it to PPC.
Update its ADRs/build plan to distinguish:
- educational runtime;
- governed EPM reference implementation candidates;
- PPC integrated proving-ground implementations.

Review PPC-aligned tools already present before adding duplicates.

## Metadata Integration
Evaluate an OpenMetadata reference path alongside the existing Purview/Unity Catalog/Bigeye architecture. The goal is to demonstrate responsibilities, not replace enterprise platform choices.

## New governed artifact recommended
Create a small **EPM Consumer Release Contract** (based on EPM-ARCH-PPC-001) and register it in EPM-FOUND-000 once approved.

## New reference architecture recommended
Create a **Governed EPM Reference Implementation** document that identifies which Homelab patterns are promoted and which remain educational experiments.
