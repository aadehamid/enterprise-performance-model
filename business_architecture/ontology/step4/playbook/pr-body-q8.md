# DO NOT MERGE — awaiting Hamid's review

## What this PR does

Records the Q8 decision and completes the parked business-architecture
hierarchy item with KPI and data products, per the project documentation.

## Change inventory

`business_architecture/ontology/ontology-playbook.md` only:

1. **Decision log (Modeling) — Q8 controlled `conceptKind` scheme
   (2026-09-22).** `core:conceptKind` as an object property to a SKOS
   scheme (Process / Capability / StructuralAnchor), not a string; why
   kinds matter to consumers; the deliberate boundary that CM-1-3-1-6's
   classification stays parked; composition with the Appendix A parked
   layer.
2. **Appendix A — parked layer item now covers the complete hierarchy:**
   domain > value stream > stages, value stream > capability > business
   process > activity, events, decisions, **KPIs**, and **data
   products**. Documents where each layer lives: overlays (parked),
   Q8 CapabilityKind (Step 4), `core` 1.0.0 (Step 4), below-L6
   activities (future), PROV-O events (Step 6), decisions (future
   decision modeling), `kpi` module (KPI Store on Databricks is the
   delivery side), data-product portfolio JSON with sparse
   produces/consumes links.

## Deliberately unchanged

- Everything else, including the other open playbook PRs (#111, #112,
  #113, #114) — those merge independently.

## How to review

Check the Q8 entry matches the agreement (especially the CM-1-3-1-6
boundary), and that the hierarchy table in Appendix A places every
layer where you expect it.
