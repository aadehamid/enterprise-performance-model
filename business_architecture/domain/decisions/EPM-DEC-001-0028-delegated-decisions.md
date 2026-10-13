# EPM-DEC-001-0028: Claude decides the open questions of emitting the ontology on Hamid's behalf, from evidence

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-12 |
| Questions | One instruction, 2026-10-12; amended 2026-10-13 to cover Steps 5 to 12 |
| Source | Claude Code session, 2026-10-12; recorded on [#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6137222677) |

## Context

Until now every open question went to Hamid, and nothing was marked Decided without his recorded words (AGENTS.md; this folder's README). The ontology still has Phase 1 batches, the release gate and Steps 5 to 12 ahead, each with questions. Hamid asked Claude to keep going until the ontology is finished and to decide for him.

## Decision

Claude decides, on Hamid's behalf, the open questions of emitting the ontology and updating its playbook, and, since the 2026-10-13 amendment, the open questions of Steps 5 to 12 of the build. Each delegated decision:

- rests on the evidence order in AGENTS.md: Marathon Petroleum (MPC) filings and public materials first, then U.S. refining peers' SEC filings, then downstream-specific industry sources. Generic frameworks are support only;
- uses light external search only to resolve an ambiguity the repository's evidence leaves open, and cites what it finds;
- is recorded where the question lives (a decision record, a review CSV row, or a backlog entry), with its evidence and the words "delegated under EPM-DEC-001-0028";
- counts as Decided, because this record is Hamid's recorded decision to delegate. Hamid can reverse any delegated decision; the reversal is recorded the same way.

Unchanged: every change still goes through a pull request, the checks in AGENTS.md and an independent review.

Scope and review: the work runs until the ontology is emitted and the ontology playbook is updated, and then, under the 2026-10-13 amendment, through Steps 5 to 12, with a log of what was done. Each PR gets at least one independent review before it opens and at most two: a full review of the branch, then, if it found something, a focused review of the fix. A fix after the second round gets `scripts/check.sh` and CI, and the PR body says it had no third review. After the PR opens, one PR reviewer reviews it the way the Cursor review bot did: one agent, no subagents, one MERGE or HOLD comment, and a new review after each push until merge. Hamid named the reviewers in the same session: the Cursor agent on Grok 4.6 for the independent review, and Pi on `glm-5.3-flash:cloud` for the PR review (Kimi K3 first, until its usage ran out).

Merging: Hamid asked "how do i remove the merge bock. I am going to bed and wont be around to merge". Claude answered with the steps to add the Claude Code permission rule `Bash(gh pr merge:*)`; the session then shows that rule added, and Hamid replied "done". Claude merges a PR with a merge commit only when all of these hold for its current head: `scripts/check.sh` passes, every independent-review finding is fixed or answered, CI is green, and the PR reviewer's latest comment is MERGE. Claude records the merge on the PR. A PR that changes approval policy or routing, as this one does, still waits for Hamid (`APPROVAL_POLICY.md`).

## Amendment, 2026-10-13: Steps 5 to 12

After `core` 1.0.0 was released (#249) and the playbook updated (#250), the original scope was complete. Claude listed the remaining steps: 5 (organizations and roles), 6 (interfaces and provenance), 7 (integration), 9 (full SHACL), 10 (publication), 11 (regression tests) and 12 (property-graph projection). Step 8 was done on 2026-09-17. Claude said the delegation covered none of them and asked whether to extend it. Hamid extended it to Steps 5 to 12.

The amendment changes only the scope. Everything else in this record applies unchanged to Steps 5 to 12: the evidence order, the recording rule, the one or two review rounds per PR, the reviewers and the merge conditions. A major release still needs Hamid ("Major (including any deprecation): Hamid. No exceptions", `step4/playbook/ontology-worklog.md`, "Who approves a release"). APPROVAL_POLICY.md still routes some PRs to a human.

In the message Hamid answered, Claude proposed bringing three kinds of business facts to him in batches for approval, the way the Phase 1 register worked: the RACI assignments (Step 5), the KPI and Market Data and Commercial Risk definitions (Step 7), and the hosting and license choices (Step 10). Claude follows that practice for those facts.

## Alternatives considered

- **Leave ready PRs for Hamid to merge.** Rejected: Hamid asked how to remove the block because he would be away, then replied "done".
- **Keep asking Hamid each question.** Rejected by Hamid's instruction.
- **Decide without recording.** Rejected: a later reader could not tell a delegated decision from an unreviewed assumption.

## Hamid's recorded words

Hamid gave the instruction in the Claude Code session on 2026-10-12 ([#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6137222677), saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation.md`): "do you need my approval for anything. I want you to keep going until we finish the ontology. Make decisions for me using available evidence to make the best decision and light external searcch to resolve ambiguity. Can we work this way"

On merging, later in the same session (saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-merge.md`): "how do i remove the merge bock. I am going to bed and wont be around to merge" ([#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6137253866)), then "done" ([#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6138072666))

On scope and review ([#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6137266851), saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-goal.md`): "go until we finish emiting the ontology and updating the ontology playbook. Keep a log of what you did. Keep using kimi for PR reviewers. Do you need independent reviewer. We should do independent reviewer at least once and at most two times"

On the extension, in the Claude Code session on 2026-10-13 (saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-steps-5-12.md`): "yes, extend the delegation to steps 5 to 12."

On the reviewers ([#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6137449831), saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-reviewers.md`): "so let us use kimi k3 for PR review and cursor agent from here with Grok 4.6 for independent reviews. cool?"; "kimi can review the PR until we merge we dont need subagents for this. we should do review like cursor bot was doing it."; "Can you try "ollama launch pi --model glm-5.3-flash:cloud""; "it looks like the two kimi got stuck. I ran out of usgae. So we will need to siwtch those to either cursor agent or pi depending on wether ther pre-PR or PR"

## Consequences

- AGENTS.md's rule on Decided and Approved points here.
- A delegated decision names its evidence, so Hamid can audit or reverse it.
