# Downstream O&G Knowledge Homelab — Curriculum and Learning Modules

**Title:** Downstream O&G Knowledge Homelab — Curriculum and Learning Modules  
**Purpose:** Define an evidence-producing learning sequence that builds the Gasoline Netback / Refining Margin CPG capstone from conceptual model through a grounded AI-agent interface. Each module uses the personal, open-source homelab stack and a consistent Downstream O&G scenario.  
**Status:** Draft (personal homelab, not an EPM governed artifact)  
**Owner:** Hamid Adesokan  
**Last updated:** 2026-08-10  

## Curriculum intent and roadmap mapping

This curriculum converts the six-phase roadmap into a learning path. Phase 0 is a preflight for the repository, Python environment, Docker Compose, PostgreSQL 18, and DuckDB. Modules 01–04 support Phase 2; Modules 05–06 support Phases 1 and 3; Modules 07–08 cover Phases 4 and 6; Modules 09–10 implement the KPI and lineage vertical slice; and Module 11 completes Phase 5. Clearly labeled extensions within Modules 04, 05, 06, 10, and 11 add the O2C process backbone, ERP/CRM source systems, master-data exercise, entity-linked unstructured-data path, an Owlready2/HermiT ontology reasoning gate, and an agent-agnostic MCP server with a tiered resolution model, without renumbering the established module sequence. The reasoning-gate and MCP/tiered-resolution extensions are adapted from patterns in AWS's Context Ontology Accelerator (ADR-HL-018 through ADR-HL-020 in `02-Tool-Selection-and-ADRs.md`; [AWS Context Ontology Accelerator docs](https://aws.github.io/context-ontology-accelerator/)).

