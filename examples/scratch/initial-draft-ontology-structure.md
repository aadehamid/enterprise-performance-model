# Drafting scratch: enterprise ontology namespace design

> **Status: working draft. Reconciliation with the foundation files is an open future step.**
>
> This file represents an earlier, less-detailed view of how one might
> design a multi-layer enterprise namespace registry (TBox + ABox across
> modeling, catalog, and Store layers). It is being kept here as a
> working draft so its claims can be reviewed against the foundation
> files and the current Turtle SoT (`ontology/stage2_enterprise_kpi_ontology.ttl`)
> before either becomes authoritative.
>
> Treat this file as the source of truth only after reconciliation.
> Until that happens, neither this file nor the foundation files override
> each other; conflicts are open items, not resolved positions.
> Tracked as Open Issue I-11 in `EPM-FOUND-000` and GitHub issue #18.

## Why this scratch exists

The project foundation (see `EPM-FOUND-003` and `EPM-FOUND-004`) draws a
sharp line between *human-readable meaning* (the semantic model), *ontology
design* (this file's neighbourhood, conceptual names), and *machine SoT*
(Turtle in git, exact IRIs). When sketching how a multi-layer enterprise
namespace design might be approached across modeling, catalog, and Store
layers, it is easy to ship a sketch that quietly competes with the
foundation. This file exists so the sketch has a home and can be
reasoned about openly, with reconciliation as the next step rather than
either side being declared authoritative by default.

## Boundaries the sketch must respect during reconciliation

Three locks, all currently enforced elsewhere in the repo. They are
listed here so the reconciliation between this file and the foundation
can be done against a fixed reference set, not as a verdict that the
sketch has already lost.

1. **Turtle is the machine SoT.** Exact IRIs, classes, and properties only
   live in `ontology/stage2_enterprise_kpi_ontology.ttl`. The Turtle
   prefixes currently declared are `ekpi:` and `data:`. Real Turtle
   terms include `BusinessProcess`, `KPI`, `Metric`, `KPIFormula`,
   `CalculationLogic`, `AggregationType`, `logicExpression`. If a future
   reconciliation promotes a class or property from this sketch into the
   foundation, it must first be added to the Turtle SoT through the
   `EPM-FOUND-004` ontology design path.

2. **The KPI Store seat is `dim_kpi_metadata`.** A named KPI is one
   individual, 1:1 with that row. The only legal join is
   **one ontology IRI → one Store row → one Metric View compiled with
   `MEASURE()`**. Any reconciliation that promotes a sketch-level
   `kpi:` namespace into a registry must end at `dim_kpi_metadata`, not
   at a new namespace (see ADR-HL-021 and the "Meaning vs compute"
   section in `EPM-FOUND-000`).

3. **Process authority is `business_architecture/business_process/` and
   `business_architecture/schema/`.** Any reconciliation that promotes a
   sketch-level `biz:` slash namespace into a registry must end at
   those folders, not at a new namespace.

## Sketching exercise (placeholder table only)

The shape below is a placeholder. Every column is a *category to think
about*, not a value to copy. No row here is meant to be a deployed
namespace. During reconciliation, each row will be checked against the
"Where the real authority lives in this project" column on the right.

| Concern to think about | Why it exists in a multi-layer enterprise sketch | Where the real authority lives in this project |
|---|---|---|
| TBox vocabulary (classes, properties) | Conceptual names that any modeling layer would reuse | Turtle SoT, prefixes `ekpi:` and `data:` |
| Conceptual / business model names | Names that humans use to talk about entities | Human-readable semantic model (`EPM-FOUND-003`) |
| Logical / physical data model names | Names bound to specific DBMS designs | ER/Studio artifacts, not Turtle |
| Catalog asset identity | Names of tables, schemas, columns in a specific catalog | Unity Catalog, Purview — discover/govern tools |
| KPI Store identity | One row per named KPI; status, approval, formula pointer | `dim_kpi_metadata` SQL seat — not Turtle |
| Process identity | Process and activity IDs | `business_architecture/business_process/` JSON + schema |

## Things this scratch is asking the reconciliation to think through

These are not verdicts against the sketch. They are items the
reconciliation between this file, the master use case
(`examples/scratch/master-use-case-kpi-store-semantic-governance.md`),
and the foundation files should resolve:

- Whether any sketch-level prefix here should become a real namespace,
  and if so under which authority.
- Whether any class or property named in this sketch should be added to
  the Turtle SoT, and through which ontology design path.
- Whether any sketch-level claim about KPI Store identity should be
  promoted to the foundation, or whether the foundation's
  `dim_kpi_metadata` seat is sufficient.
- Whether any sketch-level claim about process identity should be
  promoted, or whether `business_architecture/business_process/` is
  sufficient.

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
- If a sketch grows beyond the reconciliation scope, raise an Open
  Issue in `EPM-FOUND-000` rather than letting it settle into a default.