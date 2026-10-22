# value-stream: value streams, stages, capabilities and their processes

The `value-stream` module brings the value-stream overlay into the ontology: the Commercial Hydrocarbon Lifecycle (`../../business_process/value_stream_commercial_lifecycle.json`) and Order to Cash (`../../business_process/value_stream_order_to_cash.json`). Each value stream has stages in sequence; each stage has value-stream processes; each value-stream process uses one capability, and may realize process-map processes by IRI (57 of the 58 do), produce or consume data products (20 of the 58 do), and carry cited measure links. The overlay references process nodes and never duplicates them (playbook, Step 7). It holds definitions only (EPM-DEC-001-0005). Its namespace is `https://w3id.org/lsc/ontology/modules/value-stream/`; it depends on `core` 2.2.0 (2.1.0 until 2026-10-22, EPM-DEC-001-0076), the `data-product` module and the `kpi` module. EPM-DEC-001-0054 records the design.

| File | What |
|---|---|
| `vocabulary.ttl` | Classes (value stream, stage, capability, value-stream process, measure link), properties, and the measure-relationship code list (the schema's `informs`, `benchmarks`, `measures-performance`) |
| `shapes.ttl` | SHACL shapes, with a stated cardinality on every property: a stage in one value stream, a value-stream process in one stage with one capability, at most four data products per relation, a measure link naming one kpi measure with its basis and no measure kind |
| `build_value_streams.py`, `value-streams.ttl` | The build: 2 value streams, 12 stages, 21 capabilities, 58 value-stream processes, 72 links to core processes, 9 produces and 37 consumes links, 7 measure links and 4 flows. `--verify` fails unless `value-streams.ttl` equals a fresh build. `scripts/check.sh` runs it |
| `test_value_streams.py` | Tests: the vocabulary, the build is current and its figures match a hand count, every link keeps the source's target and relationship, pinned examples, gap notes create nothing, and SHACL accepts the module and rejects broken items |

The module is not released yet. A release needs the decision owner's approval.

Not carried over, by the schema's rule or EPM-DEC-001-0054: the `gapAnalysis` entries (documentation only), a flow's free-text note, each process's slide letter, and the files' domain as a core business-domain code (kept as written in `vs:sourceDomain`).
