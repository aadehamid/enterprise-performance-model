# DO NOT MERGE — awaiting Hamid's review

## What this PR does

Records the Q9 lifecycle-model decision in the playbook — **revised**
2026-09-22 to three independent status dimensions. The original
single-chain proposal (Candidate → Approved → Deprecated → Retired) is
withdrawn: it conflated concept lifecycle with approval status.

## Change inventory

`business_architecture/ontology/ontology-playbook.md` only — one
decision-log entry (Modeling), Q9:

- **Concept lifecycle** (`core:lifecycleStatus` → SKOS scheme): Active,
  Deprecated, Retired. No OWL conflict: Deprecated ⇒
  `owl:deprecated true` (required); Retired ⇒ `owl:deprecated true`;
  Active ⇒ absent/false (SHACL-enforced in Step 9). "Superseded" is not
  a state — it is Deprecated + `dcterms:isReplacedBy`. Retired is
  terminal for active use; restoration needs a new governance decision
  with recorded provenance.
- **Governance approval status** (`core:governanceStatus` → SKOS
  scheme): the existing artifact-control vocabulary, formalized —
  Exploratory, Draft, Candidate, ApprovedBaseline, Implemented.
- **Hold status** (`core:holdStatus` → SKOS scheme): independent flag —
  NoHold, EvidenceHold, OwnershipHold, DecisionHold,
  ImplementationHold — plus `core:holdReason` and decision-log evidence
  links. Live cases named (PTC-001-B ownership hold, CM-1-1-3-5-3
  evidence hold).
- Worked examples: the R1 L2 (Active / Implemented / NoHold) and the
  CM-1-1-4-6 tombstone (Retired, `owl:deprecated true` / Implemented /
  NoHold).

## Deliberately unchanged

- Everything else on main (the consolidated #116 is merged).

## How to review

Check the three dimensions cover your cases and that the withdrawn
single chain is fully gone from the entry.
