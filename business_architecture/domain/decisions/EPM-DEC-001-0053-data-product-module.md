# EPM-DEC-001-0053: The data-product module: definitions from the portfolio, undescribed items parked, process links from the value streams

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Step 7, item 3 of EPM-DEC-001-0017: the data products; Phase A of EPM-DEC-001-0052; Loss Control ownership, an open Step 7 item in the worklog |
| Source | Claude Code session, 2026-10-19 |

## Context

The data product portfolio (`business_architecture/business_process/data_product_portfolio.json`) lists 3 segments, 19 data product lines and 48 data products. Its schema calls it a "sibling layer to the LSC process hierarchy; joined to processes via value stream produce/consume links" (`business_architecture/schema/data_product_portfolio.schema.json`). The 15 data products in the Commercial segment have status `active` and a description. The 33 in the Midstream and Corporate segments have status `defined_only` and no description. The process map has no `produces` or `consumes` fields; the value streams do. Loss Control had no owning process until EPM-DEC-001-0048 added CM 1.1.3.7.13 Reconcile Movement Losses and Gains, which produces it. That process was added after `core` 2.1.0.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **A new module, `data-product`, not part of `core`.** `core` is the process taxonomy; a data product is a sibling layer, as the portfolio's schema says. The `kpi` module set the pattern: its own namespace, vocabulary, shapes, build and tests, depending on `core` for process IRIs.
2. **Definitions, never data.** A data product is a `dp:DataProduct` and a `skos:Concept` in one scheme, with its line as `skos:broader`, and its line's segment above that. Its definition is the portfolio's description, unchanged. A closed shape keeps data values off it (EPM-DEC-001-0005).
3. **Undescribed items are parked, not written.** Each `defined_only` data product or line carries a `skos:editorialNote` saying its definition waits for its data owners. A definition written in their place would be a guess at what the portfolio's authors meant.
4. **DCAT is mapped, not imported.** `dp:DataProduct skos:closeMatch dcat:Dataset` (DCAT Version 3, W3C Recommendation, 22 August 2024), as EPM-DEC-001-0023 says. ODPS is not mapped: no recorded source names its version, and the portfolio does not use its terms.
5. **Process links come from the value streams.** The value streams name, sparsely, the data products their processes produce and consume; those links enter the ontology with the value streams (Phase B). Segment anchors come from the portfolio's `processDomainRef`: Commercial in CM 1, Midstream in MS 1 (IRI `L1-midstream`, EPM-DEC-001-0047), Corporate in Enabling Functions. An anchor is context, not ownership.
6. **Loss Control ownership is settled.** Its owning process is CM 1.1.3.7.13 (EPM-DEC-001-0048). `links.csv` records the link, and the build emits it once a `core` release holds the process (2.2.0, Phase D). The portfolio's other note, that Loss Control's product-line placement is provisional, stays with the process authority.
7. **No new data product for receivables.** The worklog records that no AR credit, receivables or collections portfolio exists and that `dp-commercial-risk` must not be reused. No source defines one, so the Order to Cash processes' empty `produces` stay a gap for Phase B to record.
8. **Competency question 7 becomes partial.** Its graph part, which data products have no owning process, answers now. What each process produces or consumes waits for Phase B and `core` 2.2.0.

## Alternatives considered

- **Data products in `core`.** Not chosen: every data product change would then need a `core` release, and the portfolio is a separate layer.
- **Write definitions for the 33 undescribed data products from their names.** Not chosen: the names alone do not say what each covers.
- **Link each data product to every map node a value-stream process names.** Not chosen: a value-stream process names several map nodes, and the source does not say which of them produces the data.

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/business_process/data_product_portfolio.json`; `business_architecture/schema/data_product_portfolio.schema.json`; `business_architecture/ontology/step4/playbook/ontology-worklog.md` (Step 7 row, known data gaps); EPM-DEC-001-0005, 0017, 0023, 0047, 0048; W3C, Data Catalog Vocabulary (DCAT) Version 3, Recommendation, 22 August 2024, https://www.w3.org/TR/vocab-dcat-3/.

## Consequences

- The module is built and checked by `scripts/check.sh`; it is released only with the decision owner's approval.
- The regression stands at 17 answerable, 7 partial and 20 waiting.
- Phase B adds the produced-by and consumed-by links from the value streams.