The sequence expands Hamid Adesokan’s original six-module sketch into eleven modules spanning conceptual modeling, controlled vocabularies, SKOS, RDF/RDFS/OWL, materialized and virtual RDF, SHACL, Neo4j, KPI engineering, lineage, and a graph-grounded agent. The capstone is the simplified **Gasoline Netback / Refining Margin CPG** KPI, combining public EIA inputs with synthetic terminal, custody-transfer, contract, order, and invoice facts. EIA publishes the spot-price and petroleum-marketing sources used for the exercises ([EIA Spot Prices](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm); [EIA Petroleum Marketing Monthly](https://www.eia.gov/petroleum/marketing/monthly/)).

PostgreSQL retains operational facts, DuckDB retains analytical/KPI facts, and RDF/OWL supplies meaning. Ontop exposes relational sources virtually where possible; Fuseki and Neo4j receive only deliberate materializations, avoiding a graph copy as an independent business record.

### Module map

| Module | Primary capability | Roadmap emphasis | Principal tools | Estimated time |
|---|---|---|---|---|
| 01 | Conceptual model and competency questions | Phase 2 | Protégé Desktop, RDFLib | 4–6 hours |
| 02 | Controlled vocabulary | Phase 2 | Protégé Desktop, RDFLib, SKOS | 4–6 hours |
| 03 | SKOS concept scheme and RDF triples | Phase 2 | RDFLib, Protégé Desktop, SKOS | 5–7 hours |
| 04 | RDFS/OWL ontology foundation + reasoning gate | Phase 2 | Protégé Desktop, Owlready2, RDFLib | 10–13 hours |
| 05 | Materialized facts and SPARQL | Phases 1 and 3 | RDFLib, Morph-KGC, Apache Jena Fuseki | 8–12 hours |
| 06 | R2RML and virtual RDF | Phase 3 | PostgreSQL 18, Ontop, RDFLib | 8–10 hours |
| 07 | SHACL data-quality gate | Phases 2 and 6 | pySHACL, RDFLib, Docker Compose | 6–8 hours |
| 08 | RDF-to-LPG serving graph | Phase 4 | Neo4j Community Edition, neosemantics (n10s), Morph-KGC | 8–10 hours |
| 09 | Governed KPI Store | Phases 1 and 3 | DuckDB, PostgreSQL 18, Dagster | 10–14 hours |
| 10 | Asset orchestration and lineage | Phase 6 | Dagster, OpenLineage, Marquez | 8–12 hours |
| 11 | Grounded agent capstone + MCP server + tiered resolution | Phase 5 | LangGraph, Ollama, FastAPI, MCP Python SDK, Neo4j Community Edition | 15–20 hours |
| O2C extensions in 04, 05, 06, and 10 | O2C taxonomy, ERP/CRM, master-data matching, and unstructured-data fusion | Phases 1–6 | ERPNext, Frappe, trycompai/crm, block/buzz, semantica | 18–26 hours |
| COA-inspired extensions in 04 and 11 | Owlready2/HermiT reasoning gate (04); MCP server and tiered resolution model (11, folded into its own row above) | Phase 2 and Phase 5 | Owlready2, Dagster, MCP Python SDK | 2–3 hours (Module 04 extension only; Module 11's MCP/tiered-resolution time is already included in its row above) |

## Module 01: Introduction to Conceptual Modelling

**Learning objectives**

- Distinguish a business concept, an individual instance, a schema/model element, and a physical database field.
- Explain the T-Box as the terminology/model layer and the A-Box as the instance-fact layer.
- Frame competency questions before choosing tables, predicates, or graph labels.

**Key concepts**

- Conceptual versus logical versus physical model; identity, class, relationship, attribute, and event.
- T-Box: `Terminal`, `Product`, `Customer`, `Contract`, and `CustodyTicket` definitions and relationships. A-Box: an individual terminal, a regular-gasoline product, a customer, and a specific ticket.
- The custody-event-centric O2C shape: a ticket/BOL records observed or corrected volume, product, terminal, commercial party, and time.
- Competency questions, including: “Which terminal sold a product under which contract?”

**Hands-on lab**

Create a one-page conceptual model for the capstone. Use the nouns `Terminal`, `Product`, `Customer`, `Contract`, `CustodyTicket`, `Order`, `Invoice`, `PriceObservation`, and `KPIResult`; draw at least eight named relationships. Mark `Terminal`, `Product`, and `Contract` as T-Box classes, then create four A-Box examples: `GalvestonRack01`, `Regular87`, `GulfWholesaleCo`, and ticket `CT-2026-08-03-001`. Write six competency questions, including one that explains a netback movement through a ticket volume, product price, and contract differential.

**Tools used**

Protégé Desktop for the visual class sketch; RDFLib for a small Python notebook that prints the four example identifiers. Protégé Desktop is the selected visual OWL/RDFS editor, while RDFLib is the Python RDF library for the homelab ([Protégé](https://protege.stanford.edu/); [RDFLib](https://github.com/rdflib/rdflib)).

**Deliverable/artifact produced**

A conceptual-model diagram, a glossary seed list of the nine terms, and `competency_questions.md` containing six testable questions and their expected answer types.

**Estimated time**

4–6 hours.

## Module 02: Controlled Vocabularies

**Learning objectives**

- Separate an approved business term from a database code, display label, synonym, and deprecated name.
- Design a small vocabulary that prevents inconsistent product, terminal-type, and customer-channel descriptions.
- Apply preferred labels, alternative labels, scope notes, and identifiers consistently.
- Decide when a term belongs in a controlled vocabulary rather than as an OWL class or instance.

**Key concepts**

- Canonical identifier, preferred term, synonym, abbreviation, ambiguity, and stewardship.
- Product-grade terms: Regular 87, Midgrade 89, Premium 93, and reformulated gasoline where appropriate for the exercise.
- Terminal-type terms: refined-product terminal, pipeline-connected rack, and marine terminal. Customer-channel terms: branded retailer, unbranded marketer, and commercial fleet.
- Consistency rules: one preferred label per concept; codes may change but concept URIs do not; synonyms are searchable but not silently substituted in KPI logic.

**Hands-on lab**

Build a 24-concept vocabulary spreadsheet or RDFLib-generated table: 10 product/grade concepts, 7 terminal-type concepts, and 7 customer-channel concepts. Include identifier, preferred label, alternative labels, definition, scope note, status, and an example source code. Resolve three deliberate conflicts: map “87 octane,” “regular unleaded,” and “Regular 87” to one approved concept; distinguish “rack” as a terminal facility context from “rack price”; and mark “jobber” as an alternative label only when it means an unbranded marketer in the exercise. Add two deprecated labels and document their replacement concepts.

**Tools used**

RDFLib and Protégé Desktop, using SKOS as the homelab glossary/taxonomy standard ([W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)).

**Deliverable/artifact produced**

`downstream_vocab_seed.csv` and a controlled-vocabulary decision log with the three ambiguity resolutions and two deprecation decisions.

**Estimated time**

4–6 hours.

## Module 03: SKOS

**Learning objectives**

- Express a controlled vocabulary as RDF triples instead of a disconnected spreadsheet.
- Create a SKOS concept scheme with stable concept URIs, labels, hierarchy, and notes.
- Use `skos:broader`, `skos:narrower`, `skos:prefLabel`, `skos:altLabel`, and `skos:inScheme` correctly.
- Inspect and query the resulting triples without confusing a SKOS concept with a physical product instance.

**Key concepts**

- RDF subject–predicate–object triples, IRIs, literals, namespaces, and Turtle syntax.
- A SKOS `ConceptScheme` as a bounded vocabulary; a `Concept` as a business meaning; `topConceptOf` and hierarchy navigation.
- Example hierarchy: Fuel → Gasoline → Conventional Gasoline → Regular 87 and Premium 93. The hierarchy classifies terms; it does not assert that an individual custody ticket is itself a vocabulary concept.

**Hands-on lab**

Convert the Module 02 vocabulary into `downstream-glossary.ttl`. Create three schemes—Product Grade, Terminal Type, and Customer Channel—with at least 24 concepts. Model `Fuel > Gasoline > Regular 87/Premium 93`, add `skos:altLabel "regular unleaded"@en` to Regular 87, and include a scope note that octane-grade comparisons in this sandbox are nominal labels rather than a laboratory-quality specification. Use RDFLib to load the Turtle file and run a SPARQL query returning every narrower concept below `Gasoline`; print the preferred and alternative labels beside each URI.

**Tools used**

RDFLib, Protégé Desktop, and SKOS ([W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)).

**Deliverable/artifact produced**

A validated `downstream-glossary.ttl`, a namespace/URI convention note, and `query_gasoline_hierarchy.rq` with its captured result.

**Estimated time**

5–7 hours.

## Module 04: RDFS and Ontology Foundations

**Learning objectives**

- Define OWL classes, object properties, datatype properties, domains, ranges, and cardinality intent.
- Explain the difference between a SKOS glossary concept and an ontology class used to model operational facts.
- Use RDFS/OWL inference cautiously to add useful classifications without hiding required data-quality checks.
- Translate competency questions into a small, testable ontology skeleton.

**Key concepts**

- `rdfs:Class`, `rdfs:subClassOf`, `rdfs:domain`, `rdfs:range`, object property, datatype property, and `owl:equivalentClass` only where equivalence is truly intended.
- Core classes: `Terminal`, `Product`, `CustodyTicket`, `Customer`, `Contract`, `Order`, `Invoice`, `PriceObservation`, and `KPIResult`.
- Key predicates: `handledAtTerminal`, `forProduct`, `soldToCustomer`, `governedByContract`, `hasNetVolumeGallons`, `hasTicketDate`, `hasPriceObservation`, and `isResultForKPI`.
- Open-world semantics for ontology meaning versus closed-world expectations enforced later through SHACL.

**Hands-on lab**

Create `netback-ontology.ttl` in Protégé Desktop. Model `Terminal`, `Product`, `CustodyTicket`, `Customer`, and `Contract` as OWL classes; add the six key predicates with explicit domain and range; and declare `RackTerminal` a subclass of `Terminal`. Add 10 example A-Box instances, including two rack terminals, three products, two customers, two contracts, and one ticket. Use Owlready2 or RDFLib to verify that a `RackTerminal` instance is also recognized as a `Terminal`. Record three non-goals: no refinery process simulation, no enterprise-wide customer master, and no claim that an OWL restriction alone assures data completeness.

**Tools used**

Protégé Desktop, RDFLib, and Owlready2. Owlready2 is used only for Python-side ontology classes and targeted reasoning; it is not a replacement for the RDF graph or validation pipeline.

**Deliverable/artifact produced**

`netback-ontology.ttl`, a rendered class/property diagram, `ontology_competency_matrix.md`, and a short inference test.

**Estimated time**

8–10 hours.

### O2C process-taxonomy extension

**Learning objectives**

- Map the approved Downstream O&G Order to Cash Level 0/1/2 taxonomy to the ontology's T-Box process nodes and seed KPI candidates without treating every process measurement as an approved KPI.
- Use the taxonomy to decide which capabilities receive native ERPNext implementation and which receive light custom Frappe workflow depth.

**Hands-on lab**

Add `OrderToCashProcess`, `ProcessGroup`, and `KpiCandidate` to `netback-ontology.ttl`. Model Level 0 `Order to Cash`, its ten Level 1 groups, and 64 Level 2 processes as T-Box process nodes. Retain Organization & People, Information & Systems, Process & Policy, and Automation/Analytics/Digital/Tax catalyst tags as process metadata. For every Level 2 node, record a candidate measure or KPI hypothesis, classification status, and rationale; only promote a candidate when its definition, owner, grain, target, and action use are specified. Use the map to set build depth: fully exercise Master Data Mgmt, Quote & Sale, Order & Fulfillment, Billing, and Receipt through ERPNext; implement light stateful Frappe workflows for Credit & Risk, Collection, Dispute, Close, and Measure & Custody Transfer; and embed the downstream O&G-specific process structure, approved 2026-08-09, directly in the Level 1/Level 2 taxonomy rather than layering it atop a generic model.

**Deliverable/artifact produced**

`o2c_process_taxonomy.ttl`, a Level 1/Level 2-to-T-Box/KPI-candidate matrix, and an ERPNext/Frappe build-depth decision log.

**Estimated time**

6–8 hours.

### Ontology reasoning gate extension (Owlready2/HermiT)

**Learning objectives**

- Explain the difference between an OWL consistency check, automatic reclassification, and SHACL shape validation, and why a homelab pipeline benefits from all three rather than treating them as interchangeable.
- Run Owlready2's `sync_reasoner()` (HermiT, the Owlready2 default) against the T-Box and interpret a consistency failure or an unexpected reclassification.
- Explain why this reasoning step is placed before Morph-KGC materialization rather than after (ADR-HL-019).

**Key concepts**

- HermiT is a Java-based OWL DL reasoner bundled with Owlready2 and invoked through a single `sync_reasoner()` call; Pellet is available as `sync_reasoner_pellet()` for cases needing data-property inference, at the cost of an AGPL license versus HermiT's LGPL ([Owlready2 reasoning docs](https://owlready2.readthedocs.io/en/v0.51/reasoning.html)).
- Asserted versus inferred knowledge: reasoner output should be written to a separate inference ontology, not merged silently into the hand-authored T-Box.
- This pattern is adapted from AWS Context Ontology Accelerator's ontology-engine reasoning step, which runs consistency checking and classification (HermiT/ELK) as an explicit step of its Model stage before publishing an ontology proposal ([COA GitHub repo](https://github.com/aws/context-ontology-accelerator)).

**Hands-on lab**

Load `netback-ontology.ttl` (with the O2C taxonomy extension applied) into Owlready2 and run `sync_reasoner()`. Deliberately introduce one inconsistency (for example, asserting a `Terminal` individual is also a disjoint `Customer`) and confirm the reasoner reports it. Fix the inconsistency, rerun, and confirm a clean pass. Wire this check as a new Dagster asset that gates the existing Morph-KGC materialization asset: materialization must not proceed on a reported-inconsistent result. Add competency question 18 from `05-Domain-Model-and-Ontology-Pilot.md` to the pilot's validation notes.

**Tools used**

Owlready2 (HermiT via `sync_reasoner()`), Dagster.

**Deliverable/artifact produced**

A reasoning-gate Dagster asset, a short before/after inconsistency demonstration, and an updated `ontology_competency_matrix.md` entry for competency question 18.

**Estimated time**

2–3 hours.

## Module 05: Grounding Concepts in Facts

**Learning objectives**

- Map synthetic O2C data and selected EIA observations into RDF instances that conform to the ontology.
- Distinguish stable curated facts worth materializing from operational facts better exposed virtually later.
- Load an RDF dataset into the primary SPARQL endpoint and query it reproducibly.
- Read SPARQL results as evidence for business questions rather than as a replacement for KPI calculation logic.

**Key concepts**

- Instance URI construction, typed literals, named graphs, provenance notes, and repeatable mapping.
- Materialized RDF for an instructional snapshot; PostgreSQL and DuckDB remain systems of record for operational and analytical values.
- Apache Jena Fuseki as the homelab’s primary triple store and SPARQL endpoint, selected instead of GraphDB ([Apache Jena Fuseki documentation](https://jena.apache.org/documentation/fuseki2/)).
- Curated mapping with Morph-KGC when a real RDF graph is required for Fuseki or Neo4j ([Morph-KGC documentation](https://morph-kgc.readthedocs.io/)).

**Hands-on lab**

Generate 20 synthetic custody tickets for two terminals and three gasoline products, then map them into RDF alongside five dated EIA-derived price observations. Each ticket must contain a URI, ticket date, terminal, product, customer, contract, positive net volume, and price observation reference. Materialize the snapshot with Morph-KGC or RDFLib, load it into a local Apache Jena Fuseki dataset, and save three SPARQL queries: (1) “which terminals sell Product X,” (2) “what net gallons were ticketed by product this week,” and (3) “which tickets link to the selected EIA price observation.” Capture query output and document the input data snapshot date.

**Tools used**

RDFLib, Morph-KGC, Apache Jena Fuseki, PostgreSQL 18, and Docker Compose. The public price inputs come from EIA’s published spot-price and petroleum-marketing materials ([EIA Spot Prices](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm); [EIA Petroleum Marketing Monthly](https://www.eia.gov/petroleum/marketing/monthly/)).

**Deliverable/artifact produced**

`materialized_netback_facts.ttl`, a Fuseki load script, 20-ticket synthetic dataset, three `.rq` files, and an evidence capture showing each query result.

**Estimated time**

8–12 hours.

### ERPNext administration and customization extension

**Learning objectives**

- Administer the standard O2C transaction path in ERPNext and relate its records to the ontology and relational source tables.
- Build deliberately light custom Frappe DocTypes where the O2C taxonomy requires a workflow that ERPNext does not provide natively.

**Hands-on lab**

Stand up [ERPNext](https://github.com/frappe/erpnext) and configure a Downstream O&G sandbox company, customer, product, price, tax, and payment terms. Execute and preserve linked records for the native `Quotation → Sales Order → Delivery Note → Sales Invoice → Payment Entry` flow. Build five light custom Frappe DocTypes with only the fields, state transitions, approvals, and IDs needed for believable data and linked artifacts: `Credit Limit Review` for Credit & Risk, `Collection Case` for Collection, `Dispute Case` for Dispute, `AR Sub-Ledger Close Task` for Close, and `Custody Transfer Ticket` for Measure & Custody Transfer. Link each record to the relevant customer/order/invoice and mapped taxonomy `process_id`; do not attempt a full ERP-grade implementation.

**Deliverable/artifact produced**

An ERPNext configuration note, one end-to-end linked O2C record set, five DocType definitions with workflow diagrams, and an ID/mapping note for PostgreSQL and the ontology.

**Estimated time**

8–10 hours.

## Module 06: R2RML and Virtual RDF with Ontop

**Learning objectives**

- Map a relational O2C schema to ontology terms using R2RML/OBDA mappings.
- Query PostgreSQL facts through a SPARQL interface without copying them into a triple store.
- Compare virtual RDF behavior, freshness, and operational limits with Module 05’s materialized snapshot.
- Preserve the principle that the operational store remains authoritative for transactional facts.

**Key concepts**

- Relational source schema: `terminal`, `product`, `customer`, `contract`, `custody_ticket`, `order`, and `invoice`.
- R2RML logical tables, subject maps, predicate-object maps, join conditions, template-based IRIs, and datatype conversions.
- Ontop as an OBDA/virtual knowledge graph layer over PostgreSQL ([Ontop VKG guide](https://ontop-vkg.org/guide/)).
- Comparison: Fuseki answers over loaded triples at a known snapshot; Ontop translates SPARQL to PostgreSQL and sees committed source data without an RDF copy.

**Hands-on lab**

Create a PostgreSQL schema for the seven O2C tables and load the same 20 tickets used in Module 05. Write mappings for `CustodyTicket`, `Terminal`, `Product`, `Customer`, and `Contract`; map `custody_ticket.net_volume_gallons` to the ontology’s net-volume predicate and join it to product and terminal tables. Start Ontop against PostgreSQL, then run the Module 05 terminal/product query and weekly volume query against the virtual graph. Insert one additional valid ticket in PostgreSQL, rerun both Ontop and Fuseki queries, and record why the virtual result changes while the materialized snapshot does not.

**Tools used**

PostgreSQL 18, Ontop, RDFLib, Docker Compose, and the Module 04 ontology.

**Deliverable/artifact produced**

`o2c_schema.sql`, R2RML/OBDA mapping files, Ontop configuration, two virtual-graph queries, and `virtual_vs_materialized_comparison.md` with the one-ticket freshness demonstration.

**Estimated time**

8–10 hours.

### External CRM and customer-master matching extension

**Learning objectives**

- Treat CRM and ERPNext as separate source systems for customer-party master data rather than assuming either is automatically authoritative for every attribute.
- Perform a transparent matching and survivorship exercise using the owner's Customer Data Dictionary Template.

**Hands-on lab**

Deploy [trycompai/crm](https://github.com/trycompai/crm) as the external CRM source and create overlapping Account/Contact records alongside ERPNext Customer and Contact records. Build a staging table that preserves each source ID, source system, normalized name/address/email/phone values, match keys, proposed match confidence, survivorship decision, steward note, and unresolved status specified by the Customer Data Dictionary Template. Match a small set of exact, probable, and non-match examples; publish only an approved cross-reference into the customer T-Box/A-Box mapping and retain the original source identifiers and decision evidence. Record the current open gap: custom matching/survivorship logic is a learning exercise, not a replacement for an approved SAP MDG or Profisee analog.

**Deliverable/artifact produced**

CRM and ERPNext source extracts, `customer_match_staging` DDL, a completed customer matching decision sheet, and a source-to-canonical-customer mapping for the graph.

**Estimated time**

4–6 hours.

## Module 07: SHACL Validation

**Learning objectives**

- Express explicit data-quality expectations as SHACL shapes rather than relying on informal documentation.
- Distinguish SHACL’s closed-world validation role from OWL/RDFS meaning and inference.
- Diagnose violations from a human-readable validation report.
- Make validation a repeatable script and CI gate before RDF graph publication.

**Key concepts**

- Node shapes, property shapes, `sh:minCount`, `sh:maxCount`, datatype, class, numeric bounds, severity, and result paths.
- Business rules: every `CustodyTicket` has exactly one `Product`, exactly one `Terminal`, and one positive net volume; ticket date is present; every contract references a customer.
- Conformance versus warning-level diagnostics; invalid data remains a test fixture, not data to publish.
- pySHACL executes SHACL validation over RDFLib graphs and supports a Python-based CI check ([RDFLib pySHACL](https://github.com/rdflib/pyshacl)).

**Hands-on lab**

Write `netback-shapes.ttl` with shapes for `CustodyTicket`, `Contract`, and `PriceObservation`. Validate the 20-ticket graph and require zero violations. Then create an intentionally invalid graph with three cases: a ticket with two products, a ticket with no terminal, and a ticket with `-125` net gallons. Run a `validate_graph.py` script using pySHACL; save the report in Turtle and a concise text summary. Configure the script as a CI command that exits nonzero when the valid publication dataset does not conform.

**Tools used**

pySHACL, RDFLib, Docker Compose, and Apache Jena Fuseki only after the validation gate passes.

**Deliverable/artifact produced**

`netback-shapes.ttl`, valid and invalid RDF fixtures, `validate_graph.py`, a captured violation report, and a CI command documented in the repository.

**Estimated time**

6–8 hours.

## Module 08: Neo4j and the RDF-to-LPG Bridge

**Learning objectives**

- Load curated RDF into an LPG serving graph without redefining it as a separate semantic source of truth.
- Read equivalent relationship patterns in SPARQL and Cypher.
- Identify semantic details that need deliberate handling when RDF is translated to a property graph.
- Explain when Neo4j’s traversal/query experience is useful for the capstone agent.

**Key concepts**

- RDF statements versus LPG nodes, relationships, labels, and properties.
- Neo4j Community Edition as a serving/query layer, with self-hosted neosemantics (n10s) as the RDF interchange bridge ([Neo4j Labs neosemantics](https://neo4j.com/labs/neosemantics/)).
- Mapping/translation considerations: URIs, blank nodes, multi-valued literals, named graphs, OWL/SKOS semantics, and reification/provenance.
- Equivalence is query-level and use-case-specific, not a claim that every RDF semantic construct has a perfect LPG equivalent.

**Hands-on lab**

Start self-hosted Neo4j Community Edition with n10s and import the validated Module 05 RDF snapshot. Retain source URIs as properties. Run the Fuseki query “which terminals sell Regular 87 this week?” and write the equivalent Cypher query that follows `CustodyTicket` to `Terminal` and `Product`. Compare terminal/product identifiers and ticket counts. Add a second Cypher query that traverses customer → contract → ticket → product; then write a short note naming three things that are easier to inspect in the LPG and three semantic/provenance details that must be retained explicitly from RDF.

**Tools used**

Neo4j Community Edition, neosemantics (n10s), Morph-KGC, RDFLib, Apache Jena Fuseki, and Docker Compose.

**Deliverable/artifact produced**

A repeatable Neo4j load command, `sparql_cypher_equivalence.md`, two Cypher query files, graph-load counts, and RDF-to-LPG translation notes.

**Estimated time**

8–10 hours.

## Module 09: The KPI Store and Semantic Layer

**Learning objectives**

- Define Gasoline Netback CPG as a governed KPI rather than an unexplained calculation.
- Declare formula, unit, dimensions, time grain, supporting measures, and evaluation/driver context.
- Design a DuckDB fact table that stores reproducible weekly KPI results and source references.

**Key concepts**

- Raw measure, business measure, derived measure, diagnostic metric, and approved-for-homelab KPI; classification prevents every calculation from being called a KPI.
- Formula convention for the simplified exercise: `Gasoline Netback CPG = realized gasoline revenue per gallon − product cost per gallon − terminal handling cost per gallon − freight cost per gallon − applicable tax/fee cost per gallon`. The exact inputs, units, sign convention, and source snapshot must be versioned.
- Time grain: week ending date. Dimensions: terminal, product grade, customer channel, contract/pricing basis, and geography where the synthetic scenario supports it.
- A KPI Store fact row persists the result, formula version, run ID, source period, and driver decomposition; supporting transactions remain in PostgreSQL.

**Hands-on lab**

Design `fact_gasoline_netback_cpg` in DuckDB with one row per week/terminal/product grade/customer channel/pricing basis. Create 12 weekly rows using synthetic ticket revenue, contract differential, terminal/freight costs, and selected EIA-derived benchmark inputs. Build Dagster assets for `weekly_ticket_volume`, `weekly_realized_revenue`, `weekly_cost_components`, `gasoline_netback_cpg`, and `kpi_driver_variance`. Add a semantic query returning the latest weekly netback plus week-over-week change and the three largest contributors. Store the formula version and source series/reference ID in every KPI run.

**Tools used**

DuckDB, PostgreSQL 18, Dagster (Core/OSS), and Python. Dagster’s asset-based orchestration is the selected pipeline model for the homelab ([Dagster](https://github.com/dagster-io/dagster)).

**Deliverable/artifact produced**

KPI definition card, DuckDB DDL, five Dagster asset definitions, a twelve-week KPI fact table, and a latest-week semantic query with captured results.

**Estimated time**

10–14 hours.

## Module 10: Pipelines, Lineage, and Governance

**Learning objectives**

- Connect ingestion, relational loading, mapping, validation, graph load, and KPI calculation as visible software-defined assets.
- Use lineage to trace an agent-visible KPI result back to EIA-derived and synthetic source data.
- Apply lightweight personal governance: version control, repeatable runs, data contracts, validation gate, and change notes.

**Key concepts**

- Dagster assets and dependencies: raw EIA input → curated price observation → PostgreSQL O2C data → virtual mapping/materialized RDF → SHACL report → Neo4j graph → DuckDB KPI fact.
- OpenLineage events and Marquez visualization as the lineage surface for the pipeline ([OpenLineage](https://openlineage.io/); [Marquez](https://marquezproject.ai/)).
- PROV-O as the ontology-side vocabulary for activities, entities, and agents when a semantic provenance example is useful ([W3C PROV-O](https://www.w3.org/TR/prov-o/)).
- Governance is proportionate: record a decision and re-run an asset rather than simulate enterprise approval workflow.

**Hands-on lab**

Refactor the previous exercises into a single Dagster asset graph: `raw_eia_price`, `synthetic_o2c`, `postgres_o2c`, `ontop_mapping`, `materialized_rdf`, `shacl_validation`, `neo4j_graph`, and `fact_gasoline_netback_cpg`. Emit OpenLineage metadata and open Marquez to confirm a visible path from raw EIA/synthetic data to the KPI table and RDF graph. Deliberately change one ticket’s terminal handling cost, rerun the affected assets, and write a lineage note showing the impacted KPI week, graph load, run ID, and formula version. Mark the SHACL asset as a prerequisite for the Neo4j materialization path.

**Tools used**

Dagster, OpenLineage, Marquez, pySHACL, PostgreSQL 18, DuckDB, Ontop, Morph-KGC, Apache Jena Fuseki, Neo4j Community Edition, and PROV-O.

**Deliverable/artifact produced**

`assets.py` or equivalent asset package, a Marquez lineage screenshot/export, an asset/dependency diagram, a data-contract note, and one documented impact-analysis run.

**Estimated time**

8–12 hours.

### Unstructured-data generation and graph-ingestion extension

**Learning objectives**

- Generate unstructured artifacts that share synthetic entity IDs with ERPNext and PostgreSQL records rather than creating disconnected sample text.
- Fuse SOPs, PDFs, emails, and team-channel messages with relational O2C data while retaining source-aware provenance.

**Hands-on lab**

Author one SOP per Level 2 taxonomy box, grounded in the corresponding process definition and tagged with its shared `process_id`. Render invoice and receipt PDFs directly from ERPNext Sales Invoice and Payment Entry records so the `invoice_id`/`payment_id` and amounts match exactly. Generate entity-linked email threads for credit holds, disputes, collections, remittance advice, and close activities; every thread must include the applicable `customer_id`, `order_id`, `invoice_id`, `dispute_id`, or `collection_case_id`. Stand up [block/buzz](https://github.com/block/buzz) for team-channel simulation, seed messages that reference the same IDs, and export its event log as structured JSON. Use [semantica-agi/semantica](https://github.com/semantica-agi/semantica) ingestion connectors to bring the SOPs, PDFs, emails, and Buzz messages together with ERPNext/PostgreSQL relational data into the knowledge graph, applying entity-aware chunking, ontology/SHACL governance, and PROV-O source provenance.

**Deliverable/artifact produced**

64 process-tagged SOPs, ERPNext-derived invoice/receipt PDFs, entity-linked email and Buzz-message fixtures, a Buzz export, semantica ingestion configuration, and an evidence query proving structured and unstructured artifacts join on the same entity IDs.

**Estimated time**

8–12 hours.

## Module 11: AI Agents and Knowledge Graphs — Capstone

**Learning objectives**

- Build a constrained agent workflow that retrieves KPI facts and graph evidence instead of inventing an answer.
- Separate planning, tool execution, evidence assembly, response generation, and response validation in a LangGraph flow.
- Use a local Ollama-served model with Neo4j/KPI tools and a graph-grounded retrieval component.
- Expose a narrow, auditable FastAPI endpoint for the capstone question.
- Explain the neural-symbolic loop: neural language generation interprets and communicates while symbolic data/queries constrain the factual answer.
- Use [Buzz's `buzz-cli`](https://github.com/block/buzz) as an optional agent tool so the capstone can generate and respond to dispute-thread messages, rather than only consuming passively simulated discussion data.
- Formalize the answer path into three explicit resolution tiers with a visible resolution trace, and expose that same tiered path through an agent-agnostic MCP server as well as FastAPI (ADR-HL-018, ADR-HL-020).

**Key concepts**

- LangGraph state, nodes, transitions, tool contracts, retries, and answer-evidence schema ([LangGraph license](https://github.com/langchain-ai/langgraph/blob/main/LICENSE)).
- Ollama as the local model runtime; use a recommended open model such as Qwen3.6-27B, Qwen3.6-35B-A3B, or Mistral Small 3.2 24B where local hardware permits.
- `neo4j-graphrag-python` and/or LlamaIndex Property Graph Index for graph-grounded retrieval, with Cypher for deterministic structural evidence.
- Answer contract: KPI value/unit/period; week-over-week change; named drivers; exact Cypher or SPARQL; KPI formula version; EIA source series/reference ID; and a statement of any missing evidence.
- Tiered resolution model (ADR-HL-020, adapted from AWS Context Ontology Accelerator's Serve stage, [COA docs](https://aws.github.io/context-ontology-accelerator/)): Tier 0 governed metric (DuckDB KPI Store lookup, 0 LLM calls), Tier 1 structured graph query (Cypher/SPARQL), Tier 2 agentic fallback (LangGraph + Ollama synthesis). Every answer names which tier resolved it.
- The official `modelcontextprotocol/python-sdk` for building an MCP server that exposes the same KPI Store/Cypher/SPARQL tool surface to any MCP-compatible client, not only this homelab's own LangGraph agent (ADR-HL-018; [python-sdk](https://github.com/modelcontextprotocol/python-sdk); [MCP reference servers](https://github.com/modelcontextprotocol/servers)).

**Hands-on lab**

Implement a LangGraph workflow for the prompt: “What is our gasoline netback this week and why did it change?” The workflow must: (1) normalize period and scope, (2) attempt Tier 0 — query DuckDB for a pre-computed weekly KPI Store result, (3) if not resolved, attempt Tier 1 — query Neo4j/Fuseki for ticket/terminal/product/contract context, (4) if not resolved, fall through to Tier 2 — retrieve graph-grounded context using `neo4j-graphrag-python` or LlamaIndex Property Graph Index and synthesize with Ollama, (5) assemble only tool outputs plus the resolution trace (tier used, source table/query, Dagster run id), and (6) reject/flag a response without a KPI row or source reference. Expose `POST /netback/explain` in FastAPI. Build a minimal MCP server with the official `modelcontextprotocol/python-sdk` exposing equivalent `get_kpi`, `run_cypher`, and `run_sparql` tools bound to `127.0.0.1`. Run three acceptance prompts against both FastAPI and the MCP server: a normal question, a product-specific question, and an unsupported-period question that must return a transparent limitation rather than a fabricated value.

**Tools used**

LangGraph, Ollama, Neo4j Community Edition, neo4j-graphrag-python and/or LlamaIndex Property Graph Index, DuckDB, FastAPI, `modelcontextprotocol/python-sdk`, and Python. FastAPI and the MCP server are the homelab’s two serving surfaces over the same tiered resolution logic, while Neo4j remains a serving/query layer rather than a new source of truth.

**Deliverable/artifact produced**

A LangGraph workflow, tool schemas, a FastAPI endpoint, a minimal MCP server exposing the same tools, three request/response evidence bundles (each showing its resolution trace) captured against both serving surfaces, an agent evaluation checklist, and a neural-symbolic-loop design note.

**Estimated time**

15–20 hours.

## Capstone acceptance checklist

The curriculum and capstone are complete only when all of the following are demonstrably true:

- [ ] The repository contains the conceptual model, SKOS glossary, OWL/RDFS ontology, R2RML/OBDA mappings, SHACL shapes, and stable URI convention; each has a documented version.
- [ ] A clean run generates and loads at least 20 synthetic custody tickets plus selected dated EIA-derived price observations, with source snapshot metadata preserved.
- [ ] Apache Jena Fuseki answers the three saved materialized-RDF SPARQL queries, including the terminal/product query, and their results match the stated snapshot.
- [ ] Ontop answers the corresponding virtual-RDF query over PostgreSQL; adding a valid PostgreSQL ticket changes the Ontop result without changing the unrefreshed Fuseki snapshot.
- [ ] The SHACL CI command passes for the valid graph and fails with readable, expected violations for each of the three invalid-ticket fixtures.
- [ ] The reproducible Neo4j load yields counts consistent with the validated materialized graph, and the saved Cypher terminal/product result matches its SPARQL counterpart for the same snapshot.
- [ ] DuckDB holds a documented, twelve-week `Gasoline Netback CPG` fact history with declared formula version, week grain, dimensions, source/reference ID, and driver decomposition.
- [ ] Marquez shows a lineage path from raw EIA/synthetic inputs through the relevant processing assets to both the KPI Store fact table and the RDF/Neo4j graph path.
- [ ] `POST /netback/explain` returns the weekly KPI value, unit, week-over-week change, drivers, exact SPARQL or Cypher query it ran, formula version, and EIA source series/reference ID; unsupported scope produces an evidence-based limitation message.
- [ ] The Owlready2/HermiT reasoning-gate Dagster asset reports the ontology consistent before the corresponding Turtle release is materialized, and a deliberately introduced inconsistency is caught and blocks materialization (ADR-HL-019).
- [ ] The MCP server answers the same three acceptance prompts as `POST /netback/explain`, each response naming the resolution tier (Tier 0/1/2) that answered it (ADR-HL-018, ADR-HL-020).

## Related homelab documents

- `00-Homelab-Charter-and-Roadmap.md`
- `01-Reference-Architecture.md`
- `02-Tool-Selection-and-ADRs.md`
- `04-Data-Strategy-and-Datasets.md`
- `05-Domain-Model-and-Ontology-Pilot.md`
- `06-Repo-Structure-and-Build-Plan.md`

## See also (enterprise EPM parallel)

For learning-transfer context only, this curriculum loosely parallels the EPM **Knowledge & Learning** workstream and its 130-card Mochi flashcard study deck, while exercising concepts that connect to the EPM KPI Store, Commercial Margin / Gasoline Netback pilot, domain-modeling, and lineage work. It is a personal educational artifact, not a governed EPM artifact, approved curriculum, or formal EPM deliverable.
