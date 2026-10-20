# EPM-DEC-001-0059: Source authority: each cited source in one of five evidence tiers; the best tier wins

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Competency question 44 (which definition is authoritative when two sources disagree, and how that is marked), partial since the regression started; Phase E of EPM-DEC-001-0052 (Step 9) |
| Source | Claude Code session, 2026-10-19 |

## Context

The release and the modules cite 60 sources through `dcterms:source`. 528 concepts cite more than one. `AGENTS.md` sets the evidence order: the process authority in `business_architecture/` takes precedence; then MPC's filings and public materials; then U.S. refining peers' SEC filings; then downstream-specific industry sources; generic frameworks are support only. The ontology's README says APQC is "a consistency reference". The decision owner's instruction of 2026-10-19 repeats the MPC-first order.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **An `authority` module** gives each cited source an `auth:evidenceTier` from a five-tier code list, each tier with a rank.
2. **Tier 1, the process authority:** the process map, the value streams, the data product portfolio, the office lanes, the Step 3c definition workbook's approved rows, the decision owner's measure list, and the source author's recorded answers on GitHub.
3. **Tier 2, Marathon Petroleum:** the MPC evidence files in `reference/mpc/`.
4. **Tier 3, peers:** the evidence files in `reference/downstream-peers/` that rest on peers' 10-Ks.
5. **Tier 4, downstream industry and regulatory sources:** standards bodies, exchanges, regulators and agencies (API, the Energy Institute, CCRO, CME Group, CFTC, EIA, EPA, FASB, FERC, FTC, IRS, ISDA, NAESB, OFAC, OSHA and the others in `source-tiers.csv`).
6. **Tier 5, generic frameworks:** APQC's PCF, ASCM's CSCP manual, academic papers and the SKOS reference.
7. **The best tier wins.** Where two sources of one concept disagree, a source in the lower-ranked tier is authoritative. Question 44 is answerable: 520 of the 528 multi-source concepts rest on the process authority and 8 on MPC.

## Alternatives considered

- **Mark one source per concept by hand.** Not chosen: the tier follows from the evidence order the repository already sets, for every concept at once.
- **Put the tier in `core`.** Not chosen: the sources span every module, and a `core` release would be needed for each new source.

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The evidence order: "Use Marathon petroleum comapnies as the stand in company as primary and sue all other downstream oil and gas peer as secondary sources of refrecnes." (`answers-2026-10-19-completion-search.md`). The decision owner can reverse any item.

## Evidence

`AGENTS.md`, Working rules; `business_architecture/ontology/README.md`, Standing conventions; `business_architecture/ontology/authority/source-tiers.csv`.

## Consequences

- The regression stands at 27 answerable, 4 partial and 13 waiting.
- A new source needs a row in `source-tiers.csv`; the test fails until it has one.
