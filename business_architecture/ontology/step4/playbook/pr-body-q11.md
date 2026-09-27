# DO NOT MERGE — awaiting Hamid's review

## What this PR does

Records the Q11 relationship-target disposition decision in the playbook.

## Change inventory

`business_architecture/ontology/ontology-playbook.md` only — one new
decision-log entry (Modeling), Q11:

- **Governing rule.** Every relationship mention gets a governed
  disposition; only process-to-process mentions become Step 4
  object-property triples. (Corrects the looser "every mention must
  resolve" framing.)
- **Five disposition types:** ResolvedToConcept, ParkedFutureConcept,
  StructuredFlowValue, ExternalGovernanceReference,
  DroppedAsNonProcessProse.
- **All nine unmatched targets dispositioned:** Network Design and
  Integrated Marketing Planning parked as future concepts; the
  Regional Backcasting assumption basis and Monthly Operating Plan as
  structured flow values; Data Governance as an external governance
  reference; Delegation of Authority and Trading Books structure
  parked; Develop/Update Strategy conditionally resolved only in
  proven Consumer VP context (no global lexical replacement); Serve
  to Customer dropped as non-process prose, recorded with reason.
- **Deferred:** new properties for governance references (designed at
  implementation time, not here).
- The row-level target-disposition report is named as the tracked
  pre-cutover instrument.

## Deliberately unchanged

- Everything else on main.

## How to review

Check each of the nine dispositions against your business read — especially
the conditional Develop/Update Strategy rule and the parked items' recorded
open questions.
