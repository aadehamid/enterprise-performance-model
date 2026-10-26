# Demos

Two runnable Order-to-Cash **unbilled exposure** packs plus one learner workbook. Same business problem — role-aware unbilled USD — three teaching surfaces. *2026-10-25:* a fourth pack, downstream pricing, stands apart from them; the decision owner plans to bring the demos together later.

| Pack | Path | What it is |
|---|---|---|
| Full Databricks pack | [o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free](o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free/) | Runnable reference: synthetic data, Lakebase/Unity Catalog SQL, Metric View, ontology sidecar. Start at its [README.md](o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free/README.md). Test coverage is specified in the handoff, not shipped as a `tests/` tree. |
| Learner Databricks pack | [o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free-learn](o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free-learn/) | Same shape with blanks — a workbook, not a second complete run. `ontology/o2c-meaning.ttl` is an empty exercise stub (0 triples on purpose). Copy from the full pack if stuck. |
| dbt / DuckDB / MetricFlow pack | [o2c-unbilled-semantic-layer](o2c-unbilled-semantic-layer/) | Local semantic-layer path with real dbt tests. See [VERIFY.txt](o2c-unbilled-semantic-layer/VERIFY.txt) for a recorded successful run (including the dbt-metricflow / dbt-core pin). |
| Downstream pricing pack | [downstream-pricing-databricks-free](downstream-pricing-databricks-free/) | Synthetic pricing data in Databricks Free Edition from real EIA and MPC data where public: Postgres source systems, DuckDB replication, replica, silver star schema, gold, the pricing metric views the ontology binds (EPM-DEC-001-0097) and two Genie agents. Every row labelled real, spot-anchored or synthesized; offline tests run in `scripts/check.sh` (EPM-DEC-001-0102). |

These are homelab reference implementations, not governed EPM artifacts. Parent problem statement: [customer_domain_problem_statement_v0.1.md](../business_architecture/domain/customer_domain_problem_statement_v0.1.md).

Meaning path for both Databricks packs: Turtle sidecar in git; expose through Neo4j when you stand the graph up. Fuseki is optional lab SPARQL only. Band split: [MEANING vs COMPUTE](../architecture/EPM-ARCH-MEANING-vs-COMPUTE.jpg).
