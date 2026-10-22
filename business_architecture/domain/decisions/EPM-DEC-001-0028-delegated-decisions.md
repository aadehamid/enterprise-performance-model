# EPM-DEC-001-0028: Claude decides the open questions of emitting the ontology on the decision owner's behalf, from evidence

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-12 |
| Questions | One instruction, 2026-10-12; amended 2026-10-13 to cover Steps 5 to 12, 2026-10-18 on the reviewers, 2026-10-20 on merging past the approval agent and on the PR verdict while Cursor is out of usage, and 2026-10-22 on the review rounds and the PR reviewer |
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

Scope and review: the work runs until the ontology is emitted and the ontology playbook is updated, and then, under the 2026-10-13 amendment, through Steps 5 to 12, with a log of what was done. Each PR gets at least one independent review before it opens and at most two: a full review of the branch, then, if it found something, a focused review of the fix. A fix after the second round gets `scripts/check.sh` and CI, and the PR body says it had no third review. *2026-10-22:* replaced: a fix after the second round also gets a Pi quick check, and the PR body says which rounds and quick checks ran; see the amendment of 2026-10-22 below. After the PR opens, one PR reviewer reviews it the way the Cursor review bot did: one agent, no subagents, one MERGE or HOLD comment, and a new review after each push until merge. The decision owner named the reviewers in the same session: the Cursor agent on Grok 4.6 for the independent review, and Pi on `glm-5.3-flash:cloud` for the PR review (Kimi K3 first, until its usage ran out). *2026-10-13:* changed by the decision owner; see the amendment of 2026-10-18 below.

Merging: The decision owner asked "how do i remove the merge bock. I am going to bed and wont be around to merge". Claude answered with the steps to add the Claude Code permission rule `Bash(gh pr merge:*)`; the session then shows that rule added, and the decision owner replied "done". Claude merges a PR with a merge commit only when all of these hold for its current head: `scripts/check.sh` passes, every independent-review finding is fixed or answered, CI is green, and the PR reviewer's latest comment is MERGE. Claude records the merge on the PR. A PR that changes approval policy or routing, as this one does, still waits for the decision owner (`APPROVAL_POLICY.md`). *2026-10-20, see the amendment below on merging when the approval agent asks for a human:* the decision owner need not be the one who merges such a pull request once the PR reviewer's MERGE is on its head and `checks` passed; Step 3c definition batches still wait for them.

## Amendment, 2026-10-22: review rounds, and the PR reviewer back to Cursor

