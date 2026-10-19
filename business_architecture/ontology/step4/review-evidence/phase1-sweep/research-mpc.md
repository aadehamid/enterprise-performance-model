# MPC research brief for the Phase 1 sweep

**Purpose.** Evidence from Marathon Petroleum Corporation's (MPC) public disclosures that bears on how its downstream processes hand work to each other. It is input for answering the held Phase 1 relationship rows. **Prepared:** 2026-10-12 by Claude.

**Sources** (register IDs from `business_architecture/reference/mpc/source-register.md`, plus one new):
- **MPC-S01:** Form 10-K FY2025, filed 2026-02-26, accession 0001510295-26-000009. Read from EDGAR in full text on 2026-10-12.
- **MPC-S16 (new):** Proxy statement (DEF 14A), filed 2026-03-16, https://www.sec.gov/Archives/edgar/data/1510295/000151029526000023/mpc-20260316.htm. Read 2026-10-12.
- **MPC-S15 / marathonfuel.com:** site navigation, read 2026-10-12.
- Local evidence already cited in the repo: `mpc-fy2025-10k-fact-sheet.md`, `pricing-domain-evidence.md`, `customer-classification-evidence.md`, `process-map-suggestions.md`.

**The main limit.** MPC discloses what it does, its results and its governance. It does not disclose internal workflows: who hands what to whom between, for example, trade capture and confirmation, or forecasting and optimization. For nearly every held row, MPC evidence supports the business context only. The handoff itself has to be a reference-model position, which is the same basis the decision owner used for #204 and #205.

## 1. Planning, refining and supply

- **Integrated refining system.** "The transportation links that connect our refineries allow the movement of intermediate products between refineries to optimize operations, produce higher margin products and efficiently utilize our processing capacity." Intermediates also move during partial shutdowns. *(MPC-S01, Item 1 Business, Refining & Marketing)*
- **Turnarounds.** Planned maintenance that temporarily shuts down refinery units "periodically" at each refinery. *(MPC-S01, Item 1)*
- **Crude acquisition.** Crude is bought from "various domestic and foreign suppliers", under term contracts with market-related pricing and through spot purchases and exchanges. Other charge and blendstocks are also bought. *(MPC-S01, Item 1; fact sheet §4)*
- **Throughput can exceed capacity** because of other charge and blendstocks and turnaround timing. *(MPC-S01, Item 2)*
- **Not disclosed:** how demand forecasting, regional optimization, refinery planning (LP) and scheduling hand off to each other, or who approves plans. That makes every CM-1-1 handoff a reference-model position.

## 2. Supply, trading and risk

- **Purpose of derivatives.** MPC uses commodity derivatives "as part of an overall program to hedge commodity price risk" and does "a limited amount of trading not directly related to our physical transactions". It hedges crude and ethanol purchases between purchase and use, and converts fixed-price refined-product sales to market-based prices. *(MPC-S01, Item 7A)*
- **Policy and monitoring.** "We closely monitor and hedge our exposure to market risk on a daily basis in accordance with policies approved by our board of directors. Our positions are monitored daily by a risk control group to ensure compliance with our stated risk management policy." *(MPC-S01, Item 7A)* This is direct MPC evidence for the pattern that the board approves the policy, the business acts within it, and a separate control group monitors compliance.
- **MPLX's parallel arrangement.** Its hedge strategy and position monitoring "are carried out by its hedge committee, comprised of members of senior management", and its "risk management policy does not allow it to enter into speculative positions". *(MPC-S01, Item 7A, MPLX)*
- **Counterparty credit.** MPC "select[s] and monitor[s] counterparties" for financial instruments, mainly major financial institutions and energy companies, and uses master netting agreements with monthly net cash settlement. Receivable allowances are reviewed quarterly, and past-due balances over 150 days are reviewed individually. *(MPC-S01, Item 8 Notes: Concentrations of credit risk; Accounts receivable)* MPLX "analyzes the customer's financial condition prior to entering into a transaction or agreement, establishes credit terms and monitors the appropriateness of these terms on an ongoing basis". *(MPC-S01, Item 7A)* That is a clear disclosed credit-assessment pattern of assess, set terms, then monitor.
- **Trading and supply sales volumes.** Refined product sales "include volumes marketed directly to end-users and trading/supply volumes such as bulk sales to large unbranded resellers and other downstream companies". *(MPC-S01, Item 1, refined product sales table note)*
- **Not disclosed:** the trade lifecycle (capture, confirmation, actualization, settlement), how limits are set and by whom below board level, risk analytics, risk reporting cadence, and trading-compliance surveillance. The 10-K has no CFTC discussion; FERC appears only for interstate pipeline tariffs.

