# Approved target resolutions — rule 5 "approved decision evidence"

Extracted 2026-09-26 from the `main` branch of
`aadehamid/enterprise-performance-model` (read-only, via GitHub API).
These are the identity resolutions recorded as approved decision evidence
that Step 4 relationship rows may be matched against under playbook Rule 5
(same-branch nearness + approved decision evidence).

## PR #110 — stale pre-R1 relationship labels

- Title: "DO NOT MERGE — fix 16 stale pre-R1 relationship labels"
- Merged: 2026-09-22T22:39:55Z
- Merge commit SHA: `c801d982f5ec6b545cf1e3101a72489b15ea5abe`

**Important scope note:** PR #110 corrected **16 workbook cells** (16
`intake:relatedConcepts` TTL literals, 18 target segments), but they
resolve through only **2 distinct label→slug resolutions** — not 16
distinct labels. Each retired bare label is the recorded `prior_name` of
exactly one concept in `step2-identity-map.json` (verified on main).

| Retired label (as it appeared in target position) | Resolved concept slug | Current executed label |
|---|---|---|
| Refinery Planning | CM-1-1-4 | Refinery Planning and Optimization |
| Refinery Scheduling | CM-1-1-7 | Refinery Production Planning and Scheduling |

A relationship row whose target is the retired bare label
"Refinery Planning" or "Refinery Scheduling" resolves to CM-1-1-4 /
CM-1-1-7 respectively, citing PR #110 as the route.

The 16 source rows whose cells were corrected (for cross-reference):
CM-1-1-2-10, CM-1-1-2-12, CM-1-1-2-13, CM-1-1-3-7-1, CM-1-1-3-7-2,
CM-1-1-4-7, CM-1-1-4-7-7, CM-1-1-4-7-8, CM-1-1-7-2, CM-1-1-7-2-6,
CM-1-2-1-1, CM-1-2-1-1-1, CM-1-2-5-1-2, CM-1-2-5-2, CM-1-2-5-2-2,
CM-1-2-5-2-3.

(The PR also added a permanent `no stale pre-R1 relationship targets`
gate lock in `r1-gate-check.py`; the two retired labels may not reappear
as machine-consumed relationship targets.)

## PR #119 — Q11 relationship target dispositions

- Title: "DO NOT MERGE — record Q11 relationship target dispositions"
- Merged: 2026-09-23T01:53:00Z
- Merge commit SHA: `601dbfdadb92352349f150384800452f3a505a74`

Exactly **6** `ResolvedToConcept` resolutions, confirmed — no more, no
fewer. (The same six are restated in the playbook's Q11 decision-log
entry on main.)

| Target label (as approved; qualifier matters) | Resolved slug | Notes |
|---|---|---|
| Establish & Maintain Delegation Of Authority (DOA) | CM-1-2-2-3-2 | Bare "DOA" in the task = this qualified label |
| Integrated Marketing Planning (Advertising) | CM-1-3-5-2 | All four mentions are the qualified label |
| Serve to Customer (Non-Retail) | CM-1-3-6-2-6 | The only mention is the qualified label |
| Develop/Update Strategy (CVP) | CM-1-3-2-2-4 | CVP-context mention; bare mentions stay unmatched per the no-global-lexical-replacement rule |
| Manage Trading Books & Strategies Structure | CM-1-2-2-3-1 | Resolves via "Establish And Maintain Book Structure" (batch 12 split) |
| Network Design (Retail) | CM-1-3-3-4 | Qualified mentions only — the single bare `informed-by: Network Design` mention (Brand Imaging row) is genuinely unmatched → AmbiguousDeferred, do not guess |

Matching principle recorded with these: **labels aren't identity** —
parenthetical qualifiers (`(DOA)`, `(Advertising)`, `(Non-Retail)`,
`(CVP)`, `(Retail)`) are part of the label that resolves the mention.
Match rows against the qualified forms above, not the bare phrases.

## Other decision-log identity resolutions on main

**None exist.** Checked on `main`:

- The playbook's Step 4 design locks Q1–Q12 contain no other
  label→slug target resolutions. Q11 (above) is the only target-resolution
  entry. Q10 (terminology-note migration) governs label/alias migration
  for concept names, not relationship target resolution.
- `business_architecture/ontology/step4/step4-decisions.md` exists on
  `main` (PR #124 merged the step4 directory; corrected 2026-09-26).
- A scan of recently merged PRs with target/resolution/label themes
  found only #110, #119, and #120 (Q12 ambiguous-target rule — records
  no resolutions, only the AmbiguousDeferred mechanism).

## Approved R1 interface (excluded, for the record)

Seen and excluded per instructions: the one reviewed pending interface
`CM-1-1-2-9-1` → "informs: Refinery Planning and Optimization (CM-1-1-4)",
stored as `CM-1-1-4 core:informedBy CM-1-1-2-9-1`. It is an **informs**
relation, so it does not count as approved decision evidence for
`dependsOnOutputOf` (uses-input) rows. Recorded in the branch's
`step4-design-proposal.md` and `verb-predicate-mapping-v2.md` (PR #124,
not on main).
