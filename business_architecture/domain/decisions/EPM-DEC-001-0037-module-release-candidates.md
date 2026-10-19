# EPM-DEC-001-0037: Step 10: release candidates for the organization and ref-mpc modules

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028); the decision owner approved the 1.0.0 releases, 2026-10-13 |
| Date | 2026-10-13 |
| Questions | Step 10: how the modules after `core` are packaged for publication, and what waits for the decision owner |
| Source | Claude Code session, 2026-10-13, under the decision owner's extension of the delegation to Steps 5 to 12 (EPM-DEC-001-0028, amended in #252) |

## Context

EPM-DEC-001-0018 decides Step 10: w3id permanent IRIs, a DCAT catalog of each release and its files, and a release package shaped to EPM-ARCH-REL-001's manifest. `core` 1.0.0 shipped that way (EPM-DEC-001-0029): its package holds the module's Turtle and JSON-LD, its shapes, a DCAT record, a changelog and a manifest with each file's SHA-256. The module policy (2026-09-18) gives minor and patch releases to the module owner and majors to the decision owner. A module's first release, 1.0.0, is a major.

When this was decided, the organization and `ref-mpc` modules existed on `main` with no release.

## Decision

1. **One builder for the other modules.** `business_architecture/ontology/release/build_module.py` builds a module's package in the shape of the `core` 1.0.0 package: `<module>.ttl`, `<module>.jsonld`, `shapes.ttl`, `catalog.ttl`, `CHANGELOG.md` and `manifest.json`. It validates the module with its shapes, with `core` 1.0.0 loaded for the concepts the module refers to.
2. **Candidates first, then releases on the decision owner's approval.** Both modules were first built as `1.0.0-rc.1`, with no issued date, as `core` was before the decision owner approved it. The decision owner approved both on 2026-10-13, so both are now 1.0.0, issued 2026-10-13 (below). EPM-ARCH-REL-001 asks a release to record an immutable commit; the merge commit's tags record it, as `core-v1.0.0` did.
3. **Dependencies name versions that exist.** Organization 1.0.0 requires `core` 1.0.0. `ref-mpc` 1.0.0 requires organization 1.0.0. While both were candidates, the `ref-mpc` candidate required the organization candidate, `1.0.0-rc.1`, because organization 1.0.0 did not exist yet. Each requirement is a `dcterms:requires` link on the ontology header and an entry in the manifest; no module imports another.
4. **The packages stay current.** `scripts/check.sh` runs the builder with `--verify` for both modules, and `test_build_module.py` checks the packages.

## The decision owner's approval, 2026-10-13

The decision owner approved both modules as 1.0.0 (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-13-session2.md`): "aprove now". Organization 1.0.0 and ref-mpc 1.0.0 are the candidates with the issued and modified dates set to 2026-10-13 and the stage removed; ref-mpc now requires organization 1.0.0. The packages are in `releases/organization/1.0.0/` and `releases/ref-mpc/1.0.0/`, and each manifest names where their approval is recorded. When this merges, the merge commit gets the tags `organization-v1.0.0` and `ref-mpc-v1.0.0`.

## For the decision owner

Step 10 is done when the catalog resolves and the release can be retrieved. Three things are theirs:
1. **Approve organization 1.0.0 and `ref-mpc` 1.0.0** (each a major). Done: approved on 2026-10-13 (above).
2. **Register `w3id.org/lsc`.** The IRIs resolve only after a redirect is registered with w3id, a public, outside action. *2026-10-14:* The decision owner decided not to host the namespace and to keep it as a placeholder; under the delegation, it is not registered either (EPM-DEC-001-0039).
3. **Choose where the files are hosted and under which license.** *2026-10-14:* not hosted (the decision owner, EPM-DEC-001-0039); the licence is still open. The ontology README says the folder is proprietary, all rights reserved; a public catalog needs a decision on what is published. *2026-10-18:* proprietary (the decision owner, EPM-DEC-001-0041). Item 3 is closed.

## Alternatives considered

- **Issue 1.0.0 now under the delegation.** Rejected: the module policy reserves majors for the decision owner.
- **Extend `build_core.py` to the other modules.** Rejected: its steps (intake migration, canonical facts, conservation ledger) are specific to `core`.
- **Let the `ref-mpc` candidate require organization 1.0.0.** Rejected while organization 1.0.0 did not exist; the released `ref-mpc` 1.0.0 requires it.

## The decision owner's recorded words

The decision owner extended the delegation in the Claude Code session on 2026-10-13 (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`): "yes, extend the delegation to steps 5 to 12." The decision owner did not make the choices above themselves. Claude made them under that delegation, and the decision owner can reverse any of them.

The decision owner approved the 1.0.0 releases themselves in the same session (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-13-session2.md`): "aprove now".

## Evidence

EPM-DEC-001-0018, 0029, 0030 to 0033; the module policy of 2026-09-18 in `step4/playbook/ontology-worklog.md`; `releases/core/1.0.0/` (catalog and manifest); `architecture/EPM-ARCH-REL-001_EPM_Consumer_Release_Contract.md`.

## Consequences

- `releases/organization/1.0.0/` and `releases/ref-mpc/1.0.0/` hold the releases; git history keeps the 1.0.0-rc.1 candidates.
- A change to either module fails `scripts/check.sh` until its package is rebuilt.
