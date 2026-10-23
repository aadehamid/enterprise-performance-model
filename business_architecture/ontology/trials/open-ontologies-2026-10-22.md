<!-- Copied from the trial's report of 2026-10-22. The raw outputs named under Files stayed outside the repository, in a temporary folder, as the trial plan said: not in the repo or CI during the trial (EPM-DEC-001-0085). The adoption rule quoted below is Claude's trial plan, which the decision owner approved on 2026-10-21 ("yes, add the Phase D trial to the queue", answers-2026-10-21-open-ontologies-trial.md); the words of the rule are Claude's. -->

# open-ontologies trial on core 2.1.0 and 2.2.0 (2026-10-22)

The tool found nothing that `scripts/check.sh` and the regression miss, so I recommend that we do not adopt it. Its `plan` from core 2.1.0 to 2.2.0 reports the same 217 added and 7 removed triples that the repo's tests already assert. Its OWL coherence check passes core 2.2.0 and the union of the newest module packages, but those graphs give it little to check: 5 named classes in core and 47 in the union. The trial plan, which the decision owner approved on 2026-10-21, said to adopt the tool only if its report finds something check.sh and the regression miss. The trial does not meet that rule.

Nothing in any git repository changed. The tool was built and run in `/private/tmp/claude-501/open-ontologies-trial/`, and every input was a copy. `git status` in the EPM repo was clean after the runs.

## What was run

The tool is `fabio-rovai/open-ontologies`, cloned into `src/` at commit `93295305201c7374988217fd6fa609de0fd643ee`. The commit date is 2026-10-17T22:00:05+01:00. `Cargo.toml` gives package version 2.1.0. The licence file `src/LICENSE` is the MIT License, "Copyright (c) 2026 Fabio Rovai".

I built it from source at that commit with `cargo +1.95.0-aarch64-apple-darwin build --release --target-dir ../target-arm64`. The build took 86 s of wall time and peaked at about 3.0 GB of resident memory (`out/build-arm64.log`). The binary's SHA-256 is `15daa911444cf8089d2d1c633798d41e70bd0e4a8c6468c2dbae0513702b1c0f`. I installed no toolchain. The machine already had the arm64 toolchain 1.95.0. The first build attempt used the default toolchain, `stable-x86_64-apple-darwin`, and failed after 231 s. The `oxrocksdb-sys` build script could not load `libclang.dylib` because that library is arm64 and the toolchain is x86_64 (`out/build.log`).

As a fallback I also downloaded the v2.0.1 release binary `open-ontologies-aarch64-apple-darwin` into `release-bin/`. Its SHA-256 matched the digest that GitHub publishes (`268ca690...4c552b`). I did not use it, because the source build at HEAD worked.

The commands come from the tool's own docs. `README.md` shows `plan` run as `load base.ttl` then `plan proposed.ttl` in `open-ontologies batch`. `docs/lifecycle.md` says what `plan` reports. `docs/assets/hqdm/PROVENANCE.md` shows the coherence check as `load` then `reason owl-dl`, which runs the SHIQ tableaux reasoner described in `docs/reasoning.md`. Each run used its own data directory under `data/`, the `--no-connect` flag and `/usr/bin/time -l`. The wrapper script is `scripts/run.sh` and the batch files are in `batches/`.

| Run | Batch file | Output | Wall time | Peak memory |
|---|---|---|---|---|
| Syntax check of both cores | `batches/validate.txt` | `out/validate.json` | 0.05 s | 45 MB |
| `plan` 2.1.0 to 2.2.0 | `batches/plan.txt` | `out/plan.json` | 0.57 s | 189 MB |
| `diff` 2.1.0 to 2.2.0 | `batches/diff.txt` | `out/diff.json` | 0.23 s | 122 MB |
| `drift` 2.1.0 to 2.2.0 | `batches/drift.txt` | `out/drift.json` | 0.19 s | 103 MB |
| `reason owl-dl` on core 2.2.0 | `batches/coherence-core.txt` | `out/coherence-core.json` | 0.08 s | 69 MB |
| `reason owl-dl` on the union of 11 modules | `batches/coherence-union.txt` | `out/coherence-union.json` | 0.14 s | 86 MB |
| `lint` on core 2.2.0 | `batches/defects-core.txt` | `out/defects-core.json` | 0.03 s | 37 MB |
| `defects` on core 2.2.0 (CLI command) | none | `out/defects-core-cli.json` | 0.04 s | under 40 MB |
| Positive control: a deliberate clash | `batches/control-clash.txt` | `out/control-clash.json` | 0.02 s | 28 MB |

Timings and memory figures come from the matching `.stderr` file for each run. The `defects` command is not a batch command (`out/defects-core.json` records "unknown batch command"), so I ran it as a CLI command.

