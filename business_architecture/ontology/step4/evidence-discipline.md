# Step 4 evidence discipline (project text)

This is the approved text of the Step 4 evidence discipline (approved
2026-09-24), moved word for word from §3 of the ontology playbook on
2026-10-05, when the playbook was rewritten as a company-neutral method
(EPM-DEC-001-0024, decided 2026-10-06). The playbook's §3 now states the same rules in
general terms. This file keeps the project's exact wording, counts and
precedents. If the two ever differ for this project, this file applies.

Source: `ontology-playbook.md` at commit `c13dd2e`, lines 721 to 1046.

> Status: APPROVED 2026-09-24. Canonical. Restore note: this section was
> dropped in the prescriptive rewrite's first pass and restored in full
> 2026-09-26 — the rewrite's distilled bullets in §1 Step 4 are a summary
> of this section, not a replacement.

Step 4 promotes the provisional `intake:` annotations to real ontology
properties. The intake layer is the only copy of facts like "which
process uses which input" and "which process the workbook says this one
follows." If the promotion is sloppy, those facts are corrupted silently
— the triples look fine, but they no longer say what the business said.
The eleven rules below are how we keep that from happening. They were
developed promoting 5,571 intake triples and 1,318 relationship
mentions, and several of them exist because an earlier, weaker version of
the check failed and we fixed the premise instead of patching the row.

### The eleven rules

1. **Pin all evidence to one approved `main` SHA.** Every evidence file
   (dispositions, reviews, ledgers) carries `baseline_sha`, and the byte
   hashes of the baseline inputs are recorded. Before the eventual
   release, re-pin to the then-current approved `main`; all build and
   evidence artifacts must cite the same SHA.
2. **Regenerate old review packages after the taxonomy evolves.** A review
   package built against last month's taxonomy is a review of last
   month's data. After any rename/reparent/reclassification, regenerate
   the package from the pinned baseline and diff it field-by-field
   against the old one — do not merely re-validate the old CSV.
3. **Carry approvals only for field-equivalent rows, except where an
   evidence-strengthening change adds a stable identifier or source
   citation while the source, verb, resolved target, and disposition
   remain unchanged. The exception must be recorded explicitly.** An
   approval granted against v1.1 carries to v2 only if the row is
   identical on every evidence field (same concept, same label key, same
   candidate) — or qualifies under the recorded strengthening exception.
   Anything else goes back for review — only the differences, not the
   whole package.
4. **Treat labels as candidate filters, never as identity evidence.** A
   matching label proposes a candidate; it never proves the target. Slugs
   and IRIs are identity.
5. **Structural nearness alone is sufficient only for approved local
   sequence-pattern relations between sibling processes. For enables,
   governed-by, requires, assures, and dependency relations, it must be
   combined with independent definition, scope, reciprocal, or approved
   decision evidence.** A unique label match earns a candidacy, not a
   triple. Promotion needs at least one of: an explicit citation of the
   target in the source's definition or scope note; a consistent two-way
   mention (strict inverse pairs only); structural nearness inside the
   same decomposition branch (siblings for sequences; shared L2/L3 branch
   and no ancestor/descendant relation otherwise) *plus* one of the
   independent evidence types above for non-sequence relations. Label
   match alone = held for domain-batch review.
6. **Sample every batch of automatic promotions per domain, and stop at
   the first wrong resolution.** Sample `max(10, ceil(5%))` per domain
   (seeded, so it is reproducible). A human reads each sampled row's
   definitions and records OK or FLAG. One wrong resolution stops the
   line: tighten the rule and re-run — never patch the single row.
7. **Conserve every source predicate and every relationship mention
   through migration.** The Q2 ledger accounts for all 5,571 intake
   triples across 13 predicates and all 1,318 relationship mentions:
   emitted, held, merged, or redirected. No source record leaves the
   migration without a recorded disposition. DroppedAsNonProcessProse is
   a governed disposition, not unaccounted loss. Conservation is proved
   by arithmetic, not asserted; the exact counts live in the ledger's
   evidence section, not in this rule.
8. **Store one canonical direction per fact; derive inverses, never store
   mirrors.** `A precedes B` and `B follows A` are one fact stored as
   `A core:precedes B`. Mirrored rows inflate the fact count and let
   contradictions hide. Pairs that contradict one another under a
   property that does not allow mutual relation are held, not emitted.
