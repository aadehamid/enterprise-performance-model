# Ontology — Downstream Process Map

The published home of the downstream process-map ontology build: the
working record (playbook), the acceptance test (competency questions),
and the reproducible build scripts with their outputs.

**Start here:** `ontology-playbook.md` — the plan, the decision at every
step, and *why* each standard was chosen. Check the decision log (§4)
before making any modeling choice.

## Contents

| Path | What |
|------|------|
| `ontology-playbook.md` | Living handover document: 12-step plan, step log, decision log, standards rationale, versioning detail |
| `competency-questions.md` | The 44-question acceptance baseline — doubles as the Step 11 SPARQL regression tests |
| `apqc-scope-decisions.md` | One-at-a-time in/out-of-scope calls for the seven APQC gap candidates |
| `apqc-crosscheck-report.md` | Repo process map vs APQC Downstream PCF v7.2.2 consistency check (2026-09-17) |
| `build/step2-identity-map.py` | Reproducible script: URI slug for every one of the 680 nodes |
| `build/apqc_crosscheck.py` | The APQC cross-check script (historical run; local paths as executed) |
| `build/output/step2-identity-map.json` | 680 rows: uri, slug, level, name, skos_notation, parent_slug, minted flag |
| `build/output/step2-identity-report.md` | Identity normalization summary |
| `build/output/apqc_crosscheck_results.json` | Raw cross-check scores |

## Standing conventions

- **Source of truth:** `../business_process/downstream_process_map.json`.
  The ontology models those processes; APQC is a consistency reference.
- **URI base:** `https://w3id.org/lsc/ontology/` (redirect-backed; register `w3id.org/lsc`).
- **License:** this folder's contents are proprietary, all rights reserved.
  APQC-sourced material is used under the APQC/IBM license terms —
  attribution travels with every distribution (see `../reference/README.md`).

## Status

Steps 0 (APQC alignment), 1 (foundations), 2 (identity normalization), and
8 (APQC scope review) are complete. See the playbook's plan table.