The inputs are copies of the released packages at EPM commit `d23f714`. `out/inputs.sha256` lists the SHA-256 of every file. The main ones:

| File | SHA-256 |
|---|---|
| `releases/core/2.1.0/core.ttl` | `c0d92c556be2c37fd3be2214d204cbb418b12bb7b0ec19b513b3e3ba8c02d941` |
| `releases/core/2.2.0/core.ttl` | `6e7fb17e4415b89c82803c368a53a98b39481f7a98de2d79aafb34c91711a57b` |
| `releases/core/2.1.0/shapes.ttl` and `2.2.0/shapes.ttl` (identical) | `c6ea5af973af13a9bc4c988906c78685a048e0dc8f8f10bcbbc2510599c31680` |

The union run loaded the newest package of each module: core 2.2.0, data-product 1.0.0, integration 1.0.0, kpi 1.1.0, lane 1.0.0, market-data 1.0.0, organization 2.0.0, party 1.0.0, ref-mpc 1.2.0, system 1.0.0 and value-stream 1.0.0. That is 33,742 triples. The union leaves out the shapes and catalog files, which hold no OWL axioms.

## What plan reported

`plan` reports 217 inserted and 7 deleted triples, risk score `low`, blast radius 0, and no added or removed classes, properties or individuals (`out/plan.json`). Its conservativity block lists 18 new statements about names that 2.1.0 already used, all of them asserted in the source and none inferred by a rule. It lists 25 names new to the graph, and it gives the verdict `undecided_not_an_extension` with exit code 2.

To check the plan, I wrote an independent rdflib diff (`scripts/crosscheck.py`, output in `out/rdflib-crosscheck.txt`). It agrees on 217 added and 7 removed triples. The plan matches what EPM-DEC-001-0076 and `CHANGELOG-2.2.0.md` say changed:

- The 18 statements are 4 version-header triples, the 8 scope notes (CM 1.1.7, CM 1.2.4.3.6, CM 1.2.5, CM 1.2.5.1, CM 1.3.3.4, CM 1.3.8.4.6, MS 1 and RF 1.2), the 4 notations on the stubs RF 1, RF 1.1, RF 1.2 and MS 1, and the 2 APQC decisions corrected to "Rejected".
- The 25 new names are the 23 new concepts, `skos:changeNote` and the 2.2.0 version IRI.
- The 7 deleted triples are 5 version-header triples and the 2 "Review link" decisions on CM 1.2.6.3 and Downstream Operations.
- The plan does not list the 3 change notes as new statements about old names, because `skos:changeNote` itself is new to the graph. The rdflib diff finds all 3: on CM 1.2.6.3, on Downstream Operations, and on RF 1.2 ("no longer a Candidate node").
- The 14 confirmed "No candidate" 19948 references did not change, so neither tool reports them. The plan cannot confirm that 16 concepts reference element 19948. It sees only the two that changed.

The plan has three weaknesses on this ontology.

First, its shape section misses the 23 new concepts. The plan counts as an individual only something typed `owl:NamedIndividual` or typed with a declared `owl:Class` (`src/src/plan.rs`, `extract_individuals_from_store`). Our concepts are `skos:Concept`, which core does not declare as an `owl:Class`. The plan therefore reports "added_individuals: []" and risk `low` for a release that adds 23 process concepts. The concepts appear only in `signature_added`.

Second, the verdict will be `undecided_not_an_extension` for every release. Each release rewrites `owl:versionInfo`, `owl:versionIRI`, `owl:priorVersion`, `dcterms:issued` and `dcterms:modified` on the ontology header. The tool reads that as a removal, so no release can count as a pure extension.

Third, the proof certificate was not checked. The Lean checker `oo-cert` was not built, so both certificates carry the verdict `engine_opinion` and the reason "oo-cert not found" (`out/plan.json`). Building it needs the Lean toolchain manager `elan`, which I did not install.

`drift` reported nothing (`out/drift.json`). It compared 40 properties to 40 properties and does not look at concepts.

## What the coherence check reported

The coherence check finds core 2.2.0 consistent and coherent (`out/coherence-core.json`). It checked 5 named classes and found all 5 satisfiable. It checked 1,429 individuals and found the ABox consistent. The run is complete, with no undetermined classes and no constructs it could not model. The union of the 11 newest modules is also consistent and coherent (`out/coherence-union.json`): 47 classes are satisfiable, 3,400 individuals are consistent, and the run inferred 3 subclass links in `party`. `defects` found 0 of its 8 kinds of defect (`out/defects-core-cli.json`). `lint` gave 3 notes: `core:CanonicalFact` and `core:ScopedSequence` have no `rdfs:comment`, and `core:evidenceBasis` has no `rdfs:domain` (`out/defects-core.json`).

