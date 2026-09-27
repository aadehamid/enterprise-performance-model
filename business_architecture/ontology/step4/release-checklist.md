# Step 4 Release Checklist

**ID:** REL-CHECK-001
**Version:** 0.4 (Draft)
**Owner:** Hamid (accountable)
**Preparer:** Kailey (assistant)
**Reviewer:** Hamid
**Status:** Draft
**Created:** 2026-09-27
**Updated:** 2026-09-27 (v0.4: PR #159 merged, #160 evidence-only, #158/#124 details)
**Sources:** Playbook Step 4 "Done when", Evidence Discipline Rule 10, Step 4 README, Hamid's 2026-09-27 feedback
**Review trigger:** Any change to a governed count, gate result, or precondition status

---

## Preconditions

### Row verdicts and ledger

| # | Precondition | Status | Notes |
|---|---|---|---|
| 1 | Every relationship row has a recorded verdict | **Open** | Requires: 1 approve / 5 hold (evidence-only, PR #160). Assures: 5 approve / 3 hold. Constrained-by: 10 approve / 1 hold. Precedes/follows Rule 6 recorded. |
| 2 | Conservation ledger reconciles | **Arithmetic only** | Projected: 611 + 692 + 12 + 1 + 2 = 1,318; facts 453. Not yet confirmed across ledger, decision log, mapping doc, backlog. |

### Evidence and gates (run in order)

| # | Precondition | Status | Notes |
|---|---|---|---|
| 3 | Review #157 playbook methodology | **Approved — PR #159 merged** | Merged as 7b85121. Hierarchy-exception text from §5 verbatim; 4 other changes intact. |
| 4 | Re-pin evidence to current main SHA | **Blocked on PR #160** | Main is at 813fc88. #158 changed only ledger-v2.md (+43 lines, docs only, no count changes). |
| 5 | Evidence gate green on re-pinned SHA | **Blocked on 4** | |
| 6 | All hard gates green on re-pinned SHA | **Blocked on 4** | See Hard Gates below. |
| 7 | Regression tests pass on re-pinned SHA | **Blocked on 4** | SPARQL regression suite. |
| 8 | Blast-radius proof produced | **Blocked on 4-7** | See definition below. |

### Hard gates (each listed separately with current result)

| Gate | Current result |
|---|---|
| Conservation | 615 + 688 + 12 + 1 + 2 = 1,318 ✓ (arithmetic; 612/691/454 if requires holds stand) |
| No reciprocal `core:precedes` pairs | Pending re-run (182 facts) |
| Hierarchy non-duplication | Pending re-run (7 recorded exceptions) |
| Conditional G1b reverse-fact check | Pending re-run |
| Nearness-only identity (G3-B1) | Pending re-run |
| Held rows produce no triple | Pending re-run |

### Completeness

| # | Precondition | Status | Notes |
|---|---|---|---|
| 9 | Rule 6 verdicts recorded for every pass | **Partial** | Precedes/follows: 18/18 PASS. Constrained-by: 3/3 PASS (REL-00015, 00018, 00091). Requires: 1/1 PASS (REL-00873). Assures: samples drawn, not yet reviewed. |
| 10 | Supersession register complete and matches decision log | **Open** | 10 governed-by, 11 triggers, 20 precedes/follows, plus requires holds (REL-00158, 00168, 00247, 00872) in standard format. |
| 11 | 15 non-held rows have approved disposition | **Open** | 12 deferred, 1 ExternalGovernanceReference, 2 StructuredFlowValue. Each needs a recorded decision to exclude from this release. |
| 12 | Traceability of census file | **Open** | Regenerated strict-test version (383 yes / 274 no) pinned; old version marked superseded. |
| 13 | Backlog boundary decision recorded | **Open** | Source-workbook backlog doesn't block promotion. Covers 15 G1b both-held pairs, contradiction pair C, REL-00215, REL-00190, 20 precedes/follows holds. |

### Known defects

| Defect | Status |
|---|---|
| CM-1-1-4 definition | **Open** — definition ("Review data objects included in Refinery Premise") doesn't match label "Refinery Planning and Optimization". Restore definition from source workbook. |
| Merged "DO NOT MERGE" PR #124 | **Resolved** — intentional working-area drop. **SHA proof:** pre-#124 canonical-facts.csv = e50d1b6f...; #124 version = 7b21bd24...; current main (813fc88) = fc5d2db7... which matches 157bd9e (PR #147). #124's working copy was overwritten by the legitimate PR sequence. Counts unchanged. `no-consumer-attestation.md` from #124 is **stale/superseded** — do not mistake for the fresh attestation needed for item 15. |
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

1. **Hamid:** review PR #159 (methodology) and PR #160 (verb packages).
2. **Assistant:** fix CM-1-1-4 from source workbook; draw Rule 6 samples (done, pending review).
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
| 2026-09-27 | v0.2: Added supersession register, 15 non-held dispositions. |
| 2026-09-27 | v0.3: Fixed duplicate numbering (14/15, 10/14, 11/15 merged). Owner: Hamid (accountable), preparer: Kailey. Statuses updated. CM-1-1-4 defect specified. #124 files listed. |
| 2026-09-27 | v0.4: PR #159 merged (7b85121). #160 evidence-only with projected 611/692/453. #158 changed ledger only. #124 SHA proof; attestation marked stale. Rule 6: constrained-by 3/3 PASS, requires 1/1 PASS. |
