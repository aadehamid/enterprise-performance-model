# EPM-DEC-001-0082: Step 10: one catalog of every release; the Step 10 record brought up to date

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-22 |
| Questions | Phase E, Step 10: a DCAT record for each new release, and how a consumer finds every release in one place |
| Source | Claude Code session of 2026-10-22 (Phase E); `answers-2026-10-22-phase-e.md` |

## Context

Each release package carries its own `catalog.ttl`: one `dcat:Dataset` for that release, its distributions, and its link to the catalog `<https://w3id.org/lsc/ontology/catalog>` (EPM-DEC-001-0029, 0037). All 19 packages under `releases/` share that catalog IRI, but no file lists them together, so a consumer had to open each package to find the releases. The worklog's Step 10 row listed releases up to `party` 1.0.0 and left out `core` 2.2.0, the five Step 7 modules, `integration` 1.0.0, `kpi` 1.1.0 and `ref-mpc` 1.2.0 (EPM-DEC-001-0076 to 0080).

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**

1. **One catalog file.** `releases/catalog.ttl` is the union of the 19 packages' `catalog.ttl` files, plus the catalog's title and description. It says nothing about a release that the release's own record does not. `release/build_catalog.py` builds it from the packages on disk.
2. **Checked in `scripts/check.sh`.** `build_catalog.py --verify` fails unless the written catalog equals a fresh build, so a new release that is not in the catalog fails the check. `release/test_build_catalog.py` checks one dataset per package folder; that every distribution a dataset links to is described, and names a file in its package; and that the catalog adds only its own title and description.
3. **No new package and no release.** The catalog is a file beside the packages, not a module, so it needs no version or approval. The packages are unchanged.
4. **The Step 10 row lists every release.** "Catalog resolves" stays parked: the namespace is not hosted (EPM-DEC-001-0039).

## Alternatives considered

- **Leave the per-package records only.** Not chosen: a consumer would have to know every package to find them.
- **Rewrite each package's `catalog.ttl` to list every release.** Not chosen: that changes released packages, which only a new release may do.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-phase-e.md`: "Start Phase E now". The choices above are Claude's, under the delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

- `business_architecture/ontology/release/build_catalog.py`, `test_build_catalog.py`; `releases/catalog.ttl`.
- EPM-DEC-001-0029, 0037, 0039, 0076 to 0080.

## Consequences

- A new release must be followed by `build_catalog.py --write`; `scripts/check.sh` fails until it is.
