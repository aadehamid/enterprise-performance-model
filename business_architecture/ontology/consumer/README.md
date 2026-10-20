# consumer: rules for those who read the graph

How a catalog row binds a Named KPI (competency question 35), and what a graph or meaning agent may answer from the graph and must refuse (questions 41 and 42). EPM-DEC-001-0061 records the rules.

| File | What |
|---|---|
| `vocabulary.ttl` | `con:publishesMeasure`, the catalog binding from a defined data product to a defined measure; the `con:Rule` class and its kinds; six may-answer rules and five must-refuse rules, each naming the graph terms it relies on |
| `shapes.ttl` | A binding needs both ends defined; each rule has a name, a definition, a kind, the terms it relies on and its source |
| `test_consumer_rules.py` | Tests: the rule counts, every term a rule relies on exists in the graph, the rules conform, and the binding accepts defined ends and rejects undefined ones |

No catalog row binds a measure yet: no source says which data product publishes which measure. The binding is the pattern a catalog uses when it does.
