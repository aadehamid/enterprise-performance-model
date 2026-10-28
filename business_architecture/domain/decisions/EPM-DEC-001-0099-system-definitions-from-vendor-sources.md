# EPM-DEC-001-0099: The systems' definitions come from their vendors' own descriptions, marked as such; the decision owner's eleven answers on item G

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-24 and 2026-10-25, the identifications and the eleven answers; how each is applied delegated under EPM-DEC-001-0028) |
| Date | 2026-10-25 |
| Questions | Item G: what is each system the process map and the customer inputs name? Which tier does a vendor's description of its product take? Which systems are the same in the `system` and `party` modules? |
| Source | Claude Code sessions of 2026-10-24 and 2026-10-25; `answers-2026-10-24-systems.md`, `answers-2026-10-25-item-g.md` |

## Context

`system` 1.0.0 names 32 systems and defines none: each carries a note that its definition waits for its owners (EPM-DEC-001-0055). `party` 1.1.0 names 42 customer systems, each with a one-line customer role from the decision owner's inputs and no definition (EPM-DEC-001-0069). On 2026-10-24 the decision owner asked to define the off-the-shelf systems from public sources: "Most of these systems are off the shlef and public. We can search for the definitions in the public." The same day they identified APS and six other systems and approved four descriptions. On 2026-10-25 Claude asked five numbered questions; question 3 put the item G draft's eleven recommendations, and the decision owner answered it "3. I will go with your recommendation".

## Decision

The decision owner's answers, item by item (the questions are in the context comment of `answers-2026-10-25-item-g.md`):

1. **A vendor's description of its own product is evidence tier 4, industry sources** (EPM-DEC-001-0059). It says what the product is in general and nothing about how MPC uses it, so it never outranks MPC's sources or the process map.
2. **The process map's "SAP" is SAP S/4HANA,** the same system as `party`'s SAP S/4HANA, linked by `skos:exactMatch`.
3. **XPIMS and PPIMS are Aspen PIMS planning models:** XPIMS multi-plant and multi-period, PPIMS multi-period. Each is defined as an Aspen PIMS model, not as a separate product.
4. **PI is the AVEVA PI System.**
5. **Hyperion is Oracle Hyperion Planning.** Claude's recommendation called this a guess between Planning, Financial Management and Essbase; the system keeps a note saying so.
6. **TopDay and VALT are MPC-built** until the decision owner says otherwise. Neither has a definition yet.
7. **Polaris is a Marathon Pipeline LLC scheduling system,** built or bought unknown, from PHMSA's notice of amendment of 2024-09-26.
8. **Drop Tank, Gas Buddy, DTN File Server and Federal Health** go to the customer-data owner as one question (`business-closeout.md`, point 11). None is defined.
9. **Terminal Upload's direct flow to KittyHawk stays,** because the decision owner's input shows it; KittyHawk's note says its customer data comes from RightAngle and Terminal Upload sends it cross-reference IDs.
10. **Claude drafts a description of each internal system** from the repository (its process links or its customer role) for one approval round with the decision owner, as was done for DPO.
11. **The customer processes' system links go to a process-map proposal** (MPC-P11), after the decision owner checks the weak ones.

The identifications of 2026-10-24 (`answers-2026-10-24-systems.md`): APS is Aspen Petroleum Scheduler; CargoTracker, MAGIC, Allocation Manager and DPO are MPC-built, and DPO's name is "Distribution Planning Optimizer"; Quorum is Quorum Software, product not named; OneSource is Thomson Reuters ONESOURCE; KittyHawk is an MPC in-house application used by the Commercial organization, fed from RightAngle. The decision owner approved the descriptions of CargoTracker, MAGIC, Allocation Manager and DPO.

**What follows (Claude, under EPM-DEC-001-0028):**

