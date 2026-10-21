# EPM-DEC-001-0069: The customer systems, data flow and attributes

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-21 |
| Questions | Pull request 3 of EPM-DEC-001-0067's plan; it extends competency question 6 ("Which systems ... support process P, and which processes depend on system S?") to the customer's systems through the three systems the system module also holds |
| Source | Claude Code night run, 2026-10-21 |

## Context

EPM-DEC-001-0067 lists the decision owner's seven customer inputs. Inputs 1 to 3 are diagrams of the systems the customer passes through and the flows between them. Input 5 is a table of six core systems, each with the attributes that define the customer there (Create) and the attributes that enrich it (Enrich). Input 6 adds a pane on where the customer shows up in systems. That pane covers six core systems with the model entities each implements, the origin and sync patterns, and other systems in the landscape. The decision owner asked for "both the life cycle and data flow of Customer" and for both categories of attributes to be captured (EPM-DEC-001-0067). None of the inputs is in the repository. This record turns their systems, flows and attributes into the `party` module (EPM-DEC-001-0068).

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**

1. **Customer systems are the module's own class, `party:CustomerSystem`, not new members of the system module.** The system module is built only from the process map's `systems` fields. Its shapes require each system to sit in that module's scheme with the process map as its source (EPM-DEC-001-0055). Claude's plan for this pull request, shown to the decision owner but not in the repository, put them in the system module's register. This record changes that, for that reason. Three systems are in both: RightAngle, KittyHawk and Profisee. Their customer-system node carries `skos:exactMatch` to the system module's node, so the customer data flow joins the processes those systems support. Question 15's same-word test reads that link as one thing in two modules (`q15b`). The system module's `sap` is the process map's generic "SAP". It is not matched to SAP MDG or SAP S/4HANA, because the map does not say which it means.
2. **42 systems, in five tiers:**
   - **core** (6): SAP MDG, SAP S/4HANA, Salesforce, RightAngle, Polaris, Dealer Master;
   - **integration** (1): MAGIC;
   - **enrichment** (5): Tax Image Silo, Sirion, Terminal Upload, XREF and Information Steward;
   - **downstream** (22): the systems that use the customer, including the nine systems below MAGIC that feed Profisee;
   - **landscape:** the eight other sources in input 6's pane (Terminal Audit System, FlowCal, EIS, Asphalt Marketing System, Brand Credit Card System, Terminal Margin Ranking System, Corp_Vetting and Lenel Onguard).
   - Each system has one or two sentences on what it does with the customer, in Claude's words from the inputs.
   - Three names in the inputs are not systems and are left out: MPLX, a company, where input 1 shows the customer activated for Producers; Marketing Users, a user group; and Bloomberg and news, sources of risk information.
   - FuelFacs carries CBS as an alternative label, because input 2 labels FuelFacs "CBS". Whether input 6's "CBS" is the same system is open.
3. **What the six core systems implement** is input 6's mapping, entity for entity:

   | System | Entities |
   |---|---|
   | SAP MDG | Party, External Identifier |
   | SAP S/4HANA | Party, Party Role, Customer Account |
   | Salesforce | Party, Contact Point, Address |
   | RightAngle | Party, Party Role, Contact Point, Agreement |
   | Polaris | Customer Account, Party Transaction Association, Site |
   | Dealer Master | Party Role, Site, Site Brand Assignment, Agreement |

4. **35 data flows**, each a `party:DataFlow` with what it carries and the inputs that show it, plus a direct `party:feeds` link.
   - Where the inputs disagree, this record takes input 3, the only dated diagram, over input 2. Input 6 confirms the core path: the SAP customer number is generated in SAP MDG and backfilled to Salesforce through MAGIC.
   - Input 2's edges that were hard to read and that input 3 does not confirm are left out: S/4HANA to Bridger Insight, RightAngle to TFR, Kittyhawk to RCMS, and FuelFacs to TASDM.
   - Input 1 draws ten boxes below MAGIC that feed Profisee. Nine are systems and feed Profisee here. The tenth, Marketing Users, is a user group and is left out (item 2).
