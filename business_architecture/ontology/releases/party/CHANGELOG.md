# party changelog

## 2.1.0 (2026-10-28)

A minor release: it adds three definitions and one note, and removes no IRI. Approved by Claude under the delegation, which lets it approve the queue's minor releases ("Yes, delegate as described (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md`; EPM-DEC-001-0028, amendment of 2026-10-25, evening). It carries the decision owner's close-out answers of 2026-10-28 (EPM-DEC-001-0099, amendment of 2026-10-28; saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-28-closeout.md`).

- [minor] **Three customer systems defined from their vendors' own published words (Drop Tank's from a 2018 press release, its site being gone)** (close-out point 11). Drop Tank, from the press release in which Points and Drop Tank announced Marathon's MakeItCount rewards program (2018-04-23); its own site now redirects to PDI Technologies. GasBuddy, from GasBuddy's About page. The DTN File Server, from DTN's Refined Fuels page. Each cites its source, in tier 4. What MPC sends each one is not known, and each definition says so.
- [minor] **A note on Polaris** (close-out point 15): the decision owner believes it is bought, an off-the-shelf product; a web search on 2026-10-28 found no liquids-pipeline scheduling product of that name, so the vendor and what it does stay open.
- It still requires core 2.4.0 and system 1.5.0. Its three new sources go into `integration` 2.5.0, which requires this release. `ref-mpc` 1.3.0 still requires party 2.0.0, which stays released as it is.

### Known gaps

- Federal Health has no definition, and what MPC sends Drop Tank, GasBuddy, the DTN File Server and Federal Health is not known; they wait for the customer-data owner (`business-closeout.md`, point 11).
- Polaris's vendor, and what it does, wait for Marathon Pipe Line's scheduling owners (`business-closeout.md`, point 15).
- The drafted descriptions wait for each system's owner to confirm or correct them (`business-closeout.md`, point 16).
- Which description of TMR is right waits for its owner (EPM-DEC-001-0108, question 7).
- Dealer Master's billing customer number, and whether its fuel volumes reach the Enterprise Data Lake, are open (`business-closeout.md`, points 17 and 18; EPM-DEC-001-0108).

## 2.0.0 (2026-10-27)

A major release: the decision owner's customer inputs of 2026-10-27 change what five existing statements mean, and deprecate one. No IRI is removed. Approved by the decision owner, who aligned with the plan that names this major release ("I am aligned with all your recommendation in the input plan.", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-27-customer-inputs.md`; EPM-DEC-001-0108).

- [major] **Dealer Master.** Its role and definition no longer say it is built on Salesforce, which is only its intake, or that jobbers start there. It is the Retail Payments Application, the system of record for the branded dealer network's ship-to stations (`party:systemOfRecordFor` sites and party relationships). The term keeps its IRI and gains a dated `skos:changeNote`.
- [major] **Two flows.** Dealer Master to SAP MDG carries ship-to stations, which SAP MDG numbers in the 20000 series, not jobbers. SAP MDG to Dealer Master carries the replicated six-digit sold-tos, not direct dealers that start in SAP MDG. Each gains a dated change note.
- [major] **The direct dealers' sourcing** in SAP MDG is reworded: sold-tos, direct dealers among them, are mastered in SAP MDG and RightAngle and replicated to Dealer Master.
- [major] **The prospect system stage's definition** is corrected the same way.
- [major] **Deprecated:** `party:sourcing/dealer-master--origin--party-role--jobber`, with its triples kept and `dcterms:isReplacedBy` the new `party:sourcing/dealer-master--origin--site-type--station`. A sourcing can now name a site type.
- [minor] **New terms.** `party:siteIdentifiedBy` and `party:systemOfRecordFor`; the sub-jobber role and the grouped-under relationship type; the SAP ship-to number identifier type; the dealer-class list (4, 2, 9), each value an exact match of the jobber role, the sub-jobber role and the station site type; the class-of-trade list (MST, DTW); scope notes on the sold-to role (also called the Capital C customer, with its six-digit SAP customer number) and on the class-of-trade attribute.
- [minor] **Systems and flows.** Eight customer systems (PRM, the station point-of-sale systems, the street price aggregator, Credit Card Summary, the Enterprise Data Lake, MSMIS, MCS and Terminaling Throughputs), each matching system 1.5.0's (20 of the 50 customer systems now match); 13 flows, among them Dealer Master's loop with RightAngle, the flows to PRM, and SAP S/4HANA to Bridger Insight and RightAngle to TFR; four system-stage links; Salesforce's Financial Statement field; the Brand Credit Card Master database as an alternative label; a note on TMR. Inputs 8 to 11 can be cited.
- [minor] **Four flows say more of what they carry.** Salesforce to Dealer Master (`flow/salesforce--dealer-master`) and Dealer Master to Salesforce (`flow/dealer-master--salesforce`) said only that they carry customer data the inputs did not name; they now name it: the approved operations change form for a new station, a change of owner, or a change of address or name; and mastered station and dealer updates. SAP MDG to RightAngle (`flow/sap-mdg--rightangle`) also carries the ship-to customer records in the 20000 series, and Terminal Upload to Kittyhawk (`flow/terminal-upload--kittyhawk`) carries its mappings for the new customer setup. Each gains a dated change note. Minor under rules 3 and 4 of the `ontology` skill's `release.md`: each text states more of what the flow carries, and every answer the old text gave stays correct, because the old text either named no content or named content the new text keeps.
- [minor] **Tax Image Silo and Bridger Insight say more.** Tax Image Silo's definition and customer role now say that the customers supply its certificates; Bridger Insight's customer role now says that SAP MDG calls it through the interface MDG.BP.I.1001. Each gains a dated change note. Minor under the same rules: what each system holds or does is unchanged, and each text only adds.
- [minor] **Three definitions widened.** `party:evidenceInput` now counts the inputs 8 to 11, and `party:CustomerSourcing` and `party:sourcedConcept` now allow a site type. Each gains a dated change note. Minor under the same rules: each widens what the term covers, and every earlier value stays valid.
- It requires core 2.4.0 and system 1.5.0.

