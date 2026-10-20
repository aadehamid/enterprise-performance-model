# EPM-DEC-001-0064: External mappings: DCAT and GLEIF mapped; PIDX and OEO wait for product concepts; IOF Supply Chain parked

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | The external mappings EPM-DEC-001-0023 assigned to Step 7, and its instruction to check PIDX's access terms before the Customer work; Phase E of EPM-DEC-001-0052 |
| Source | Claude Code session, 2026-10-19 |

## Context

EPM-DEC-001-0023 says to map public ontologies with SKOS mapping properties and not import them: GLEIF at Step 5, PIDX and the Open Energy Ontology (OEO) at Step 7 and on the Customer product-line facet, and IOF Supply Chain at Step 7 if fuels logistics comes in. GLEIF is mapped in `ref-mpc` (EPM-DEC-001-0033). DCAT is mapped in the `data-product` module (EPM-DEC-001-0053). MPC-P01 brought fuels logistics in as MS 1 (EPM-DEC-001-0047). PIDX publishes downstream product codes and terminal codes (pidx.org/standards, retrieved 2026-10-19). OEO covers energy carriers and fuels. The ontology now holds processes, roles, measures, data products, value streams, systems, lanes and benchmark series, but no product class: a benchmark is a price at a market, not a product.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **PIDX's access terms are checked.** PIDX says it develops "Royalty free standards licensed to all on an open basis pursuant to the End User License Agreement" and makes its standards "available to all interested parties in the petroleum industry and it’s a trading community free of charge" (pidx.org/about, retrieved 2026-10-19; the agreement is the "Standard End User License Agreement (V110329)", pidx.org/about/policies-and-procedures). Nothing in the terms stops the mapping.
2. **PIDX and OEO wait for product concepts.** Both map products and fuels, and the ontology has no product concept to map yet. *Trigger:* the Customer module's product-line facet (Phase C) or another product dimension. The mapping then uses `skos:closeMatch` or `skos:exactMatch` to PIDX downstream product codes and OEO's fuel classes, cited with their versions.
3. **IOF Supply Chain is parked.** MS 1 and the logistics processes are business-process concepts; IOF's classes are BFO-based process types. A SKOS match between them would claim a meaning match that no source checks. *Trigger:* a concept layer for logistics assets or movements, or a consumer that needs IOF terms.
4. **The Step 7 external mappings are otherwise done:** GLEIF (EPM-DEC-001-0033) and DCAT (EPM-DEC-001-0053).

## Alternatives considered

- **Map MPC's benchmark products (CBOB, ULSD, CARBOB) to PIDX codes now.** Not chosen: they are price benchmarks at named markets, not product definitions, and a code match would say more than the source.
- **Import IOF Supply Chain.** Not chosen: EPM-DEC-001-0023 says map, do not import.

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

PIDX, "About Us", https://pidx.org/about/, and "Standards", https://pidx.org/standards/, both retrieved 2026-10-19; EPM-DEC-001-0023, 0033, 0047, 0053.

## Consequences

- The Customer work (Phase C) carries the PIDX and OEO mappings.
