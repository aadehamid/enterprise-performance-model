# Business close-out package

This package lists the points about the ontology that only the business can settle. `OPEN-ITEMS.md` lists everything open on the ontology, these points among them. The decision owner asked for this package on 2026-10-23, so that it goes with the ontology and lists what to close out with the business (EPM-DEC-001-0086). Each point is settled when the ontology is first shared with business consumers, unless a row says otherwise. The work that does not wait on the business is in EPM-DEC-001-0088: six approved releases, which carry MPC-P10 and the product values and close the 16 projection gaps. Until they merge, the README's Status section says which have landed. *2026-10-23:* all six are released and tagged (EPM-DEC-001-0089 to 0094), and the ontology is closed (EPM-DEC-001-0096); the points below stay open with the business. *2026-10-26:* the ontology is done (EPM-DEC-001-0107). Points 1 and 2 stay open by the decision owner's choice, and the decision owner may work through some of the others first, to narrow them down. *2026-10-28:* the decision owner worked through points 3 to 16 (EPM-DEC-001-0086, amendment of 2026-10-28). Points 3 and 4 are closed, point 5 is narrowed to the PIDX family letters, and points 17 and 18 are added from EPM-DEC-001-0108. The answers to points 7, 8, 9, 11 and 15 change the ontology, so each row says so until its release merges. Points 7, 8 and 9 are released in `organization` 2.2.0, and points 7 and 8 are closed. Points 11 and 15 are released in `party` 2.1.0, and both stay open for what is left (EPM-DEC-001-0099, amendment of 2026-10-28).

Each row gives the point, what the ontology holds today, what the business needs to say, and the record that holds the answer. Settling a point changes no released IRI unless the row says so. The answer is recorded as an amendment to the named record, in the business's own words, and goes into the next release of the module named.

## Meaning and stewardship

| # | Point | What the ontology holds today | What the business needs to say | Who | Record; module |
|---|---|---|---|---|---|
| 1 | Who owns the meaning of each concept, and who only stewards its data (competency question 17) | Nothing. Q17 is parked (EPM-DEC-001-0086). The register's IT Data Owner, IT Data Steward and IT Data Custodian are RACI parties on processes, and do not answer it (EPM-DEC-001-0045, decision 7). | For each module or concept scheme (processes, roles, measures, data products, value streams, systems, lanes, market data, parties): the role that owns the meaning, the role that stewards the data, and the role that keeps the systems. A concept that differs from its scheme is named. | Business leads per domain, convened by the decision owner | EPM-DEC-001-0045, 0086; a minor release of `organization` adds the governance assignment that 0045, item 7, proposes |
| 2 | Market Data accountability | The Risk Group is accountable for Market Data, provisionally, pending confirmation of its mandate (EPM-DEC-001-0046, MD2) | Confirm the Risk Group's mandate, or name the accountable group | The Risk Group, or whoever sets its mandate | EPM-DEC-001-0046; `market-data` |

## Customer systems

| # | Point | What the ontology holds today | What the business needs to say | Who | Record; module |
|---|---|---|---|---|---|
| 3 | HOLDORDIND, Taboot, MPA_Flag and CR_Incentive_Flag | Named fields with no definition (EPM-DEC-001-0072, amendment of 2026-10-22) | What each code means, in one sentence. *2026-10-28:* closed: the decision owner chose to leave the four codes undefined (EPM-DEC-001-0072, amendment of 2026-10-28); a consumer who needs a meaning reopens it | The owners of the systems that hold them | EPM-DEC-001-0072; `party` |
| 4 | TID Nbr | Read as a terminal identifier that describes a site; no MPC source states it (EPM-DEC-001-0069) | Confirm the reading, or give the meaning. *2026-10-28:* closed: the decision owner kept the reading as it stands (EPM-DEC-001-0072, amendment of 2026-10-28) | The same system owners | EPM-DEC-001-0069, 0072; `party` |
| 5 | The product list and its PIDX families | `party` 1.1.0 holds 27 products named in MPC's FY2025 Form 10-K, with Claude's definitions, mapped to the Open Energy Ontology, and 10 one-letter PIDX product families on 7 of them, taken from a PIDX family list dated 2015 (EPM-DEC-001-0092) | Confirm the products and their definitions, or supply MPC's own product list; confirm the PIDX family letters with PIDX, or give the PIDX codes MPC trades. A finer list would add values and mappings in a minor release; a changed product would retire the old one (deprecated, never deleted) in a major. *2026-10-28:* the products are closed; only the PIDX family letters stay open (EPM-DEC-001-0092, amendment of 2026-10-28) | Commercial product owners, with PIDX for the families | EPM-DEC-001-0064, 0088, 0092; `party` |

