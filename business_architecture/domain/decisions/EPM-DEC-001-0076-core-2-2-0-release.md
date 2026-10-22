# EPM-DEC-001-0076: Release `core` 2.2.0

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-22, for the release; the package's contents delegated under EPM-DEC-001-0028) |
| Date | 2026-10-22 |
| Questions | The `core` release with the process-map changes merged since 2.0.0 (release plan, section 1; EPM-DEC-001-0052, Phase D), with the two checks EPM-DEC-001-0060 and 0063 left for it |
| Source | Claude Code session of 2026-10-22; `answers-2026-10-22-morning.md` |

## Context

Released packages stay fixed, and builds read the process map at a pinned commit (EPM-DEC-001-0047, What follows, item 2). `core` 2.0.0 and 2.1.0 were built from the map at commit b75fd99. Ten merged pull requests changed the map since then (#288 to #296 and #301): the MPC proposals P01, P02b, P03, P04, P05, P07 and P08 (EPM-DEC-001-0047), and the two gaps of EPM-DEC-001-0048 and the widening of EPM-DEC-001-0051. EPM-DEC-001-0060 asked the next `core` release to check the concepts that reference APQC element 19948, and EPM-DEC-001-0063, item 2, asked it to review RF 1.2's Candidate status. Claude's release plan named `core` 2.2.0 as its first release, and the decision owner approved the plan.

## Decision

**The decision owner's approval:** "release plan approved"

**What follows (Claude, under EPM-DEC-001-0028):**

1. **A minor release, 2.2.0, issued 2026-10-22,** built by `release/build_core_2_2.py` from the released 2.1.0 graph and the map at commit 8259354 (the merge of #301, the last change to the map on `main`). It adds concepts and notes and removes no IRI (`references/versioning.md` in the ontology skill). The proposal MPC-P10 is not applied to the map, so nothing of it is here.
2. **23 new concepts:** CM 1.1.3.7.13 and CM 1.2.5.1.5 (EPM-DEC-001-0048), CM 1.2.4.3.8 and its two children (MPC-P05), RF 1.2.1 to RF 1.2.5 (MPC-P02b) and 13 Midstream service concepts, MS 1.1 to MS 1.4.2 (MPC-P01). The four stubs RF 1, RF 1.1, RF 1.2 and MS 1 keep their IRIs under Step 2's slug pins and gain their IDs as `skos:notation`. That makes the 27 map IDs the release plan counted.
3. **New concepts are shaped as 2.1.0's map-sourced concepts:** preferred label, notation, definition, parent, scheme and level. The definition is the first sentence of the map's description, which states the activity and its outcome; the rest of the description is the scope note, so citations and boundaries stay with the concept. A provenance note names the map commit and the record that added it. They carry no conceptKind, domain or planned flows, because the map gives them none, as with the 175 map-sourced concepts in 2.1.0.
4. **Changed descriptions become scope notes on eight concepts.** Approved definitions do not change. Where 2.1.0's definition is the map's earlier description (CM 1.1.7, CM 1.2.5), the note is the text the map added; elsewhere it is the map's new description.
5. **APQC element 19948 (EPM-DEC-001-0060).** Element 19948 is "Analyze internal operations" (APQC 1.1.3.2), a strategy element. Each of the 16 concepts carries it as its top-scoring step 3b candidate (`build/output/step3b-definition-review.csv`, column `apqc_id`), as every concept with an APQC mapping decision carries its candidate. Fourteen are marked "No candidate": confirmed, because the reference names the candidate compared and the decision says it does not match. Two are marked "Review link" and are corrected to "Rejected", each with a change note: CM 1.2.6.3 Supply Operations, whose own note calls the candidate "an unrelated internal-operations match", and the scheme root Downstream Operations, which is not an analysis of internal operations and whose definition review linked no element.
6. **RF 1.2 is no longer a Candidate node (EPM-DEC-001-0063, item 2).** P02b populated it with five steps, and its ownership question is answered for the map's scope. A change note says so; its 2026-09-22 provenance stays as history. RF 1.1's Candidate note is unchanged: no record has reviewed it.
7. **The package** holds `core.ttl`, `core.jsonld`, the shapes and canonical-fact mapping of 2.1.0 unchanged, a DCAT record, counts, the changelog and a manifest with each file's SHA-256: 19,810 triples and 706 process concepts. The shapes conform.
8. **Repointing follows in its own pull request:** the regression, projection, validation and module builds still read 2.1.0 until then, and the data-product module's Loss Control link to CM 1.1.3.7.13 is emitted there.

## Alternatives considered

- **Take each new concept's whole description as its definition,** as 2.1.0 did for the original map descriptions. Not chosen: several descriptions carry boundaries and citations, which belong in a scope note.
- **Drop the 19948 references from the "No candidate" concepts.** Not chosen: every concept with an APQC decision references the candidate it was compared with; dropping 14 would make them the exception.
- **Rebuild the whole Step 2 to Step 3 chain from the current map.** Not chosen: 2.1.0 is released and fixed, and the minor release adds to it.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`: "release plan approved".

## Evidence

- `business_architecture/business_process/downstream_process_map.json` at commits b75fd99 and 8259354.
- EPM-DEC-001-0047, 0048, 0051, 0060, 0063; `build/output/step3b-definition-review.csv`; `apqc/apqc-elements.ttl` (element 19948).
- `release/build_core_2_2.py` and `test_build_core_2_2.py`.

## Consequences

- `releases/core/2.2.0/` is written, with `CHANGELOG-2.2.0.md`; `scripts/check.sh` fails unless it equals a fresh build. 2.1.0 is unchanged.
- EPM-DEC-001-0060 and 0063 carry dated notes.
- Tag `core-v2.2.0` after the merge.
