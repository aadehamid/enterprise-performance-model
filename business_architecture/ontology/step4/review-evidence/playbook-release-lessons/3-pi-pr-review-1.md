HOLD

## Blocking finding

1. `business_architecture/ontology/step4/playbook/ontology-worklog.md:87` — the Step 5 row's status changed from `Planned` to `Planned (after Step 11)`, but nothing records that sequencing. Checked: EPM-DEC-001-0015 (the record the row cites) decides Step 5's content, not its place in the plan; EPM-DEC-001-0019 (Step 11) says to re-run coverage after each module; EPM-DEC-001-0020 puts only Step 12 after Step 11 (`epm_facts.py find "after Step 11"` returns exactly those two hits). The PR body says the step table "marks Phase 1 and the R1 release done" and does not mention this third edit. The change also sits in the review-fix commit 3434721, whose summary in the body does not cover it. And the worklog note two lines under the table (`ontology-worklog.md:98`) still says "The plan order is otherwise unchanged", which this edit contradicts if it stands.
   Fix: either (a) revert the row to `Planned`, or (b) record the sequencing (a dated amendment or a named decision record), update the "The plan order is otherwise unchanged" note to match, sweep any dependent statements per the before-push rules, and say the change in the PR body.

## Non-blocking notes

1. The #250 review transcripts are not saved. #249 saved its rounds as numbered files under `step4/review-evidence/core-1.0.0-release/`, and the body leans on #249's rounds as the source of the playbook additions. Saving rounds 1 and 2 of #250 the same way would keep that trail uniform. (Body statements satisfy the standing rule, so this is a suggestion.)
2. Playbook, `ontology-playbook.md:1366-1367`: the release-candidate paragraph lists the candidate label in `owl:versionInfo`, the version IRI and the catalog, but the #249 package also carried the rc label in the manifest (`2-grok-round-2.md`, finding 2). Consider adding it to the list.
3. Pre-existing, outside this diff: `ontology-worklog.md:1015-1023` ("#204 triggers batch 1") still says "Pending merge of the batch PR ... #204 closes when it merges" — that batch merged in #235. Same stale-status class this PR fixes elsewhere and now codifies; worth a one-line sweep in a later PR.

## What I verified (all passes)

- Playbook additions match what #249's reviews record (release candidate until approved; destination tests and mutants; cardinality on every property including unused ones; ConceptScheme typing; dates set at the cut). Wording is company-neutral, so the review rule that keeps the playbook a method holds.
- The decision log leads with "core 1.0.0 released (EPM-DEC-001-0029, 2026-10-13)" and runs newest first; the moved entry keeps its wording, and only its status lines changed.
- Landed-state claims are true: #249 merged 2026-10-13T11:57Z as d8b16e1; the annotated tag `core-v1.0.0` exists and points at d8b16e1; the six sweep PRs (#239, #241, #243, #244, #247, #248) are merged; #242 merged. The "are in the playbook" pointer lands with this PR's playbook commit, so it is true at the merge commit that carries both files.
- Figures: `python3 scripts/epm_facts.py counts` at head prints `commit 3434721`, matching the body's quoted line. Phase 1 counts 276 rows, 51 held (the P1 row's figure). Canonical facts 640 (counts and the release's `counts.json`); 1,003 blank nodes resolved (`counts.json`); the moved entry's other figures match the #249 evidence (5,571 = 5,571 in `conservation.csv`; 8 code-list schemes in review record 4).
- The decision owner's attestation quote exists exactly in `step4/review-evidence/decision-owner-answers/core-1-0-0-release.md`, and EPM-DEC-001-0029 reads "Decided (the decision owner approved, 2026-10-13)", so "approved by the decision owner" in the step table and worklog traces to their recorded words.
- CI: checks, lychee (both jobs) and Cursor Bugbot all SUCCESS, confirming the body's `scripts/check.sh` claim.