### Known gaps

- Drop Tank, Gas Buddy, DTN File Server and Federal Health have no definition; they wait for the customer-data owner (`business-closeout.md`, point 11).
- The drafted descriptions, the eight new ones among them, wait for each system's owner to confirm or correct them (`business-closeout.md`, point 16).
- Which description of TMR is right waits for its owner (EPM-DEC-001-0108, question 7).
- The brands Marathon, ARCO and Tesoro are not yet brand values (*2026-10-27:* now `party:Brand` individuals in `ref-mpc` 1.3.0, EPM-DEC-001-0108, amendment); Dealer Master's billing customer number, and whether its fuel volumes reach the Enterprise Data Lake, are open (EPM-DEC-001-0108).

## 1.4.0 (2026-10-26)

A minor release: it adds seven matches and rewords one shape message, and removes no IRI. Approved by Claude under the delegation, which lets it approve the queue's minor releases ("Approve (Recommended)", the decision owner's approval of the night brief of 2026-10-26, which says Claude approves the night's minor releases, saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-26-night.md`; EPM-DEC-001-0028; EPM-DEC-001-0104).

- [minor] **Matches.** SAP MDG, Salesforce, MAGIC, Bridger Insight, Information Steward, Sirion and Customer Portal are now the system module's systems of the same name (`skos:exactMatch`), which system 1.4.0 adds with MPC-P11 (EPM-DEC-001-0104). 12 of the 42 customer systems now match a system-module system.
- [minor] **Shapes.** The message "A customer system's definition cites its source." becomes "The definition of a customer system cites its source.", with the same meaning. The `ontology` skill's SHACL rule 19 keeps apostrophes out of `sh:message`, because the neosemantics (n10s) validator writes the message into Cypher unescaped.
- It requires core 2.4.0, the current release (EPM-DEC-001-0105) and system 1.4.0.

### Known gaps

- Drop Tank, Gas Buddy, DTN File Server and Federal Health have no definition; they wait for the customer-data owner (`business-closeout.md`, point 11).
- The drafted descriptions wait for each system's owner to confirm or correct them (`business-closeout.md`, point 16).

## 1.3.0 (2026-10-26)

A minor release: it adds definitions and a source, and removes no IRI. Approved by Claude under the delegation, which lets it approve the queue's minor releases ("Yes, delegate as described (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md`; EPM-DEC-001-0028, amendment of 2026-10-25, evening; EPM-DEC-001-0103).

- [minor] **Definitions.** The 20 internal customer systems gain a `skos:definition` Claude drafted from their customer roles, data flows and attributes, each citing the decision owner's customer inputs and carrying a note saying it was drafted from the repository. 38 of the 42 customer systems are now defined.
- It requires core 2.3.0 and system 1.3.0.

### Known gaps

- Drop Tank, Gas Buddy, DTN File Server and Federal Health have no definition; they wait for the customer-data owner (`business-closeout.md`, point 11).
- The 20 drafted descriptions wait for each system's owner to confirm or correct them (`business-closeout.md`, point 16).

