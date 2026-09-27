# DO NOT MERGE — awaiting Hamid's review

## What this PR does

Documents the Step 4 Q5 flow-modeling decision in the playbook's
decision log (Modeling), as one of the design considerations the team
needs to see.

## Change inventory

`business_architecture/ontology/ontology-playbook.md` only — one new
decision-log entry:

- **Flow modeling depth (2026-09-22).** Step 4 captures flows as
  governed structured values on the input/output links (controlled,
  consistently-spelled flow names, no new nodes). Minting
  InformationObject nodes (~1,900) deferred — it is a data-governance
  project (identity, dedup, ownership, lifecycle) no Step 4 competency
  question or consumer requires. Revisit trigger: a real use case that
  needs to trace a specific artefact; then mint that flow deliberately,
  one at a time. Notes the composition with Q4 (`core:usesInput` links
  processes; the structured value says what travels on the link).

## Deliberately unchanged

- Everything else in the playbook, including the versioning material
  from PR #111 (open separately).

## How to review

Read the new entry. Check: (a) it matches the decision as you
understood it; (b) the revisit trigger is the right bar for minting
flow nodes later.
