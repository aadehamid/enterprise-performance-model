# integration changelog

## 2.1.0 (2026-10-25)

A minor release: it adds sources and top-concept statements, and removes no IRI. Approved by the decision owner ("Approve all three (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-item-g-releases.md`; EPM-DEC-001-0099).

- [minor] **Source tiers.** 27 sources join `authority`: the decision owner's two answers files on the systems in tier 1, and 25 vendor and regulator pages in tier 4, industry and regulatory sources (92 sources in all).
- [minor] **Top concepts** (EPM-DEC-001-0098): the members of `auth:EvidenceTier`, `con:RuleKind` and `plc:PlacementKind` are top concepts, stated both ways.
- It requires the current releases, system 1.1.0 and party 1.2.0 among them.

## 2.0.0 (2026-10-23)

A major: the five projection fixes, and no IRI changes. `con:reliesOn`'s definition narrows from property or class to property, which makes it a major. Approved by the decision owner: "Major: integration 2.0.0 (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md` (EPM-DEC-001-0088, 0094).

- [minor] `plc:placementKind` takes `rdfs:range skos:Concept`, and a shape states it: exactly one for each of the twelve placing properties (`placement/shapes.ttl`).
- [major] `con:reliesOn` takes `rdfs:range rdf:Property`, and its definition says property, not property or class. Every value was a property except the process concept CM 1.3.7.1.1 on the rule "Name the customer without a role", which moves to `rdfs:seeAlso` on that rule.
- [minor] Shapes state the cardinality of `auth:rank` (exactly one per tier, from 1) and `auth:evidenceTier` (exactly one per source) (`authority/shapes.ttl`).
- The package's `shapes.ttl` holds the consumer, placement and authority shapes together.
- It requires the current releases: core 2.3.0, organization 2.0.0, kpi 1.1.1, data-product 1.1.0, value-stream 1.1.0, system 1.0.0, lane 1.0.0, market-data 1.0.0 and party 1.1.0.

## 1.0.0 (2026-10-22)

The package's first release, a major. Approved by the decision owner with the release plan ("release plan approved", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`; EPM-DEC-001-0078). It holds three vocabularies, each in its own namespace: `placement` (the certification and context kinds of the placing properties, EPM-DEC-001-0058), `authority` (the five evidence tiers and the tier of each of the 65 cited sources, EPM-DEC-001-0059) and `consumer` (the catalog binding and the seven may-answer and five must-refuse rules, EPM-DEC-001-0061), with the consumer shapes. The population statements (EPM-DEC-001-0062) ship in `kpi` 1.1.0, and the APQC element list (EPM-DEC-001-0060) stays a reference file. It requires core 2.2.0, organization 2.0.0, kpi 1.0.1, data-product, value-stream, system, lane and market-data 1.0.0, and party 1.0.0, whose terms it names.