In session 7 (2026-10-21) Claude ran more than two independent (Pi) rounds on several pull requests (for example #337, by its PR body). It had read the decision owner's "keep it uncapped, do the full sweep first" (`answers-2026-10-21-review-uncapped.md`) as covering the independent review; that answer covered PR verdict rounds only, as Claude recorded on #337. The session 7 morning summary asked whether to keep the two-round limit. Claude proposed at most two full Pi rounds per pull request, then a Pi quick check of each later fix commit, with PR verdict rounds uncapped. The decision owner answered "I agree".

During the same session the Cursor bot was out of usage, and Codex (through `herdr-review.sh`) gave the PR verdict. When the bot came back on 2026-10-21, the decision owner kept Codex for the rest of that goal: "for the rest of this work. Let us continue to use CODEX for this goal. for consistentcy. We can siwtch back to cursor cli next goal". At the start of the next goal, on 2026-10-22, Claude asked whether Pi gives the independent review and the Cursor bot the PR verdict, with the Cursor agent CLI on Auto as the bot's stand-in. The decision owner chose "Yes, go (Recommended)".

**What follows (Claude, under EPM-DEC-001-0028):**
1. **Independent review rounds.** Round 1 is a full Pi review of the branch. Round 2, only if round 1 found something, is a full Pi review of the fix. Each fix commit after round 2 gets a Pi quick check of that commit only, plus `scripts/check.sh` and CI. The PR body says which rounds and quick checks ran.
2. **PR verdict rounds are uncapped.** The PR reviewer reviews every push until it posts MERGE on the head.
3. **The PR reviewer is the Cursor bot again,** from 2026-10-22. If the bot's check has not started 8 minutes after a push, or it has posted no verdict 9 minutes after the push, the Cursor agent CLI on Auto gives the verdict (`herdr-review.sh --kind cursor --model auto`), posted word for word as the amendment of 2026-10-20 (later) says, and stays the PR reviewer for the rest of that pull request, as the way-of-working skill's switch rule says. Pi gives the independent review in both cases, so the merged commit's two reviews come from different tools. This replaces the fallback of the amendment of 2026-10-18 (the Cursor agent CLI as independent reviewer and Pi as PR reviewer).

## Amendment, 2026-10-20 (later): the PR verdict while Cursor is out of usage

The decision owner said the Cursor review still matters: "But cursor still ask to merge. correct? that is important that cursor finds no issue". Later that day Cursor's on-demand usage ran out: the review bot, the approval agent and Bugbot failed to start on PR #313's new head, and the Cursor agent CLI on Grok 4.7 refused for the same reason. The decision owner first chose "Use cursor agent cli with GROK 4.7 as the reviwer." and then, when Grok was out too, "Cursor CLI on Auto". Claude Code's safety check refused a merge on a verdict posted from the decision owner's account; they chose "Allow the merge script (Recommended)" and "Allow me to post reviews (Recommended)" and added the permission rules `Bash(~/.claude/skills/way-of-working/scripts/merge-on-verdict.sh:*)` and `Bash(gh pr review:*)`.

**What follows (Claude, under EPM-DEC-001-0028):**
1. **While the Cursor bot is out of usage, the Cursor agent CLI on Auto gives the PR verdict** (`herdr-review.sh --kind cursor --model auto`). Its report starts with MERGE or HOLD and the commit it reviewed. This replaces Pi as the PR reviewer named by the amendment of 2026-10-18 for as long as the bot is out. Pi gives the independent review, as when the bot runs, so the merged commit's two reviews still come from different tools.
2. **Claude posts the report on the pull request word for word,** as a review comment with a line naming the reviewer, and merges on its MERGE plus passing `checks` with `merge-on-verdict.sh --bot <the decision owner's account> --admin-if-only-review`. A HOLD is fixed and the new head reviewed again.
3. **When the bot runs again,** it gives the PR verdict as before.


## Amendment, 2026-10-20: merging when the approval agent asks for a human

PR #308 had the Cursor review bot's MERGE on its head and passing CI, but the Cursor approval agent withheld its approving review as "medium risk", and ruleset 25440735 requires one approving review, so the PR waited until the decision owner merged it. The decision owner then wrote: "You should not be waiting for me to merge. What made you wait for me this time?" Asked whether Claude should merge such pull requests itself with an admin merge, they chose "Yes, admin-merge on MERGE + CI (Recommended)".

**What follows (Claude, under EPM-DEC-001-0028):**
1. **When Claude admin-merges.** Only when the PR reviewer's verdict on the current head is MERGE, the `checks` status has passed on that head, and the only unmet requirement is the approving review. Claude merges with `gh pr merge --admin --match-head-commit <head>`, through way-of-working's `merge-on-verdict.sh --admin-if-only-review` (personal-agent-skills #41), which first checks that every check on the head passed, that the head is not behind `main` where the rules require an up-to-date branch, and that no current review thread is unresolved. This ruleset does not require an up-to-date branch, so a branch behind `main` merges without admin privileges too.
2. **Never past a HOLD or a failed check.** An admin merge is not a way round the PR reviewer, CI or the independent review; those rules are unchanged.
3. **Each one is visible.** Claude says on the PR, and in the session log, that it merged with admin privileges and why.
4. **APPROVAL_POLICY.md** still tells the approval agent when to ask for a human; the decision owner's answer is that, for those pull requests, they do not need to be the one who merges.
5. **Step 3c definition batches are the exception.** Their flow says the decision owner merges them (`step3c-review-handoff.md`, "Never merge — the decision owner merges."); this amendment does not change that.

## Amendment, 2026-10-18: who gives which review

On 2026-10-13, during the Steps 5 to 12 night run, the decision owner changed the reviewers named above: "the night run now default to Cursor bot for PR review and only use PI when cursor is not available." From then on the way-of-working skill's "Who reviews" table applied: while the Cursor bot is available, Pi gives the independent review and the bot gives the PR verdict; when it is not, the Cursor agent CLI gives the independent review and Pi the verdict. *2026-10-20: while Cursor is out of usage, see the later amendment of that date above.* *2026-10-22: replaced; when the bot is not available, the Cursor agent CLI on Auto gives the verdict and Pi still gives the independent review (amendment of 2026-10-22 above).* This record and AGENTS.md still named the Cursor agent for the independent review, and on 2026-10-18 Claude followed that text. The decision owner asked "why are you using indepdent cursor review. are you not supposed to use PI?". AGENTS.md now points to the table. The decision owner allowed Claude to merge that routing change itself: "Yes, merge it (Recommended)". The review rounds and merge conditions above are unchanged.

## Amendment, 2026-10-13: Steps 5 to 12

After `core` 1.0.0 was released (#249) and the playbook updated (#250), the original scope was complete. Claude listed the remaining steps: 5 (organizations and roles), 6 (interfaces and provenance), 7 (integration), 9 (full SHACL), 10 (publication), 11 (regression tests) and 12 (property-graph projection). Step 8 was done on 2026-09-17. Claude said the delegation covered none of them and asked whether to extend it. The decision owner extended it to Steps 5 to 12.

The amendment changes only the scope. Everything else in this record applies unchanged to Steps 5 to 12: the evidence order, the recording rule, the one or two review rounds per PR (*2026-10-22:* plus quick checks of later fixes; see the amendment of 2026-10-22), the reviewers (changed 2026-10-13; see the amendment of 2026-10-18) and the merge conditions. A major release still needs the decision owner ("Major (including any deprecation): The decision owner. No exceptions", `step4/playbook/ontology-worklog.md`, "Who approves a release"). APPROVAL_POLICY.md still routes some PRs to a human.

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

On the PR verdict while Cursor is out of usage, in the Claude Code session on 2026-10-20 (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-20-reviewer-cursor-out.md`): "But cursor still ask to merge. correct? that is important that cursor finds no issue"; then "Use cursor agent cli with GROK 4.7 as the reviwer."; then "Cursor CLI on Auto"; then "Allow the merge script (Recommended)" and "Allow me to post reviews (Recommended)".

On the review rounds in session 7, in the Claude Code session on 2026-10-21 (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-21-review-uncapped.md`): "keep it uncapped, do the full sweep first". On the review rounds, in the Claude Code session on 2026-10-22 (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`): "I agree". On keeping Codex for the Customer goal, in the session of 2026-10-21 (saved in `answers-2026-10-21-reviewer-codex.md` in the same folder): "for the rest of this work. Let us continue to use CODEX for this goal. for consistentcy. We can siwtch back to cursor cli next goal". On the reviewers for the next goal, on 2026-10-22 (saved in `answers-2026-10-22-morning.md`): "Yes, go (Recommended)".

On the extension, in the Claude Code session on 2026-10-13 (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`): "yes, extend the delegation to steps 5 to 12."

## Consequences

- AGENTS.md's rule on Decided and Approved points here.
- A delegated decision names its evidence, so the decision owner can audit or reverse it.
