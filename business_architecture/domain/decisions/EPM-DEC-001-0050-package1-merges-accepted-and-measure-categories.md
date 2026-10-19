# EPM-DEC-001-0050: PRs #262, #266 and #269 accepted as merged, a ruleset on `main` (blocked), and the eight measure categories approved

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-19; how each is carried out delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Decision package 1 (`decision-packages/2026-10-14/pr-reviews-262-266-269.md`, questions 1 and 2); the eight measure categories of the `kpi` module (EPM-DEC-001-0042), on which MPC-P09 waited (EPM-DEC-001-0047, What follows, item 6) |
| Source | Claude Code session, 2026-10-19 |

## Context

Package 1 asked two questions. Question 1: accept PRs #262, #266 and #269, which `app/cursor` merged without the human review the approval agent asked for, or ask for a follow-up. Question 2: change the merge rules so a medium-risk PR waits for the decision owner. Its recommended options were (a), accept all three, and (A), a GitHub ruleset on `main`.

EPM-DEC-001-0042 sorts every measure into eight classes: KPI, operational metric, plan-variance diagnostic, market indicator, decision-support indicator, tracker or report, alert, and not a measure. Claude chose them under the delegation. The decision owner accepted MPC-P09 "after category approval", so P09 waited for this approval.

## Decision

**The decision owner's decisions:**
1. Package 1 is approved: question 1, option (a), and question 2, option (A).
2. The eight measure categories are approved.

**What follows (Claude, under EPM-DEC-001-0028):**
1. **The three merges stand.** No file changes. EPM-DEC-001-0036 (#262) and EPM-DEC-001-0038 (#266 and #269) each carry a dated note that the decision owner accepted the merge after the fact.
2. **The ruleset is blocked, and waits for the decision owner.** Option (A) is a ruleset that applies to `main`, requires the `checks` status check to pass and one approving review, and lists the repository admin role on its bypass list. GitHub refuses it on this repository. On 2026-10-19, `gh api repos/<owner>/<repo>/rulesets` and `gh api repos/<owner>/<repo>/branches/main/protection` each returned HTTP 403: "Upgrade to GitHub Pro or make this repository public to enable this feature." The package read the repository's state on 2026-10-14, while the repository was still public; it has been private since 2026-10-18, at the decision owner's instruction (`decision-packages/2026-10-14/README.md`). Both ways to enable it are the decision owner's: a paid GitHub plan, or making the repository public again, which reverses their 2026-10-18 instruction. Until they choose, `main` has no ruleset, and merges follow `APPROVAL_POLICY.md` as before. The package's other caveat still applies once a ruleset exists: whether an approval from `cursor[bot]` counts as the required review is not confirmed.
3. **The approval covers the classes, not each row.** The decision owner approved the eight categories. The rule that assigns them, and each measure's class and candidate flag in `kpi/measure-classification.csv`, stay Claude's under the delegation (EPM-DEC-001-0042), and the decision owner can reverse them.
4. **MPC-P09 is unblocked.** It is applied in its own pull request (EPM-DEC-001-0047, What follows, items 1 and 6).

## Alternatives considered

- **Question 1, option (b): a follow-up change on a named PR.** Not chosen: the decision owner approved the package, whose recommended option is (a).
- **Question 2, options (B) and (C): edit the Cursor automation's instructions, or leave the rules.** Not chosen, for the same reason.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-19-after-run.md`: "I Approve the eight measure categories" and "I approve package 1". Items 1 to 4 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and the decision owner can reverse them.

## Evidence

`business_architecture/domain/decision-packages/2026-10-14/pr-reviews-262-266-269.md`; EPM-DEC-001-0042; EPM-DEC-001-0047.

## Consequences

- No ruleset is in place. If the decision owner enables one, no pull request merges before `checks` passes, and a pull request without an approving review waits for them.
- EPM-DEC-001-0042's eight classes are approved; a change to the set needs the decision owner.
- MPC-P09 can be applied.