The pass says little, because the graphs carry almost no OWL axioms that could clash. Core 2.2.0 mentions `owl:Class` 2 times and `skos:Concept` 807 times. All the newest packages together, shapes and catalogs included, mention `owl:Class` 43 times and hold one disjointness axiom, `party:Person owl:disjointWith party:Organization` (`releases/party/1.0.0/party.ttl`, line 25).

To show that the check can fail, I ran a positive control. I loaded the party module with one added resource typed as both `party:Person` and `party:Organization` (`inputs/control/clash.ttl`). The reasoner reported `consistent: false` (`out/control-clash.json`). The check works, but our data gives it only one axiom to test.

The ABox output also lists language-tagged strings as "individuals" with the inferred type `rdf:langString`: 5 in each run. These lines are noise from the tool and say nothing about the ontology.

## Comparison with the repo's checks

| Tool finding | Covered by the repo? | Verdict |
|---|---|---|
| 217 added and 7 removed triples. The 7 removed are the header plus 2 APQC decisions. | `test_build_core_2_2.py`, `test_every_2_1_0_triple_is_kept_except_the_header_and_two_apqc_decisions`, asserts exactly this set of removed triples. `test_no_iri_is_removed` asserts that no IRI is lost. | Duplicate |
| 23 new concepts, 4 notations, 8 scope notes, 2 corrected APQC decisions, change note on RF 1.2 | `test_the_new_concepts` asserts the 23 concepts and 706 process concepts, and the `CHANGED`, `CONFIRMED_19948` and `REJECTED_19948` sets cover the rest. `build_core_2_2.py --verify` in `check.sh` requires the package to equal a fresh build. | Duplicate. The plan sees less than the tests: it misses the 14 unchanged 19948 references and lists no concepts as added. |
| No added individuals, risk `low` | The test above proves 23 concepts were added. | False negative. The plan does not count `skos:Concept` as an individual. |
| Verdict `undecided_not_an_extension` | The test above allows exactly the header and the 2 APQC triples as removals. | False alarm. It will occur on every release because the version header changes. |
| Core and union coherent and consistent | SHACL in `check.sh` validates each module and the whole graph. `partysh:Party` has `sh:xone ( [ sh:class party:Person ] [ sh:class party:Organization ] )` (`releases/party/1.0.0/shapes.ttl`), which enforces the one disjointness axiom on the data. | Duplicate. The SHACL rule is stricter, because it also requires every party to be one of the two kinds. |
| 0 structural defects | No repo check looks for these defects by name. The ontology has no transitive, symmetric or inverse properties and no subclass cycles for them to apply to. | New check, but it found nothing. |
| 3 lint notes | Not covered. | New information. All three are minor gaps in documentation. |

The projection pipeline already runs a reasoner: `pipeline.py reason --robot` runs ELK through ROBOT (`business_architecture/ontology/projection/pipeline.py`, line 258). `check.sh` does not run that step. It runs `pipeline.py build --verify`, which compares a fresh build with the committed manifest and `inferred.nt`. The tool's `reason owl-dl` would be a sub-second check for coherence that needs no Java. Today it would have nothing to find.

## Recommendation

Do not adopt the tool into `check.sh` or CI. The approved trial plan was to adopt it only if its report finds something that `check.sh` and the regression miss. The trial found three lint notes about documentation and nothing else new. The plan repeats what `test_build_core_2_2.py` already asserts, and it misreads SKOS concepts and version headers. The coherence check passes because the graphs hold almost no OWL axioms to test.

Two things could change this view. A later release could add OWL axioms that interact, such as disjointness between process classes, domains and ranges on classes, or property chains. Then `reason owl-dl` and the plan's rule-based consequences would test something that SHACL does not test. If that happens, run this trial again with `scripts/run.sh`.

The three lint notes could be fixed in a later core release, as a [patch] change to documentation. That is a proposal for the module owner, not a finding against 2.2.0.

## Files

Everything is in `/private/tmp/claude-501/open-ontologies-trial/`:

- `src/` is the tool's source at commit `9329530`.
- `target-arm64/release/open-ontologies` is the binary that was built.
- `release-bin/open-ontologies-aarch64-apple-darwin` is the v2.0.1 binary, downloaded and not used.
- `inputs/` holds copies of the packages and the control file. `out/inputs.sha256` lists their hashes.
- `batches/` holds the batch files, and `scripts/` holds `run.sh` and `crosscheck.py`.
- `out/` holds every raw output (`*.json`), the timings (`*.stderr`), both build logs and the rdflib cross-check.
- `data/` holds the tool's state directory for each run.
