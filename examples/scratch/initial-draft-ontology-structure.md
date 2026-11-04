# Scratch reconciliation: enterprise ontology namespace design

Status: non-authoritative scratch, reconciled for I-11 on 2026-11-04.

This file and [the master use case](master-use-case-kpi-store-semantic-governance.md) remain examples. Closing I-11 does not promote either file into the foundation or a released ontology. The disposition below is repository maintenance; it adopts no new business rule, class, property or namespace.

## Authority and boundaries

[EPM-FOUND-003](../../EPM_Foundation_v2_Markdown_HTML/EPM-FOUND-003.md) is the human-readable semantic model. [EPM-FOUND-004](../../EPM_Foundation_v2_Markdown_HTML/EPM-FOUND-004.md) is the ontology design and its implementation path. Exact machine terms belong to Turtle in Git. The foundation's Stage 2 vocabulary is in [stage2_enterprise_kpi_ontology.ttl](../../ontology/stage2_enterprise_kpi_ontology.ttl); the later business-architecture modules and releases are indexed by [the ontology README](../../business_architecture/ontology/README.md). The latter takes precedence for this project's business-architecture ontology, as AGENTS.md requires. A prefix is an abbreviation, not an authority of its own.

The [master index's Meaning vs compute section](../../EPM-FOUND-000.md#meaning-vs-compute-target-band-split) and [ADR-HL-021](../../EPM_Homelab/02-Tool-Selection-and-ADRs.md#adr-hl-021--no-enterprise-triple-store-turtle-in-git-expose-through-neo4j) keep the same binding: one ontology IRI to one `dim_kpi_metadata` row to the Metric View and measure named by its formula pointer, compiled with `MEASURE()`. The Store row owns identity, approval, catalog status and the formula pointer. Purview and Unity Catalog support discovery and governance; they do not replace that row. A contract or example URI creates no additional KPI identity.

Process authority remains `business_architecture/business_process/` and `business_architecture/schema/`. A process link in Turtle or a contract refers to that authority. Neither a scratch namespace nor a domain model replaces it.

## Prefix and identifier disposition

These dispositions cover this namespace sketch and the linked master use case named in issue #18. The separate [metadata journey slide draft](metadata-journey-slides-content-draft.md) and its slide pages remain illustrative scratch; this reconciliation does not adopt their content. "Retired" means no proposed project namespace or alias survives; its spelling remains here only to record the disposition. "Scratch-only" means an example, with no adoption into Turtle or the foundation. Any future promotion follows FOUND-004 and the current ontology playbook through a separate reviewed change.

| Prefix or identifier family | Disposition | Authority or next step |
|---|---|---|
| `ekpi:` and `data:` | Existing Stage 2 vocabulary, unchanged | Read their declared IRIs in the Stage 2 Turtle. They are its project prefixes, not its only prefixes and not the complete prefix set of the later module releases. |
| `biz:`, `kpi:` as proposed competing scratch namespaces; `ex:domain/Refining`, `ex:process/…`, `ex:kpi/CrackSpread321` | Retired from the sketch's proposed design | Process identity stays in the two authority folders; KPI identity uses the existing IRI, Store row and formula pointer. This does not retire any prefix in a released module. |
| `example:` | Scratch-only notation in authoring guidance | No namespace declaration or deployed IRI is created. |
| `skos:`, `foaf:`, `prov:`, `dcat:` in the master use case | Scratch-only references to external vocabulary names | Their occurrence here neither imports a vocabulary nor adopts a new project mapping. The exact terms are listed below. |
| `odps:` as an RDF prefix | Retired | The scratch declares no RDF namespace for ODPS. Its contract fields are illustrative YAML keys, not ontology properties. |
| `https://metadata.example.org/domains/Refining`, `/kpis/CrackSpread321`, `/concepts/DollarPerBarrel` | Scratch-only IRI placeholders | They replace the earlier `metadata.enterprise.org` example host. No mapping to a real domain, KPI or unit is asserted. A real contract must use its released IRI and Store binding. |
| `urn:dataproduct:refining:crack-spread-321`, example API/SQL/Power BI endpoints, schema/table names and formula pointers | Scratch-only identifiers for the contract example | They do not identify deployed objects. No new process or KPI identity follows from them. |

## Class and property disposition through FOUND-004

| Names in the namespace sketch, master use case or issue #18 | Disposition | Basis |
|---|---|---|
| `BusinessProcess`, `KPI`, `Metric`, `KPIFormula`, `CalculationLogic`, `AggregationType`, `logicExpression` with `ekpi:` | Existing Stage 2 terms, unchanged | The Turtle declares these names. This reconciliation adds no term or mapping. |
| `Metric` used as a synonym for `KPI` | Retired interpretation | Stage 2 declares `KPI` as a subclass of `Metric`; the names are not interchangeable. FOUND-003/004 distinguish the concepts. |
| `LogicalEntity`, `mapsToPhysical` | Scratch-only candidates named by issue #18 | Neither is declared by the Stage 2 Turtle. No class or mapping is adopted here. Any proposal must use FOUND-004 and check the later released module vocabulary before adding a term. |
| `aggregationMethod` | Retired proposed alias | Stage 2 uses `AggregationType` for the aggregation category. This is not an equivalence assertion between a proposed property and that class. Execution still belongs to the formula pointer and Metric View. |
| `skos:Concept`, `foaf:Person`, `prov:wasAttributedTo`, `prov:wasGeneratedBy`, `prov:used`, `dcat:endpointURL`, `dcat:accessURL` | Scratch-only vocabulary references | The master use case illustrates possible descriptions. It declares no new project class/property, required import or approved mapping. |
| `odps:freshnessTarget` | Retired RDF-style spelling | The example now calls it the YAML field `freshnessTarget`; no standard-conformance claim or RDF property is made. |
| `Customer`, `Refinery`, `Crude Barrel`, `Crack Spread`, `Gross Refining Margin`, `Named KPI`, `Candidate KPI` | Scratch-only business examples and governance language | These labels do not declare OWL classes or new individuals. In particular, do not create CandidateKPI or ApprovedKPI classes; FOUND-004 keeps catalog status on the Store row. |
| `domainIRI`, `ontologyIRI`, `mapsToConcept`, `endpointURL`, `formulaPointer`, `underlyingFormulaNotation`, and the remaining YAML keys in section 8 | Scratch-only contract fields | They are fields of the illustrative document, not RDF property declarations. The YAML has not been validated against an ODPS schema. No field becomes part of the ontology through this example. |
| Domain Data Owner, Data Product Owner, Data Steward, Technical Owner; the diagram's other component names | Scratch-only role and component labels | No staffing assignment, new ontology class, operational workflow or software deployment is approved by this reconciliation. |

## What remains outside I-11

The master use case's contract, automation, ownership scheme, SLAs, thresholds and consumption examples remain scratch. Adopting any of them requires its own evidence and decision. C-08, the Family C and remaining Family E reconciliation, stays open. The namespace sketch and master use case remain separate documents.

When extending either example, check the current released vocabulary first. Keep an undeclared term marked scratch-only until a separate FOUND-004 proposal is reviewed. Preserve the Store binding and process authority above.
