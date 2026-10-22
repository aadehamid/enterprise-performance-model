# The ref-mpc module (Step 5)

Public reference facts about Marathon Petroleum Corporation, kept apart from the company-neutral modules (EPM-DEC-001-0015). Its namespace is `https://w3id.org/lsc/ontology/modules/ref-mpc/`. The design is EPM-DEC-001-0033.

- `ref-mpc.ttl`: MPC and MPLX as legal entities, MPC's control of MPLX (`orgm:ControlRelationship`, about 64 percent, as of 2025-12-31), MPC's three reportable segments, and its 13 refineries. Every fact comes from MPC's FY2025 Form 10-K (MPC-S01 in `../../reference/mpc/source-register.md`) and holds as of 2025-12-31. MPC and MPLX also carry their LEIs from GLEIF (EPM-DEC-001-0023).
- `reference-parties.ttl`: MPC and MPLX in the `party` module's terms, on this module's IRIs: MPC holds the Throughput Holder and Payer roles and MPLX the Carrier and Vendor roles under MPLX's fee-based services agreements, each held since 2012-10-31 (the first agreements' date) and sourced to MPLX's FY2025 Form 10-K. They are the real organisations of competency questions section VII's done-when (EPM-DEC-001-0071). Moved here from `../party/` on 2026-10-22 (EPM-DEC-001-0075); the regression loads the file. The party module's shapes check it.
- `shapes.ttl`: every organization, segment and refinery has one English name, a described source and an as-of date; a segment belongs to one company and a refinery to one owner. The control relationship is checked by the organization module's shapes (`../organization/shapes.ttl`), which `test_ref_mpc.py` loads with these.
- `test_ref_mpc.py`: SHACL, the facts against the filing, broken instances that must fail, and MPC and MPLX as parties read both ways, held since 2012-10-31, citing MPLX's 10-K and conforming to the party module's shapes. `scripts/check.sh` runs it.

The module uses the organization module's terms, the party module's terms and W3C ORG terms by IRI and defines none of its own. Refinery capacity is not here yet: it is a dated quantity, which waits for the measure pattern in Step 7.

Released as 1.0.0 and 1.1.0 (EPM-DEC-001-0037, 0045), and as 1.2.0 on 2026-10-22, which adds `reference-parties.ttl` and requires organization 2.0.0 and party 1.0.0 (EPM-DEC-001-0080): `../releases/ref-mpc/1.2.0/`.