## Roles

| # | Point | What the ontology holds today | What the business needs to say | Who | Record; module |
|---|---|---|---|---|---|
| 6 | Forecaster | Kept apart from the Local Refinery Forecaster (EPM-DEC-001-0045, decision 2) | In these backcasting activities, is the Forecaster the Local Refinery Forecaster? If so, the two merge: Forecaster is deprecated and points to its successor, which is a major release of `organization` | The refinery Economics and Planning process owner | EPM-DEC-001-0045; `organization` |
| 7 | Crude RFC | Read as Crude Refinery Feedstock Coordinator, a contextual reading pending confirmation (EPM-DEC-001-0045, decision 5). *2026-10-28:* since `organization` 2.2.0, the decision owner's confirmed reading | Confirm the reading, or give the expansion. *2026-10-28:* closed: the decision owner confirmed the reading, released in `organization` 2.2.0 (EPM-DEC-001-0045, amendment of 2026-10-28) | The process owner named in `organization/roles.csv` | EPM-DEC-001-0045; `organization` |
| 8 | PSM | Left unexpanded. Process Safety Management is the industry expansion, but nothing shows this RACI party means it (EPM-DEC-001-0045, decision 6). *2026-10-28:* since `organization` 2.2.0, expanded as Process Safety Management, with PSM kept as an alternative label | What PSM stands for in these assignments. *2026-10-28:* closed: the decision owner says PSM is Process Safety Management, released in `organization` 2.2.0 (EPM-DEC-001-0045, amendment of 2026-10-28) | The owners of the processes that assign PSM | EPM-DEC-001-0045; `organization` |
| 9 | Four working definitions | Refinery Value Chain Optimization Advisor, Refinery Technical Representative and Crude Refinery Feedstock Coordinator carry EPM working definitions; Business Planning and Analysis carries one adapted from an MPC job posting (EPM-DEC-001-0045, What follows, item 5) | Confirm or replace each definition. *2026-10-28:* the decision owner confirmed Business Planning and Analysis's definition, released in `organization` 2.2.0 (EPM-DEC-001-0045, amendment of 2026-10-28); the other three stay open | The managers of those roles | EPM-DEC-001-0045; `organization` |

## Measures

| # | Point | What the ontology holds today | What the business needs to say | Who | Record; module |
|---|---|---|---|---|---|
| 10 | What each measure includes and excludes | Eight MPC-defined measures carry their population from MPC's own wording; the other 33 are parked, because no source states them (EPM-DEC-001-0062) | For each of the 33, what is in and what is out, in business words | Each measure's owner | EPM-DEC-001-0062; `kpi` |

## Systems (item G, 2026-10-25)

