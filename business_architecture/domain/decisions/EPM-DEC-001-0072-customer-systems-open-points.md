# EPM-DEC-001-0072: The decision owner's answers on the customer systems' open points

| Field | Value |
|---|---|
| Status | Decided (the decision owner's recorded words, 2026-10-21) |
| Date | 2026-10-21 |
| Questions | The points EPM-DEC-001-0069 left open for the decision owner: whether input 6's CBS is FuelFacs, whether the Terminal Margin Ranking System is the process map's TMR, and the meaning of HOLDORDIND, Taboot, MPA_Flag, CR_Incentive_Flag and TDS Seller ID |
| Source | Claude Code session of 2026-10-21 (session 7); `answers-2026-10-21-open-codes.md` |

## Context

EPM-DEC-001-0069 built the customer's systems, data flow and attributes in the `party` module and left points open for the decision owner (its Consequences). Claude listed them, and the decision owner answered four of them in one message. Two open points stay with them: whether TABS Seller ID is read rightly, and whether TID Nbr is a terminal identifier (EPM-DEC-001-0069, item 8).

## Decision

**The decision owner's answers:**

1. **HOLDORDIND, Taboot, MPA_Flag and CR_Incentive_Flag stay in the model** as named fields without a definition. The decision owner will define them later: "leave HOLDORDIND, Taboot, MPA_Flag, CR_Incentive_Flag in . I can define later".
2. **TDS Seller ID is the seller's identifier:** "TDS Seller ID this is the ID of the seller". It stays mapped to an external identifier of the party, as EPM-DEC-001-0069 item 8 mapped it.
3. **Input 6's CBS is taken to be FuelFacs** for this model: "CBS is potentially FuelFac. Let us assume it is in this case". The decision owner described FuelFacs' role as "an enterprise-wide terminal integration and business-information system—not simply customer relationship management."
4. **The Terminal Margin Ranking System is the process map's TMR:** "Terminal Margin Ranking System = TMR".

**What follows (Claude):**

- The CBS sourcing of terminal customers stays on FuelFacs. Its note no longer calls the identity open; it says the decision owner takes input 6's CBS to be FuelFacs.
- FuelFacs' role says it is the enterprise-wide terminal integration and business-information system, from the decision owner's words, beside what the inputs show it doing.
- The Terminal Margin Ranking System carries TMR as an alternative label and `skos:exactMatch` to the system module's TMR node, so four customer systems now match the system module. The build holds this match by hand (`SAME_SYSTEM` in `build_party.py`), because the two nodes have different slugs.
- Question 15's `q15b` compares a node's alternative labels as well as its preferred label, so the TMR pair is reported as one system in two modules. The only rows this adds are `skos:exactMatch` rows: the TMR pair, and the RightAngle and KittyHawk pairs under their alternative spellings.
- EPM-DEC-001-0069 keeps its text, with dated notes pointing here.

## Alternatives considered

- **Keep CBS open until a source confirms it.** Not chosen: the decision owner decided to assume it for this model.
- **Rename the Terminal Margin Ranking System's slug to `tmr`.** Not chosen: the module is not released, but the slug is cited in two sourcings, and a hand-held match states the decision where it is made.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-21-open-codes.md`, one message, one answer per line:

- "leave HOLDORDIND, Taboot, MPA_Flag, CR_Incentive_Flag in . I can define later"
- "TDS Seller ID this is the ID of the seller"
- "CBS is potentially FuelFac. Let us assume it is in this case given If you saw CBS on a downstream terminal or fuel-distribution architecture diagram, FuelFACS Central Business System is a concrete possibility. Its documented role is an enterprise-wide terminal integration and business-information system—not simply customer relationship management."
- "Terminal Margin Ranking System = TMR"

## Evidence

- EPM-DEC-001-0067, 0068, 0069.
- `business_architecture/ontology/system/systems.csv` (the system module's TMR node, from the process map's systems fields).

## Consequences

- `party/systems.csv`, `customer-sources.csv` and `build_party.py` carry the answers; `systems.ttl` is rebuilt. `test_party_systems.py` pins the four matches and the CBS sourcing's note, and `regression/test_run.py` pins q15b's four cross-module pairs.
- Still open for the decision owner: the meaning of HOLDORDIND, Taboot, MPA_Flag and CR_Incentive_Flag; whether TABS Seller ID is read rightly; whether TID Nbr is a terminal identifier.
