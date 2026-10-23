# EPM-DEC-001-0092: Release `party` 1.1.0: products from MPC's FY2025 Form 10-K, mapped to OEO, with PIDX families; onboarding linked to CM 1.3.7.1.7; eight projection fixes

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-23, for the release and for PIDX family codes; the package's contents delegated under EPM-DEC-001-0028) |
| Date | 2026-10-23 |
| Questions | The fourth close-out release (EPM-DEC-001-0088): the product values that the PIDX and OEO mappings wait for (EPM-DEC-001-0064); MPC-P10.1's link from the onboarding stage (EPM-DEC-001-0087); party's eight projection gaps (EPM-DEC-001-0036) |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md` |

## Context

`party:Product` had no values, so PIDX and OEO waited (EPM-DEC-001-0064). The decision owner chose product values from MPC's FY2025 Form 10-K in `party`, mapped to PIDX and OEO (EPM-DEC-001-0088). Research against the primary sources on 2026-10-23 found:

- **OEO.** The current release is v2.14.0, released 2026-10-08 (version IRI `https://openenergyplatform.org/ontology/oeo/releases/2.14.0/oeo.owl`). It has classes for motor gasoline, gas diesel oil, jet fuel, kerosene, heating oil, liquefied petroleum gas, hydrocarbon, petroleum coke, mineral oil product, diesel fuel and liquid biofuel, and none for distillates, NGLs, fuel oil, asphalt or renewable diesel (OEO issue 1958, still open, asks for fuel oil classes).
- **PIDX.** The downstream product codes are free to download (document 04-101-15-45-2010, file `PIDX_ProductCodes_10_20_2026.xlsx`, from pidx.org/standards). PIDX publishes no IRIs, and each code names one traded grade that a company requested. Codes are grouped in one-letter families, but the Families sheet is dated 2015-09-29, and PIDX's notice of 2024-07-31 changed family S. The licence (EULA V110329) allows using a Standard unmodified and copying it with attribution and PIDX's notices (section 2(b)(ii)), and grants no licence to modify it or create derivative works outside a Standards Development Activity (section 2(c)(v)).

Claude put PIDX to the decision owner again, because no SKOS mapping to PIDX is possible.

## Decision

**The decision owner's decisions:** the release, "Approve all six (Recommended)" (EPM-DEC-001-0088); and for PIDX, "Family codes, flagged (Recommended)": each product records its PIDX family letter as a plain identifier, with the workbook as its source, PIDX's notice and a note that the family list dates from 2015; no IRIs; the business confirms the letters with PIDX.

**What follows (Claude, under EPM-DEC-001-0028):**

