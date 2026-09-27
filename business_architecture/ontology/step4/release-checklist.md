# Step 4 Release Checklist

**ID:** REL-CHECK-001
**Version:** 0.2 (Draft)
**Owner:** Kailey (assistant)
**Reviewer:** Hamid
**Status:** Draft
**Created:** 2026-09-27
**Updated:** 2026-09-27 (v0.2: added hard gates detail, supersession register, 15 non-held dispositions, known defects, backlog boundary decision)
**Sources:** Playbook Step 4 "Done when", Evidence Discipline Rule 10, Step 4 README, Hamid's 2026-09-27 feedback
**Review trigger:** Any change to a governed count, gate result, or precondition status

---

## Preconditions

### Row verdicts and ledger

| # | Precondition | Status | Notes |
|---|---|---|---|
| 1 | Every relationship row has a recorded verdict | **Open** | Requires, assures, constrained-by packages on main but not yet reviewed by Hamid. Precedes/follows Rule 6 pass proposed but verdicts not recorded. |
| 2 | Conservation ledger reconciles | **Arithmetic only** | 615 + 688 + 12 + 1 + 2 = 1,318 adds up. Not yet confirmed that ledger, decision log, mapping doc, and backlog all agree on 615/688/457, 137/157, 256, 182. |

### Evidence and gates (run in order)

| # | Precondition | Status | Notes |
|---|---|---|---|
| 3 | Review #157 playbook methodology | **Pending Hamid** | c8e13cc added verb review methodology. If it changes any rule, earlier passes may need re-checking before re-pin. |
| 4 | Re-pin evidence to current main SHA | **Blocked on 3** | Current pins reference 1428e8e; main is at c8e13cc. |
| 5 | Evidence gate green on re-pinned SHA | **Blocked on 4** | A gate run against 1428e8e doesn't count after re-pin to c8e13cc. |
| 6 | All hard gates green on re-pinned SHA | **Blocked on 4** | See Hard Gates below. |
| 7 | Regression tests pass on re-pinned SHA | **Blocked on 4** | SPARQL regression suite. |
| 8 | Blast-radius proof produced | **Blocked on 4-7** | See definition below. |

### Hard gates (each listed separately with current result)

| Gate | Current result |
|---|---|
| Conservation | 615 + 688 + 12 + 1 + 2 = 1,318 ✓ (arithmetic) |
| No reciprocal `core:precedes` pairs | Pending re-run (182 facts) |
| Hierarchy non-duplication | Pending re-run (7 recorded exceptions) |
| Conditional G1b reverse-fact check | Pending re-run |
| Nearness-only identity (G3-B1) | Pending re-run |
| Held rows produce no triple | Pending re-run |

### Completeness

| # | Precondition | Status | Notes |
|---|---|---|---|
| 9 | Rule 6 verdicts recorded for every pass | **Open** | Precedes/follows pending. |
| 10 | Supersession register complete and matches decision log | **Open** | 10 governed-by, 11 triggers, 20 precedes/follows, plus earlier ones. |
| 11 | 15 non-held rows have approved disposition | **Open** | 12 deferred, 1 ExternalGovernanceReference, 2 StructuredFlowValue. Each needs a recorded decision to exclude from this release. |
| 12 | Traceability of census file | **Open** | Regenerated strict-test version (383 yes / 274 no) pinned; old version marked superseded. |
| 13 | Backlog boundary decision recorded | **Open** | Source-workbook backlog doesn't block promotion. Covers 15 G1b both-held pairs, contradiction pair C, REL-00215, REL-00190, 20 precedes/follows holds. |
| 14 | Supersession register reconciled with decision log | **Open** | Must match: 10 governed-by, 11 triggers, 20 precedes/follows, plus earlier ones. |
| 15 | Dispositions for 15 non-held rows recorded | **Open** | 12 deferred, 1 ExternalGovernanceReference, 2 StructuredFlowValue. Each needs a recorded decision to exclude from this release. |

### Known defects

| Defect | Status |
|---|---|
| CM-1-1-4 definition ("Refinery Premise") | Open — needs Hamid to specify the defect |
| Merged "DO NOT MERGE" PR #124 | Resolved — intentional working-area drop, ledger amended |
| Duplicated commit messages (6 commits) | Documented in ledger; traceability note recorded |

### Hamid-owned

| # | Precondition | Status | Notes |
|---|---|---|---|
| 14 | Mapping document approved section by section | **Open — large item** | Header says "No emission script may use this mapping until Hamid approves it row by row." This is a real review, not a sign-off. |
| 15 | Fresh no-consumer attestation | **Open** | See definition below. |
| 16 | Explicit promotion approval | **Open** | Separate from attestation and mapping approval. |

---

## Definitions (to be agreed before work)

### No-consumer attestation (item 15)

**Consumers covered:** Power BI semantic models, the KPI Store pilot, AI/automation consumers.

**"Fresh" means:** dated after the re-pin (item 4), so it attests to the exact SHA being promoted.

### Blast-radius proof (item 8)

Must show:
- Facts added, removed, or changed compared with the last promoted baseline, by predicate.
- Every downstream artifact that reads `canonical-facts.csv`.

---

## Execution order

1. **Hamid:** review #157 and the three verb packages.
2. **Assistant:** fix CM-1-1-4, record precedes/follows Rule 6 verdicts. (#124 and commit messages already addressed.)
3. **Assistant:** re-pin to the resulting main SHA.
4. **Assistant:** run evidence gate, all hard gates, regression tests on that SHA.
5. **Assistant:** produce blast-radius proof.
6. **Hamid:** approve mapping doc section by section.
7. **Hamid:** no-consumer attestation, then explicit promotion approval.

---

## Status log

| Date | Change |
|---|---|
| 2026-09-27 | Created as Draft from Hamid's feedback. Items 1-2 corrected from premature ✅. |
| 2026-09-27 | v0.2: Added supersession register (item 14), 15 non-held dispositions (item 15). Clarified CM-1-1-4 needs Hamid to specify defect. |
