## Code Review Results

**Scope:** standalone `release/core-1.0.0` vs `phase1/sweep-201` (`847aac38`) -> `bd8ad7ffeebbaed676b4453801ed1f3a27a4bdec` (24 files). PR #248 / issue #201 is out of scope.
**Intent:** Ship Core ontology 1.0.0 from pinned Step 4 evidence per EPM-DEC-001-0029 (delegated under pending EPM-DEC-001-0028). Package, `check.sh` wiring, and ledger/checklist/worklog records land here. Attestation, ledger approval, and release approval stay open for the decision owner.
**Mode:** markdown report-only

**Reviewers:** correctness, project-standards, testing, maintainability, api-contract, adversarial
- correctness -- always-on
- project-standards -- `AGENTS.md` and `REVIEW_STANDARDS.md` govern all changed files (no `CODING_STANDARDS.md`)
- testing -- new `test_build_core.py` and `--verify` / `check.sh` wiring
- maintainability -- 418 executable non-test lines; new `build_core.py`
- api-contract -- published ontology package, `owl:versionIRI`, DCAT, changelog
- adversarial -- in-process fallback after cross-model transport failure (`independence_verified: false`)

### Triage Groups

| Group | Findings | Context | Preferred Resolution | Why |
|-------|----------|---------|----------------------|-----|
| Public 1.0.0 header (decision-gate) | #2, #7 | Packaged ontology is issued as 1.0.0 on 2026-10-13 while CHANGELOG says (unreleased); the ontology IRI also carries two titles | Decide the public state first (#2). Then remove leftover ConceptScheme title/description before the playbook literals (#7) and rebuild | One cut decision sets `ISSUED`, changelog, and `versionIRI`. The rebuild is what publishes a single title |

#1 and #5 stay ungrouped: conservation/`--verify` is a test-and-count defect; the 0029 stamp is a decision-record status call.

### P1 -- High

| # | File | Issue | Reviewer | Confidence |
|---|------|-------|----------|------------|
| 1 | `business_architecture/ontology/release/build_core.py:286` | `5571=5571` and `--verify` stay green after swapped mappings | adversarial, testing | 100 |
| 2 | `business_architecture/ontology/release/build_core.py:41` | Ontology issued 2026-10-13 while changelog is unreleased | adversarial, api-contract | 100 |
| 5 | `business_architecture/domain/decisions/EPM-DEC-001-0029-core-1-0-0-release-design.md:6` | 0029 stamped Decided while 0028 is still pending | adversarial | 75 |

- **#1** -- `conservation()` compares `source:*` tallies to `emitted:*` plus `replaced:*` and writes a hardcoded target name. `relatedConcepts` increments `replaced:` with no emit. Tests assert `sum(source_triples)==5571` and `source==migrated`, not graph triples per EPM-DEC-001-0029 destination. `--verify` rebuilds with the same generator and diffs the package, so a buggy `--write` then `--verify` always matches. `check.sh` runs that `--verify` then pytest. Scratch swaps of `primaryPurpose`/`responsibleDomain`, Q10 note predicates, AddAsAltLabel vs MigrationOnly, and canonical-fact ends still passed 10 tests. SHACL still conforms for a langString/langString swap and for unconstrained Q10/label predicates. Count destinations in the graph; fail `relatedConcepts` unless `canonical-facts.csv` rows are present as those predicates; add invert/swap tests that must fail; keep `--verify` as a freshness check only. Confirmed. Incidence of a wrong mapping in the current generator was not measured.

- **#2** -- `ISSUED = "2026-10-13"` writes `dcterms:issued` / `dcterms:modified` and `owl:versionIRI` / `owl:versionInfo` `1.0.0` into `core.ttl` and the DCAT catalog. `CHANGELOG.md` still says `## 1.0.0 (unreleased)` and names no approver. `release-checklist.md:76-80` still leaves ledger approval, attestation, "Release approval: The decision owner.", and "set ISSUED at the cut" open. Design call: leave `ISSUED` unset or pre-release until the decision owner's release approval is quoted, and keep the changelog in lockstep; or drop `(unreleased)`, add a SemVer/approver line, and rebuild. Do not mint `versionIRI` 1.0.0 before that approval is recorded. Confirmed (`public-contract`).

- **#5** -- Status is `Decided (delegated under EPM-DEC-001-0028)`. `domain/decisions/README.md:5-6` allows Decided only when the decision owner has recorded the decision. No 0028 file exists (pending in #242). 0029:46 quotes the delegation and says the decision owner did not make these choices themselves. Agents and the decision index treat Decided as locked intake targets, IRI scheme, and package layout. Set Status to Proposed or Delegated-pending-0028 until 0028 lands and the decision owner's words cover this record. Confirmed. Owner: human.

### P2 -- Moderate

| # | File | Issue | Reviewer | Confidence |
|---|------|-------|----------|------------|
| 7 | `business_architecture/ontology/releases/core/1.0.0/core.ttl:17164` | Ontology IRI publishes two `dcterms:title` values | api-contract | 75 |

- **#7** -- `build_core.py:267-270` adds the playbook title without removing the pinned ConceptScheme title copied from `step3-taxonomy.ttl`. `core.ttl:17164-17165` and `core.jsonld:64-72` publish `LSC Core Process Ontology` and `LSC downstream process taxonomy` (same split on description). JSON-LD and SPARQL clients that expect one string get an array. After #2, remove existing `DCTERMS.title` and `DCTERMS.description` on `ONTOLOGY_IRI` before adding the playbook literals, then rebuild. Confirmed (`public-contract`).

### Actionable Findings

