# DO NOT MERGE — Step 4 evidence-discipline playbook section (proposed 2026-09-24)

Docs-only PR. **Do not merge without Hamid's explicit approval.**
Base: `main` at `6ab2197ba3fe6246bdb501391d22b71d0338d2c7` (verified current
before push; no other files touched).

## What this PR contains

One new playbook section, **Step 4 evidence discipline — promoting intake
data without corrupting it**, placed after the step log and before §4
Decision log (the approved placement), plus a short Step 4 step-log pointer
entry. The section is marked PROPOSED 2026-09-24 and becomes canonical
operating discipline only on Hamid's approval.

The eleven rules (Hamid's six wording edits applied):

1. Pin all evidence to one approved `main` SHA.
2. Regenerate old review packages after the taxonomy evolves.
3. Carry approvals only for field-equivalent rows — **with the new
   evidence-strengthening exception** (stable identifier/source citation
   added; source, verb, target, disposition unchanged; exception recorded
   explicitly).
4. Labels are candidate filters, never identity evidence (PR #120).
5. **Structural nearness alone suffices only for sibling sequence-pattern
   relations**; for enables/governed-by/requires/assures/dependency it must
   combine with independent definition, scope, reciprocal, or approved
   decision evidence.
6. Sample every automatic-promotion batch per domain; stop at first wrong
   resolution.
7. **No source record leaves without a recorded disposition**
   (DroppedAsNonProcessProse is a governed disposition, not loss; counts live
   in the ledger, not the rule).
8. One canonical direction per fact; **mutual pairs that contradict under a
   property disallowing them are held, not emitted**.
9. Raw verb/source-row evidence stays out of RDF reification for 1.0.0.
10. Release gate: same-SHA evidence plus a fresh no-consumer attestation.
11. **NEW — Emission never changes source meaning.** Promotion may emit,
    hold, defer, or reclassify; it may not replace a verb, invent a target,
    or reinterpret business meaning. Corrections go through reviewed
    workbook authoring.

Also: the "why" section no longer states an unproven percentage — it points
to the conservation ledger's exact mention-to-canonical-fact reconciliation.

## Deliberately unchanged

- No ontology TTL, JSON, or build script touched.
- No `intake:` predicate retired; no relationship RDF emitted.
- No promotion-script implementation.
- No changes to any existing decision-log entry or step-log entry.
- Review evidence CSVs (53/14/11-row batches, nearness sample, enabledBy
  mutual batch) are **not** in this PR — they live with the evidence
  package pending Hamid's review-batch decisions.

## Evidence and review instructions

- The section text was built from the reviewer-evolved working-tree draft;
  the six edits above are Hamid's 2026-09-24 wording, applied verbatim.
- Verify placement: new `### Step 4` pointer at the end of §3 step log; full
  section between the step log's closing `---` and `## 4. Decision log`.
- Verify the status blockquote still reads PROPOSED (not canonical).
- The substantive review batches this discipline governs are tracked in the
  Step 4 evidence package (`~/workspace/ontology-step4/review-evidence/`);
  their decisions must complete before promotion-script implementation
  begins.

## Blast radius

Docs only: one Markdown file changed
(`business_architecture/ontology/ontology-playbook.md`). No build, consumer,
or data impact. Safe to leave open unmerged indefinitely.
