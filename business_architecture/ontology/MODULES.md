# The ontology's modules and how they connect

This guide explains what each module of the ontology holds and how the modules link to one another, with one real example for each link. Every example is quoted from the newest release of its module, and `scripts/test_modules_guide.py` fails when a quoted triple is no longer there.

The guide gives no version numbers or counts, because they change with each release. For those, run these from the repository root:

- `uv run --with rdflib python scripts/epm_facts.py modules` lists each module's newest and earlier releases, the versions it requires and its triple count. It names what a release was built from where the release's manifest records it, and otherwise the source folders the builder packages today, labelled as the builder's.
- `uv run --with rdflib python scripts/epm_facts.py coverage` counts how many processes have a RACI assignment, a system, a KPI, a lane, a value-stream step and a data product, and lists the ones with none. `--processes lifecycle`, `--processes stage:<name>` or `--processes module:<name>` narrows it to other sets of processes.

The diagram "EPM ontology: modules and how they connect" draws the same picture, with an arrow from each module to each module it requires: https://app.eraser.io/workspace/GogQQcK6yNMwogKucbtj.

## The whole picture

`core` is the process map. Most other modules add one kind of thing and link it to core's processes, mostly by using core's process IRIs (`https://w3id.org/lsc/ontology/process/CM-…`) directly. Four do not: `market-data` links to `kpi`'s measures, `ref-mpc` holds company facts in the terms of `organization` and `party`, `integration` holds rules about the other modules' links, and `technical-graph` links what is built on a data platform to `data-product`, `kpi` and `system`. A module names the versions of the modules it was released against. When modules are loaded together, the newest release of each one is loaded.

Some source folders are not packages of their own. `placement/`, `authority/` and `consumer/` ship together as `integration`. `population/` ships in `kpi`. `apqc/` is a reference list that ships in no package. *2026-11-02:* `technical-graph/` ships as the `technical-graph` package since its `1.0.0`, which the decision owner approved (EPM-DEC-001-0112); its `example/` graph is test data and ships in no package. *2026-11-02:* `logical-model/` holds the machinery of the logical-model module and a made-up example model; it ships in no package in `main`. Its first model, the customer logical model, is kept out of `main` and joins the release as `logical-model 1.0.0`, which the decision owner approves (EPM-DEC-001-0113).

## Three kinds of content

The ontology holds three kinds of content, and keeps each in a fixed place:

| Kind | Where it lives | Example |
|---|---|---|
| Definitions: classes, properties, role types | `organization`, `party` and the other modules | the control relationship; the Payer role |
| Company-neutral instances | `organization`, `party`, `lane` and the other modules | the role register, RACI assignments, the customer lifecycle stages |
| Company-specific instances | `ref-mpc` only | MPC, MPLX, MPC's control of MPLX, and MPC's brands (since 2026-10-27; EPM-DEC-001-0108) |

Operational records stay in the business systems and never enter the ontology: actual customers, invoices and KPI values. The playbook's policy 2 calls this "define, don't record".

## The three files of each package, and what each is built from

Every module package holds three graphs in Turtle:

- **`<module>.ttl`, the content:** the module's terms, individuals and links.
- **`shapes.ttl`, the rules:** the SHACL shapes the content must meet.
- **`catalog.ttl`, the release record:** the DCAT dataset for this release, with its version, issue date and distributions.

`scripts/test_modules_guide.py` checks the table below against the module builder. Paths are under `business_architecture/ontology/`.

