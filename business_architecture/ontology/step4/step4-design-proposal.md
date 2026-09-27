# Step 4 Design Proposal — Process-definition ontology & `intake:` retirement

**Status:** Survey and design proposal for Hamid's review. Nothing implemented, no branches, no PRs.
**Source:** `aadehamid/enterprise-performance-model`, main HEAD `2d5529841cd33cab427f1d72dccf669c65516d77` (verified read-only via GitHub API, 2026-09-22).
**Input artifact:** `business_architecture/ontology/build/output/step3-taxonomy.ttl` (683 concepts, 14,496 triples, 681 broader links).

**Playbook intent for Step 4** (plan table + decision log): build the process-definition ontology — `ProcessDefinition`/`ProcessType` classes; systems, variants, lanes, flags, capabilities, value streams — and promote the provisional `intake:` annotations to real properties between concept URIs, retiring the `intake:` predicates. The RDFS/OWL "why we chose it" section already anticipates real classes (`ProcessDefinition`, `ResponsibilityAssignment`, `NamedKPI`); Step 6 then layers planned-vs-observed execution (PROV-O) on top of Step 4's planned flow model.

---

## 1. Inventory — every `intake:` predicate in the TTL

Namespace: `https://w3id.org/lsc/ontology/intake/` (declared line 2 of the TTL). **No OWL/RDFS declarations exist** — the predicates are bare; their only "definitions" are prose comments in `build/step3-skos-taxonomy.py` (lines 52–57, 345, 525–536) and the playbook decision-log entry "Provisional `intake:` namespace" (2026-09-20). Total `intake:` triples: **5,571**.

| Predicate | Triples | Annotates | Workbook column / generator logic (`step3-skos-taxonomy.py`) |
|---|---|---|---|
| `intake:level` | 683 | every concept | identity-map `level` → `"L0"`…`"L6"@en` (all concepts, line ~307) |
| `intake:apqcDecision` | 500 | approved rows | `apqc_decision` — REVIEW LINK / ADOPTED / REJECTED / NO CANDIDATE / NO SOURCE |
| `intake:terminologyNotes` | 491 | approved + blocked/retired rows | `terminology_notes` (long prose; also emitted for blocked/retired rows) |
| `intake:referenceSources` | 488 | approved rows | `reference_sources` — `SRC-` IDs, `|`- or `;`-separated, some with annotation suffixes |
| `intake:primaryPurpose` | 488 | approved rows | `primary_purpose` — one-sentence purpose prose |
| `intake:conceptTypeCheck` | 488 | approved rows | `concept_type_check` — process (463) / capability (23) / not-process (2) |
| `intake:relatedConcepts` | 486 | approved rows + 1 reviewed pending interface | `related_concepts` — semi-structured `verb: Target` segments; 13 verbs (see §3) |
| `intake:responsibleDomain` | 485 | approved rows | `responsible_domain` — 456× "Commercial & Marketing", rest Finance / cross-functional variants |
| `intake:processHorizon` | 485 | approved rows | `process_horizon` — event-driven 122, periodic 107, continuous 93, tactical 44, daily 40, monthly 36, strategic 27, weekly 16 |
| `intake:primaryOutput` | 485 | approved rows | `primary_output` — free prose, 485 distinct values |
| `intake:keyInputs` | 485 | workbook `key_inputs` — `|`-separated lists, 1,442 distinct values |
| `intake:parkedChildren` | 5 | approved rows | `parked_children` — pipe-separated planned child names |
| `intake:status` | 2 | blocked/retired rows only | `status` — `CM-1-1-4-6-1` "blocked", `CM-1-1-4-6` "retired" (retired also `owl:deprecated`) |

Generation rule recap: approved rows emit the full Phase-1 column set; blocked/retired rows emit only `intake:status` + `intake:terminologyNotes`; the one reviewed pending interface (`CM-1-1-2-9-1` → "informs: Refinery Planning and Optimization (CM-1-1-4)") emits `intake:relatedConcepts` via the `REVIEWED_PENDING_INTERFACES` allowlist.

---

## 2. Proposed real properties

