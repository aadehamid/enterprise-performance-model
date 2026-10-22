# EPM-DEC-001-0079: Release `kpi` 1.1.0: the measure populations join the package, and the measure shape is closed

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-22, for the release; the package's contents and the version class delegated under EPM-DEC-001-0028) |
| Date | 2026-10-22 |
| Questions | Release plan, section 3: fold the eight measure populations (EPM-DEC-001-0062) into the kpi module, and close the measure shape so a value cannot hang off a measure definition |
| Source | Claude Code session of 2026-10-22; `answers-2026-10-22-morning.md` |

## Context

`kpi` 1.0.1 holds 41 measure definitions. What eight MPC-defined measures include and exclude sits in a separate `population` folder, which EPM-DEC-001-0062 kept outside the released kpi tables and left for the next kpi release. The released kpi shapes also leave the measure open: a data-product, series or region carries a closed "definitions, never values" shape (EPM-DEC-001-0005), but a measure does not, so a target or an actual stated on a measure passes. Pi found this on the market-data branch. Claude's release plan proposed `kpi` 1.1.0 for both, and the decision owner approved the plan.

## Decision

**The decision owner's approval:** "release plan approved"

**What follows (Claude, under EPM-DEC-001-0028):**

1. **`kpi` 1.1.0, issued 2026-10-22,** built by `release/build_module.py`: 1,056 triples, requiring `core` 2.2.0. The kpi build reads `core` 2.2.0, and the 41 measures and their 47 process links are unchanged on it.
2. **The populations join the package as their own files.** The package holds `kpi/vocabulary.ttl` and `kpi/measures.ttl`, and `population/vocabulary.ttl` and `population/population.ttl`: eight `pop:includes` and five `pop:excludes` statements on the measure IRIs, each with its evidence row. They keep their `pop:` IRIs. The `integration` 1.0.0 package's seventh may-answer rule (EPM-DEC-001-0078) and the regression's question 28 query name those IRIs, so renaming them into the kpi namespace would break both. They are in this package only: `integration` 1.0.0 leaves them out.
3. **The measure shape is closed.** `shp:NoValuesOnMeasures` lists every property a measure carries: its definition, classification, links, source and population. Any other property fails, so no value, target or actual can be stated on a measure. The three population properties get stated cardinalities, at most one each. Every measure in every module conforms. A repository-wide search found no other property on a measure.
4. **A minor release.** No IRI changes and nothing is removed (`references/versioning.md` in the ontology skill: minor is "new concepts, modules, aliases, references"). The closed shape changes no definition's meaning, so every query and answer stays correct. It encodes EPM-DEC-001-0005, which already ruled out values, and the released content meets it. `core` 2.1.0 added constraint shapes as a minor release in the same way, and no consumer is active (EPM-DEC-001-0001).
5. **The released dependents stay on `kpi` 1.0.1.** `value-stream`, `market-data` and `integration` 1.0.0 were released against it and pin it, and a check reads each released dependency's own dependencies from its manifest (EPM-DEC-001-0077's builder), so their packages and what their checks load are unchanged by this release.
6. **Tag** `kpi-v1.1.0` follows the merge.

## Alternatives considered

- **Move the populations into the kpi namespace and tables.** Not chosen, for item 2's reason.
- **Ship the populations in `integration` 1.0.0, as section 2 of the plan lists them.** Not chosen: section 3 folds them into kpi, and EPM-DEC-001-0062 item 5 says the next kpi release takes them; one package each (EPM-DEC-001-0078, item 3).
- **A major release for the closed shape.** Not chosen, for item 4's reasons.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`: "release plan approved".

## Evidence

- `business_architecture/ontology/release/build_module.py`, `test_build_module.py`; `kpi/shapes.ttl`, `kpi/test_measures.py`.
- EPM-DEC-001-0005, 0042, 0043, 0062, 0076, 0078.

## Consequences

- `releases/kpi/1.1.0/` is written; `releases/kpi/1.0.0/` and `1.0.1/` are untouched. `scripts/check.sh` fails unless 1.1.0 equals a fresh build.
- EPM-DEC-001-0062, the kpi and population READMEs and the ontology README carry dated notes.
