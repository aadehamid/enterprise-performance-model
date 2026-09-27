# DO NOT MERGE — awaiting Hamid's review

## What this PR does

Records the Q10 terminology-note migration decision in the playbook.

## Change inventory

`business_architecture/ontology/ontology-playbook.md` only — one new
decision-log entry (Modeling), Q10:

- **Selective-alias policy.** A prior name becomes `skos:altLabel`
  only when unique, non-misleading, non-colliding, and useful for
  retrieval. Generic, ambiguous, authority-overstating,
  case/punctuation-only, or scope-limited former names are preserved
  via `core:priorPreferredLabel` (annotation property) but not
  searchable. Scoped aliases keep their context in the migration map,
  never flattened into `skos:altLabel`.
- **Rationale placement.** One-line rename rationale →
  `skos:editorialNote`; migration event/source → `dcterms:provenance`;
  full reviewer reasoning stays in the decision log / naming queue by
  reference.
- **Conservation rule (extends Q2, gates cutover).** Every non-null
  `prior_name` gets exactly one recorded disposition; every
  `name_change_note` maps to rationale + provenance; every
  `scoped_historical_alias` has a context or is explicitly rejected.
- **Minimal vocabulary.** Only `core:priorPreferredLabel` is added in
  Step 4; a reified historical-label record is deferred.
- The 92-row historical-label disposition report is named as the
  tracked pre-cutover instrument.

## Deliberately unchanged

- Everything else on main.

## How to review

Check the disposition rules against a few Step 3d renames you remember
(e.g. a generic old name vs. a genuinely useful former name) and confirm
the conservation rule reads as a fair merge gate.
