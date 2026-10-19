# EPM-DEC-001-0040: the `kpi` module is seeded from Hamid's planner measure list, with personas as roles

| Field | Value |
|---|---|
| Status | Decided (Hamid, 2026-10-18: the list, personas, internal names, the DSV column, the files out of the repo; the build choices delegated under EPM-DEC-001-0028) |
| Date | 2026-10-18 |
| Questions | Step 7 rulings package, item 1 (`decision-packages/2026-10-14/step7-rulings.md`) |
| Source | Claude Code session, 2026-10-18 |

## Context

EPM-DEC-001-0017 seeds the `kpi` module from "Hamid's Pricing KPI categories and named KPI definitions". The 2026-10-14 package asked Hamid for that list. On 2026-10-18 he sent two files instead: a per-persona list of 55 rows, and a consolidated list of 30 measures with what the personas share, where they differ, open items and linked alerts. Both list measures for a regional refining and supply planning team, grouped by theme (Performance and Capabilities, General Planning, Future Phase) and topic (Refinery Performance, Transportation Utilization, DPO Plans, Market Margin Potential and others). Each row names a measure, its definition and calculation, the persona who uses it, the plan type and horizon, the plan and actuals sources, the history window and the frequency.

## Decision

**Hamid's decisions:**
1. His two files are the KPI answer. The pasted "KPI: B" in his Step 7 reply is not his answer.
2. Personas stay as a notion, without the people's names. The four personas are planning roles: Prompt Planner (prompt month, hourly and daily, the APS schedule), Short-Term Planner (M+1 to M+3, the LP plan handed to the refineries), Distribution Planner (the DPO plan, prompt to M+3: pipelines, marine, inventory) and Mid-Term Planner (the MTP, M+4 to M+36). Any other person named in a cell also becomes a role.
3. Internal system, table and report names may be used. The GitHub repository was switched to private on 2026-10-18 for this reason (`gh repo edit --visibility private`; the API then returned `"visibility": "private"`); only the personas are generalized.
4. The "DSV Data Pull" column is ignored.
5. The two files are not added to the repository. The module holds the definitions built from them.
6. The list mixes true KPIs with operational metrics, and each row is to be classified, using industry practice, external research and MPC's public information.
7. Measures are marked as KPI candidates from industry practice and public information. No target or owner is invented.

**What follows (Claude, under EPM-DEC-001-0028):**
1. This amends EPM-DEC-001-0017, order item 1: the module is seeded from the planner measure list, not from a list of Pricing KPI categories. The Pricing measures already in the repo (R&M margin per barrel, margin capture, the regional 3-2-1 crack spreads) join the module beside the list's rows, each citing MPC's filing.
2. The classification rule, the evidence and the verdict for each row get their own decision record, in the classification pull request that follows this one.
3. The ontology still holds definitions only, never values (EPM-DEC-001-0005). The list's plan and actuals sources, tools and history windows describe how a consuming system computes a measure; they are recorded as attributes of the definition where a competency question needs them, and nowhere else.

## Alternatives considered

- **Wait for a separate list of Pricing KPI categories.** Not chosen: Hamid's reply "I have already provided you the KPI" says the files are the list.
- **Add the files to the repo with names removed.** Not chosen: Hamid said "you should not include the files as source files".
- **Keep the people's names.** Not chosen: Hamid said "I dont wnat you to add names listed".

## Hamid's recorded words

He also wrote that the DSV Data Pull column is to be ignored (same file). Saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/answers-2026-10-18.md`: "Here is the KPI. As far as Personae goes I dont wnat you to add names listed, but still represents the notion of persona", "Some of these are not actually KPI, majority are operational metrics. Please lassify those as such. Use industry best practices and do additional external reserch onthis . Continue to use Marathn as the stand in public compnay... So use any publickly available data from Marathon", "Switch the repo to private so that we can use the name. The only think we should generalize is the persona.", "Use these four (Recommended)", "you should not include the files as source files.sounds.", "For the next one. I have already provided you the KPI. Here is the rest" and "7. Mark candidate based on industry best practices and publickly available information". Items 1 to 3 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and Hamid can reverse them.

## Evidence

The two files (held by Claude outside the repo, in the session handoff folder); `decision-packages/2026-10-14/step7-rulings.md`; EPM-DEC-001-0005, 0008 and 0017; competency questions 13, 14 and 27 to 36.

## Consequences

- EPM-DEC-001-0017's status notes the amendment.
- The Step 7 package's KPI item is answered.
