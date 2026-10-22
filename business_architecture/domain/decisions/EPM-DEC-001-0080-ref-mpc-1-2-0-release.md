# EPM-DEC-001-0080: Release `ref-mpc` 1.2.0: MPC and MPLX as parties join the reference module

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-22, for the release; the package's contents delegated under EPM-DEC-001-0028) |
| Date | 2026-10-22 |
| Questions | The `ref-mpc` release that carries the reference parties moved by EPM-DEC-001-0075, which the approved release plan does not list |
| Source | Claude Code session of 2026-10-22; `answers-2026-10-22-ref-mpc-release.md` |

## Context

EPM-DEC-001-0075 moved MPC and MPLX, described as parties in the `party` module's terms, from `party/` into `ref-mpc/reference-parties.ttl`, on the decision owner's word that they "should split into their own refrence module". It said the move ships in `ref-mpc` 1.2.0, and that the release needs the decision owner's own approval, because the release plan approved that morning does not list it. Claude asked for that approval, saying it is a minor release that adds the two parties' roles and their services agreement, changes no released IRI and requires `party` 1.0.0.

## Decision

**The decision owner's approval:** "Approve ref-mpc 1.2.0 (Recommended)"

**What follows (Claude, under EPM-DEC-001-0028):**

1. **`ref-mpc` 1.2.0, issued 2026-10-22,** built by `release/build_module.py`: 180 triples, `ref-mpc.ttl` and `reference-parties.ttl`. The 1.1.0 package is unchanged.
2. **It requires `organization` 2.0.0, as 1.1.0 did, and `party` 1.0.0,** whose terms the parties use. The package's check loads both releases and validates the parties against the party module's shapes and code lists, and the companies against the ref-mpc and organization shapes.
3. **A minor release:** it adds instances and changes no released IRI (`references/versioning.md` in the ontology skill). The roles' and agreement's IRIs were never released (EPM-DEC-001-0075, item 2).
4. **MPLX's 10-K source node meets core's source shape,** as MPC's does; `test_ref_mpc.py` checks both files.
5. **Tag** `ref-mpc-v1.2.0` follows the merge.

## Alternatives considered

- **Keep the parties outside every package until a later release.** Not chosen: the decision owner approved this release.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-ref-mpc-release.md`: "Approve ref-mpc 1.2.0 (Recommended)".

## Evidence

- `business_architecture/ontology/release/build_module.py`, `test_build_module.py`; `ref-mpc/test_ref_mpc.py`.
- EPM-DEC-001-0033, 0071, 0074, 0075.

## Consequences

- `releases/ref-mpc/1.2.0/` is written; `scripts/check.sh` fails unless it equals a fresh build.
- EPM-DEC-001-0075's pending statements, the ref-mpc README and the ontology README carry dated notes.