| Module | Its purpose | `<module>.ttl` is built from | `shapes.ttl` is built from |
|---|---|---|---|
| `core` | The process map | `business_architecture/business_process/downstream_process_map.json` at a pinned commit and core's previous release, through `release/build_core*.py` | `release/shapes.ttl`, and the canonical-fact and controlled-value shapes the later core builders add |
| `organization` | Who does what | `organization/vocabulary.ttl`, `organization/roles.ttl`, `organization/assignments.ttl` | `organization/shapes.ttl` |
| `ref-mpc` | The company facts | `ref-mpc/ref-mpc.ttl`, `ref-mpc/reference-parties.ttl`, `ref-mpc/reference-brands.ttl` | `ref-mpc/shapes.ttl` and the shapes of the `organization` and `party` releases it pins |
| `party` | The customer domain | `party/vocabulary.ttl`, `party/code-lists.ttl`, `party/systems.ttl`, `party/lifecycle.ttl` | `party/shapes.ttl` |
| `kpi` | What each measure means | `kpi/vocabulary.ttl`, `kpi/measures.ttl`, `population/vocabulary.ttl`, `population/population.ttl` | `kpi/shapes.ttl` |
| `market-data` | The crack-spread recipes | `market-data/vocabulary.ttl`, `market-data/market-data.ttl` | `market-data/shapes.ttl` |
| `data-product` | The portfolio | `data-product/vocabulary.ttl`, `data-product/data-products.ttl`, `data-product/pricing.ttl` | `data-product/shapes.ttl` |
| `value-stream` | How value flows | `value-stream/vocabulary.ttl`, `value-stream/value-streams.ttl` | `value-stream/shapes.ttl` |
| `system` | What each process uses | `system/vocabulary.ttl`, `system/systems.ttl` | `system/shapes.ttl` |
| `lane` | Where a trading process sits | `lane/vocabulary.ttl`, `lane/lanes.ttl` | `lane/shapes.ttl` |
| `integration` | Rules that apply across modules | `placement/vocabulary.ttl`, `authority/vocabulary.ttl`, `authority/source-tiers.ttl`, `consumer/vocabulary.ttl` | `consumer/shapes.ttl`, `placement/shapes.ttl`, `authority/shapes.ttl` |
| `technical-graph` | What was built on the data platform | `technical-graph/vocabulary.ttl` | `technical-graph/shapes.ttl` |

The module builder writes each `catalog.ttl` from the release's own version and issue date; several of the Turtle files above are themselves built from the CSV tables beside them.

**What each store holds.** Jena and the Delta table `epm_triples` hold all three graphs of each module in full. Neo4j and AuraDB hold all of `<module>.ttl`, with no selective projection, and one `ModuleRelease` node per module drawn from `catalog.ttl`; the shapes validate the release and are not nodes. There is one local Neo4j and one standing Jena. `projection/README.md`, "What each store holds", gives the policy.

## Each module and its links

### core: the process map

Each process is a `skos:Concept` with a notation, a definition and a parent (`skos:broader`). An approved relationship between two processes appears twice: as a direct triple, and as a canonical-fact node that carries its evidence row.

<!-- module: core -->
```turtle
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix proc: <https://w3id.org/lsc/ontology/process/> .
@prefix core: <https://w3id.org/lsc/ontology/modules/core/> .
@prefix fact: <https://w3id.org/lsc/ontology/fact/> .

proc:CM-1-3-7-1-7 a skos:Concept ;
    skos:prefLabel "Coordinate Customer Onboarding"@en ;
    skos:notation "CM 1.3.7.1.7" ;
    skos:broader proc:CM-1-3-7-1 .

fact:CM-1-3-7-1-1--informedBy--CM-1-3-7-4-6 a core:CanonicalFact ;
    core:factSubject proc:CM-1-3-7-1-1 ;
    core:factPredicate core:informedBy ;
    core:factObject proc:CM-1-3-7-4-6 ;
    core:evidenceRow "REL-00915" .
```

### organization: who does what

The module holds roles (positions, never people), RACI assignments as nodes of their own, and the definition of a control relationship between legal entities. It links to core through `forProcess`: each assignment names the process it is for.

<!-- module: organization -->
```turtle
@prefix org: <http://www.w3.org/ns/org#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix proc: <https://w3id.org/lsc/ontology/process/> .
@prefix orgm: <https://w3id.org/lsc/ontology/modules/organization/> .
@prefix role: <https://w3id.org/lsc/ontology/modules/organization/role/> .
@prefix asg: <https://w3id.org/lsc/ontology/modules/organization/assignment/> .
@prefix raci: <https://w3id.org/lsc/ontology/modules/organization/raci-level/> .

role:it-data-owner a org:Role ;
    skos:prefLabel "IT Data Owner"@en .

asg:CM-1-1-2-1--accountable--it-data-owner--e842d6dc a orgm:ResponsibilityAssignment ;
    orgm:forProcess proc:CM-1-1-2-1 ;
    orgm:assignedRole role:it-data-owner ;
    orgm:raciLevel raci:accountable .
```

### ref-mpc: the company facts

This is the only company-specific module. It uses the terms of `organization` and `party` and defines none of its own. Keeping MPC's facts here leaves every other module company-neutral (EPM-DEC-001-0015).

