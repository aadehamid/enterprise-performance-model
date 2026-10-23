# EPM-DEC-001-0089: Release `core` 2.3.0

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-23, for the release; the package's contents delegated under EPM-DEC-001-0028) |
| Date | 2026-10-23 |
| Questions | The first of the six close-out releases (EPM-DEC-001-0088): `core` 2.3.0 with MPC-P10.1 (EPM-DEC-001-0087) |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md` |

## Context

The decision owner accepted MPC-P10.1 (EPM-DEC-001-0087), and the map gained CM 1.3.7.1.7 Coordinate Customer Onboarding in the pull request before this one. Released packages stay fixed, and builds read the process map at a pinned commit (EPM-DEC-001-0047, What follows, item 2). `core` 2.2.0 was built from the map at commit 8259354 (EPM-DEC-001-0076).

## Decision

**The decision owner's approval:** "Approve all six (Recommended)"

**What follows (Claude, under EPM-DEC-001-0028):**

1. **A minor release, 2.3.0, issued 2026-10-23,** built by `release/build_core_2_3.py` from the released 2.2.0 graph and the map at commit c351ef0, the merge that added CM 1.3.7.1.7. It adds one concept and removes no IRI.
2. **The new concept is shaped as 2.2.0's new concepts are:** preferred label, notation, definition (the first sentence of the map's description), scope note (the rest), parent CM 1.3.7.1, scheme, taxonomy level 5 and a provenance note naming the map commit and EPM-DEC-001-0087. It carries no concept kind, domain or planned flows, because the map gives none.
3. **The builder stops on any other map change since 2.2.0,** so nothing else enters the release unreviewed.
4. **The package** holds `core.ttl`, `core.jsonld`, the shapes and canonical-fact mapping of 2.2.0 unchanged, a DCAT record, counts, the changelog and a manifest with each file's SHA-256: 19,819 triples and 707 process concepts. The shapes conform.
5. **Repointing in the same pull request:** the regression, the controlled-value and module-shape checks, the projection and the builds of the apqc, data-product, kpi, lane, system and value-stream modules read 2.3.0. The `party` build stays on 2.1.0 until its 1.1.0 release, which links the onboarding stage to the new process. The released module packages keep the core version they were released against.

## Alternatives considered

- **Fold the concept into the `party` release.** Not chosen: process concepts live in `core`, and every module links to them there.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`: "Approve all six (Recommended)".

## Evidence

- `business_architecture/business_process/downstream_process_map.json` at commits 8259354 and c351ef0.
- EPM-DEC-001-0047, 0076, 0087, 0088.
- `release/build_core_2_3.py` and `test_build_core_2_3.py`.

## Consequences

- `releases/core/2.3.0/` is written, with `CHANGELOG-2.3.0.md`; `scripts/check.sh` fails unless it equals a fresh build. 2.2.0 is unchanged.
- Tag `core-v2.3.0` after the merge.
