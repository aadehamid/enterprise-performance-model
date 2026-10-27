# EPM-DEC-001-0105: MPC-P12 is accepted: the processes that share a name take their parent's subject; released with core's qSKOS fixes as core 2.4.0

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-26, for accepting MPC-P12; the release and how it applies the proposal delegated under EPM-DEC-001-0028) |
| Date | 2026-10-26 |
| Questions | EPM-DEC-001-0098, item 8: should the seven preferred labels shared inside core's process scheme be renamed through a process-map proposal? And which release carries core's deferred qSKOS fixes (EPM-DEC-001-0098, items 2, 5 and 7)? |
| Source | Claude Code session of 2026-10-26 (night); `answers-2026-10-26-night.md`; proposal MPC-P12 (`business_architecture/business_process/proposals/MPC-P12-shared-process-names.md`) |

## Context

EPM-DEC-001-0098 accepted seven preferred labels shared inside core's process scheme "until a process-map proposal settles them" (item 8). The process map gives 25 processes one of those seven names, and core takes its labels from the map, which is the process authority (AGENTS.md). The same record left core's own qSKOS fixes, items 2 and 5, for "their next releases, which no queue item plans yet" (item 7).

On 2026-10-26 Claude put the proposal to the decision owner, with a preview of every rename, and recommended renaming by parent. The decision owner accepted it, and approved the night's brief, which plans core 2.4.0 as a minor release that Claude approves.

## Decision

**The decision owner's decision:** accept MPC-P12, renaming each shared process by its parent, as the preview listed.

**What follows (Claude, under EPM-DEC-001-0028):**

1. **The map takes the 25 names in the proposal's table.** Only the `name` field changes. IDs, parents and descriptions stay. The analysis steps name their parent analysis as the map names it, so "Customer And Marketer Analysis" keeps the map's capital A; "Analyze ... Data" names the subject only, as the preview did.
2. **A minor release, `core` 2.4.0, issued 2026-10-26,** built by `release/build_core_2_4.py` from the released 2.3.0 graph and the map at commit 4906666, the commit that applied MPC-P12. It adds and removes no IRI and moves no concept. Claude approves it under the delegation ("Yes, delegate as described (Recommended)", EPM-DEC-001-0028, amendment of 2026-10-25, evening), as the night's brief planned.
3. **Each renamed concept keeps its old name as `core:priorPreferredLabel`,** with a change note. Core defines that annotation for "generic, ambiguous, overstating or scoped former names", never `skos:altLabel`; an old name as an alternative label would still be shared, and the `ontology` skill keeps "other former names in a history annotation" (`identity-taxonomy.md`, Step 3, rule 8).
4. **Item 2 of EPM-DEC-001-0098 lands here:** the four alternative labels of CM 1.3.2.3.1 to CM 1.3.2.3.4 move to `core:priorPreferredLabel`, with a change note.
5. **Item 5 of EPM-DEC-001-0098 lands here:** every member of core's eleven flat code lists is `skos:topConceptOf` its list, and the list `skos:hasTopConcept` it. That is 51 members.
6. **The builder stops on any other map change since 2.3.0,** except to the `systems` field, which core does not read. MPC-P11 changes that field in its own pull request, so either can merge first.
7. **The shapes and the canonical-fact mapping are 2.3.0's, unchanged.** The package conforms to them: 19,975 triples and 707 process concepts.
8. **Repointing in the same pull request:** the regression, the controlled-value and module-shape checks, the projection and the builds of the apqc, data-product, kpi, lane, system and value-stream modules read 2.4.0. Each of those builds checks only that a process IRI or ID is in core, and none of their outputs changed. The `party` build, whose output names the core version, moves with party's next release. The released module packages keep the core version they were released against.
9. **Competency question Q38 still answers.** Its query `q38c-same-name-processes.rq` listed the names more than one process shares; on 2.4.0 no two processes share a preferred label, so it now lists the names shared as a preferred or a prior preferred label. Each such name still belongs to different IRIs with different parents, which is the answer Q38 asks for.

The `ontology` skill's `check_taxonomy.py` (personal-agent-skills, as of merge `125c9e8`) on 2.3.0 and on 2.4.0:

| Check | 2.3.0 | 2.4.0 |
|---|---|---|
| `collision` | 11 (7 shared preferred labels, 4 alternative labels) | 0 |
| `scheme` | 11 (code lists with no top concept) | 0 |
| `parent` | 51 (the code-list members: each had no parent and was not stated as a top concept) | 0 |
| every other check | 1,192: `untagged` 1,130, `notation` 56, `domain-range` 3, `definition` 3, none of them a finding EPM-DEC-001-0098 disposes of | the same 1,192 |

## Alternatives considered

- **Keep the shared names.** Not chosen by the decision owner. Each process has its own IRI and parent, but a search by label, or a list without the hierarchy, cannot tell them apart.
- **Put the old names in `skos:altLabel`.** Not chosen: each old name would still be shared, and the collision check would fail on it.
- **A separate core release for the qSKOS fixes.** Not chosen: both change only labels and statements, and one minor release carries both.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-26-night.md`: "Rename by parent (Recommended)" (MPC-P12) and "Approve (Recommended)" (the night's brief).

## Evidence

- `business_architecture/business_process/downstream_process_map.json` at commits c351ef0 and 4906666.
- Proposal MPC-P12; EPM-DEC-001-0028, 0089, 0098.
- `release/build_core_2_4.py` and `test_build_core_2_4.py`.
- The `ontology` skill: `check_taxonomy.py`; `references/identity-taxonomy.md`, Step 3, rule 8; `references/quality.md`, "The qSKOS issues".

## Consequences

- `releases/core/2.4.0/` is written, with `CHANGELOG-2.4.0.md`; `scripts/check.sh` fails unless it equals a fresh build. 2.3.0 is unchanged.
- EPM-DEC-001-0098 carries dated notes on items 7 and 8.
- Tag `core-v2.4.0` after the merge.
