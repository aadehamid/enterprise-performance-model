# EPM-DEC-001-0028: Claude decides open questions on Hamid's behalf, from evidence

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-12 |
| Questions | One instruction, 2026-10-12 |
| Source | Claude Code session, 2026-10-12; recorded on [#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6137222677) |

## Context

Until now every open question went to Hamid, and nothing was marked Decided without his recorded words (AGENTS.md; this folder's README). The ontology still has Phase 1 batches, the release gate and Steps 5 to 12 ahead, each with questions. Hamid asked Claude to keep going until the ontology is finished and to decide for him.

## Decision

Claude decides open project questions on Hamid's behalf. Each delegated decision:

- rests on the evidence order in AGENTS.md: Marathon Petroleum (MPC) filings and public materials first, then U.S. refining peers' SEC filings, then downstream-specific industry sources. Generic frameworks are support only;
- uses light external search only to resolve an ambiguity the repository's evidence leaves open, and cites what it finds;
- is recorded where the question lives (a decision record, a review CSV row, or a backlog entry), with its evidence and the words "delegated under EPM-DEC-001-0028";
- counts as Decided, because this record is Hamid's recorded decision to delegate. Hamid can reverse any delegated decision; the reversal is recorded the same way.

Unchanged: every change still goes through a pull request, the checks in AGENTS.md and an independent review.

Merging: Hamid asked how to remove the merge block because he would be away, then added the Claude Code permission rule `Bash(gh pr merge:*)`. Claude merges a PR with a merge commit only after `scripts/check.sh` passes, every independent-review finding is fixed or answered, and CI is green, and records the merge on the PR.

## Alternatives considered

- **Leave ready PRs for Hamid to merge.** Rejected: Hamid will be away and removed the block for that reason.
- **Keep asking Hamid each question.** Rejected by Hamid's instruction.
- **Decide without recording.** Rejected: a later reader could not tell a delegated decision from an unreviewed assumption.

## Hamid's recorded words

Hamid gave the instruction in the Claude Code session on 2026-10-12 ([#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6137222677), saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation.md`): "do you need my approval for anything. I want you to keep going until we finish the ontology. Make decisions for me using available evidence to make the best decision and light external searcch to resolve ambiguity. Can we work this way"

On merging, later in the same session ([#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6137253866), saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-merge.md`): "how do i remove the merge bock. I am going to bed and wont be around to merge"

## Consequences

- AGENTS.md's rule on Decided and Approved points here.
- A delegated decision names its evidence, so Hamid can audit or reverse it.
