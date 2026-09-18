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
| `build/apqc_crosscheck.py` | Reproducible script: cited-ID check + coverage scores vs the vendored v7.2.2 workbook |
| `build/output/step2-identity-map.json` | 680 rows: uri, slug, level, name, skos_notation, parent_slug, minted flag |
| `build/output/step2-identity-report.md` | Identity normalization summary |
| `build/output/apqc_crosscheck_results.json` | Raw cross-check scores |
| `build/step3-skos-taxonomy.py` | Reproducible script: 680 `skos:Concept` taxonomy with URIs, labels, definitions, scope notes, APQC + validator + human-author provenance (`--adoptions`, `--authored`) |
| `build/output/step3-taxonomy.ttl` | The initial SKOS taxonomy: 680 concepts, 678 broader links, 192 definitions (177 repo + 1 triangulated + 14 human-authored), 3,660 triples |
| `build/output/step3-taxonomy-report.md` | Step 3 build summary |
| `build/step3b-definition-triangulation.py` | Reproducible script: APQC candidate matching + EIA/web triangulation over the 503 definition gaps |
| `build/step3b-merge-validations.py` | Merge automated + human validation records into final adoption decisions |
| `build/output/step3b-definition-review.csv` | All 503 definition-gap review rows: 1 adopted, 10 rejected at the human gate, 14 human-authored in Step 3c; 488 gaps remain (all L4–L6) |
| `build/output/step3b-adoptions.json` | The single adopted definition (internal marketing communications strategy) with provenance |
| `build/output/step3b-web-input.json` | 131 strong-match rows sent for web validation |
| `build/output/step3b-web-validations.json` | 111 automated web-validation records |
| `build/output/step3b-web-validations-manual.json` | 11 human-vetted manual validation records |
| `build/output/step3c-authored-definitions.json` | 14 human-authored definitions (approved by Hamid 2026-09-18) with scope notes, parked concepts, and planned children |

## Standing conventions

- **Source of truth:** `../business_process/downstream_process_map.json`.
  The ontology models those processes; APQC is a consistency reference.
- **URI base:** `https://w3id.org/lsc/ontology/` (redirect-backed; register `w3id.org/lsc`).
- **License:** this folder's contents are proprietary, all rights reserved.
  APQC-sourced material is used under the APQC/IBM license terms —
  attribution travels with every distribution (see `../reference/README.md`).

## Status

Steps 0 (APQC alignment), 1 (foundations), 2 (identity normalization),
3 (SKOS taxonomy), 3b (definition triangulation), 3c (human definition
authoring), and 8 (APQC scope review) are complete. See the playbook's
plan table.
