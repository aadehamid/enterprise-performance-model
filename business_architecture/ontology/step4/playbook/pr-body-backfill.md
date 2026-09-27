# DO NOT MERGE — awaiting Hamid's review

## What this PR does

Records Step 4 design decisions in the playbook, per the standing rule
that every design approach coming out of the Q&A lives in the playbook's
decision log — plus one parked roadmap item.

## Change inventory

`business_architecture/ontology/ontology-playbook.md` only:

1. **Decision log (Modeling) — backfilled Step 4 decisions:**
   - Q1 refinements: module-boundary rule, `ProcessDefinition` typing
     rule, `conceptKind`/`lifecycleStatus` as object properties,
     `taxonomyLevel` as derived metadata, terminology-notes migration.
   - Q2: `intake:` flag-day retirement + preconditions (no-consumer
     reconfirmation, conservation ledger, explicit release approval).
   - Q4: `core:usesInput` process-to-process edges.
   - Q6: `processHorizon` split into operatingMode / cadence /
     planningLevel, with the workbook evidence.
2. **Appendix A — new parked item:** the value-stream / capability /
   activity / event / decision layer. Parked as a post-1.0.0 roadmap
   item: represented eventually as governed overlays over the stable
   process backbone (not a second hierarchy), following the existing
   `linkedProcessIds` overlay pattern; hooks named (Q8 CapabilityKind,
   Step 6 PROV-O for events); revival trigger recorded.

## Deliberately unchanged

- Everything else, including the open versioning (PR #111), Q5
  (PR #112), and Q7 (PR #113) playbook PRs — those merge independently.

## How to review

Read the four decision-log entries and the Appendix A item. Check each
matches the decision as you understood it, and that the parked item's
revival trigger is the right bar.
