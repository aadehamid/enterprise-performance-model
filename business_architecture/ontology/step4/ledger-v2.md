# Intake Predicate Conservation Ledger v2 — DRAFT (not approved)

**Status:** draft for review. No predicate retires until Hamid approves this ledger
AND the promotion script proves the migration in a before/after reconciliation run.
**Baseline:** `6ab2197ba3fe6246bdb501391d22b71d0338d2c7` (PR #120).
**Census method:** literal-aware block parser (triple-quoted literals kept intact).
**Census date:** 2026-09-25.

## Why this census exists

The rule is: **conservation, not deletion.** Every `intake:` triple on the pinned
baseline must be traceable to exactly one of: emitted to its Step 4 target,
held for a pending decision, or deliberately retired with a recorded rationale.
Zero `intake:` triples after migration proves deletion, not migration. This ledger
is the "before" half of the before/after reconciliation.

## Census reconciliation: 5,571, not 5,565

An earlier naive parser reported 5,565 triples. The literal-aware census reports
**5,571**. The 6-triple difference is fully explained — no triples invented:

- **5 triples:** one concept's definition contains a blank line inside a
  triple-quoted literal (a paragraph beginning "Does…"). The naive parser split the
  block at that blank line, orphaning the 5 following predicates
  (processHorizon ×1, conceptTypeCheck ×2 net, and 2 more of the affected
  predicates). Re-parsing with literal awareness restores them.
- **1 triple:** the approved R1 interface relation (`CM-1-1-2-9-1 informs
  Refinery Planning and Optimization`) was missing from the stale earlier source
  and is present on the pinned baseline.

## Master conservation table (source triple counts)

| intake: predicate | Source | Emitted | Held | Retired | Disposition |
|---|---|---|---|---|---|
| level | 683 | 0 | 0 | 683 | retired as annotation; depth derived from skos:broader (approved Q-step-3) |
| apqcDecision | 500 | 500 | 0 | 0 | → core:apqcMappingDecision |
| terminologyNotes | 491 | 491 | 0 | 0 | Q10 three-way split (see below) |
| referenceSources | 488 | 488 | 0 | 0 | → 737 dcterms:source resource links (see below) |
| primaryPurpose | 488 | 488 | 0 | 0 | → core:primaryPurpose |
| conceptTypeCheck | 488 | 0 | 488 | 0 | Q8 core:conceptKind scheme pending; literals preserved |
| relatedConcepts | 486 | 1,114 mention-facts → 921 canonical facts* | 187 mentions | 0 | mapping v2 (proposed, not approved) |
| responsibleDomain | 485 | 485 | 0 | 0 | Q7 interim governed literal |
| processHorizon | 485 | 485 → 577 facet assignments | 0 | 0 | Q6 three-facet expansion |
| primaryOutput | 485 | 485 | 0 | 0 | Q5 structured flow values |
| keyInputs | 485 | 485 | 0 | 0 | Q5 structured flow values |
| parkedChildren | 5 | 5 | 0 | 0 | → core:plannedChildNote |
| status | 2 | 0 | 2 | 0 | Q9 three-dimension model pending |
| **Total** | **5,571** | | | | |

\* relatedConcepts accounting is per-MENTION (one predicate triple carries ~2.7
mentions). 486 triples = 1,318 mentions = 1,129 emitting + 187 held + 2 redirected
to Q5 flow values. 1,129 emitting − 15 G2 enables (proposed: no triple) = 1,114
mention-triples → 921 canonical facts after 193 mirror merges.

Held totals: 488 (conceptTypeCheck) + 187 (relatedConcepts) + 2 (status) = 677
triples/mentions awaiting Q8/Q9 decisions or pending review outcomes.
Retired totals: 683 (level) with recorded rationale. **Nothing is dropped.**

## Predicate details

### terminologyNotes (491)
Deterministic classification rules (reviewed, not yet approved):
- `dcterms:provenance` — note documents a migration event: rename, prior-name
  carryover, tombstone re-anchor, label-change history, or an R1 reclassification move.
- decision-log reference — note's primary content is a pointer to a decision record
  ("decision recorded on", "per Hamid's decision (…)", "Hamid accepted Option …",
  "PTC-001 (step3c-parked-tree-changes.md)").
- `skos:editorialNote` — authoring/review history, batch notes, weak-match
  assessments, scope notes about the intake process itself.
- Dual-aspect (5): migration event + decision pointer — filed under provenance,
  decision pointer preserved in the note text.

Measured: **editorialNote 384 / provenance 95 / decision-log-ref 7 / dual-aspect 5.**
The promotion script must apply these exact rules; any note matching none falls to
a manual-review bucket (currently 0). Hamid approves the rules, then the run proves
491 = 384 + 95 + 7 + 5.

### referenceSources (488 triples → 737 resource links)
Tokenization: split cells on `|` (191 cells) and `;` (27 cells); strip annotation
suffixes (" — …"). Measured: **737 tokens = 728 clean SRC tokens + 9 SRC tokens
with annotation suffixes.** The 9 annotations are preserved as note text on the
resource link; 0 tokens unparseable. Every token links to the controlled
vocabulary of sources (SRC-APQC-PCF-001, SRC-OSHA-PSM-001, …).

### processHorizon (485 → 577 facet assignments)
Expansion rule (Q6): operatingMode ∈ {event-driven, continuous, periodic};
cadence ∈ {daily, weekly, monthly} implies operatingMode=periodic; planningLevel ∈
{tactical, strategic} for explicit tactical/strategic values.

Measured: operatingMode = event-driven 122 + continuous 93 + periodic
(107 explicit + 40 daily + 16 weekly + 36 monthly = 199) = **414**;
cadence = daily 40 + weekly 16 + monthly 36 = **92**;
planningLevel = tactical 44 + strategic 27 = **71**.
**Total facet assignments: 577.** Cadence-unspecified rows: 485 − 92 = 393 carry
no cadence assertion (absence recorded, not defaulted).

### primaryOutput / keyInputs (485 + 485)
Emitted as Q5 structured flow values (name + format + frequency + destination/source).
Structured-flow accounting: 2 `produces` mentions are structured flow values, not
relationships — they emit zero relationship triples (Q11, locked).

### responsibleDomain (485)
Interim: single governed literal per concept, cross-functional values kept verbatim
(12 concepts). No splitting until the ORG/RACI layer lands (Step 5).

### apqcDecision (500)
REVIEW LINK 287 / NO SOURCE 124 / NO CANDIDATE 78 / REJECTED 10 / ADOPTED 1.
Emitted verbatim as the audit trail of the APQC alignment decision.

### relatedConcepts (486 triples / 1,318 mentions)
Full accounting in `verb-predicate-mapping-v2.md` and `canonical-facts.csv`:

**Mention reconciliation (sums to 1,318):**

| bucket | count | composition |
|---|---|---|
| ResolvedToConcept / StableIdentifier | 239 | 203 carried from v1.1 + 35 strengthened (ContextualResolved→StableIdentifier, same target — carries per rule-3 exception) + 1 new R1 `informs` interface row (REL-00028) |
| ResolvedToConcept / ContextualInferredSibling | 42 | held for Hamid's review (sibling batch) |
| ResolvedToConcept / ContextualResolved | 1 | REL-00388 — resolution basis changed to contextual |
| SoleCandidate / CandidateOnly | 1,021 | 852 context-promoted + 169 context-held |
| AmbiguousDeferred | 12 | — |
| ExternalGovernanceReference | 1 | pending property design |
| StructuredFlowValue | 2 | `produces` → Q5 flow values, no process relationship |
| **Total** | **1,318** | 239+42+1+1021+12+1+2 |

(The 37 Hamid flagged: 35 strengthened + 1 new `informs` row + REL-00388.)

**Emission → facts derivation:**
1,129 emitting mentions (282 ResolvedToConcept + 852 promoted − 5 property-rule
holds: REL-00503 + 2 mutual-`enabledBy` pairs) − 15 G2 `enables` (no separate
triple) = **1,114 stored mention-triples** → **921 canonical facts**: 193 merged
facts absorb 386 mentions (386 − 193 = 193 duplicates removed), so
1,114 − 193 = 921 (728 singleton facts + 193 merged facts). Held: 174
(169 context + 5 property-rule) + 12 AmbiguousDeferred + 1
ExternalGovernanceReference. Redirected: 2 produces → Q5 flow values.
3 contradictions (`contradictions.csv`, all `dependsOnOutputOf` loops allowed
under the property rule); ruled pairs recorded in the mapping doc.

## Release checklist (Q2)

- [x] Baseline pinned to one approved main SHA; all evidence artifacts cite it.
- [x] Every predicate: source = emitted + held + retired, with the arithmetic shown.
- [x] terminologyNotes split defined with deterministic rules; counts measured.
- [x] referenceSources token accounting: separators, suffixes, unparseable = 0.
- [x] Horizon expansion counts and cadence-unspecified rows recorded.
- [x] Structured-flow accounting: produces emits zero relationship triples.
- [x] Per-verb relationship conservation table (mapping v2, per-verb counts).
- [x] Mentions → canonical facts → merged mirrors accounting.
- [x] Contradiction report produced for Hamid.
- [ ] Promotion script implements these rules and reproduces this ledger in a
      before/after reconciliation run (NOT YET BUILT — no implementation authorized).
- [ ] Fresh no-consumer attestation at release time (last: 2026-09-22 foundation-stage).
- [ ] Same-SHA release gate: re-pin to then-current approved main; every build and
      evidence artifact cites that identical SHA.

## Evidence already approved (carried, not re-decided)

- Q1–Q12 design decisions (PRs #119, #120 on main).
- Target disposition baseline v1.1: 1,317 mentions conserved; v2 diff = 53 raw-label
  updates (same candidates) + 1 approved R1 interface + 1 resolution-basis change.
- Sibling 42-row package: regenerated from pinned main (0 semantic-key mismatches,
  0 evidence-field diffs); reviewer decision fields blank.
- Historical labels v1.2: 90 carried by exact key; 14 new proposals for review.
- Context confirmation: corrected pass implemented; 51-row sample reviewed 51/51 OK.

## Nearness-only stratified review (2026-09-24, Hamid-approved plan)

Population: 161 B-only promoted rows (145 enables + 16 governed-by; REL-01312
excluded — held as a mutual-enabledBy pair). Seeded sample (seed 20260924):
8 enables same-parent + 8 enables cross-parent + 23 high-risk enables
(authority/approval/compliance/financial-control/policy terms) + all 16
governed-by = 55 rows. Review instrument:
`review-evidence/nearness-sample-review-batch.csv`.

Result: **50 approved, 1 error, 4 held by stratum stop.**

- enables strata (same-parent, cross-parent, high-risk): 39/39 approved, no
  errors. Automatic approval stands for the reviewed rows.
- governed-by: 11 approved, **1 error at REL-01143**, 4 held by stop rule.

**The error (REL-01143):** "Terminal Operations Management governed-by Develop
Compliance Policies & Procedures." Terminal operations (site safety, fleet,
asset integrity) was claimed governed by the *trading* compliance program's
policies (market-conduct, information barriers, personal-account dealing).
Unsupported cross-domain governance implication — structural nearness at L1
(CM-1-2) was too coarse to license a governance claim.

**Stop-rule application (Hamid 2026-09-24):** automatic approval stopped for
the governed-by stratum. The 11 individually human-reviewed OKs stand (human
review supersedes automatic approval). The 4 rows unreviewed at stop time
(REL-01228, REL-01256, REL-01286, REL-01313) are held with reason
"stratum stop after REL-01143"; the error row is held with the error reason.
The enables strata are unaffected.

**Diagnosed rule defect:** the B (structural-nearness) test licensed
governed-by promotions across L2 boundaries without checking that the target
policy's domain covers the source's activity. **Proposed fix (for Hamid's
approval):** governed-by promotion on nearness alone requires source and
target in the same L2 branch; cross-L2 governance claims go to human review.
Predicted effect: REL-01143-type rows held; also holds the weak cross-L2 rows
REL-00190, REL-00274, REL-00858, REL-00907, REL-01005, REL-01228, REL-01286,
REL-01313 for review. Re-run of the classifier and re-sampling follow Hamid's
approval of the fix.

## Decisions recorded 2026-09-24 (Hamid)

- 53 changed-label rows: 35 "Approval carried" under the documented
  evidence-strengthening exception (same subject/verb/candidate/disposition;
  validation performed on the semantic key); 18 "Pending review".
- 14 new historical-label rows: CM-1-1-4 and CM-1-1-7 approved **MigrationOnly**
  (do not add as aliases); 12 pending with expected dispositions.
- 11 slug-carried rows: REL-01309 approved (procedures-govern-parent /
  set-versus-apply); 10 held with `AncestorDescendantGovernanceAmbiguity`.
- Contradictions: sequence — none found (recorded); mutual `precedes` — hold
  both, fix workbook, no emission (none currently exist); three
  `dependsOnOutputOf` loops allowed as intentional feedback loops where each
  direction is independently evidenced; Safety ↔ Fleet — REL-00500 emits,
  REL-00503 held; two `enabledBy` mutual pairs — **all four rows held**
  (enablement not automatically reciprocal), review via
  `review-evidence/enabledby-mutual-review-batch.csv`.
- REL-01106: deferred for source-workbook correction (backlog).
- Locked principle: emission may emit, hold, or defer — it never changes the
  source verb or target. Corrections happen in the source workbook through
  reviewed authoring.

## Playbook PR (2026-09-24)

Docs-only PR #121 opened (branch `docs/step4-evidence-discipline`, base pinned
main `6ab2197ba3fe6246bdb501391d22b71d0338d2c7`): the Step 4 evidence-discipline
section with Hamid's six wording edits, placed after the step log / before §4
Decision log, plus a short Step 4 step-log pointer. Blast-radius proof: parent
is pinned main, exactly one file changed
(`business_architecture/ontology/ontology-playbook.md`). **DO NOT MERGE**
without Hamid's explicit approval. Local draft superseded by the PR.

