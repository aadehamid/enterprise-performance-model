# EPM-DEC-001-0029: How `core` 1.0.0 is built: intake: targets, provenance, IRIs and the release package

| Field | Value |
|---|---|
| Status | Proposed (Claude's delegated choice under EPM-DEC-001-0028, which is pending in #242; Hamid decides) |
| Date | 2026-10-13 |
| Questions | The open implementation questions of the `core` 1.0.0 release |
| Source | Claude Code session, 2026-10-13, under Hamid's delegation of 2026-10-12 ([#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6137222677)); EPM-DEC-001-0028 is pending in #242 |

## Context

EPM-DEC-001-0013 releases `core` 1.0.0 after Phase 1: the canonical facts at that time, zero `intake:` triples, and a fresh attestation. Step 4 decision Q2 retires all 5,571 `intake:` triples in one release (`step4/step4-decisions.md:52-62`). The approved decisions fix most targets (Q5 flows, Q6 horizon facets, Q7 responsible domain, Q8 concept kind, Q9 status dimensions, Q10 terminology notes). They leave implementation questions open, and the conservation ledger (`step4/ledger-v2.md`, still a draft) disagrees with the approved decisions in three places. Hamid delegated these questions: "Make decisions for me using available evidence to make the best decision and light external searcch to resolve ambiguity."

## Decision

**Precedence.** Where the draft ledger and an approved decision disagree, the approved decision wins: `core:taxonomyLevel` is kept as derived metadata (`step4-decisions.md:35-37`), not retired (ledger:35); Q8 and Q9 are approved (`step4-decisions.md:151`, `:219`), not pending (ledger:40, :47); cross-functional domains are normalized with the detail in a note (Q7, `step4-decisions.md:118-128`), not kept verbatim (ledger:102-104).

**Targets for each `intake:` predicate** (counts from the census, ledger:33-48):

| intake: predicate | Target in `core` 1.0.0 | Basis |
|---|---|---|
| `level` | `core:taxonomyLevel`, `xsd:integer` 0–6, derived from the L-level | `step4-decisions.md:35-37` |
| `apqcDecision` | `core:apqcMappingDecision` → code list `core:ApqcMappingDecision` (review-link, no-source, no-candidate, rejected, adopted) | ledger:106-108; one kind and range per property (EPM-DEC-001-0020) |
| `terminologyNotes` | the ledger's deterministic rule: migration events, and dual-aspect notes, → `dcterms:provenance`; authoring history and decision-record pointers → `skos:editorialNote`, pointer text kept | Q10 (`step4-decisions.md:236-257`); ledger:61-76 |
| former names | the approved label report (`label-report/label-dispositions-v1.2.csv`): `AddAsAltLabel` and `RetainAsAltLabel` → `skos:altLabel`; `MigrationOnly` and `RetireAsAmbiguous`, and scoped aliases, → `core:priorPreferredLabel` (annotation, not searchable) | Q10; label report v1.1 approved |
| `referenceSources` | one `dcterms:source` link per cited source ID to `src:<id in lower case>`, a `dcterms:BibliographicResource` carrying the registry's title, publisher and permitted use; the 9 annotation suffixes → `skos:editorialNote` on the concept, prefixed with the source ID | ledger:78-83 |
| `primaryPurpose` | `core:primaryPurpose`, `rdf:langString` | ledger:39 |
| `conceptTypeCheck` | `core:conceptKind` → code list `core:ConceptKind` (process, capability, structural-anchor); "not-process" marks the two L0 roots, which Q8 names as structural anchors | Q8 (`step4-decisions.md:151-161`) |
| `relatedConcepts` | removed. The canonical facts (`step4/canonical-facts.csv`) and the scoped sequences replace it. Held, deferred, external-governance and structured-flow mentions emit nothing and stay recorded in the Step 4 evidence | mapping v2 (approved 2026-09-29); EPM-DEC-001-0025, -0026 |
| `responsibleDomain` | `core:responsibleDomain`, `rdf:langString`; the 12 cross-functional values → "Cross-functional", the original text in `skos:note` | Q7 |
| `processHorizon` | `core:operatingMode`, `core:cadence`, `core:planningLevel`, each to its own code list; daily, weekly and monthly also set operating mode periodic; "periodic" alone sets no cadence | Q6; ledger:85-95 |
| `primaryOutput`, `keyInputs` | `core:primaryOutputFlow` and `core:keyInputFlow`, `rdf:langString`, one triple per flow name (inputs split on `\|`), whitespace normalized; no nodes | Q5 (`step4-decisions.md:93-103`) |
| `parkedChildren` | `core:plannedChildNote`, annotation, `rdf:langString` | ledger:46 |
| `intake:status` | "retired" (CM-1-1-4-6) → `core:lifecycleStatus` retired, with its existing `owl:deprecated true`; "blocked" (CM-1-1-4-6-1, parked by PTC-001 until its destination exists) → `core:holdStatus` implementation-hold, with its note as `core:holdReason`. All three Q9 code lists are defined in full | Q9 revision (`step4-decisions.md:219-234`) |

**Facts carry no reifiers.** Each canonical fact is one direct triple, `proc:S core:P proc:O`. Its provenance (row IDs, raw verbs, notes) ships beside the ontology as `canonical-facts.csv`, which satisfies "the raw verb is retained in migration/provenance evidence on every emitted triple" (`verb-predicate-mapping-v2.md`, direction table) without reification, which EPM-DEC-001-0020 rules out.

**No blank nodes.** The 500 APQC `dcterms:references` nodes become `src:apqc-pcf-7.2.2/element/<id>` resources with the same identifier, title and `dcterms:isPartOf`. The 503 workbook `dcterms:source` nodes, which all carry the same title, become one resource, `src:step3c-definition-workbook`. (Playbook: "No blank nodes in released data"; EPM-DEC-001-0020 rule 3.)

**The release package.** `business_architecture/ontology/release/build_core.py` builds `business_architecture/ontology/releases/core/1.0.0/` from the pinned Step 4 baseline: `core.ttl` (the ontology header, the core vocabulary, the code lists, the taxonomy with its migrated fields, the canonical facts and the scoped sequences), `canonical-facts.csv` (provenance), `conservation.csv` (the after half of the ledger: every census triple's destination), `manifest.json` (files and SHA-256 checksums, the source commit) and `CHANGELOG.md`. The header follows the playbook's worked example (`ontology-playbook.md:1309-1318`). Until Hamid approves the release, the package is built as release candidate `1.0.0-rc.1`, with no `dcterms:issued`; at the cut, `build_core.py` sets the release date as `dcterms:issued` and drops the candidate label. The SHACL release slice (EPM-DEC-001-0014) runs on `core.ttl` before the package is written.

**Approvals stay with Hamid.** This record proposes the release design under EPM-DEC-001-0028; it becomes Decided only with Hamid's recorded words. Three things wait for Hamid: the fresh no-consumer attestation, a fact about who uses the ontology (`step4/no-consumer-attestation.md:3`); the conservation ledger's approval (`step4/ledger-v2.md`), now backed by a reconciled before/after run; and the release itself, because a major release needs his approval ("Major (including any deprecation): Hamid. No exceptions", `step4/playbook/ontology-worklog.md`, "Who approves a release"). The release PR waits for all three.

## Hamid's recorded words

Hamid delegated these questions in the Claude Code session on 2026-10-12 ([#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6137222677), saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation.md`): "I want you to keep going until we finish the ontology. Make decisions for me using available evidence to make the best decision and light external searcch to resolve ambiguity." Each choice above is delegated under that instruction (EPM-DEC-001-0028, pending in #242); Hamid did not make these choices himself, and he can reverse any of them.

## Alternatives considered

- **Reify each fact to carry its provenance in RDF.** Rejected: EPM-DEC-001-0020 rules out reifiers, and released data may hold no blank nodes.
- **Follow the draft ledger where it disagrees with an approved decision.** Rejected: the ledger is marked draft; the decisions are approved.
- **One IRI per workbook provenance blank node.** Rejected: the 503 nodes are identical, and one shared resource states the same fact.

## Evidence

The approved decisions cited above; the census and measured splits in `step4/ledger-v2.md`; the approved label report (`step4/label-report/README.md`); the value counts measured on `build/output/step3-taxonomy.ttl` at the #201 build commit.

## Consequences

- New `core` terms: the predicates above, `core:priorPreferredLabel`, `core:holdReason`, and seven code lists. Each gets a label, a definition, one kind and one range.
- `ledger-v2.md` gets its after half and is ready for Hamid's approval.
- Step 5 (ORG/RACI) later replaces `core:responsibleDomain` literals with references to org units, as Q7 says.
