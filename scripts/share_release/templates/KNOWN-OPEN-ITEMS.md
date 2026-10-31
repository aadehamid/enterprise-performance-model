# Known open items

What is open on the ontology and the demo, and what this release did not run.

- **The ontology's open items** are listed in `business_architecture/ontology/OPEN-ITEMS.md`: the points only the business can settle (who owns each module's meaning, the Market Data mandate, the PIDX codes, three role definitions, the measures' scope in business words, the internal systems' descriptions), the gaps the process map still records, and the work that needs no one from the business.
- **The pricing demo's acceptance tests** stopped at 2 of 21 use cases on the last recorded run, as the demo's README reports; the recorded runs and their re-judged verdicts ship in `demos/downstream-pricing-databricks-free/data/acceptance/`. The live run was not run on this release: it needs a Databricks workspace and its model endpoints, and it was the one heavy use of the workspace's daily limit.
- **Store sync is manual.** `business_architecture/ontology/projection/sync_stores.py check` says which store is behind the newest release, and `sync` reloads it; nothing runs it on a schedule here. The guide's "The in-sync strategy" lists what can drift and what catches it.
- **The technical graph** is kept in Neo4j and copied to Databricks by hand after each demo run; a vocabulary module for it, lineage read from Databricks, and the scheduled sync are the next work on the original build.
