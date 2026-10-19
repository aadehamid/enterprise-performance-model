HOLD

Merge reviewer's report for #249, third review round, against `AGENTS.md`, `REVIEW_STANDARDS.md` and `APPROVAL_POLICY.md`. The head is now 6308941, which answers the two open non-blocking notes from round 2.

**What I verified this round.** Figures from `python3 scripts/epm_facts.py counts` at 6308941 are unchanged and match the PR body: 824 emitting / 462 held of 1,318 mentions, 640 canonical facts, evidence gate GREEN with 347 PASS / 0 FAIL. Locally: 17 tests and 1,587 subtests pass, `build_core.py --verify` says "release package is current", and `epm_facts.py decisions` and `quotes` both report 0 problems. CI's `checks` job passed on 6308941. The new commit does two things, and both check out:

- The cardinality test now covers concept properties by declared domain as well as by use, so the unused `core:governanceStatus` is asserted (`test_build_core.py:235-239`); the suite passes with it.
- The former-names basis in `EPM-DEC-001-0029-core-1-0-0-release-design.md:25` now reads "label report v1.1 approved (the 90 rows it carries); the 14 rows v1.2 adds have their own recorded verdicts of 2026-09-24 and 2026-09-25". I checked: v1.2 adds exactly 14 rows (104 total = 90 carried + 14), CM-1-1-4 and CM-1-1-7 were decided 2026-09-24, and the 12 new-label rows were decided 2026-09-25. Accurate.

The PR body's round-3 additions also check out: it states which status rule applies to EPM-DEC-001-0029 — it stays Proposed until the decision owner's own words are recorded, because #242 is unmerged and a major release needs them without exceptions — and it lists honestly what stayed open. That answers the reconciliation question from round 2.

Eleven of thirteen findings across the three rounds now stand resolved. Two remain, and both clear the same way.

## Blocking

1. **The decision owner's recorded decisions are still absent.** `EPM-DEC-001-0029-core-1-0-0-release-design.md:5` (Status: Proposed), `:42` ("The release PR waits for all three"), `business_architecture/ontology/step4/release-checklist.md:76,80,81` (unchecked the decision owner's gates: ledger approval, fresh no-consumer attestation, release approval), and the PR body's "What waits for the decision owner". No approval comment or recorded words exist on #249, and #242 is still open. Fix: nothing for the branch to change. The decision owner merges #242 (the delegation), then records their decisions on the design, the ledger, the attestation and the release; only then does `release-checklist.md:82`'s cut list run.

2. **#242 must merge first, and this branch then rebases.** Re-verified this round against #242's new head 368f0d2: it merges clean onto current main, and a later merge of this PR still conflicts in `business_architecture/domain/decisions/README.md` (both PRs add a row at line 40; #242 also rewrites line 6). The two `delegation.md` files remain byte-identical, so that part is safe. Fix: after #242 merges, rebase this branch, put the 0029 row after the 0028 row in the decisions README, and update the three "pending in #242" phrases (record lines 5, 8, 46) and the PR body to the merged state. The PR body already records which rule applies, so only the stale phrase needs to go.

## Non-blocking

- The PR body's figures line still cites `commit 78d994c`; the head is 6308941 and the figures are unchanged there. Quote the current head when the body is next touched.
- The shipped `label-dispositions.csv` still marks CM-1-1-4 and CM-1-1-7 `row_status=NEW-needs-review` while their Decision column records approval (the decision owner, 2026-09-24). The builder reads `proposed_disposition`, so the build is right; the shipped copy carries a stale status column.
- The ledger header discloses that the source-link split moved from the census's 737 tokens / 9 annotations to 736 links / 8 annotations on the current baseline, but names no row for the one dropped annotated token. For the decision owner's ledger review, one sentence naming that row would close the gap.
- The round-1 and round-2 review results (Grok 4.6; the mutated-builder runs) exist only in the PR body; earlier Step 4 work saved its review batches under `step4/review-evidence/`. Same treatment would make the rounds auditable.
- At review time the Cursor security reviewer's run was still pending; per `APPROVAL_POLICY.md` it is not a gate. The `checks` job on 6308941 passed.