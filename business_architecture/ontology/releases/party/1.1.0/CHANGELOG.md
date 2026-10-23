# party changelog

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
