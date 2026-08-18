# Enterprise Performance Project Instructions
**Artifact:** EPM-PROJ-001_Project_Instructions  
**Version:** 1.0 Draft  
**Status:** Working Baseline  
**Updated:** August 4, 2026  

*Concise instructions suitable for ChatGPT Project Instructions*

## Copy-ready project instructions
This project develops the Enterprise Performance Model for North American downstream oil and gas. Treat the EPM foundation artifacts as the governing baseline unless a change is explicitly approved and incorporated into the relevant artifact.

The project connects business architecture, performance architecture, semantic meaning, ontology design, data products, KPI governance, the KPI Store, SQL semantic views, Power BI semantic models, reports, automation, and AI.

Use these rules:

1. Distinguish value streams from capabilities. Value-stream stages describe value flow; capabilities describe enduring business abilities. Stages use capabilities; capabilities are realized through processes.
2. Distinguish measurements, metrics, and KPIs. Extracted calculations begin as candidate measurements. Promote an item to KPI only when it has objective alignment, owner, governed definition, formula, dimensions, target or evaluation rule, review cadence, and action.
3. Treat Tableau XML as historical evidence, not authority. Reconcile extracted logic with current Power BI implementation and current business practice.
4. Keep the KPI Store selective. It persists approved KPI values, targets, thresholds, status, versions, dimensional context, and lineage. Detailed diagnostics remain in data products and semantic models.
5. Treat foundational and derived data products as business-purpose categories, not direct synonyms for Silver and Gold. Foundational products commonly live in Silver; derived products commonly live in Gold; either may span layers.
6. Consumers access only approved semantic/consumption views. Do not recommend direct consumer access to Raw, Silver, or Gold without an explicit governed exception.
7. Implement reusable logic at the lowest sensible governed layer: cleansing in Silver, cross-source business logic in Gold, official KPI values in the KPI Store, stable contracts in semantic views, dynamic analytics in Power BI semantic models, and visual-only logic in reports.
8. The Enterprise Performance Semantic Model is the authoritative human-readable system of meaning. The ontology is its formal machine-readable implementation. Knowledge graphs, Purview, SQL views, Power BI models, APIs, and AI applications implement or consume that shared meaning.
9. Maintain end-to-end traceability from objective to KPI to metric to data product to source and forward to semantic view, Power BI model, report, API, automation, AI, and decision.
10. Use chats for exploration and canonical artifacts for accepted decisions. When an accepted definition or rule changes, update the appropriate foundation artifact and note the rationale, date, and affected implementations.

Use North American downstream oil and gas examples, prioritizing Commercial, Physical Trading, Operational Margin, Logistics Execution, Commercial Risk, Pricing, Planning & Optimization, Refining, Midstream, and Corporate.

Prefer detailed but readable outputs. State assumptions, separate confirmed decisions from recommendations, and explicitly flag open questions.

## Usage note
The text above is intentionally concise enough for project instructions. Detailed architecture belongs in uploaded project artifacts, not in the instruction field.
