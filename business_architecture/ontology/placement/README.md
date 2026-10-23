# placement: what a placement claims

Competency question 38 asks whether a measure's or concept's placement on a process certifies the process or is only context. This vocabulary answers it by marking each placing property of the other modules with its kind: `certification` (the link names a data product's owning process) or `context` (the link says only where one thing is used or placed with another). Only producing a data product certifies (`vs:produces`, `dp:producedBy`, the owning process). Every other placement, including every measure's, is context. EPM-DEC-001-0058 records the choice.

| File | What |
|---|---|
| `vocabulary.ttl` | The `placementKind` annotation, the two kinds, and the annotations on twelve properties of the kpi, value-stream, data-product, system, lane and market-data modules |
| `test_placement.py` | Tests: the kinds are the decided ones, one per property, every annotated property exists in its module, and q38a sees a measure certified as an object |

Released in `integration` 1.0.0 on 2026-10-22, with `authority` and `consumer` (EPM-DEC-001-0078): the package in `../releases/integration/1.0.0/`. *2026-10-23:* `integration` 2.0.0 (`../releases/integration/2.0.0/`): `plc:placementKind` takes `rdfs:range skos:Concept`, and `placement/shapes.ttl` states one kind per placing property (EPM-DEC-001-0094).
