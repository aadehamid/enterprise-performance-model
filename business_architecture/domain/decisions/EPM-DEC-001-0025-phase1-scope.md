# EPM-DEC-001-0025: Phase 1 covers the source-correction backlog; other held rows wait

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-06 |
| Questions | Follow-up to Q12 (EPM-DEC-001-0013) |
| Source | Claude Code session, 2026-10-06 |

## Context

EPM-DEC-001-0013 releases `core` 1.0.0 after Phase 1, so that held rows get fresh verdicts before the `intake:` layer is retired. The playbook's release gate then said every held row needs a fresh verdict after source correction. Running `mapping_v2.py` on `main` (commit `1179405`) shows that the pipeline holds 686 mentions. 277 of them are in `step4/source-workbook-backlog.md` and are worked through the eight Phase 1 issues (#201 to #206, #209, #210; parent #207). 409 are held but appear nowhere in the backlog:

| Held mentions not in the backlog | Count |
|---|---|
| Context-pass holds (label-only target the context check could not confirm) | 166 |
| `uses-input` pass holds (no citation, or boundary wording only) | 113 |
| `informed-by` pass holds | 80 |
| `enables` mentions held with their removed `uses-input` supporter (G1a) | 40 |
| `governed-by` pass holds | 9 |
| Property-rule hold | 1 |

Read literally, the gate would block the release until all 686 were corrected, while the handover plan defined Phase 1 as the backlog sections.

## Decision

Option (a). Phase 1 is the source-correction backlog: the rows worked through the eight Phase 1 issues. The `core` 1.0.0 release requires a fresh verdict, after source correction, for every row on that backlog. The 409 held mentions outside it stay held with their recorded reasons, emit no fact, and move to a backlog for a later release. Their evidence stays in the Step 4 CSVs (playbook evidence rule 9). This amends EPM-DEC-001-0013. The release gate in the playbook (Step 4 and Appendix B) now says "every row on the source-correction backlog". The ontology skill in personal-agent-skills gets the same change through its own pull request (personal-agent-skills #5).

## Alternatives considered

(b) Phase 1 covers all 686 held mentions, with new issues for the 166 context-pass holds (target clarification, like #201) and the 233 `uses-input`, `informed-by` and dependent holds (citations, like #205). Roughly 2.5 times the Phase 1 work before the first release.

## Hamid's recorded words

Asked to choose between (a) and (b), with (a) recommended, Hamid replied on 2026-10-06: "i agree with your recommendation"

## Evidence

`business_architecture/ontology/step4/mapping_v2.py` (run on commit `1179405`: 686 held mentions, 617 emitting, 457 facts); `business_architecture/ontology/step4/source-workbook-backlog.md`; `ledger-v2.md` ("uses-input pass applied" and "Informed-by pass" records).
