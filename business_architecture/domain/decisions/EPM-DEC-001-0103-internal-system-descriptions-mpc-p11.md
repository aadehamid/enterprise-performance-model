# EPM-DEC-001-0103: The internal systems' descriptions, drafted from the repository; proposal MPC-P11 waits for the decision owner

*2026-10-26:* the wait is over: the decision owner accepted MPC-P11 (EPM-DEC-001-0104).

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028, amendment of 2026-10-25, evening: the descriptions and the releases); one question open for the decision owner (MPC-P11); *2026-10-26:* MPC-P11 accepted (EPM-DEC-001-0104) |
| Date | 2026-10-26 |
| Questions | Item G, items 10 and 11 (EPM-DEC-001-0099): what do the internal systems do, and which systems do the customer-lifecycle processes use? |
| Source | The process map and core 2.3.0's process definitions; the `party` module's customer roles, data flows and attributes, from the decision owner's customer inputs; `answers-2026-10-25-item-g.md`; `answers-2026-10-25-queue-delegation.md` |

## Context

EPM-DEC-001-0099 recorded the decision owner's acceptance of Claude's eleven item G recommendations ("3. I will go with your recommendation"). Item 10: Claude drafts a description of each internal system from the repository, for one approval round, as was done for DPO. Item 11: the customer processes' system links go to a process-map proposal, MPC-P11, after the decision owner checks the weak ones. On 2026-10-25 the decision owner then delegated the night's remaining approvals, the internal systems' descriptions included ("Yes, delegate as described (Recommended)"; EPM-DEC-001-0028, amendment of 2026-10-25, evening).

## Decision

**What follows (Claude, under EPM-DEC-001-0028, amendment of 2026-10-25, evening):**

1. **The internal systems are defined from the repository.** Each description says what the evidence shows the system does for the business, and nothing more:
   - **14 `system`-module systems,** from the processes the process map says use them and those processes' definitions in core 2.3.0: Planning DB, APS Planning DB, Planning and Scheduling UI, Backcasting Dashboard, Market Outlook and Avails Dashboard, PSR, the XPIMS <> DPO Integration Macro, TMR, TRR, the three premise documents, the RFC Hindsight Analysis Excel and the Actuals Case Prep File. Each cites core 2.3.0 beside the process map; TMR also cites the customer inputs, which name it the Terminal Margin Ranking System.
   - **20 `party` customer systems,** from their customer roles, data flows and attributes: Dealer Master, Star, Terminal download, Tax Image Silo, TFR, TMIS, RCMS, Data Products IDP, FuelFacs, TASDM, Terminal Upload, XREF, TMT, Customer Portal, Terminal Audit System, EIS, Asphalt Marketing System, Brand Credit Card System, Terminal Margin Ranking System and Corp_Vetting. Each cites the decision owner's customer inputs.
   - Each carries a note that Claude drafted it from the repository and approved it under the delegation. The business confirms or corrects each (`business-closeout.md`, point 16).
2. **Still undefined:** TopDay and VALT, which wait for their owners (`business-closeout.md`, point 12), and Drop Tank, Gas Buddy, DTN File Server and Federal Health, which wait for the customer-data owner (point 11).
3. **Two new sources, tier 1:** core 2.3.0's process definitions, and the decision owner's customer inputs as the `party` module holds them.
4. **MPC-P11 is written and not applied.** `business_architecture/business_process/proposals/MPC-P11-customer-process-systems.md` proposes the strong and medium links and lists the weak ones as not proposed. The process map is the process authority, and AGENTS.md says to suggest its changes as proposals; the delegation covers questions the evidence order settles, and accepting a change to the authority itself is the decision owner's. So the proposal waits for the decision owner, and `downstream_process_map.json` does not change here. *2026-10-26:* the decision owner accepted it, and the map gains its links (EPM-DEC-001-0104).
5. **Releases, approved by Claude under the delegation (minor):** `system` 1.3.0 and `party` 1.3.0 carry the descriptions; `integration` 2.3.0 carries the two new sources.

## Open question for the decision owner

- **MPC-P11:** accept the proposal's strong and medium links, so the process map names those systems for the customer processes? Claude's recommendation: accept them, and leave the three weak links out until a source shows them. *2026-10-26:* the decision owner accepted them, and the three weak links stay out (EPM-DEC-001-0104).

## Alternatives considered

- **Leave the descriptions for a separate approval round with the decision owner.** Not chosen: the decision owner delegated the night's approvals, the internal systems' descriptions included, so nothing waits for them; the business still confirms each (point 16).
- **Apply MPC-P11 under the delegation.** Not chosen: it would edit the process authority without its owner's acceptance.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-25-item-g.md`: "3. I will go with your recommendation". Saved in `answers-2026-10-25-queue-delegation.md`: "Yes, delegate as described (Recommended)".

## Evidence

- `ontology/system/definitions.csv`, `ontology/party/definitions.csv`, `ontology/system/sources.csv`, `ontology/authority/source-tiers.csv`.
- `business_architecture/ontology/releases/core/2.3.0/core.ttl` (process names and definitions); `ontology/party/systems.csv`, `data-flows.csv`, `attributes.csv`.

## Consequences

- `system/test_systems.py` and `party/test_party_systems.py` pin 32 and 38 defined systems and the remaining undefined ones. *2026-10-26:* `system` 1.4.0 adds MPC-P11's seven, so the system test pins 39 (EPM-DEC-001-0104).
- *2026-10-27:* Dealer Master's drafted description is corrected from the decision owner's customer inputs of that day: it is not built on Salesforce, and jobbers do not start there (EPM-DEC-001-0108).