1. **Each definition is Claude's, in plain words, from the cited sources.** A definition from a vendor's page says "By the vendor's description, …", so a reader does not take it for MPC's description. The passages are quoted whole in `business_architecture/reference/vendors/README.md`, with URL, version where stated, page date where shown, and the date read (2026-10-25; *2026-10-26:* SAP S/4HANA's passage now comes from SAP's conversion guide, read that day).
2. **`system` defines 15 of its 32 systems.** From vendor sources: Aspen Petroleum Scheduler, XPIMS, PPIMS, RightAngle, Profisee, SAP S/4HANA, Oracle Hyperion Planning, AVEVA PI System and the four Microsoft tools. From the decision owner's descriptions: Distribution Planning Optimizer, KittyHawk and CargoTracker. Each definition cites its source beside the process map (`dcterms:source`). The other 17 keep their note; TopDay's and VALT's notes say they are MPC-built.
3. **Full forms become preferred labels,** with the process map's abbreviation as an alternative label (the `ontology` skill's identity rule on abbreviations): Distribution Planning Optimizer (DPO), Aspen Petroleum Scheduler (APS), SAP S/4HANA (SAP), Oracle Hyperion Planning (Hyperion), AVEVA PI System (PI). The IRIs do not change.
4. **`party` defines 18 of its 42 customer systems:** 14 from vendor sources (SAP MDG, SAP S/4HANA, Salesforce, RightAngle, Profisee, Bridger Insight, EMK3, FlowCal, Gravitate, Information Steward, Lenel Onguard, Sirion, OneSource, Quorum), Polaris from the PHMSA notice, and KittyHawk, MAGIC and Allocation Manager from the decision owner. Five customer systems now match a `system`-module system, SAP S/4HANA joining the four of EPM-DEC-001-0072.
5. **The shapes change.** A `system`-module system either has a definition and a source beside the process map, or a note saying why it has none (`sh:xone`). A `party` customer system's definition cites a source.
6. **The 27 sources join the `authority` module:** the two answers files in tier 1, and 25 vendor and regulator pages in tier 4.
7. **The new definitions ship in `system` 1.1.0, `party` 1.2.0 and `integration` 2.1.0,** which the decision owner approved: "Approve all three (Recommended)" (`answers-2026-10-25-item-g-releases.md`). The plan they saw did not list the qSKOS top-concept statements EPM-DEC-001-0098 assigns to these modules; Claude approved those additions under the delegation, which lets it approve the queue's minor releases (EPM-DEC-001-0028, amendment of 2026-10-25, evening). `party` 1.2.0 also requires `system` 1.1.0, whose systems its five matches name; the earlier `party` packages name four of them without requiring `system`. Every source is typed `dcterms:BibliographicResource`. The released packages do not change.
8. **Still to do:** the internal systems' descriptions for one approval round (item 10), and proposal MPC-P11 (item 11). Each comes in its own pull request. *2026-10-26:* both are done: the descriptions in EPM-DEC-001-0103, and MPC-P11, accepted and applied, in EPM-DEC-001-0104.
9. **The four approved descriptions are used word for word.** The drafts of CargoTracker, MAGIC, Allocation Manager and DPO the decision owner approved on 2026-10-24 are in the context comment of `answers-2026-10-24-systems.md`, as the store-tests handoff recorded them; each definition is its draft with a capital first letter. KittyHawk's definition is Claude's rewording of the decision owner's own description, quoted in full below.

## Amendment, 2026-10-28: Drop Tank, GasBuddy and DTN defined from their own public pages; a note on Polaris

Claude walked the decision owner through the business close-out package on 2026-10-28 (EPM-DEC-001-0086, amendment of 2026-10-28). Points 11 and 15 are this record's.

**The decision owner's answers:**

1. **Point 11:** "Define 3, rest open (Recommended)". The option read: Drop Tank, GasBuddy and DTN defined from their public pages in party's next minor; Federal Health and the data sent stay open.
2. **Point 15:** "I think this is an off the shelf system that offers this service". It is a belief, not a confirmation.

**What follows (Claude, under EPM-DEC-001-0028):**

