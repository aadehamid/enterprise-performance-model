# MPC Customer Classification

**Status:** Adopted — Hamid, 2026-09-29, as the customer classification for
the Customer data domain · **Domain:** Customer · **Evidence checked:**
2026-09-29

MPC doesn't publish a single customer taxonomy. It sorts customers by sales
channel and relationship, then describes them further by brand status,
contract, product line, segment and geography. The classification below is
built from MPC's 10-K filings and MPC's own public materials. Every class and
figure is cited to the source register (`source-register.md`). Figures are
updated to the latest filing (FY2025 10-K).

## 1. Primary classes — sales channel

| Code | Class | Definition (MPC language) | Source | Disclosed scale (FY2025 10-K) |
|---|---|---|---|---|
| C1 | Brand jobber | "independent entrepreneurs who operate primarily Marathon® branded outlets" | MPC-S01/S05/S09 Item 1; MPC-S11 | 7,882 branded outlets in 40 states, DC and Mexico (7,217 at FY2023; 7,738 at FY2024) |
| C2 | Direct dealer | "long-term supply contracts with direct dealers who operate locations mainly under the ARCO® brand" | MPC-S01/S05/S09 Item 1; MPC-S11 | 1,162 locations, primarily Southern California (1,114 at FY2023; 1,161 at FY2024) |
| C3 | Wholesale marketing customer | "wholesale marketing customers domestically and internationally". The 10-K names "private-brand marketers and large commercial and industrial consumers" among them | MPC-S01 Item 1 (Overview; Competition) | Not disclosed |
| C4 | Independent retailer | Named first in "Our refined products are sold to independent retailers, wholesale customers, our brand jobbers and direct dealers" | MPC-S01/S05/S09 Item 1; MPC-S11 | Not disclosed |
| C5 | Unbranded customer | "MPC markets gasoline and diesel fuel to independent marketers, commercial end-users, unbranded distributors and high-volume retailers" | MPC-S10 (MPC Unbranded Marketing page) | Not disclosed |
| C6 | Spot market buyer | "buyers on the spot market" | MPC-S01/S05/S09 Item 1; MPC-S11 | Not disclosed |
| C7 | Export / international customer | "we sell refined products for export to international customers" | MPC-S01/S05/S09 Item 1; MPC-S11 | 401 mbpd exported in 2025 (gasoline 114, distillates 195, asphalt/NGLs/other 92) |

C5 subclasses (MPC-S10):

- **C5.1** Independent marketer
- **C5.2** Commercial end-user
- **C5.3** Unbranded distributor
- **C5.4** High-volume retailer

Enterprise-level context: MPC reports ~3.6 million bpd of refined products
sold to **5,900+ customers** in 2024 (MPC-S12, search excerpt; read in full
before citing). No single customer was ≥10% of revenue in 2023–2025
(MPC-S01, Notes).

## 2. Secondary facets

| Facet | Values | Source |
|---|---|---|
| Brand status | Branded: Marathon, ARCO, or other flags (Shell, Mobil, Tesoro, other). Unbranded | MPC-S01/S05 Item 2 outlet table; MPC-S10 |
| Contract type | Long-term supply contract; wholesale/rack; spot | Long-term supply: MPC-S01 (direct dealers). Spot: MPC-S01. Wholesale/rack: see §4 |
| Product line | Gasoline and distillates (No. 1/No. 2 fuel oils, jet fuel, kerosene, diesel), renewable diesel, propane, NGLs and petrochemicals, heavy fuel oil, asphalt | MPC-S01 Item 1 (Refined Product Sales); MPC-S11 |
| Segment | Refining & Marketing; Midstream (MPLX); Renewable Diesel | MPC-S01 Item 1 and Note 20 (external revenue by segment) |
| Geography | Refining region (Gulf Coast, Mid-Continent, West Coast); U.S. state, DC or Mexico for outlets | MPC-S01 Items 1–2 |
| Delivery tier | Marketed directly to end-users, including branded retail stations (2,449 mbpd in 2025; 2,429 in 2024; 2,385 in 2023), or trading/supply volumes such as bulk sales to large unbranded resellers and other downstream companies | MPC-S01 Item 1, sales-volume footnote |

Product-specific customer types stated by MPC (useful sub-facets):

- **Asphalt:** asphalt-paving contractors, resellers, government entities
  (states, counties, cities, townships), asphalt roofing shingle manufacturers
  (MPC-S01; MPC-S11)
