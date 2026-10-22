# EPM-DEC-001-0077: Release the Step 7 modules data-product, value-stream, system, lane and market-data as 1.0.0

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-22, for the releases; the packages' contents delegated under EPM-DEC-001-0028) |
| Date | 2026-10-22 |
| Questions | The first releases of five Step 7 modules, each a major that needs the decision owner's approval (module policy, 2026-09-18; release plan, section 2) |
| Source | Claude Code session of 2026-10-22; `answers-2026-10-22-morning.md` |

## Context

The `data-product` (EPM-DEC-001-0053), `value-stream` (0054), `system` (0055), `lane` (0056) and `market-data` (0057, 0066) modules were built and merged during the Step 7 work, each unreleased. A module's first release is a major, and a major needs the decision owner's approval. Claude's release plan listed all five as 1.0.0 releases, after `core` 2.2.0, and the decision owner approved the plan. `core` 2.2.0 (EPM-DEC-001-0076) holds every process these modules link, including CM 1.1.3.7.13, Loss Control's producer, and the modules' builds now read it.

## Decision

**The decision owner's approval:** "release plan approved"

**What follows (Claude, under EPM-DEC-001-0028):**

1. **Five releases, each 1.0.0, issued 2026-10-22,** built by `release/build_module.py` as the other modules' packages are: the module's Turtle and JSON-LD, its shapes, a DCAT record, its changelog and a manifest with each file's SHA-256.
2. **Each package holds its module's vocabulary and instance file, nothing else:** `data-product` 718 triples, `value-stream` 992, `system` 589, `lane` 59 and `market-data` 668.
3. **Dependencies follow the IRIs each module uses.** `data-product`, `system` and `lane` require `core` 2.2.0. `value-stream` requires `core` 2.2.0, `data-product` 1.0.0 and `kpi` 1.0.1, because its processes produce and consume data products and carry measure links. `market-data` requires `kpi` 1.0.1, whose crack-spreads measure its series belong to; it names no process. Each package's shapes conform with the released packages it depends on loaded. Where two paths reach different releases of one module (value-stream reaches `core` 2.2.0 directly and 2.1.0 through `kpi` 1.0.1), the check loads only the highest.
4. **The 33 parked data products are in the `data-product` package** as parked items: each is a defined node with its place in the portfolio, its status and a note that its definition waits for its data owners (EPM-DEC-001-0053, item 3). They have no definition, and the release adds none. A later minor release defines them when the portfolio describes them.
5. **Tags** `data-product-v1.0.0`, `value-stream-v1.0.0`, `system-v1.0.0`, `lane-v1.0.0` and `market-data-v1.0.0` follow the merge.

## Alternatives considered

- **One package for the five modules.** Not chosen: each module has its own namespace, decision record and owners, and versions independently (the playbook's module policy).
- **Wait for `kpi` 1.1.0 before releasing value-stream and market-data.** Not chosen: they use only measure IRIs that `kpi` 1.0.1 already releases; a later minor release can move them to 1.1.0.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`: "release plan approved".

## Evidence

- `business_architecture/ontology/release/build_module.py` and `test_build_module.py`.
- EPM-DEC-001-0053 to 0057, 0066, 0076; EPM-DEC-001-0037 (module packages).

## Consequences

- `releases/<module>/1.0.0/` is written for each; `scripts/check.sh` fails unless each equals a fresh build.
- The module READMEs, the ontology README and records 0053 to 0057 and 0066 carry dated notes.
