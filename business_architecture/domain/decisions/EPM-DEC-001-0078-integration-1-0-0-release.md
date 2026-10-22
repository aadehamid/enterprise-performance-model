# EPM-DEC-001-0078: Release `integration` 1.0.0: placement, authority and consumer; the APQC list stays a reference file

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-22, for the release; the package's contents and the APQC list's place delegated under EPM-DEC-001-0028) |
| Date | 2026-10-22 |
| Questions | The first release of the small Phase E vocabularies, a major that needs the decision owner's approval (module policy, 2026-09-18; release plan, section 2), and whether the APQC element list goes with it |
| Source | Claude Code session of 2026-10-22; `answers-2026-10-22-morning.md` |

## Context

Four small folders came out of the Phase E work on the competency questions: `placement` (EPM-DEC-001-0058), `authority` (0059), `consumer` (0061) and `population` (0062). Each is a few dozen triples that ties the other modules together. Claude's release plan recommended releasing them together as one `integration` 1.0.0 package rather than as four, and left open whether `apqc`, the full APQC PCF 7.2.2 element list (EPM-DEC-001-0060), goes with them or stays a reference file. The same plan, in section 3, folds the eight measure populations into `kpi` 1.1.0. The decision owner approved the plan.

## Decision

**The decision owner's approval:** "release plan approved"

**What follows (Claude, under EPM-DEC-001-0028):**

1. **`integration` 1.0.0, issued 2026-10-22,** built by `release/build_module.py` as the other modules' packages are: Turtle and JSON-LD, the consumer shapes, a DCAT record, a changelog and a manifest with each file's SHA-256. 279 triples.
2. **It holds three vocabularies, each in its own namespace:** `placement/vocabulary.ttl`, `authority/vocabulary.ttl` with `authority/source-tiers.ttl`, and `consumer/vocabulary.ttl`. No IRI changes. The package IRI, `https://w3id.org/lsc/ontology/modules/integration`, names the release only; no term is minted under it.
3. **The population statements ship in `kpi` 1.1.0, not here.** The release plan puts them in both places. Section 3 is the specific one: it folds them into kpi, and EPM-DEC-001-0062, item 5, says the next kpi release can take them. They hang on the kpi module's measure IRIs, so they belong with the measures, and shipping them twice would put the same triples in two packages.
4. **The APQC element list stays a reference file, outside any package.**
   - It is APQC's content, not this ontology's definitions: a tier 5 consistency reference, support only (EPM-DEC-001-0059; AGENTS.md's evidence order).
   - The APQC/IBM licence lets the list be copied and published only if its notice and attribution "travel with all copies" (`business_architecture/reference/README.md`). The file carries the notice as a Turtle comment in its header. A package is a serialised graph, which drops comments, and the graph holds no rights statement, so a package would ship APQC's content without its notice.
   - Consumers need what they already have. `core` carries the 251 elements its processes reference, with the PCF's rights statement. Question 11 needs the full list, and the regression loads the file from the repository.
   - A later release can package it with a rights statement in the graph, if a consumer needs it outside the repository.
5. **Dependencies follow the terms the vocabularies name.** The package requires `core` 2.2.0 and `organization` 2.0.0, `kpi` 1.0.1, and `data-product`, `value-stream`, `system`, `lane` and `market-data` 1.0.0. `placement` annotates their properties, `consumer`'s rules rely on their terms, and `authority` tiers the sources they cite. The consumer shapes conform with those packages loaded. The seventh may-answer rule relies on the population terms, which ship in `kpi` 1.1.0, after this package. A later minor release can require `kpi` 1.1.0.
6. **Tag** `integration-v1.0.0` follows the merge.

## Alternatives considered

- **Four packages, one per folder.** Not chosen: each is a few dozen triples, with one decision record each, and they change together when a module is added. The release plan recommended one package.
- **Put `population` in this package too, as section 2 of the plan lists it.** Not chosen, for item 3's reason.
- **Package the APQC list here.** Not chosen, for item 4's reasons.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`: "release plan approved".

## Evidence

- `business_architecture/ontology/release/build_module.py` and `test_build_module.py`.
- EPM-DEC-001-0058 to 0062; `business_architecture/reference/README.md` (APQC attribution); the playbook's module policy (§2, policy 8).

## Consequences

- `releases/integration/1.0.0/` is written; `scripts/check.sh` fails unless it equals a fresh build.
- The placement, authority, consumer and apqc READMEs and the ontology README say where each folder ships.
