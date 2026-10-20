# EPM-DEC-001-0050: PRs #262, #266 and #269 accepted as merged, a ruleset on `main` while the repository is public, and the eight measure categories approved

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-19; how each is carried out delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Decision package 1 (`decision-packages/2026-10-14/pr-reviews-262-266-269.md`, questions 1 and 2); the eight measure categories of the `kpi` module (EPM-DEC-001-0042), on which MPC-P09 waited (EPM-DEC-001-0047, What follows, item 6); amended 2026-10-19 on repository visibility |
| Source | Claude Code session, 2026-10-19 |

## Context

Package 1 asked two questions. Question 1: accept PRs #262, #266 and #269, which `app/cursor` merged without the human review the approval agent asked for, or ask for a follow-up. Question 2: change the merge rules so a medium-risk PR waits for the decision owner. Its recommended options were (a), accept all three, and (A), a GitHub ruleset on `main`.

EPM-DEC-001-0042 sorts every measure into eight classes: KPI, operational metric, plan-variance diagnostic, market indicator, decision-support indicator, tracker or report, alert, and not a measure. Claude chose them under the delegation. The decision owner accepted MPC-P09 "after category approval", so P09 waited for this approval.

## Decision

**The decision owner's decisions:**
1. Package 1 is approved: question 1, option (a), and question 2, option (A).
2. The eight measure categories are approved.
3. The repository is public temporarily, for the current goal, so that the ruleset can be enabled, although while it is public anyone can read the internal system, table and report names that EPM-DEC-001-0040 item 3 allows because the repository was private. *2026-10-19, amendment:* a standing rule replaces "for the current goal": public while work needs it, private at the end of each session or goal (see the amendment below).

**What follows (Claude, under EPM-DEC-001-0028):**
1. **The three merges stand.** No file changes. EPM-DEC-001-0036 (#262) and EPM-DEC-001-0038 (#266 and #269) each carry a dated note that the decision owner accepted the merge after the fact.
2. **The ruleset is enabled while the repository is public.** Option (A) is a ruleset that applies to `main`, requires the `checks` status check to pass and one approving review, and lists the repository admin role on its bypass list. GitHub refuses it on this repository. On 2026-10-19, `gh api repos/<owner>/<repo>/rulesets` and `gh api repos/<owner>/<repo>/branches/main/protection` each returned HTTP 403: "Upgrade to GitHub Pro or make this repository public to enable this feature." The package read the repository's state on 2026-10-14, while the repository was still public; it has been private since 2026-10-18, at the decision owner's instruction (`decision-packages/2026-10-14/README.md`). Both ways to enable it were the decision owner's: a paid GitHub plan, or making the repository public again. They chose the second, for the current goal only. Claude made the repository public on 2026-10-19 (`gh repo edit --visibility public`), and the rulesets API then answered. Claude then found that EPM-DEC-001-0040 item 3 relies on the repository being private, made it private again within minutes, and asked; the decision owner chose "Public anyway, for this goal", and Claude made it public again. The ruleset is added once this record merges, so that this record's own pull request does not wait on it. When the goal is reached, Claude makes the repository private again and records it; from then on GitHub no longer enforces the ruleset on the current plan. The package's other caveat still applies once a ruleset exists: whether an approval from `cursor[bot]` counts as the required review is not confirmed. If it does not count, every pull request waits for the decision owner until the rule is adjusted, and the next pull request's log says so.
3. **The approval covers the classes, not each row.** The decision owner approved the eight categories. The rule that assigns them, and each measure's class and candidate flag in `kpi/measure-classification.csv`, stay Claude's under the delegation (EPM-DEC-001-0042), and the decision owner can reverse them.
4. **MPC-P09 is unblocked.** It is applied in its own pull request (EPM-DEC-001-0047, What follows, items 1 and 6).

## Amendment, 2026-10-19: public while work needs it, private at the end of each session or goal

After the session 5 retro, the decision owner set a standing rule on visibility: "if we need to switche to public to get work doen we can. We just need to switch back to private at he end of the session or goal". At the start of the next session they said: "Make the repo public while you work, so the ruleset gates every PR. Make it private again at the end of the session or the goal, and confirm it."

**What follows (Claude, under EPM-DEC-001-0028):**
1. **The rule replaces "for the current goal" in decision 3.** The repository may be public while work needs it, so that GitHub enforces ruleset 25440735 (one approving review and `checks`) on every pull request. It goes back to private at the end of each session or goal.
2. **Each switch is confirmed.** Claude runs `gh repo edit --visibility <public|private> --accept-visibility-change-consequences`, then `gh repo view --json visibility`, and writes both in the session log. A switch is not recorded in this repository each time; the rule covers it.
3. **The exposure is accepted with the rule.** While the repository is public, anyone can read the internal system, table and report names that EPM-DEC-001-0040 item 3 allows because the repository is private. Decision 3 accepted that for one goal; the rule accepts it for each session that needs it.

## Alternatives considered

- **Question 1, option (b): a follow-up change on a named PR.** Not chosen: the decision owner approved the package, whose recommended option is (a).
- **Question 2, options (B) and (C): edit the Cursor automation's instructions, or leave the rules.** Not chosen, for the same reason.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-19-after-run.md`: "I Approve the eight measure categories" and "I approve package 1". Saved in `answers-2026-10-19-visibility.md`: "change to public temporarily for this goal." and "Public anyway, for this goal". Saved in `answers-2026-10-19-completion-order.md`: "if we need to switche to public to get work doen we can. We just need to switch back to private at he end of the session or goal". Saved in `answers-2026-10-19-completion-goal.md`: "Make the repo public while you work, so the ruleset gates every PR. Make it private again at the end of the session or the goal, and confirm it." Items 1 to 4 under "What follows", and items 1 to 3 under the amendment, are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and the decision owner can reverse them.

## Evidence

`business_architecture/domain/decision-packages/2026-10-14/pr-reviews-262-266-269.md`; EPM-DEC-001-0042; EPM-DEC-001-0047.

## Consequences

- While the repository is public and the ruleset is in place, no pull request merges before `checks` passes, and a pull request without an approving review waits for the decision owner.
- The repository returns to private when the current goal is reached. *2026-10-19, later:* done. After PRs #298 to #301 merged, Claude made it private again (`gh repo edit --visibility private`; the API returned `"visibility": "PRIVATE"`). Ruleset 25440735, created after this record merged, required one approving review and `checks` on #300 and #301. On the private repository GitHub again answers HTTP 403 for rulesets, so it is not enforced on the current plan. *2026-10-19, amendment:* the repository may now be public while work needs it, and goes back to private at the end of each session or goal.
- EPM-DEC-001-0042's eight classes are approved; a change to the set needs the decision owner.
- MPC-P09 can be applied.
