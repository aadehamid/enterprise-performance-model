# Demos

Three runnable Order-to-Cash **unbilled exposure** packs. Same business problem — role-aware unbilled USD — three teaching surfaces.

| Pack | Path | What it is |
|---|---|---|
| Full Databricks pack | [o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free](o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free/) | Complete reference: synthetic data, Lakebase/Unity Catalog SQL, Metric View, ontology sidecar, tests. Start at its [README.md](o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free/README.md). |
| Learner Databricks pack | [o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free-learn](o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free-learn/) | Same shape with blanks. `ontology/o2c-meaning.ttl` is an empty exercise stub (0 triples on purpose). Copy from the full pack if stuck. |
| dbt / DuckDB / MetricFlow pack | [o2c-unbilled-semantic-layer](o2c-unbilled-semantic-layer/) | Local semantic-layer path. See [VERIFY.txt](o2c-unbilled-semantic-layer/VERIFY.txt) for a recorded successful run (including the dbt-metricflow / dbt-core pin). |

These are homelab reference implementations, not governed EPM artifacts. Parent problem statement: [customer_domain_problem_statement_v0.1.md](../business_architecture/domain/customer_domain_problem_statement_v0.1.md).
