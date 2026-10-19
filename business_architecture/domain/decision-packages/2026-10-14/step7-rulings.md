# Step 7 rulings: decision package

*2026-10-18:* answered by Hamid. KPI: his planner measure list (EPM-DEC-001-0040). MD and P: his rulings in `answers-2026-10-18.md`, carried out in later pull requests.

Status: Answered by Hamid on 2026-10-18 (see the note above). Date: 2026-10-14. When prepared, nothing in this package was ruled. Each question ends with options, and the recommendation is listed first.

## What you need to do

1. KPI: send your Pricing KPI categories and the KPI names under each. Only you have this list. Reply "KPI: A" with the list attached.
2. MD1 to MD5: the Market Data and Commercial Risk draft. Recommended answer to each is A. Reply "MD: all A", or name the one you want different.
3. P01, P03 to P09, and the deferred half of P02: the MPC process-map proposals. Recommended answer to each is A. Reply "P: all A", or name the ones you want different.

A short reply such as "KPI: list below. MD: all A. P: all A, except P04: B" is enough.

## 1. KPI: your Pricing KPI categories and named KPIs

### The question

Step 7 starts with your Pricing KPI categories and the named KPI definitions under them (EPM-DEC-001-0017, order item 1). The `kpi` module is seeded from those categories. This is information only you have, so the question is what you send, not which option to pick.

### Background

On 2026-10-05 you wrote, in answer to Q11: "We have Pricing domain KPI category or type such as Crack Spread. I will share them later." (EPM-DEC-001-0005 and EPM-DEC-001-0017, "Hamid's recorded words"). The repo has no copy of that list. A search of the repo and of `business_architecture/ontology/step4/review-evidence/hamid-answers/` found no later message that carries it.

The repo does hold the pricing classification P1 to P11, which you proposed on 2026-09-29 (`business_architecture/reference/mpc/pricing-domain-evidence.md` §1). My reading is that P1 to P11 classifies pricing data, and your KPI categories are a different list. Your Q11 remark came six days after P1 to P11 and still said "I will share them later". I could not confirm this reading from the repo. If your categories are P1 to P11, say so, and that answers the question.

EPM-DEC-001-0008 already puts margin indicators and margin capture (P2) in the `kpi` module as measure definitions. The ontology holds the definitions and never the values (EPM-DEC-001-0005).

### What to send

The minimum that lets Step 7 start:

1. The category names, for example the category that holds Crack Spread.
2. The named KPIs in each category, by the name your teams use.

Send these too if you have them. If you do not, the agent drafts them from MPC and peer filings and you correct the draft. EPM-DEC-001-0017 says each definition cites the filing that uses the measure.

3. For each named KPI, one line on what it measures.
4. What it is not, for example the 3-2-1 crack spread is not realized refinery margin (competency question 32).
5. Aliases your teams use, such as "the crack" (competency question 36).
6. The grain, for example daily by region, or a monthly roll-up (competency questions 29 and 30).
7. The process or decision each KPI informs (competency question 33).

The MPC evidence already in the repo covers several candidates: R&M margin per barrel, refining operating cost per barrel, distribution cost per barrel, planned turnaround cost per barrel, the three regional 3-2-1 crack spreads and the blended crack (`business_architecture/reference/mpc/mpc-fy2025-10k-fact-sheet.md` §8), and margin capture against the R&M Margin Indicator (`pricing-domain-evidence.md` E16, E17). Two of them need care. The R&M margin definition changed between the FY2025 10-K and the Q2 2026 10-Q (`pricing-domain-evidence.md` §3 note 1). The capacity basis behind utilization is not confirmed (`data-domain-register.md`, open items).

### Options

| Option | What it means | What happens next |
|---|---|---|
| A (Recommended) | You send the list (items 1 and 2 at least). | The agent drafts one measure definition per named KPI, cites the MPC or peer filing for each, and opens a PR for your review. Your list becomes the `kpi` module's category scheme, as EPM-DEC-001-0017 says. |
| B | You ask the agent to draft a starter list from the MPC measures above, for you to edit. | This departs from EPM-DEC-001-0017, which seeds the module from your categories, so it needs a new decision record first. The risk is that the draft categories differ from the ones your teams use. |
| C | Wait. | Step 7 order item 1 stays blocked, and so does P09, which attaches measures to value-stream stages. |

A is recommended because EPM-DEC-001-0017 already chose your categories as the seed, and you said the list exists.

### Competency questions this unblocks