| # | File | Issue | Route | Notes |
|---|------|-------|-------|-------|
| 1 | `business_architecture/ontology/release/build_core.py:286` | Count graph triples per 0029 destination; add invert/swap tests; keep `--verify` as freshness only | `manual -> downstream-resolver` | `suggested_fix` present. `validation_status: confirmed`. Incidence of a wrong mapping in this generator was not measured. Confirmation grants no apply authority. |
| 7 | `business_architecture/ontology/releases/core/1.0.0/core.ttl:17164` | Drop leftover ConceptScheme title/description before playbook literals; rebuild | `gated_auto -> downstream-resolver` | `suggested_fix` present. Do after #2. Confirmed `public-contract`. |

#2 and #5 are decisions a person must make. They are not in this apply queue.

### Learnings & Past Solutions

No pack-rule notes and no linked past solutions survived as non-finding Known Patterns.

### Coverage

- Cross-model peer: not run. Codex then Claude both reported transport unavailable (pre-egress, route): `acpx` exited 1 before sending the prompt. No reviewed content left the machine. In-process adversarial fallback; `independence_verified: false`. Peer agreement did not raise confidence.
- Helper: first pass 14 primary; after semantic reconciliation 7 primary. `first_evidence_backfilled`: 0. Quote-the-line demotions at 75/100: 0. Suppressed by confidence: 0. Mode-aware demotion: 0. Malformed findings/returns: 0.
- Settlement suppression was not evaluated: no plan was discovered in Stage 2b.
- Validator skip count: 0. No finding had `first_evidence` plus an ordinary reviewer plus an `adversarial-<provider>` artifact with `independence_verified: true`.
- One validator batch: findings #1-#7, ordered by severity then `#`. Verdicts landed (wait bound not exceeded): confirmed 4 (#1, #2, #5, #7); rejected 3 (#3 notation, #4 SHACL allow-list, #6 blank-node IRI tests); unresolved 0; malformed 0; failed 0; shortcut-skipped 0.
- Protected-subject classification (report leaf, before verdicts): #2 and #7 `public-contract`; #1, #3, #4, #5, #6 not protected. Validator keys matched. No reclassification.
- Rejected #3: the 14 `inScheme` concepts without `skos:notation` are slug-only L0/L1/L2 nodes; playbook Step 2 mints slugs where no local ID exists; `shp:NotatedConcept` matches that policy.
- Rejected #4: EPM-DEC-001-0014 records a minimal 1.0.0 slice and defers controlled-value lists to Step 9; `sh:class skos:Concept` on those facets is that slice; REVIEW_STANDARDS rule 8 applies where a check already guards per-item decided values.
- Rejected #6: `counts['blank nodes resolved']==1003` is a coverage gap; `build_core.py:129-131` already mints `{part}/element/{ident}` and `src:step3c-definition-workbook`, and released `core.ttl` uses those IRIs.
- Failed reviewers: none. Bound exceeded: none.
- Residual risks: APQC same-id merge with no conflict check; `resolve()` rematerializes triples if the same blank is visited twice; `ledger-v2.md` master table still shows retired/pending targets (header says 0029 wins); DCAT `dcat:downloadURL` equals the w3id IRI with no rewrite map; catalog Dataset omits `dcterms:modified` and the playbook HTML-docs distribution; license IRI has no described resource; merging `core.ttl` + `catalog.ttl` types `versionIRI` as Dataset; EPM-DEC-001-0020 rule 5 (`lpg:name` collision check) unimplemented; scoped-sequence predicates not exhaustively mapped to SHACL cardinality.
- Testing gaps: no test that `--verify` exits non-zero on a packaged-file or extra-file mismatch; Q6 dual assignment pinned only as `horizon facet assignments == 577`; retired vs blocked has no graph assertion; vocabulary `skos:definition` text is not compared to approved wording; no `catalog()` test for issued/modified, distribution set, or `downloadURL` vs identifier.

**How this can pass review and still be wrong.** `check.sh` can be green while Core 1.0.0 is not the decided mapping. `conservation.csv` still prints `5571=5571` and the decided target names because those names are a label table, not a count of `out`. `--verify` diffs this generator against itself. The SHACL slice still conforms after a langString/langString property swap and after Q10/label swaps (those predicates are unconstrained). Status=Decided on 0029 lets agents treat intake targets and package layout as owner-locked while 0028 is pending in #242 and the record says they did not choose them. A reader of a green gate plus the Decided stamp can ship the package as proved 1.0.0.

---

> **Verdict:** Ready with fixes
>
> **Reasoning:** Four confirmed findings remain, three of them P1. #1 lets `check.sh` pass while every intake triple can land on the wrong core predicate (`5571=5571`, self `--verify`, SHACL still green on unconstrained swaps). #2 publishes `dcterms:issued` 2026-10-13 and `owl:versionIRI` 1.0.0 while CHANGELOG is `(unreleased)` and the decision owner's release approval is still open. #5 stamps 0029 Decided without the decision owner's recorded decision. #7 ships two titles on the public ontology IRI. No unresolved verification gates. Rejected #3/#4/#6 do not clear the silent-pass path in #1.
>
> **Fix order:** Decide public state (#2) and 0029 status (#5). Then count graph destinations and add invert/swap tests (#1). Then strip dual titles and rebuild (#7).

### Actionable Findings

- **#1** P1 `business_architecture/ontology/release/build_core.py:286` -- conservation/`--verify` silent-pass. `manual`. `suggested_fix` present. Confidence 100. Count graph triples; add invert tests.
- **#7** P2 `business_architecture/ontology/releases/core/1.0.0/core.ttl:17164` -- two `dcterms:title` values. `gated_auto`. `suggested_fix` present. Confidence 75. Rebuild after #2.

Actionable findings: 2 (`#1`, `#7`). Artifact: `/tmp/compound-engineering-501/ce-code-review/20261013-030244-7e0e8ac2/report.md`
