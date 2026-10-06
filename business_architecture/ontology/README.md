# Ontology — Downstream Process Map

The published home of the downstream process-map ontology build: the
playbook (the method), the worklog (the build record), the acceptance
test (competency questions), and the reproducible build scripts with their outputs.

**Start here.** This README is the single entry point. Two documents, two
roles:

| File | Role | Read it for |
|------|------|-------------|
| `ontology-playbook.md` | **Playbook**: a company-neutral method for building an ontology from scratch | Foundations, Steps 0 to 12, policies (§2), promoting provisional data (§3), standards (§4), soundness checks (§5), working agreements (§6), worked example (§7) |
| `step4/playbook/ontology-worklog.md` | **Worklog**: the build record | The plan table with current step statuses (§2), the per-step log (§3), and the dated decision journal (§4) |

Check the playbook's §2 Policies and this project's decision records
(`../domain/decisions/`, EPM-DEC-001) before making any modeling choice, and
the worklog's plan table for where the build stands. The worklog was named
`ontology-playbook.md` until 2026-09-30. The maintenance rule was decided on
2026-10-05 (EPM-DEC-001-0002). The playbook was then rewritten as a
company-neutral method, and the amendment EPM-DEC-001-0024 was decided on
2026-10-06: project decisions get an EPM-DEC-001 record and a dated worklog
entry, and the playbook changes only when the method changes.

## Contents

| Path | What |
|------|------|
| `ontology-playbook.md` | **Playbook** (the method, normative): policies, method, standards, soundness, working agreements, worked example |
| `step4/playbook/ontology-worklog.md` | **Worklog** (the build record): plan table and statuses, step log, decision journal |
| `step4/` | Step 4 working area: verb-predicate mapping, evidence gate, canonical facts, correction backlog (see `step4/README.md`) |
| `step4/evidence-discipline.md` | The approved Step 4 evidence discipline text, moved word for word from the playbook on 2026-10-05 |
| `lpg-projection/` | Pinned snapshot of the ontology-to-LPG projection guideline used in Step 12 (EPM-DEC-001-0020, 0021) |
| `../domain/decisions/` | Project decision records (EPM-DEC-001) |
| `competency-questions.md` | The 44-question acceptance baseline — doubles as the Step 11 SPARQL regression tests |
| `apqc-scope-decisions.md` | One-at-a-time in/out-of-scope calls for the seven APQC gap candidates |
| `apqc-crosscheck-report.md` | Repo process map vs APQC Downstream PCF v7.2.2 consistency check (2026-09-17) |
| `build/step2-identity-map.py` | Reproducible script: URI slug for every one of the 680 nodes |
| `build/apqc_crosscheck.py` | Reproducible script: cited-ID check + coverage scores vs the vendored v7.2.2 workbook |
| `build/output/step2-identity-map.json` | 680 rows: uri, slug, level, name, skos_notation, parent_slug, minted flag |
| `build/output/step2-identity-report.md` | Identity normalization summary |
| `build/output/apqc_crosscheck_results.json` | Raw cross-check scores |
| `build/step3-skos-taxonomy.py` | Reproducible script: 680 `skos:Concept` taxonomy with URIs, labels, definitions, scope notes, APQC + validator + human-author provenance (`--adoptions`, `--authored`) |
| `build/output/step3-taxonomy.ttl` | The SKOS taxonomy. Measured on `main` 37ab0a0 (2026-09-30): 14,496 triples, 683 `skos:Concept`, 681 `skos:broader` links, 680 concepts with `skos:definition`. Still carries the provisional `intake:` annotations until the `core` 1.0.0 release |
| `build/output/step3-taxonomy-report.md` | Step 3 build summary |
| `build/step3b-definition-triangulation.py` | Reproducible script: APQC candidate matching + EIA/web triangulation over the 503 definition gaps |
| `build/step3b-merge-validations.py` | Merge automated + human validation records into final adoption decisions |
| `build/output/step3b-definition-review.csv` | All 503 definition-gap review rows: 1 adopted, 10 rejected at the human gate, 14 human-authored in Step 3c; L4–L6 authoring continues in the intake workbook |
| `build/output/step3b-adoptions.json` | The single adopted definition (internal marketing communications strategy) with provenance |
| `build/output/step3b-web-input.json` | 131 strong-match rows sent for web validation |
| `build/output/step3b-web-validations.json` | 111 automated web-validation records |
| `build/output/step3b-web-validations-manual.json` | 11 human-vetted manual validation records |
| `build/output/step3c-authored-definitions.json` | 14 human-authored L1–L3 definitions (approved by Hamid 2026-09-18) merged into the taxonomy |
| `build/output/step3c-definition-authoring-workbook.xlsx` | Semantic-intake workbook (6 sheets, 503 rows). Step 3c closed 2026-09-21: 498/503 approved (see the working record's decision log) |
| `build/scripts/step3c-workbook-validate.py` | Mechanical review gate. Synced v2026-09-19b (`ptc-closed` is blocked-only) |
| `step3c-reviewer-instructions.md` | Locked reviewer guide (v2026-09-19b) |
| `step3c-parked-tree-changes.md` | Structural moves accepted in review and deferred to a later JSON/TTL pass |

## Standing conventions

- **Source of truth:** `../business_process/downstream_process_map.json`.
  The ontology models those processes; APQC is a consistency reference.
- **URI base:** `https://w3id.org/lsc/ontology/` (redirect-backed; register `w3id.org/lsc`).
- **License:** this folder's contents are proprietary, all rights reserved.
  APQC-sourced material is used under the APQC/IBM license terms —
  attribution travels with every distribution (see `../reference/README.md`).

## Status

The worklog's plan table (`step4/playbook/ontology-worklog.md` §2)
is authoritative for step status. As of 2026-09-30: Steps 0–3c and 8 are
done; Step 3d is complete with explicit open exceptions; **Step 4 is
PROMOTED** (2026-09-30), which approved the relationship-layer review,
not a release. Next is Phase 1 (source-workbook corrections), then the
`core` 1.0.0 release (EPM-DEC-001-0013). Steps 5 to 7 and 9 to 12 are
planned.
