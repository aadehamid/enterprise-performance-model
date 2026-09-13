# Drafting scratch: enterprise ontology namespace design

> **Status: scratch / drafting exercise. Not project material.**
>
> This file is a *what-if* sketch of how one might design a multi-layer
> enterprise namespace registry (TBox + ABox across modeling, catalog, and
> Store layers). It is **not** a registry, it does not declare IRIs, and
> nothing here is part of this project's design.
>
> The real machine ontology SoT for this project is
> `ontology/stage2_enterprise_kpi_ontology.ttl`, which declares exactly two
> prefixes:
>
> ```turtle
> @prefix ekpi: <https://ontology.enterprise.example.com/kpi-store/core#> .
> @prefix data: <https://data.enterprise.example.com/kpi-store/> .
> ```
>
> Anything resembling "the registry" or "exact IRIs" in this file is a
> placeholder shape only. Treat it as a thinking tool, not an artifact.

## Why this scratch exists

The project foundation (see `EPM-FOUND-003` and `EPM-FOUND-004`) draws a
sharp line between *human-readable meaning* (the semantic model), *ontology
design* (this file's neighbourhood, conceptual names), and *machine SoT*
(Turtle in git, exact IRIs). When sketching how a multi-layer enterprise
namespace design might be approached across modeling, catalog, and Store
layers, it is easy to accidentally ship that sketch as if it were the
SoT. This file exists so the sketch has a home and can be reasoned about
without confusing future readers.

## Boundaries the sketch must respect (do not violate in the sketch)

Three locks, all enforced elsewhere in the repo:

1. **Turtle is the machine SoT.** Exact IRIs, classes, and properties only
   live in `ontology/stage2_enterprise_kpi_ontology.ttl`. A sketching
   exercise that invents prefixes like `core:`, `kpi-ont:`, `biz:`, `cdm:`,
   `ldm:`, `pdm:`, `unity:`, `purview:`, or `kpi:` *and treats them as
   live IRIs* is replicating the same miss as PR #14 / #16 and must be
   rejected. Real Turtle terms include `BusinessProcess`, `KPI`, `Metric`,
   `KPIFormula`, `CalculationLogic`, `AggregationType`, `logicExpression`
   — not `LogicalEntity`, `Metric` (as a KPI synonym), or
   `aggregationMethod`.

2. **The KPI Store seat is `dim_kpi_metadata`.** A named KPI is one
   individual, 1:1 with that row. The only legal join is
   **one ontology IRI → one Store row → one Metric View compiled with
   `MEASURE()`**. A sketch that adds a `kpi:` namespace and uses a metric
   *name* as a third identifier next to the ontology IRI and the catalog
   row reopens the Meaning-vs-Compute box (see ADR-HL-021 and the
   "Meaning vs compute" section in `EPM-FOUND-000`).

3. **Process authority is `business_architecture/business_process/` and
   `business_architecture/schema/`.** A sketch that introduces a `biz:`
   slash namespace with process names as local IDs is re-deriving
   process identity in Turtle and must not be merged into anything that
   could be read as project material.

## Sketching exercise (placeholder table only)

The shape below is a placeholder. Every column is a *category to think
about*, not a value to copy. No row here is meant to be a deployed
namespace.

| Concern to think about | Why it exists in a multi-layer enterprise sketch | Where the real authority lives in this project |
|---|---|---|
| TBox vocabulary (classes, properties) | Conceptual names that any modeling layer would reuse | Turtle SoT, prefixes `ekpi:` and `data:` |
| Conceptual / business model names | Names that humans use to talk about entities | Human-readable semantic model (`EPM-FOUND-003`) |
| Logical / physical data model names | Names bound to specific DBMS designs | ER/Studio artifacts, not Turtle |
| Catalog asset identity | Names of tables, schemas, columns in a specific catalog | Unity Catalog, Purview — discover/govern tools |
| KPI Store identity | One row per named KPI; status, approval, formula pointer | `dim_kpi_metadata` SQL seat — not Turtle |
| Process identity | Process and activity IDs | `business_architecture/business_process/` JSON + schema |

## Anti-patterns this scratch is *not* trying to ship

- An invented IRI on a placeholder host presented as the registry.
- A second TBox prefix competing with `ekpi:`.
- A new namespace that re-derives process, catalog, or Store identity.
- A class or property name that does not exist in the Turtle SoT being
  presented as if it did.
- A "Specification" title on a drafting scratch.

## How to use this file

Use it as a checklist when sketching multi-layer namespace designs:

- If your sketch invents a prefix, label it `example:` (or similar) and
  put it in a scratch folder, not `ontology/`.
- If your sketch names a class or property, check it against
  `ontology/stage2_enterprise_kpi_ontology.ttl` first; if it does not
  exist there, mark it *proposed* and route it through the ontology
  design path (`EPM-FOUND-004`) before it can appear in a registry.
- If your sketch touches KPI Store identity, it must end at
  `dim_kpi_metadata`, not at a new namespace.
- If your sketch touches process identity, it must end at
  `business_architecture/business_process/`, not at a new namespace.