- **NGLs and petrochemicals:** customers in the chemical, agricultural and
  fuel-blending industries (MPC-S01; MPC-S11)
- **Propane:** ~80% home heating / ~20% industrial and petrochemical (MPC-S01)
- **Heavy fuel oil:** utility and ship-bunkering industries (MPC-S01; MPC-S11)

## 3. Hierarchy view

- **Customer**
  - End-user channel: brand jobber (C1), direct dealer (C2), independent retailer (C4)
  - Reseller/bulk channel: wholesale marketing customer (C3), unbranded customer (C5.1–C5.4)
  - Market/trade channel: spot market buyer (C6), export customer (C7)
  - Midstream shipper: MPC's own R&M segment and third-party shippers using MPLX

The three channel groupings are an EPM synthesis. MPC lists the classes but
doesn't group them this way. MPC's own groupings are its "four distinct
markets" (wholesale including exports, spot, branded, retail distribution)
and the two-way volume split in the delivery-tier facet.

## Worked examples

- Marathon-branded station in Ohio, supplied by a jobber: **C1** · Marathon ·
  branded supply · gasoline and diesel · R&M · Ohio
- ARCO site in Southern California: **C2** · ARCO · long-term supply
  contract · gasoline and diesel · R&M · California

## 4. Evidence notes (for the review, not changes to the classification)

1. **Figures updated to FY2025.** The originating draft used FY2024 counts and
   cited third-party filing mirrors (fintel, stocklight, edgar.tools). The
   citations now point to EDGAR accessions.
2. **C5.1 and C5.4 also appear as competitors.** The 10-K names "independent
   marketers … and high-volume retailers" as competitors (MPC-S01 Item 1,
   Competition). MPC's web page names them as customers. Both can be true, since
   one party can be a competitor and a customer. The ontology should model
   customer as a role so this isn't a contradiction.
3. **Jobber contract type.** The filings describe only direct dealers as being on
   "long-term supply contracts". "Branded supply" for jobbers in the worked
   example is a reasonable reading, but it isn't MPC's wording.
4. **"Rack" isn't MPC filing wording.** Keep "wholesale/rack" as the contract
   value, noted as industry usage.
5. **Lubricants: supported by MPC material. Marine: meaning to confirm.**
   MPC's Consumer Products page (MPC-S13) describes a full Marathon lubricants
   line (motor oils, transmission fluids, hydraulic oils, gear lubes, greases).
   The page is partly dated, since it describes the Cincinnati site as a
   biodiesel plant where the FY2025 10-K calls it an aggregation facility, so
   re-check it before citing any figures. Lubricants don't appear in the
   FY2023–FY2025 10-Ks. "Marine" appears only as MPLX's inland marine logistics
   business and as a ship-bunkering use of heavy fuel oil. Confirm which of the
   two the marine product line means.
6. **Midstream shipper.** MPLX serves "principally … the Refining & Marketing
   segment", and Midstream has external-customer revenue ($5,628M in 2025, Note
   20). The words "third-party shippers" haven't been found in MPC documents yet.
   Confirm from the MPLX 10-K (MPC-S08).
7. **Possible gap: crude oil buyers.** R&M sold $5,817M of crude oil to external
   customers in 2025 (Note 20). Decide whether crude buyers fall under C3, C6,
   or need their own class.
8. **Restatements.** FY2022 direct-to-end-user volume is 2,355 mbpd in the FY2023
   10-K and 2,356 in the FY2024 10-K. Store each figure with its filing vintage.

## 5. How the ontology will carry it (Step 5, party module — proposal)

In line with `../../domain/customer_domain_problem_statement_v0.1.md`
("Customer" is a contextual role; Party → Customer Account → Party Role):

- C1–C7 and C5.1–C5.4 become a SKOS concept scheme, *MPC Customer Channel*,
  with the codes as `skos:notation` and the MPC wording as `skos:definition`,
  cited with `dcterms:source`.
- Each facet in §2 becomes its own concept scheme. The §3 groupings go in a
  separate EPM-owned scheme linked by `skos:broader`.
- Channel classes are assigned to the **customer account / relationship**, not
  fixed on the legal party. That lets one party be both a C3 wholesale customer
  and a C6 spot buyer.
- Branded outlets (7,882) are **sites** operated by jobbers' businesses, not
  customers. MPC doesn't disclose how many jobbers there are.
