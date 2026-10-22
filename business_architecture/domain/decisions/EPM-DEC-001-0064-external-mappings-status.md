# EPM-DEC-001-0064: External mappings: DCAT and GLEIF mapped; PIDX and OEO wait for product concepts; IOF Supply Chain parked

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | The external mappings EPM-DEC-001-0023 assigned to Step 7, and its instruction to check PIDX's access terms before the Customer work; Phase E of EPM-DEC-001-0052, the external mappings (EPM-DEC-001-0023) |
| Source | Claude Code session, 2026-10-19 |

## Context

EPM-DEC-001-0023 says to map public ontologies with SKOS mapping properties and not import them: GLEIF at Step 5, PIDX and the Open Energy Ontology (OEO) at Step 7 and on the Customer product-line facet, and IOF Supply Chain at Step 7 if fuels logistics comes in. GLEIF is mapped in `ref-mpc` (EPM-DEC-001-0033). DCAT is mapped in the `data-product` module (EPM-DEC-001-0053). MPC-P01 brought fuels logistics in as MS 1 (EPM-DEC-001-0047). PIDX publishes downstream product codes and terminal codes (pidx.org/standards, retrieved 2026-10-19). OEO covers energy carriers and fuels. The ontology now holds processes, roles, measures, data products, value streams, systems, lanes and benchmark series, but no product class: a benchmark is a price at a market, not a product. *2026-10-21:* see item 2's note: `party:Product` now exists, without values (EPM-DEC-001-0068).

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **PIDX's access terms are checked.** PIDX says it develops "Royalty free standards licensed to all on an open basis pursuant to the End User License Agreement" and makes its standards "available to all interested parties in the petroleum industry and it’s a trading community free of charge" (pidx.org/about, retrieved 2026-10-19; the agreement is the "Standard End User License Agreement (V110329)", pidx.org/about/policies-and-procedures). The agreement (PIDX-EULA-v110329, linked from https://pidx.org/license/, retrieved 2026-10-20) licenses use of a Standard "without modification for any Permitted Use" (section 2(b)(i)); copying needs attribution to PIDX and its legends (2(b)(ii)); and it grants no licence "to modify any Standard or create derivative works based on the Standard" outside a Standards Development Activity (2(c)(v)), nor to develop competing standards (2(c)(iv)). A mapping that points to PIDX codes by identifier uses the Standard without changing it. It must not copy PIDX code lists into the ontology without the legends, or alter them.
2. **PIDX and OEO wait for product concepts.** Both map products and fuels, and the ontology has no product concept to map yet. *Trigger:* the Customer module's product-line facet (Phase C) or another product dimension. *2026-10-21:* that facet is in the `party` module, which owns the Customer domain's concepts (EPM-DEC-001-0067, What follows, item 13), and its values are not yet defined. The `party` module declares a `party:Product` class, which stands in for a Product domain this repository does not model yet; it has no values, so PIDX and OEO still wait for product values (EPM-DEC-001-0068). The mapping then uses `skos:closeMatch` or `skos:exactMatch` to PIDX downstream product codes and OEO's fuel classes, cited with their versions.
3. **IOF Supply Chain is parked.** MS 1 and the logistics processes are business-process concepts; IOF's supply-chain classes are BFO-based types, logistics process types among them along with facilities, shipments and roles (IOF Supply Chain Ontology, version IRI https://spec.industrialontologies.org/ontology/202603/supplychain/SupplyChain/, maturity Released, retrieved 2026-10-20). A SKOS match between a business process and one of them would claim a meaning match that no source checks. *Trigger:* a concept layer for logistics assets or movements, or a consumer that needs IOF terms.
4. **The other EPM-DEC-001-0023 mappings are done:** GLEIF at Step 5, by identifier with an `rdfs:seeAlso` link to each GLEIF record (EPM-DEC-001-0033), and DCAT in the `data-product` module (EPM-DEC-001-0053).

## Alternatives considered

- **Map MPC's benchmark products (CBOB, ULSD, CARBOB) to PIDX codes now.** Not chosen: they are price benchmarks at named markets, not product definitions, and a code match would say more than the source.
- **Import IOF Supply Chain.** Not chosen: EPM-DEC-001-0023 says map, do not import.

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

PIDX, "About Us", https://pidx.org/about/, and "Standards", https://pidx.org/standards/, both retrieved 2026-10-19; PIDX, "Standard End User License Agreement (V110329)", https://pidx.org/license/, retrieved 2026-10-20; Industrial Ontologies Foundry, Supply Chain Ontology, `SupplyChain.rdf` in https://github.com/iofoundry/ontology/tree/master/supplychain (version IRI 202603, maturity Released; retrieved 2026-10-20); EPM-DEC-001-0023, 0033, 0047, 0053.

## Consequences

- The Customer module's product-line facet (Phase C), or another product dimension, brings the PIDX and OEO mappings. *2026-10-21:* that facet is in the `party` module (EPM-DEC-001-0067, What follows, item 13).
- IOF Supply Chain waits for a concept layer for logistics assets or movements, or a consumer that needs IOF terms.
- *2026-10-22 (Phase E):* both triggers re-checked on every released package under `releases/`, and neither is met. `party:Product` has no values in party 1.0.0. Three customer-system attributes describe products (RightAngle's commodities and product, Salesforce's product description), and RightAngle holds a "PIDX Supplier ID", which identifies a supplier, not a product, so it brings no PIDX product mapping. Logistics appears only as process, capability, value-stream and data-product concepts, with no asset or movement layer, and no consumer has asked for IOF terms. A product code list, for example from MPC's FY2025 Form 10-K, would meet the PIDX and OEO trigger; it would change a released module, so it needs a minor release and the decision owner's approval.
