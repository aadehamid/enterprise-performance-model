# Business close-out package

This package lists the points about the ontology that only the business can settle. The decision owner asked for this package on 2026-10-23, so that it goes with the ontology and lists what to close out with the business (EPM-DEC-001-0086). Each point is settled when the ontology is first shared with business consumers, unless a row says otherwise. The work that does not wait on the business is in EPM-DEC-001-0088: six approved releases, which carry MPC-P10 and the product values and close the 16 projection gaps. Until they merge, the README's Status section says which have landed.

Each row gives the point, what the ontology holds today, what the business needs to say, and the record that holds the answer. Settling a point changes no released IRI unless the row says so. The answer is recorded as an amendment to the named record, in the business's own words, and goes into the next release of the module named.

## Meaning and stewardship

| # | Point | What the ontology holds today | What the business needs to say | Who | Record; module |
|---|---|---|---|---|---|
| 1 | Who owns the meaning of each concept, and who only stewards its data (competency question 17) | Nothing. Q17 is parked (EPM-DEC-001-0086). The register's IT Data Owner, IT Data Steward and IT Data Custodian are RACI parties on processes, and do not answer it (EPM-DEC-001-0045, decision 7). | For each module or concept scheme (processes, roles, measures, data products, value streams, systems, lanes, market data, parties): the role that owns the meaning, the role that stewards the data, and the role that keeps the systems. A concept that differs from its scheme is named. | Business leads per domain, convened by the decision owner | EPM-DEC-001-0045, 0086; a minor release of `organization` adds the governance assignment that 0045, item 7, proposes |
| 2 | Market Data accountability | The Risk Group is accountable for Market Data, provisionally, pending confirmation of its mandate (EPM-DEC-001-0046, MD2) | Confirm the Risk Group's mandate, or name the accountable group | The Risk Group, or whoever sets its mandate | EPM-DEC-001-0046; `market-data` |

## Customer systems

| # | Point | What the ontology holds today | What the business needs to say | Who | Record; module |
|---|---|---|---|---|---|
| 3 | HOLDORDIND, Taboot, MPA_Flag and CR_Incentive_Flag | Named fields with no definition (EPM-DEC-001-0072, amendment of 2026-10-22) | What each code means, in one sentence | The owners of the systems that hold them | EPM-DEC-001-0072; `party` |
| 4 | TID Nbr | Read as a terminal identifier that describes a site; no MPC source states it (EPM-DEC-001-0069) | Confirm the reading, or give the meaning | The same system owners | EPM-DEC-001-0069, 0072; `party` |
| 5 | The product list and its PIDX families | `party` 1.1.0 holds 27 products named in MPC's FY2025 Form 10-K, with Claude's definitions, mapped to the Open Energy Ontology, and 10 one-letter PIDX product families on 7 of them, taken from a PIDX family list dated 2015 (EPM-DEC-001-0092) | Confirm the products and their definitions, or supply MPC's own product list; confirm the PIDX family letters with PIDX, or give the PIDX codes MPC trades. A finer list would add values and mappings in a minor release; a changed product would retire the old one (deprecated, never deleted) in a major | Commercial product owners, with PIDX for the families | EPM-DEC-001-0064, 0088, 0092; `party` |

## Roles

| # | Point | What the ontology holds today | What the business needs to say | Who | Record; module |
|---|---|---|---|---|---|
| 6 | Forecaster | Kept apart from the Local Refinery Forecaster (EPM-DEC-001-0045, decision 2) | In these backcasting activities, is the Forecaster the Local Refinery Forecaster? If so, the two merge: Forecaster is deprecated and points to its successor, which is a major release of `organization` | The refinery Economics and Planning process owner | EPM-DEC-001-0045; `organization` |
| 7 | Crude RFC | Read as Crude Refinery Feedstock Coordinator, a contextual reading pending confirmation (EPM-DEC-001-0045, decision 5) | Confirm the reading, or give the expansion | The process owner named in `organization/roles.csv` | EPM-DEC-001-0045; `organization` |
| 8 | PSM | Left unexpanded. Process Safety Management is the industry expansion, but nothing shows this RACI party means it (EPM-DEC-001-0045, decision 6) | What PSM stands for in these assignments | The owners of the processes that assign PSM | EPM-DEC-001-0045; `organization` |
| 9 | Four working definitions | Refinery Value Chain Optimization Advisor, Refinery Technical Representative and Crude Refinery Feedstock Coordinator carry EPM working definitions; Business Planning and Analysis carries one adapted from an MPC job posting (EPM-DEC-001-0045, What follows, item 5) | Confirm or replace each definition | The managers of those roles | EPM-DEC-001-0045; `organization` |

## Measures

| # | Point | What the ontology holds today | What the business needs to say | Who | Record; module |
|---|---|---|---|---|---|
| 10 | What each measure includes and excludes | Eight MPC-defined measures carry their population from MPC's own wording; the other 33 are parked, because no source states them (EPM-DEC-001-0062) | For each of the 33, what is in and what is out, in business words | Each measure's owner | EPM-DEC-001-0062; `kpi` |

## Parked for other reasons

These are not for the business. Each waits on a trigger its record names:

- **IOF Supply Chain mapping:** waits for a concept layer for logistics assets or movements, or a consumer that needs IOF terms (EPM-DEC-001-0064).
- **IRIs that resolve:** the w3id namespace is a placeholder, and nothing is registered or hosted (EPM-DEC-001-0039).
- **Held process-map rows:** each gets a fresh verdict only if its source is corrected, through the source-correction backlog (EPM-DEC-001-0025, 0083).