9. **Keep raw verb and source-row evidence outside RDF reification for
   1.0.0.** The evidence (which workbook verb, which row, which test
   promoted it) lives in versioned CSVs beside the build, not as reified
   triples. Revisit after 1.0.0 if consumers need provenance in-graph.
10. **Release gate: same-SHA evidence plus a fresh no-consumer
    attestation.** The release build, the evidence package, and the
    consumer-impact scan must all cite one SHA. And immediately before
    flag-day, re-confirm the foundation-stage attestation (no consumers
    yet) — a stale attestation is not an attestation.
11. **Emission never changes source meaning.** Promotion may emit, hold,
    defer, or reclassify a source relationship; it may not replace a
    verb, invent a target, or reinterpret business meaning. Corrections
    are made in the workbook through a reviewed authoring change.

### Why each rule exists (the failures that taught them)

- **Stale baselines silently approve different data.** The v1.1→v2
  comparison found 53 rows whose raw target labels changed under them
  (Step 3d renames), 1 genuinely new relationship row (the approved R1
  interface), and 35 rows whose evidence got *stronger* (slug
  parentheticals added to mentions). None of that is visible without the
  SHA pin and the field-by-field diff (rules 1–3). Reviewing v2 rows
  against v1.1 approvals without the diff would have approved renames
  nobody re-read.
- **Labels drift and collide.** "Refinery Planning" became "Refinery
  Planning and Optimization"; "Determine Taxability" names two different
  concepts in two decompositions; the CVP strategy labels split four
  ways in Step 3d. Any pipeline that joins on labels inherits every one
  of those events as a silent misresolution (rule 4).
- **The first context pass was confidently wrong.** It promoted 915 rows
  on tests that did not test what they claimed: "explicit reference"
  read terminology notes instead of definitions, any backlink counted
  as two-way confirmation, and hierarchy proximity counted as
  relationship evidence. The corrected pass promotes 852 and holds
  169 — including rows the old pass had blessed. The lesson was not
  "fix the 63 rows" but "the premise was untested": we wrote the failing
  checks first, watched them fail, then fixed the implementation
  (rule 5, and the attack-the-premise trigger below).
- **Zero `intake:` triples proves deletion, not migration.** A build
  that drops the intake namespace and shows no intake triples has proved
  the annotations are gone. Migration is proved only by the ledger:
  every triple and every mention accounted for, each with a recorded
  disposition (rule 7).
- **Mirrored rows inflate facts.** 386 mentions collapse into 193 facts
  once mirrors merge. Mirrored relationship mentions materially inflate
  the raw mention count; the conservation ledger reports the exact
  mention-to-canonical-fact reconciliation for each release (rule 8).
- **Release evidence from mixed commits is invalid.** A consumer-impact
  scan run against one SHA and a build cut from another is theater. One
  SHA for build, evidence, and scan — re-pinned at release time
  (rule 10).
- **Promotion logic must not author meaning.** A mistyped workbook verb
  ("assures" where the business meant "satisfies") cannot be repaired by
  the promotion script choosing a nicer predicate — that would launder
  an authoring error into the ontology. The script emits, holds, or
  defers; the correction goes through reviewed workbook authoring
  (rule 11).

### Standing triggers

- **Attack the premise:** two failed fixes on the same gate, or two "the
  checker never asserted that" moments on one class of check → stop
  writing fixes; census what the check does *not* cover and fix the
  premise.
- **Write the failing check first:** every regression fix starts with a
  gate assertion watched failing on the broken state, then the fix,
  then the pass.
- **Reviewer verdicts:** every evidence package gets the interrogate
  pass (Act On / Consider / Noted / Dismissed) before Hamid reviews it.


### Verb review methodology — how to judge a predicate family

Each verb gets its own review pass: one predicate, one batch, one set of
verdicts. The pass has four phases.

**Phase 1 — Lock the definition.** Write the predicate definition before
looking at rows. The definition must be falsifiable: it should be possible
to read a row and say "this fails the definition." A definition that every
row passes is not a definition. Each definition below is shaped by a
specific confusion it exists to prevent.

