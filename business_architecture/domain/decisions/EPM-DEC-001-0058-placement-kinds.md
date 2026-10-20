# EPM-DEC-001-0058: Placement kinds: only the producing process certifies; every other placement is context

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Competency questions 37 (what a concept or Named KPI sits on), 38 (whether a placement is certification or context) and 39 (what breaks if a meaning changes); Phase E of EPM-DEC-001-0052 |
| Source | Claude Code session, 2026-10-19 |

## Context

Since the Step 7 overlays, measures, data products, systems and lanes are placed on processes by twelve properties across six modules. Each property's own definition already says what it claims: `kpi:informsProcess` is "context for where the measure is used, not a certification" (EPM-DEC-001-0043); a value-stream process that produces a data product "owns/publishes" it (the value-stream schema; EPM-DEC-001-0054). The graph did not say so in a form a query can read.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **A placement-kind annotation.** A small `placement` vocabulary defines `plc:placementKind` with two kinds, certification and context, and annotates each placing property with one.
2. **Only producing certifies.** `vs:produces` and `dp:producedBy` are certification, because the schema makes the producing process the data product's owning process. The other ten properties are context, because their definitions say so: measure links, consuming, realizing, using a capability, segment anchors, systems, lanes and regions.
3. **Question 38 is answerable.** No measure is placed by a certification link; the query that would list one returns none. Its second part, whether two processes with one name mean the same thing, is the same-word test of question 15: they are different IRIs with their own definitions.
4. **Questions 37 and 39 are answerable.** With the value streams and market series, a data product or benchmark series sits on the value-stream processes and capabilities that produce, consume or measure it (37). A change of a measure's meaning reaches its series, the value-stream processes that link it and the processes it informs; a data product's reaches its consumers (39).

## Alternatives considered

- **Leave the kind in each property's prose definition.** Not chosen: a query cannot read it.
- **Treat a measure's process links as certification.** Not chosen: EPM-DEC-001-0043 made them context, and a KPI needs a recorded owner (EPM-DEC-001-0042).

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/schema/value_stream.schema.json` (`produces`: "this process owns/publishes"); the vocabularies of the kpi, value-stream, data-product, system, lane and market-data modules; EPM-DEC-001-0042, 0043, 0053 to 0057.

## Consequences

- The regression stands at 26 answerable, 5 partial and 13 waiting.
