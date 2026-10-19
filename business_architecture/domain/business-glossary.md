# Business glossary (EPM-GLOS-001)

The terms this repository uses, with one definition each. Use these names in
issues, proposals and documents. A term says **Approved Baseline** only when
Hamid has recorded that approval. A PR merge alone does not approve it. See
`docs/agents/domain.md` for the entry format.

| Term | Definition | Avoid | Source | Status |
|---|---|---|---|---|
| Reference fact | A publicly available fact about a real organization, site or asset, such as a refinery's capacity or an ownership share, held in the ontology with a cited source and an as-of date. | "data", "master data" | EPM-DEC-001-0005 | Draft |
| Event record | A record of something that happened on a date, such as a sale, a shipment or a process run. The ontology never holds event records; consuming systems do. | "transaction" (when the record is not a financial transaction) | EPM-DEC-001-0005 | Draft |
| Observed measure value | The value a measure took at a time, such as a day's crack spread. The ontology never holds observed values. | "KPI value", "actual" | EPM-DEC-001-0005 | Draft |
| Measure definition | What a named measure is: its population, grain, formula basis and what it is not. The ontology holds measure definitions, not their values. | "KPI" (for the value) | EPM-DEC-001-0005, EPM-DEC-001-0008 | Draft |
| Reference module | An ontology module that holds reference facts about one real company and its assets (for example `ref-mpc`), kept apart from the company-neutral core modules. | "instance module" | EPM-DEC-001-0015 | Draft |
| Qualified-relation node | A node with its own IRI that stands for one relationship between two things and holds that relationship's properties, such as a share, a date or a source. Used instead of RDF 1.2 reifiers. | "reifier", "edge record" | EPM-DEC-001-0020 | Draft |
| Scoped sequence | A qualified-relation node stating that, for each instance of a named scope unit, a stated part of an earlier process happens before a stated part of a later process. Neither process needs to complete. It may hold only under a stated condition. | "precedes" (which means the whole earlier process completes first), "handoff" | EPM-DEC-001-0026 | Draft |
| Scope unit | The kind of business object a scoped sequence repeats for, such as a transaction, a delivery period or a forecast version. A scope unit names a kind of object, never a particular trade or claim. | "scope" (alone), "instance" | EPM-DEC-001-0026 | Draft |
| Evidence basis | How firm the evidence for a relationship is: source-confirmed, or a reference-model assumption that Hamid adopted from industry practice without a verified MPC procedure. | "verified" (for an assumption) | EPM-DEC-001-0026 | Draft |
| LPG projection | Loading the finished ontology into a labelled property graph (Neo4j) by the fixed pipeline in `business_architecture/ontology/lpg-projection/`. Turtle stays the master copy. | "Neo4j migration" | EPM-DEC-001-0020 | Draft |
| Downstream consumer | A system that validates against or uses an EPM release without being an EPM authority. PPC is the first one, planned and not yet active. | "client" | EPM-DEC-001-0001; EPM-FOUND-000 D-18 | Draft |
| Commercial Pricing & Price Realization | The data domain for the price a company offers or contracts, how it is applied and adjusted, and what it realizes. | "Pricing" (alone) | EPM-DEC-001-0009; `data-domain-register.md` | Draft |
| Market Data | The data domain that governs externally sourced market observations and shared market-data products: benchmark identifiers, source provenance, licensing restrictions, timestamps, assessment conventions and approved curve-construction metadata. | "price data" | EPM-DEC-001-0006, EPM-DEC-001-0046 | Draft |
| Commercial Risk | The data domain that governs commercial exposure, risk measures, limits, risk-model methodologies and parameters, and trading-counterparty credit assessment and exposure. | "trading risk" | EPM-DEC-001-0007, EPM-DEC-001-0046 | Draft |
| Accounting consolidation | The relation in which one legal entity's accounts are fully consolidated into another's financial statements, as MPC consolidates MPLX. Mapped to GLEIF Level 2. | "parent company" (without the basis) | EPM-DEC-001-0015, EPM-DEC-001-0023 | Draft |