**Phase 2 — Build the review batch.** Pull every row asserting the verb.
For each row, record: source and target (by slug, never label alone),
both definitions, the raw verb string, the evidence tier, and the
pipeline's proposed disposition. The reviewer reads the definitions, not
the pipeline's recommendation.

**Phase 3 — Verdict each row.** For each row: identity first (record the
match type — stable ID or label only — and the rule 4/5 route; label-only
rows need an affirmative citation, a strict two-way pair, or a recorded
architecture decision; exception: for `core:precedes` siblings, structural
nearness alone suffices per Rule 5), then direction (is the arrow pointing the right
way?), then the definition test (does the source-target pair satisfy the
locked definition on the evidence in their definitions?), then the
verdict: APPROVE, HOLD, or STAND.
- **APPROVE** means the row satisfies the definition and the fact is
  stored (or its basis is updated if already emitting).
- **HOLD** means the row fails the definition or the evidence is
  insufficient. The fact is not emitted. The row is routed for source
  correction. A hold is never a remap: if the row seems better expressed
  as a different predicate, that is a source-meaning question, not an
  emission-time decision.
- **STAND** means the row was already correctly emitting and the review
  confirms it. Approving an already-emitting row changes only its basis;
  counts move only when a row changes bucket.

**Phase 4 — Sample and reconcile.** For large batches, sample per the
evidence discipline (Rule 6): draw samples only from promotions, record
outcomes as pending until Hamid reviews them. One wrong sample stops the
pass. Reconcile counts: every row has a verdict, every verdict is
recorded, the ledger balances.

**Exclusion citations (all verbs).** Exclusion, boundary, "owned by", and
"may be handled by" wording is never a route — for any verb. This is the
REL-00009 precedent, applied across all predicates. A citation that only
states where a boundary lies, who owns something, or what is excluded
does not establish the relationship the verb asserts.

**Approved-decision evidence.** Row-level verdicts are not
approved-decision evidence. Only recorded architecture decisions count —
for example, PR #110 and PR #119. A verdict recorded in a review batch
documents the reviewer's judgment; it does not constitute an architecture
decision.

**Per-verb guidance.** Each entry: the locked definition, what counts as
evidence, the common pitfall the definition guards against, and why the
boundary is drawn where it is.

- **`core:enabledBy` (source is enabled by target).** *The target supplies a
  maintained operating base, required control, governed mechanism,
  capability, resource, or prerequisite condition that makes the source
  able to operate.* Stored: `enables (S, T)` → `T core:enabledBy S` —
  the triple reads with the enabled thing as subject, the enabler as
  object, the same stored-direction convention as `informedBy`,
  `assuredBy`, and `triggeredBy`. Evidence: the target definition names
  the capability or control the source depends on. Pitfall: confusing
  enablement with sequence (the source happens after the target), with
  information flow (the target informs the source), or with hierarchy
  (the target is the parent). The test is capability: would the source
  be unable to operate without what the target supplies? If the answer
  is "it would just be less informed" or "it would happen later," that
  is not enablement.
  - **Disposition split (enables only).** Not every enables row becomes
    an `enabledBy` triple. G1a: merge as duplicate evidence on the
    existing `dependsOnOutputOf` fact — no new `enabledBy` triple.
    G1b: HOLD, no verb change. G2: no triple. Only G3 emits
    `core:enabledBy`.

- **`core:informedBy` (source is informed by target).** *The target
  provides context, planning input, or situational awareness the source
  uses. Information flows from target to source.* Evidence: the source
  definition names the information or the target as an input. Pitfall:
  promoting every data flow to informedBy. The definition requires that
  the information actually shapes the source's behavior, not merely that
  data moves between them. **Hold label:** "counterpart, opposite flow"
  — when the citation shows information flowing from source to target,
  the direction is reversed; hold, do not flip at emission time.

