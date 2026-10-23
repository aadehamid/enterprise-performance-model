# EPM-DEC-001-0023: Public ontologies: map to them, do not import them

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-05 |
| Questions | Q34 |
| Source | Grilling session on the handover plan |

## Context

An external search on 2026-10-05 found no public business-architecture or process ontology for downstream oil and gas. Public oil and gas ontologies cover upstream (OSDU, O3PO) or plant equipment (ISO 15926, IDO ISO/FDIS 23726-3). APQC's Downstream Petroleum PCF 7.2.2 is a framework and is already the Step 0 reference. Five sources each cover a piece of the scope: GLEIF Level 2 (accounting consolidation), PIDX (downstream product and terminal codes), the Open Energy Ontology (fuels; CC0 or MIT, BFO-based), IOF Supply Chain (MIT, BFO-based) and FIBO (ownership and control; MIT, large).

## Decision

Keep EPM's own terms and link them to these sources with SKOS mapping properties (`skos:exactMatch`, `skos:closeMatch`) at the step where each fits: GLEIF at Step 5 (MPC and MPLX), PIDX and OEO at Step 7 and the Customer product-line facet, IOF Supply Chain at Step 7 if P01 brings in fuels logistics. Do not import them. Check PIDX's access terms before the Customer work. *2026-10-19:* checked; the standards are royalty free under PIDX's end user licence, for use without modification (EPM-DEC-001-0064). *2026-10-20:* P01 brought fuels logistics in, and IOF Supply Chain is parked until a concept layer for logistics assets or movements, or a consumer that needs IOF terms (EPM-DEC-001-0064). *2026-10-23:* for PIDX, which publishes no IRIs, `party` 1.1.0 records family letters as plain identifiers instead of a SKOS mapping; OEO is mapped with SKOS (EPM-DEC-001-0092).

## Alternatives considered

Import one or more of them; ignore them.

## The decision owner's recorded words

"can you do a external search to see if there are publickly available business architecture/process ontology for Downstream oil and gas that we can adapt in our ontology here." Q34: Not commented on; agreed per the decision owner's rule "If i dont comment on a question, it means I am aligned." Later: "make sure to update the playbook with how we use this publickly aavailable ontology."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with the decision owner). The decision owner answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." They also stated: "If i dont comment on a question, it means I am aligned." A question they did not comment on is therefore recorded as agreed with the recommendation.

## Evidence

https://www.gleif.org/ontology/L2/ ; https://pidx.org/standards/ ; https://github.com/openenergyplatform/ontology ; https://github.com/iofoundry/ontology ; https://github.com/Accenture/OSDU-Ontology ; https://www.iso.org/standard/87560.html