| # | Point | What the ontology holds today | What the business needs to say | Who | Record; module |
|---|---|---|---|---|---|
| 11 | Drop Tank, Gas Buddy, DTN File Server and Federal Health | Four customer systems downstream of MAGIC that send customer data to Profisee, each with only its customer role; no definition (EPM-DEC-001-0099, item 8). *2026-10-28:* since `party` 2.1.0, Drop Tank, GasBuddy and DTN are defined from their vendors' own published words (Drop Tank's from a 2018 press release, its site being gone); Federal Health is not | What each is, and what MPC sends it. *2026-10-28:* narrowed: Drop Tank, GasBuddy and DTN are defined from their vendors' own published words (Drop Tank's from a 2018 press release, its site being gone), at the decision owner's choice, released in `party` 2.1.0 (EPM-DEC-001-0099, amendment of 2026-10-28); Federal Health, and what MPC sends each of the four, stay open | The customer-data owner, asked once for all four | EPM-DEC-001-0099; `party` |
| 12 | TopDay and VALT | MPC-built, by the decision owner's answer; no definition (EPM-DEC-001-0099, item 6) | What each does | Their owners | EPM-DEC-001-0099; `system` |
| 13 | CargoTracker and Allocation Manager | Thin descriptions the decision owner approved: what each feeds or derives, not what it is (EPM-DEC-001-0099, item 10) | A fuller description of each; for Allocation Manager, whether it also allocates product | Their owners | EPM-DEC-001-0099; `system`, `party` |
| 14 | Hyperion and Quorum | Hyperion read as Oracle Hyperion Planning, Claude's guess, which the decision owner accepted; Quorum defined at vendor level, product not named (EPM-DEC-001-0099, item 5 and the identifications of 2026-10-24) | Which Oracle Hyperion product, and which Quorum product | The owners of the backcast's actual-data steps; the customer-data owner | EPM-DEC-001-0099; `system`, `party` |
| 15 | Polaris | A Marathon Pipeline LLC scheduling system named in a PHMSA notice; built or bought unknown (EPM-DEC-001-0099, item 7). *2026-10-28:* since `party` 2.1.0, a note gives the decision owner's belief that it is bought | Whether MPC built or bought it, and what it does. *2026-10-28:* the decision owner believes it is bought, an off-the-shelf product, noted in `party` 2.1.0 (EPM-DEC-001-0099, amendment of 2026-10-28); the vendor and what it does stay open | Marathon Pipeline LLC's scheduling owners | EPM-DEC-001-0099; `party` |
| 16 | The internal systems' descriptions | 14 system-module systems and 20 customer systems carry descriptions Claude drafted from the repository (the processes that use them, or their customer roles and flows) and approved under the delegation (EPM-DEC-001-0103). *2026-10-27:* 22 system-module systems and 28 customer systems, with the eight of that day's customer inputs in each (EPM-DEC-001-0108) | Confirm or correct each description | Each system's owner | EPM-DEC-001-0103; `system`, `party` |

## Dealer Master (added 2026-10-28)

| # | Point | What the ontology holds today | What the business needs to say | Who | Record; module |
|---|---|---|---|---|---|
| 17 | Dealer Master's billing customer number | Dealer Master holds a billing customer number; the decision owner's inputs of 2026-10-27 leave open how it relates to the SAP customer number (EPM-DEC-001-0108) | Whether the billing customer number is the SAP customer number, maps to it, or is separate | Dealer Master's owners | EPM-DEC-001-0108; `party` |
| 18 | Dealer Master's fuel volumes and the Enterprise Data Lake | The inputs mark as not confirmed whether Dealer Master's fuel volumes reach the Enterprise Data Lake (EPM-DEC-001-0108) | Whether they do, and by which flow | Dealer Master's owners, with the Enterprise Data Lake's owners | EPM-DEC-001-0108; `party` |

## Parked for other reasons

These are not for the business. Each waits on a trigger its record names:

- **IOF Supply Chain mapping:** waits for a concept layer for logistics assets or movements, or a consumer that needs IOF terms (EPM-DEC-001-0064).
- **IRIs that resolve:** the w3id namespace is a placeholder, and nothing is registered or hosted (EPM-DEC-001-0039).
- **Held process-map rows:** each gets a fresh verdict only if its source is corrected, through the source-correction backlog (EPM-DEC-001-0025, 0083).
