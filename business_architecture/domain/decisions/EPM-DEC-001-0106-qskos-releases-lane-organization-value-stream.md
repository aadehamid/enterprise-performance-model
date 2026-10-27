# EPM-DEC-001-0106: Lane 1.1.0, organization 2.1.0 and value-stream 1.2.0 carry their deferred qSKOS fixes

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028, amendment of 2026-10-25, evening; Claude approves the queue's minor releases) |
| Date | 2026-10-26 |
| Questions | EPM-DEC-001-0098, item 7: "Core, lane, organization and value-stream carry theirs in their next releases, which no queue item plans yet." Which releases carry lane's, organization's and value-stream's fixes, and what else do they carry? |
| Source | Claude Code session of 2026-10-26 (night run); `answers-2026-10-26-night.md` in the handoff folder (the decision owner approved the night's brief, which names these releases) |

## Context

EPM-DEC-001-0098, item 5, found one code-list scheme with no top concept in each of these three modules: `lane:OfficeLanes`, `orgm:RaciLevel` and `vs:MeasureRelationship`. Each is flat: no member has a parent in its scheme. The `ontology` skill treats such a code list as "a flat scheme of top concepts by design" (`quality.md`, "The qSKOS issues"). Item 7 left these modules' fixes to releases that no queue item planned yet.

The `ontology` skill's SHACL rule 19 (personal-agent-skills #72) says a shape's `sh:message` must not hold a single quote, because n10s 2025.06.1 writes the message into Cypher unescaped and the quote breaks its validator. Its rule asks for the messages of party and lane to be reworded in their next releases.

## Decision

1. **Three minor releases**, issued 2026-10-26 and approved by Claude under the delegation: lane 1.1.0, organization 2.1.0 and value-stream 1.2.0. None removes or renames an IRI or changes a definition, so none is a major.
2. **Top concepts both ways.** Each member of the three schemes states `skos:topConceptOf` its scheme, and the scheme states `skos:hasTopConcept` for it: the 4 office lanes, the 4 RACI levels and the 3 measure relationships, 11 members in all. SKOS defines the two properties as inverses, so the meaning does not change.
3. **Lane's shape message is reworded.** "A process's lane is one of the four office lanes." becomes "The lane of a process is one of the four office lanes." The organization and value-stream shapes hold no message with an apostrophe. Party's messages are reworded in party 1.4.0, which the MPC-P11 work releases under EPM-DEC-001-0104.
4. **Each release requires the current releases.** Lane 1.1.0 requires core 2.3.0 (1.0.0 required 2.2.0), which its build already reads. Organization 2.1.0 requires core 2.3.0 (2.0.0 required 2.1.0). Value-stream 1.2.0 requires core 2.3.0, data-product 1.2.0 and kpi 1.2.0 (1.1.0 required data-product 1.0.0 and kpi 1.1.0). This follows value-stream 1.1.0, which required "the current releases" (EPM-DEC-001-0090). The released packages that pin the older versions stay as released: ref-mpc 1.2.0 still requires organization 2.0.0, and integration 2.3.0 still requires lane 1.0.0, organization 2.0.0 and value-stream 1.1.0. Their next releases can move the pins.
5. **The projection loads the new releases.** `projection/pipeline.py` projects every module at its newest release (EPM-DEC-001-0036, amendment of 2026-10-22), so it now loads these three.

Core's fixes from EPM-DEC-001-0098 (items 2 and 5) are not in this record. They go in core's next release.

## The checker's findings, before and after

`check_taxonomy.py` in the `ontology` skill (personal-agent-skills, as checked out on 2026-10-26) on each package, counted by check:

| Package | Before | After |
|---|---|---|
| lane 1.0.0 to 1.1.0 | `scheme` 1, `parent` 4, `untyped` 7 | `untyped` 7 |
| organization 2.0.0 to 2.1.0 | `scheme` 1, `parent` 4, `untagged` 940 | `untagged` 940 |
| value-stream 1.1.0 to 1.2.0 | `scheme` 1, `parent` 3, `domain-range` 1, `untagged` 13 | `domain-range` 1, `untagged` 13 |

The `scheme` findings that item 5 named are gone, and the `parent` findings go with them, since a top concept needs no parent. No check finds anything new. The findings that stay come from checks that predate personal-agent-skills #53, which EPM-DEC-001-0098 does not cover: `untyped` counts the seven core processes that lane places, typed in core rather than in lane; `untagged` counts literals with no language tag, such as the RACI assignments' source text.

## Alternatives considered

- **Wait for each module's next content change.** Not chosen: item 7 left the fixes waiting on releases no one had planned, and each fix is small and changes no meaning.
- **One major release that also moves integration's and ref-mpc's pins.** Not chosen: moving those pins needs releases of integration and ref-mpc, and a major release is the decision owner's.

## The decision owner's recorded words

The delegation: "Yes, delegate as described (Recommended)" (`answers-2026-10-25-queue-delegation.md`; EPM-DEC-001-0028, amendment of 2026-10-25, evening). The night's brief, which names "qSKOS releases for core, lane, organization, value-stream", was approved with "Approve (Recommended)" on 2026-10-26 (the handoff folder's `answers-2026-10-26-night.md`, answer 5).

## Evidence

- `business_architecture/ontology/releases/lane/1.1.0/`, `organization/2.1.0/`, `value-stream/1.2.0/`, and the packages they replace.
- EPM-DEC-001-0098, items 5 and 7; EPM-DEC-001-0090, item 4.
- The `ontology` skill: `scripts/check_taxonomy.py`; `references/quality.md`, "The qSKOS issues"; SHACL rule 19 (personal-agent-skills #72).
- W3C, *SKOS Simple Knowledge Organization System Reference*, Recommendation, 18 August 2009, https://www.w3.org/TR/skos-reference/: `skos:hasTopConcept` and `skos:topConceptOf` are inverse properties.
- The projection rerun of 2026-10-26: 4,137 nodes and 21,317 relationships from 36,207 triples, no SHACL violation in the graph, an empty round-trip diff (`projection/projection-report.json`).

## Consequences

- EPM-DEC-001-0098, items 5 and 7, carry dated notes.
- Each module's tests pin, by hand, the member count of its scheme and that each member is a top concept both ways. They also check that no IRI of the previous release is gone and that no shape message holds an apostrophe.
- When integration and ref-mpc are next released, they can require these releases.
