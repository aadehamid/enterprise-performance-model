# DRAFT — Playbook addition: Step 4 evidence discipline

> Status: PROPOSED 2026-09-24. Not yet in the playbook. Hamid to review wording
> before it is added. Intended placement: new section after the step log
> (before §4 Decision log), plus a short Step 4 step-log entry pointing to it.
> Based on the repo working-tree copy (reviewer-evolved).

---

## Step 4 evidence discipline — promoting intake data without corrupting it

Step 4 promotes the provisional `intake:` annotations to real ontology
properties. The intake layer is the only copy of facts like "which process uses
which input" and "which process the workbook says this one follows." If the
promotion is sloppy, those facts are corrupted silently — the triples look
fine, but they no longer say what the business said. The eleven rules below are
how we keep that from happening. They were developed promoting 5,571 intake
triples and 1,318 relationship mentions, and several of them exist because an
earlier, weaker version of the check failed and we fixed the premise instead
of patching the row.

### The eleven rules

1. **Pin all evidence to one approved `main` SHA.** Every evidence file
   (dispositions, reviews, ledgers) carries `baseline_sha`, and the byte
   hashes of the baseline inputs are recorded. Before the eventual release,
   re-pin to the then-current approved `main`; all build and evidence artifacts
   must cite the same SHA.

2. **Regenerate old review packages after the taxonomy evolves.** A review
   package built against last month's taxonomy is a review of last month's
   data. After any rename/reparent/reclassification, regenerate the package
   from the pinned baseline and diff it field-by-field against the old one —
   do not merely re-validate the old CSV.

3. **Carry approvals only for field-equivalent rows, except where an
   evidence-strengthening change adds a stable identifier or source citation
   while the source, verb, resolved target, and disposition remain unchanged.
   The exception must be recorded explicitly.** An approval granted
   against v1.1 carries to v2 only if the row is identical on every evidence
   field (same concept, same label key, same candidate) — or qualifies under
   the recorded strengthening exception. Anything else goes back for review —
   only the differences, not the whole package.

4. **Treat labels as candidate filters, never as identity evidence.**
   A matching label proposes a candidate; it never proves the target. Slugs
   and IRIs are identity. (PR #120.)

5. **Structural nearness alone is sufficient only for approved local
   sequence-pattern relations between sibling processes. For enables,
   governed-by, requires, assures, and dependency relations, it must be
   combined with independent definition, scope, reciprocal, or approved
   decision evidence.** A unique label match earns a candidacy, not a triple.
   Promotion needs at least one of: an explicit citation of the target in the
   source's definition or scope note; a consistent two-way mention (strict
   inverse pairs only); structural nearness inside the same decomposition
   branch (siblings for sequences; shared L2/L3 branch and no
   ancestor/descendant relation otherwise) *plus* one of the independent
   evidence types above for non-sequence relations. Label match alone = held
   for domain-batch review.

6. **Sample every batch of automatic promotions per domain, and stop at the
   first wrong resolution.** Sample `max(10, ceil(5%))` per domain (seeded, so
   it is reproducible). A human reads each sampled row's definitions and
   records OK or FLAG. One wrong resolution stops the line: tighten the rule
   and re-run — never patch the single row.

7. **Conserve every source predicate and every relationship mention through
   migration.** The Q2 ledger accounts for all 5,571 intake triples across 13
   predicates and all 1,318 relationship mentions: emitted, held, merged, or
   redirected. No source record leaves the migration without a recorded
   disposition. DroppedAsNonProcessProse is a governed disposition, not
   unaccounted loss. Conservation is proved by arithmetic, not asserted; the
   exact counts live in the ledger's evidence section, not in this rule.

8. **Store one canonical direction per fact; derive inverses, never store
   mirrors.** `A precedes B` and `B follows A` are one fact stored as
   `A core:precedes B`. Mirrored rows inflate the fact count and let
   contradictions hide. Pairs that contradict one another under a property
   that does not allow mutual relation are held, not emitted.

9. **Keep raw verb and source-row evidence outside RDF reification for 1.0.0.**
   The evidence (which workbook verb, which row, which test promoted it)
   lives in versioned CSVs beside the build, not as reified triples. Revisit
   after 1.0.0 if consumers need provenance in-graph.

10. **Release gate: same-SHA evidence plus a fresh no-consumer attestation.**
    The release build, the evidence package, and the consumer-impact scan must
    all cite one SHA. And immediately before flag-day, re-confirm the
    foundation-stage attestation (no consumers yet) — a stale attestation is
    not an attestation.

11. **Emission never changes source meaning.** Promotion may emit, hold, defer,
    or reclassify a source relationship; it may not replace a verb, invent
    a target, or reinterpret business meaning. Corrections are made in the
    workbook through a reviewed authoring change.

### Why each rule exists (the failures that taught them)

- **Stale baselines silently approve different data.** The v1.1→v2 comparison
  found 53 rows whose raw target labels changed under them (Step 3d renames),
  1 genuinely new relationship row (the approved R1 interface), and 35 rows
  whose evidence got *stronger* (slug parentheticals added to mentions). None
  of that is visible without the SHA pin and the field-by-field diff (rules
  1–3). Reviewing v2 rows against v1.1 approvals without the diff would have
  approved renames nobody re-read.
- **Labels drift and collide.** "Refinery Planning" became "Refinery Planning
  and Optimization"; "Determine Taxability" names two different concepts in
  two decompositions; the CVP strategy labels split four ways in Step 3d.
  Any pipeline that joins on labels inherits every one of those events as a
  silent misresolution (rule 4).
- **The first context pass was confidently wrong.** It promoted 915 rows on
  tests that did not test what they claimed: "explicit reference" read
  terminology notes instead of definitions, any backlink counted as two-way
  confirmation, and hierarchy proximity counted as relationship evidence.
  The corrected pass promotes 852 and holds 169 — including rows the old
  pass had blessed. The lesson was not "fix the 63 rows" but "the premise was
  untested": we wrote the failing checks first, watched them fail, then fixed
  the implementation (rule 5, and the attack-the-premise trigger below).
- **Zero `intake:` triples proves deletion, not migration.** A build that
  drops the intake namespace and shows no intake triples has proved the
  annotations are gone. Migration is proved only by the ledger: every triple
  and every mention accounted for, each with a recorded disposition (rule 7).
- **Mirrored rows inflate facts.** 386 mentions collapse into 193 facts once
  mirrors merge. Mirrored relationship mentions materially inflate the raw
  mention count; the conservation ledger reports the exact
  mention-to-canonical-fact reconciliation for each release (rule 8).
- **Release evidence from mixed commits is invalid.** A consumer-impact scan
  run against one SHA and a build cut from another is theater. One SHA for
  build, evidence, and scan — re-pinned at release time (rule 10).
- **Promotion logic must not author meaning.** A mistyped workbook verb
  ("assures" where the business meant "satisfies") cannot be repaired by the
  promotion script choosing a nicer predicate — that would launder an
  authoring error into the ontology. The script emits, holds, or defers; the
  correction goes through reviewed workbook authoring (rule 11).

### Standing triggers

- **Attack the premise:** two failed fixes on the same gate, or two "the
  checker never asserted that" moments on one class of check → stop writing
  fixes; census what the check does *not* cover and fix the premise.
- **Write the failing check first:** every regression fix starts with a gate
  assertion watched failing on the broken state, then the fix, then the pass.
- **Reviewer verdicts:** every evidence package gets the interrogate pass
  (Act On / Consider / Noted / Dismissed) before Hamid reviews it.