The list lets Step 7 build the `kpi` module. In `business_architecture/ontology/regression/expected.csv` these rows wait for it: 13 and 14 (KPI seed), 27 to 36 (Named KPI), 37 and 38 (placement of Named KPIs), the Named KPI part of 39, and 41 and 42 (what an agent may answer or must refuse). Each moves to answerable only when its query is written and passes, not when the list arrives.

## 2. MD: the Market Data and Commercial Risk draft

### The question

`business_architecture/domain/market-data-and-commercial-risk-draft.md` (merged in PR #268, commit cd3ba23) proposes full definitions for the two domains. EPM-DEC-001-0010 left those definitions to Step 7. The draft asks you for five answers. Its own list is at "What Hamid decides", lines 36 to 40.

### Background

EPM-DEC-001-0006 makes Market Data its own domain, owning benchmarks (P1) and benchmark methodology (P11). EPM-DEC-001-0007 gives Commercial Risk price risk and hedging (P10). The register keeps both rows with "Owner to be confirmed" (`data-domain-register.md` lines 37 and 38). The glossary holds one Draft row for each domain (`business-glossary.md` lines 22 and 23).

### Evidence

- Market data comes from licensed vendors (Platts, Argus, OPIS, NYMEX, CBOT) and serves valuation, margin benchmarks, RIN pricing and investor reporting, as well as pricing. Source: `business_architecture/reference/downstream-peers/pricing-market-data-risk-evidence.md`, Finding 1 (DP-01, DP-03, DP-05, DP-06, DP-07).
- Phillips 66 and Valero govern price risk with board-approved limits, and a separate risk group monitors it daily. Source: the same file, Finding 2 (DP-01, DP-02 Item 7A).
- The process map puts CM 1.2.2.3.3 Setup And Manage Curves under CM 1.2.2.3 Market Risk Management, in the middle office. Neither CM 1.2.2 nor its children carry a RACI (`business_architecture/business_process/downstream_process_map.json`).
- The existing data product `dp-commercial-risk` already covers "counterparty credit in the trading context. Distinct from Order-to-Cash customer AR credit." (`business_architecture/business_process/data_product_portfolio.json`, the `dp-commercial-risk` entry). The Order-to-Cash value stream says not to reuse it for AR credit (`value_stream_order_to_cash.json` line 799).
- The role register has a "Risk Group" team (`business_architecture/ontology/organization/roles.csv` line 51). It has no market data role.
- The proposed federated ownership in `pricing-domain-evidence.md` §8 gives benchmarks, differentials and curves to "trading/supply/economics". That proposal predates EPM-DEC-001-0006 and points to a different Market Data owner than the draft does.

The peer file states its own limit. Filings describe governance and data sources, not data-domain boundaries, so the split is an inference from consistent practice (`pricing-market-data-risk-evidence.md`, "Conclusion", last paragraph).

### MD1: the two definitions and their scope

| Option | What happens |
|---|---|
| A (Recommended) Accept both definitions as drafted, with your answers to MD4 and MD5 folded in. | The agent writes a decision record, updates the two register rows, and replaces the two glossary definitions with the drafted wording. The glossary status stays Draft unless your answer says otherwise (`business-glossary.md` lines 4 to 6). |
| B Accept with changes you name. | Same, with your changes. |
| C Reject one or both. | Both domains keep their short register and glossary rows. Step 7 order item 2 stays open. |

A is recommended because each scope line in the draft cites MPC, a peer 10-K or the process map, and the out-of-scope lines follow EPM-DEC-001-0006, 0007 and 0009.

### MD2: who owns Market Data

| Option | What happens |
|---|---|
| A (Recommended) The market risk (middle-office) function that sets up curves, recorded against the "Risk Group" team until a narrower role exists. | The register row names that owner. The role register stays as it is. |
| B A dedicated market data team. | The agent adds a new role to `roles.csv` through its own PR, and the register row names it. |
| C Trading, supply and economics, as `pricing-domain-evidence.md` §8 proposed. | The register row names that owner. Market Data then sits with the teams that also use it for pricing. |
| D Leave it "to be confirmed". | The register row stays as it is. |

A is recommended because the process map already places curve setup in Market Risk Management. The CCRO guidance (DP-10, support only) also has the middle office validate each forward curve daily.

### MD3: who owns Commercial Risk

| Option | What happens |
|---|---|
| A (Recommended) The "Risk Group" team in the role register. | The register row names it. |
| B Another role you name. | The register row names it. A new role goes into `roles.csv` through its own PR. |
| C Leave it "to be confirmed". | No change. |

A is recommended because the peers name a separate risk group that monitors daily (Finding 2), and the role register already has that team.

### MD4: counterparty credit risk (CM 1.2.2.1) and trade confirmations (CM 1.2.2.2)

| Option | What happens |
|---|---|
| A (Recommended) Credit risk yes, limited to trading counterparties. Confirmations no. | Commercial Risk gets a second part for trading counterparty credit. Customer AR credit stays outside it. Confirmations stay with trade operations and feed the domain. |
| B Both in. | Commercial Risk covers all of CM 1.2.2. |
| C Neither. | Commercial Risk covers CM 1.2.2.3 only. |

A is recommended because the existing `dp-commercial-risk` product already holds trading counterparty credit and excludes AR credit, so the domain and the data product would match.

### MD5: volatilities and correlations (CM 1.2.2.3.14)

| Option | What happens |
|---|---|
| A (Recommended) Commercial Risk owns them. Market Data supplies the observations they are built from. | The Commercial Risk definition lists them as risk-model inputs. |
| B Market Data owns them as constructed market data. | The Market Data definition lists them next to forward curves. |

A is recommended because the process sits in Market Risk Management and its outputs serve risk measurement (draft line 32).

### Competency questions this unblocks

No row in `expected.csv` waits on this draft by name. In my reading it supports three questions. Q34 asks which domain concepts a Named KPI quantifies, such as region and crude marker; those are Market Data's assessed items and benchmarks. Q44 asks which source is authoritative; Market Data holds each observation's source and licence. Q17 asks who owns a concept's meaning; the owners in MD2 and MD3 give part of that answer, and Q17 itself waits for Step 5.

## 3. P: the MPC process-map proposals

### The question

Rule on MPC-P01 and P03 to P09 (`business_architecture/reference/mpc/process-map-suggestions.md`). EPM-DEC-001-0011 moved them to Step 7 and asked for the MPLX 10-K read before P01. That read is done (`business_architecture/reference/mpc/mplx-fy2025-10k-fact-sheet.md`; worklog entry "Step 7 groundwork", `business_architecture/ontology/step4/playbook/ontology-worklog.md`, section "Step 7 groundwork: MPLX FY2025 10-K read for MPC-P01 (2026-10-13)"). EPM-DEC-001-0012 also deferred the turnaround lifecycle children of P02 to Step 7, so that item is included as P02b.

### How any answer is carried out

An accepted proposal becomes a proposal file in `business_architecture/business_process/proposals/`, like `MPC-P02-refining-ids.md`. Nobody edits the process map directly (AGENTS.md, working rules; `process-map-suggestions.md` lines 7 to 11). EPM-DEC-001-0017 places these proposals fourth in the Step 7 order, so the work on them starts after items 1 to 3, even if you answer now.

### P01: the empty Midstream L1

Proposal: model the fuels logistics that serves Refining & Marketing (pipeline transport, terminal operations, marine, storage). Leave gas gathering, processing and NGL fractionation out unless a KPI needs them.

Evidence for: MPLX's Crude Oil and Products Logistics segment does the transport, terminal and storage work for MPC under fee-based agreements with minimum volumes. MPC was 48 percent of MPLX's 2025 total revenues and other income, mostly in that segment (`mplx-fy2025-10k-fact-sheet.md` §2, §3). MPLX operates 88 terminals and R&M operates 18 (`mpc-fy2025-10k-fact-sheet.md` §6). The map already has CM 1.2.7 Products Distribution Management and CM 1.3.10 Terminal Loading for the downstream side.

Evidence against: MPC's Midstream segment also includes gas gathering and processing and NGL work (`mpc-fy2025-10k-fact-sheet.md` §2), so option A models part of a reported segment. MPLX also serves third parties (`mplx-fy2025-10k-fact-sheet.md` §3).

| Option | What happens |
|---|---|
| A (Recommended) Fuels logistics only. | A proposal adds Midstream L2 and L3 processes for pipeline transport, terminal operations, marine and storage, linked to CM 1.2.7 and CM 1.3.10. The proposal records gas and NGL as out of scope. |
| B The whole Midstream segment, gas and NGL included. | A larger proposal, with processes that no current downstream node consumes. |
| C Keep Midstream empty and record why. | A scope note only. Midstream stays an L1 with no children. |

A is recommended because the part of Midstream that serves the map's refining and marketing processes is the logistics part, and that is where MPC's spend with MPLX falls.

### P03: inter-refinery intermediate transfers

Proposal: add an inter-refinery transfer process under planning and scheduling, or confirm that CM 1.1.7 covers it and say so in its definition.

Evidence for a need: MPC's refineries move intermediate products between sites, including during partial shutdowns (`mpc-fy2025-10k-fact-sheet.md` §3).

Evidence that the map already covers much of it: CM 1.1.2.9.1 lists "refinery transfers" in its description. CM 1.1.5.5.4 is "Build and run IRT optimization case", with "transfer (IRT)" inputs. CM 1.1.5.1.2.5 receives actual transfer volume and cost. CM 1.2.4.1.18 is Settle Intermediates. The map does not spell out "IRT". I found no node for executing the physical transfer.

| Option | What happens |
|---|---|
| A (Recommended) No new process. Propose a definition note on CM 1.1.7 that names the existing transfer steps. | One proposal with wording only. |
| B Add a new inter-refinery transfer process. | A proposal adds a node, which may overlap the four nodes above. |
| C Reject. | No change. |

A is recommended because the planning, backcasting and settlement steps for transfers already exist, and a new node would overlap them.

### P04: renewable diesel

Proposal: decide scope. At minimum, add renewable feedstock sourcing and renewable fuel marketing. Production can stay parked.

Evidence for: Renewable Diesel is one of MPC's three reportable segments, with the Dickinson plant, the Martinez joint venture, and feedstock aggregation and pre-treatment sites (`mpc-fy2025-10k-fact-sheet.md` §2, §7). The P04 row says renewables "appear only as trading/forecast steps (CM 1.2.1.1.3, CM 1.2.1.3.6) and `renewablesSpecific` flags" (`process-map-suggestions.md` line 22). The map flags ten nodes `renewablesSpecific`, from power forecasting and trade capture to settlements, RINs and emission trading (`downstream_process_map.json`); none is a production step. The words "Renewable Diesel" appear nowhere in it.

Evidence against: production is a plant operation, and the map covers no plant operations for fossil refining either. Its refining children are planning only (`process-map-suggestions.md`, P03 row).

| Option | What happens |
|---|---|
| A (Recommended) Minimum scope: feedstock sourcing and renewable fuel marketing. Production stays parked. | A proposal adds two processes. The product scheme gets a renewable diesel branch. |
| B Full renewable diesel line, production included. | A larger proposal. |
| C Defer. | No change. |

A is recommended because sourcing and marketing are commercial work, which matches the rest of the map, and production would be the map's only plant-operations content.

### P05: regulatory credits

Proposal: broaden RIN handling to Regulatory Credit Management across RIN, LCFS and 45Z, with one regulatory credit concept that has kinds.

Evidence for: MPC's renewable diesel generates RINs, 45Z tax credits and LCFS credits, and MPC runs a RIN integrity program (`mpc-fy2025-10k-fact-sheet.md` §7). Purchased-RIN expense was $1.33 billion in 2025 (`pricing-domain-evidence.md` E6). The map has CM 1.2.3.1.7 Perform RINs/REC Actualization and CM 1.2.4.3.6 Manage RINs Reporting, and no LCFS or 45Z node.

Evidence against: the repo holds no source that describes the steps for LCFS or 45Z. The five steps in the proposal (obligation, generation, purchase with vetting, retirement, reporting) come from the suggestion, not from a filing.

| Option | What happens |
|---|---|
| A (Recommended) One regulatory credit concept with kinds, and a proposal to broaden the RIN processes to it. | A proposal plus one concept scheme. The agent cites the filing for each kind. |
| B Separate process trees for RIN, LCFS and 45Z. | Three parallel proposals. |
| C RINs only. | No change. |

A is recommended because one concept with kinds avoids three parallel trees, and MPC's filing names all three credit kinds together.

### P06: jobber and direct-dealer channels

Proposal: make the sales channel explicit, either as a dimension or as channel-specific L4 steps.

Evidence for: MPC sells through 7,882 brand jobber outlets in 40 states, DC and Mexico, and 1,162 direct-dealer locations, mainly in Southern California (`mpc-fy2025-10k-fact-sheet.md` §5). The words "jobber" and "dealer" appear nowhere in the map. The customer classification C1 to C8 already names these channels (`data-domain-register.md` line 35).

Evidence against channel-specific steps: the map stays company-neutral (`process-map-suggestions.md`, "Not suggested"). The use of C1 to C8 waits for your customer details (EPM-DEC-001-0004).

| Option | What happens |
|---|---|
| A (Recommended) Channel as a dimension, built from C1 to C8 when the Customer work resumes. | No process node changes. The agent adds the dimension after EPM-DEC-001-0004 is resolved. |
| B Channel-specific L4 steps. | A proposal adds steps such as jobber supply agreements and dealer supply contracts. |
| C Reject. | No change. |

A is recommended because a dimension keeps process names company-neutral and reuses the channel classes the register already holds.

### P07: retail-facing nodes

Proposal: review retail-facing nodes and add scope notes where a node assumes company-operated sites. Delete nothing.

Evidence for: MPC sold its company-operated retail (Speedway) in 2021 (`mpc-fy2025-10k-fact-sheet.md` §1). Boundary rule 5 already says retail pump prices sit outside MPC's data (`data-domain-register.md` line 64). Candidate nodes are CM 1.3.6.6.15 Manage Brand Loyalty Programs, the Retail Payments data product, and the value-stream stage "Retail Sales & Payment".

Evidence against marking all of them: MPC still runs a loyalty program, Marathon Rewards (`pricing-domain-evidence.md` E21), so CM 1.3.6.6.15 does not assume company-operated sites.

| Option | What happens |
|---|---|
| A (Recommended) Scope notes only, node by node, with no deletion. | One proposal with notes. Nodes that do not assume company-operated sites, such as the loyalty node, get no note. |
| B Mark retail nodes out of scope. | A proposal that narrows scope. |
| C No change. | No change. |

A is recommended because the map is meant to stay usable for a company that differs from MPC (`process-map-suggestions.md`, P07 row).

### P08: intercompany logistics fees

Proposal: confirm that intercompany logistics fees fall under CM 1.3.8.4.6 Manage Intercompany Invoicing and Order-to-Cash settlement.

Evidence for: R&M pays MPLX $3.69 per barrel under long-term fee-based agreements (`mpc-fy2025-10k-fact-sheet.md` §6; `pricing-domain-evidence.md` E9). CM 1.3.8.4.6 exists in the map with no description.

Evidence against: none found in the repo.

| Option | What happens |
|---|---|
| A (Recommended) Confirm, and propose a description for CM 1.3.8.4.6 that names affiliate logistics fees. | One proposal with wording only. |
| B Add a separate process. | A proposal adds a node. |
| C Out of scope. | No change. |

A is recommended because the node already exists and has no description, so a description settles the question.

### P09: candidate measures on the value stream

Proposal: attach R&M margin per barrel, opex per barrel, distribution cost per barrel, turnaround cost per barrel and the regional 3-2-1 cracks as candidate measures on the Price Management and Performance Management & Backcasting stages. Classify each one. None is a KPI automatically.

Evidence for: MPC reports all of them (`mpc-fy2025-10k-fact-sheet.md` §8). Both stages exist in `value_stream_commercial_lifecycle.json`.

Evidence against acting now: EPM-DEC-001-0017 seeds the `kpi` module from your categories (question 1). Two open items affect these measures, the changed R&M margin definition and the unconfirmed capacity basis (`pricing-domain-evidence.md` §3 notes 1 and 4).

| Option | What happens |
|---|---|
| A (Recommended) Accept, after your KPI categories arrive. Each measure is classified against them. | The agent attaches the measures in the same PR series as the `kpi` module. |
| B Accept now, independent of your categories. | The measures may need reclassifying when your list arrives. |
| C Reject. | No change. |

A is recommended because it follows the order in EPM-DEC-001-0017 and avoids classifying the same measures twice.

### P02b: turnaround lifecycle children

Proposal: add children under "Refinery Asset Reliability and Turnaround Coordination" to plan scope, schedule, execute, restart and close out cost. EPM-DEC-001-0012 deferred this to Step 7, together with the turnaround-cost measure.

Evidence for: MPC performs turnarounds periodically at each refinery and reports planned turnaround cost as its own line, $1.39 per barrel in 2025 (`mpc-fy2025-10k-fact-sheet.md` §3, §8). Evidence against: the five step names come from the suggestion, not from a filing.

| Option | What happens |
|---|---|
| A (Recommended) Accept, as a proposal that pairs with the turnaround-cost measure definition. | A proposal adds the children. The measure gets a process anchor. |
| B Defer again. | No change. |

A is recommended because the turnaround-cost measure needs a process to sit on (competency question 37), and the node has no children today.

### Competency questions these unblock

No row in `expected.csv` waits on P01, P03 to P08 or P02b by name. They add process content that Q1 and Q2, both answerable today, will report on. P09 feeds the rows that wait on Step 7 value streams and KPIs. These rows are 10 (value streams), 33 (which process a Named KPI informs) and 37 (where a Named KPI sits).
