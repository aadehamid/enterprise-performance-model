# The ref-mpc module (Step 5)

Public reference facts about Marathon Petroleum Corporation, kept apart from the company-neutral modules (EPM-DEC-001-0015). Its namespace is `https://w3id.org/lsc/ontology/modules/ref-mpc/`. The design is EPM-DEC-001-0033.

- `ref-mpc.ttl`: MPC and MPLX as legal entities, MPC's control of MPLX (`orgm:ControlRelationship`, about 64 percent, as of 2025-12-31), MPC's three reportable segments, and its 13 refineries. Every fact comes from MPC's FY2025 Form 10-K (MPC-S01 in `../../reference/mpc/source-register.md`) and holds as of 2025-12-31.
- `shapes.ttl`: every instance has one English name, a described source and an as-of date; a segment belongs to one company and a refinery to one owner.
- `test_ref_mpc.py`: SHACL, the facts against the filing, and broken instances that must fail. `scripts/check.sh` runs it.

The module uses the organization module's terms and W3C ORG terms by IRI and defines none of its own. Refinery capacity is not here yet: it is a dated quantity, which waits for the measure pattern in Step 7.
