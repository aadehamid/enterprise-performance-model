# EPM-DEC-001-0094: Release `integration` 1.0.1; the projection's list of release gaps is empty

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-23, for the release; the package's contents delegated under EPM-DEC-001-0028) |
| Date | 2026-10-23 |
| Questions | The sixth and last close-out release (EPM-DEC-001-0088): integration's five projection gaps (EPM-DEC-001-0036) |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md` |

## Context

After value-stream 1.1.0, party 1.1.0 and kpi 1.1.1, five gaps remained in the projection's list, all in integration 1.0.0 (EPM-DEC-001-0036, 0090, 0092, 0093): no range for `plc:placementKind` or `con:reliesOn`, and no shape stating the cardinality of `plc:placementKind`, `auth:rank` or `auth:evidenceTier`. `con:reliesOn` is defined as "the property or class an answer reads"; 24 of its 25 values are properties, and one, on the rule "Name the customer without a role", is the process concept CM 1.3.7.1.1, which is neither.

## Decision

**The decision owner's approval:** "Approve all six (Recommended)", with the counts corrected to five integration fixes: "Approve 8 and 5 (Recommended)".

**What follows (Claude, under EPM-DEC-001-0028):**

1. **A patch release, 1.0.1, issued 2026-10-23.** No IRI changes.
2. **`plc:placementKind` takes `rdfs:range skos:Concept`**, the type of the placement-kind values, and `placement/shapes.ttl` states exactly one kind per placing property.
3. **`con:reliesOn` takes `rdfs:range rdf:Property`,** and its definition says property, not property or class, with a change note. The one value that was not a property, CM 1.3.7.1.1, moves to `rdfs:seeAlso` on its rule, so the rule still points to it. `dcterms:references` was tried first; the consumer shapes read its object as a cited source. This corrects a value that did not fit the property's definition, so it is a patch.
4. **`authority/shapes.ttl` states** exactly one `auth:rank` per tier (an integer from 1) and exactly one `auth:evidenceTier` per source. All 5 tiers and 65 sources already conform.
5. **The package's `shapes.ttl` holds the consumer, placement and authority shapes together.** `release/build_module.py` gains an `own_shapes` count, so a module can package more than one shape file of its own; every other module keeps one.
6. **It requires the current releases:** core 2.3.0, organization 2.0.0, kpi 1.1.1, data-product 1.1.0, value-stream 1.1.0, system 1.0.0, lane 1.0.0, market-data 1.0.0 and party 1.1.0. 1.0.0 stays on disk as released.
7. **The projection** loads integration 1.0.1, and its list of release gaps is empty: the 16 gaps of EPM-DEC-001-0036's amendment of 2026-10-22 are all closed. The rerun gave 34,058 triples, 3,971 nodes and 19,843 relationships, no SHACL violation in the graph over 602 in-graph constraints (the mutant still caught), an empty round-trip diff and equal hashes for the sorted and shuffled loads.

## Alternatives considered

- **`owl:Thing` as `con:reliesOn`'s range.** Not chosen: it is concrete only in name and says nothing about the values.
- **Split `con:reliesOn` into a property link and a concept link.** Not chosen: it adds a property for one value, and the rule's link to the concept is context, which `rdfs:seeAlso` states.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`: "Approve all six (Recommended)" and "Approve 8 and 5 (Recommended)".

## Evidence

- `placement/vocabulary.ttl`, `consumer/vocabulary.ttl`, `authority/vocabulary.ttl`, `authority/source-tiers.ttl`; `consumer/shapes.ttl`.
- EPM-DEC-001-0036, 0058, 0059, 0061, 0078, 0088, 0090, 0092, 0093.

## Consequences

- `releases/integration/1.0.1/` is written; `scripts/check.sh` fails unless it equals a fresh build.
- `projection/pipeline.py`'s `RELEASE_EXCEPTIONS` is empty; a new gap fails the build until a release closes it or it is listed with its fix.
- Tag `integration-v1.0.1` after the merge.
