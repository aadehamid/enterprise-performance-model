# EPM-DEC-001-0108: The customer inputs of 2026-10-27: Dealer Master masters the ship-to stations, jobbers are mastered in SAP MDG and RightAngle, and party 2.0.0, system 1.5.0 and integration 2.4.0 carry them

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-27, for the rulings, the 13 modeling questions and the releases; how each is applied delegated under EPM-DEC-001-0028) |
| Date | 2026-10-27 |
| Questions | What the decision owner's customer inputs of 2026-10-27 change in the `party` and `system` modules, how to model what they add, and which releases carry it |
| Source | Claude Code session of 2026-10-27; `answers-2026-10-27-customer-inputs.md` |

## Context

On 2026-10-27 the decision owner shared four customer inputs, numbered 8 to 11 after the seven of EPM-DEC-001-0067:

- **Input 8:** a customer input describing how a new customer record is created, enriched and consumed across the applications, with 26 data flows.
- **Input 9:** a customer input describing the customer lifecycle and the five system stages of the six core systems, with each system's core and enrich fields.
- **Input 10:** the notes of a meeting with Dealer Master's system expert on Dealer Master's business context and data flows.
- **Input 11:** Dealer Master's architecture flow.

As with the earlier inputs, they are kept out of the repository, and this record states only what the ontology takes from them. Claude recorded the inputs in working notes, and the decision owner settled every point those notes left open (block 1 to block 6 of the answers file). Claude then compared the inputs with `party` 1.4.0 and `system` 1.4.0: 113 items as the ontology holds them, 45 new, and 9 conflicting rows in 6 places, with 13 modeling questions the facts leave open. The comparison and the plan stay with the inputs.

## Decision

**The decision owner's decisions:**

1. **Jobbers are mastered in SAP MDG and RightAngle, not in Dealer Master.** Input 9 says jobbers originate in Dealer Master; inputs 10 and 11 say Dealer Master does not create them. The decision owner chose the documents: Dealer Master holds a replica of each jobber to link it to its stations, and what Dealer Master originates and sends to SAP MDG is the ship-to station, which SAP MDG numbers in the 20000 series.
2. **The direct dealers that sync from SAP MDG into Dealer Master are the replicated six-digit sold-tos.**
3. **SAP MDG and SAP S/4HANA stay two systems.**
4. **TMT is its own system,** as `party` holds it, and TMR is another. The decision owner first answered that the two are one, then, once Claude noted that `party` holds them apart, kept them apart.
5. **The six core systems are as `party` holds them;** MAGIC is not one. Salesforce has 10 core fields. Repeated fields in the inputs count once. Input 8's data flows from RightAngle to the Gravitate customer portal and from SAP MDG to Star are right, and its new-customer-setup description applies to the flow from Terminal Upload to Kittyhawk.
6. **All 13 of Claude's recommendations, and the releases they lead to.** The decision owner aligned with the plan: `party` 2.0.0, a major release, so the decision owner's to approve; `system` 1.5.0 and an `integration` minor, Claude's under the delegation; no `core` change.

**What follows (Claude, under EPM-DEC-001-0028):**

1. **Corrections, which change meaning.** Dealer Master's role and definition no longer say it is built on Salesforce, which is only its intake, or that jobbers start there: it is the Retail Payments Application, the system of record for the ship-to stations. The flow from Dealer Master to SAP MDG carries ship-to stations, not jobbers; the flow from SAP MDG to Dealer Master carries the replicated sold-tos. The sourcing of direct dealers in SAP MDG is reworded to say the sold-tos are mastered in SAP MDG and RightAngle and replicated to Dealer Master. The prospect system stage's definition is corrected the same way. Each keeps its IRI and gains a dated `skos:changeNote` (`party/change-notes.csv`).
2. **One deprecation.** The sourcing that says jobbers originate in Dealer Master is false, so it is deprecated, its triples kept, and replaced by a sourcing that says ship-to stations originate there. A sourcing can now name a site type.
3. **The 13 questions, as recommended:**
   - (Q1) A ship-to stays a site, as EPM-DEC-001-0068 decided. A new property, `party:siteIdentifiedBy`, gives a site its external identifier, and a new identifier type holds the SAP ship-to number in the 20000 series. A new property, `party:systemOfRecordFor`, records Dealer Master as the system of record for sites and for the link from each jobber to its stations.
   - (Q2) Dealer Master's dealer classes 4, 2 and 9 are a code list, each value an exact match of the jobber role, the new sub-jobber role and the station site type. A record stays in the class it was created in.
   - (Q3) A new party role, sub-jobber, and a new relationship type, grouped under.
   - (Q4) The direct-dealer sourcing is reworded, and the direct-dealer customer class (C2) is kept.
   - (Q5) The sold-to role's scope note says it is also called the Capital C customer and is identified by a six-digit SAP customer number.
   - (Q6) The jobber-to-station link uses the existing supplies relationship and `party:atSite`, with Dealer Master as its system of record (Q1).
   - (Q7) TMR keeps its held descriptions; an editorial note gives the inputs' description, and which is right waits for its owner.
   - (Q8) PRM is a system of its own, not MPR. The channel of trade is the class of trade, with MST and DTW as the values of a new class-of-trade list.
   - (Q9) The third-party street price aggregator and the Enterprise Data Lake are systems; external vendors and Marketing Users are not modeled until they are named.
   - (Q10) The Brand Credit Card System gains the alternative label Brand Credit Card Master database.
   - (Q11) The flow from RightAngle to Terminal download is added, and the flow from SAP MDG is kept.
   - (Q12) Tax Image Silo's role says the customer supplies the certificates; no flow starts at the customer.
   - (Q13) Salesforce gains the core field Financial Statement; the held Financial Statement Request Frequency keeps its IRI and meaning.
