# Review rounds for the core 1.0.0 release (PR #249)

These are the reviewers' reports, saved as they wrote them.

| File | Reviewer | Commit reviewed | Verdict | What was fixed |
|---|---|---|---|---|
| `1-grok-round-1.md` | Cursor agent, Grok 4.6, full review | before 0543e76 | 4 findings confirmed, 3 rejected by the reviewer | 0543e76 |
| `2-grok-round-2.md` | Cursor agent, Grok 4.6, focused on 0543e76 | 0543e76 | 4 test gaps | 78d994c; three mutants of `build_core.py` then fail the tests |
| `3-pi-pr-review-1.md` | Pi (glm-5.3-flash), PR merge review | 78d994c | HOLD | 3ca5e44 |
| `4-pi-pr-review-2.md` | Pi, PR merge review | 3ca5e44 | HOLD | 6308941 |
| `5-pi-pr-review-3.md` | Pi, PR merge review | 6308941 | HOLD: The decision owner's approvals and #242 merging first; minor notes | 94a59ec |
| `6-pi-pr-review-4.md` | Pi, PR merge review | 94a59ec | HOLD: The decision owner's approvals and #242; minor notes | 5318256 |
| `7-pi-pr-review-5.md` | Pi, PR merge review | 5318256 | HOLD: The decision owner's approvals and #242 only | cleared by the decision owner's approval and the #242 merge |
| `8-pi-pr-review-6.md` | Pi, PR merge review of the 1.0.0 cut | c79615f | HOLD: tag claimed before it exists; two reports unsaved; attestation evidence line | the commit after c79615f |

The holds for the decision owner's approvals and #242 are cleared: #242 merged, and the decision owner's approvals are recorded in `decision-owner-answers/core-1-0-0-release.md`.
