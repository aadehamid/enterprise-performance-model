# Relationship-target disposition report — v1.1 (APPROVED)

Source: committed `step3-taxonomy.ttl` (main) + `step2-identity-map.json`.
**All 1,317 mentions have a governed disposition — zero undispositioned
mentions.** Generator: `classify.py` (re-runnable).

**Generated output is a proposal, never the governed file.** `classify.py`,
`classify_v2.py` and `context_pass.py` write to
`step4/proposal/target-report/` (gitignored), the same rule `mapping_v2.py`
follows. The governed files in this folder carry reviewed decisions that a
regeneration would revert (e.g. `target-dispositions-v2.csv` holds approvals
from 2026-09-25). Downstream consumers (`context_pass.py`, `mapping_v2.py`,
`evidence-gate.py`) read the governed files only, so a proposal changes
nothing until it's reviewed and promoted into this folder by PR. Script paths
derive from each script's location; `EPM_STEP4_DIR` and `EPM_REPO_ROOT`
override them. `../test_script_portability.py` guards all of this.

## Confidence taxonomy (per 2026-09-22 review)

| Confidence | Meaning | Emission rule |
|---|---|---|
| `Resolved` | Stable identifier (slug/notation) carried in the mention | Emit automatically after subject/target existence checks |
| `ContextualResolved` | Unique exact preferred-label match; label was the candidate filter, slug recorded as identity | Emit after mechanical uniqueness validation |
| `ContextualInferredSibling` | Inferred from shared local decomposition pattern; **not** conclusive proof | **HOLD** — targeted human review before emission |
| `Deferred` | Ambiguous, flow value, or external reference | No process-dependency triple |

Definitions: **ContextualResolved** — resolution supported by approved
context identifying one target. **ContextualInferredSibling** —
resolution inferred from a shared local decomposition pattern;
requires targeted human confirmation before triple emission.
**Undispositioned** — a mention with no classified handling; this
report has zero.

## Resolution patterns (per 2026-09-24 sibling review)

Every row carries a `resolution_pattern`: the governed method by which
the raw target was resolved. Values: `StableIdentifier`,
`UniquePreferredLabel`, `ApprovedLocalAnalysisCycle`,
`ApprovedSiblingTaxability`, `AmbiguousDeferred`,
`StructuredFlowValue`, `ExternalGovernanceReference`.

- **ApprovedLocalAnalysisCycle** (40 rows): a narrow approved pattern
  for the five sibling decompositions (Market, Company, Consumer,
  Customer/Marketer, Competitor Analysis) that instantiate the
  four-stage template — Define Objectives and Scope → Source and
  Collect Information → Analyze Data → Document Findings — with aligned
  definitions and reciprocal relationship verbs. Applies only within
  those approved decompositions.
- **ApprovedSiblingTaxability** (2 rows): `CM-1-3-8-1-1 → CM-1-3-8-1-3`
  (invoice creation consumes transaction-level tax determination) and
  `CM-1-3-8-4-4 → CM-1-3-8-4-5` (indirect-tax reconciliation consumes
  period-end taxability-treatment recommendations).

## Result (v1.1)

| Disposition | Confidence | resolution_pattern | Rows |
|---|---|---|---|
| ResolvedToConcept | Resolved | StableIdentifier | 203 |
| ResolvedToConcept | ContextualResolved | UniquePreferredLabel | 1057 |
| ResolvedToConcept | ContextualInferredSibling | ApprovedLocalAnalysisCycle | 40 |
| ResolvedToConcept | ContextualInferredSibling | ApprovedSiblingTaxability | 2 |
| AmbiguousDeferred | Deferred | AmbiguousDeferred | 12 |
| StructuredFlowValue | Deferred | StructuredFlowValue | 2 |
| ExternalGovernanceReference | Deferred | ExternalGovernanceReference | 1 |

## Sibling review package

`sibling-review-package.csv` — **APPROVED 2026-09-24**: the 42 held rows with source/candidate
slugs, labels, verb, raw target, shared-parent evidence, both
definition excerpts, and **completed decision cells**: all 42
`approve`, with per-row rationale and the assigned resolution pattern.
Preserved as the approved review artifact; do not discard after
implementation.

## Emission guards (for the future promotion script)

Sibling-derived triples may be emitted only if:

- `resolution_pattern` is an explicitly approved pattern;
- source slug, candidate slug, and raw target exactly match the
  approved row;
- the relationship verb is one of the approved pattern verbs;
- both source and candidate remain in the approved local parent
  subtree;
- no later rename/reparenting invalidates the pattern;
- the disposition report is versioned and checked into the release
  evidence.

Do NOT generalize same-parent lexical matching beyond the approved
patterns.

## Future terminology item

Two distinct concepts retain the same preferred label "Determine
Taxability" (`CM-1-3-8-1-3` transaction tax determination vs
`CM-1-3-8-4-5` period-end taxability treatment recommendation).
Semantic-search and target-resolution risk; review in a future
terminology/semantic-model refinement.

## Deliberately not decided here

Verb→predicate mapping (which RDF property each of precedes / enables /
governed-by / constrained-by / triggers / assures / requires /
constrains becomes) is implementation design, not part of this report.
The emission column says *whether* a triple is emitted, not *which*.
