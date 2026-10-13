# core changelog

## 1.0.0 (unreleased; built as release candidate 1.0.0-rc.1)

Not yet released: it waits for Hamid's fresh no-consumer attestation, his approval of the conservation ledger and his approval of the release, which a major release needs. At the cut, the builder drops the `-rc.1` stage and sets the issue date, and this entry names the approver and the date.

The first release of the `core` module (EPM-DEC-001-0013, built as EPM-DEC-001-0029 proposes).

- The process taxonomy, with every `intake:` field migrated to its `core` target. No `intake:` triple remains; `conservation.csv` records where each one went.
- The canonical relationship facts as direct triples on nine predicates. Their provenance (source rows, raw verbs, notes) is in `canonical-facts.csv`.
- The scoped sequences (EPM-DEC-001-0026).
- Seven code lists: concept kind, APQC mapping decision, operating mode, cadence, planning level, and the three Q9 status lists.
- Cited sources and APQC elements are IRI resources; the release holds no blank nodes.
- The SHACL release slice (`release/shapes.ttl`) conforms.