4. **What else the inputs add:** eight systems in both modules, each defined from the inputs in Claude's words (PRM, the station point-of-sale systems, the street price aggregator, Credit Card Summary, the Enterprise Data Lake, MSMIS, MCS and Terminaling Throughputs), and matched with `skos:exactMatch` from `party` to `system`; 13 data flows, among them Dealer Master's loop with RightAngle, the flows to PRM, and the flows from SAP S/4HANA to Bridger Insight and from RightAngle to TFR, which EPM-DEC-001-0069 left out as uncertain and input 8 shows; six flows that carry more or other than before; four system-stage links (Dealer Master in the prospect and settle stages, Salesforce in the record stage, Polaris in the settle stage); and Bridger Insight's interface name. Inputs 8 to 11 join the inputs a statement can cite.
5. **The releases.** `party` 2.0.0 is major: the corrections and the deprecation change what existing statements mean. `system` 1.5.0 is minor: it adds systems and notes and changes no definition. `integration` 2.4.0 is minor: it puts the inputs of 2026-10-27 in tier 1, as 2.3.0 did for the earlier inputs, and requires the current releases.

## Alternatives considered

- **Deprecate Dealer Master's system concept and mint a new one.** Not chosen: it is the same system, and only its description was wrong. The skill asks for a major release when a definition's meaning changes; a deprecation is for a term replaced by another.
- **Keep both descriptions of where jobbers start.** Not chosen: the decision owner ruled on it (decision 1).
- **Make Channel of Trade a separate attribute.** Not chosen: Q8.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-27-customer-inputs.md`: "MAGIC is not", "both are correct", "10", "dedup", "same system, TMR is correct", "so TMT should be treated separate then", "The docs (Recommended)", "Replicated Sold-Tos (Recommended)", "Keep them separate (Recommended)", "I am aligned with all your recommendation in the input plan." and "Terminal upload to Kittyhawk".

## Evidence

- The decision owner's customer inputs of 2026-10-27 (inputs 8 to 11), kept out of the repository; in `system/sources.csv` as `decision-owner-customer-inputs-2026-10-27`, tier 1 in `authority/source-tiers.csv`.
- EPM-DEC-001-0028, 0067 to 0072, 0099, 0100, 0103, 0104.
- The ontology skill's `release.md`, rules 3 to 5 (classifying a change, the meaning-change test, deprecate never delete), and its SHACL rule 19 (no apostrophe in a shape message).

## Consequences

- `party` 2.0.0, `system` 1.5.0 and `integration` 2.4.0 are released in one pull request, with their changelogs and manifests.
- EPM-DEC-001-0069, 0070, 0072 and 0103 carry dated notes.
- Known gaps: the brands Marathon, ARCO and Tesoro as brand values; Dealer Master's billing customer number, whose relation to the SAP customer number the inputs leave open; and whether Dealer Master's fuel volumes reach the Enterprise Data Lake, which the inputs mark as not confirmed. (2026-10-27, later: the brands gap is closed and the other two stay open; see the amendment below.)

## Amendment, 2026-10-27 (later): the brands

Claude asked the decision owner about the three known gaps. From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-27-customer-inputs.md`: "yes those can be brand values. Others I cannot answer."

- **The brands gap is closed.** Marathon, ARCO and Tesoro are individuals of `party:Brand`. They are instances of a real company, which the module policy puts in `ref-mpc` only (`MODULES.md`, "Three kinds of content"), so they go in `ref-mpc/reference-brands.ttl` on ref-mpc's IRIs, not in `party`. Each cites the customer inputs of 2026-10-27 and MPC's FY2025 Form 10-K, as `business_architecture/reference/mpc/customer-classification-evidence.md` and `mpc-fy2025-10k-fact-sheet.md` record its wording: brand jobbers "operate primarily Marathon® branded outlets"; direct dealers "operate locations mainly under the ARCO® brand"; and the brand jobbers' outlets also carry "Shell, Mobil, Tesoro, others". Who owns or licenses each brand is not stated, because the repository holds no source for it.
- **ref-mpc 1.3.0 carries them.** It is a minor, because it only adds; Claude approves it on the decision owner's answer, delegated under EPM-DEC-001-0028. It requires organization 2.1.0 and party 2.0.0, the current releases.
- **Two gaps stay open with the business.** The decision owner cannot answer them, so they wait for the business: how Dealer Master's billing customer number relates to the SAP customer number, and whether Dealer Master's fuel volumes reach the Enterprise Data Lake. The party 2.0.0 package is left as built, because its review had started; ref-mpc 1.3.0's changelog and this amendment carry the change to its known gaps.
