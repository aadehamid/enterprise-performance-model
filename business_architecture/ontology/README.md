# Ontology — Downstream Process Map

The published home of the downstream process-map ontology build: the
playbook (the method), the worklog (the build record), the acceptance
test (competency questions), and the reproducible build scripts with their outputs.

**Start here.** This README is the single entry point. Three documents, three
roles, and a fourth to read first if you are new (`epm-ontology-guide.html`, below the table):

| File | Role | Read it for |
|------|------|-------------|
| The `ontology` skill's guide (`skills/data/ontology/references/playbook.md`, personal-agent-skills) | **Playbook**: a company-neutral method for building an ontology from scratch | Foundations, Steps 0 to 12, policies (§2), promoting provisional data (§3), standards (§4), soundness checks (§5), working agreements (§6), a worked example in a neutral domain (§7). *2026-10-25:* moved from this folder into the skill, which tests that it names no project's records, companies or paths (EPM-DEC-001-0101) |
| `step4/playbook/ontology-worklog.md` | **Worklog**: the build record | The plan table with current step statuses (§2), the per-step log (§3), the dated decision journal (§4), and the evidence map for the playbook, section by section (§8, *2026-10-23*) |
| `MODULES.md` | **Module guide**: the released modules and how they connect | What each module holds, the three kinds of content, each link between modules with a real example from the releases, and one walk across modules |

**New to the ontology?** Open `epm-ontology-guide.html` in a browser. It explains what the ontology is for, why it is split into modules, what each module holds and why, and follows one pricing measure, the crack spread, through every module, with diagrams and a query you can run. Its figures are a dated snapshot; `MODULES.md` and `scripts/epm_facts.py` stay the current reference.

Check the playbook's §2 Policies and this project's decision records
(`../domain/decisions/`, EPM-DEC-001) before making any modeling choice, and
the worklog's plan table for where the build stands. The worklog was named
`ontology-playbook.md` until 2026-09-30. The maintenance rule was decided on
2026-10-05 (EPM-DEC-001-0002). The playbook was then rewritten as a
company-neutral method, and the amendment EPM-DEC-001-0024 was decided on
2026-10-06: project decisions get an EPM-DEC-001 record and a dated worklog
entry, and the playbook changes only when the method changes.

For current figures (ledger, gate, taxonomy size, Phase 1 rows) and one row's
status, run `python3 scripts/epm_facts.py counts` or `row REL-xxxxx` from the repo
root.

## Modules

The ontology ships as modules, each released and versioned on its own. `core` is the process
map, and most other modules add one kind of thing and link it to core's processes. Three do not:
`market-data` links to `kpi`'s measures, `ref-mpc` holds company facts in the terms of
`organization` and `party`, and `integration` holds rules about the other modules' links.
`MODULES.md` shows each link with an
example quoted from the releases.

| Module | What it is for |
|---|---|
| `core` | The process map: processes as a hierarchy, the approved relationships between them and their evidence |
| `organization` | Roles, RACI assignments, and the control relationship between legal entities |
| `party` | The customer domain: the customer model, customer systems and data flows, and the customer lifecycle |
| `kpi` | What each measure means, never its value, with the population it counts |
| `data-product` | The data-product portfolio: segments, product lines and data products |
| `value-stream` | The value streams, as an overlay of steps that realize core processes |
| `system` | The systems, office tools and working documents the process map names |
| `lane` | The office lanes, and the processes the process map places in them |
| `market-data` | The recipes of market series, such as crack spreads, never their prices |
| `ref-mpc` | The company-specific facts: MPC and MPLX; the only module that is not company-neutral |
| `integration` | Rules across modules: which links certify (placement), which source wins (authority), and what consumers may bind and answer (consumer) |

For versions, what each module requires and triple counts, run
`uv run --with rdflib python scripts/epm_facts.py modules`. It also says what each release was built
from where its manifest records that ("built from (release manifest)"); for the other releases it
shows the source folders the builder packages today ("sources (builder today)"), which a later
change to the builder can move away from what the release was built from. For which processes have a RACI
assignment, a system, a KPI, a lane, a value-stream step or a data product, run
`uv run --with rdflib python scripts/epm_facts.py coverage` (see `--help` for other process sets).
The diagram "EPM ontology: modules and how they connect" draws the modules with an arrow from each to
each module it requires: https://app.eraser.io/workspace/GogQQcK6yNMwogKucbtj.

## Contents

