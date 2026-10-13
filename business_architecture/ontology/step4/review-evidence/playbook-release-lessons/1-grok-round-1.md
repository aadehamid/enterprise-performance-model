## Code Review Results

**Scope:** `d8b16e1` (origin/main, merge of #249) -> working tree `ec41559` on `playbook/release-lessons` (2 files: `ontology-playbook.md`, `ontology-worklog.md`)
**Intent:** Add company-neutral release lessons from core 1.0.0 to Appendix B, and update the worklog so the core 1.0.0 decision-log entry is newest-first and states only what has landed (merge d8b16e1, tag core-v1.0.0).
**Mode:** markdown report-only
**Standards:** AGENTS.md + REVIEW_STANDARDS.md

**Reviewers:** correctness, project-standards
- correctness -- always-on
- project-standards -- root AGENTS.md governs the changed markdown; REVIEW_STANDARDS.md is the merge bar

### P1 -- High

| # | File | Issue | Reviewer | Confidence |
|---|------|-------|----------|------------|
| 1 | `business_architecture/ontology/step4/release-checklist.md:80` | Landed-tag wording missed the checklist | project-standards | 100 |

- **#1** -- The worklog now says core 1.0.0 merged as d8b16e1 and is tagged `core-v1.0.0`. `release-checklist.md:80` still says the #249 merge gets that tag when it merges. A reader of the checked item still treats a landed tag as future work. That is an AGENTS.md item 4 miss (instruction replacement not applied everywhere) and a REVIEW_STANDARDS blocking item. Validator confirmed: annotated tag `core-v1.0.0` peels to d8b16e1. `validation_status: confirmed`. Replace the future-tense clause with the worklog wording: Merged in #249 as d8b16e1 and tagged `core-v1.0.0`. Keep the cut steps. Leave historical review-evidence files unchanged.

### Actionable Findings

| # | File | Issue | Route | Notes |
|---|------|-------|-------|-------|
| 1 | `business_architecture/ontology/step4/release-checklist.md:80` | Landed-tag wording missed the checklist | `gated_auto -> downstream-resolver` | `suggested_fix` present. `validation_status: confirmed`. Local apply was not authorized. |

### Coverage

- Cross-model pass: not run (adversarial not selected: instruction-prose only)
- Standards: AGENTS.md instruction-file fallback; REVIEW_STANDARDS.md applied because AGENTS.md requires it for PR review
- Depth: full (caller asked for a full review of the branch vs main)
- No PR associated with playbook/release-lessons
- Local main was stale (c892ac98); reviewed vs origin/main d8b16e1 (merge of #249). HEAD ec41559 is one commit ahead of origin/main.
- Folded nothing from a peer artifact (peer.outcome=not-run).
- 0 findings suppressed at any confidence anchor. first_evidence_backfilled: 0. Quote-the-line demotions of 75/100 findings for missing first_evidence: 0.
- Mode-aware demotion count: 0.
- Settlement suppression was not evaluated (plan source none).
- Validator shortcut skips: 0 (no finding had first_evidence plus an ordinary reviewer and an adversarial-<provider> artifact with independence_verified:true).
- Validator batch: 1 selected finding (#1). Outcome: 1 confirmed, 0 rejected, 0 unresolved, 0 malformed, 0 failed. Protected-subject reclassification: none (`protected_subject` was null; this is an instruction-propagation miss, not a protected subject).
- Confirmation reason: the diff replaces the worklog's "gets the tag at merge" instruction with landed wording while release-checklist.md:80 still says the #249 merge gets `core-v1.0.0` when it merges, even though annotated tag core-v1.0.0 peels to d8b16e1.
- Failed reviewers: none. Bound exceeded: none. Fast-pass: none.
- Malformed findings dropped before Stage 5b: 0.
- Stage 5c skipped (`mode.apply_local` is false; findings only).

**Verification (1) Appendix B vs core 1.0.0.** Appendix B additions are company-neutral method (owner, rc label, cardinality, builder tests). They match what core 1.0.0 actually did for rc until approval, independent builder tests, cardinality on core properties, and ConceptScheme typing. Residual: the playbook says cardinality on every property in the SHACL slice; shipped `shapes.ttl` states cardinality on core properties; `dcterms:source` and `dcterms:references` have only `sh:nodeKind`.

**Verification (2) Step 9 / Appendix B remainder.** No contradiction with Step 9 (small slice, SHACL Core first, failing shape is a question) or with Appendix B's remaining text except the worked Turtle header still types only `owl:Ontology` while the new paragraph requires ConceptScheme when concepts are inScheme that IRI.

**Verification (3) Decision log.** Newest-first: core 1.0.0 released (2026-10-13), then Playbook method update, then Phase 1. Entry states merge d8b16e1 and tag `core-v1.0.0`; tag peels to d8b16e1; Hamid quote matches `hamid-answers/core-1-0-0-release.md`. Miss: checklist still future-tense.

**How this could pass review while still being wrong.** A reviewer who only diffs the two changed files would miss the checklist. Figures 5571/640/1003 were moved, not re-derived. Residual cardinality overstatement vs the shipped slice. Turtle example vs ConceptScheme paragraph.

**Residual risks:**
- Appendix B's worked Turtle header still types the module as `owl:Ontology` only (`ontology-playbook.md:1388-1389`). The new adjacent rule requires `skos:ConceptScheme` as well when concepts are `skos:inScheme` that IRI. Core 1.0.0 does that (`releases/core/1.0.0/core.ttl:17156-17157`). A reader who copies the example and skips the next paragraph would omit the scheme type the lesson exists to prevent.
- The new cardinality lesson says every property in the SHACL slice states `sh:maxCount 1` or `sh:minCount 0` with no maximum (`ontology-playbook.md:1361-1364`). The shipped core 1.0.0 slice does that for core properties, including unused `core:governanceStatus`, but `dcterms:source` and `dcterms:references` in `shp:ProcessConcept` have only `sh:nodeKind` (`releases/core/1.0.0/shapes.ttl:41-43`). The test also excludes code-list and ontology-header properties (`release/test_build_core.py:228-229`).

**Testing gaps:** none.

---

> **Verdict:** HOLD
>
> **Reasoning:** Finding #1 is an AGENTS.md Before every push item 4 miss: the worklog instruction replacement was not applied to `release-checklist.md:80`. REVIEW_STANDARDS treats AGENTS.md items 3 and 4 as blocking. One open P1 blocks MERGE-READY. Validator confirmed #1. Local apply was not authorized. Skill-scale verdict is Ready with fixes.
>
> **Fix order:** Update `release-checklist.md:80` to the landed wording already in the worklog. Then re-check AGENTS.md item 4 for any remaining future-tense tag instruction.

### Actionable Findings

1. **#1** P1 `business_architecture/ontology/step4/release-checklist.md:80` -- landed-tag wording still future tense. Response: mechanical edit (`gated_auto -> downstream-resolver`). `suggested_fix` present. Confidence 100. Confirmed.