<!-- module: ref-mpc -->
```turtle
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix orgm: <https://w3id.org/lsc/ontology/modules/organization/> .
@prefix refmpc: <https://w3id.org/lsc/ontology/modules/ref-mpc/> .

refmpc:mpc-controls-mplx a orgm:ControlRelationship ;
    orgm:controllingEntity refmpc:mpc ;
    orgm:controlledEntity refmpc:mplx ;
    orgm:asOf "2025-12-31"^^xsd:date .
```

### party: the customer domain

The module holds the decision owner's conceptual model of the customer, the customer systems with their data flows and attributes, and the customer lifecycle (EPM-DEC-001-0068 to 0070). The lifecycle has a business view and a system view. A business stage links to core through `stageProcess`, and to the system stages it matches through `correspondsTo`.

<!-- module: party -->
```turtle
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix proc: <https://w3id.org/lsc/ontology/process/> .
@prefix party: <https://w3id.org/lsc/ontology/modules/party/> .
@prefix stage: <https://w3id.org/lsc/ontology/modules/party/lifecycle-stage/> .
@prefix sysstage: <https://w3id.org/lsc/ontology/modules/party/system-stage/> .
@prefix prole: <https://w3id.org/lsc/ontology/modules/party/party-role/> .

stage:onboarding
    party:stageProcess proc:CM-1-3-7-1-1, proc:CM-1-3-7-1-7, proc:CM-1-3-7-2-1,
        proc:CM-1-3-7-4-2, proc:CM-1-3-7-4-6 ;
    party:correspondsTo sysstage:master, sysstage:record .

prole:payer a skos:Concept ;
    skos:prefLabel "Payer"@en ;
    skos:definition "The role of the party that pays the invoices of an account."@en .
```

### kpi: what each measure means

Each measure is a definition, never a value, classified by its kind (EPM-DEC-001-0042). It links to core through `informsProcess`.

<!-- module: kpi -->
```turtle
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix proc: <https://w3id.org/lsc/ontology/process/> .
@prefix kpi: <https://w3id.org/lsc/ontology/modules/kpi/> .
@prefix measure: <https://w3id.org/lsc/ontology/modules/kpi/measure/> .
@prefix kind: <https://w3id.org/lsc/ontology/modules/kpi/measure-kind/> .

measure:crack-spreads
    skos:prefLabel "Crack Spreads Pricing"@en ;
    kpi:measureKind kind:market-indicator ;
    kpi:informsProcess proc:CM-1-1-4-7-4 .
```

### market-data: the crack-spread recipes

Each series is a recipe: the benchmark legs it is built from and its region. The module holds no prices; its shapes reject them. It links to `kpi`: each series names the measure it publishes through `seriesOf`.

<!-- module: market-data -->
```turtle
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix mkt: <https://w3id.org/lsc/ontology/modules/market-data/> .
@prefix series: <https://w3id.org/lsc/ontology/modules/market-data/series/> .
@prefix leg: <https://w3id.org/lsc/ontology/modules/market-data/leg/> .
@prefix region: <https://w3id.org/lsc/ontology/modules/market-data/region/> .
@prefix measure: <https://w3id.org/lsc/ontology/modules/kpi/measure/> .

series:crack-gulf-coast-3-2-1
    skos:prefLabel "Gulf Coast 3-2-1 crack spread"@en ;
    mkt:seriesOf measure:crack-spreads ;
    mkt:region region:gulf-coast ;
    mkt:leg leg:crack-gulf-coast-3-2-1--meh, leg:crack-gulf-coast-3-2-1--usgc-cbob,
        leg:crack-gulf-coast-3-2-1--usgc-ulsd .
```

### data-product: the portfolio

The portfolio runs from segments to product lines to data products. A data product links to core directly in a few places, through `producedBy` and `consumedBy`, and a segment through `anchoredIn`. Most of the portfolio's links to processes run through value-stream steps (next section).

<!-- module: data-product -->
```turtle
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix proc: <https://w3id.org/lsc/ontology/process/> .
@prefix dp: <https://w3id.org/lsc/ontology/modules/data-product/> .
@prefix product: <https://w3id.org/lsc/ontology/modules/data-product/product/> .
@prefix line: <https://w3id.org/lsc/ontology/modules/data-product/line/> .

product:customer-master
    skos:prefLabel "Customer Master"@en ;
    skos:broader line:marketing-sales ;
    dp:producedBy proc:CM-1-3-7-1-1 .
```

### value-stream: how value flows

