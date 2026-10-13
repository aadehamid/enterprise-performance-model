# EPM-DEC-001-0033: The ref-mpc module: MPC, MPLX, the control relationship, segments and refineries

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-13 |
| Questions | Step 5, slice 4: which MPC reference instances the `ref-mpc` module holds, and how each fact carries its source and as-of date |
| Source | Claude Code session, 2026-10-13, under Hamid's extension of the delegation to Steps 5 to 12 (EPM-DEC-001-0028, amended in #252) |

## Context

EPM-DEC-001-0015 puts MPC reference instances in a separate `ref-mpc` module, makes MPLX an Organization that MPC controls through a relation separate from `org:subOrganizationOf`, and keeps the Midstream segment as a separate concept. EPM-DEC-001-0030 defines `orgm:ControlRelationship`. The playbook's Step 5 asks for a source and an as-of date on each fact.

MPC's FY2025 Form 10-K (MPC-S01, accession 0001510295-26-000009, filed 2026-02-26) states:
- "As of December 31, 2025, we owned the general partner of MPLX and approximately 64 percent of the outstanding MPLX common units."
- "Our operations consist of three reportable operating segments: Refining & Marketing, Midstream and Renewable Diesel."
- MPC owns and operates refineries in the Gulf Coast, Mid-Continent and West Coast regions, with 2,986 mbpcd of crude oil refining capacity. Item 2 names 13 refineries (`business_architecture/reference/mpc/mpc-fy2025-10k-fact-sheet.md`, section 3).


## Decision

`business_architecture/ontology/ref-mpc/ref-mpc.ttl` holds:

1. **MPC and MPLX** as `org:FormalOrganization`.
2. **MPC's control of MPLX** as one `orgm:ControlRelationship`: share 0.64, as of 2025-12-31, source MPC-S01. A note quotes the filing's "approximately", because the share is rounded.
3. **The three reportable segments** as `org:OrganizationalUnit`, each `org:unitOf` MPC. Midstream's scope note says MPLX's operations roll up into it.
4. **The 13 refineries** as `org:Site`, each `org:siteOf` MPC, with its location and region in a note.
5. **Source and date on every instance.** Each instance cites `src:mpc-s01` (`dcterms:source`) and states `dcterms:date` 2025-12-31, the date its facts held. The source node carries its title, accession number and filing date.
6. **GLEIF by identifier (EPM-DEC-001-0023).** MPC's LEI is 3BNYRYQHD39K4LCKQF12 and MPLX's is 5493000CZJ19CK4P3G36, each as `org:identifier` with an `rdfs:seeAlso` link to its GLEIF API record. GLEIF lists MPLX's registration as lapsed, and records no accounting-consolidation parent for it (reporting exception NO_KNOWN_PERSON). So the control relationship has no GLEIF Level 2 relationship to map to. MPLX's note says so.
7. **No terms of its own.** The module uses the organization module and W3C ORG by IRI.

Left out for now:
- **Refinery capacity.** It is a dated quantity with a unit, which waits for the measure pattern of Step 7.
- **Renewable diesel facilities, terminals and joint ventures.** Nothing in Steps 5 to 7 asks for them yet.

## Alternatives considered

- **MPLX as `org:subOrganizationOf` MPC.** Rejected by EPM-DEC-001-0015.
- **Only the Midstream segment,** the one EPM-DEC-001-0015 names. Rejected: the FY2025 10-K names three, and Refining & Marketing holds the refineries.
- **An as-of date on the source only.** Rejected: the playbook asks for one on each fact, and a later filing may restate some facts but not others.

## Hamid's recorded words

Hamid extended the delegation in the Claude Code session on 2026-10-13 (saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-steps-5-12.md`): "yes, extend the delegation to steps 5 to 12." Hamid did not make the choices above himself. Claude made them under that delegation, and Hamid can reverse any of them.

## Evidence

MPC-S01, the FY2025 Form 10-K (https://www.sec.gov/Archives/edgar/data/1510295/000151029526000009/mpc-20251231.htm), checked for the MPLX and segment sentences on 2026-10-13; the GLEIF API (`https://api.gleif.org/api/v1/lei-records`), queried on 2026-10-13 for both legal names and for MPLX's parent relationships; `business_architecture/reference/mpc/mpc-fy2025-10k-fact-sheet.md` for the refinery list; EPM-DEC-001-0015, 0020, 0030.

## Consequences

- `scripts/check.sh` runs `ref-mpc/test_ref_mpc.py`.
- A later filing adds or restates facts with its own source and date. Earlier facts stay as they were.