## 1.2.0 (2026-10-25)

A minor release: it adds definitions, sources, a match and top-concept statements, and removes no IRI. Approved by the decision owner ("Approve all three (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-item-g-releases.md`; EPM-DEC-001-0099). The plan they approved did not list the qSKOS top-concept statements; Claude approved those additions under the delegation, which lets it approve the queue's minor releases (EPM-DEC-001-0028, amendment of 2026-10-25, evening).

- [minor] **Definitions.** 18 of the 42 customer systems gain a `skos:definition` in Claude's words, each citing its source: 14 from their vendors' own descriptions, marked as such, Polaris from PHMSA's notice of amendment of 2024-09-26, and KittyHawk, MAGIC and Allocation Manager from the decision owner's descriptions.
- [minor] **Match.** SAP S/4HANA is the system module's SAP (`skos:exactMatch`), the decision owner's answer, so five customer systems now match a system-module system.
- [minor] **Top concepts** (EPM-DEC-001-0098): each code list states its top concepts both ways, and every customer system is a top concept of `party:customer-systems`.
- [minor] **Shapes.** A customer system's definition cites a source.
- It requires core 2.3.0, the current release.


### Known gaps

- 24 customer systems have no definition: Drop Tank, Gas Buddy, DTN File Server and Federal Health wait for the customer-data owner (`business-closeout.md`, point 11), and the other 20 have only their customer role (EPM-DEC-001-0099, item 10).
- Quorum is defined at vendor level; which Quorum product it is stays open (`business-closeout.md`, point 14).
- Polaris: built or bought is not known (`business-closeout.md`, point 15).

## 1.1.0 (2026-10-23)

A minor release: it adds values, a property, links, ranges and shapes, and removes no IRI. Approved by the decision owner with the close-out releases ("Approve all six (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`; EPM-DEC-001-0088, 0092).

- [minor] **Products.** The scheme `party:product` holds 27 values, each a `party:Product`: MPC's six refinery product groups and renewable diesel as top concepts, and the 20 products MPC's FY2025 Form 10-K names under them. Each cites the 10-K; the definitions are Claude's words.
- [minor] **OEO mappings.** 19 SKOS mappings to the Open Energy Ontology v2.14.0 (released 2026-10-08): 3 `skos:closeMatch` and 16 `skos:broadMatch`. No product has an exact match. Nine have none (distillates, NGLs and petrochemicals, No. 1 fuel oil, and the asphalt group with its five products), because OEO has no class for them.
- [minor] **PIDX families.** `party:pidxProductFamily`, a new datatype property, gives 7 products a total of 10 one-letter PIDX product families, as plain identifiers with PIDX's notice. PIDX publishes no IRIs, so nothing is mapped to PIDX codes. The family list is dated 2015, so the business confirms the letters with PIDX (`ontology/business-closeout.md`, point 5).
- [minor] **Onboarding.** The onboarding stage links to CM 1.3.7.1.7 Coordinate Customer Onboarding (MPC-P10.1, EPM-DEC-001-0087).
- [patch] **Projection fixes** (EPM-DEC-001-0036): ranges for `party:evidenceInput` (`xsd:string`), `party:customerRole` and `party:carries` (`rdf:langString`), and shapes stating the cardinality of `party:plays`, `party:mpcClassification`, `party:implements`, `party:governedBy` and `party:feeds`.
- `party:Product`'s definition drops "the module gives products no properties or values", which 1.1.0 makes untrue; a scope note says where its values come from.
- It requires core 2.3.0, the current release.

## 1.0.0 (2026-10-22)

The module's first release, a major. Approved by the decision owner ("You have my permission to release the stable version when you are done.", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-21-release-playbook.md`; EPM-DEC-001-0074). It holds the Customer domain's concepts: the decision owner's conceptual model as fifteen entity classes (seventeen with Person and Organization, the two kinds of party), with party roles as dated nodes, and eighteen code lists (EPM-DEC-001-0068, 0069, 0070); 42 customer systems in five tiers, 35 data flows, 24 customer sourcings and 275 system attributes, four systems matched to the system module (EPM-DEC-001-0069, 0072); and the customer lifecycle, six business stages linked to core processes and five system stages linked to customer systems (EPM-DEC-001-0070). Competency questions 19 to 26 are answerable on it (EPM-DEC-001-0071). Definitions only, never records (EPM-DEC-001-0005): the reference parties MPC and MPLX stay outside the package. It requires core 2.1.0.
