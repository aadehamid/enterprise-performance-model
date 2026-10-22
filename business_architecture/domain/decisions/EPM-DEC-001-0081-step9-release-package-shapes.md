# EPM-DEC-001-0081: Step 9 is done: every release package conforms to its own shapes

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-22 |
| Questions | Phase E, Step 9: zero unexplained violations for the new modules; whether the shipped packages, not only the source files, meet their shapes |
| Source | Claude Code session of 2026-10-22 (Phase E); `answers-2026-10-22-phase-e.md` |

## Context

The Step 9 gate (EPM-DEC-001-0065) runs every module's shape file over the graph the regression loads, and finds zero violations. Each module's builder runs its shapes when it writes a package. No test ran the packages already written: a package's own `shapes.ttl` over that package, with the released packages it requires. Run on 2026-10-22, all 19 packages under `releases/` conform. The `value-stream` 1.0.0 package fails its own shapes when its required packages are not loaded, so the closure is part of the check.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**

1. **A test of every release package.** `validation/test_release_package_shapes.py` runs each package's `shapes.ttl` over the package and its closure: the packages its manifest requires, and theirs, with the highest version where two paths differ (`release/build_module.py`, `closure()`). The list of packages is pinned by hand, and a package folder on disk that is not in it fails the test, with or without a manifest. `scripts/check.sh` runs it.
2. **Two negative tests.** `value-stream` 1.0.0 without its closure fails on its measure links, and the `lane` 1.0.0 package with one office lane's notation removed fails.
3. **Step 9 is done,** with one exception by design: `provenance/run-shapes.ttl` checks a consumer's runs, which the ontology does not hold (EPM-DEC-001-0016, 0034).

## Alternatives considered

- **Leave the check to each builder.** Not chosen: a builder validates the package it builds now, from the source files. The earlier packages are tested only for being unchanged on disk, not against their shapes.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-phase-e.md`: "Start Phase E now", and "keep going until all the PRs merge". The choices above are Claude's, under the delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

- `business_architecture/ontology/validation/test_release_package_shapes.py`; `release/build_module.py`.
- EPM-DEC-001-0016, 0034, 0065.

## Consequences

- The worklog's Step 9 row is marked done, with the exception above.
- A new release must join the test's package list.
