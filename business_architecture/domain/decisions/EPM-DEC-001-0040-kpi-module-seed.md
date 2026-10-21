# EPM-DEC-001-0040: the `kpi` module is seeded from the decision owner's planner measure list, with personas as roles

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-18: the list, personas, internal names, the data-pull column, the files out of the repo; the build choices delegated under EPM-DEC-001-0028) |
| Date | 2026-10-18 |
| Questions | Step 7 rulings package, item 1 (`decision-packages/2026-10-14/step7-rulings.md`) |
| Source | Claude Code session, 2026-10-18 |

## Context

EPM-DEC-001-0017 seeds the `kpi` module from "The decision owner's Pricing KPI categories and named KPI definitions". The 2026-10-14 package asked the decision owner for that list. On 2026-10-18 they sent two files instead: a per-persona list of 55 rows, and a consolidated list of 30 measures with what the personas share, where they differ, open items and linked alerts. Both list measures for a regional refining and supply planning team, grouped by theme (Performance and Capabilities, General Planning, Future Phase) and topic (Refinery Performance, Transportation Utilization, DPO Plans, Market Margin Potential and others). Each row names a measure, its definition and calculation, the persona who uses it, the plan type and horizon, the plan and actuals sources, the history window and the frequency.

## Decision

**The decision owner's decisions:**
1. Their two files are the KPI answer. The pasted "KPI: B" in their Step 7 reply is not their answer.
2. Personas stay as a notion, without the people's names. To Claude's question on persona names they answered "Use these four (Recommended)".
3. Internal system, table and report names may be used. The GitHub repository was switched to private on 2026-10-18 for this reason (`gh repo edit --visibility private`; the API then returned `"visibility": "private"`); only the personas are generalized. *2026-10-19:* the decision owner had it made public temporarily, for the current goal, knowing it exposes these names (EPM-DEC-001-0050). *2026-10-19, later:* the goal was reached (PRs #298 to #301 merged), and the repository is private again (EPM-DEC-001-0050). *2026-10-19, amendment of EPM-DEC-001-0050:* the repository may be public while work needs it, and goes back to private at the end of each session or goal; these names are readable while it is public. *2026-10-21:* for the Customer work the decision owner keeps the repository private ("yes, keep it private", EPM-DEC-001-0067, decision 11; What follows, item 12); those pull requests merge through `merge-on-verdict.sh`, which waits for a MERGE verdict on the head and for `checks`.
4. They wrote to ignore the "DVS data pull"; the column in their files is headed DSV Data Pull, so that column is ignored.
5. The two files are not added to the repository. The module holds the definitions built from them.
6. The list mixes true KPIs with operational metrics, and each row is to be classified, using industry practice, external research and MPC's public information.
7. Measures are marked as KPI candidates from industry practice and public information.

**What follows (Claude, under EPM-DEC-001-0028):**
1. This amends EPM-DEC-001-0017, order item 1: the module is seeded from the planner measure list, not from a list of Pricing KPI categories. The Pricing measures already in the repo (R&M margin per barrel, margin capture, the regional 3-2-1 crack spreads) join the module beside the list's rows, each citing MPC's filing.
2. The classification rule, the evidence and the verdict for each row get their own decision record, in the classification pull request that follows this one.
3. The four personas are Claude's proposal, the option that answer selected: Prompt Planner (prompt month, hourly and daily, the APS schedule), Short-Term Planner (M+1 to M+3, the LP plan handed to the refineries), Distribution Planner (the DPO plan, prompt to M+3: pipelines, marine, inventory) and Mid-Term Planner (the MTP, M+4 to M+36). The names and horizons are Claude's wording.
4. Any other person named in a cell of their files also becomes a role, so no person's name enters the repo.
5. No target or owner is invented to make a measure a KPI; a measure becomes a KPI only by a recorded decision that names them.
6. The ontology still holds definitions only, never values (EPM-DEC-001-0005). The list's plan and actuals sources, tools and history windows describe how a consuming system computes a measure; they are recorded as attributes of the definition where a competency question needs them, and nowhere else.

*2026-10-19:* The decision owner named the list's source: "Value Chain Optimization Decision Support and Visualization (VCO DSV)". The source the planner-list measures and personas cite now carries that title, with "VCO DSV" as its short name; it keeps its IRI (kpi 1.0.1). Their words are in `answers-2026-10-19-vco-dsv.md`.

## Alternatives considered

- **Wait for a separate list of Pricing KPI categories.** Not chosen: The decision owner's reply "I have already provided you the KPI" says the files are the list.
- **Add the files to the repo with names removed.** Not chosen: The decision owner said "you should not include the files as source files".
- **Keep the people's names.** Not chosen: The decision owner said "I dont wnat you to add names listed".

## The decision owner's recorded words

On the source, saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-19-vco-dsv.md`: "By the way do we have a source for the operational metrics/KPI?"

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-18.md`: "Here is the KPI. As far as Personae goes I dont wnat you to add names listed, but still represents the notion of persona", "Some of these are not actually KPI, majority are operational metrics. Please lassify those as such. Use industry best practices and do additional external reserch onthis . Continue to use Marathn as the stand in public compnay... So use any publickly available data from Marathon", "Switch the repo to private so that we can use the name. The only think we should generalize is the persona.", "Use these four (Recommended)", "you should not include the files as source files.sounds.", "For the next one. I have already provided you the KPI. Here is the rest" and "7. Mark candidate based on industry best practices and publickly available information". Items 1 to 6 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and the decision owner can reverse them.

## Evidence

The two files (held by Claude outside the repo, in the session handoff folder); `decision-packages/2026-10-14/step7-rulings.md`; EPM-DEC-001-0005, 0008 and 0017; competency questions 13, 14 and 27 to 36.

## Consequences

- EPM-DEC-001-0017's status notes the amendment.
- The Step 7 package's KPI item is answered.
