# EPM-DEC-001-0054: The value-stream module: the two value streams as an overlay that references processes, with data product and measure links

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Step 7: capabilities and value streams (competency question 10) and what each process produces or consumes (question 7); Phase B of EPM-DEC-001-0052; the `kpi` measure links MPC-P09 added (EPM-DEC-001-0047) |
| Source | Claude Code session, 2026-10-19 |

## Context

Two value streams sit in `business_architecture/business_process/`: the Commercial Hydrocarbon Lifecycle (3 stages, 12 capabilities, 12 value-stream processes) and Order to Cash (9 stages, 9 capabilities, 46 value-stream processes). Their schema (`business_architecture/schema/value_stream.schema.json`) gives the model: Domain, Value Stream, Stage, Capability, Process, with processes that reference process-map nodes through `linkedProcessIds` and carry sparse `produces` and `consumes` links to data products. Every linked process and process group is in `core` 2.1.0. One value-stream process, Review Credit Limit & Risk Code, links to no map node. MPC-P09 added seven cited measure links on two processes (#300). Both files name their domain "Commercial". In `core`, the business-domain code Commercial covers CM 1.1 and CM 1.2, and Order to Cash's processes sit in CM 1.3.7 and CM 1.3.8 (EPM-DEC-001-0038).

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **A new module, `value-stream`.** Like `kpi` and `data-product`, it has its own namespace, vocabulary, shapes, build and tests, and refers to `core` processes by IRI.
2. **The overlay references, never duplicates.** A value-stream process is its own node (`vs:ValueStreamProcess`), with `vs:realizes` to each process-map process it names. A value stream is never a process's parent.
3. **Data product links come from the value streams.** `vs:produces` and `vs:consumes` point to the `data-product` module's data products or lines. A producing value-stream process is the data product's owning process, as the schema says ("this process owns/publishes"). With these links, competency question 10 is answerable, and question 7 answers all but Loss Control's producer, which waits for `core` 2.2.0: 8 of the 48 data products have an owning process and 40 do not. *2026-10-22:* `core` 2.2.0 adds CM 1.1.3.7.13 and the link is emitted: 9 have an owning process and 39 do not (EPM-DEC-001-0076). *2026-10-23:* 10 have an owning process and 39 do not, of 49, since Customer Master's producer CM 1.3.7.1.1 (EPM-DEC-001-0091).
4. **Measure links are qualified, and context only.** Each MPC-P09 link is a `vs:MeasureLink` with the measure, the relationship from the schema's list, and the cited basis. A shape keeps any measure kind off the link: a link is not a KPI designation (EPM-DEC-001-0042).
5. **The source's domain stays as written.** `vs:sourceDomain` keeps "Commercial". It is not mapped to `core`'s business-domain list, because that list's Commercial code does not cover Order to Cash's processes.
6. **Not carried over:** the `gapAnalysis` entries, which the schema calls documentation only; a flow's free-text note, which restates the flow; and each process's slide letter.
7. **Systems and lanes are separate concerns.** The systems a process uses (competency question 6) and its office lane (question 9) are fields of the process map, not of the value streams. They go in their own pull requests.

## Alternatives considered

- **Reuse `core:businessDomain` for the value stream's domain.** Not chosen, for the reason in item 5.
- **Draw producer links from each value-stream process to every process-map node it realizes.** Not chosen: the source names several map nodes per value-stream process and does not say which produces the data.
- **One node for both the value-stream process and the map process.** Not chosen: the playbook says overlays reference process nodes and never duplicate them.

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner asked about these value streams by name: "At waht point I will ging to handle Commercial Lifecyle and Order to cash." (`answers-2026-10-19-completion-order.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/business_process/value_stream_commercial_lifecycle.json`; `business_architecture/business_process/value_stream_order_to_cash.json`; `business_architecture/schema/value_stream.schema.json`; `business_architecture/ontology/ontology-playbook.md`, Step 7; EPM-DEC-001-0038, 0042, 0047, 0053.

## Consequences

- The regression stands at 18 answerable, 7 partial and 19 waiting.
- The module is built and checked by `scripts/check.sh`; it is released only with the decision owner's approval. *2026-10-22:* released as 1.0.0, with the decision owner's approval of the release plan (EPM-DEC-001-0077).
