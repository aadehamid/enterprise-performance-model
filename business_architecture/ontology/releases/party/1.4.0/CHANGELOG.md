# party changelog

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
