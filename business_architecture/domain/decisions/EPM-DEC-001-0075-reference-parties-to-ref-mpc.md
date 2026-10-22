# EPM-DEC-001-0075: The reference parties MPC and MPLX move into the ref-mpc module

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-22, for the move; how it is done delegated under EPM-DEC-001-0028) |
| Date | 2026-10-22 |
| Questions | Whether MPC and MPLX, described as parties in `party/reference-parties.ttl`, move into a reference module (EPM-DEC-001-0074, Consequences) |
| Source | Claude Code session of 2026-10-22; `answers-2026-10-22-morning.md` |

## Context

EPM-DEC-001-0071 described MPC and MPLX in the `party` module's terms, so that competency questions section VII's done-when has real organisations. The file sat in `party/`. When `party` 1.0.0 was released, EPM-DEC-001-0074 kept it out of the package, because the playbook's module policy puts reference instances of real companies in their own module, and left the move open for the decision owner. The session 7 morning summary asked whether to move them into `ref-mpc`. The decision owner answered on 2026-10-22, and agreed that one pull request records the answers and a later one moves the parties ("Aligned with your proposal").

## Decision

**The decision owner's answer:** "Yes they should split into their own refrence module"

**What follows (Claude, under EPM-DEC-001-0028):**

1. **The file moves to `ref-mpc/reference-parties.ttl`.** `ref-mpc` already holds MPC and MPLX as legal entities (EPM-DEC-001-0033), and the parties already use its IRIs for the two companies.
2. **The roles and the agreement take ref-mpc's namespace.** The four party roles and the services agreement move from `https://w3id.org/lsc/ontology/modules/party/reference/` to `https://w3id.org/lsc/ontology/modules/ref-mpc/party/`, so every node the file describes is in the module that owns it. No released package holds the old IRIs: `party` 1.0.0 left them out (EPM-DEC-001-0074, item 3), so the change breaks no consumer.
3. **The content is unchanged otherwise:** the same roles, dates, agreement type and source, each sourced to MPLX's FY2025 Form 10-K.
4. **The tests move with the file.** `ref-mpc/test_ref_mpc.py` reads the parties both ways, checks the dates and the source, checks every described node is in ref-mpc's namespace, checks the file left `party/`, and validates the parties against the party module's shapes. The regression loads the file from its new place.
5. **No `party` release is needed:** the `party` 1.0.0 package does not hold the file, and no file in it changes.
6. **The move ships in `ref-mpc` 1.2.0,** a minor release: it adds instances and changes no released IRI (`references/versioning.md` in the ontology skill). The release follows in its own pull request under the approved release plan, and requires `party` 1.0.0 beside `organization` 2.0.0.

## Alternatives considered

- **Keep the old IRIs under the party namespace.** Not chosen: ref-mpc would then describe nodes in another module's namespace, and the old IRIs were never released.
- **A new reference module for parties only.** Not chosen: `ref-mpc` is the reference module for MPC and MPLX, and already holds both companies.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`: "Yes they should split into their own refrence module". On how to record it: "Aligned with your proposal".

## Evidence

- EPM-DEC-001-0033 (the ref-mpc module), 0071 (the real parties), 0074 (party 1.0.0 keeps them out).
- `business_architecture/reference/mpc/mplx-fy2025-10k-fact-sheet.md`, section 3.

## Consequences

- `party/README.md`, `ref-mpc/README.md`, `party/examples.ttl`, `release/build_module.py` and `release/test_build_module.py` point to the new place; EPM-DEC-001-0071 and 0074 carry dated notes.
- `ref-mpc` 1.2.0 is pending, in its own pull request.
