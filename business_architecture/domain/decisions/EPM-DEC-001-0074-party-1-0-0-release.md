# EPM-DEC-001-0074: Release `party` 1.0.0

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-21, for the release; the package's contents delegated under EPM-DEC-001-0028) |
| Date | 2026-10-22 |
| Questions | The `party` module's first release, which needs the decision owner's approval (module policy, 2026-09-18; EPM-DEC-001-0067, What follows, item 13) |
| Source | Claude Code session of 2026-10-21 (session 7); `answers-2026-10-21-release-playbook.md` |

## Context

The `party` module holds the Customer domain's concepts (EPM-DEC-001-0068), the customer's systems, data flow and attributes (EPM-DEC-001-0069, 0072), and the customer lifecycle (EPM-DEC-001-0070). Competency questions 19 to 26 are answerable on it (EPM-DEC-001-0071). A module's first release is a major, and a major needs the decision owner's approval. The decision owner gave it for when the Customer domain work was done; all five pull requests of EPM-DEC-001-0067's plan and the open-points answers (#327, #329 to #333) are merged.

## Decision

**The decision owner's approval:** "You have my permission to release the stable version when you are done."

**What follows (Claude, under EPM-DEC-001-0028):**

1. **"The stable version" is `party` 1.0.0**, the module's first release, issued 2026-10-22. No `core` release was pending: the process-map changes of MPC-P10 wait for the decision owner, so no `core` version is cut.
2. **The package holds** `vocabulary.ttl`, `code-lists.ttl`, `systems.ttl` and `lifecycle.ttl` (3,405 triples), with the module's shapes, a DCAT record, a changelog and a manifest, built by `release/build_module.py` as the other modules' packages are. It requires core 2.1.0, and the shapes conform with core 2.1.0 loaded.
3. **The reference parties stay outside the package.** `party/reference-parties.ttl` describes MPC and MPLX, real companies; the playbook's module policy puts reference instances in their own module. The regression keeps loading the file. Moving it into `ref-mpc` would be a `ref-mpc` release, which needs its own approval. *2026-10-22:* the decision owner split them into their own reference module; the file is now `ref-mpc/reference-parties.ttl` (EPM-DEC-001-0075).
4. **The examples stay outside too:** `examples.ttl` holds invented test fixtures.

## Alternatives considered

- **Include the reference parties in the package.** Not chosen: it would put instances of real companies in a domain module, against the module policy.
- **Release a candidate (1.0.0-rc.1) first.** Not chosen: the decision owner approved the stable version.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-21-release-playbook.md`: "You have my permission to release the stable version when you are done."

## Evidence

- `business_architecture/ontology/release/build_module.py` and `test_build_module.py`.
- EPM-DEC-001-0037 (module packages), 0067 to 0072.

## Consequences

- `releases/party/1.0.0/` is written; `scripts/check.sh` fails unless it equals a fresh build.
- The records and READMEs that said the module is not released carry dated notes.
- Open for the decision owner: whether to move the reference parties into `ref-mpc` in its next release. *2026-10-22:* answered: they move, in `ref-mpc` 1.2.0 (EPM-DEC-001-0075).
