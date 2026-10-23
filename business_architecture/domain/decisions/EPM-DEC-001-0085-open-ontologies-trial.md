# EPM-DEC-001-0085: The open-ontologies trial: not adopted; it found no defect the checks miss

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028; the trial and its adoption rule approved by the decision owner, 2026-10-21) |
| Date | 2026-10-22 |
| Questions | Queue item 9: does open-ontologies' semantic plan or OWL coherence check find anything in the core releases that `scripts/check.sh` and the competency regression miss? |
| Source | Claude Code sessions of 2026-10-21 (session 7) and 2026-10-22 (Phase E); `answers-2026-10-21-open-ontologies-trial.md`, `answers-2026-10-22-phase-f.md` |

## Context

On 2026-10-21 Claude proposed a local trial of open-ontologies (github.com/fabio-rovai/open-ontologies, MIT licence, Rust) once the next core release existed: its `plan` of core 2.1.0 against 2.2.0, and its OWL coherence check, outside the repository and CI, with the result recorded here and the tool adopted only if its report finds something `check.sh` and the regression miss. The decision owner added it to the queue. On 2026-10-22, after Phase E, the decision owner gave the go-ahead. The trial ran that night; its report is `business_architecture/ontology/trials/open-ontologies-2026-10-22.md`.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**

1. **The tool is not adopted** into `scripts/check.sh` or CI. The trial does not meet the adoption rule, read as a finding of a defect: its only new output is three lint notes, none a defect (item 2).
2. **What it found** (commit `93295305`, built from source, each run under a second):
   - `plan` reports 217 added and 7 removed triples, which an independent rdflib diff confirms; `release/test_build_core_2_2.py` asserts the same removed set (the version header and two APQC decisions) and the 23 new concepts. It counts no `skos:Concept` as an individual, so it reports no added individuals for a release that adds 23 concepts, and it calls every release "not an extension" because each release rewrites the version header.
   - `reason owl-dl` finds core 2.2.0, and the union of the 11 newest packages, consistent and every class satisfiable. A deliberate clash fails as it should. The graphs hold one disjointness axiom (Person and Organization in `party`), which the party shapes' `sh:xone` already enforces.
   - Three lint notes: `core:CanonicalFact` and `core:ScopedSequence` have no `rdfs:comment`, and `core:evidenceBasis` has no `rdfs:domain`. Both classes carry a `skos:definition`, which is how core defines its terms, and Rule 1 of the projection needs a range, which `evidenceBasis` has. None is a defect.
3. **When to run it again:** if a release adds OWL axioms that SHACL does not test, such as disjointness between classes, class domains and ranges, or property chains. The trial's script is described in the report.

## Alternatives considered

- **Adopt the coherence check for its speed.** Not chosen: it would have nothing to find today, and the adoption rule asks for a finding.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-21-open-ontologies-trial.md`: "yes, add the Phase D trial to the queue". Saved in `answers-2026-10-22-phase-f.md`: "you can do the openontology trial as well." The trial plan and its adoption rule are Claude's words, which the decision owner approved; the verdict above is Claude's, under the delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse it.

## Evidence

- `business_architecture/ontology/trials/open-ontologies-2026-10-22.md`.
- `business_architecture/ontology/release/test_build_core_2_2.py`; `releases/party/1.0.0/shapes.ttl`; EPM-DEC-001-0076.

## Consequences

- Queue item 9 is done. Nothing changes in the repository's checks.
