# Verb → Predicate Mapping v2 — CANDIDATE FOR REVIEW (not approved)

**Status:** draft for controlled review, supersedes `verb-predicate-mapping.md` (v1).
Figures refreshed 2026-09-26 to the reviewed evidence package
(615 emitting / 688 held / 457 facts — 635/668/477 before the 2026-09-27 precedes/follows amendment; 646/657/488 before the 2026-09-26 triggers pass; 666/637/508 before the 2026-09-26 governed-by pass; 761/542/603 before the 2026-09-26 informed-by pass; 716 facts before the uses-input pass; 717 before the REL-00873 supersession); section-by-section approval pending.
No emission script may use this mapping until Hamid approves it row by row.
**Baseline:** `579ed89b479529d179485f633828df89399ad3c5` (PR #126; was `a73d313ba922e323ccfeaad667efef42c194e4b8`/PR #123 — repinned 2026-09-26 after the uses-input pass).
**Inputs:** `target-dispositions-v2.csv` (1,318 mentions), `context-pass.csv`
(849 promoted / 172 context-held — the earlier draft said 812 promoted: that
figure had netted 37 mention-level property-rule/hierarchy holds out of the
context-promoted count; 849 is the file's own PROMOTE outcome count, and the
mapping applies those mention-level holds separately),
`requires-review.csv`, `assures-review.csv`, `enables-review.csv`,
`canonical-facts.csv`, `contradictions.csv`.

## The 5 mapping answers — Approved Baseline (Hamid 2026-09-26)

> **Status:** Answers 1–5 are approved. Any later change needs a decision-log
> entry. (Items 1–5 are the mapping answers; item 6, "Enablement is not
> reciprocal by default," is a rule section that follows the same approval
> pass.)

1. **`uses-input` → `core:dependsOnOutputOf`** (Q4, review-corrected). A process is
   not an input; its output is. Stored direction: consumer → producer.
2. **`informed-by` stays distinct as `core:informedBy`** — NOT merged into
   `dependsOnOutputOf`. Informational dependency keeps its own subproperty;
   `informs` is its inverse and covers the approved R1 interface
   (`CM-1-1-2-9-1 informs CM-1-1-4`, stored as `CM-1-1-4 core:informedBy CM-1-1-2-9-1`).
   A mutual `informedBy` pair is allowed; it records two-way information flow
   and is not a contradiction. An `informed-by` assertion supports only its
   own `informedBy` fact. It is never evidence for a different predicate or
   for the opposite direction (G1b precedent).
3. **`enables` → `core:enabledBy`** only for genuine enablement. A row emits
   `core:enabledBy` only if **(a)** the target is identified by a stable ID or
   an explicit reference in the source definition, and **(b)** the source
   supplies a maintained capability, governed operating base, control, or
   prerequisite that makes the target able to operate.

   The following never emit `core:enabledBy` on their own:
   - a target matched by nearness only;
   - a recommendation or piece of advice (PTC-002);
   - information passed along, output handed over, or a feedback loop;
   - a step that simply comes before or after (the disguised-sequence rule);
   - something that just restates the parent/child hierarchy;
   - a reference where the source names the target only to say it does not
     do that work.

   An approval **never transfers authority** from the target to the source.

   Current disposition of the 172 emitting `enables` mentions (refreshed 2026-09-26):
   - **G3 (84)** stored as `core:enabledBy` (approved by Hamid 2026-09-26 —
     the Section A explicit-reference approvals; Section B's 96 nearness-only
     rows are all held);
   - **5 former row-level verdicts** stored as `core:enabledBy` (REL-00243,
     REL-00304, REL-01006 approved 2026-09-25 as G1a independent facts;
     REL-00129, REL-00728 approved 2026-09-25 as G2 exceptions) — all five
     **formally superseded** 2026-09-26 under the nearness-only identity
     rule, with decision lineage in the supersession register; their facts
     were verified unique and removed; none remains emitting;
   - **G1a (77 of 81)** approved 2026-09-26: merge as extra evidence on the
     existing `dependsOnOutputOf` fact (duplicate merge, not a verb change).
     4 of the 81 split rows did not enter the review batch: REL-00243,
     REL-00304, REL-01006 (excluded as independent row-level `core:enabledBy`
     approvals — all three superseded 2026-09-26 in G3-B5, now held with no
     fact) and REL-00936 (held for source-classification review, no stored
     fact). Of the 77 approved, 33 mentions emit and attach as provenance (42 held in the 2026-09-26 uses-input pass);
     REL-00152 and REL-00436 are mention-level property-rule holds
     re-attached as duplicate provenance on the independently-evidenced fact
     (REL-00447) — updated 2026-09-26: REL-00214 held (no citation route)
     with REL-00152 (fact removed); REL-00447 retained via range citation
     with REL-00436 attached;
   - **G1b (29)** approved 2026-09-26: HOLD for workbook correction (merging
     into `dependsOnOutputOf` would change the verb — only an `informed-by`
     mention exists on the reverse pair);
   - **G2 (15 rows)**: 13 emitting mentions with no triple (13 Hamid
     verdicts: NoSeparateEnablesFact — the sequence fact already records the
     relationship); 2 held after superseding their earlier row-level
     approvals. The enables assertions are kept as non-emitting evidence.
   The G1 split lives in `review-evidence/enables-g1-split.csv`.

   **Disguised-sequence control (implemented 2026-09-26):** when an `enables`
   assertion connects same-parent sibling activities and a documented
   `precedes` or `follows` fact already represents the relationship, do not
   emit a separate `core:enabledBy` fact unless an explicit row-level approval
   establishes both **(a)** source-backed target identity (stable ID or
   explicit reference in the source definition), and **(b)** independent
   capability-enablement evidence beyond sequence, meeting the Answer 3 test.
   Same-parent plus sequence is a promotion block, not proof the source
   assertion is wrong. **Row-level exception precedence:** an explicit
   approved relationship verdict supersedes a later group-classification
   heuristic unless formally superseded through a new reviewed decision.
   Precedence applies only to verdicts that met every control in force when
   they were made. A later control that exposes a missing required premise
   supersedes the verdict through the supersession-by-control-refinement rule,
   with the decision history kept (precedent: REL-00129, REL-00728,
   2026-09-26).

   The 13 `NoSeparateEnablesFact` rows are not workbook-correction items.
   The source's `enables` wording may stand; it is kept as non-emitting
   evidence because the `precedes`/`follows` fact already records the
   relationship.

   **Gate:** no `core:enabledBy` fact from any of the 15 G2 rows;
   REL-00129 and REL-00728 checked as absent; their `precedes`/`follows`
   facts (on REL-00131 and REL-00734) checked as present.

   **Status: Approved Baseline (Hamid 2026-09-26).**
4. **`requires` → `core:requires`** for 5 genuine prerequisite-condition rows, approved
   by Hamid 2026-09-25 (REL-00158, REL-00168, REL-00247, REL-00872, REL-00873);
   REL-00208 held for workbook correction — no remap at emission.
   `core:requires`: the source cannot validly start, proceed, or reach its
   intended controlled state without the target activity or the condition the
   target produces. It is not a remap target for other verbs. REL-00873 is
   limited to credit-controlled onboarding under applicable policy.
5. **One canonical storage direction per inverse pair.** Stored forms:
   `core:dependsOn` family (`dependsOnOutputOf`, `informedBy`, `requires`,
   `enabledBy`, `constrainedBy`, `triggeredBy`), `core:precedes`,
   `core:governedBy`, `core:assuredBy`. Inverse properties may be declared for
   query and navigation. Materialized inverse triples are never written to
   the canonical facts store. Source verbs `follows`, `informs`,
   `constrains`, `triggers`, and `enables` are always stored in the canonical
   direction, with the raw verb kept in provenance. Mirror mentions (for
   example `A precedes B` + `B follows A`) merge into one canonical fact. No
   transitivity asserted without a separate semantic decision.

6. **Enablement is not reciprocal by default** (Hamid 2026-09-24). A mutual
   `enables` pair (A enables B and B enables A) emits a direction only if that
   direction passes a context test independently. A direction held up only by
   its mirror row is not evidence. Control, authority, prerequisite, cadence,
   sequencing, and close-feed dependency must not be normalized into
   `core:enabledBy`: "Market Risk Management enables Trade Capture" means
   governance/constraint (risk limits, delegated authority), and "Period-End
   Processing enables AR Reconciliation" means the close verifies/consumes
   reconciliation evidence — neither is capability enablement. Such rows are
   held for source-workbook correction, never reinterpreted at promotion.
   Precedent: REL-01303/REL-01056 approved; REL-01312/REL-01053 held
   (see `source-workbook-backlog.md`).

   **The four dependency meanings** (Hamid 2026-09-25) — the promotion layer
   must not silently translate between them:
   - `enables`: the source process, capability, framework, artifact, or control
     output makes the target process able to operate as defined.
   - `informs`: the source contributes context, evidence, intelligence, or a
     planning input, but is not necessary for the target to operate.
   - `dependsOnOutputOf`: the target consumes a specific output it needs from
     the source.
   - `requires`: the target needs an approved prerequisite, authorization,
     control, or condition from the source.
   **Source-meaning rule:** the promotion layer must not silently translate
   `enables` into `informs`. It holds the row and sends the meaning correction
   to the workbook backlog. **Source classification review:** a required
   business review when the relationship verb does not match the approved
   process definitions (precedent: REL-00936).

## Canonical direction table (raw verb → stored triple) — Approved Baseline (Hamid 2026-09-26)

> **Status:** Rows 1–12 approved. Two-cycle rules for `precedes` and
> `governedBy` approved and gate-enforced. Zero-inverse-predicate check
> gate-enforced. Later changes need a decision-log entry.

| Raw verb | Stored as | Example |
|---|---|---|
| `uses-input` (S, T) | `S core:dependsOnOutputOf T` | — |
| `informed-by` (S, T) | `S core:informedBy T` | — |
| `informs` (S, T) | `T core:informedBy S` | R1: `CM-1-1-4 informedBy CM-1-1-2-9-1` |
| `requires` (S, T) | `S core:requires T` | 5 rows approved 2026-09-25; REL-00208 held for workbook correction, no remap |
| `precedes` (S, T) | `S core:precedes T` | no reciprocal two-cycles (rule, gate-checked) |
| `follows` (S, T) | `T core:precedes S` | mirror-merged with `precedes` |
| `governed-by` (S, T) | `S core:governedBy T` | governed-by emission guard; ancestor/descendant restatements held; 7 recorded exceptions (REL-01309 + 6 from the 2026-09-26 pass: REL-00106, 00531, 00542, 00588, 00601, 00623; each not a precedent); no reciprocal two-cycles (rule, gate-checked); 43 → 38 emitting in the 2026-09-26 refresh; 38 → 18 in the 2026-09-26 governed-by pass |
| `constrained-by` (S, T) | `S core:constrainedBy T` | REL-00097 held (Refining target undefined and too broad) |
| `constrains` (S, T) | `T core:constrainedBy S` | 1 row |
| `triggers` (S, T) | `T core:triggeredBy S` | 7 rows (18 reviewed: 2 stand, 5 promote, 11 held 2026-09-26) |
| `assures` (S, T) | `T core:assuredBy S` | 5 rows approved 2026-09-26; 3 held (2 context, 1 workbook correction) |
| `enables` (S, T) | `T core:enabledBy S` (G3 only) | 84 stored + 33 G1a evidence-only + 13 G2 no-triple; G1b 29 held non-emitting (see Answer 3) |

The raw verb is retained in migration/provenance evidence on every emitted triple.

**Reconciliation:** 569 mentions map to their own predicate; 33 G1a mentions attach as duplicate evidence to existing facts — 602 mentions attached to stored facts, which with 13 G2 no-triple mentions gives 615 emitting.

*Footnote — non-emitting, non-held mentions: 2 Q5 structured-flow values, 1 ExternalGovernanceReference, 12 deferred.*
`core:consumes` / `core:produces` stay reserved for future identified
InformationObject instances (Q5).

## Mention → canonical fact → mirror accounting (refreshed 2026-09-26)

- Emitting mentions: **615**.
- G2 enables emitting no triple: 13 (approved 2026-09-26; the 2 former
  row-level exceptions superseded the same day — all 15 G2 rows now emit no
  `core:enabledBy` fact).
- Mentions attached to stored facts: **602** (569 map to their own predicate + 33 G1a duplicate evidence; 615 − 13 G2 no-triple).
- Canonical facts (distinct stored subject/predicate/object): **457** (477 before the 2026-09-27 precedes/follows amendment; 488 before the 2026-09-26 triggers pass; 508 before the 2026-09-26 governed-by pass; 603 before the 2026-09-26 informed-by pass; 716 before the uses-input pass; 717 before the REL-00873 supersession).
- Facts absorbing >1 mention (mirror/duplicate merges): **148**, covering 296 mentions.
  Typical case: `A precedes B` + `B follows A` → one `A core:precedes B` fact.
- Non-emitting mentions: 688 held + 12 deferred + 1 ExternalGovernanceReference
  (held pending property design) + 2 StructuredFlowValue (redirected to Q5 flow
  values). Total: 615 + 688 + 12 + 1 + 2 = 1,318. ✓

## Per-verb proposed predicate counts (emitting mentions)

| Raw verb | Stored predicate | Mentions |
|---|---|---|
| uses-input | core:dependsOnOutputOf | 101 |
| informed-by | core:informedBy | 44 |
| informs | core:informedBy (inverse) | 1 |
| requires | core:requires (5 approved 2026-09-25; REL-00873 supersession reversed 2026-09-26, scope-note label citation) | 5 |
| precedes | core:precedes | 136 |
| follows | core:precedes (canonicalized) | 158 |
| governed-by | core:governedBy | 18 |
| constrained-by | core:constrainedBy | 9 |
| constrains | core:constrainedBy (inverse) | 1 |
| triggers | core:triggeredBy | 7 |
| assures | core:assuredBy (5 approved 2026-09-26) | 5 |
| enables G3 | core:enabledBy (84 approved 2026-09-26) | 84 |
| enables G1a | merge as evidence on existing dependsOnOutputOf fact | 33 |
| enables G1b | HOLD for workbook correction (approved 2026-09-26; non-emitting) | 29 |
| enables G2 | no triple (approved 2026-09-26) | 13 |

Emitting mentions in this table: 616 (the G1b row is non-emitting and shown
for completeness). The 5 former row-level `core:enabledBy` verdicts were
superseded 2026-09-26; none remains emitting.

## Contradictions (3) — for Hamid

**Property rule (Hamid 2026-09-24; tightened 2026-09-26):** whether a mutual
pair is a contradiction depends on the property.
- **Sequence (`core:precedes`): no mutual pairs allowed.** A process cannot come
  both before and after another in the same lifecycle. Both mentions are held
  with a contradiction reason; the source is fixed in a later workbook batch.
  Emitting both would write a cycle into the sequence graph. Enforced with
  SHACL in Step 9 — not an OWL asymmetry axiom (an axiom would make a reasoner
  mark the whole graph inconsistent over one bad row).
- **`core:informedBy`: mutual pairs allowed.** Feedback loops are normal.
  Both directions emit if *each* has its own evidence; a direction promoted
  on nearness alone is held.
- **`core:dependsOnOutputOf`: no two-cycles (hard gate, Hamid 2026-09-26).**
  For a concept pair (A, B), the facts A → B and B → A cannot both be
  emitted. A detected pair blocks promotion until each row has an independent
  direction verdict; at most one direction is retained unless the source model
  is corrected to represent distinct artifacts or a different relation
  family. This supersedes the earlier "allowed where each direction is
  independently evidenced" reading.
- Zero mutual `precedes` pairs exist in the emitting set (verified).

Ruled pairs (not contradictions):
- **Mutual informedBy, Safety ↔ Fleet (REL-00500 / REL-00503):** allowed as a
  feedback loop, but REL-00503 was B-only (nearness) and is held per the
  property rule; REL-00500 (A:explicit-reference + B) emits.
- **Mutual governedBy, Accounting ↔ procedures child (REL-01309 / REL-00366):**
  not a contradiction in the emitting set. REL-01309 **approved** by Hamid
  2026-09-24 — a parent capability governed by its own procedures child fits
  the approved Accounting-cluster pattern (set-versus-apply: the procedures
  child governs how the parent executes). REL-00366 held — **restates
  hierarchy**: child "governed by" parent mostly repeats `skos:broader`.

`contradictions.csv` carries the full rows; it is 0 (empty) — all three
reciprocal pairs resolved 2026-09-26, each reverse fact verified unique
before removal. Summary:

1. **Mutual dependsOnOutputOf** — `Reconcile And Report Indirect Tax` ↔
   `Determine Taxability` (REL-01061 / REL-01065). Retained REL-01061
   (tax reporting consumes taxability); held REL-01065.
2. **Mutual dependsOnOutputOf** — `Maintain Price & Discount Master Data` ↔
   `Implement Rebate` (REL-00917 / REL-00862). Retained REL-00862
   (rebate consumes price/discount master data); held REL-00917.
3. **Mutual dependsOnOutputOf** — `Manage Credit Card Transactions` ↔ `Perform
   Cash, Acquirer, and Receivables Reconciliation` (REL-00884 / REL-01029).
   Retained REL-01029 (reconciliation consumes card transactions);
   held REL-00884.

Zero reciprocal `core:dependsOnOutputOf` two-cycles is a hard gate.

## Review instruments

- `review-evidence/requires-6-review-batch.csv` — 6 rows decided 2026-09-25:
  5 approved as `core:requires` (REL-00158, REL-00168, REL-00247, REL-00872,
  REL-00873, the last with a credit-controlled-onboarding scope note);
  REL-00208 held for workbook correction (no remap at emission).
- `assures-review.csv` — 8 rows decided 2026-09-26: 5 approved as
  `core:assuredBy` (REL-00401, REL-00719, REL-00801, REL-01269, REL-01270);
  3 held — REL-00355 and REL-00385 (context holds retained:
  support/documentation is not assurance), REL-01106 (held for workbook
  correction; its `core:assuredBy` fact was removed, verified unique, and no
  substitute emitted). None names Internal Audit as source — no false
  audit-authority grant.
- `enables-review.csv` — all 399 rows with pipeline-built group, proposed
  disposition, decision cells blank.
- `review-evidence/enables-g1-split.csv` — G1 split per Hamid 2026-09-25:
  **G1a (81)** duplicates proposed for merge as evidence; **G1b (31)**
  proposed hold for workbook correction (verb change, not a duplicate).
- `review-evidence/enables-g3-genuine-enablement-review-batch.csv` — G3
  (249 review rows: 143 explicit-reference, 106 nearness-only; 21
  context-held rows outside the review population). Decided 2026-09-26:
  Section A — 84 approvals emitting (explicit target identity); Section B —
  all 96 rows held (60 in B1–B4; 36 in B5: 33-row class verdict +
  3 supersessions — REL-01016, REL-01124, REL-01174), none emitting. Six
  further supersessions (REL-00129, REL-00243, REL-00304, REL-00489,
  REL-00728, REL-01006) sit outside the Section B population. Every
  emitting `core:enabledBy` fact was matched to its target by an explicit
  reference in the source definition and carries a row-level approval.
- `review-evidence/st-enables-search.csv` — Supply & Trading enables sweep:
  21 rows. Verdicts 2026-09-26: 2 approved as bounded `core:enabledBy`
  (REL-00433, REL-01172) and emitting; 4 prior approvals superseded under
  the nearness-only identity rule (REL-00437 in G3-B3; REL-00489, REL-01124,
  REL-01174 in G3-B5); the rest held (5 pattern-holds, ambiguous holds,
  and hierarchy holds).
- `review-evidence/11-slug-ancestor-descendant-rows-for-review.csv` — 10 held
  ancestor/descendant governance rows (REL-01309 approved).

## How to review (sequence agreed 2026-09-25)

1. requires (6 rows).
2. assures (7 rows).
3. constrained-by (10) batch (to be built); triggers (7) batch complete 2026-09-26.
4. The 3 contradictions and the 10 ancestor/descendant governance rows.
5. The Supply & Trading search (pattern-holds to backlog).
6. G1 split (G1a merge / G1b hold), then G2, then G3.
7. The mapping doc itself (the 5 answers + canonical direction table) —
   **in progress now** (figures refreshed 2026-09-26; section-by-section
   approval to follow).
8. Nothing emits until every decision cell is resolved and the release
   checklist (including fresh no-consumer attestation) is green.

Steps 1–6 completed 2026-09-26: requires (5 approved, 1 held), assures
(5 approved, 3 held), constrained-by (10 approved, 1 held), triggers
(18 approved), 3 contradictions resolved, 10 ancestor/descendant rows held
(1 recorded exception), S&T sweep decided, G1a/G1b/G2/G3 decided.

**Resolved 2026-09-26:** the 3 `dependsOnOutputOf` reciprocal pairs are
resolved (one direction retained, the reverse held after fact-provenance
uniqueness validation); `contradictions.csv` is 0. The no-two-cycle hard
gate above supersedes the earlier "allowed where each direction is
independently evidenced" reading. The 2 mutual `enabledBy` pairs remain
**held** (Hamid 2026-09-24: enablement is not automatically reciprocal) —
see `review-evidence/enabledby-mutual-review-batch.csv`.

## Governed-by (added 2026-09-25, Hamid)

- **Governed-by:** a process/capability operates within a policy, authority,
  control framework, delegation, limit, or approved rule owned by another
  process/capability.
- **Scope-qualified governance relation:** a governance relation applying only
  to a named control boundary — e.g. credit eligibility, IP/licensing, or
  trading-compliance obligations — not entire operational ownership.
- **Governed-by emission guard** (future promotion script): emit
  `core:governedBy` only when the source definition/scope explicitly says the
  source operates within target-owned policy/framework/authority, applies
  target-owned limits/rules/guardrails/delegation/approved criteria, or is
  subject to a specific target-owned control boundary. Do NOT emit merely
  because: source and target share a parent; the target monitors compliance
  generally; the source must comply with regulation; the source consumes target
  information; or the target provides review, support, or assurance without
  governance ownership.

## Requires (added 2026-09-25, Hamid)
- **`core:requires`:** a directed relationship in which the source activity
  cannot validly start, complete, proceed, or reach its intended controlled
  state without the target activity, its completed control, or its required
  resulting condition.
- **Not `core:requires`:** a relation inferred solely because the target may
  later consume, calculate, depend on, or use information related to the
  source.
- **No semantic remap at emission:** the "no verb change at promotion" control
  applies equally to `requires` and `enables`. Precedent: REL-00208 held for
  workbook correction — neither `core:requires` nor `core:dependsOnOutputOf`
  may be emitted from its present assertion.
- Approved 2026-09-25 (5 rows, stored as `core:requires`): REL-00158,
  REL-00168, REL-00247, REL-00872, REL-00873. Scope note on REL-00873: a
  credit-controlled onboarding prerequisite — not every prospect/card-account
  setup requires a non-zero limit or full facility; the required credit/risk
  decision must be established under the applicable onboarding policy. The
  scope note lives in the rationale column; the stored triple is plain
  `core:requires`.
- Requires mapping: approved for these five evidenced rows only; no blanket
  remapping rule approved.

## Basis change versus bucket change (standing rule, Hamid 2026-09-25)

- Approving a row that is already emitting changes only its basis
  (proposed → `D:hamid-verdict`); the count does not move.
- Counts change only when a row moves between buckets (emitting ↔ held ↔
  deferred). Every expected ledger effect is stated in bucket terms from now
  on.

## Assures (added 2026-09-25, Hamid)

- Stored direction follows the dependent-to-dependency rule: `core:assuredBy`
  runs from the thing being assured to the assurance activity.
- The row-level check is whether the source actually carries out assurance
  (verification, reconciliation, control testing, quality checks) over the
  target's outputs.
- `assures` used loosely to mean "supports", "ensures availability of", or
  "feeds" gets the REL-00445/REL-00208 treatment: held for workbook
  correction, never remapped at emission.
- A row whose direction is already on the workbook backlog is not emitted on
  any reading of the verb; direction must be corrected first.

## `core:assuredBy` scope boundary (approved, Hamid 2026-09-26)

> `core:assuredBy` applies when the assurance activity performs a defined
> governance, compliance, quality, review, control-testing, or equivalent
> oversight role over the assured activity or outcome. It does not mean
> operationally supports, supplies, documents, evidences, balances, fulfills,
> feeds, or is merely necessary for the target.

Approved 2026-09-26 (5 rows, stored as `core:assuredBy`): REL-00401,
REL-00719, REL-00801, REL-01269, REL-01270. Held: REL-00355 and REL-00385
(context holds retained — support/documentation is not assurance); REL-01106
held for workbook correction with its existing `core:assuredBy` fact removed
and no substitute emitted.

## Constrained-by (added 2026-09-26, Hamid)

- **`core:constrainedBy`** is stored from the activity, decision, process, or
  outcome whose feasible choices are bounded to the activity, policy,
  control, operating envelope, allocation limit, credit limit, capacity,
  inventory condition, or other source of binding restriction.
- **Canonicalization rule:**
  ```text
  source constrained-by target
  → source core:constrainedBy target

  source constrains target
  → target core:constrainedBy source
  ```
  Valid only where the source assertion explicitly supports the inversion and
  the original verb/direction remains preserved in relationship evidence
  (e.g. canonical-facts `raw_verbs` + notes). Do not infer inverse direction
  from proximity or reclassify an unrelated relationship as a constraint.
- **Exclusions:** `core:constrainedBy` does **not** mean: merely informed by
  or using a data input from; sequenced before or after; governed, owned, or
  contained by; associated with a broad capability or domain label; receiving
  support, advice, a recommendation, or a report; an optional operating
  consideration rather than a defined feasibility, policy, capacity,
  allocation, credit, or control boundary.
- Approved 2026-09-26 (10 rows, stored as `core:constrainedBy`): REL-00015,
  REL-00018, REL-00024, REL-00087, REL-00091, REL-00099 (approved canonical
  inversion of source `constrains`; original assertion preserved in the fact
  row as `raw_verbs: constrains`), REL-00103, REL-00574, REL-00894, REL-01284.
  Held: REL-00097 (context hold retained — broad Refining target undefined;
  source author must supply a defined, more specific target).

## Triggers (added 2026-09-26, Hamid)

- **`core:triggeredBy`** is stored from an activity initiated or materially
  invoked by a defined event, exception, monitoring outcome, change, referral,
  detection, or handoff to the activity that generates, detects, manages, or
  records that trigger condition.
- **Canonicalization:**
  ```text
  source triggers target
  → target core:triggeredBy source
  ```
  This preserves the dependency-style direction of the other canonical
  predicates: the activity that must occur is stored as dependent on the
  triggering activity.
- **Boundary conditions:** a valid trigger requires more than ordinary
  sequence or general support. The source must generate, detect, identify,
  raise, enact, or formally hand off a condition that calls the target
  activity; the target must be an action, response, reassessment, exception
  process, reporting obligation, or workflow that occurs because of that
  condition. "Feeds", "informs", "supports", "uses", "precedes", and "is
  associated with" do not become `core:triggeredBy` without an event or
  condition that invokes the target.
- **Affirmative-citation definition (adopted 2026-09-26):** an affirmative
  citation for `triggers` must tie the source's event or result to the target
  (trigger, route to, refer, escalate, hand off). A statement of where work
  is done does not count.
- Reviewed 2026-09-26 (18 rows): 2 STAND (rule 4: REL-00725, REL-00897);
  5 PROMOTE (`D:hamid-verdict`: REL-00127, REL-00235, REL-00236, REL-00246,
  REL-00901 — each with an event-to-target citation); 11 HOLD
  (`D:hamid-verdict` / `NoAffirmativeTriggerLink` / `Supersedes2026-09-26Approval`:
  REL-00049, REL-00163, REL-00169, REL-00170, REL-00252, REL-00291, REL-00396,
  REL-00398, REL-00400, REL-00403, REL-00892). 7 `core:triggeredBy` facts
  emitting. Scope notes: card-process triggers (REL-00897/00901) are
  conditional workflow triggers within program controls, not universal.

## No-two-cycle rule (hard gate, Hamid 2026-09-26)

> **No two-cycle rule for `core:dependsOnOutputOf`:** for a concept pair
> (A, B), the facts A → B and B → A cannot both be emitted under
> `core:dependsOnOutputOf`. A detected pair blocks promotion until each row
> has an independent direction verdict. Retain at most one direction unless
> the source model is corrected to represent distinct artifacts or a
> different relation family.

- `ContextualInferredSibling` may support triage but cannot independently
  justify a directional dependency fact (precedent: REL-01061 approved on its
  definitions, sibling context supplementary only).

## Unique-candidate triage-signal rule (Hamid 2026-09-26)

> **A unique-candidate match is a triage signal only.** A candidate selected
> only through label similarity, unique-candidate filtering, structural
> proximity, or classifier nearness can never promote a row or keep a fact
> emitting on its own. It requires either explicit target evidence in source
> material or separately recorded manual identity confirmation backed by
> source material.

Section B is the proof: 96 nearness-only rows reviewed, 96 held — a unique
label match was never enough, 96 times out of 96. The classifier should stop
marking such rows `PROMOTE`.
- Resolved 2026-09-26: pair A retained REL-00862 / held REL-00917; pair B
  retained REL-01029 / held REL-00884; pair C retained REL-01061 / held
  REL-01065. All three reverse facts were unique and removed; the global
  reciprocal-cycle assertion now requires zero two-cycles.

## Hierarchy non-duplication rule (hard gate, Hamid 2026-09-26)

> **Ancestor/descendant non-duplication rule:** Do not emit a semantic
> relationship solely because the source and target are in an
> ancestor/descendant or same-branch parent-child relationship. Hold the row
> unless independent evidence establishes a relationship that is not already
> expressed by the business hierarchy.

- Held 2026-09-26 (facts removed, each verified unique): REL-00002,
  REL-00013, REL-00466, REL-00469, REL-00764, REL-00768, REL-00773, REL-00912,
  REL-00923, REL-00925. The relationship is retained only as historical
  source evidence pending source-author clarification.
- **Permitted exception (all five must hold):** (1) documented relationship
  beyond containment; (2) the definition identifies distinct governance,
  control, decision-right, output-consumption, or externally reusable
  enablement semantics; (3) the rationale identifies that independent
  semantic evidence rather than the hierarchy path; (4) the evidence ledger
  preserves the hierarchy path and the exception rationale; (5) a reviewer
  approves the row explicitly — no automatic promotion; (6) the target is
  identified by source-backed evidence under the identity rule as finally
  scoped.
- **Recorded exception:** REL-01309 (already approved; prior decision
  unchanged, original evidence marker and rationale intact). It is not a
  precedent for automatic emission. Its match basis is included in the
  scope census; the recorded exception stands only if it passes all six
  exception conditions.
- **Recorded exceptions (Hamid 2026-09-26, governed-by pass).** Each passes
  all six exception conditions and is **not a precedent** for automatic
  emission:
  - **REL-00531** (`CM-1-3-1-3-1 core:governedBy CM-1-3-1-3`).
    (1) Independent semantics: a privacy-governance control — the child
    "operates under the shared personal-data governance statement recorded
    at" the parent, which is governance of data handling, not containment.
    (2) Identity: source CM-1-3-1-3-1, target CM-1-3-1-3 (stable-ID).
    (3) Rationale: the citation names a specific governance instrument
    (the shared personal-data governance statement), not the hierarchy path.
    (4) Hierarchy path: CM-1-3-1-3-1 → CM-1-3-1-3 (child → parent).
    (5) Hamid approved 2026-09-26. (6) Target identified by stable ID.
  - **REL-00542** (`CM-1-3-1-4-1 core:governedBy CM-1-3-1-4`).
    (1) Independent semantics: same privacy-governance control as REL-00531.
    (2) Identity: source CM-1-3-1-4-1, target CM-1-3-1-4 (stable-ID).
    (3) Rationale: citation names the shared personal-data governance
    statement, not the hierarchy path.
    (4) Hierarchy path: CM-1-3-1-4-1 → CM-1-3-1-4 (child → parent).
    (5) Hamid approved 2026-09-26. (6) Target identified by stable ID.
  - **REL-00588** (`CM-1-3-2-1-1 core:governedBy CM-1-3-2-1`).
    (1) Independent semantics: a legal constraint — "franchise constraints…
    (cluster PMPA statement at [parent])"; PMPA is the franchise law, an
    external legal instrument recorded at the cluster level.
    (2) Identity: source CM-1-3-2-1-1, target CM-1-3-2-1 (stable-ID).
    (3) Rationale: the citation names an external legal constraint, not
    the hierarchy path.
    (4) Hierarchy path: CM-1-3-2-1-1 → CM-1-3-2-1 (child → parent).
    (5) Hamid approved 2026-09-26. (6) Target identified by stable ID.
  - **REL-00601** (`CM-1-3-2-2-2 core:governedBy CM-1-3-2-2`).
    (1) Independent semantics: same PMPA legal constraint as REL-00588.
    (2) Identity: source CM-1-3-2-2-2, target CM-1-3-2-2 (stable-ID).
    (3) Rationale: citation names the PMPA franchise-law constraint.
    (4) Hierarchy path: CM-1-3-2-2-2 → CM-1-3-2-2 (child → parent).
    (5) Hamid approved 2026-09-26. (6) Target identified by stable ID.
  - **REL-00623** (`CM-1-3-2-4-2 core:governedBy CM-1-3-2-4`).
    (1) Independent semantics: same PMPA legal constraint as REL-00588.
    (2) Identity: source CM-1-3-2-4-2, target CM-1-3-2-4 (stable-ID).
    (3) Rationale: citation names the PMPA franchise-law constraint.
    (4) Hierarchy path: CM-1-3-2-4-2 → CM-1-3-2-4 (child → parent).
    (5) Hamid approved 2026-09-26. (6) Target identified by stable ID.
  - **REL-00106** (`CM-1-1-4-7-7 core:governedBy CM-1-1-4`).
    (1) Independent semantics: decision rights — "the Refinery Planning and
    Optimization (CM-1-1-4) decision this step records"; the ancestor
    decides and this step records that decision.
    (2) Identity: source CM-1-1-4-7-7, target CM-1-1-4 (stable-ID).
    (3) Rationale: the citation names a decision right exercised by the
    ancestor, not the hierarchy path.
    (4) Hierarchy path: CM-1-1-4-7-7 → CM-1-1-4-7 → CM-1-1-4
    (grandchild → ancestor).
    (5) Hamid approved 2026-09-26. (6) Target identified by stable ID.
- Applies to every predicate, not only `governedBy`.
- The 10 held rows are on the workbook backlog for source-author
  clarification.
- **Gate:** no fact from the 10 held rows; any ancestor/descendant pair
  that emits must carry a recorded exception that passes all six
  conditions.

**Status: Approved Baseline (Hamid 2026-09-26).**

## Enablement definition (reinforced by the S&T sweep, Hamid 2026-09-26)

- **Enablement:** a maintained, governed, or operationally necessary
  capability/input base that makes the target able to perform its stated
  function (e.g., vetted term slate for recommendation production,
  quality-screened options for trading coordination, entitlement rules and
  governed agreement terms for exchange utilization, a validated
  feedstock-demand signal for trading action).
- **Not enablement:** advisory recommendations, evaluations, optional
  analysis, decision proposals, approval submissions, ordinary sequence, a
  potential output dependency, or a broad parent-child relationship.
- **No emission-time remapping:** an `enables` assertion that appears better
  expressed as another predicate is held until source correction; semantic
  plausibility alone never authorizes reclassification at promotion time.
  (Precedent: REL-00436's plausible `dependsOnOutputOf` was held; the fact
  survives only via the independent `uses-input` row REL-00447.)
- **PTC-002** (Refinery Planning and Optimization decides; Supply & Trading
  advises) remains the standing recommendation-versus-enablement control.
- Approved 2026-09-26 (bounded): REL-00433, REL-01172. Scope limits recorded
  per row: approval enables the stated process path, never asserts decision
  authority, binding plans, or trade approval. Four earlier S&T approvals
  were superseded under the nearness-only identity rule: REL-00437 (G3-B3,
  2026-09-26) and REL-00489, REL-01124, REL-01174 (G3-B5, 2026-09-26) —
  each had judged the relationship plausible without evidence of which
  target the source meant.

## Duplicate-evidence merge (defined 2026-09-26, Hamid G1a verdict)

- **Duplicate evidence merge:** retention of an additional source assertion
  as provenance for a canonical fact already independently supported by
  another assertion, without changing the fact's predicate, direction, or
  meaning.
- **Independent fact survival:** the canonical fact remains valid after the
  duplicate source mention is removed because at least one separately
  approved source record still supports it.
- The merge preserves both raw source verbs in provenance
  (e.g., `raw_verbs: uses-input; enables`), records the duplicate row as
  evidence only, and never treats the duplicate wording as authority to
  change the fact's predicate.
- **True duplicate:** a G1a row is a true duplicate only if its `enables`
  mention resolves to the same source and target slugs, in the same canonical
  direction, as an independently approved `uses-input` row, and maps to that
  row's canonical fact.
- **Target-match census (2026-09-26):** each attached mention records how its
  target was matched — `target_match` in the G1a batch. 33 rows carry a
  stable identifier in the mention text (identity confirmed); 44 rows matched
  by unique exact preferred-label only. A mention matched by nearness only
  attaches as **identity-unconfirmed provenance**: it never counts toward the
  fact surviving, and it never counts as corroboration.
- Precedents: REL-00436 attaches as duplicate provenance on the
  independently-evidenced `uses-input` fact (REL-00447, via the
  2026-09-26 scope-note range citation route); the fact survives through
  the approved `uses-input` row alone. REL-00214 had no citation route
  and was held in the 2026-09-26 uses-input pass; its fact was removed
  and the attached `enables` mention REL-00152 held with it.
  (REL-00152's own target match was label-only — it is
  identity-unconfirmed provenance.)
- G1a applies only to true duplicates. The former exclusion for rows with
  row-level `core:enabledBy` approvals (REL-00243, REL-00304, REL-01006)
  is moot: those approvals were superseded 2026-09-26 (G3-B5) under the
  nearness-only identity rule, and the rows are now held with no fact.
- **Gate:** every G1a row names at least one independent `uses-input`
  supporter in `merged_with_rows`; source and target match after slug
  resolution; the fact survives if the `enables` mention is removed; no G1a
  row is the sole evidence for its fact; no merge creates a fact.
- Held mentions attached as duplicate provenance (REL-00152, REL-00436)
  stay counted as held (in the 657), add no support, and are not
  emitting.
- **Counts:** 81 split → 77 approved (4 excluded: REL-00243, REL-00304,
  REL-01006 superseded; REL-00936 source-classification hold). 77 → 33
  emitting (2 property-rule holds [REL-00152, REL-00436] + 42 held in the 2026-09-26 uses-input pass). The G1a report was
  regenerated to replace the `<generator object …>` values with fixed,
  readable values.

**Status: Approved Baseline (Hamid 2026-09-26).**

## Recommendation versus enablement (added 2026-09-25, Hamid)

- **Recommendation rule:** a process that recommends, advises, or proposes an
  input which another process may accept, modify, or reject does **not**
  enable that process, even when the recommendation feeds a binding decision.
  An `enables` assertion with this meaning is held for source correction
  (typically to `informed-by`). It is **never remapped to `core:informedBy`
  at emission**; only a corrected source assertion, with a fresh verdict,
  can emit.
- The rule applies across the enterprise. **PTC-002** is its Supply &
  Trading instance: Refinery Planning and Optimization decides; Supply &
  Trading advises. Precedent: REL-00445 (Recommend Feedstock Slate and Run
  Rate → Refinery Planning and Optimization) held for source correction from
  `enables` to `informed-by`. Applied outside S&T: REL-00232 (portfolio
  credit analytics → credit limits, A2); REL-00818 and REL-00820 (spend and
  ROI analysis → budget and mix decisions, A3); REL-00750 and REL-01206
  (portfolio and lifecycle recommendations → product/service change, S&T
  sweep) — all held.
- **S&T sweep, 2026-09-26 (21 rows):**
  - **6 approved** as bounded `core:enabledBy`. 2 still emit (REL-00433,
    REL-01172). 4 were superseded under the identity rule: REL-00437 (B3),
    REL-00489, REL-01124, REL-01174 (B5).
  - **13 held** for source correction: 5 REL-00445-pattern and 8 ambiguous.
  - **2 hierarchy holds** kept (REL-00466, REL-00469).
  - REL-00436's fact survives on its independent `uses-input` row REL-00447
    (range citation), not on the `enables` assertion. REL-00152's fact was
    removed with REL-00214 (held, no citation route) in the 2026-09-26
    uses-input pass.
- **Scope limits on the surviving approvals:** REL-00433 and REL-01172
  enable the **production of the recommendation**. They do not assert
  decision authority, a binding plan, or trade approval.

**Status: Approved Baseline (Hamid 2026-09-26).**

## G1b no-verb-change rule (hard gate, Hamid 2026-09-26)

- **Rule:** when an `enables` source assertion has only an opposite-direction
  `informed-by` counterpart and no independently approved `uses-input`
  evidence for the same directed pair, the `enables` assertion must not emit
  `core:dependsOnOutputOf`. The source assertion may be retained only as
  non-emitting evidence unless it receives a separate, explicit row-level
  `core:enabledBy` approval that meets Answer 3: source-backed target
  identity, and capability-effect evidence.
- **Why:** the pipeline was emitting `core:dependsOnOutputOf` from `enables`
  assertions on informed-by-only reverse evidence — a silent verb change
  prohibited by Rule 11. Reverse `informed-by` establishes an information
  relationship, not an output dependency; it is not independent `uses-input`
  evidence and cannot justify reclassifying the opposite-direction `enables`
  record. A reverse `informed-by` row is evidence only for its own
  `informedBy` fact (Answer 2). It never establishes target identity or
  predicate for the opposite-direction row.
- **Precedent:** 29 G1b rows held (HOLD / D:hamid-verdict / G1bNoVerbChange);
  28 stored `core:dependsOnOutputOf` facts removed after fact-provenance
  uniqueness validation (all 28 were unique single-row facts); reverse
  informed-by facts preserved on their own records. REL-00489's "leave
  unchanged" listing was superseded 2026-09-26 (G3-B5): its `core:enabledBy`
  fact was removed (verified unique) and the row is a no-fact hold;
  REL-00469's hierarchy hold untouched.
- **Counts:** 29 held = 28 emitting rows whose facts were removed +
  REL-01224 (already held). All 29 are on the workbook backlog.
- **Gate:** GREEN since 2026-09-26. It fails if any `core:dependsOnOutputOf`
  fact is supported only by an `enables` source row, or is emitted only
  because a reverse `informed-by` exists. For each held G1b row — no
  `core:dependsOnOutputOf` fact from its enables row; no fact emitted
  solely because reverse informed-by exists; reverse informed-by fact
  present through its own row-level evidence **if** the reverse row has a
  route (stable-ID, affirmative citation, two-way, or approved decision);
  otherwise the reverse row is held with no fact. For REL-00489 — superseded;
  no emitted fact. For REL-00469 — no emitted fact.

**Status: Approved Baseline (Hamid 2026-09-26).**