5. **24 customer sourcings** say how a system relates to a kind of customer:
   - **origin** (input 6): prospects start in Salesforce; jobbers in Dealer Master; direct dealers in SAP MDG.
   - **setup** (input 1): the lines of business the customer is created for in RightAngle, Salesforce and Polaris.
   - **source** (input 6's landscape list).
   - Input 6 lists CBS as a source of terminal customers. That sourcing is placed on FuelFacs as a reading, and its note says so, because whether input 6's CBS is FuelFacs is open (item 2).
   - "Customer" in input 6's Corp_Vetting line is not a role in the list, so only vendor and surety are taken.
6. **275 system attributes, 43 Create and 232 Enrich**, from input 5 after the corrections and deduplication the decision owner asked for ("correct them", "dedup them"; EPM-DEC-001-0067).
   - Six labels are corrected: Sales Manager, Address_Line_1, Joint_Tariff_Flag, Broker Reconcile Method, SAP Net Out Profit Cntr, and Inactive_Indicator_Flag, which merges two spellings.
   - Nine repeats are removed.
   - Each attribute names its system, its category and the entity of the conceptual model it describes. The mapping is Claude's reading of each field name:
     - fields naming the company's own staff on the account (account manager, territory manager, collection specialist) describe the customer account. This mapping is Claude's reading; a search of vendor customer-master practice guided it, and none of that practice is cited (EPM-DEC-001-0067);
     - authorization groups describe the line of business, because MDG keeps them by line of business (input 6);
     - fields about a system's own record (who created or changed it, and when) describe a `party:SystemRecord`, which is not an entity of the model.
7. **Nine shared attributes** name one thing several systems carry under different names:
   - the SAP customer number (four systems);
   - the business associate ID (three);
   - the tax ID (five);
   - the legal name, the territory manager, the class of trade, credit, status, and the business partner's role and group.
   - The business associate ID in SAP MDG is the identification number of type ZBAID, which RightAngle assigns (inputs 2, 3 and 5).
8. **The six internal codes the decision owner asked about** ("use external MPC search and Peer to resolve these ones."; EPM-DEC-001-0067):
   - **ZBAID** is resolved from the inputs: the SAP MDG identification number that holds RightAngle's business associate ID (item 7).
   - **TID Nbr** is read as a terminal identifier, next to RightAngle's Site Nbr, so it describes a site. That is a reading; no MPC source states it.
   - **HOLDORDIND, Taboot, MPA_Flag and CR_Incentive_Flag** stay named fields without a definition. Neither MPC's filings nor the inputs define them (EDGAR full-text search of MPC's and MPLX's filings and the inputs, 2026-10-21), and the peer and vendor sources that may explain some of them are not cited in the Customer domain (EPM-DEC-001-0067).
   - **TABS Seller ID** is read as the party's seller identifier in a terminal lifting-control service: the system that authorizes or denies a lifting at the rack against the seller's allocations and the customer's credit, and passes on the bill of lading. It is mapped to an external identifier of the party. Neither MPC's filings nor the inputs name it (EDGAR full-text search, 2026-10-21). The repository already names DTN TABS as one example of a Terminal Automation System, the system that owns the gate, bay, meter and bill of lading in the Order to Cash landscape (`O2C/index.html`, reference R14; its vendor names are illustrative), and the O2C demo's ontology gives the Loading-Authorized Party the label "TABS customer" (`demos/o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free/ontology/o2c-meaning.ttl`). The reading comes from industry and vendor material, which guides it and is not cited (EPM-DEC-001-0067). The decision owner asked for that search and took this recommendation, keeping the vendor material out ("I will take your recommendation", `answers-2026-10-21-tabs.md`). Lifting authorization is what the Loading-Authorized Party role names (item 4 of EPM-DEC-001-0068).
   - **TDS Seller ID**, which the decision owner did not ask about, stays unexplained. It is mapped to an external identifier of the party, as its name says.
9. **Internal names are allowed** by EPM-DEC-001-0040, item 3. The repository is public until the goal is achieved (EPM-DEC-001-0067, decision 12), and private again at the end of the session or the goal (EPM-DEC-001-0067, What follows, item 12).

## Alternatives considered

- **Add the customer systems to the system module's register.** Not chosen: that module is built from the process map, and its shapes say so.
- **Take every edge of input 2, including those hard to read.** Not chosen: an uncertain edge would be stated as fact.
- **Leave unmapped the attributes whose entity is unclear.** Not chosen: every attribute gets an entity, so the model's coverage can be counted. Each mapping is a reading the decision owner can correct in `attributes.csv`.

## The decision owner's recorded words

This record is Claude's, under the delegation: "yes, extend the delegation to steps 5 to 12." (`delegation-steps-5-12.md`). It builds on the decision owner's words recorded in EPM-DEC-001-0067 (`answers-2026-10-21-customer.md`), including "correct them" and "dedup them". On TABS Seller ID (item 8), the decision owner said "sounds good. I will take your recommendation" (`answers-2026-10-21-tabs.md`). The decision owner can reverse any item.

## Evidence

- EPM-DEC-001-0067 and `answers-2026-10-21-customer.md`; EPM-DEC-001-0068.
- `business_architecture/ontology/system/systems.csv` and `shapes.ttl` (EPM-DEC-001-0055).
- EPM-DEC-001-0040.

## Consequences

- `party/systems.csv`, `data-flows.csv`, `customer-sources.csv` and `attributes.csv` are the sources. `build_party.py` builds `systems.ttl` from them, and `scripts/check.sh` fails unless the file equals a fresh build. `test_party_systems.py` pins the figures and the core mappings by hand.
- The regression loads `systems.ttl` with the module.
- Open for the decision owner: whether input 6's CBS is FuelFacs; whether the Terminal Margin Ranking System is the process map's TMR; and the meaning of HOLDORDIND, Taboot, MPA_Flag, CR_Incentive_Flag and TDS Seller ID, whether TABS Seller ID is read rightly, and whether TID Nbr is a terminal identifier.
