# EPM-DEC-001-0003: Phase 1 tracking and batch format

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-05 |
| Questions | Q3, Q4 |
| Source | Grilling session on the handover plan |

## Context

Phase 1 corrects the source workbook for the held Step 4 rows: G3 Section B (96 rows), G1b pairs, S&T recommendations, triggers, precedes/follows holds and governed-by superseded approvals.

## Decision

Keep `step4/source-workbook-backlog.md` as the row ledger. Open one GitHub issue per backlog section to track progress, each linking to its section. Review in batches of about 12 rows, grouped by target process, with one review file and one PR per batch.

## Alternatives considered

Issues only; the repo file only; batches by row number.

## Hamid's recorded words

Round 1: "Agree with the rest."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with Hamid). Hamid answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." He also stated: "If i dont comment on a question, it means I am aligned." A question he did not comment on is therefore recorded as agreed with the recommendation.

## Evidence

`business_architecture/ontology/step4/source-workbook-backlog.md`; `docs/agents/issue-tracker.md`.