- **`core:dependsOnOutputOf` (source consumes target's output).**
  *The source consumes a specific, identifiable output the target
  produces.* Evidence: the source definition names the output or the
  target as its producer. Pitfall: confusing consumption with
  enablement. If the source needs the target's output to function, that
  is a dependency; if the source needs the target's capability to exist,
  that is enablement. The distinction matters because the remediation
  differs: a broken output is a data problem, a missing capability is an
  operating-model problem.

- **`core:requires` (source requires target).** *The source cannot
  validly start, complete, proceed, or reach its controlled state
  without the target, its completed control, or its required condition.*
  Evidence: the source definition states the prerequisite as a gate —
  "once required approvals are complete," "validating X before Y."
  Pitfall: inferring a requirement because the target later consumes or
  calculates related information. A downstream consumer does not create
  an upstream requirement. The requirement must be stated as a
  precondition in the source, not inferred from the target's behavior.

- **`core:assuredBy` (source is assured by target).** *The target
  performs defined governance, compliance, quality, review,
  control-testing, or equivalent oversight over the source or its
  outcome.* Evidence: the target definition describes the oversight
  activity and names the source (or its domain) as the assured thing.
  Pitfall: promoting support, documentation, or evidence-supply to
  assurance. A process that produces the workpapers is not assuring the
  process that uses them. Assurance requires an explicit oversight role,
  not merely involvement in the control environment.

- **`core:constrainedBy` (source is constrained by target).**
  *The target is a binding constraint source for the bounded activity,
  decision, or outcome.* Stored from the constrained thing to the
  constraint. Evidence: the source definition names the constraint or
  the target as imposing it. Pitfall: confusing constraints with advice,
  ownership, sequencing, or broad association. A target that the source
  "considers" or "coordinates with" is not a constraint. The constraint
  must bind: the source cannot validly exceed, ignore, or waive it.

- **`core:governedBy` (source is governed by target).** *The target
  exercises governance authority over the source — policy-setting,
  approval rights, or compliance enforcement.* Evidence: the target
  definition states the governance relationship. Pitfall: structural
  closeness. A process is not governed by its parent merely because the
  parent exists in the hierarchy. Governance requires an explicit
  authority relationship, not a position on the org chart. **Hierarchy
  exception (approved text, verb-predicate-mapping-v2.md §5):** Permitted
  only if all six hold: (1) documented relationship beyond containment;
  (2) the definition identifies distinct governance, control,
  decision-right, output-consumption, or externally reusable enablement
  semantics; (3) the rationale identifies that independent semantic
  evidence rather than the hierarchy path; (4) the evidence ledger
  preserves the hierarchy path and the exception rationale; (5) a
  reviewer approves the row explicitly — no automatic promotion; (6) the
  target is identified by source-backed evidence under the identity rule
  as finally scoped. Each exception is recorded as "not a precedent"
  for automatic emission.

- **`core:triggeredBy` (source is triggered by target).** *The target
  generates, detects, manages, or records the event, exception,
  monitoring outcome, change, referral, or handoff that initiates the
  source.* Evidence: the source definition names the triggering
  condition and the target as its origin, and the citation must tie the
  source's event to the target — the target is where the event comes
  from, not merely a process the source interacts with. Pitfall:
  "feeds," "informs," "supports," "uses," or "precedes" do not become
  triggers without an invoking event. A trigger is a discrete initiating
  condition, not a standing relationship.

- **`core:precedes` (source precedes target).** *The source completes
  before the target begins, as a sequence the business asserts.*
  Evidence (Rule 5): for siblings, structural nearness alone is
  sufficient — sibling sequence-pattern relations do not need an
  additional citation; for non-siblings, an affirmative sequence link
  in the source definition ("arrives from," "routes to," "executes
  through," "comes from," an explicit handoff) or a strict two-way
  mention. The citation must be an affirmative sequence assertion, not
  merely a mention of both processes. Pitfall: exclusion, boundary, or
  owned-by wording is not a sequence route. "Excludes X" tells you where
  the boundary is, not what happens first. A non-sibling row with only
  boundary wording is held.

**Why one verb per pass.** Verdicts require the reviewer to hold one
definition in mind and apply it uniformly. Mixing verbs in a batch
invites definition drift: the reviewer starts judging "requires" rows by
"enables" instincts. The cost of separate passes is linear; the cost of
a corrupted predicate is unbounded, because every downstream consumer
inherits the misclassification.

**Why holds are not remaps.** When a row fails its verb's definition but
seems to satisfy another's, the temptation is to reclassify at emission
time. This launders an authoring decision into the pipeline. The source
author chose the verb; if the verb is wrong, the correction belongs in
the source, reviewed as an authoring change. The pipeline emits, holds,
or defers — it never authors.