- **Three definitions, released in `party` 2.1.0.** Each is in Claude's words, marked as the source's description, and cites its source in tier 4, as item G's vendor definitions do. Each passage is quoted whole in `business_architecture/reference/vendors/README.md`.
  - **GasBuddy**, from GasBuddy's About page (https://www.gasbuddy.com/about, read 2026-10-28).
  - **DTN File Server**, from DTN's Refined Fuels page (https://www.dtn.com/refined-fuels/, read 2026-10-28). The page describes DTN, not the file server, so the definition says the server carries data exchanged with DTN.
  - **Drop Tank**, from the press release in which Points and Drop Tank announced Marathon's MakeItCount rewards program (GlobeNewswire, 2018-04-23, read 2026-10-28). Drop Tank's own site, https://www.drop-tank.com/, redirected to PDI Technologies' home page on 2026-10-28, and no page of PDI's read that day describes Drop Tank, so the release's "About Drop Tank" paragraph is the company's own description.
  - Each definition says that what MPC sends the system is not known. Federal Health stays undefined. Both wait for the customer-data owner (`business-closeout.md`, point 11).
- **A note on Polaris, in `party` 2.1.0.** It records the decision owner's belief that Polaris is bought. A web search on 2026-10-28 for liquids-pipeline scheduling software found Emerson's SchedulingManager, myQuorum and Pandell's Latitude, and no product named Polaris. Its vendor and what it does stay open (`business-closeout.md`, point 15).
- **`integration` 2.5.0** carries the three new sources' tiers, since the source tiers ship in it. It requires the current releases, `organization` 2.2.0 and `party` 2.1.0 among them. Both releases are minors Claude approved under the delegation.

## Alternatives considered

- **Quote the vendor's passage as the definition.** Not chosen: vendor pages are marketing ("the most trusted", "the world's leading"), and a definition should say what the thing is in plain words. The passage stays in the reference file.
- **Define each system as MPC uses it.** Not chosen: how MPC uses a system comes from the process map's links, not from a vendor (the decision owner's item G instruction, as the handoff recorded it).

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-24-systems.md`: "can we add this to the plan. Most of these systems are off the shlef and public. We can search for the definitions in the public."; "APS is https://www.aspentech.com/en/products/msc/aspen-petroleum-scheduler"; "cargoTracker and MAGIC.. consider them MPC built. Allocation Manager is home grown/mpc built. Let us assume it is the same Quorum as the one that came back from the research. DPO and OneSource .. let assume it is the one from the research I shared."; "DPO.. let us change that to MPC built. And give it the name "Distribution Planning Optimizer""; "yes, record all three as drafted"; "yes, record that description for DPO"; "where I say assumed. Consider those the answer. you can scrape the word "assume""; "KittyHawk is an MPC in-house application. It gets all of its data from RightAngle. Almost a replica of RightAngle. Kittyhawk is used by the Commercial orgainization".

Saved in `answers-2026-10-25-item-g.md`: "3. I will go with your recommendation". Saved in `answers-2026-10-25-item-g-releases.md`: "Approve all three (Recommended)".

For the amendment of 2026-10-28, from `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-28-closeout.md`: "Define 3, rest open (Recommended)" and "I think this is an off the shelf system that offers this service".

## Evidence

- `business_architecture/reference/vendors/README.md`: each vendor passage, quoted whole, and the PHMSA passage on Polaris.
- `ontology/system/definitions.csv`, `ontology/system/sources.csv`, `ontology/party/definitions.csv`; `ontology/authority/source-tiers.csv`.
- `system` 1.0.0 and `party` 1.1.0, for what the modules held before.

## Consequences

- `system/test_systems.py` and `party/test_party_systems.py` pin the defined systems, the labels, the five matches and the new shape rules.
- `business-closeout.md` points 11 to 15 list what the business must still say about these systems. *2026-10-28:* point 11 is narrowed to Federal Health and what MPC sends the four systems, and point 15 carries the decision owner's belief that Polaris is bought (amendment of 2026-10-28 above).
