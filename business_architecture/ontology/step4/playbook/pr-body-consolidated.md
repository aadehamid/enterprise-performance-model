# DO NOT MERGE — awaiting Hamid's review

## What this PR does

Consolidates the five overlapping Step 4 playbook PRs (#111–#115) into
one clean change, with the approved review corrections applied.
Supersedes #111, #112, #113, #114, #115 (to be closed after this is
reviewed).

## Change inventory

`business_architecture/ontology/ontology-playbook.md` only.

**Decision log (Modeling) — final Step 4 decisions:**

- Ontology identity: `core` IRI, per-release version IRI, explicit
  `owl:Ontology` header (title, description, versionIRI/versionInfo,
  issued, creator, license), stable unversioned term IRIs.
- First formal version: `core` 1.0.0 — first release with governed
  properties instead of provisional `intake:` annotations.
- Q1 refinements: module-boundary rule, `ProcessDefinition` typing rule,
  `conceptKind`/`lifecycleStatus` as object properties, `taxonomyLevel`
  as derived metadata, terminology-note migration rules.
- Q2: `intake:` flag-day retirement + preconditions (no-consumer
  reconfirmation, per-predicate conservation ledger, explicit release
  approval).
- Q4: process dependency links — `core:dependsOnOutputOf` (consumer →
  producer) with inverse `core:providesInputTo`; structured flow values
  state what moves; `consumes`/`produces` reserved for future identified
  InformationObjects.
- Q5: flows as governed structured values now; InformationObject catalog
  deferred until an artifact-specific consumer need exists.
- Q6: `processHorizon` split into `operatingMode` / `cadence` /
  `planningLevel`; periodic-only rows stay cadence-unspecified.
- Q7: `responsible_domain` as interim governed literal; Step 5 maps to
  governed organization/role/ResponsibilityAssignment references where
  the operating model evidences the relationship (some labels are
  business domains, not org units).
- Q8: `conceptKind` as controlled SKOS scheme (Process / Capability /
  StructuralAnchor kinds); CM-1-3-1-6 classification stays parked.

**Appendix A — parked layer:** the full business-architecture hierarchy
(domain > value stream > stages, capabilities, activities, events,
decisions, KPIs, data products) as future governed overlays over the
stable backbone, with each layer's home and the revival trigger.
Distinguishes `core:CapabilityKind` (classification value) from the
future `core:BusinessCapability` class (architecture entity with
`realizedBy` links).

## Review corrections applied (from the approved feedback)

1. Q4 property renamed `usesInput` → `dependsOnOutputOf` /
   `providesInputTo` (a process is not an input; its output is).
2. Q7 wording: Step 5 mapping only where the operating model evidences
   the relationship.
3. CapabilityKind vs BusinessCapability split.

## Deliberately unchanged

- Everything else in the playbook. No ontology implementation, no
  `intake:` cutover, no merges of the superseded PRs.

## How to review

Read the decision-log entries and the Appendix A item end to end. Check
each decision matches your understanding, especially the three corrected
items above. The superseded PRs (#111–#115) stay open until you approve
this one.
