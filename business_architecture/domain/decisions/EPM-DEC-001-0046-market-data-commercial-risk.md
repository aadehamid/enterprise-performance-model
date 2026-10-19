# EPM-DEC-001-0046: Market Data and Commercial Risk: definitions, scope and owners

| Field | Value |
|---|---|
| Status | Decided (Hamid, 2026-10-18: MD1 to MD5; the wording of the register and glossary delegated under EPM-DEC-001-0028) |
| Date | 2026-10-18 |
| Questions | MD1 to MD5 in `decision-packages/2026-10-14/step7-rulings.md`; the "What Hamid decides" list in `market-data-and-commercial-risk-draft.md` |
| Source | Claude Code session, 2026-10-18 |

## Context

EPM-DEC-001-0006 made Market Data its own domain and EPM-DEC-001-0007 gave Commercial Risk price risk and hedging (P10). EPM-DEC-001-0010 left their full definitions to Step 7. The draft of 2026-10-13 (`market-data-and-commercial-risk-draft.md`, PR #268) proposed them and asked Hamid five questions.

## Decision

**Hamid's decisions:**
1. **MD1, accept with changes.** The two domains are defined by the business meaning and control needs of their information:
   - **Market Data** governs externally sourced market observations and shared market-data products, including benchmark identifiers, source provenance, licensing restrictions, timestamps, assessment conventions, and approved curve-construction metadata.
   - **Commercial Risk** governs commercial exposure, risk measures, limits, risk-model methodologies and parameters, and trading-counterparty credit assessment and exposure.
   - The publisher's methodology stays the publisher's. EPM governs its record of that methodology, not the methodology.
2. **MD2, provisional.** The Risk Group is the accountable owner of Market Data, pending confirmation of its mandate. Operational stewardship (curve maintenance), business requirements (trading, supply, refinery economics and planning, finance), independent validation, and licensing and contractual controls are recorded as separate responsibilities.
3. **MD3.** The Risk Group owns Commercial Risk, subject to an explicit mandate and a named accountable authority.
4. **MD4.** Trading-counterparty credit risk (CM 1.2.2.1) is in Commercial Risk. Trade confirmations (CM 1.2.2.2) stay with trade operations and feed the domain. Customer receivables and AR credit stay outside it. A counterparty keeps one legal-entity identity across the trading-risk and receivables contexts.
5. **MD5.** Commercial Risk owns volatilities and correlations as risk-model parameters (estimation windows, calibration methods, stress assumptions, the estimated values used in a model). Vendor-supplied observations, such as implied-volatility surfaces and historical prices, are Market Data.

**What follows (Claude, under EPM-DEC-001-0028):**
1. The data domain register's two rows carry these definitions and owners; "Owner to be confirmed" is replaced.
2. The glossary rows for both domains carry the new definitions. Their status stays Draft, because Hamid's answer does not approve the glossary wording (the package said the status stays Draft unless his answer says otherwise).
3. The draft file is marked decided and points here.
4. The governance responsibilities in MD2 are recorded in words only. Modelling them as assignments waits for the semantic-ownership decision that Hamid kept separate (role question 7).

## Alternatives considered

- **Accept the draft as written (MD1 A).** Not chosen: Hamid's answer was B, with the distinctions above.
- **A dedicated market data team, or trading, supply and economics, as Market Data's owner (MD2 B, C).** Not chosen: Hamid chose the Risk Group provisionally.

## Hamid's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/answers-2026-10-18.md`: "MD1: B. Accept the domain split with explicit distinctions between external observations, shared market-data products, risk methodologies, and modeled parameters.", "MD2: A provisionally. Assign Risk Group accountability pending mandate confirmation, and record operational stewardship, licensing controls, and independent validation separately.", "MD3: A. MD4: A. MD5: A for risk-model parameters, with vendor-supplied volatility observations governed as Market Data.", and the two definitions: "Market Data governs externally sourced market observations and shared market-data products, including benchmark identifiers, source provenance, licensing restrictions, timestamps, assessment conventions, and approved curve-construction metadata." and "Commercial Risk governs commercial exposure, risk measures, limits, risk-model methodologies and parameters, and trading-counterparty credit assessment and exposure." Items 1 to 4 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and Hamid can reverse them.

## Evidence

`market-data-and-commercial-risk-draft.md`; `business_architecture/reference/downstream-peers/pricing-market-data-risk-evidence.md`, Findings 1 to 4; the process map's CM 1.2.2 subtree; `business_architecture/business_process/data_product_portfolio.json`, the `dp-commercial-risk` entry; `business_architecture/ontology/organization/roles.csv`, the "Risk Group" row.

## Consequences

- Step 7 order item 2 (EPM-DEC-001-0017) is done.
- The register, glossary and draft change as listed under "What follows".
