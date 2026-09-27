# DO NOT MERGE — awaiting Hamid's review

## What this PR does

Records the Q12 ambiguous-target decision in the playbook — the twelfth
and final Step 4 question.

## Change inventory

`business_architecture/ontology/ontology-playbook.md` only — one new
decision-log entry (Modeling), Q12:

- **Governing rule.** A lexical match is not a semantic resolution.
  Resolve only on stable identifier or approved contextual evidence;
  otherwise `AmbiguousDeferred` with candidates, rationale, and review
  trigger — no triple emitted.
- **Decision ladder:** stable ID → approved contextual evidence
  sufficient to identify exactly one governed target → scoped
  historical alias → defer. A label match is a candidate filter, not
  a resolution step — resolutions are recorded as concept slugs, per
  the standing identity lock.
- **`AmbiguousDeferred`** added as the sixth disposition type.
- **Amendment to Q11:** the bare Brand Imaging `Network Design`
  mention moves from ParkedFutureConcept to AmbiguousDeferred.
- **Report fields** for the row-level disposition report and
  **per-disposition emission rules** for the future promotion script.

## Deliberately unchanged

- Everything else on main (Q11's merged dispositions stand, as amended
  above).

## How to review

Confirm the ladder order feels right and the Network Design
reclassification reads correctly. This closes out Q1–Q12.
