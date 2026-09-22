# R1 Refining reclassification — gate evidence

Hamid-approved decision package: `r1-refining-proposal.md` (workspace;
Candidate decision recorded 2026-09-22). This file records the evidence for
the four PR gates defined in that package, with exact re-verification
instructions. All paths below are relative to the repository root.

## Gate 1 — hierarchy integrity

**Mechanically re-verified with the independent checker
`build/scripts/r1-gate-check.py` (all 29 checks PASS, exit 0) against the
committed regenerated outputs:**

- 683 concepts (682 + 1 new R&T L2), 14,495 triples (baseline 14,481; +14
  fully accounted for by the new L2's own triples — see §Delta below).
- 681 `skos:broader` links — every non-root concept has exactly one; the two
  L0 roots (`L0-downstream-operations`, `L0-enabling-functions`) are the only
  concepts without a broader. (Note: the task text's "683 broader links"
  assumed one root; the baseline has 682 concepts / 680 broader links, so the
  mechanical expectation is 681. The build script now derives this count
  instead of hardcoding it.)
- 0 dangling `skos:broader` targets; 0 orphan concepts.
- All 42 migrated rows have the correct new parent and new level; all other
  concepts' identities (slug, URI, `skos:notation`) are byte-stable.
- No identity-map changes outside the migration set (42 changed parents/levels
  + 1 added concept + governance overlays).
- Exactly 2 `skos:prefLabel` changes (the two promoted L2s); `skos:altLabel`
  count unchanged at 317; neither old promoted name is kept as an altLabel.
- Tombstone `CM-1-1-4-6` still `owl:deprecated`; still under `CM-1-1` (L3);
  `CM-1-1-4-6-1` still `intake:status "blocked"` (PTC-001-B hold intact).

**Re-verify:** run the committed regenerated TTL and identity map through
`python3 build/scripts/r1-gate-check.py`.

## Gate 2 — path compatibility

Hamid stated 2026-09-22 (recorded): **"Right now no consumer have been
consuming what we are building. We are building the foundation that
everything else will connect to later."** This is the superseding fact for
Gate 2: no hierarchy-dependent consumer exists yet, so no consumer can break.

- `build/r1/r1-path-compatibility-register.csv` — 42 data rows (one per
  migrated concept) plus header. Every row's disposition:
  **"No consumer — foundation stage, confirmed 2026-09-22 (Hamid)"**.
- `build/r1/r1-path-compatibility-register.md` — human-readable companion.
- `build/r1/r1-consumer-inventory-checklist.md` — the external-team inventory
  (Power BI / RLS-OLS / catalog / data products / saved queries). **This
  checklist reactivates before the first hierarchy-dependent consumer
  connects**; it is stored with the evidence so the dependency is visible.

**Re-verify:** open the CSV; confirm 42 data rows, one per migrated concept,
all with the "No consumer — foundation stage" disposition.

## Gate 3 — governance

- `r1_migration` overlay present on all 42 migrated identity-map rows:
  old→new parent, old→new level, historical breadcrumb, date 2026-09-22,
  Candidate-package reference.
- Historical breadcrumbs retained (all begin
  "Downstream Operations > Commercial & Marketing"), so the old path is
  recoverable from the row itself.
- Two `prior_name` / `name_change_note` entries for the renamed L2s.
- Energy placement note on `CM-1-1-7-3` and its three children: temporary /
  inherited through the scheduling parent; R2 review trigger recorded.
- SemVer classification: this is a **minor** release under the locked version
  policy — additive (one new L2) plus reparenting (breaking for hierarchy
  consumers). No consumer exists (Gate 2), so the reparenting is safe; the
  §1g register records all 42 path changes for the day a consumer connects.
- Deliberately unchanged: PTC-001-B hold (still blocked under the tombstone);
  PTC-002-adjacent node `CM-1-1-4-6-3` (parent/level identical);
  Supply & Trading feedstock-quality cluster (16 `CM-1-2-5-*` nodes identical);
  `CM-1-1-2-9-1` structural placement (stays under Regional Optimization,
  `intake:relatedConcepts` interface only); all R2-deferred work
  (L3 decomposition, HR 7.x, EHS, 10.x asset maintenance, R2 energy scope
  decision).

**Re-verify:** `python3 build/scripts/r1-gate-check.py` covers the unchanged
checks; read any migrated row's `r1_migration` object in
`build/output/step2-identity-map.json`.

## Gate 4 — regeneration evidence

- Baseline proof: the baseline build scripts were run against git-HEAD inputs
  before any change and reproduced `step3-taxonomy.ttl` and
  `step3-taxonomy-report.md` byte-identically (682 concepts, 14,481 triples,
  679/682 definitions, 680 broader links, 502 workbook-approved rows).
- Regeneration, not hand edits: every changed output was produced by an
  asserted one-shot script committed at `build/scripts/r1-workbook-update.py`
  (workbook) and `build/scripts/r1-json-update.py` (source JSON; the
  deterministic JSON writer preserves the source file's formatting
  conventions — see its header). The workbook script refuses to run twice
  rather than double-applying.
- Overlay-restoration evidence: a raw Step 2 regen wipes the 96 pre-existing
  naming overlays; the one-shot script restores them from the committed
  baseline — restoration verified with **zero mismatches**; overlay counts
  after R1: 98 `prior_name`, 98 `name_change_note`, 92
  `scoped_historical_alias` (96 + 2 new for the renamed L2s).
- Structural diffs: `build/r1/r1-json-diff.md` (source JSON structural diff —
  review the substance, not formatting churn) and
  `build/r1/r1-cell-diff.md` (every changed workbook cell, grouped by concept,
  with the reason for each edit).
- Validator: `scripts/step3c-workbook-validate.py` — **0 blocking** on the
  updated workbook (522 rows: 503 approved, 17 pending, 1 blocked, 1 retired);
  the 4 questions and 18 notes are identical to baseline (all pre-existing).

**Re-verify:** run the workbook validator against
`build/output/step3c-definition-authoring-workbook.xlsx`; confirm exit 0.

## Delta accounting

| Measure | Baseline | R1 | Δ |
|---|---|---|---|
| Concepts | 682 | 683 | +1 (new R&T L2) |
| Triples | 14,481 | 14,495 | +14 (new L2's own triples; nothing else changed) |
| Definitions | 679/682 | 680/683 | +1 (new L2's approved definition) |
| Broader links | 680 | 681 | +1 (new L2's broader) |
| prefLabel changes | — | 2 | the two promoted L2s |
| altLabels | 317 | 317 | 0 |
| Workbook rows | 505 | 522 | +1 approved L2 +16 asserted pending |
| Identity-map overlays | 96/96/92 | 98/98/92 | +2 prior_name/name_change_note pairs |