The two value streams are an overlay on the process map. A step `realizes` core processes. A capability aligns to a core process group. A step also `produces` and `consumes` data products, and links to the measures it moves through a measure link that names the relationship.

<!-- module: value-stream -->
```turtle
@prefix proc: <https://w3id.org/lsc/ontology/process/> .
@prefix vs: <https://w3id.org/lsc/ontology/modules/value-stream/> .
@prefix vsprocess: <https://w3id.org/lsc/ontology/modules/value-stream/process/> .
@prefix capability: <https://w3id.org/lsc/ontology/modules/value-stream/capability/> .
@prefix mlink: <https://w3id.org/lsc/ontology/modules/value-stream/measure-link/> .
@prefix rel: <https://w3id.org/lsc/ontology/modules/value-stream/measure-relationship/> .
@prefix product: <https://w3id.org/lsc/ontology/modules/data-product/product/> .
@prefix measure: <https://w3id.org/lsc/ontology/modules/kpi/measure/> .

vsprocess:otc-capture-validate-order
    vs:realizes proc:CM-1-3-7-3-1 ;
    vs:usesCapability capability:otc-order-management .

capability:otc-order-management vs:alignsToProcessGroup proc:CM-1-3-7-3 .

vsprocess:market-price-calculation-validation
    vs:consumes product:external-market-data, product:physical-trading ;
    vs:produces product:master-pricing ;
    vs:measureLink mlink:market-price-calculation-validation--crack-spreads .

mlink:market-price-calculation-validation--crack-spreads a vs:MeasureLink ;
    vs:measure measure:crack-spreads ;
    vs:relationship rel:benchmarks .
```

### system: what each process uses

The module holds the applications, office tools and working documents the process map names. It links to core through `supports`, taken from the process map's "systems" fields. The `party` module's customer systems join it through `skos:exactMatch` where they are the same system.

<!-- module: system -->
```turtle
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix proc: <https://w3id.org/lsc/ontology/process/> .
@prefix sys: <https://w3id.org/lsc/ontology/modules/system/> .
@prefix system: <https://w3id.org/lsc/ontology/modules/system/system/> .
@prefix syskind: <https://w3id.org/lsc/ontology/modules/system/kind/> .

system:rightangle
    skos:prefLabel "RightAngle"@en ;
    sys:systemKind syskind:application ;
    sys:supports proc:CM-1-1-2-2, proc:CM-1-1-2-2-3 .
```

### lane: where a trading process sits

The four office lanes are a code list. The module places only the processes the process map places, with at most one lane each, and a child does not inherit its parent's lane (EPM-DEC-001-0056). Here the process is the subject: `officeLane` points from core to the lane.

<!-- module: lane -->
```turtle
@prefix proc: <https://w3id.org/lsc/ontology/process/> .
@prefix lane: <https://w3id.org/lsc/ontology/modules/lane/> .
@prefix lanev: <https://w3id.org/lsc/ontology/modules/lane/lane/> .

proc:CM-1-2-1 lane:officeLane lanev:front-office .
proc:CM-1-2-2 lane:officeLane lanev:middle-office .
proc:CM-1-2-3 lane:officeLane lanev:operations .
proc:CM-1-2-4 lane:officeLane lanev:back-office .
```

### technical-graph: what was built on the data platform

The module defines the kinds of thing a technical graph records about a data platform as built: hosts, source databases, tables, views, metric views, pipeline steps, quality checks and agents. It holds definitions only; the graph's nodes, row counts and check results stay in the technical graph (EPM-DEC-001-0112). Its links reach three modules by IRI: a metric view `implements` a `kpi` measure, a source database `standsFor` a `system` system, and a built thing is `designedAs` its design in `data-product`, with its `layer` from data-product's layer code list. Here the definitions state the first two links.

<!-- module: technical-graph -->
```turtle
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tg: <https://w3id.org/lsc/ontology/modules/technical-graph/> .
@prefix kpi: <https://w3id.org/lsc/ontology/modules/kpi/> .
@prefix sys: <https://w3id.org/lsc/ontology/modules/system/> .

tg:implements rdfs:domain tg:MetricView ;
    rdfs:range kpi:MeasureDefinition .
tg:standsFor rdfs:domain tg:SourceDatabase ;
    rdfs:range sys:System .
```

### logical-model: logical data models

