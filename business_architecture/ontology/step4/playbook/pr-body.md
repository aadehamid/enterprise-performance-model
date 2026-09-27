# DO NOT MERGE — awaiting Hamid's review

## What this PR does

Documents how we do versioning in the ontology playbook, per the Step 4
decisions Q1 (namespaces/identity) and Q3 (first formal version 1.0.0).

## Change inventory

`business_architecture/ontology/ontology-playbook.md` only:

1. **Decision log** — two new entries (2026-09-22):
   - *Ontology identity*: ontology IRI `https://w3id.org/lsc/ontology/core`,
     version IRI pattern `…/core/<version>`, the explicit `owl:Ontology`
     header contents, stable unversioned term IRIs.
   - *First formal version 1.0.0*: Step 4 ships `core` 1.0.0 — first
     release with governed properties and the first version header;
     baseline for Step 5/6 and later modules.
2. **Appendix B** — two new sections:
   - *Ontology identity and header*: the canonical Turtle `owl:Ontology`
     block plus the three rules (stable ontology IRI, per-release
     version IRI, never version a term IRI).
   - *Version history*: pre-1.0.0 unversioned working builds; 1.0.0 as
     the Step 4 baseline.

## Deliberately unchanged

- The existing SemVer mechanics (major/minor/patch definitions,
  meaning-change test, deprecation protocol, APQC version changes, who
  approves a release) — all still accurate; the new material references
  them rather than restating them.
- The 12-step plan table and all other decision-log entries.

## How to review

Read the two new Appendix B sections and the two decision-log bullets.
Check: (a) the Turtle header block is valid and complete; (b) the
version-history claims match what we decided (pre-1.0.0 builds shipped
no `owl:versionInfo`; 1.0.0 is Step 4).