**Module:** all in `core` (new vocabulary namespace `https://w3id.org/lsc/ontology/modules/core/`, prefix `core:`). Rationale: the module policy makes `core` the owning module for the process domain; `proc:` stays the instance namespace for concepts.

**New classes (Step 4):**
- `core:ProcessDefinition` — every `proc:` concept gets `a core:ProcessDefinition` in addition to `a skos:Concept` (the class the playbook's RDFS/OWL section already anticipates).
- `core:InformationObject` — first-class flow node for inputs/outputs (see §4).

| `intake:` predicate | Proposed property | Kind | Domain → Range | Notes |
|---|---|---|---|---|
| `intake:level` | `core:taxonomyLevel` | datatype, `xsd:integer` | ProcessDefinition → 0–6 | locked structural fact; SHACL range check lands in Step 9 |
| `intake:status` | `core:lifecycleStatus` | datatype, controlled vocab | Concept → string | values: `active` (default, unstated) / `blocked` / `retired`; governance metadata, not domain data |
| `intake:primaryPurpose` | `core:primaryPurpose` | datatype, `rdf:langString` | ProcessDefinition → text | keep as prose; distinct from `skos:definition` |
| `intake:conceptTypeCheck` | `core:conceptKind` | datatype, controlled vocab | Concept → string | `process` / `capability` / `not-process`; class promotion deferred until the CM-1-3-1-6 capability-vs-process question resolves |
| `intake:processHorizon` | `core:processHorizon` | datatype, controlled vocab | ProcessDefinition → string | values need normalization — current cells mix cadence (daily/weekly/monthly), mode (event-driven/continuous/periodic), and planning level (tactical/strategic) |
| `intake:responsibleDomain` | `core:responsibleDomain` | datatype, controlled vocab (interim) | ProcessDefinition → string | interim literal; **Step 5** promotes to `org:Role` / `ResponsibilityAssignment` |
| `intake:apqcDecision` | `core:apqcMappingDecision` | datatype, controlled vocab | Concept → string | ADOPTED / REVIEW LINK / REJECTED / NO CANDIDATE / NO SOURCE; REJECTED = deliberate divergence (competency Q12) |
| `intake:terminologyNotes` | `core:definitionNote` | annotation, `rdf:langString` | Concept → text | authoring-process notes; alternatively `skos:editorialNote` — recommend `core:definitionNote` for a stable, documented predicate |
| `intake:referenceSources` | `dcterms:source` | object → `dcterms:BibliographicResource` blank node | Concept → Resource | parse bare `SRC-XXX-NNN` tokens (59 distinct; handle `|`/`;` separators and strip annotation suffixes); node carries `dcterms:identifier` + `dcterms:title` from the 50-source registry in `build/output/source-to-process-traceability.md` |
| `intake:parkedChildren` | `core:plannedChildNote` | annotation, `rdf:langString` | Concept → text | only 5 triples; targets don't exist as concepts yet, so no object property is possible; replaced by `skos:narrower` when R2 creates them |
| `intake:keyInputs` | `core:consumes` | **object** → `core:InformationObject` | ProcessDefinition → InformationObject | §4 |
| `intake:primaryOutput` | `core:produces` | **object** → `core:InformationObject` | ProcessDefinition → InformationObject | §4 |
| `intake:relatedConcepts` | verb-specific `core:` object properties | **object** | ProcessDefinition → ProcessDefinition | §3 |

---

## 3. `relatedConcepts` → object properties

The 486 cells contain **1,318 relation mentions** across 13 verb tokens:

| Verb | Mentions | Proposed canonical property | Inverse |
|---|---|---|---|
| `enables` | 399 | `core:enables` | `core:enabledBy` |
| `uses-input` | 221 | `core:usesInput` (see decision Q4) | `core:inputUsedBy` |
| `follows` | 181 | `core:follows` | `core:precedes` |
| `precedes` | 171 | `core:precedes` | `core:follows` |
| `informed-by` | 152 | `core:informedBy` | `core:informs` |
| `governed-by` | 148 | `core:governedBy` | `core:governs` |
| `triggers` | 18 | `core:triggers` | `core:triggeredBy` |
| `constrained-by` | 10 | `core:constrainedBy` | `core:constrains` |
| `assures` | 8 | `core:assures` | `core:assuredBy` |
| `requires` | 6 | `core:requires` | `core:requiredBy` |
| `produces` | 2 | `core:deliversTo` (process→process; distinct from flow `core:produces`) | `core:receivesFrom` |
| `informs` | 1 | `core:informs` | `core:informedBy` |
| `constrains` | 1 | `core:constrains` | `core:constrainedBy` |

Canonical direction: active voice; `owl:inverseOf` declared for each pair. The vocabulary is already directionally clean (no `enables-by`/`follows-by` variants).

**Target resolution (measured):** 411 distinct target names; 404 resolve exactly to a `skos:prefLabel`. Resolution plan: `(ID)`-suffixed targets resolve by notation; bare names resolve by exact prefLabel match; **ambiguous or unresolvable targets are held for human review, never guessed.**

---

## 4. Flow modeling (inputs/outputs)

Per the standing plan ("inputs/outputs → flow modeling"), Step 4 mints `core:InformationObject` instances — one per distinct value string — and links them with `core:consumes` / `core:produces`. Sizing: **1,442 distinct input values** (485 cells) + **485 distinct outputs** ≈ ~1,900 flow nodes after dedup (case/whitespace normalization). No value currently appears as both an input and an output, so the flow graph starts bipartite-clean. This gives Step 6 the *planned* flow layer on which observed executions (`prov:Activity`) will hang.

`uses-input` (221 mentions, process→process) overlaps the flow model: it names a process whose output is consumed. Recommendation: keep `core:usesInput` as the process→process edge in Step 4 and let Step 6 expand it through the `InformationObject` nodes (see decision Q4).

---

## 5. Cutover approach (ordered)

1. **Pre-Step-4 workbook patch (separate, small).** Normalize before any promotion: fix the 16 `relatedConcepts` cells with stale pre-R1 bare targets ("Refinery Planning" → "Refinery Planning and Optimization"; "Refinery Scheduling" → "Refinery Production Planning and Scheduling") — subjects: CM-1-1-2-10, CM-1-1-2-12, CM-1-1-2-13, CM-1-1-3-7-1, CM-1-1-3-7-2, CM-1-1-4-7-7, CM-1-1-4-7-8, CM-1-1-7-2-6, CM-1-2-1-1-1, CM-1-2-5-1-2, CM-1-2-5-2-2, CM-1-2-5-2-3, CM-1-2-5-2, CM-1-1-7-2, CM-1-2-1-1, CM-1-1-4-7 — and resolve the 7 non-matching bare targets (Data Governance [external workstream], Monthly Operating Plan, Network Design, "Manage Trading Books & Strategies Structure", "contemporaneous assumption basis for Regional Backcasting" [prose, not a concept]). Workbook patch → TTL regen → gates, as its own review.
2. **Step 4a — vocabulary.** Author `core:` classes + ~20 properties with `rdfs:label`, `skos:definition`, `rdfs:domain`/`range` (Hamid-reviewed batch). Additive only.
3. **Step 4b — migration.** New `build/step4-promote-intake.py`: parses the workbook Phase-1 columns (the authoring source of truth, not the TTL strings) and emits the new triples; writes a held-for-review report for ambiguous / unresolvable targets instead of emitting them.
4. **Cutover: flag-day in one release.** The generator's `intake:` block is replaced by the new emission; the release drops all 5,571 `intake:` triples and adds the promoted model. (Rationale §6.)
5. **Pipeline updates.** Gate checker: assert zero `intake:` triples + assert the new properties' invariants (target resolvability, controlled vocabs, flow-node dedup). Report template updated. Workbook columns unchanged (they remain the authoring source).
6. **Changelog + first versioned release** (no `owl:versionInfo` is shipped today; Step 4 establishes it — see §6).

---

## 6. SemVer assessment

- **New vocabulary (classes, properties, new triples): minor** — purely additive.
- **Removing the 5,571 `intake:` triples: major.** Version-policy test: "would every query, report, and Genie answer produced under the old data still be correct?" — any consumer reading `intake:` predicates breaks. "When in doubt, it's major."
- **Retirement mode: outright removal, not `owl:deprecated` aliases.** The `intake:` namespace was explicitly provisional ("explicitly NOT the Step 4 model"), was never a published contract, and Gate 2 evidence stands: **zero consumers** (foundation stage, Hamid 2026-09-22). Deprecating a staging namespace would double ~5.5k triples of dead weight for ceremony. Document the removal in the changelog instead.
- **Recommendation:** ship the Step 4 release as the first versioned release (`core` 1.0.0 + release 1.0.0), with the changelog recording the `intake:` retirement as the breaking change from the unversioned baseline. Majors require Hamid's approval — which starting Step 4 constitutes.

---

## 7. Risks

1. **Target ambiguity:** 6 `relatedConcepts` target names match 2–5 concepts each (Actualizations, Analyze Data, Define Analysis Objectives & Scope, Determine Taxability, Document Findings, Source & Collect Information). Migration must hold these for human disambiguation.
2. **Stale references:** the 16 cells in §5(1) missed the R1 stale-label sweep; promoting them unresolved would bake dangling targets into object properties.
3. **Separator inconsistency:** `referenceSources` cells mix `|` and `;` separators and carry annotation suffixes — parser must normalize.
4. **`processHorizon` semantic mixing:** cadence vs mode vs planning-level values in one column; controlled-vocab normalization needs Hamid's value list.
5. **`responsibleDomain` free text:** "Cross-functional (…)" variants need a multi-value or interim-literal decision before Step 5.
6. **Flow-node dedup:** ~1,900 `InformationObject` nodes from free prose; near-duplicate strings will need a review pass to avoid a noisy flow graph.
7. **`conceptTypeCheck` vs CM-1-3-1-6:** the capability-vs-process modeling question is still open; a datatype property now keeps options open, class promotion later is additive.

---

## 8. Effort estimate (concrete steps, review-batch sized)

1. Workbook patch batch: 16 stale cells + 7 target resolutions → regen → gates. (1 batch)
2. Core vocabulary authoring: 2 classes + ~20 properties with definitions. (1 Hamid-reviewed batch)
3. `step4-promote-intake.py`: parser + emitter + held-for-review report. (1 batch)
4. Generator swap (`step3-skos-taxonomy.py`), gate-checker updates, report template. (1 batch)
5. Full gates + workbook validation + Hamid review → merge. (1 batch)

**Total: ~5 review batches.** No Step 5/6/9 work is pulled in; SHACL for the new controlled vocabs lands in Step 9 as planned.

---

## 9. Decision questions for Hamid

1. **Vocabulary namespace:** `core:` (`https://w3id.org/lsc/ontology/modules/core/`) for the new classes/properties, keeping `proc:` for concept instances? (Recommended: yes — APPROVED as Q1, 2026-09-22.)
2. **Retirement mode:** flag-day removal of all `intake:` triples in the Step 4 release (recommended), vs. a deprecated-alias transition release?
3. **First version:** ship Step 4 as `core`/`release` 1.0.0 with the `intake:` retirement recorded as the breaking change from the unversioned baseline?
4. **`uses-input`:** keep as process→process `core:usesInput` edge (recommended), or fold entirely into the `InformationObject` flow model now?
5. **Flow depth:** mint `InformationObject` nodes for all ~1,900 distinct input/output values (recommended), or keep inputs/outputs as structured literals and do flow nodes in Step 6?
6. **`processHorizon`:** normalize to a controlled vocabulary now — what is the canonical value list (cadence vs mode vs planning level)?
7. **`responsibleDomain`:** interim controlled literal until Step 5 RACI (recommended), or model org units now?
8. **`conceptKind`:** datatype property now (recommended), or promote capability/not-process to classes immediately?
9. **The 7 unresolvable targets** (§5.1): confirm dispositions — Data Governance as external reference, the stale R1 labels as renames, and the prose fragment dropped or modeled?
10. **Ambiguous targets** (6 names, §7.1): disambiguate by hand in the workbook patch batch, or defer those edges to a follow-up?
