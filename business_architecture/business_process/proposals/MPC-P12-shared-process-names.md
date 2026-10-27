# Proposal MPC-P12: names for the processes that share a name in the process map

| Field | Value |
|---|---|
| Status | Accepted (the decision owner, 2026-10-26, EPM-DEC-001-0105). Applied to `downstream_process_map.json` and released in `core` 2.4.0 |
| Date | 2026-10-26 |
| Decision | EPM-DEC-001-0098, item 8: the seven preferred labels shared inside core's process scheme are accepted "until a process-map proposal settles them" |
| Source | `downstream_process_map.json`: each node's name and its parent's name; the `ontology` skill's collision check (`check_taxonomy.py`), run on `core` 2.3.0 |

## The gap

The process map gives 25 processes one of seven names that another process also has. Core takes its preferred labels from the map, so `core` 2.3.0 holds seven preferred labels that more than one process in the `mod:core` scheme shares. Each process has its own IRI and its own parent, so the shared name is ambiguous only in a search by label, or wherever a process is shown without its parent. The `ontology` skill's collision check fails on each of the seven.

The names repeat in three patterns:

- **The same four steps under five analyses.** Each of the five L4 analyses under CM 1.3.1 has the steps Source & Collect Information, Define Analysis Objectives & Scope, Analyze Data and Document Findings.
- **The same step under two parents.** Determine Taxability is a step of invoicing (CM 1.3.8.1) and of accounting and regulatory reporting (CM 1.3.8.4). Obtain latest XPIMS MOP model is a step of crude oil evaluations (CM 1.1.2.6) and of product evaluations (CM 1.1.2.7).
- **A process and its own child.** CM 1.2.3 Actualizations has one child, CM 1.2.3.1, also named Actualizations.

## The proposal

Qualify each name with its parent's subject, in the map's own words. Each process keeps its ID, its parent and its description. Only the `name` field changes.

| Process | Name now | Proposed name | Parent |
|---|---|---|---|
| CM 1.3.1.1.1 | Source & Collect Information | Source & Collect Information for Market Analysis | CM 1.3.1.1 Market Analysis |
| CM 1.3.1.1.2 | Define Analysis Objectives & Scope | Define Analysis Objectives & Scope for Market Analysis | CM 1.3.1.1 Market Analysis |
| CM 1.3.1.1.3 | Analyze Data | Analyze Market Data | CM 1.3.1.1 Market Analysis |
| CM 1.3.1.1.4 | Document Findings | Document Findings of Market Analysis | CM 1.3.1.1 Market Analysis |
| CM 1.3.1.2.1 | Source & Collect Information | Source & Collect Information for Company Analysis | CM 1.3.1.2 Company Analysis |
| CM 1.3.1.2.2 | Define Analysis Objectives & Scope | Define Analysis Objectives & Scope for Company Analysis | CM 1.3.1.2 Company Analysis |
| CM 1.3.1.2.3 | Analyze Data | Analyze Company Data | CM 1.3.1.2 Company Analysis |
| CM 1.3.1.2.4 | Document Findings | Document Findings of Company Analysis | CM 1.3.1.2 Company Analysis |
| CM 1.3.1.3.1 | Source & Collect Information | Source & Collect Information for Consumer Analysis | CM 1.3.1.3 Consumer Analysis |
| CM 1.3.1.3.2 | Define Analysis Objectives & Scope | Define Analysis Objectives & Scope for Consumer Analysis | CM 1.3.1.3 Consumer Analysis |
| CM 1.3.1.3.3 | Analyze Data | Analyze Consumer Data | CM 1.3.1.3 Consumer Analysis |
| CM 1.3.1.3.4 | Document Findings | Document Findings of Consumer Analysis | CM 1.3.1.3 Consumer Analysis |
| CM 1.3.1.4.1 | Source & Collect Information | Source & Collect Information for Customer And Marketer Analysis | CM 1.3.1.4 Customer And Marketer Analysis |
| CM 1.3.1.4.2 | Define Analysis Objectives & Scope | Define Analysis Objectives & Scope for Customer And Marketer Analysis | CM 1.3.1.4 Customer And Marketer Analysis |
| CM 1.3.1.4.3 | Analyze Data | Analyze Customer and Marketer Data | CM 1.3.1.4 Customer And Marketer Analysis |
| CM 1.3.1.4.4 | Document Findings | Document Findings of Customer And Marketer Analysis | CM 1.3.1.4 Customer And Marketer Analysis |
| CM 1.3.1.5.1 | Source & Collect Information | Source & Collect Information for Competitor Analysis | CM 1.3.1.5 Competitor Analysis |
| CM 1.3.1.5.2 | Define Analysis Objectives & Scope | Define Analysis Objectives & Scope for Competitor Analysis | CM 1.3.1.5 Competitor Analysis |
| CM 1.3.1.5.3 | Analyze Data | Analyze Competitor Data | CM 1.3.1.5 Competitor Analysis |
| CM 1.3.1.5.4 | Document Findings | Document Findings of Competitor Analysis | CM 1.3.1.5 Competitor Analysis |
| CM 1.3.8.1.3 | Determine Taxability | Determine Invoice Taxability | CM 1.3.8.1 Manage Customer Invoicing and Billing |
| CM 1.3.8.4.5 | Determine Taxability | Determine Taxability for Reporting | CM 1.3.8.4 Manage Accounting, Regulatory Reporting and Compliance |
| CM 1.1.2.6.1 | Obtain latest XPIMS MOP model | Obtain latest XPIMS MOP model for Crude Oil Evaluation | CM 1.1.2.6 Perform Crude Oil Evaluations |
| CM 1.1.2.7.1 | Obtain latest XPIMS MOP model | Obtain latest XPIMS MOP model for Product Evaluation | CM 1.1.2.7 Perform Product Evaluations - COP / ACOP |
| CM 1.2.3.1 | Actualizations | Perform Actualizations | CM 1.2.3 Actualizations |

The analysis steps name the parent analysis as the map names it, so "Customer And Marketer Analysis" keeps the map's capital A. "Analyze ... Data" names the subject only, as the preview the decision owner accepted did. The two XPIMS steps name the evaluation each one supports, from their descriptions ("in support of COE", "in support of COP"). CM 1.2.3 keeps its name, because its description says what actualizations are, and its child takes the verb.

## How the ontology takes it

The process map changes only through an accepted proposal (AGENTS.md). The decision owner accepted this one on 2026-10-26 (EPM-DEC-001-0105). The renames change no IRI and move no node, so `core` takes them in a minor release, 2.4.0. Each renamed concept takes the new name as its `skos:prefLabel` and keeps the old name as `core:priorPreferredLabel`, the annotation core uses for former names. The old name is not an alternative label (`skos:altLabel`): it would still be shared, so a search on it would find several processes (the `ontology` skill's `identity-taxonomy.md`, Step 3, rule 8).
