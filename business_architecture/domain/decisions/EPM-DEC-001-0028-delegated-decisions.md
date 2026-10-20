# EPM-DEC-001-0028: Claude decides the open questions of emitting the ontology on the decision owner's behalf, from evidence

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-12 |
| Questions | One instruction, 2026-10-12; amended 2026-10-13 to cover Steps 5 to 12, 2026-10-18 on the reviewers, and 2026-10-20 on merging past the approval agent |
| Source | Claude Code session, 2026-10-12; recorded on #207 comment 6137222677 |

## Context

Until now every open question went to the decision owner, and nothing was marked Decided without their recorded words (AGENTS.md; this folder's README). The ontology still has Phase 1 batches, the release gate and Steps 5 to 12 ahead, each with questions. The decision owner asked Claude to keep going until the ontology is finished and to decide for them.

## Decision

Claude decides, on the decision owner's behalf, the open questions of emitting the ontology and updating its playbook, and, since the 2026-10-13 amendment, the open questions of Steps 5 to 12 of the build. Each delegated decision:

- rests on the evidence order in AGENTS.md: Marathon Petroleum (MPC) filings and public materials first, then U.S. refining peers' SEC filings, then downstream-specific industry sources. Generic frameworks are support only;
- uses light external search only to resolve an ambiguity the repository's evidence leaves open, and cites what it finds;
- is recorded where the question lives (a decision record, a review CSV row, or a backlog entry), with its evidence and the words "delegated under EPM-DEC-001-0028";
- counts as Decided, because this record is the decision owner's recorded decision to delegate. The decision owner can reverse any delegated decision; the reversal is recorded the same way.

Unchanged: every change still goes through a pull request, the checks in AGENTS.md and an independent review.

Scope and review: the work runs until the ontology is emitted and the ontology playbook is updated, and then, under the 2026-10-13 amendment, through Steps 5 to 12, with a log of what was done. Each PR gets at least one independent review before it opens and at most two: a full review of the branch, then, if it found something, a focused review of the fix. A fix after the second round gets `scripts/check.sh` and CI, and the PR body says it had no third review. After the PR opens, one PR reviewer reviews it the way the Cursor review bot did: one agent, no subagents, one MERGE or HOLD comment, and a new review after each push until merge. The decision owner named the reviewers in the same session: the Cursor agent on Grok 4.6 for the independent review, and Pi on `glm-5.3-flash:cloud` for the PR review (Kimi K3 first, until its usage ran out). *2026-10-13:* changed by the decision owner; see the amendment of 2026-10-18 below.

Merging: The decision owner asked "how do i remove the merge bock. I am going to bed and wont be around to merge". Claude answered with the steps to add the Claude Code permission rule `Bash(gh pr merge:*)`; the session then shows that rule added, and the decision owner replied "done". Claude merges a PR with a merge commit only when all of these hold for its current head: `scripts/check.sh` passes, every independent-review finding is fixed or answered, CI is green, and the PR reviewer's latest comment is MERGE. Claude records the merge on the PR. A PR that changes approval policy or routing, as this one does, still waits for the decision owner (`APPROVAL_POLICY.md`).

## Amendment, 2026-10-20: merging when the approval agent asks for a human

PR #308 had the Cursor review bot's MERGE on its head and passing CI, but the Cursor approval agent withheld its approving review as "medium risk", and ruleset 25440735 requires one approving review, so the PR waited until the decision owner merged it. The decision owner then wrote: "You should not be waiting for me to merge. What made you wait for me this time?" Asked whether Claude should merge such pull requests itself with an admin merge, they chose "Yes, admin-merge on MERGE + CI (Recommended)".

**What follows (Claude, under EPM-DEC-001-0028):**
1. **When Claude admin-merges.** Only when the PR reviewer's verdict on the current head is MERGE, the `checks` status has passed on that head, and the only unmet requirement is the approving review. Claude merges with `gh pr merge --admin --match-head-commit <head>`.
2. **Never past a HOLD or a failed check.** An admin merge is not a way round the PR reviewer, CI or the independent review; those rules are unchanged.
3. **Each one is visible.** Claude says on the PR, and in the session log, that it merged with admin privileges and why.
4. **APPROVAL_POLICY.md** still tells the approval agent when to ask for a human; the decision owner's answer is that, for those pull requests, they do not need to be the one who merges.
5. **Step 3c definition batches are the exception.** Their flow says the decision owner merges them (`step3c-review-handoff.md`, "Never merge — the decision owner merges."); this amendment does not change that.

## Amendment, 2026-10-18: who gives which review

On 2026-10-13, during the Steps 5 to 12 night run, the decision owner changed the reviewers named above: "the night run now default to Cursor bot for PR review and only use PI when cursor is not available." From then on the way-of-working skill's "Who reviews" table applied: while the Cursor bot is available, Pi gives the independent review and the bot gives the PR verdict; when it is not, the Cursor agent CLI gives the independent review and Pi the verdict. This record and AGENTS.md still named the Cursor agent for the independent review, and on 2026-10-18 Claude followed that text. The decision owner asked "why are you using indepdent cursor review. are you not supposed to use PI?". AGENTS.md now points to the table. The decision owner allowed Claude to merge that routing change itself: "Yes, merge it (Recommended)". The review rounds and merge conditions above are unchanged.

## Amendment, 2026-10-13: Steps 5 to 12

After `core` 1.0.0 was released (#249) and the playbook updated (#250), the original scope was complete. Claude listed the remaining steps: 5 (organizations and roles), 6 (interfaces and provenance), 7 (integration), 9 (full SHACL), 10 (publication), 11 (regression tests) and 12 (property-graph projection). Step 8 was done on 2026-09-17. Claude said the delegation covered none of them and asked whether to extend it. The decision owner extended it to Steps 5 to 12.

The amendment changes only the scope. Everything else in this record applies unchanged to Steps 5 to 12: the evidence order, the recording rule, the one or two review rounds per PR, the reviewers (changed 2026-10-13; see the amendment of 2026-10-18) and the merge conditions. A major release still needs the decision owner ("Major (including any deprecation): The decision owner. No exceptions", `step4/playbook/ontology-worklog.md`, "Who approves a release"). APPROVAL_POLICY.md still routes some PRs to a human.

Not part of the decision: in the message the decision owner answered, Claude proposed bringing three kinds of business facts to them in batches for approval, the way the Phase 1 register worked: the RACI assignments (Step 5), the KPI and Market Data and Commercial Risk definitions (Step 7), and the hosting and license choices (Step 10). The decision owner's words extend the scope only; they neither adopt nor reject that proposal. Those questions are delegated like any other in scope, and Claude may still choose to put them to the decision owner.

## Alternatives considered

- **Leave ready PRs for the decision owner to merge.** Rejected: The decision owner asked how to remove the block because they would be away, then replied "done".
- **Keep asking the decision owner each question.** Rejected by the decision owner's instruction.
- **Decide without recording.** Rejected: a later reader could not tell a delegated decision from an unreviewed assumption.

## The decision owner's recorded words

The decision owner gave the instruction in the Claude Code session on 2026-10-12 (#207 comment 6137222677, saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation.md`): "do you need my approval for anything. I want you to keep going until we finish the ontology. Make decisions for me using available evidence to make the best decision and light external searcch to resolve ambiguity. Can we work this way"

On merging, later in the same session (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-merge.md`): "how do i remove the merge bock. I am going to bed and wont be around to merge" (#207 comment 6137253866), then "done" (#207 comment 6138072666)

On scope and review (#207 comment 6137266851, saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-goal.md`): "go until we finish emiting the ontology and updating the ontology playbook. Keep a log of what you did. Keep using kimi for PR reviewers. Do you need independent reviewer. We should do independent reviewer at least once and at most two times"

On the reviewers (#207 comment 6137449831, saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-reviewers.md`): "so let us use kimi k3 for PR review and cursor agent from here with Grok 4.6 for independent reviews. cool?"; "kimi can review the PR until we merge we dont need subagents for this. we should do review like cursor bot was doing it."; "Can you try "ollama launch pi --model glm-5.3-flash:cloud""; "it looks like the two kimi got stuck. I ran out of usgae. So we will need to siwtch those to either cursor agent or pi depending on wether ther pre-PR or PR"

On merging past the approval agent, in the Claude Code session on 2026-10-20 (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-20-admin-merge.md`): "You should not be waiting for me to merge. What made you wait for me this time?" and "Yes, admin-merge on MERGE + CI (Recommended)"

On the extension, in the Claude Code session on 2026-10-13 (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`): "yes, extend the delegation to steps 5 to 12."

## Consequences

- AGENTS.md's rule on Decided and Approved points here.
- A delegated decision names its evidence, so the decision owner can audit or reverse it.
