# EPM-DEC-001-0047: Hamid's rulings on the MPC process-map proposals, applied to the map

| Field | Value |
|---|---|
| Status | Decided (Hamid, 2026-10-18: the rulings and that they are applied; how each is applied delegated under EPM-DEC-001-0028) |
| Date | 2026-10-18 |
| Questions | MPC-P01, P03 to P09 and P02b (`decision-packages/2026-10-14/step7-rulings.md` §3; `reference/mpc/process-map-suggestions.md`) |
| Source | Claude Code session, 2026-10-18 |

## Context

EPM-DEC-001-0011 moved MPC-P01 and P03 to P09 to Step 7, and EPM-DEC-001-0012 deferred P02's turnaround children (P02b) there too. The 2026-10-14 package asked Hamid to rule on each. AGENTS.md says process-map changes are suggested as proposals and the map is not edited directly, and the package said each accepted proposal would become a proposal file. Before the night run of 2026-10-18, Claude asked whether the accepted proposals should be applied to the map or only recorded. Hamid said to apply them.

## Decision

**Hamid's decisions:**
1. P01, P03, P04, P05 (with changes), P06, P07, P08, P09 and P02b are accepted, with the conditions in his answer.
2. They are applied to `business_architecture/business_process/downstream_process_map.json`, not only recorded. This is Hamid's exception to the AGENTS.md rule for these proposals; it does not change the rule for other changes.
3. Everything done overnight goes in a separate log he reviews in the morning.

**What follows (Claude, under EPM-DEC-001-0028):**
1. **One pull request per proposal that edits the map**, each citing this record. Proposals that need no map edit are recorded here and in `process-map-suggestions.md`.
2. **Released packages stay fixed.** With this record's pull request (commit "fix(release): core 2.0.0 builds from the process map at its pinned commit"), `core` 2.0.0 builds from the map at the commit it was released from, so a map edit does not change a released package. New and changed nodes reach the ontology in a later `core` release, through the usual path: identity (Step 2), definitions (Step 3), then the release build.
3. **IDs follow the map's pattern.** The MPC-P02 proposal set out the pattern, a two-letter prefix for each L1 under Downstream Operations, and the IDs `RF 1`, `RF 1.1` and `RF 1.2`. P02's three IDs are applied with P02b, because P02b's children need their parent's ID. Midstream's ID was left to P01; its application gives it `MS 1` by the same pattern. The minted slugs stay (SLUG_PINS in `build/step2-identity-map.py`).
4. **Nothing is invented to close a gap.** Where a condition Hamid set (P03's physical-execution coverage check; P04's "reuse before new process creation", checked as a fit-gap) finds a real gap, the pull request writes a targeted proposal for Hamid instead of adding a process.
5. **P06 needs no map edit now.** Hamid chose the channel dimension ("P06: A."; the package's option A: a channel dimension built from the customer classification C1 to C8 when the Customer work resumes, EPM-DEC-001-0004). What is Claude's, under the delegation, is only the follow-through: no map edit until the Customer work resumes.
6. **P09 waits for Hamid's category approval.** Hamid accepted it "after category approval". The measure categories are the classes in EPM-DEC-001-0042, which Claude decided under the delegation; that is not Hamid's approval. So P09 is to be prepared, with each measure's relationship to its stage (informs, benchmarks, measures performance), and applied only after Hamid approves the categories.
7. **Process names stay company-neutral.** MPC facts go in descriptions with their source, never in a node name (`process-map-suggestions.md`, "Not suggested").
8. **P01's scope label is Claude's.** Hamid accepted the fuels-logistics scope ("P01: A."). Claude, under the delegation, labels it "Fuels Logistics supporting Refining and Marketing", Claude's wording, built on the proposal's recommendation to model the fuels-logistics part that serves R&M (`process-map-suggestions.md`, MPC-P01).

## Alternatives considered

- **Proposal files only, as the package described.** Not chosen: Hamid said "Apply them."
- **One pull request for all proposals.** Not chosen: one concern per pull request keeps each map change reviewable.

## Hamid's recorded words

The rulings, saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/answers-2026-10-18.md`: "P01: A. P03: A with a physical-execution coverage check. P04: A with reuse before new process creation.", "P05: A with changes. Use a common governance framework, but separate environmental-compliance credit lifecycles from clean-fuel tax-credit lifecycles. Do not apply RIN retirement semantics to 45Z.", "P06: A. P07: A.", "P08: A with seller O2C, buyer P2P, and consolidation responsibilities distinguished. Do not treat disclosed per-barrel expense as a contract tariff.", "P09: A after category approval", and "P02b: A as turnaround coordination. Physical maintenance execution remains outside the current scope unless separately approved." Applying them, saved in `answers-2026-10-18-night.md`: "Apply them. And record everything in a seperate log I can review in the morning. This log should contain all the work you do overnight anyways". Items 1 to 8 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and Hamid can reverse them.

## Evidence

`business_architecture/reference/mpc/process-map-suggestions.md`; `business_architecture/business_process/proposals/MPC-P02-refining-ids.md`; `business_architecture/reference/mpc/mplx-fy2025-10k-fact-sheet.md`; `business_architecture/reference/mpc/mpc-fy2025-10k-fact-sheet.md`; `decision-packages/2026-10-14/step7-rulings.md` §3.

## Consequences

- `process-map-suggestions.md` records each proposal's ruling (P02b in the P02 row), and each map-edit pull request updates its own row when it lands.
- Step 7 order item 4 (EPM-DEC-001-0017) is carried out by these pull requests.
