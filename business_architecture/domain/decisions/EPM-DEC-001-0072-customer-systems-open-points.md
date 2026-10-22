# EPM-DEC-001-0072: The decision owner's answers on the customer systems' open points

| Field | Value |
|---|---|
| Status | Decided (the decision owner's recorded words, 2026-10-21) |
| Date | 2026-10-21 |
| Questions | Three of the five points EPM-DEC-001-0069 left open for the decision owner: whether input 6's CBS is FuelFacs, whether the Terminal Margin Ranking System is the process map's TMR, and the meaning of HOLDORDIND, Taboot, MPA_Flag, CR_Incentive_Flag and TDS Seller ID |
| Source | Claude Code session of 2026-10-21 (session 7); `answers-2026-10-21-open-codes.md`; amended 2026-10-22 (`answers-2026-10-22-morning.md`) |

## Context

EPM-DEC-001-0069 built the customer's systems, data flow and attributes in the `party` module and left five points open for the decision owner (its Consequences). Claude raised three of them again: CBS, TMR and the meaning of the five codes. The decision owner answered in one message, with four answers: CBS and TMR are settled, TDS Seller ID is defined, and the other four codes are kept for them to define later. The other two points were not raised: whether TABS Seller ID is read rightly, and whether TID Nbr is a terminal identifier (EPM-DEC-001-0069, item 8).

## Decision

**The decision owner's answers:**

1. **HOLDORDIND, Taboot, MPA_Flag and CR_Incentive_Flag stay in the model** as named fields without a definition. The decision owner will define them later: "leave HOLDORDIND, Taboot, MPA_Flag, CR_Incentive_Flag in . I can define later".
2. **TDS Seller ID is the seller's identifier:** "TDS Seller ID this is the ID of the seller". It stays mapped to an external identifier of the party, as EPM-DEC-001-0069 item 8 mapped it.
3. **Input 6's CBS is assumed to be FuelFacs** for this model: "CBS is potentially FuelFac. Let us assume it is in this case". The decision owner described FuelFacs' role as "an enterprise-wide terminal integration and business-information system—not simply customer relationship management."
4. **The Terminal Margin Ranking System is the process map's TMR:** "Terminal Margin Ranking System = TMR".

**What follows (Claude):**

- The CBS sourcing of terminal customers stays on FuelFacs. Its note no longer calls the identity open; it says the decision owner assumes, for this model, that input 6's CBS is FuelFacs.
- FuelFacs' role says it is the enterprise-wide terminal integration and business-information system, from the decision owner's words, beside what the inputs show it doing.
- The Terminal Margin Ranking System carries TMR as an alternative label and `skos:exactMatch` to the system module's TMR node, so four customer systems now match the system module. The build holds this match by hand (`SAME_SYSTEM` in `build_party.py`), because the two nodes have different slugs.
- Question 15's `q15b` compares a node's alternative labels as well as its preferred label, so the TMR pair is reported as one system in two modules. The only rows this adds are `skos:exactMatch` rows: the TMR pair, and the RightAngle and KittyHawk pairs under their alternative spellings.
- EPM-DEC-001-0069 keeps its text, with dated notes pointing here.

## Amendment, 2026-10-22: the four codes and TID Nbr wait for the business; TABS Seller ID confirmed

The session 7 morning summary asked the decision owner about the two points this record left open, and about the four codes again. They answered on 2026-10-22.

**The decision owner's answers:**

1. **HOLDORDIND, Taboot, MPA_Flag, CR_Incentive_Flag and the reading of TID Nbr stay as they are** until the ontology is shared for use: "let us keep the code this way. We wont settle it until finish the ontology and start sharing for consumption at which point we will confirm what these means from the business".
2. **The reading of TABS Seller ID is confirmed:** "I confirm".

**What follows (Claude, under EPM-DEC-001-0028):**

- The four codes stay named fields without a definition, and TID Nbr stays read as a terminal identifier that describes a site. Each stays open, with a trigger: when the ontology is first shared for consumption, the business confirms what each one means, and the answer is recorded as an amendment here.
- TABS Seller ID keeps the reading in EPM-DEC-001-0069, item 8: the party's seller identifier in a terminal lifting-control service, mapped to an external identifier of the party. It is now the decision owner's confirmed reading, not only Claude's.
- No file in the `party` module changes: the attributes carry no definition or note for these codes.

## Alternatives considered

- **Keep CBS open until a source confirms it.** Not chosen: the decision owner decided to assume it for this model.
- **Rename the Terminal Margin Ranking System's slug to `tmr`.** Not chosen: the module is not released, but the slug is cited in two sourcings, and a hand-held match states the decision where it is made. *2026-10-22:* the module is now released as 1.0.0, so the slug is part of a released identity (EPM-DEC-001-0074).

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-21-open-codes.md`, one message, one answer per line:

- "leave HOLDORDIND, Taboot, MPA_Flag, CR_Incentive_Flag in . I can define later"
- "TDS Seller ID this is the ID of the seller"
- "CBS is potentially FuelFac. Let us assume it is in this case given If you saw CBS on a downstream terminal or fuel-distribution architecture diagram, FuelFACS Central Business System is a concrete possibility. Its documented role is an enterprise-wide terminal integration and business-information system—not simply customer relationship management."
- "Terminal Margin Ranking System = TMR"

For the amendment of 2026-10-22, from `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`:

- "let us keep the code this way. We wont settle it until finish the ontology and start sharing for consumption at which point we will confirm what these means from the business"
- "I confirm"

## Evidence

- EPM-DEC-001-0067, 0068, 0069.
- `business_architecture/ontology/system/systems.csv` (the system module's TMR node, from the process map's systems fields).

## Consequences

- `party/systems.csv`, `customer-sources.csv` and `build_party.py` carry the answers; `systems.ttl` is rebuilt. `test_party_systems.py` pins the four matches, the build's rejection of a hand-held match that does not hold, and the CBS sourcing's note, and `regression/test_run.py` pins q15b's four cross-module pairs.
- Still open for the decision owner: the meaning of HOLDORDIND, Taboot, MPA_Flag and CR_Incentive_Flag, which they will define later; whether TABS Seller ID is read rightly; whether TID Nbr is a terminal identifier. *2026-10-22:* TABS Seller ID's reading is confirmed; the four codes and TID Nbr wait until the ontology is shared for consumption, when the business confirms them (amendment of 2026-10-22 above).
