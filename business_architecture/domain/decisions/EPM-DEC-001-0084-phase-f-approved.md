# EPM-DEC-001-0084: Phase F is approved: the `ontology` skill is rebuilt as planned, with neutral examples, through pull requests in its own repository

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-22, for the plan, the examples, the shipping route and the delegation; the design choices delegated under this record) |
| Date | 2026-10-22 |
| Questions | Phase F of EPM-DEC-001-0052: rebuilding the `ontology` skill, which starts only on the decision owner's yes; what its examples may use; how it ships; who makes its design choices |
| Source | Claude Code session of 2026-10-22 (Phase E); `answers-2026-10-22-phase-f.md` |

## Context

EPM-DEC-001-0052, item 6, says Phase F rebuilds the `ontology` skill from the playbook and the work done, after phases A to E, and starts only after the decision owner approves the plan. The plan is kept outside this repository, with the session handoffs, as `phase-f-skill-plan.md`. On 2026-10-22 it gained an item 6: proposals from Neo4j's Going Meta series and from the `neo4j-ontology-skill` in `neo4j-contrib/neo4j-skills`, which the decision owner asked Claude to read, with the sources documented beside the plan. The skill lives in the `personal-agent-skills` repository, which is public, while this ontology is proprietary (EPM-DEC-001-0041).

## Decision

**The decision owner's answers:** "Yes, rebuild as planned (Recommended)"; for the examples, "Neutral examples + public MPC facts (Recommended)"; for shipping, "PRs in personal-agent-skills (Recommended)"; and for the design choices, "I agree with 1. But makkes sure you use high quality evdence internal or external to make your decision".

**What follows (Claude):**

1. **The plan stands as written,** items 1 to 6: a short `SKILL.md` that indexes Steps 0 to 12 with their gates, one reference per step group, a governance layer, templates, and the external proposals.
2. **No proprietary content leaves this repository.** The skill's worked examples are invented, or facts from MPC's public SEC filings. They carry no EPM decision, process-map content, customer input, internal name, or the decision owner's name.
3. **The skill ships through pull requests in `personal-agent-skills`,** under that repository's rules and the `way-of-working` loop: its check script, an independent review, its PR reviewer, and a merge on the reviewer's verdict.
4. **Claude makes the design choices and logs each one,** with its evidence, in the pull request that relies on it and in the session's night log. The evidence comes first from this repository's method as practised (the playbook, the worklog, the decision records and the review lessons), then from primary external sources such as W3C specifications and the sources documented with the plan. The decision owner can reverse any choice.

## Alternatives considered

- **Use EPM content as worked examples.** Not chosen: the skill's repository is public, and the decision owner chose neutral examples and public MPC facts.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-phase-f.md`: "Yes, rebuild as planned (Recommended)", "Neutral examples + public MPC facts (Recommended)", "PRs in personal-agent-skills (Recommended)", and "I agree with 1. But makkes sure you use high quality evdence internal or external to make your decision".

## Evidence

- EPM-DEC-001-0041, 0052, 0083.

## Consequences

- Phase F starts. Its pull requests are in `personal-agent-skills`, not here.
- EPM-DEC-001-0052's Phase F item, and the Phase F lines of EPM-DEC-001-0083 and the ontology README's Status section, carry dated notes.
- Later in the same session the decision owner also gave the go-ahead for queue item 9, the open-ontologies trial (block 5 of the answers file). Its result is recorded in its own pull request.
