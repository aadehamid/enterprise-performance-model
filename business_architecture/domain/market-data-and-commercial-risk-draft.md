# Market Data and Commercial Risk: draft definitions

**Status:** Draft, for Hamid's decision · **Date:** 2026-10-13 · **Decisions:** EPM-DEC-001-0006 (Market Data is its own domain), EPM-DEC-001-0007 (Commercial Risk owns P10), EPM-DEC-001-0010 (full definitions at Step 7)

EPM-DEC-001-0010 leaves the full definitions (scope, owners, entities) to Step 7. This draft proposes them from the evidence the repo already holds, so Hamid can approve, change or reject each part. Nothing here is decided.

Evidence: `../reference/downstream-peers/pricing-market-data-risk-evidence.md` (Findings 1 to 3: MPC's FY2025 10-K and seven U.S. refining peers' FY2025 10-Ks; Finding 4: an SAP IS-Oil practitioner source, DP-08, and the APQC Downstream PCF, DP-09), and the process map's CM 1.2.2 Confirmations & Risk Management subtree.

## Market Data

**Proposed definition.** The data domain for external and constructed market observations, and the rules for using them: price assessments and quotes, benchmark and index prices, forward curves, differentials, and each source's methodology and licence.

| Part | Proposal | Evidence |
|---|---|---|
| In scope | Price assessments from licensed reporting agencies and exchanges (Platts, Argus, OPIS, NYMEX, CBOT); benchmark and index definitions (for example a 3-2-1 crack, the Argus Sour Crude Index); forward curves; location and quality differentials; methodology and publication rules (P11); licences and permitted uses | Finding 1 (DP-01, DP-03, DP-05, DP-06, DP-07; MPC-S01 Item 7); Finding 4 (DP-08, DP-09) |
| Out of scope | The prices the company sets or realizes (Commercial Pricing & Price Realization); positions, limits and valuations (Commercial Risk) | EPM-DEC-001-0006, 0007, 0009 |
| Key entities | Market observation (one value, for one assessed item, on one date, from one source); assessed item (product, location, timing); benchmark (a formula over assessed items); forward curve (dated points for one item); differential; source and licence | Finding 4: systems keep quotations as their own maintained data that pricing formulas reference |
| Consumers | Commercial pricing, fair-value accounting, refinery margin benchmarking, RIN pricing, investor reporting | Finding 1 |
| Processes | CM 1.2.2.3.3 Setup And Manage Curves (today under Market Risk Management); APQC 4.1.7 Evaluate commodity values | Finding 4 |
| Owner | **For Hamid.** The process map gives CM 1.2.2.3.3 no RACI. Candidates: the market risk (middle-office) function that sets up curves, or a dedicated market data team | Finding 4; DP-10 (support only: the middle office validates forward curves) |

## Commercial Risk

**Proposed definition.** The data domain for commodity price exposure and its control: positions and books, derivatives and hedges, risk limits and the delegation of authority, risk measures such as Value at Risk, valuations and profit and loss, and risk reporting.

| Part | Proposal | Evidence |
|---|---|---|
| In scope | Book structure; positions; derivative and hedge records (P10: price risk and hedging); risk limits and the delegation of authority; risk measures (VaR and scenarios); commodity valuations, end-of-day and end-of-month valuation and P&L; risk policy compliance; risk reporting | Finding 2 (DP-01, DP-02, MPC-S01 Item 7A); CM 1.2.2.3.1 to CM 1.2.2.3.15 |
| Question | **For Hamid:** does Commercial Risk also own **counterparty credit risk** (CM 1.2.2.1: credit reviews, limits, collateral, exposure, margining) and **trade confirmations** (CM 1.2.2.2)? Both sit under the same CM 1.2.2 parent. Recommendation: credit risk yes, as a second part of the domain; confirmations no, they are trade operations that feed it | The process map's CM 1.2.2 tree |
| Out of scope | Market observations (Market Data, referenced, not owned); setting or realizing prices (Commercial Pricing) | EPM-DEC-001-0006, 0009 |
| Key entities | Book; position; derivative contract; risk limit; delegation of authority; risk measure; valuation; P&L explain; risk report | CM 1.2.2.3 process names; Finding 2 for derivative contracts (DP-01, DP-02, MPC-S01 Item 7A) |
| Question | **For Hamid:** CM 1.2.2.3.14 Manage Volatilities And Correlations. Volatilities and correlations are constructed from market observations (Market Data's definition) and used as risk-model inputs (Commercial Risk). Recommendation: Commercial Risk owns them, because the process sits in Market Risk Management and its outputs serve risk measurement; Market Data supplies the observations they are built from | The process map's CM 1.2.2.3 tree |
| Governance | Board-approved policy and limits, monitored daily by a risk control group | Finding 2 (DP-01: "monitored daily by our global risk group"; DP-02: "monitored and managed on a daily basis by our risk control group") |
| Owner | **For Hamid.** The process map gives CM 1.2.2 no RACI. Candidate: the risk control function the peers describe; the role register has a "Risk Group" team (`../ontology/organization/roles.csv`) | Finding 2; EPM-DEC-001-0031 |

## What Hamid decides

1. Approve, change or reject each definition and its scope.
2. Name the owner of each domain.
3. Answer the credit-risk and confirmations question, and the volatilities and correlations question.

When he does, the answers go into a decision record and the data domain register (`data-domain-register.md`), and the glossary rows for both domains move from Draft.