## 3. Renewables and regulatory credits

- **RFS.** MPC must blend renewable fuels at a rate "commensurate to the EPA's quota", or "purchase RINs in the open market". *(MPC-S01, Item 1A)*
- **RIN integrity.** "We have developed a RIN integrity program to vet the RINs that we purchase, and we incur costs to audit RIN generators." *(MPC-S01, Item 1 Regulatory Matters; Item 1A)*
- **Credits generated.** Renewable diesel generates RINs, 45Z tax credits and LCFS credits, which MPC uses toward its RFS and LCFS compliance obligations. *(MPC-S01, Item 1; fact sheet §7)*

## 4. Commercial and marketing

- **Four markets:** wholesale (including exports), spot, branded and retail distribution. *(MPC-S01, Item 1, Competition)*
- **Channels:** 7,882 brand jobber outlets, where "independent entrepreneurs primarily maintain Marathon-branded outlets". 1,162 direct dealer locations under long-term supply contracts, mainly ARCO in Southern California. Company-operated retail was sold to 7-Eleven in 2021. *(MPC-S01, Item 1)*
- **Card transactions.** MPC processes "credit card transactions on behalf of certain of our marketing customers" *(MPC-S01, Item 7, R&M margin reconciliation note (a))*. Its systems support "credit card payments and authorizations at certain of our customers' retail outlets" *(MPC-S01, Item 1A, cybersecurity risk)*. marathonfuel.com lists Payment Cards, Fleet Cards, Gift Cards and Rewards *(site navigation, 2026-10-12)*. Card administration and production details, including issuers and vendors, are **not disclosed**.
- **Pricing.** The "vast majority" of contracts are priced at market at delivery, fixed-price sales are hedged to market-based prices, and Marathon Rewards offers fuel incentives. *(pricing-domain-evidence.md, items P7, P9, P10)*
- **Not disclosed:** order management, quote and renewal processes, product-development and R&D governance, marketing-communications workflow, tax determination and tax master data.

## 5. Governance and decision authority

- **Enterprise risk management.** "We apply a comprehensive ERM program across the Company to identify, assess and manage enterprise-level risks … established and driven by our leadership team, led by our enterprise risk manager and ERM Committee, and supported by officers and senior managers … [who] provide regular updates to our Board and its committees." *(MPC-S16, Board oversight of risk)* The 10-K adds that the ERM methodology is "established and led by our executive leadership team and overseen by our Board". *(MPC-S01, Item 1C Cybersecurity)*
- **Board committees.** The Audit Committee oversees the independent auditor and, with the Board, business continuity, data privacy and cybersecurity. Its charter assigns it review of the ERM process and risk-management guidelines and policies. The Sustainability and Public Policy Committee oversees environment and climate risk matters. *(MPC-S16; Audit Committee Charter, 2024-07-31)*
- **Management system.** The Operational Excellence Management System follows Plan-Do-Check-Act, is aligned to ISO 9001 and covers RC14001. *(fact sheet §1)*
- **Policy approved above, execution below.** Market-risk policies are board-approved and monitored daily by a separate risk control group (§2). This supports reading a policy or limit-setting process as governing the processes that act within it, and a monitoring process as checking them, as opposed to an analytics process merely advising.

## 6. What this brief supports, and what it doesn't

- **Supports, with MPC citations:** advisory vs deciding roles in market risk (policy, then daily monitoring); a credit-assessment pattern; the RIN purchase and integrity link; integrated refining with intermediate transfers; card-transaction processing for marketing customers; jobber and dealer channels; board-level ERM governance.
- **Doesn't support:** any specific internal handoff between two named processes. Those answers must be reference-model positions informed by the industry brief (`research-industry.md`), labelled as such, as the decision owner's #204 and #205 answers were.