*2026-11-02:* not released in `main`; its first model, the customer logical model, ships only in the release (EPM-DEC-001-0113). The module keeps each logical data model exported from ER Studio Data Architect as two views. The first is ER Studio's export, unchanged, in ER Studio's namespace and its own named graph. The second is an annotation layer in the module's namespace, keyed on ER Studio's identifier for each entity. The layer links each entity to three modules by IRI: `lm:sourceSystem` to a system of `system` or a customer system of `party`, `lm:describes` to a `party` concept or class, and `lm:implementedBy` to a `data-product` platform table or data product. `lm:inModel` names the model the entity belongs to. Here the subject is ER Studio's own entity IRI, and nothing is re-minted. The guide's "Adding a logical model" gives the method for any later model.

Because the module has no release in `main`, this quote is from the layer of the made-up example model, `logical-model/example/example-logical-model.layer.ttl`, which `scripts/check.sh` verifies; it is not a release.

```text
@prefix lm: <https://w3id.org/lsc/ontology/modules/logical-model/> .
@prefix party: <https://w3id.org/lsc/ontology/modules/party/> .
@prefix system: <https://w3id.org/lsc/ontology/modules/system/system/> .
@prefix product: <https://w3id.org/lsc/ontology/modules/data-product/product/> .
@prefix er: <https://www.erstudio.com/semanticmodel/> .

er:example_core_Example_Account_Dim lm:describes party:CustomerAccount ;
    lm:implementedBy product:customer-master ;
    lm:inModel <https://w3id.org/lsc/ontology/modules/logical-model/model/example-logical-model> ;
    lm:sourceSystem system:profisee .
```

### integration: rules that apply across modules

`integration` adds no new facts. It packages three sets of rules that apply to the other modules' links, sources and bindings:

- **placement** says which links prove the work and which only give context. Producing a data product certifies; every other placement is context (EPM-DEC-001-0058).
- **authority** puts each cited source in one evidence tier, and the best tier wins when two sources disagree (EPM-DEC-001-0059).
- **consumer** sets how a catalog binds a measure to the data product that publishes it, and what an agent may answer from the graph and must refuse (EPM-DEC-001-0061).

<!-- module: integration -->
```turtle
@prefix plc: <https://w3id.org/lsc/ontology/modules/placement/> .
@prefix pkind: <https://w3id.org/lsc/ontology/modules/placement/kind/> .
@prefix auth: <https://w3id.org/lsc/ontology/modules/authority/> .
@prefix tier: <https://w3id.org/lsc/ontology/modules/authority/tier/> .
@prefix src: <https://w3id.org/lsc/ontology/source/> .
@prefix vs: <https://w3id.org/lsc/ontology/modules/value-stream/> .
@prefix dp: <https://w3id.org/lsc/ontology/modules/data-product/> .
@prefix sys: <https://w3id.org/lsc/ontology/modules/system/> .
@prefix lane: <https://w3id.org/lsc/ontology/modules/lane/> .
@prefix kpi: <https://w3id.org/lsc/ontology/modules/kpi/> .

vs:produces plc:placementKind pkind:certification .
dp:producedBy plc:placementKind pkind:certification .
vs:consumes plc:placementKind pkind:context .
sys:supports plc:placementKind pkind:context .
lane:officeLane plc:placementKind pkind:context .
kpi:informsProcess plc:placementKind pkind:context .

src:mpc-economics-crack-spread-kpi-definition auth:evidenceTier tier:process-authority .
src:cme-trading-crack-spreads-2024 auth:evidenceTier tier:industry .
```

## One walk across modules

This walk starts at a market-data series and ends at a core process, crossing five modules. Each arrow is a link quoted above.

```text
Gulf Coast 3-2-1 crack spread (market-data)
  ─seriesOf→ Crack Spreads Pricing (kpi) ─informsProcess→ CM 1.1.4.7.4 (core)
       ↑ measure link, relationship "benchmarks"
Market Price Calculation & Validation (value-stream)
  ─produces→ Master Pricing (data-product)
  ─consumes→ External Market Data, Physical Trading (data-product)
```

`integration` then says what each link proves: `produces` certifies the work, and the rest are context. No data product publishes the crack-spread measure yet, because no source says which one does; `consumer` records that gap. *2026-10-26:* since `data-product` 1.2.0, the crack-spread metric view serves the measure (`dp:servesMeasure`), a binding at the view, not a catalog row's `con:publishesMeasure` (EPM-DEC-001-0100, item 4).
