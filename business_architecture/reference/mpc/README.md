# Reference: Marathon Petroleum Corporation (MPC) — anchor company

**Status:** Draft · **Owner:** Hamid Adesokan · **Created:** 2026-09-29

Marathon Petroleum Corporation (MPC) stands in for "a Downstream Oil & Gas
company" so the ontology has a concrete, public, citable company to anchor
instances, KPIs and definitions against.

## How this material is used

- **Evidence, not authority.** The repo's own business architecture
  (`../../business_process/`, `../../schema/`) remains the process source of
  truth. MPC material ranks as external evidence. Where it suggests the
  process map is missing or misaligned, the suggestion is written up in
  `process-map-suggestions.md` for review — the process map is never edited
  from here directly.
- **Company-neutral vocabulary.** The `core:` / `kpi:` / `organization:`
  vocabularies stay generic. MPC, its segments, refineries and MPLX become
  *instances* (party / organization modules, Step 5 onward).
- **Every fact is cited.** Each fact in `mpc-fy2025-10k-fact-sheet.md` names
  its source (register ID + filing section). In Turtle, that becomes
  `dcterms:source` / `prov:wasDerivedFrom`.
- **Public information only.** Nothing here is non-public MPC information,
  and nothing here implies MPC uses or endorses this model. No MPC logos or
  branding are reproduced. Brand names (Marathon®, ARCO®) appear only as facts
  quoted from filings.
- **Figures age.** Re-verify against the latest filing before using a figure
  in a governed artifact. The baseline is the FY2025 Form 10-K.

## Contents

| File | What |
|---|---|
| `source-register.md` | Every MPC / MPLX source used, with accession number, URL and retrieval date |
| `mpc-fy2025-10k-fact-sheet.md` | Structured facts extracted from the FY2025 10-K (segments, sites, products, channels, KPI definitions) |
| `customer-classification-evidence.md` | Adopted MPC customer classification (C1–C7 + facets), each class cited to filings or MPC materials |
| `pricing-domain-evidence.md` | Evidence for Pricing as a candidate data domain (MPC filings + EIA definitions) |
| `process-map-suggestions.md` | Proposed updates to the process map suggested by MPC material (Proposed — not applied) |