1. **A minor release, 1.1.0, issued 2026-10-23.** It adds values, a property, links, ranges and shapes, and removes no IRI.
2. **Products.** The scheme `party:product` holds 27 values, each also a `party:Product`. The top concepts are the 10-K's six refinery product groups (gasoline, distillates, propane, NGLs and petrochemicals, heavy fuel oil, asphalt) and renewable diesel, from the Renewable Diesel segment. Under them sit the 20 products the 10-K names: reformulated and blend-grade gasoline; ULSD, jet fuel, kerosene, and No. 1 and No. 2 fuel oils; propylene, xylene, butane, benzene, toluene, cumene, and fuel-grade and anode-grade coke, which the 10-K names in its NGLs and petrochemicals paragraph; and five asphalt products. Each cites the 10-K. The definitions are Claude's words, and an editorial note says so.
3. **OEO mappings,** in `party/product-mappings.csv`, each with its reason: 3 `skos:closeMatch` (gasoline to motor gasoline, jet fuel to jet fuel, No. 2 fuel oil to heating oil) and 16 `skos:broadMatch` (the two gasoline grades, ULSD, kerosene, propane, butane, the five petrochemicals, both cokes, heavy fuel oil, and renewable diesel to both diesel fuel and liquid biofuel). There is no `skos:exactMatch`: the 10-K names products and does not define them, so no two definitions can be shown to say the same thing. Nine products have no OEO class to map to.
4. **PIDX families,** in `party/pidx-families.csv`, through a new datatype property `party:pidxProductFamily` (range `xsd:string`, at most two per product, one capital letter): ULSD V and S, jet fuel K and J, kerosene H, No. 1 fuel oil E and L, No. 2 fuel oil M, butane N, asphalt Y. Only the letters are recorded, not PIDX's family names or code lists. The property's scope note gives the source, the 2015 caveat and PIDX's notice, as the licence requires.
5. **Onboarding.** The onboarding stage links to CM 1.3.7.1.7 Coordinate Customer Onboarding (MPC-P10.1). The build and its decided-links shape name five processes for the stage.
6. **The eight projection fixes:** ranges for `party:evidenceInput` (`xsd:string`), `party:customerRole` and `party:carries` (`rdf:langString`), and shapes stating the cardinality of `party:plays`, `party:governedBy`, `party:implements` and `party:feeds` (each optional) and `party:mpcClassification` (exactly one, C1 to C8, on each class that has one).
7. **`party:Product`'s definition** drops "the module gives products no properties or values", which 1.1.0 makes untrue; a scope note says where its values come from.
8. **It requires core 2.3.0,** the current release, for CM 1.3.7.1.7. The `party` build reads 2.3.0. 1.0.0 stays on disk as released.
9. **The projection** loads party 1.1.0 with a fixed prefix `oeo` for the mapping targets. The eight gaps leave its list, so 6 remain, in kpi and integration. The rerun gave 34,054 triples, 3,971 nodes and 19,840 relationships, no SHACL violation in the graph over 602 in-graph constraints (the mutant still caught), an empty round-trip diff and equal hashes for the sorted and shuffled loads.

## Alternatives considered

- **A SKOS mapping to PIDX codes.** Not possible: PIDX publishes no IRIs, and a code names one company's grade, not a product.
- **No PIDX now.** Not chosen by the decision owner.
- **`skos:exactMatch` for gasoline or jet fuel.** Not chosen: it would claim the 10-K's term and OEO's definition say the same thing, and the 10-K gives no definition.
- **`dcterms:source` for each product's citation.** Tried first; the integration vocabulary's shapes read a `dcterms:source` object as a bibliographic record, so the citation is a `dcterms:bibliographicCitation`, as elsewhere in the module.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`: "10-K slate in party (Recommended)", "Approve all six (Recommended)", "Approve 8 and 5 (Recommended)" and "Family codes, flagged (Recommended)".

## Evidence

- MPC FY2025 Form 10-K, Item 1 (`business_architecture/reference/mpc/mpc-fy2025-10k-fact-sheet.md`, section 4; the NGLs and petrochemicals paragraph, read at https://www.marathonpetroleum.com/content/documents/Investors/Annual_Report/2025_MPC_Annual_Report_and_10K.pdf on 2026-10-23).
- Open Energy Ontology v2.14.0, release asset `oeo-full.owl` (https://github.com/OpenEnergyPlatform/ontology/releases/tag/v2.14.0, released 2026-10-08, read 2026-10-23); OEO issue 1958.
- PIDX Downstream Product Codes, 04-101-15-45-2010 (https://pidx.org/standards/, read 2026-10-23); PIDX notice "Expansion of Product Codes for Ultra Low Sulfur Diesel #2", 2024-07-31 (https://pidx.org/important-downstream-update/); PIDX EULA V110329.
- EPM-DEC-001-0036, 0064, 0068, 0070, 0074, 0087, 0088.

## Consequences

- `releases/party/1.1.0/` is written; `scripts/check.sh` fails unless it equals a fresh build.
- The business close-out package's point 5 now asks the business to confirm the product list and the PIDX letters (with PIDX).
- EPM-DEC-001-0064 records that the PIDX and OEO trigger is met.
- Tag `party-v1.1.0` after the merge.