## PR #121 merged (2026-09-24)

Hamid merged PR #121 at 2026-09-25T01:51:39Z. Merge commit
`577c3aa13d784f5f77bdf023c378aed79a70dc5a` is the new `main` head. The Step 4
evidence-discipline section (eleven rules, six edits applied) is merged **as
PROPOSED** — its own text says it becomes canonical only on Hamid's explicit
approval (via #122, after he reads the final wording). Until then, work to the
proposed rules but do not describe them as adopted. (Correction 2026-09-24: an
earlier ledger line called the section canonical; that was wrong.)

Note: the section's status blockquote still reads "PROPOSED 2026-09-24" —
stale now that the merge is the approval. Follow-up: flip it to Approved in a
tiny docs PR (awaiting Hamid's word).

Baseline note: the Step 4 evidence package remains pinned to
`6ab2197ba3fe6246bdb501391d22b71d0338d2c7` (the approved main at evidence
time). Per rule 1 / rule 10, re-pin to the then-current approved main before
the eventual release; the merge does not invalidate the pinned evidence.

## Status-flip follow-up (2026-09-24)

PR #121 merged with the section's PROPOSED marker stripped, but the Step 4
step-log pointer still read "(proposed 2026-09-24; canonical on Hamid's
approval)". Hamid approved the flip; docs-only PR #122 opened
(branch `docs/step4-evidence-discipline-approved`, parent = current main
`577c3aa1`, one file changed, blast radius proven). Ready for his merge.

## Row-level change section: 1,133 → 1,129 emitting (2026-09-24)

Every row that moved buckets since the 1,133-emitting version, per the
proposed evidence-discipline rules (rule 7: no record moves without a recorded
reason). Totals: emitting −4, canonical facts −4 (all four were singleton
facts), held +5, new-label pending −2.

| row_id | old bucket | new bucket | reason |
|---|---|---|---|
| REL-00503 | emitting (promoted) | held (property-rule) | Mutual `informedBy` with REL-00500; this direction nearness-only. Hamid 2026-09-24: emit only the independently evidenced direction. |
| REL-01303 | emitting (promoted, A+B) | held (property-rule) | Mutual `enabledBy` pair 1 (Trade Capture ↔ Market Risk Mgmt). Hamid 2026-09-24: enablement not automatically reciprocal; hold both pending review. |
| REL-01312 | emitting (promoted, B-only) | held (property-rule) | Same as REL-01303, other direction. |
| REL-01056 | emitting (promoted, stable-ID) | held (property-rule) | Mutual `enabledBy` pair 2 (Period-End Processing ↔ AR Reconciliation and Compliance). Same Hamid decision. |
| REL-01053 | emitting (promoted, stable-ID) | held (property-rule) | Same as REL-01056, other direction. |
| CM-1-1-4 (label row) | new-label pending | decided: MigrationOnly | R1 prior name ("Refinery Planning"); Hamid 2026-09-24 approved MigrationOnly, do not add as alias. |
| CM-1-1-7 (label row) | new-label pending | decided: MigrationOnly | R1 prior name ("Refinery Scheduling"); same decision. |

Held bucket composition now: 169 context-held + 5 property-rule holds
(REL-00503, REL-01303, REL-01312, REL-01056, REL-01053) = 174.

Not yet moved (recorded as review decisions, pipeline unchanged): REL-01143
(sample error) and the 4 governed-by stratum-stop rows remain promoted in the
mapping until the governed-by classifier re-run below.

## Governed-by re-run under the stricter rule (2026-09-24)

Hamid's amendment (2026-09-24): structural closeness alone **never** promotes
governed-by, at any level. Governance is a claim about authority; the
hierarchy says nothing about authority. Implemented in
`target-report/context_pass.py` (`_real()` excludes `B:structural-nearness`
for governed-by rows; B-only governed-by rows record
`tests_passed="B:structural-nearness (not evidence for governed-by)"` so the
evidence is visible, not hidden).

Re-run result: 16 governed-by rows moved from PROMOTE to HOLD (all B-only).
None had non-singleton facts.

| measure | before | after | change |
|---|---|---|---|
| context promoted | 852 | 836 | −16 |
| context held | 169 | 185 | +16 |
| emitting mentions | 1,129 | 1,113 | −16 |
| canonical facts | 921 | 905 | −16 |
| held (incl. 5 property-rule) | 174 | 190 | +16 |

Enables membership verified unchanged (282 promoted, same row set).
The 16 rows: 11 previously sample-OK (superseded — Hamid reviews all 16),
REL-01143 (sample error), 4 stratum-stop rows (absorbed). No overlap with the
10 ancestor/descendant held rows. Enables re-sample: not needed (membership
unchanged).

## EnabledBy verdicts recorded (2026-09-24)

Hamid's verdicts on the mutual-enabledBy special batch: emit one direction
per pair, hold the reverse. Neither pair is a genuine reciprocal
`core:enables` loop — the reverse direction means control/constraint or
close-feed consumption, not capability enablement.

Row-level changes:

| row_id | old bucket | new bucket | reason |
|---|---|---|---|
| REL-01303 | held (property-rule, pending review) | emitting (approved) | Hamid 2026-09-24: Trade Capture creates the deal record Market Risk measures; explicit reference, directionally sensible. |
| REL-01056 | held (property-rule, pending review) | emitting (approved) | Hamid 2026-09-24: reconciliation readiness enables a supported, evidenced close. |
| REL-01312 | held (property-rule, pending review) | held (source correction) | Hamid 2026-09-24: governance/constraint, not enablement. No `core:enables` triple; workbook correction via reviewed authoring (see source-workbook-backlog.md). |
| REL-01053 | held (property-rule, pending review) | held (source correction) | Hamid 2026-09-24: close verifies/consumes reconciliation evidence; does not enable it. Same correction path. |

New totals: emitting 1,115 (+2), held 188 (−2: 185 context + 3 property-rule),
canonical facts 907 (+2). Conservation: 1,115 + 188 + 12 + 1 + 2 = 1,318.

Recorded in: `review-evidence/enabledby-mutual-review-batch.csv` (decisions +
rationales), `target-report/target-dispositions-v2.csv` (emission_decision,
reason, review_trigger, decision_reference), `source-workbook-backlog.md`
(REL-01312, REL-01053), `verb-predicate-mapping-v2.md` (enablement
non-reciprocity rule 6), `evidence-gate.py` (four control-case regression
tests: REL-01303/REL-01056 must emit, REL-01312/REL-01053 must stay held).

Definitions adopted: reciprocal enablement (rare loop, separate evidence per
direction), control/constraint relationship (authority/limits under which a
process operates — not enablement), close-feed dependency (close
consumes/validates control-process evidence — not reciprocal enablement).

Open: whether the held reverse directions become `governs`/`constrains`/
`requires` (REL-01312) or `precedes`/`dependsOnOutputOf` (REL-01053) after
source review; whether similar reverse-enablement rows exist in the remaining
enablement cases.

## 32-row review run (2026-09-24/25)

Hamid's next action: record the enabledBy verdicts, then run the stratified
32-row review (16 enables sampled + all 16 governed-by in full) with the four
enabledBy decisions enforced as regression tests (done — see gate section 2b).

Worklist: `target-report/review32-worklist.json` (seed 20260925). Enables
sample: 8 same-parent + 8 cross-parent, all fresh (the 23 high-risk enables
were exhausted in round 1 — all reviewed). Governed-by: all 16 rows, for
Hamid's review (`review-evidence/governed-by-full-review-batch.csv`).

Assistant review of the 16 enables (`review-evidence/review32-enables-batch.csv`):
**12 approve (1 weak), 4 hold.** The 4 holds all follow the pattern Hamid
identified in the enabledBy verdicts — "enables" flattening "informs":
- REL-01131 (Supply Network Participation Analysis → Refined Product Demand
  Management): strategic scoping, not necessary for operational demand
  management. Better: informs.
- REL-01192 (Brand Strategy → Sales & Distribution Channel Strategy):
  positioning context for channel choice, not required. Better: informs.
- REL-00758 (Collaborate with Research Partners → Conduct Research): external
  collaboration not required for internal research. At most: supports.
- REL-01094 (Measure Service Infrastructure → Manage Technology): measurement
  evidence informs the roadmap; management does not require it. Better: informs.

These are recommendations; Hamid decides. Not applied to the pipeline.

## Enables-sample verdicts recorded (2026-09-25)

Hamid's verdicts on the 16-row enables sample: **11 approved as
`core:enables`, 4 held for source correction, 1 held for source classification
review.** More conservative than the reviewer's 12/4 — REL-00936 downgraded:
the revenue plan is not demonstrated as necessary for profitability analysis.

Row-level changes (5 rows emitting → held):

| row_id | old bucket | new bucket | reason |
|---|---|---|---|
| REL-00758 | emitting (B-only) | held (source correction) | "enables" flattens "informs"/"supports". Correct verb in workbook. |
| REL-01094 | emitting (B-only) | held (source correction) | "enables" flattens "informs". Correct verb in workbook. |
| REL-01131 | emitting (B-only) | held (source correction) | "enables" flattens "informs". Correct verb in workbook. |
| REL-01192 | emitting (B-only) | held (source correction) | "enables" flattens "informs". Correct verb in workbook. |
| REL-00936 | emitting (B-only) | held (classification review) | Business must confirm plan-based vs actual-data-based analysis. |

New totals: emitting 1,110 (−5), held 193 (+5: 185 context + 8 property-rule),
canonical facts 903 (−4; one held row shared a merge, which un-merged cleanly).
Conservation: 1,110 + 193 + 12 + 1 + 2 = 1,318.

Recorded in: `review-evidence/review32-enables-batch.csv` (16 decisions),
`target-report/target-dispositions-v2.csv` (16 decisions),
`source-workbook-backlog.md` (5 rows: 4 correction + 1 classification review),
`verb-predicate-mapping-v2.md` (enables/informs/dependsOnOutputOf/requires
distinctions + source-meaning rule + classification-review definition),
`evidence-gate.py` (16 new control-case regression tests; 20 total),
`mapping_v2.py` (PROPERTY_RULE_HOLDS: 8 rows).

Definitions adopted: enablement (source makes target able to operate),
influence/informs (context without necessity), source classification review
(business review when verb mismatches definitions).

## Governed-by verdicts recorded (2026-09-25)

Hamid's verdicts on the 16-row governed-by batch: **13 approved as
`core:governedBy` (4 with scope qualifiers), 3 held for source review.**
Approvals rest on explicit authority/policy/framework/set-versus-apply
language — none on hierarchy proximity, consistent with the stricter rule.
Promotion basis for the 13 is the recorded `D:hamid-verdict(2026-09-25)`
evidence test in `context_pass.py`; the B-exclusion rule is unchanged for all
other rows.

Row-level changes (13 rows held → emitting; 3 rows remain held with recorded
hold reasons):

| row_id | old bucket | new bucket | reason |
|---|---|---|---|
| REL-00050 | held (B-only) | emitting | Approved: inventory policy set-versus-apply |
| REL-00067 | held (B-only) | emitting | Approved: explicit within-policy operation |
| REL-00190 | held (B-only) | emitting | Approved: Market Risk owns risk-book/delegation/limits |
| REL-00394 | held (B-only) | emitting | Approved: compliance set-versus-apply |
| REL-00399 | held (B-only) | emitting | Approved: controls verified against program policies |
| REL-00406 | held (B-only) | emitting | Approved: RIN reporting under program requirements |
| REL-00858 | held (B-only) | emitting | Approved: rebate negotiation within approved pricing architecture |
| REL-00907 | held (B-only) | emitting | Approved with scope qualifier: IP/licensing/protected-mark boundaries only |
| REL-00937 | held (B-only) | emitting | Approved: Treasury/Credit-approved instruments and rules |
| REL-01005 | held (B-only) | emitting | Approved: self-billing under executed agreement framework |
| REL-01228 | held (B-only) | emitting | Approved with scope qualifier: trading-compliance/reporting/market-rule boundaries only |
| REL-01256 | held (B-only) | emitting | Approved with scope qualifier: credit-control gates within fulfillment only |
| REL-01313 | held (B-only) | emitting | Approved with scope qualifier: credit eligibility/limits/holds constraints only |
| REL-00274 | held (B-only) | held (source review) | DOA framework ownership not evidenced in Regulatory & Compliance |
| REL-01143 | held (B-only) | held (known error) | Terminal operations vs trading-compliance policies |
| REL-01286 | held (B-only) | held (source review) | Credit Risk is independent; no compliance authority over credit policy |

New totals: emitting 1,123 (+13), held 180 (−13: 172 context + 8 property-rule),
canonical facts 916 (+13; all singleton facts).
Conservation: 1,123 + 180 + 12 + 1 + 2 = 1,318.

Note on verdict arithmetic: Hamid's message carried three different totals
(heading "approve 11, hold 5, defer 1"; footer "Approved: 12, Held: 3"; per-row
table 13 approve + 3 hold = 16). Recorded the per-row table — the only one
summing to the 16-row batch — and flagged the discrepancy for confirmation.

Recorded in: `review-evidence/governed-by-full-review-batch.csv` (16 decisions),
`target-report/target-dispositions-v2.csv` (16 decisions),
`source-workbook-backlog.md` (3 rows: REL-00274, REL-01143, REL-01286),
`verb-predicate-mapping-v2.md` (governed-by definition, scope-qualified
governance relation, emission guard), `evidence-gate.py` (16 new control-case
regression tests; 36 total), `target-report/context_pass.py`
(HAMID_APPROVED_GOVERNED_BY + D:hamid-verdict evidence test).

Definitions adopted: governed-by (operates within target-owned policy/
authority/framework/delegation/limit/rule); scope-qualified governance
relation (named control boundary, not operational ownership).

Next per Hamid: the 18 changed-label rows and 12 new historical-label rows,
then unblocking the Step 4 migration script.

## Label batches recorded; REL-00445 held (2026-09-25)

Hamid's verdicts: **12 historical-label rows approved as proposed**
(3 AddAsAltLabel, 1 MigrationOnly, 8 RetainAsAltLabel); **18 changed-label
rows: 17 carry existing decisions forward, REL-00445 held for source
correction** (enables → informed-by; PTC-002: planning decides, trading
advises).

Row-level change (1 row emitting → held):

| row_id | old bucket | new bucket | reason |
|---|---|---|---|
| REL-00445 | emitting (A:explicit-reference) | held (source correction) | Recommendation informs planning; not capability enablement. Correct verb in workbook. |

New totals: emitting 1,122 (−1), held 181 (+1: 172 context + 9 property-rule),
canonical facts 915 (−1; singleton, no merge impact).
Conservation: 1,122 + 181 + 12 + 1 + 2 = 1,318.

The 17 carried rows: slug unchanged on all 18, verb unchanged, source meaning
unchanged — 7 remain context-held, 10 remain emitting on their existing basis.

Recorded in: `review-evidence/historical-label-12-review-batch.csv` (12
decisions), `label-report/label-dispositions-v1.2.csv` (12 decisions),
`review-evidence/changed-label-18-review-batch.csv` (18 decisions),
`target-report/target-dispositions-v2.csv` (REL-00445 hold + 18 review
triggers), `source-workbook-backlog.md` (REL-00445),
`verb-predicate-mapping-v2.md` (recommendation-vs-enablement rule, PTC-002),
`evidence-gate.py` (REL-00445 control-case regression test; 37 total),
`mapping_v2.py` (PROPERTY_RULE_HOLDS: 9 rows).

Definition adopted: recommendation rule (advisory input is informed-by, not
enables, even when it feeds a binding decision).

## Verb-mapping review prep (2026-09-25, per Hamid's sequence)

**G1 split** (rule 11): 112 G1 rows split by reverse-pair evidence —
**G1a 81** (a `uses-input` mention states the same pair; merge as extra
evidence = duplicate merge, not a verb change), **G1b 31** (only an
`informed-by` mention exists; merging into `dependsOnOutputOf` would change
the verb → proposed hold for workbook correction).
`review-evidence/enables-g1-split.csv`.

**S&T enables search** (REL-00445 pattern): 21 rows where the source
definition says recommend/advise. Triaged by reading each definition —
**5 pattern-holds** (source advises, target decides), **9 genuine**
(source builds the base the target operates on), **7 ambiguous** (Hamid
decides). The search is a candidate filter, not a verdict.
`review-evidence/st-enables-search.csv`.

**G3 evidence column** (refreshed 2026-09-26 against current dispositions):
249-row review population — **143 explicit-reference** (54 ResolvedToConcept
+ 89 SoleCandidate/PROMOTE-A) and **106 nearness-only**
(SoleCandidate/PROMOTE-B); the 21 context-held G3 rows are out of scope.
Section A6 decided 2026-09-26 (final explicit-reference chunk): 4 approved
(REL-01274, REL-01298, REL-01303, REL-01311; basis to D:hamid-verdict; scope
conditions on each), 2 held (REL-01277 adjacent execution, REL-01299
independent-function exclusion; facts removed after uniqueness
validation). Section A is now COMPLETE: 143/143 explicit-reference rows
decided (131 new A1–A6 verdicts + 12 prior-held reconciliation-only). New
boundary definitions: Framework-versus-enablement boundary,
Independent-function exclusion. G3 now: 179 emitting, 66 mapping-held + 21
context-held. Remaining G3 work: 96 undecided Section B nearness-only rows
(+ 10 already-held reconciliation rows).
`review-evidence/enables-g3-genuine-enablement-review-batch.csv`
(supersedes the 2026-09-25 `enables-g3-evidence-batch.csv`).

**Stored-fact regression tests**: control cases rewritten to assert the
stored canonical triple — approved `enables` = `(target, core:enabledBy,
source)`; held rows must contribute to no stored triple. Pipeline updated:
`EN_ENABLEDBY_OVERRIDE` (13 rows) implements the row-level verdicts,
overriding the G1/G2 group proposal. Facts 915 → 920 (+5: 3 G1a + 2 G2 now
stored as enabledBy). Gate green, 37 control cases.

**Mapping doc refreshed**: 1,122 emitting / 181 held / 920 facts; per-verb
table and enables accounting reconciled to the row level (242 G3 + 5
verdicts + 77 G1a + 30 G1b + 13 G2 = 367). Sequence section updated.

**Definition adopted**: duplicate merge — an extra mention of a fact already
stored, recorded as evidence; not a verb change.

**Requires batch** ready: `review-evidence/requires-6-review-batch.csv`
(6 rows, full definitions, reviewer notes). REL-00208's proposed remap
flagged as a verb change at emission time — expected hold, not remap.

## 2026-09-25 — Requires verdicts recorded (Hamid)

Decision basis: requires-6-review-batch.csv (6/6 decided).

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-00158 | emitting (proposed `core:requires`) | emitting (`core:requires`, D:hamid-verdict) | Approved: genuine credit-clearance precondition |
| REL-00168 | emitting (proposed `core:requires`) | emitting (`core:requires`, D:hamid-verdict) | Approved: valid closure-control prerequisite |
| REL-00247 | emitting (proposed `core:requires`) | emitting (`core:requires`, D:hamid-verdict) | Approved: clear lifecycle dependency |
| REL-00872 | emitting (proposed `core:requires`) | emitting (`core:requires`, D:hamid-verdict) | Approved: legitimate KYC onboarding gate |
| REL-00873 | emitting (proposed `core:requires`) | emitting (`core:requires`, D:hamid-verdict) | Approved with scope note: credit-controlled onboarding prerequisite only, not every prospect setup |
| REL-00208 | emitting (proposed remap to `core:dependsOnOutputOf`) | held — source-workbook correction | Neither requires nor dependsOnOutputOf supported; remap at emission would change source meaning |

**Bucket totals:** emitting 1,122 → **1,121** (−1); held 181 → **182** (+1);
deferred 12; external-governance 1; structured-flow 2. Canonical facts
920 → **919** (−1; REL-00208's dependsOnOutputOf fact removed, nothing replaces
it). Conservation: 1,121 + 182 + 12 + 1 + 2 = 1,318 ✓.

**Standing rule (Hamid 2026-09-25):** approving a row that is already emitting
changes only its basis (proposed → D:hamid-verdict); counts move only when a
row changes bucket. The 5 approved requires rows were already emitting, so the
+5 expectation in the verdict brief was corrected to a basis change only.

**Ledger-flag:** the provisional expectation in the verdict brief was
+5 emitting (1,127). The 5 approved rows were already emitting under the
proposed mapping — approvals change the decision basis (proposed →
D:hamid-verdict), not the bucket. The only bucket change is REL-00208
emitting → held. No triple merges/drops occurred: the 5 approved
(core:requires) stored triples were and remain fact-distinct.

## 2026-09-26 — Assures verdicts recorded (Hamid)

Decision basis: assures-8-review-batch.csv (8/8 decided; 0 deferred).

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-00401 | emitting (proposed `core:assuredBy`) | emitting (`core:assuredBy`, D:hamid-verdict) | Approved: tax-compliance control assurance |
| REL-00719 | emitting (proposed `core:assuredBy`) | emitting (`core:assuredBy`, D:hamid-verdict) | Approved: management/quality assurance of research conduct |
| REL-00801 | emitting (proposed `core:assuredBy`) | emitting (`core:assuredBy`, D:hamid-verdict) | Approved: bounded brand-compliance assurance over campaigns |
| REL-01269 | emitting (proposed `core:assuredBy`) | emitting (`core:assuredBy`, D:hamid-verdict) | Approved: regulatory/compliance assurance over Trading Management |
| REL-01270 | emitting (proposed `core:assuredBy`) | emitting (`core:assuredBy`, D:hamid-verdict) | Approved: regulatory/compliance assurance over Settlements |
| REL-00355 | held (context) | held (context) | No change: documents support/evidencing is not assurance |
| REL-00385 | held (context) | held (context) | No change: reporting support is not assurance |
| REL-01106 | emitting (`core:assuredBy` fact) | held — source-workbook correction | Supply-position management does not assure demand management; existing fact removed, no substitute |

**Bucket totals:** emitting 1,121 → **1,120** (−1); held 182 → **183** (+1);
deferred 12; external-governance 1; structured-flow 2. Canonical facts
919 → **918** (−1; REL-01106's `core:assuredBy` fact was unique — verified
no other row stored the identical fact). Conservation: 1,120 + 183 + 12 + 1
+ 2 = 1,318 ✓. Per the basis/bucket standing rule, the five approvals
changed only the decision basis.

## 2026-09-26 — Constrained-by verdicts recorded (Hamid)

Decision basis: constrained-by-11-review-batch.csv (11/11 decided; 0 deferred).

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-00015 | emitting (proposed `core:constrainedBy`) | emitting (`core:constrainedBy`, D:hamid-verdict) | Approved: inventory-bound allocation |
| REL-00018 | emitting (proposed `core:constrainedBy`) | emitting (`core:constrainedBy`, D:hamid-verdict) | Approved: inventory-bound allocation |
| REL-00024 | emitting (proposed `core:constrainedBy`) | emitting (`core:constrainedBy`, D:hamid-verdict) | Approved: inventory-bound planning |
| REL-00087 | emitting (proposed `core:constrainedBy`) | emitting (`core:constrainedBy`, D:hamid-verdict) | Approved: refinery operating-envelope bound |
| REL-00091 | emitting (proposed `core:constrainedBy`) | emitting (`core:constrainedBy`, D:hamid-verdict) | Approved: refinery operating-envelope bound |
| REL-00099 | emitting (proposed `core:constrainedBy`) | emitting (`core:constrainedBy`, D:hamid-verdict) | Approved canonical inversion of source `constrains`; original assertion preserved in fact row (`raw_verbs: constrains`) |
| REL-00103 | emitting (proposed `core:constrainedBy`) | emitting (`core:constrainedBy`, D:hamid-verdict) | Approved: inventory-bound capture |
| REL-00574 | emitting (proposed `core:constrainedBy`) | emitting (`core:constrainedBy`, D:hamid-verdict) | Approved: terminal lifting allocation controls |
| REL-00894 | emitting (proposed `core:constrainedBy`) | emitting (`core:constrainedBy`, D:hamid-verdict) | Approved: genuine credit-control constraint |
| REL-01284 | emitting (proposed `core:constrainedBy`) | emitting (`core:constrainedBy`, D:hamid-verdict) | Approved: inventory-bound optimization |
| REL-00097 | held (context) | held (context) | No change: broad undefined Refining target; backlog row 14 added for target clarification |

**Bucket totals:** emitting **1,120**; held **183**; deferred 12;
external-governance 1; structured-flow 2. Canonical facts **918**. Conservation:
1,120 + 183 + 12 + 1 + 2 = 1,318 ✓. This batch produced **basis changes
only** — no row moved buckets.

**Provenance check:** REL-00099 is the only `constrains` row in the population;
its fact row carries `raw_verbs: constrains` and the inversion note, so
source-direction provenance is intact.

## 2026-09-26 — Triggers verdicts recorded (Hamid)

Decision basis: triggers-18-review-batch.csv (18/18 decided; 0 deferred).

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-00049, REL-00127, REL-00163, REL-00169, REL-00170, REL-00235, REL-00236, REL-00246, REL-00252, REL-00291, REL-00396, REL-00398, REL-00400, REL-00403, REL-00725, REL-00892, REL-00897, REL-00901 | emitting (proposed `core:triggeredBy`) | emitting (`core:triggeredBy`, D:hamid-verdict) | Approved: identifiable event/exception/threshold/handoff invoking the target; stored direction (triggered → trigger) correct |

**Bucket totals:** emitting **1,120**; held **183**; deferred 12;
external-governance 1; structured-flow 2. Canonical facts **918**. Conservation:
1,120 + 183 + 12 + 1 + 2 = 1,318 ✓. This batch produced **basis changes
only** — no row moved buckets. Scope notes recorded for the card-process
triggers (conditional workflow triggers, not universal) and the four
compliance-monitoring rows (monitoring-finding → exception-workflow pattern).

## 2026-09-26 — dependsOnOutputOf contradiction verdicts recorded (Hamid)

Decision basis: dependsOnOutputOf-3-contradictions-batch.csv (3 pairs / 6 rows).

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-00862 | emitting (`core:dependsOnOutputOf`) | emitting (D:hamid-verdict) | Pair A retained: rebate implementation consumes maintained price/discount master data |
| REL-00917 | emitting (`core:dependsOnOutputOf`) | held — workbook correction | Pair A reverse: definitions don't show consumption of implemented-rebate output; fact removed |
| REL-01029 | emitting (`core:dependsOnOutputOf`) | emitting (D:hamid-verdict) | Pair B retained: reconciliation consumes card-transaction records/exceptions |
| REL-00884 | emitting (`core:dependsOnOutputOf`) | held — workbook correction | Pair B reverse: may be exception feedback/remediation loop; fact removed |
| REL-01061 | emitting (`core:dependsOnOutputOf`) | emitting (D:hamid-verdict) | Pair C retained on definitions; ContextualInferredSibling supplementary only |
| REL-01065 | emitting (`core:dependsOnOutputOf`) | held — workbook correction | Pair C reverse: may be feedback/reporting-impact consideration; fact removed |

**Bucket totals:** emitting 1,120 → **1,117** (−3); held 183 → **186** (+3);
deferred 12; external-governance 1; structured-flow 2. Canonical facts
918 → **915** (−3; each removed reverse fact was verified unique, single-row).
Conservation: 1,117 + 186 + 12 + 1 + 2 = 1,318 ✓.

**Hard rule adopted:** no reciprocal `core:dependsOnOutputOf` two-cycles may be
emitted; `contradictions.csv` must stay at 0; the gate asserts zero cycles
globally plus six presence/absence controls.

## 2026-09-26 — Ancestor/descendant governance verdicts recorded (Hamid)

Decision basis: ancestor-descendant-10-review-batch.csv (10/10 held; REL-01309
excluded as an already-approved exception — untouched, original evidence marker
and rationale unchanged).

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-00002, REL-00013, REL-00466, REL-00469, REL-00764, REL-00768, REL-00773, REL-00912, REL-00923, REL-00925 | emitting | held — hierarchy restatement | Parent/child containment; no independent cross-cutting governance, output-dependency, or enablement evidence; facts removed (each verified unique, single-row) |

**Bucket totals:** emitting 1,117 → **1,107** (−10); held 186 → **196** (+10);
deferred 12; external-governance 1; structured-flow 2. Canonical facts
915 → **905** (−10). Conservation: 1,107 + 196 + 12 + 1 + 2 = 1,318 ✓.

**Rule adopted:** ancestor/descendant non-duplication — no semantic
relationship may emit solely because source and target are in an
ancestor/descendant or same-branch parent-child relationship; a
hierarchy-adjacent row may emit only with documented independent evidence,
all five exception conditions, and explicit reviewer approval. REL-01309
remains a recorded exception with its own rationale, not a precedent.

## 2026-09-26 — Supply & Trading enables verdicts recorded (Hamid)

Decision basis: st-enables-21-review-batch.csv (21/21 decided; 0 deferred).

| Rows | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-00433, REL-00437, REL-00489, REL-01124, REL-01172, REL-01174 | emitting | emitting (D:hamid-verdict) | Approved as genuine, bounded enablement (maintained/quality-controlled base). REL-00489: reviewer-approved core:enabledBy (override of G1-redundant group proposal) |
| REL-00152, REL-00262, REL-00458, REL-01122, REL-01129 | emitting | held — workbook correction | Advisory/recommendation pattern (REL-00445 family): source advises, target decides. No emission-time remap |
| REL-00263, REL-00436, REL-00440, REL-00455, REL-00712, REL-00750, REL-01064, REL-01206 | emitting | held — workbook correction | Ambiguous enables; may be informational, output dependency, event handoff, or no separate relationship. No emission-time remap |
| REL-00466, REL-00469 | held | held | Existing hierarchy holds; no change |

**Uniqueness validation:** 11 of the 13 held facts were unique single-row facts
and removed. Two facts had independent approved evidence and are preserved:
- `(CM-1-2-1-4 core:dependsOnOutputOf CM-1-2-1-1-4)` — REL-00152's evidence removed; survives via REL-00214 (`uses-input`).
- `(CM-1-2-5-2-3 core:dependsOnOutputOf CM-1-2-5-1-4)` — REL-00436's evidence removed; survives via REL-00447 (`uses-input`).

*Update 2026-09-26 (uses-input pass): REL-00214 held (no citation route); its fact removed. REL-00152 held with it. Only REL-00447's fact survives.*

**Bucket totals:** emitting 1,107 → **1,094** (−13); held 196 → **209** (+13);
deferred 12; external-governance 1; structured-flow 2. Canonical facts
905 → **894** (−11). Conservation: 1,094 + 209 + 12 + 1 + 2 = 1,318 ✓.

**Rules reinforced:** enablement = a maintained, governed, or operationally
necessary capability/input base that makes the target able to perform its
function — not advisory input, evaluation, decision proposals, approval
submissions, ordinary sequence, a potential output dependency, or a broad
parent-child relationship. No emission-time remapping: an `enables` assertion
that seems better expressed as another predicate is held until source
correction; semantic plausibility alone never authorizes reclassification.
PTC-002 (Refinery Planning and Optimization decides; Supply & Trading advises)
remains the recommendation-versus-enablement control.

## 2026-09-26 — G1a duplicate-merge verdicts recorded (Hamid)

Population-level ruling for the G1a batch: 77 rows approved as
`MergeAsDuplicateEvidence`. Provenance and decision basis only — no bucket
or fact-count movement.

**Report-quality defect fixed first:** the batch generator emitted
`<generator object ...>` into `pipeline_emission_status`. The batch was
regenerated with deterministic values
(`DUPLICATE_MERGE / canonical fact retained via <uses-input row-ids>`) and
every row exposes its named independent supporter in `merged_with_rows`.

**Exclusions (4 of the original 81, not G1a):**
| Row | Reason |
|---|---|
| REL-00243, REL-00304, REL-01006 | Row-level approved `core:enabledBy` facts (Hamid verdicts) — independent facts, not duplicates |
| REL-00936 | Held for source-classification review; not finalized |

**Special provenance handling:** REL-00152 and REL-00436 re-attached as
duplicate provenance on their independently-evidenced `uses-input` facts
(via REL-00214 and REL-00447). `raw_verbs` preserves `uses-input; enables`.
The facts survive through the approved `uses-input` rows alone.

*Update 2026-09-26: Only REL-00447's fact survives; REL-00214's fact was removed (see above).*

**Bucket totals:** emitting 1,094; held 209; deferred 12; external-governance 1;
structured-flow 2. Canonical facts 894. Conservation:
1,094 + 209 + 12 + 1 + 2 = 1,318 ✓. Gate controls assert: 77 approved rows,
every row names ≥1 independent `uses-input` partner, every fact survives on
independent evidence, no G1a row is sole evidence, no new fact created.

## 2026-09-26 — G2 disguised-sequence verdicts recorded (Hamid)

Batch ruling for the 15-row G2 batch
(`review-evidence/enables-g2-disguised-sequence-review-batch.csv`):

- **13 rows approved as `NoSeparateEnablesFact`** (APPROVE / D:hamid-verdict):
  REL-00122, REL-00135, REL-00174, REL-00216, REL-00375, REL-00698, REL-00727,
  REL-00731, REL-00955, REL-00983, REL-00992, REL-01024, REL-01090. Each
  connects same-parent sibling activities with an independently recorded
  `precedes`/`follows` fact; the definitions support workflow sequence,
  handoff, or prerequisite ordering — not a distinct capability-enablement
  relationship. The enables assertion is kept as non-emitting evidence; no
  `core:enabledBy` fact is emitted and the assertion is not remapped to
  another predicate.
- **2 rows retain prior row-level `core:enabledBy` approvals**
  (APPROVE / D:hamid-verdict / ExistingRowLevelApproval): REL-00129
  (Manage Production Schedule Exceptions → Measure Production Scheduling
  Performance) and REL-00728 (Set up Intellectual Asset Framework → Protect
  Intellectual Assets). Group classification never overrides a named,
  recorded row-level verdict.

**Control rule implemented:** disguised-sequence control — same-parent plus
sequence is a promotion block, not proof the source assertion is wrong; a
previously approved, explicitly evidenced row-level exception wins over the
group classifier and retains its original rationale. Recorded in
`verb-predicate-mapping-v2.md`; asserted by the evidence gate (section 2o).

**Bucket totals:** emitting 1,094; held 209; deferred 12; external-governance 1;
structured-flow 2. Canonical facts 894. Conservation:
1,094 + 209 + 12 + 1 + 2 = 1,318 ✓. Decision basis only — no row changed
bucket, no fact count moved.

## 2026-09-26 — G1b no-verb-change verdicts recorded (Hamid)

Batch ruling for the 31-row G1b batch
(`review-evidence/enables-g1b-verb-change-risk-review-batch.csv`):

- **29 rows HELD** (HOLD / D:hamid-verdict / G1bNoVerbChange): the source
  assertion uses `enables`; the only paired evidence is the inverse
  `informed-by` assertion; no independently approved `uses-input`
  assertion exists for the pair. Emitting `core:dependsOnOutputOf` would
  silently change the source assertion's meaning, which Rule 11
  prohibits. The enables row is retained as non-emitting source
  evidence; the separate informed-by fact is preserved on its own
  source record; no replacement predicate is emitted. A corrected source
  assertion requires a fresh verdict.
- **2 rows reconciled, not re-decided:** REL-00489 (prior bounded approval
  as `core:enabledBy` — unchanged) and REL-00469 (prior hierarchy-hold —
  remains non-emitting).

**Repair defect fixed first:** the original batch claimed
`VERB_CHANGE_RISK / only apparent match is informed-by via no partner...`
but named no informed_by_rows on any of the 31 rows. The repaired batch
names the actual reverse informed-by row and its emission status for
every candidate before Hamid's review.

**Fact-provenance uniqueness validation:** all 28 removed
`core:dependsOnOutputOf` facts were unique single-row facts — each
supported only by its G1b enables row, with no independent approved
supporter for the identical canonical fact. All 28 facts removed;
no fact retained via other evidence. Reverse informed-by facts for all
28 pairs remain present on their own records.

**Row-level changes** (old bucket → new bucket; reason identical for all
28: HOLD under G1bNoVerbChange — enables assertion with only reverse
informed-by evidence cannot emit core:dependsOnOutputOf, Rule 11):

| Row | Old bucket | New bucket |
|---|---|---|
| REL-00140 | emitting | held |
| REL-00499 | emitting | held |
| REL-00565 | emitting | held |
| REL-00648 | emitting | held |
| REL-00679 | emitting | held |
| REL-00709 | emitting | held |
| REL-00732 | emitting | held |
| REL-00973 | emitting | held |
| REL-00974 | emitting | held |
| REL-00977 | emitting | held |
| REL-01108 | emitting | held |
| REL-01112 | emitting | held |
| REL-01148 | emitting | held |
| REL-01151 | emitting | held |
| REL-01154 | emitting | held |
| REL-01181 | emitting | held |
| REL-01184 | emitting | held |
| REL-01191 | emitting | held |
| REL-01194 | emitting | held |
| REL-01197 | emitting | held |
| REL-01213 | emitting | held |
| REL-01225 | emitting | held |
| REL-01230 | emitting | held |
| REL-01233 | emitting | held |
| REL-01234 | emitting | held |
| REL-01273 | emitting | held |
| REL-01296 | emitting | held |
| REL-01315 | emitting | held |
| REL-01224 | held (context-confirmation) | held (same verdict recorded) |

**Bucket totals:** emitting 1,094 → **1,066** (−28); held 209 → **237**
(+28); deferred 12; external-governance 1; structured-flow 2. Canonical
facts 894 → **866** (−28). Conservation:
1,066 + 237 + 12 + 1 + 2 = 1,318 ✓.

**Gate control:** `g1b-no-verb-change` implemented as a hard promotion
gate — an enables row with only opposite-direction informed-by
counterpart and no independently approved uses-input evidence must not
emit `core:dependsOnOutputOf`; the source assertion may be retained only
as non-emitting evidence unless it receives a separate explicit
row-level `core:enabledBy` approval. The gate stays red until every such
fact emission is removed, then passes only on proven fact provenance.

## 2026-09-26 — G3 Section A1 verdicts recorded (Hamid)

Section A1: first 25 undecided explicit-reference rows
(`review-evidence/enables-g3-section-a1-review.csv`), REL-00009 → REL-00211.

- **19 rows APPROVED** (APPROVE / D:hamid-verdict) as genuine, bounded
  `core:enabledBy`: the sources supply policies, governed terms,
  operational parameters, or controlled records that make the target
  processes able to operate. **Basis change only** — all 19 were already
  emitting; no bucket or fact-count movement.
- **6 rows HELD** (HOLD / D:hamid-verdict): exclusion references
  (REL-00009, REL-00054, REL-00077), informational/evidence feeds
  (REL-00041, REL-00118), lifecycle/sequence assertion (REL-00176).
  Explicit target identification is not enablement proof. Stored
  `core:enabledBy` facts removed; no substitute predicate emitted;
  enables assertions retained as non-emitting evidence; routed for
  source-workbook correction.

**Fact-provenance uniqueness validation:** all 6 removed `core:enabledBy`
facts were unique single-row facts (mention_count 1, row_ids = the held
row only), with no independent approved supporter. All 6 removed; no fact
retained via other evidence.

**Row-level changes:**

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-00009 | emitting | held | G3-A1: exclusion reference, not enablement |
| REL-00041 | emitting | held | G3-A1: informational feed, not capability enablement |
| REL-00054 | emitting | held | G3-A1: exclusion; policy ≠ operational capability |
| REL-00077 | emitting | held | G3-A1: exclusion reference, not enablement |
| REL-00118 | emitting | held | G3-A1: input/evidence feed, not proven enablement |
| REL-00176 | emitting | held | G3-A1: lifecycle relation, wrong direction |
| REL-00027 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00038 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00043 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00052 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00053 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00060 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00065 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00074 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00108 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00160 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00161 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00172 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00177 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00178 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00179 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00180 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00196 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00199 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |
| REL-00211 | emitting | emitting | G3-A1 APPROVED — basis to D:hamid-verdict |

**Bucket totals:** emitting 1,066 → **1,060** (−6); held 237 → **243**
(+6); deferred 12; external-governance 1; structured-flow 2. Canonical
facts 866 → **860** (−6). Conservation:
1,060 + 243 + 12 + 1 + 2 = 1,318 ✓.

**Gate:** all 393 evidence-gate checks pass (conservation assertions updated
to 860 facts). Promotion remains blocked pending completion
of G3 review and the mapping-document review.

## 2026-09-26 — G3 Section A2 verdicts recorded (Hamid)

Section A2: next 25 undecided explicit-reference rows
(`review-evidence/enables-g3-section-a2-review.csv`), REL-00217 → REL-00517.

- **19 rows APPROVED** (APPROVE / D:hamid-verdict) as genuine, bounded
  `core:enabledBy`: decision criteria, limits, control structures,
  approved terms, operational demand signals, or service capability that
  makes the target able to operate. **Basis change only** — no bucket or
  fact-count movement.
- **6 rows HELD** (HOLD / D:hamid-verdict): analytical advice
  (REL-00232), output contribution (REL-00294), operational feedback
  (REL-00409), informational feed (REL-00479), excluded scope
  (REL-00493), documentation contribution (REL-00517). Stored
  `core:enabledBy` facts removed; no substitute predicate emitted;
  enables assertions retained as non-emitting evidence; routed for
  source-workbook correction.

**Fact-provenance uniqueness validation:** all 6 removed `core:enabledBy`
facts were unique single-row facts (mention_count 1, row_ids = the held
row only), with no independent approved supporter. All 6 removed; no fact
retained via other evidence.

**Row-level changes:**

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-00232 | emitting | held | G3-A2: analytical advice, not enablement |
| REL-00294 | emitting | held | G3-A2: output contribution; no silent remap |
| REL-00409 | emitting | held | G3-A2: operational feedback, not foundation |
| REL-00479 | emitting | held | G3-A2: informational feed, no executable capability |
| REL-00493 | emitting | held | G3-A2: excluded scope owned by target |
| REL-00517 | emitting | held | G3-A2: documentation contribution, not enablement |
| REL-00217 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00220 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00221 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00223 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00226 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00254 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00255 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00272 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00273 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00276 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00284 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00367 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00386 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00391 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00433 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00472 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00473 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00475 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |
| REL-00501 | emitting | emitting | G3-A2 APPROVED — basis to D:hamid-verdict |

**Bucket totals:** emitting 1,060 → **1,054** (−6); held 243 → **249**
(+6); deferred 12; external-governance 1; structured-flow 2. Canonical
facts 860 → **854** (−6). Conservation:
1,054 + 249 + 12 + 1 + 2 = 1,318 ✓.

**Gate:** all 393 evidence-gate checks pass (conservation assertions
updated to 854 facts). Promotion remains blocked.

## 2026-09-26 — G3 Section A3 verdicts recorded (Hamid)

Section A3: 25 explicit-reference rows (`review-evidence/enables-g3-section-a3-review.csv`),
REL-00528 → REL-00852.

**Count reconciliation (authoritative = row-level table):** the message
summary said "14 approve / 11 hold" but the verdict table lists **12
approvals and 13 holds**; the table was applied per Hamid's instruction
that the row-level decisions are the intended substance.

- **12 rows APPROVED** (APPROVE / D:hamid-verdict): approved strategic
  direction, operating calendars, authority frameworks, governed pricing
  direction, integrated plans, or release-ready deliverables that make
  the target able to operate. **Basis change only** — no bucket or
  fact-count movement. Scope condition recorded: the brand/promotion
  approvals do NOT transfer authorization — the source gains no media-buying
  authority, procurement commitment, in-market deployment, or release
  approval; the approval is limited to the governed directional base.
- **13 rows HELD** (HOLD / D:hamid-verdict): four documentation feeds
  (REL-00528, REL-00539, REL-00551, REL-00562), partitioned ownership
  (REL-00665, REL-00846), forecast inputs (REL-00811, REL-00834),
  analytical feedback (REL-00818, REL-00820), hierarchy-adjacent
  (REL-00843), informational contributions (REL-00851, REL-00852).
  Stored `core:enabledBy` facts removed; no substitute predicate emitted;
  enables assertions retained as non-emitting evidence; routed for
  source-workbook correction.

**Fact-provenance uniqueness validation:** all 13 removed `core:enabledBy`
facts were unique single-row facts (mention_count 1, row_ids = the held
row only), with no independent approved supporter. All 13 removed; no fact
retained via other evidence. (REL-00851 and REL-00852 share a source but
have different targets — distinct facts.)

**Row-level changes:**

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-00528 | emitting | held | G3-A3: documentation feed (company findings) |
| REL-00539 | emitting | held | G3-A3: documentation feed (consumer findings) |
| REL-00551 | emitting | held | G3-A3: documentation feed (customer/marketer findings) |
| REL-00562 | emitting | held | G3-A3: documentation feed (competitor findings) |
| REL-00665 | emitting | held | G3-A3: partitioned ownership (channel design vs partner mgmt) |
| REL-00811 | emitting | held | G3-A3: forecast input, not enablement |
| REL-00818 | emitting | held | G3-A3: analytical feedback (spend analysis) |
| REL-00820 | emitting | held | G3-A3: analytical feedback (ROI analysis) |
| REL-00834 | emitting | held | G3-A3: forecast input, not enablement |
| REL-00843 | emitting | held | G3-A3: hierarchy-adjacent (quote dev in target scope) |
| REL-00846 | emitting | held | G3-A3: partitioned ownership (commercial vs fulfillment records) |
| REL-00851 | emitting | held | G3-A3: informational contribution (sales reporting) |
| REL-00852 | emitting | held | G3-A3: informational contribution (sales reporting) |
| (REL-00595→REL-00816 approvals) | emitting | emitting | G3-A3 APPROVED — basis to D:hamid-verdict |

**Bucket totals:** emitting 1,054 → **1,041** (−13); held 249 → **262**
(+13); deferred 12; external-governance 1; structured-flow 2. Canonical
facts 854 → **841** (−13). Conservation:
1,041 + 262 + 12 + 1 + 2 = 1,318 ✓.

**Gate:** all 393 evidence-gate checks pass (conservation assertions
updated to 841 facts). Promotion remains blocked.

## 2026-09-26 — G3 Section A4 verdicts recorded (Hamid)

Section A4: 25 explicit-reference rows (`review-evidence/enables-g3-section-a4-review.csv`),
REL-00857 → REL-01092.

**Count reconciliation (authoritative = row-level table):** the message
summary said "13 approve / 12 hold" and its ledger-impact section assumed
13/12, but the verdict table's Approve/Hold column and per-row hold
narratives all say **16 approvals and 9 holds** (16+9=25). The 16/9 split
was applied per Hamid's instruction.

- **16 rows APPROVED** (APPROVE / D:hamid-verdict): governed master data,
  policies, operational controls, service capacity, or required terms that
  make the target capable of operating. **Basis change only** — no bucket
  or fact-count movement.
- **9 rows HELD** (HOLD / D:hamid-verdict): deployment/data-consumption
  (REL-00857), operational-data feed (REL-00886), boundary statement
  (REL-00889), input/data relationship (REL-00898), exception/lifecycle
  handoff (REL-01038), output/input to billing (REL-01072), output/input to
  close (REL-01073), coordination/support (REL-01082), evidence/output for
  billing (REL-01092). Stored `core:enabledBy` facts removed; no substitute
  predicate emitted; enables assertions retained as non-emitting evidence;
  routed for source-workbook correction.

**Fact-provenance uniqueness validation:** all 9 removed `core:enabledBy`
facts were unique single-row facts (mention_count 1, row_ids = the held
row only), with no independent approved supporter. All 9 removed; no fact
retained via other evidence.

**Row-level changes:**

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-00857 | emitting | held | G3-A4: deployment/data-consumption |
| REL-00886 | emitting | held | G3-A4: operational-data feed |
| REL-00889 | emitting | held | G3-A4: boundary statement |
| REL-00898 | emitting | held | G3-A4: input/data relationship |
| REL-01038 | emitting | held | G3-A4: exception/lifecycle handoff |
| REL-01072 | emitting | held | G3-A4: output/input to billing |
| REL-01073 | emitting | held | G3-A4: output/input to close |
| REL-01082 | emitting | held | G3-A4: coordination/support |
| REL-01092 | emitting | held | G3-A4: evidence/output for billing |
| (REL-00880→REL-01087 approvals) | emitting | emitting | G3-A4 APPROVED — basis to D:hamid-verdict |

**Bucket totals:** emitting 1,041 → **1,032** (−9); held 262 → **271**
(+9); deferred 12; external-governance 1; structured-flow 2. Canonical
facts 841 → **832** (−9). Conservation:
1,032 + 271 + 12 + 1 + 2 = 1,318 ✓.

**Gate:** all 393 evidence-gate checks pass (conservation assertions
updated to 832 facts). Promotion remains blocked.

## 2026-09-26 — G3 Section A5 verdicts recorded (Hamid)

Section A5: 25 explicit-reference rows (`review-evidence/enables-g3-section-a5-review.csv`),
REL-01100 → REL-01267.

**Count reconciliation (authoritative = row-level table):** the message
summary said "13 approve / 12 hold" and its ledger-impact section assumed
13/12, but the verdict table's Approve/Hold column lists **14 approvals and
11 holds** (14+11=25). The 14/11 split was applied per Hamid's instruction.

- **14 rows APPROVED** (APPROVE / D:hamid-verdict): approved strategy,
  governed agreements, operational infrastructure, controls, or required
  close inputs that make the target capable of operating. **Basis change
  only** — no bucket or fact-count movement. Authority-preserving
  scope conditions recorded on REL-01109, REL-01138, REL-01141,
  REL-01149, REL-01215, REL-01267: enablement does not transfer decision,
  approval, legal, procurement, scheduling, or platform authority; the
  target retains ownership of its functions.
- **11 rows HELD** (HOLD / D:hamid-verdict): analysis/evidence feeds
  (REL-01157, REL-01178, REL-01182, REL-01185), output/evidence feeds
  (REL-01163, REL-01171, REL-01257), forecast input (REL-01216),
  partitioned coordination (REL-01210), cross-capability partition
  (REL-01254), non-enabling coordination (REL-01262). Stored
  `core:enabledBy` facts removed; no substitute predicate emitted; enables
  assertions retained as non-emitting evidence; routed for source-workbook
  correction.

**Fact-provenance uniqueness validation:** all 11 removed `core:enabledBy`
facts were unique single-row facts (mention_count 1, row_ids = the held
row only), with no independent approved supporter. All 11 removed; no fact
retained via other evidence.

**Row-level changes:**

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-01157 | emitting | held | G3-A5: analysis/evidence feed |
| REL-01163 | emitting | held | G3-A5: output/evidence feed |
| REL-01171 | emitting | held | G3-A5: output/lifecycle relation |
| REL-01178 | emitting | held | G3-A5: analysis feed (company) |
| REL-01182 | emitting | held | G3-A5: analysis feed (consumer) |
| REL-01185 | emitting | held | G3-A5: analysis feed (customer/marketer) |
| REL-01210 | emitting | held | G3-A5: partitioned coordination |
| REL-01216 | emitting | held | G3-A5: forecast input |
| REL-01254 | emitting | held | G3-A5: cross-capability partition |
| REL-01257 | emitting | held | G3-A5: output/lifecycle relation |
| REL-01262 | emitting | held | G3-A5: non-enabling coordination |
| (REL-01100→REL-01267 approvals) | emitting | emitting | G3-A5 APPROVED — basis to D:hamid-verdict |

**Bucket totals:** emitting 1,032 → **1,021** (−11); held 271 → **282**
(+11); deferred 12; external-governance 1; structured-flow 2. Canonical
facts 832 → **821** (−11). Conservation:
1,021 + 282 + 12 + 1 + 2 = 1,318 ✓.

**Gate:** all 393 evidence-gate checks pass (conservation assertions
updated to 821 facts). Promotion remains blocked.

## 2026-09-26 — G3 Section A6 verdicts recorded (Hamid); Section A complete

Section A6: final 6 explicit-reference rows
(`review-evidence/enables-g3-section-a6-review.csv`), REL-01274 → REL-01311.
Table says 4 approvals / 2 holds — message narrative, row table, and hold
narratives agree; no reconciliation needed.

- **4 rows APPROVED** (APPROVE / D:hamid-verdict): governed strategy,
  contract/control framework, controlled transaction record, or
  independent risk-control basis that makes the target capable. **Basis
  change only.** Scope conditions recorded on each approval
  (REL-01274/01298/01303/01311).
- **2 rows HELD** (HOLD / D:hamid-verdict): adjacent execution
  (REL-01277), independent-function exclusion (REL-01299). Stored
  `core:enabledBy` facts removed; no substitute predicate emitted; enables
  assertions retained as non-emitting evidence; routed for source-workbook
  correction.

**Fact-provenance uniqueness validation:** both removed `core:enabledBy`
facts were unique single-row facts (mention_count 1, row_ids = the held
row only), with no independent approved supporter. Both removed; no fact
retained via other evidence.

**Row-level changes:**

| Row | Old bucket | New bucket | Reason |
|---|---|---|---|
| REL-01277 | emitting | held | G3-A6: adjacent execution |
| REL-01299 | emitting | held | G3-A6: independent-function exclusion |
| (REL-01274, REL-01298, REL-01303, REL-01311) | emitting | emitting | G3-A6 APPROVED — basis to D:hamid-verdict |

**Bucket totals:** emitting 1,021 → **1,019** (−2); held 282 → **284**
(+2); deferred 12; external-governance 1; structured-flow 2. Canonical
facts 821 → **819** (−2). Conservation:
1,019 + 284 + 12 + 1 + 2 = 1,318 ✓.

**Gate:** all 393 evidence-gate checks pass (conservation assertions
updated to 819 facts). Promotion remains blocked.

### Section A completion record

All **143 Section A explicit-reference rows** are now decided:
- 131 rows received new row-level verdicts across A1–A6 (A1: 19/6, A2:
  19/6, A3: 12/13, A4: 16/9, A5: 14/11, A6: 4/2 — approvals/holds).
- 12 pre-existing held rows remained reconciliation-only (not re-decided).

Remaining G3 work: 96 undecided Section B nearness-only rows
(`B — nearness-only (needs Hamid verdict)`), plus 10 already-held
Section B reconciliation rows. Promotion remains blocked until every
recorded batch and the mapping document are approved.

New boundary definitions: Framework-versus-enablement boundary
(framework/contract/adjacent process counts as core:enabledBy only where
it provides the target's required governed operating basis; mere
relevance of terms or lifecycle participation is insufficient),
Independent-function exclusion (a source explicitly excluding the
target's owned operational function cannot be promoted as enabling it
without separate positive capability-effect evidence).

## 2026-09-26 — G3 Section B1 verdicts recorded (Hamid)

Section B1: first 15 nearness-only rows (`review-evidence/enables-g3-section-b1-review.csv`),
REL-00032 → REL-00239. All were emitting before review.

- **15 rows HELD** — no predicate review reached; target identity fails first.
  - 13 rows: **HOLD / D:hamid-verdict / TargetIdentityUnconfirmed** — candidate
    target plausible but no stable identifier, explicit target name, or
    source-definition/scope evidence links the source to that target.
  - 2 rows: **HOLD / D:hamid-verdict / TargetIdentityRejected** — candidate
    target semantically misaligned (REL-00164: contract monitoring vs
    trading-strategy stewardship; REL-00239: credit-risk reporting vs
    trading-strategy stewardship).
- No retarget or remap at promotion; enables assertions retained as
  non-emitting evidence; routed for source-workbook target clarification.
  The actual intended targets remain unknown — no inferred replacements
  were supplied to the backlog.

**Fact-provenance uniqueness validation:** all 15 removed `core:enabledBy`
facts were unique single-row facts (mention_count 1, row_ids = the held
row only), with no independent approved supporter. All 15 removed; no fact
retained via other evidence.

**Row-level changes:** each of the 15 rows: emitting → held
(B1 target-identity hold).

**Bucket totals:** emitting 1,019 → **1,004** (−15); held 284 → **299**
(+15); deferred 12; external-governance 1; structured-flow 2. Canonical
facts 819 → **804** (−15). Conservation:
1,004 + 299 + 12 + 1 + 2 = 1,318 ✓.

**New hard gate rule — nearness-only identity rule** (implemented in
evidence-gate.py, Hamid 2026-09-26): a candidate resolved solely by label
similarity, unique-candidate filtering, structural proximity, or other
classifier nearness evidence cannot emit a semantic fact; it requires
explicit target evidence or a separately recorded manual identity
confirmation based on source material. The gate fails if a B1 row whose
`target_identity_evidence` is NEARENESS ONLY contributes a canonical
relationship fact without a row-level identity override backed by source
evidence.

**Control-case correction (observed failure → fix → pass):** two
control-case checks (`control-case stored REL-00059/REL-00133 as
core:enabledBy`) failed after B1 verdicts were applied. Investigation:
both rows were never row-level approved by Hamid — the control-case
assertion was mistaken (they were previously "held pending domain-batch
review" and emitting only as unreviewed pipeline output). Moved both from
the approved-emission control list to the hold control list; gate now
green on 395 checks.

**Gate:** all evidence-gate checks pass (conservation assertions updated
to 804 facts; 15 B1 no-fact assertions live in the nearness-identity
rule). Promotion remains blocked.

## 2026-09-26 — G3 Section B2 verdicts recorded (Hamid)

Section B2: second 15 nearness-only rows (`review-evidence/enables-g3-section-b2-review.csv`),
REL-00253 → REL-00431. All were emitting before review.

- **15 rows HELD** — no predicate review reached; target identity fails first.
  - 13 rows: **HOLD / D:hamid-verdict / TargetIdentityUnconfirmed**.
  - 2 rows: **HOLD / D:hamid-verdict / TargetIdentityRejected** — candidate
    target semantically misaligned (REL-00266: risk reporting vs trading
    strategy stewardship; REL-00285: risk limits vs trading strategy
    stewardship).
- No retarget or remap at promotion; enables assertions retained as
  non-emitting evidence; routed for source-workbook target clarification.
  Possible interpretations (e.g. inputs, constraints, coordination) are
  noted but explicitly NOT approved predicates.

**Fact-provenance uniqueness validation:** all 15 removed `core:enabledBy`
facts were unique single-row facts (mention_count 1, row_ids = the held
row only), with no independent approved supporter. All 15 removed; no fact
retained via other evidence.

**Row-level changes:** each of the 15 rows: emitting → held
(B2 target-identity hold).

**Bucket totals:** emitting 1,004 → **989** (−15); held 299 → **314**
(+15); deferred 12; external-governance 1; structured-flow 2. Canonical
facts 804 → **789** (−15). Conservation:
989 + 314 + 12 + 1 + 2 = 1,318 ✓.

**REL-00428 supersession (observed failure → fix → pass):** REL-00428 had a
genuine 2026-09-25 row-level approval ("validated feedstock-quality data
underpins term-slate quality screening", review32-enables-batch) and was in
EN_ENABLEDBY_OVERRIDE. Hamid's B2 verdict now holds it
(TargetIdentityUnconfirmed): the approval rested on semantic plausibility,
but the Hamid-approved nearness-only identity rule requires source-backed
target identity before any predicate verdict — the later row-level verdict
is authoritative. REL-00428 removed from EN_ENABLEDBY_OVERRIDE and moved
from the stored-emission control list to the hold control list.

**Gate:** all evidence-gate checks pass (conservation assertions updated
to 789 facts; nearness-identity rule extended to B2). Promotion remains
blocked.

## 2026-09-26 — G3 Section B3 verdicts recorded (Hamid)

Section B3: third 15 nearness-only rows (`review-evidence/enables-g3-section-b3-review.csv`),
REL-00437 → REL-00837. All were emitting before review.

- **15 rows HELD** — no predicate review reached; target identity fails first.
  - 14 rows: **HOLD / D:hamid-verdict / TargetIdentityUnconfirmed**.
  - **REL-00770**: HOLD / D:hamid-verdict / TargetIdentityUnconfirmed /
    **Supersedes2026-09-25Approval** — the 2026-09-25 approval recognized a
    plausible semantic relationship, but the source assertion never
    identified Sales Execution as its target; under the subsequently
    approved nearness-only identity rule, predicate plausibility cannot
    substitute for source-backed target identity. Prior decision retained
    in provenance as superseded, not deleted.
- No retarget or remap at promotion; enables assertions retained as
  non-emitting evidence; routed for source-workbook target clarification.
  Semantic hypotheses (e.g. "account planning may support Sales Execution")
  are noted but explicitly NOT approved predicates.

**Fact-provenance uniqueness validation:** all 15 removed `core:enabledBy`
facts were unique single-row facts (mention_count 1, row_ids = the held
row only), with no independent approved supporter. All 15 removed; no fact
retained via other evidence.

**Row-level changes:** each of the 15 rows: emitting → held
(B3 target-identity hold).

**Bucket totals:** emitting 989 → **974** (−15); held 314 → **329**
(+15); deferred 12; external-governance 1; structured-flow 2. Canonical
facts 789 → **774** (−15). Conservation:
974 + 329 + 12 + 1 + 2 = 1,318 ✓.

**REL-00437 supersession (observed failure → fix → pass):** REL-00437 had a
genuine 2026-09-26 S&T approval ("quality-screened spot options make
coordinated purchases, sales, and exchanges operationally actionable;
bounded: trading coordination on quality-screened choices, not
directing/approving trades", st-enables-21-review-batch). Hamid's same-day
B3 verdict holds it (TargetIdentityUnconfirmed): the approval assumed the
asserted target, but the identity rule requires source-backed target
identity before any predicate verdict — the later row-level verdict is
authoritative. Moved from the stored-emission control list to the hold
control list with the supersession note. Not in EN_ENABLEDBY_OVERRIDE (the
S&T approvals were never in that set).

**New definition — Decision supersession by control refinement:** a prior
row-level verdict may be superseded when a newly approved gate/control
exposes a missing required premise; the old decision must remain
traceable with its reason, date, and superseding decision.

**Gate:** all evidence-gate checks pass (conservation assertions updated
to 774 facts; nearness-identity rule extended to B3; explicit
superseded-fact absence tests for REL-00770 and REL-00437). Promotion
remains blocked.

## 2026-09-26 — G3 Section B4 verdicts recorded (Hamid)

Section B4: fourth 15 nearness-only rows (`review-evidence/enables-g3-section-b4-review.csv`),
REL-00867 → REL-01013. All were emitting before review.

- **15 rows HELD** — no predicate review reached; target identity fails first.
  - 13 rows: **HOLD / D:hamid-verdict / TargetIdentityUnconfirmed**.
  - **REL-00960**: HOLD / D:hamid-verdict / **TargetIdentityRejected** —
    order-book tracking and volume forecasting give scheduling and supply
    their planning basis; they have nothing to do with running the customer
    self-service portal. The label match reads order tracking as portal
    operation; neither definition supports that.
  - **REL-00939**: HOLD / D:hamid-verdict / TargetIdentityUnconfirmed /
    **Supersedes2026-09-25Approval** — the earlier approval's relationship
    may well be true, but the source row never names Manage Customer
    Invoicing and Billing as its target. Prior decision retained in
    provenance as superseded, not deleted.
- No retarget or remap at promotion; enables assertions retained as
  non-emitting evidence; routed for source-workbook target clarification.

**Fact-provenance uniqueness validation:** all 15 removed `core:enabledBy`
facts were unique single-row facts (mention_count 1, row_ids = the held
row only), with no independent approved supporter. All 15 removed; no fact
retained via other evidence.

**Row-level changes:** each of the 15 rows: emitting → held
(B4 target-identity hold).

**Bucket totals:** emitting 974 → **959** (−15); held 329 → **344**
(+15); deferred 12; external-governance 1; structured-flow 2. Canonical
facts 774 → **759** (−15). Conservation:
959 + 344 + 12 + 1 + 2 = 1,318 ✓.

**REL-00939 supersession:** genuine 2026-09-25 approval ("approved
financing/payment methods, terms, eligibility, commercial rules are
governed prerequisites for billing", review32-enables-batch) superseded by
the B4 row-level verdict. Removed from EN_ENABLEDBY_OVERRIDE; moved from
the stored-emission control list to the hold control list.

**Gate:** all evidence-gate checks pass (conservation assertions updated
to 759 facts; nearness-identity rule extended to B4; explicit
superseded-fact absence test for REL-00939). Promotion remains blocked.

**Section B running total: 60 rows held out of 60 decided.**

## 2026-09-26 — G3 Section B5: 9 prior-approval supersessions + 33-row class verdict (Hamid)

All 96 Section B rows are now HELD; Section B is complete at **96 holds out of 96**
(60 in B1–B4; 36 in B5: 33-row class verdict + 3 supersessions — REL-01016,
REL-01124, REL-01174; 6 further supersessions outside the Section B population).
Verdicts recorded in `review-evidence/enables-g3-section-b5-class-verdict.csv` (42 rows).

**The 9 prior approvals** — all recorded as HOLD / D:hamid-verdict / TargetIdentityUnconfirmed / Supersedes<date><batch>Approval.
Each approval judged whether the relationship made sense, not whether the target was right;
none of the nine has evidence of which target the source meant. Original approval text kept in
provenance, marked superseded.

- REL-00129, REL-00728 — review32 2026-09-25 approvals + G2 row-level exceptions
  (Supersedes2026-09-25Review32Approval). Gate flips: the G2 exception checks changed
  from "fact present" to "fact absent". The G2 disguised-sequence exception goes too.
  Their independently recorded `precedes`/`follows` facts are separate (supported by
  REL-00131 and REL-00734) and stay as they are.
- REL-00243, REL-00304, REL-01006 — review32 2026-09-25 approvals
  (Supersedes2026-09-25Review32Approval). Uniqueness check before removal: all three had
  blank `merged_with_rows` in the G1a batch; confirmed none was ever merged as a G1a
  duplicate and no other approved row supports the same fact. All three facts unique.
- REL-00489 — S&T 2026-09-26 approval (reviewer predicate change), Supersedes2026-09-26STApproval.
  Quick-confirmation candidate: the target's own scope description names the source process
  (REL-00475 communicates utilization requirements to the agreement owner CM-1-2-7-1-1).
  That links the two processes; it does not prove the source row's raw target text meant
  CM-1-2-6-2-2. Superseded now; placed at the top of the workbook backlog with that evidence
  attached. If the source author confirms, the row returns with a proper identity override
  and a fresh verdict. This also resolves REL-00489's G1b "leave unchanged" listing — that
  decision is now superseded.
- REL-01016 — review32 2026-09-25 approval (Supersedes2026-09-25Review32Approval); removed
  from EN_ENABLEDBY_OVERRIDE.
- REL-01124, REL-01174 — S&T 2026-09-26 approvals (Supersedes2026-09-26STApproval);
  S&T stored controls removed.

**The 33-row class verdict** (REL-01049 through REL-01318): each confirmed nearness-only
(SoleCandidate), no source-backed identity override, no prior approval, none marked Rejected.
All recorded as HOLD / D:hamid-verdict / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26.
If the source author finds a clearly wrong candidate while clearing the backlog, it can be
relabelled then; the outcome is the same either way.

**Fact-provenance uniqueness validation:** all 42 removed `core:enabledBy` facts were unique
single-row facts (mention_count 1, row_ids = the held row only), with no independent approved
supporter. All 42 removed; no substitutes, retargeting, or predicate remaps emitted.

**Row-level changes:** each of the 42 rows: emitting → held (B5 target-identity hold).

**Bucket totals:** emitting 959 → **917** (−42); held 344 → **386** (+42); deferred 12;
external-governance 1; structured-flow 2. Canonical facts 759 → **717** (−42). Conservation:
917 + 386 + 12 + 1 + 2 = 1,318 ✓.

Emitting `core:enabledBy` facts fall from 126 to 84. Every one of the remaining 84 was
matched to its target by an explicit reference in the source definition (a stable ID or the
target's label), and every one has a row-level approval.

**Gate:** all evidence-gate checks pass (conservation assertions updated to 717 facts;
nearness-identity rule extended to B5; G2 exception checks flipped to fact-absent;
REL-01016 removed from the override stored list; REL-01124/REL-01174 removed from the
S&T stored list; all nine added to the no-fact hold controls; REL-00489's G1b "keep
approved" listing resolved). Promotion remains blocked; the mapping-doc approval pass
is next.

**G3 status:** Section B Candidate → Approved, all 96 rows held. G3 overall: Approved
with held exceptions (Section A: 84 approvals emitting, all cleared by the sweep).

## 2026-09-26 — Mapping answers 1–5: Approved Baseline (Hamid)

**Answers 1–5: Candidate → Approved Baseline.** Answer 1 approved as written;
Answers 2–5 approved with Hamid's wording edits (controls already agreed, now
stated in the answers so the doc stands alone). Baseline change control: any
later change to an approved answer needs a decision-log entry. Counts
unchanged: 917 emitting / 386 held / 717 facts. Doc figures-fix pass (6
issues) also landed 2026-09-26; gate green including the new
zero-stored-inverse-predicate check (Answer 5).
Next: canonical direction table, row by row, then the rule sections.

## 2026-09-26 — Direction table: two new two-cycle rules (Hamid)

**New rule 1: no reciprocal `core:precedes` two-cycles.** A process cannot come
both before and after another in the same lifecycle. Gate check added and
passing (202 facts, zero reciprocal pairs).

**New rule 2: no reciprocal `core:governedBy` two-cycles.** Governance runs one
way; a mutual governedBy pair is a contradiction. Gate check added and passing
(38 facts, zero reciprocal pairs).

**`core:governedBy` emission guard** (promotion script): emit only when the
source definition/scope explicitly says the source operates within
target-owned policy/framework/authority, applies target-owned
limits/rules/guardrails/delegation/approved criteria, or is subject to a
specific target-owned control boundary. Ancestor/descendant restatements are
held (child "governed by" parent mostly repeats `skos:broader`). REL-01309 is
the one recorded exception — approved 2026-09-24 as the Accounting-cluster
set-versus-apply pattern — and sets no precedent. Emitting `governed-by`
mentions: 43 → 38 in the 2026-09-26 refresh (pipeline-recomputed; the rest are
context/source-review holds or the external-governance reference).

Direction table: Rows 1–4, 6, 9–11 approved as written; Rows 5, 7, 8, 12
approved with the edits above. Reconciliation recorded in the doc:
829 + 75 + 13 = 917 emitting mentions.

## 2026-09-26 — Direction table: Approved Baseline (Hamid)

**Direction table Rows 1–12: Candidate → Approved Baseline.** Wording fix:
829 mentions map to their own predicate; 75 G1a attach as duplicate evidence
(904 attached to stored facts; 917 − 13 G2 no-triple). Footnote retitled:
"Non-emitting, non-held mentions: 2 Q5 structured-flow values,
1 ExternalGovernanceReference, 12 deferred." Counts unchanged: 917 / 386 / 717.
Next: the rule sections, one at a time.

## 2026-09-26 — Rule section 1 (disguised-sequence control): Approved Baseline (Hamid)

**Rule section 1: Candidate → Approved Baseline** with 5 edits. The exception
clause now requires (a) source-backed target identity AND (b) independent
capability-enablement evidence meeting the Answer 3 test — the old clause
predated the identity rule and is exactly what failed for REL-00129/REL-00728.
Row-level precedence qualified: it applies only to verdicts that met every
control in force when made; a later control exposing a missing required
premise supersedes the verdict via supersession-by-control-refinement, with
decision history kept. The 13 NoSeparateEnablesFact rows are not
workbook-correction items (source wording stands as non-emitting evidence).
G2 batch CSV gained a `supersession` column marking the two former
ExistingRowLevelApproval exceptions as superseded 2026-09-26. Gate: 15 G2
rows emit no enabledBy fact; REL-00129/REL-00728 absent; their sequence facts
(REL-00131, REL-00734) present. Counts unchanged: 917 / 386 / 717.

## 2026-09-26 — Rule section 2 (recommendation versus enablement): Approved Baseline (Hamid)

**Rule section 2: Candidate → Approved Baseline** with 4 edits. The rule now
classifies and routes for source correction — never remaps to informedBy at
emission (Rule 11). Widened enterprise-wide with PTC-002 as the S&T instance;
non-S&T precedents recorded (REL-00232 A2; REL-00818/REL-00820 A3;
REL-00750/REL-01206 S&T sweep). The stale "open watch" is closed: the 2026-09-26
S&T sweep (21 rows: 6 approved — 2 still emitting, 4 superseded under the
identity rule; 13 held for source correction — 5 advisory-pattern, 8
ambiguous; 2 hierarchy holds kept) replaces it. REL-00433/REL-01172 scope
note: they enable production of the recommendation only. Counts unchanged:
917 / 386 / 717.

## 2026-09-26 — Rule section 3 (duplicate-evidence merge): Approved Baseline (Hamid)

**Rule section 3: Candidate → Approved Baseline** with 5 edits. True duplicate
now defined: same source/target slugs, same canonical direction, same fact as
an independently approved uses-input row. **Target-match census (2026-09-26):**
33 of 77 G1a rows carry a stable identifier in the mention text (identity
confirmed); 44 matched by unique exact preferred-label only → attach as
identity-unconfirmed provenance (kept for audit, never support or
corroboration). Verified: every G1a row names an independent uses-input
supporter on the same fact; no G1a row is sole evidence; no merge created a
fact. REL-00152/REL-00436 stay counted in the 386 held. G1a batch gained a
`target_match` column; gate asserts it plus the not-sole-evidence rule (562
checks, all pass). Counts unchanged: 917 / 386 / 717.

## 2026-09-26 — Rule section 4 (G1b no-verb-change): Approved Baseline (Hamid)

**Rule section 4: Candidate → Approved Baseline** with 4 edits. The exception
route now requires an Answer-3-meeting row-level approval (identity +
capability effect). Counts: 29 held = 28 removed facts + REL-01224 (already
held); all 29 on the workbook backlog. Gate text updated to its current
state (GREEN since 2026-09-26). Reverse informed-by cross-referenced: evidence
only for its own informedBy fact, never identity/predicate for the opposite
row (Answer 2).

**OPEN — identity-rule scope (blocks promotion):** the rule is written
general but has only been applied to `enables`. Full-verb census 2026-09-26
(917 emitting): 176 stable-id, 84 explicit-reference (G3-A), 657
nearness-only. By verb (nearness-only): uses-input 152/215, informed-by
115/139, precedes 130/150, follows 146/164, governed-by 33/38, triggers
16/18, assures 5/5, enables 52/172 (rest stable-id/explicit). REL-00873
(requires) approved on PROMOTE/B:structural-nearness — same premise
superseded for REL-00770. 51 of the 77 G1a supporting uses-input rows are
nearness-only. Hamid to rule: apply everywhere with per-verb supersession
pass, or limit with a recorded reason. No action until he rules.

## 2026-09-26 — Rule section 5 (hierarchy non-duplication): Approved Baseline (Hamid)

**Rule section 5: Candidate → Approved Baseline** with 5 edits: sixth exception
condition added (target identified by source-backed evidence under the
identity rule as finally scoped); REL-01309's exception stands only if it
passes all six conditions; rule applies to every predicate, not only
governedBy; the 10 held rows are on the workbook backlog; gate named (no
fact from the 10 held rows; any emitting ancestor/descendant pair carries a
recorded six-condition exception).

## 2026-09-26 — PR #120 rationale + label-reuse evidence (for the identity-rule scope ruling)

PR #120's rationale (from the PR body): "A lexical match is not a semantic
resolution." Decision ladder: stable ID → approved contextual evidence
sufficient to identify exactly one governed target → scoped historical alias
→ defer. A label match is a candidate filter, never a join key, per the
standing identity lock (slugs/IRIs are identity; labels are presentation
metadata). The PR states the ladder as a governing assertion — it cites no
concrete collision cases. Repo data validates the underlying concern:

- 13 prefLabels are shared by multiple concepts: label reuse across levels
  ('Demand Forecasting' → CM-1-1-1 and CM-1-1-1-1; 'Actualizations' →
  CM-1-2-3 and CM-1-2-3-1) and across sibling branches ('Source & Collect
  Information', 'Analyze Data', 'Document Findings', 'Define Analysis
  Objectives & Scope' each × 5).
- 11 live rows (REL-00194, REL-00312, REL-00336, REL-00338, REL-00340,
  REL-00360) where an exact label matched multiple concepts with no single
  contextual target.
- 28 "unique exact preferred-label match" rows now point at labels absent
  from the current identity map (e.g. 'Refinery Planning and Optimization') —
  stale labels after the Step 3d rename pass. A triple built on such a match
  silently loses its target.

Pending: explicit-reference test + match-type breakdown (delegated).

## 2026-09-26 — Identity-rule scope census results (for Hamid's ruling)

Explicit-reference test on all 657 nearness-only emitting mentions:
**21 pass / 636 do not.** Passes by verb: assures 5, constrained-by 3,
constrains 1, enables 2, governed-by 5, requires 1, triggers 1, uses-input 3 —
all individually reviewed rows. 60 further rows carry a ≥2-word chunk of the
target label in source evidence (reported, not a pass).

Match-type breakdown of the 636: **635 exact-unique-current** (raw target =
target's current prefLabel, unique across the map), 1 structural/contextual
(REL-00388, Q11 split-row special). Zero altLabel/historical, zero
partial/fuzzy. The "nearness-only" bucket is essentially one thing: exact,
unique, current labels.

Special rows: REL-00164 and REL-00239 — exact-unique-current, held, look like
verb problems not target problems. REL-00873 — exact-unique-current ("Establish
Credit Limit & Risk Code"); the B:structural-nearness was the context-pass
tier, not the label match. G1a supporters: 0/77 pass explicit-reference; 26
stable-id (identity confirmed), 51 exact-unique-label.

Files: review-evidence/identity-scope-explicit-reference-test.csv,
review-evidence/identity-scope-match-types.csv. No counts changed.

## 2026-09-26 — Identity-rule scope RULING (Hamid)

**Part 1 — scope:** the identity rule applies to every verb. Rule 5 evidence
routes: sibling sequences (precedes/follows) may promote on structural
nearness between siblings; every other verb (enables, governed-by, requires,
assures, constrained-by, triggers, uses-input, informed-by) needs an
independent route: explicit citation of the target in the source definition
or scope note; a consistent two-way mention (strict inverse pairs only); or
nearness within the same branch plus an independent evidence type.
informed-by is not a sequence relation and needs a route; an
informs/informed-by pair meets the two-way test.

**Part 2 — evidence line:** stands as written (playbook rules 4–5 on main at
a73d313: "a unique label match earns a candidacy, not a triple"). A verdict
cannot change an Approved Baseline rule; amendment would need a playbook PR
plus a decision-log entry (an ADR). Rule 6 argues against rescuing rows
one approval at a time.

**Consequences recorded:**
- 13 supersessions + 96 Section B holds stand; no re-review. Held rows
  promote only through a rule 5 route, recorded with the route used.
- 5 relabels: REL-00164, REL-00239, REL-00266, REL-00285, REL-00960 —
  TargetIdentityRejected → TargetIdentityUnconfirmed ("predicate doubt
  recorded"); the target was never in doubt, the verb was.
- REL-00873 superseded (no rule 5 route); its unique core:requires fact
  removed; row on the workbook backlog. Facts: 717 → 716. Emitting 917,
  held 386 unchanged (the row was already held).
- **REL-00873 supersession REVERSED 2026-09-26.** The corrected citation
  test found the scope note names "Establish Credit Limit & Risk Code"
  — the target CM-1-3-7-4-2's exact unique prefLabel — affirmatively
  ("requests governed record creation and consumes the outcomes").
  Qualifies under the approved "scope-note label citation, unique
  label" route. The 2026-09-25 predicate judgment (credit-controlled
  onboarding prerequisite) stands as the predicate basis; the target
  identity is now established by the citation route, not by the
  predicate judgment. Fact restored. Supersession register:
  *superseded 2026-09-26 on an incomplete census; reversed 2026-09-26
  on the corrected citation test.*
- G1a knock-on: 26 stable-id supporters keep standing; the 51 label-only
  supporters go through the uses-input pass — any held leaves its fact
  without independent support, and identity-unconfirmed enables mentions
  cannot carry it.
- Census extended with two-way-mention and branch flags; per-verb pass with
  rule 6 sampling follows, starting with uses-input.

**Open:** the definition of "approved decision evidence" in rule 5. Hamid's
reading: recorded architecture decisions (e.g. the R1 reviewed interface),
not a row-level verdict that a relationship is plausible. The phrase is
undefined in the playbook as merged — recommend pinning the definition via
a small playbook amendment (PR + decision-log entry) before the per-verb
pass relies on it. Hamid's reading is the safer one and is consistent with
rule 6.

## 2026-09-26 — PR #124 review fixes (Hamid: HOLD, not merging)

Two leftover defects found on review of `step4/working` at `3a1a413`:

1. **Lock 3 IRI fork.** Q1/Q3 APPROVED headers in `step4-decisions.md`,
   `step4-design-proposal.md` (§2 and decision-question 1), and
   `playbook/pr-body.md` still read `https://w3id.org/lsc/ontology/core`
   (and `…/core/1.0.0`). Corrected to the locked Step 1 URI policy
   `https://w3id.org/lsc/ontology/modules/core` (version IRI
   `…/modules/core/1.0.0`), with dated correction notes. The fork-description
   notes (the "IRI fork correction" section) are unchanged — they describe
   the error, they don't restate it as approved.

2. **Rule 7 conservation.** The REL-00873 supersession removed its fact
   (717 → 716) but `evidence-gate.py` still asserted 717 and
   `verb-predicate-mapping-v2.md` still cited 717. Updated: gate asserts
   716/716, mapping doc cites 716 with the supersession noted, baseline
   rebased to `a73d313` (PR #123). The gate's REL-00873 control case now
   asserts emits-nothing (it previously asserted the removed fact was
   stored). Historical ledger entries recording 717 at the time are
   unchanged. Gate re-run: GREEN.

Current: 917 emitting / 386 held / 716 facts. PR stays DO NOT MERGE;
Hamid re-reviews after the sync.

## uses-input pass applied (2026-09-26)

Hamid approved the 33/31 citation split and the disposition at
761 emitting / 542 held / 603 facts (PR #125, #126; fourth revision; corrected 2026-09-26: 917 baseline was stale, true pre-pass 916/387).

**Applied:**
- 114 uses-input rows moved emitting → held (82 no-citation, 31
  exclusion/boundary, REL-01061 wrong-concept). Full list in
  `review-evidence/uses-input-application-log.md`.
- 114 canonical facts removed (73 sole-evidence, 41 G1a-shared; the
  enables mentions cannot carry a fact alone).
- 42 enables mentions moved emitting → held (k=42; G1a 75 → 33).
  REL-00436 was already held (in the 386) and not counted in k.
- REL-00873 supersession reversed; core:requires fact restored
  (basis: scope-note label citation).
- REL-00564 promoted on the scope-note range citation route; its fact
  retained with REL-01188 attached (emitting).
- REL-00447 promoted on the scope-note range citation route; its fact
  retained with REL-00436 attached (held).

**Totals:** 916 − 114 − 42 + 1 = 761 emitting; 387 + 114 + 42 − 1 = 542
held; 716 − 114 + 1 = 603 facts. Conservation: 761 + 542 = 1303. ✓

**Gate:** updated for the new disposition (603 facts, 36 active G1a
rows, REL-00873 stored, REL-01061 held, REL-00214 fact removed).
Pre-existing SHA-pin failures unchanged.

## Informed-by pass (2026-09-26, Hamid approved)

139 emitting `informed-by` rows reviewed under the strict citation test
(slug, unique label, or range in the source's definition or scope note),
split affirmative/exclusion, with the two-way route, R1 decision evidence,
and rule 5 checked per row.

- **24 rows stand** under rule 4 (stable-ID identity; no rule 5 route required):
  7 with an affirmative citation + 17 without.
- **20 label-only rows promote** on an affirmative citation, recorded
  `D:hamid-verdict`.
- **95 rows held**: 55 exclusion/boundary-only citations, 1 counterpart
  citation with information flowing the wrong way (REL-00476,
  "counterpart, opposite flow"), 39 with no citation.
- Two-way (strict inverse `informs` pair): 0. Approved decision evidence: 0
  (R1 is the `informs` row itself, not in this population).
- All 95 removed facts were unique single-row facts (mention_count=1);
  no knock-on effects on other facts.

**Totals:** 761 − 95 = **666** emitting; 542 + 95 = **637** held;
603 − 95 = **508** facts. Conservation: 666 + 637 + 12 + 1 + 2 = 1,318. ✓

**G1b gate amendment:** The approved section 4 gate check "reverse
informed-by fact present through its own row-level evidence" is now
conditional: the reverse fact is present **if** the reverse row has a route
(stable-ID, affirmative citation, two-way, or approved decision); otherwise
the reverse row is held with no fact.

**15 G1b pairs held on both sides** (relationship disappears from the graph
entirely; added to the backlog the same way as contradiction pair C):

| G1b row | Informed-by row |
|---|---|
| REL-00469 | REL-01130 |
| REL-00489 | REL-00476 |
| REL-00499 | REL-00505 |
| REL-00648 | REL-00643 |
| REL-00974 | REL-00896 |
| REL-00977 | REL-00965 |
| REL-01112 | REL-00646 |
| REL-01148 | REL-01150 |
| REL-01151 | REL-01152 |
| REL-01154 | REL-01205 |
| REL-01184 | REL-01193 |
| REL-01194 | REL-01199 |
| REL-01197 | REL-01200 |
| REL-01233 | REL-01217 |
| REL-01273 | REL-01295 |

The other 16 G1b reverse rows keep their facts: 6 STAND by rule 4
(REL-00081, REL-00144, REL-00822, REL-01275, REL-00136, REL-01190) and
10 PROMOTE (REL-00706, REL-00739, REL-00775, REL-00776, REL-00948,
REL-01110, REL-01196, REL-01202, REL-01232, REL-01272).

## Governed-by pass (2026-09-26, Hamid approved)

38 emitting `governed-by` rows reviewed (predicate `core:governedBy`).

**Verdicts:**
- **5 STAND** (rule 4, stable-ID): REL-01309, REL-00359, REL-00577, REL-00902,
  REL-00908.
- **13 PROMOTE**:
  - 4 non-hierarchy affirmative citations: REL-00397, REL-00876, REL-00952,
    REL-01158. (REL-00876, REL-00952: short snippets verified against full
    definition/scope text.)
  - 6 hierarchy exceptions (Hamid 2026-09-26, each not a precedent):
    REL-00531, REL-00542 (privacy-governance control at parent);
    REL-00588, REL-00601, REL-00623 (PMPA legal constraint at cluster);
    REL-00106 (decision rights, ancestor decides).
  - 3 from strict re-test of 13 prior approvals: REL-00190, REL-00858,
    REL-01313. (REL-00190: promotes on unique label "Market Risk Management";
    target stays CM-1-2-2-3 per Rule 11. REL-01313: scope condition carries
    forward — credit eligibility, limits, holds/releases, risk-control
    constraints only.)
- **20 HOLD** (all facts verified unique single-row; zero knock-on):
  - 7 exclusion/boundary citations: REL-00185, REL-00215, REL-00250,
    REL-00969, REL-01113, REL-01300, REL-01310.
  - 3 hierarchy restatements (composition, not governance): REL-00620,
    REL-00625, REL-00629.
  - 10 no affirmative citation (2026-09-25 approvals superseded): REL-00050,
    REL-00067, REL-00394, REL-00399, REL-00406, REL-00907, REL-00937,
    REL-01005, REL-01228, REL-01256.

**Rule 6 check:** PASSED. Hamid read all 13 promotions against citations and
exception rationales; none reversed. Recorded as `D:hamid-verdict` 2026-09-26.

**Totals:** 666 − 20 = **646** emitting; 637 + 20 = **657** held;
508 − 20 = **488** facts. Conservation: 646 + 657 + 12 + 1 + 2 = 1,318.

## Triggers pass (2026-09-26, Hamid approved)

18 emitting `triggers` rows reviewed (2 stable-ID, 16 label-only).

- **2 STAND** (rule 4, stable-ID): REL-00725, REL-00897.
- **5 PROMOTE** (affirmative citation + event semantics, `D:hamid-verdict`):
  REL-00127 ("triggering rescheduling through…"),
  REL-00235 ("deterioration signals that trigger event-driven reviews"),
  REL-00236 ("trigger event-driven reviews or limit actions (CM-1-2-2-1-2)"),
  REL-00246 ("triggering of continuation reporting through…"),
  REL-00901 ("Anomalies suggesting fraud route to…" — anomaly handed off).
- **11 HOLD**: 3 exclusion/boundary (REL-00049, REL-00291, REL-00892),
  7 no citation (REL-00169, REL-00170, REL-00252, REL-00396, REL-00398,
  REL-00400, REL-00403), 1 boundary (REL-00163 — states where amendments
  are done, does not link finding to target).

Rule 6 (seed 42): 5 passed, REL-00163 held after scope-sentence review.
Recorded `D:hamid-verdict` 2026-09-26.

**Definition adopted:** an affirmative citation for `triggers` must tie the
source's event or result to the target (trigger, route to, refer, escalate,
hand off). A statement of where work is done does not count.

Totals: 646 − 11 = **635** emitting; 657 + 11 = **668** held;
488 − 11 = **477** facts. Conservation: 635 + 668 + 12 + 1 + 2 = 1,318. ✓
All 11 held facts verified unique single-row; zero knock-on effects.
11 supersession entries in `step4-decisions.md`; 11 backlog items for source
correction (including target-side range check for the 4 compliance monitors).

## Precedes/follows pass (Hamid 2026-09-26, AMENDED 2026-09-27)

**Verdicts:**
- **38 STAND** (rule 4, stable-ID mentions).
- **256 PROMOTE** (D:hamid-verdict / Rule 5 sequence route).
- **20 HOLD** (D:hamid-verdict / Supersedes2026-09-26Approval):
  - 6 no citation, no two-way (REL-01223, 01227, 01241, 01289, 01291, 01294).
  - 14 exclusion/boundary/owned-by/reference-data as sole route (REL-00008, 00068, 00112,
    00149, 00184, 00188, 00193, 00200, 00206, 00307, 00319, 00351, 00374, 00930).

**NOT basis-only:** 20 facts removed (all unique single-row, zero knock-on).
Raw `B follows A` retained in provenance for emitting rows.

**Rule 6:** method approved 2026-09-26 (seed 42). Samples NOT yet reviewed —
all outcomes pending `D:hamid-verdict`. REL-01241 held. CM-1-1-4 label corrected.
Evidence in `review-evidence/precedes-follows-rule6-samples.md`.

**Evidence Discipline Rule 5 (lock):** non-sibling precedes/follows needs an
affirmative sequence citation (or two-way). Exclusion/boundary/owned-by is
not a route (REL-00009 precedent).

**Zero reciprocal `core:precedes` pairs** (182 facts checked). Hard gate GREEN.

**Totals:** 635 − 20 = **615** emitting; 668 + 20 = **688** held;
477 − 20 = **457** facts.
Conservation: 615 + 688 + 12 + 1 + 2 = 1,318. ✓