| Path | What |
|------|------|
| The `ontology` skill's guide | **Playbook** (the method, normative): policies, method, standards, soundness, working agreements, a neutral worked example; in personal-agent-skills since 2026-10-25 (EPM-DEC-001-0101) |
| `step4/playbook/ontology-worklog.md` | **Worklog** (the build record): plan table and statuses, step log, decision journal, the playbook's evidence map |
| `MODULES.md` | **Module guide**: each released module, how the modules connect, with examples quoted from the releases (tested by `scripts/test_modules_guide.py`) |
| `epm-ontology-guide.html` | **Ontology guide**, a standalone page for a person: why modules, each module and why it exists, the module map, and the crack-spread measure traced through every module, with diagrams |
| `step4/` | Step 4 working area: verb-predicate mapping, evidence gate, canonical facts, correction backlog (see `step4/README.md`) |
| `step4/evidence-discipline.md` | The approved Step 4 evidence discipline text, moved word for word from the playbook on 2026-10-05 |
| `lpg-projection/` | The superseded v2.2 copy of the ontology-to-LPG projection guideline, kept as evidence of what Step 12 followed (EPM-DEC-001-0020, 0021). Since 2026-10-23 the method is the `ontology-to-lpg` skill in personal-agent-skills, at `da75164`; the folder's README points to it (EPM-DEC-001-0095) |
| `../domain/decisions/` | Project decision records (EPM-DEC-001) |
| `competency-questions.md` | The 44-question acceptance baseline, tested by the Step 11 regression in `regression/` |
| `projection/` | Step 12: the pipeline that projects the ontology into Neo4j, its manifest and its last report (EPM-DEC-001-0036) |
| `validation/` | Step 9 shapes run against the released modules: controlled values (EPM-DEC-001-0035) |
| `provenance/` | The Step 6 definition-to-run pattern: the shapes a consumer's run must meet, an example run and tests (EPM-DEC-001-0034) |
| `ref-mpc/` | The Step 5 reference instances for MPC: MPC, MPLX, MPC's control of MPLX, segments and refineries, from the FY2025 10-K (EPM-DEC-001-0033); and MPC and MPLX as parties in the `party` module's terms, moved from `party/` on 2026-10-22 (EPM-DEC-001-0071, 0075); released as 1.2.0 with the parties (EPM-DEC-001-0080); and, since 2026-10-27, MPC's brands Marathon, ARCO and Tesoro as `party:Brand` individuals, released as 1.3.0 (EPM-DEC-001-0108, amendment of 2026-10-27) |
| `kpi/` | The Step 7 kpi module: 41 measure definitions classified by kind (EPM-DEC-001-0042), the measure-kind code list, planning personas and process links (EPM-DEC-001-0043); released as 1.0.0 (`releases/kpi/1.0.0/`), approved by the decision owner, and 1.0.1, a patch naming the measure list's source (VCO DSV); 1.1.0 (`releases/kpi/1.1.0/`), a minor carrying the measure populations, with the measure shape closed (EPM-DEC-001-0079) |
| `party/` | The Steps 5 to 7 `party` module, which owns the Customer domain's concepts: the decision owner's conceptual model of Customer as fifteen entity classes (17 with Person and Organization), party roles as dated nodes, twelve code lists including 14 roles and 14 customer classes with MPC's C1 to C8, and SHACL (EPM-DEC-001-0067, 0068); the customer's 42 systems, 35 data flows and 275 Create and Enrich attributes, with four more code lists for them (EPM-DEC-001-0069); the customer lifecycle, linked to core processes and systems (EPM-DEC-001-0070); released as 1.0.0 on 2026-10-22 (EPM-DEC-001-0074) *2026-10-26:* released as 1.1.0 (EPM-DEC-001-0092), 1.2.0 (EPM-DEC-001-0099) and 1.3.0, which defines 38 of its 42 customer systems (EPM-DEC-001-0103); 1.4.0 matches 12 of them to the system module and rewords its one shape message with an apostrophe (EPM-DEC-001-0104); *2026-10-27:* 2.0.0, a major, takes the customer inputs of that day: Dealer Master masters the ship-to stations and jobbers are mastered in SAP MDG and RightAngle, with the sub-jobber role, the dealer classes, 50 customer systems (20 matched to the system module), 48 flows and one deprecated sourcing (EPM-DEC-001-0108). |
| `population/` | What eight MPC-defined measures include and exclude, from MPC's wording (EPM-DEC-001-0062); released in `kpi` 1.1.0 (EPM-DEC-001-0079) |
| `consumer/` | Rules for consumers: the catalog binding and what an agent may answer and must refuse (EPM-DEC-001-0061); released in `integration` 1.0.0 (EPM-DEC-001-0078) |
| `apqc/` | The full APQC Downstream Petroleum PCF 7.2.2 element list (2,012 elements), a reference for Q11 (EPM-DEC-001-0060); a reference file, in no package (EPM-DEC-001-0078) |
| `authority/` | Step 9: the evidence tier of every cited source, so the best-tier source wins when two disagree (EPM-DEC-001-0059); released in `integration` 1.0.0 (EPM-DEC-001-0078) |
| `placement/` | The placement kinds: which placing properties certify (only producing a data product) and which give context (EPM-DEC-001-0058); released in `integration` 1.0.0 (EPM-DEC-001-0078) |
| `market-data/` | The Step 7 market-data module (*2026-10-26:* 1.1.0 adds 2 series, 40 market prices and the views' series enumerations, EPM-DEC-001-0100): 13 series of the crack-spreads measure, from MPC Economics' definition first (six regional ex-RIN series, the NYMEX 3-2-1, two MPC-weighted blends), then MPC's FY2025 Form 10-K, Item 7, and CME Group, with their benchmarks and regions (EPM-DEC-001-0057, 0066); released as 1.0.0 on 2026-10-22 (EPM-DEC-001-0077) |
| `lane/` | The Step 7 lane module: the four office lanes and the seven processes the process map places in them (EPM-DEC-001-0056); released as 1.0.0 on 2026-10-22 (EPM-DEC-001-0077) |
| `system/` | The Step 7 system module (*2026-10-26:* 34 systems since 1.2.0, with MIPS and Databricks; 1.1.0 and 1.2.0 define 18, EPM-DEC-001-0099, 0100; 1.3.0 defines 14 more from the repository, 32 of 34, EPM-DEC-001-0103; 1.4.0 adds MPC-P11's seven systems and 21 links, 39 of 41 defined, EPM-DEC-001-0104; 1.5.0 adds eight systems the process map does not name, from the customer inputs of 2026-10-27, 47 of 49 defined, EPM-DEC-001-0108): the systems come from the process map's system strings (32 in 1.0.0), merged on spelling through a register, with their kind and the processes they support (EPM-DEC-001-0055); released as 1.0.0 on 2026-10-22 (EPM-DEC-001-0077) |
| `value-stream/` | The Step 7 value-stream module: the Commercial Hydrocarbon Lifecycle and Order to Cash, their stages, capabilities and 58 value-stream processes, which realize core processes, produce and consume data products and carry the MPC-P09 measure links (EPM-DEC-001-0054); released as 1.0.0 on 2026-10-22 (EPM-DEC-001-0077) |
| `data-product/` | The Step 7 data-product module: the portfolio's 3 segments, 19 lines and 48 data products as definitions (49 since Customer Master, 2026-10-23, EPM-DEC-001-0091), 33 of them parked for lack of a description, mapped to DCAT, not imported (EPM-DEC-001-0053); released as 1.0.0 on 2026-10-22 (EPM-DEC-001-0077) |
| `organization/` | The Step 5 organization module: the RACI assignment and control vocabulary, its SHACL shapes and tests (EPM-DEC-001-0030), the role register with the roles built from it (EPM-DEC-001-0031), and the RACI assignments with their ledger (EPM-DEC-001-0032) |
| `regression/` | The Step 11 SPARQL regression: one query per tested part of a question, each question's status, and the runner `check.sh` calls |
| `release/`, `releases/` | Release builders and packages: `core` 1.0.0 (EPM-DEC-001-0029), organization 1.0.0 and ref-mpc 1.0.0 (EPM-DEC-001-0037), core 2.0.0 (EPM-DEC-001-0038), core 2.1.0 (EPM-DEC-001-0044), core 2.2.0 (EPM-DEC-001-0076), organization 2.0.0 and ref-mpc 1.1.0 (EPM-DEC-001-0045), and kpi 1.0.0 and 1.0.1 (EPM-DEC-001-0043), and party 1.0.0 (EPM-DEC-001-0074), and data-product, value-stream, system, lane and market-data 1.0.0 (EPM-DEC-001-0077), and integration 1.0.0 (EPM-DEC-001-0078), and kpi 1.1.0 (EPM-DEC-001-0079), and ref-mpc 1.2.0 (EPM-DEC-001-0080), and core 2.3.0 (EPM-DEC-001-0089), and core 2.4.0 (EPM-DEC-001-0105), and value-stream 1.1.0 (EPM-DEC-001-0090), and data-product 1.1.0 (EPM-DEC-001-0091), and party 1.1.0 (EPM-DEC-001-0092), and kpi 1.1.1 (EPM-DEC-001-0093), and integration 2.0.0 (EPM-DEC-001-0094); system 1.1.0, party 1.2.0 and integration 2.1.0 (EPM-DEC-001-0099, in the item G pull request); kpi 1.2.0, market-data 1.1.0, data-product 1.2.0, system 1.2.0 and integration 2.2.0 (EPM-DEC-001-0100, in the item F pull request); system 1.3.0, party 1.3.0 and integration 2.3.0 (EPM-DEC-001-0103, in the item G descriptions pull request); system 1.4.0 and party 1.4.0 (EPM-DEC-001-0104, in the MPC-P11 pull request); party 2.0.0, system 1.5.0, integration 2.4.0 and ref-mpc 1.3.0 (EPM-DEC-001-0108, in the customer inputs pull request); `releases/catalog.ttl`, one DCAT catalog of every release, built by `release/build_catalog.py` (EPM-DEC-001-0082) |
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
| `build/output/step3c-authored-definitions.json` | 14 human-authored L1–L3 definitions (approved by the decision owner 2026-09-18) merged into the taxonomy |
| `build/output/step3c-definition-authoring-workbook.xlsx` | Semantic-intake workbook (6 sheets, 503 rows). Step 3c closed 2026-09-21: 498/503 approved (see the working record's decision log) |
| `build/scripts/step3c-workbook-validate.py` | Mechanical review gate. Synced v2026-09-19b (`ptc-closed` is blocked-only) |
| `step3c-reviewer-instructions.md` | Locked reviewer guide (v2026-09-19b) |
| `step3c-parked-tree-changes.md` | Structural moves accepted in review and deferred to a later JSON/TTL pass |

## Standing conventions

- **Source of truth:** `../business_process/downstream_process_map.json`.
  The ontology models those processes; APQC is a consistency reference.
- **URI base:** `https://w3id.org/lsc/ontology/`, a placeholder: not registered with w3id.org and not hosted, because the domain may change (EPM-DEC-001-0039).
- **License:** this folder's contents are proprietary, all rights reserved.
  APQC-sourced material is used under the APQC/IBM license terms —
  attribution travels with every distribution (see `../reference/README.md`).
- **HTML pages:** each reading document here (this README, `MODULES.md`, the module READMEs and the others
  `scripts/build_docs_html.py` lists) has an `.html` page beside it, generated from the Markdown, and the
  decision records are one page, `../domain/decisions/decisions.html`. Edit the Markdown, then run
  `python3 scripts/build_docs_html.py` from the repo root; `scripts/check.sh` fails while a page is stale.

## Status

**The ontology is closed** (EPM-DEC-001-0096, 2026-10-23). *2026-10-26:* **the ontology is done** (EPM-DEC-001-0107): MPC-P11 and MPC-P12 are accepted and released, the deferred qSKOS fixes are released, and what stays open is the business's points in `business-closeout.md`, the next releases' small fixes, the items parked for other reasons, and usage and integration, a separate, later task. Every item that
waited on the decision owner is answered (EPM-DEC-001-0086 to 0095), the six
close-out releases are built and tagged, the projection's list of release
gaps is empty, and the competency regression is green. The worklog's plan
table (`step4/playbook/ontology-worklog.md` §2) is authoritative for step
status: Steps 0 to 12 are done or stand as recorded, each with its listed
exceptions (EPM-DEC-001-0083). Phase E closed on 2026-10-22.

- **Releases:** 47 packages under `releases/`, listed in
  `releases/catalog.ttl` (EPM-DEC-001-0082). The newest of each module:
  `core` 2.4.0 (EPM-DEC-001-0105), organization 2.2.0 (EPM-DEC-001-0045, amendment of 2026-10-28), ref-mpc 1.3.0 (EPM-DEC-001-0108), kpi 1.2.0 (EPM-DEC-001-0100), party 2.0.0
  (EPM-DEC-001-0108),
  value-stream 1.2.0 (EPM-DEC-001-0106), data-product 1.2.0
  (EPM-DEC-001-0100), system 1.5.0 (EPM-DEC-001-0108), lane 1.1.0 (EPM-DEC-001-0106), market-data 1.1.0 (EPM-DEC-001-0100), and
  integration 2.4.0 (EPM-DEC-001-0108). *2026-10-25:* system 1.1.0, party 1.2.0 and integration
  2.1.0 carry the systems' definitions from item G and the qSKOS top-concept fixes (EPM-DEC-001-0098); item F's
  five releases carry the pricing measures' bindings, prices, platform tables and lineage (EPM-DEC-001-0097, 0100). *2026-10-26:* system 1.3.0, party 1.3.0 and integration 2.3.0 carry the internal systems' descriptions, drafted from the repository (EPM-DEC-001-0103). Lane 1.1.0, organization 2.1.0 and value-stream 1.2.0 carry the deferred qSKOS top-concept fixes (EPM-DEC-001-0098, item 5; EPM-DEC-001-0106). core 2.4.0 renames the 25 processes that shared seven names (MPC-P12) and carries core's qSKOS fixes (EPM-DEC-001-0098, 0105). System 1.4.0 and party 1.4.0 carry MPC-P11, which the decision owner accepted, and party's shape message without an apostrophe (EPM-DEC-001-0104). *2026-10-27:* party 2.0.0 (a major the decision owner approved), system 1.5.0 and integration 2.4.0 carry the decision owner's customer inputs of that day (EPM-DEC-001-0108). ref-mpc 1.3.0 adds MPC's brands Marathon, ARCO and Tesoro, which the decision owner confirmed as brand values later that day (EPM-DEC-001-0108, amendment of 2026-10-27). *2026-10-28:* organization 2.2.0 carries the decision owner's close-out answers: PSM expanded as Process Safety Management, and the Crude RFC reading and Business Planning and Analysis's definition confirmed (EPM-DEC-001-0045, amendment of 2026-10-28).
- **Checks:** every package conforms to its own shapes (EPM-DEC-001-0081);
  the competency regression has 43 questions answerable, 0 partial,
  0 waiting and 1 parked (Q17, EPM-DEC-001-0086); the Neo4j projection of every released package passes,
  with no rule gap listed (16 before value-stream 1.1.0, 14 before party
  1.1.0, 6 before kpi 1.1.1, 5 before integration 2.0.0)
  (EPM-DEC-001-0036).
- **Held rows:** 462, each held with its reason: 51 Phase 1 rows and 411
  outside Phase 1 (`python3 scripts/epm_facts.py counts`). PTC-001-B is
  held by design.
- **Decided by the decision owner on 2026-10-23:** Q17 is parked until
  the ontology is first shared with business consumers (EPM-DEC-001-0086);
  MPC-P10 is accepted (EPM-DEC-001-0087); product values from MPC's FY2025
  Form 10-K, and six releases that carry these and close the 16 projection
  gaps, are approved (EPM-DEC-001-0088). `core` 2.3.0, `value-stream` 1.1.0,
  `data-product` 1.1.0, `party` 1.1.0, `kpi` 1.1.1 and `integration` 2.0.0
  are released (EPM-DEC-001-0089 to 0094). The projection guideline moved
  into the `ontology-to-lpg` skill (EPM-DEC-001-0095).
  Phase F, the `ontology` skill, was approved on 2026-10-22
  (EPM-DEC-001-0084) and is done: personal-agent-skills pull request #45,
  merged on 2026-10-23.
- **Open after closure, with the business:** every point only the business
  can settle is in `business-closeout.md`, with the record each answer goes
  to: Q17, Market Data's accountable group, the four codes and TID Nbr, the
  product list, Forecaster, Crude RFC, PSM, four working role definitions
  and 33 measure populations. They are settled when the ontology is first
  shared with business consumers. *2026-10-28:* the decision owner worked
  through the package: points 3 and 4 are closed, point 5 is narrowed to the
  PIDX family letters, and points 17 and 18 (Dealer Master) are added
  (EPM-DEC-001-0086, amendment of 2026-10-28). Organization 2.2.0 closes
  points 7 (Crude RFC) and 8 (PSM) and settles one of point 9's four
  definitions (EPM-DEC-001-0045, amendment of 2026-10-28).
- **Open after closure, apart from the ontology:** the store tests are a
  separate, later task: load the ontology into Apache Jena and into a
  Databricks Delta triple table, project it to a local Neo4j and to Aura, then
  rebuild both from the Databricks store and check that no data is lost;
  OntoBricks follows, to link Unity Catalog metric views to the processes
  (EPM-DEC-001-0096).
