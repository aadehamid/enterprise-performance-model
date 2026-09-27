# Step 4 decision log (working)

Decisions taken with Hamid, one at a time. Folded into the design proposal revision once all are recorded.

## Q1 — Vocabulary namespace (2026-09-22): APPROVED

`core:` (`https://w3id.org/lsc/ontology/core/`) for reusable vocabulary — classes and properties.
`proc:` (`https://w3id.org/lsc/ontology/process/`) stays instance-only.

Refinements (from external review, adopted):
- Term IRIs stable and unversioned (`core:ProcessDefinition`, never `core/1.0.0/...`).
- Ontology IRI `https://w3id.org/lsc/ontology/core`; version IRI `https://w3id.org/lsc/ontology/core/1.0.0`;
  explicit `owl:Ontology` header with `dcterms:title/description`, `owl:versionIRI`,
  `owl:versionInfo`, `dcterms:issued/creator/license` (answers the unnamed-header nit).
- Module-boundary rule: `core:` = foundational planned-process semantics only.
  org → Step 5, kpi → kpi module, observed execution → PROV-O in Step 6.
- NOT adopted: the `data:` module in the external boundary rule — our module policy has
  four modules (core, party, kpi, organization); adding `data:` needs its own decision.

## Adopted from external review (design deltas, pending spec revision)

- `core:ProcessDefinition` typing rule (narrower than proposal §2; supersedes our F1):
  apply to approved process + capability concepts, candidate structural/capability nodes
  with authored definitions, blocked/retired only when retaining a meaningful record.
  Do NOT apply to L0 scheme roots, pure structural anchors, tombstones, not-process roots.
- `core:conceptKind`: object property → controlled SKOS kind scheme
  (`core:ProcessKind`, `core:CapabilityKind`, `core:StructuralAnchorKind`), not a string.
  Reframes Q8. Does not force the CM-1-3-1-6 class decision.
- `core:lifecycleStatus`: object property → lifecycle-state concepts
  (Active, Candidate, Blocked, Retired, Deprecated, Superseded), not a string.
  Keep three layers distinct: architecture artifact status (Candidate/Implemented, cf. path register),
  concept lifecycle, authoring status. New decision question.
- `core:taxonomyLevel`: documented as derived metadata ("current rendered depth"),
  never for security / KPI ownership / criticality / domain assignment / level-assuming queries.
  Composes with the taxonomyLevel-vs-broader-depth gate.
- Terminology notes migration: `skos:editorialNote` (authoring/review history),
  `dcterms:provenance` (migration/change history), decision-log references (review evidence) —
  not a blanket `core:definitionNote`. New decision question.
- Proposed resolutions queued for their questions: Q4 → retain `usesInput` process edge
  (resolves Act On #4); Q5 → structured literals now, defer InformationObject minting
  (resolves Act On #2).

## Open questions (revised order)

Q2 retirement mode · Q3 first version · Q5 flow depth ·
Q6 processHorizon (+ facet split: cadence / mode / planning level) ·
Q7 responsibleDomain interim · Q8 conceptKind (reframed) · Q9 lifecycleStatus model ·
Q10 terminology-notes mapping · Q11 seven unresolvable targets · Q12 six ambiguous targets

## Q2 — intake: retirement mode (2026-09-22): APPROVED

**Flag-day.** All `intake:` triples go in one Step 4 release — no deprecated-alias
transition (~5,571 dead staging triples is not worth carrying).

Preconditions before that release ships:
- Reconfirm the no-consumer attestation (last given 2026-09-22).
- Per-predicate conservation ledger: `emitted + held = source total` for every
  `intake:` predicate — "zero `intake:` triples" proves deletion, not replacement.
- Explicit merge/release approval still required — Step 4 kickoff did not approve
  the major release.

## Workbook PR #110 (2026-09-22, DO NOT MERGE)

https://github.com/aadehamid/enterprise-performance-model/pull/110
16 stale pre-R1 relationship-label cells fixed (`Refinery Planning` →
`Refinery Planning and Optimization`, `Refinery Scheduling` →
`Refinery Production Planning and Scheduling`); TTL regenerated
(14,496 triples before and after, exactly 16 `relatedConcepts` literals changed);
permanent `no stale pre-R1 relationship targets` lock added to `r1-gate-check.py`.
Deliberately unchanged: `terminology_notes` prose (authoring history),
`primary_output` free text (Step 4 Q5), `Daily Refinery Scheduling` altLabel,
9 unmatched non-stale targets (Step 4 Q11).

## Q3 — first formal version (2026-09-22): APPROVED

Step 4 ships as `core` 1.0.0 — the first formal release of the core module.
It is the first version with governed properties instead of provisional
annotations, and the first to ship an explicit version header
(`owl:versionInfo`, issued date, license, `owl:versionIRI`
`https://w3id.org/lsc/ontology/core/1.0.0`). 1.0.0 becomes the baseline
that Step 5 (organization), Step 6 (PROV-O) and later modules version against.

## Q4 — uses-input (2026-09-22): APPROVED

Step 4 models inputs as direct process-to-process edges (`core:usesInput`
from a process to the process it takes input from). No new nodes — the
edge preserves the dependency chain ("what does this process depend on;
what breaks if it fails") that the competency questions need. What
exactly flows through those edges is Q5.

## Q5 — flow depth (2026-09-22): APPROVED

Step 4 captures flows as governed structured values on the input/output
links — controlled, consistently-spelled flow names, no new nodes. The
workbook's flow information is preserved and queryable ("which processes
consume the demand forecast?"). Minting InformationObject nodes (~1,900)
is deferred: it is a data-governance project (identity, dedup, ownership,
lifecycle) that no Step 4 competency question or consumer requires.
Revisit trigger: a real use case that needs to trace a specific artefact
(e.g. audit lineage of the approved operating plan) — then mint that
flow as a node deliberately, one at a time.

## Q6 — processHorizon facet split (2026-09-22): APPROVED

`intake:processHorizon` conflated three dimensions (evidence: 8 distinct
workbook values across 485 rows — event-driven/periodic/continuous are
operating modes; daily/weekly/monthly are cadences; tactical/strategic
are planning levels; "periodic" alone (107 rows) records no cadence).
Step 4 splits it into three controlled fields: `core:operatingMode`
(event-driven | periodic | continuous), `core:cadence`
(daily | weekly | monthly | quarterly | annual), `core:planningLevel`
(strategic | tactical | operational). Rows with only "periodic" are
recorded as cadence-unspecified — honest about the gap rather than
pretending "periodic" is a cadence.

## Q7 — responsibleDomain interim (2026-09-22): APPROVED

Step 4 keeps `responsible_domain` as a governed literal on the process,
explicitly interim. No org nodes are minted — Step 5 (ORG/RACI) designs
the org model and replaces these labels with references to real org
units/roles. Evidence: 10 distinct workbook values across 485 rows, 456
of them "Commercial & Marketing"; the value is in the exceptions
(Finance-enabled Supply & Trading ×13, Finance ×2, Refining ×2,
cross-functional ×6). The 6 free-text cross-functional entries are
normalized to a governed "Cross-functional" value with detail preserved
in a note. Controlled list makes the Step 5 migration mechanical.

## Standing rule (2026-09-22, per Hamid)

Every Step 4 design decision that comes out of the Q&A goes in the
ontology playbook's decision log — the playbook is the team handover,
so the approach must live there, not just in working notes. Backfilled
2026-09-22: Q1 refinements, Q2 flag-day, Q4 usesInput, Q6 facet split
(PR #114); Q3 in PR #111, Q5 in PR #112, Q7 in PR #113.

## Value-stream / capability / activity / event / decision layer (2026-09-22): PARKED

Hamid asked whether the fuller business-architecture hierarchy (domain >
value stream > stages; value stream > capability > business process >
activity; events; decisions — as in the KPI Store / domain modeling docs)
should be represented in the ontology. Decision: park it as a post-1.0.0
roadmap item. Represent as governed overlays over the stable process
backbone, not a second hierarchy (value streams cut across the
single-parent tree; the existing value_stream_*.json overlays already
reference-not-duplicate via linkedProcessIds — that pattern is the
template). Hooks: Q8 CapabilityKind (bridge), Step 6 PROV-O (events).
Recorded in playbook Appendix A with revival trigger.

## Q8 — conceptKind controlled scheme (2026-09-22): APPROVED

`core:conceptKind` is an object property to a controlled SKOS scheme, not
a string. Kinds: Process (real business process with inputs/outputs/
cadence), Capability (an ability the organization has, realized by
processes), StructuralAnchor (navigation/grouping node — L0 roots, empty
stubs, tombstones — not work anyone performs). Rationale: consumers treat
kinds differently ("all processes" must not return navigation nodes; no
RACI/cadence on anchors). Deliberate boundary: this does NOT classify
CM-1-3-1-6 ('Marketing Insight and Metrics Stewardship') — that stays a
parked modeling question. We build the shelf; classification comes later.

## Review corrections applied (2026-09-22)

Hamid approved the external review feedback. Applied in the consolidated
playbook PR:
- Q4 property renamed: `core:usesInput` → `core:dependsOnOutputOf` /
  inverse `core:providesInputTo` (a process is not an input; its output
  is). `core:consumes`/`core:produces` reserved for future identified
  InformationObject instances.
- Q7 wording refined: Step 5 maps interim values to governed
  organization/role/ResponsibilityAssignment references *where the
  operating model evidences the relationship* (some labels are business
  domains, not org units).
- CapabilityKind vs BusinessCapability split: `core:CapabilityKind` is a
  classification value; actual capabilities are a future
  `core:BusinessCapability` class with `core:realizedBy` links.
- #111–#115 consolidated into a single playbook PR.

## Consolidation (2026-09-22)

PRs #111-#115 closed as superseded. Single consolidated playbook PR
opened: #116 (DO NOT MERGE), branch docs/step4-decisions-consolidated,
commit e13b70738e41fa73f37ac2f2568440f0a68a5b72, based on main
c801d982f5ec6b545cf1e3101a72489b15ea5abe. Awaiting Hamid's review, then
Q9 (lifecycle model).

## Q9 — lifecycle model (2026-09-22): APPROVED

`core:lifecycleStatus` is an object property to a controlled SKOS scheme
with four states: Candidate → Approved → Deprecated → Retired.
Blocked/held are NOT states: a separate hold flag applies to a concept
in any lifecycle state, with a recorded reason (a Candidate can be
blocked; an Approved concept can be put on hold without losing its
state). Must not conflict with OWL:
- Deprecated ⇒ owl:deprecated true (required).
- Retired ⇒ owl:deprecated true (retired implies deprecated).
- Candidate/Approved ⇒ owl:deprecated absent or false.
Agreement enforced by SHACL in Step 9; the rule is stated now.
Allowed transitions: Candidate→Approved, Candidate→Retired (rejected
before publication), Approved→Deprecated, Deprecated→Approved
(undeprecation, governed), Deprecated→Retired. Retired is terminal —
never resurrect; mint a new concept instead. dcterms:isReplacedBy points
to the successor where one exists.

## IRI fork correction (2026-09-22)

Hamid caught a fork: the Q1/Q3 wording in the consolidated PR used
`https://w3id.org/lsc/ontology/core` as the ontology IRI, but the locked
Step 1 URI policy (2026-09-18) fixes module namespaces at
`…/ontology/modules/{module}`. Decision: KEEP the locked
`https://w3id.org/lsc/ontology/modules/core` — no supersession (the lock
was never changed, the shorthand never shipped, nothing published). My
error: I proposed the shorthand in Q1 without checking Lock 3. Playbook
corrected: ontology IRI, version IRI (`…/modules/core/1.0.0`), Turtle
header example, and Appendix B rules all use the locked IRI, with an
explicit reconciliation note in the decision log.

## Q9 revision — three dimensions (2026-09-22)

Hamid approved the review feedback on PR #117. The single-chain model
(Candidate → Approved → Deprecated → Retired) is WITHDRAWN — it
conflated concept lifecycle with approval status, violating the Q1
three-layer lock. Replaced with three independent dimensions:
- core:lifecycleStatus: Active / Deprecated / Retired (Superseded =
  Deprecated + dcterms:isReplacedBy, not a state).
- core:governanceStatus: Exploratory / Draft / Candidate /
  ApprovedBaseline / Implemented (existing vocabulary, formalized).
- core:holdStatus: NoHold / EvidenceHold / OwnershipHold / DecisionHold /
  ImplementationHold + core:holdReason.
OWL alignment kept (Deprecated/Retired ⇒ owl:deprecated true).
"Retired is terminal" softened: terminal for active use, restorable only
via new governance decision + provenance. PR #117 revised in place
(#116 already merged, so folding was moot).

## Q10 — terminology-note migration (2026-09-22): APPROVED

Selective-alias policy (review-corrected; blanket "every prior name
becomes altLabel" rejected — altLabel is a live search commitment):
- Safe former names → skos:altLabel, only if unique, non-misleading,
  non-colliding, and useful for retrieval (7-check rule).
- Generic, ambiguous, authority-overstating, case/punctuation-only, or
  scope-limited former names → preserved in migration history
  (core:priorPreferredLabel, annotation property), NOT searchable.
- Scoped aliases (e.g. APQC-comparison context) → kept with their
  context in the migration map; never flattened into skos:altLabel.
- One-line rename rationale → skos:editorialNote; migration event and
  source → dcterms:provenance; full reviewer reasoning stays in the
  decision log / naming queue by reference.
- Conservation rule (extends Q2 ledger, merge gate for intake cutover):
  every non-null prior_name gets exactly one recorded disposition;
  every name_change_note maps to rationale + provenance; every
  scoped_historical_alias has a context or is explicitly rejected.
- Minimal Step 4 vocabulary: core:priorPreferredLabel only. Reified
  HistoricalLabelRecord deferred until needed.
- 92-row historical-label disposition report is a tracked pre-cutover
  gate (not built tonight).

## Q11 — relationship target dispositions (2026-09-22): APPROVED

Rule (review-corrected): every relationship mention gets a governed
disposition; ONLY mentions classified as process-to-process become Step
4 object-property triples. Five disposition types: ResolvedToConcept,
ParkedFutureConcept, StructuredFlowValue, ExternalGovernanceReference,
DroppedAsNonProcessProse.
Item dispositions for the 9 unmatched targets:
- Network Design -> ParkedFutureConcept (which network? retail/supply/
  distribution/terminal/channel is the recorded future question; do not
  collapse into existing nodes).
- Integrated Marketing Planning -> ParkedFutureConcept (likely a
  cross-cutting planning capability / value-stream overlay).
- "contemporaneous assumption basis for Regional Backcasting" ->
  StructuredFlowValue (information flowing into the process, Q5).
- Data Governance -> ExternalGovernanceReference (cross-cutting
  enterprise domain; never a proc: node under Commercial).
- Monthly Operating Plan -> StructuredFlowValue (plan artifact, per the
  R1 plan-vs-artifact distinction).
- Establish & Maintain Delegation Of Authority -> ParkedFutureConcept
  (enterprise governance; Finance/Legal/corporate ownership TBD).
- Manage Trading Books & Strategies Structure -> ParkedFutureConcept
  (pending Supply & Trading operating-model refinement; normalize label
  later).
- Develop/Update Strategy -> ResolvedToConcept ONLY where source-row
  context proves the Consumer VP lifecycle (CM-1-3-2-3-4); otherwise
  ParkedFutureConcept. No global lexical replacement.
- Serve to Customer -> DroppedAsNonProcessProse (recorded as dropped
  with reason; dropped only where no source context evidences a target).
New properties (subjectToGovernanceDomain etc.) deferred to
implementation design. Pre-cutover instrument: the row-level
target-disposition report (subject, verb, phrase, disposition,
rationale, emit-triple-or-not).

## Q11 correction — six dispositions fixed (2026-09-22)

Hamid caught that the first-cut "unmatched" report matched bare phrases
and missed parenthetical qualifiers. Verified against the identity map
and committed TTL: six of the nine were wrongly parked/dropped.
Corrected: DOA -> CM-1-2-2-3-2; Integrated Marketing Planning ->
CM-1-3-5-2; Serve to Customer -> CM-1-3-6-2-6; Develop/Update Strategy
-> CM-1-3-2-2-4 (CVP context confirmed); Trading Books ->
CM-1-2-2-3-1 (batch 12 split); Network Design -> CM-1-3-3-4 for
qualified mentions, with ONE genuinely unmatched bare mention (Brand
Imaging row) parked. Unchanged: backcasting basis + Monthly Operating
Plan -> StructuredFlowValue; Data Governance -> ExternalGovernanceReference.
Recorded principle: labels aren't identity. Framework (five types)
unchanged; DroppedAsNonProcessProse has no current members. PR #119
stays HOLD, not merged.

## Q12 — ambiguous relationship targets (2026-09-22): APPROVED

Rule: a lexical match is not a semantic resolution. Resolve a target
only when stable identifier evidence or approved contextual evidence
(source definition, branch/domain, verb, scope, decision record)
identifies ONE governed concept. Otherwise record AmbiguousDeferred
with raw phrase, candidate set, evidence considered, reason, and review
trigger; emit no triple. Decision ladder: stable ID -> approved
contextual evidence sufficient to identify exactly one governed target
(label match is a candidate filter, never a join; resolution recorded
as the concept's slug, per the 2026-09-21 identity lock) -> scoped
historical alias (valid context) -> defer; non-
process phrases fall back to Q11 dispositions. Adds AmbiguousDeferred
as the sixth disposition type (extends Q11's five). Amendment to Q11:
the single bare "informed-by: Network Design" mention (Brand Imaging
row) moves from ParkedFutureConcept to AmbiguousDeferred — the network
type itself is uncertain, not just unmodeled. Canonical example with
candidate set (retail/supply/distribution/terminal/channel) and review
trigger (R2 network-design decomposition or first consumer need).
Row-level disposition report gains: candidate slugs/labels, resolution
evidence, confidence (Resolved/Contextual/Deferred), emission decision,
review trigger. Per-disposition emission rules recorded for the future
promotion script.

## Step 4 design complete (2026-09-22/23)

All 12 questions decided and merged on main (PRs #116–#120).
Q12 merged via #120 at 6ab2197b. Standing locks carried into the
record: labels aren't identity (2026-09-21 lock); label match is a
candidate filter, never a join; resolutions recorded as slugs.
Pre-cutover gates: 92-row label report, row-level target report,
Q2 ledger, no-consumer confirmation. No implementation without
Hamid's explicit approval.

## Step 4 design complete (2026-09-23)

All 12 questions decided and merged on main (PRs #116–#120).
Q12 merged via #120 at 6ab2197b. Standing locks carried into the
record: labels aren't identity (2026-09-21 lock); label match is a
candidate filter, never a join; resolutions recorded as slugs.
Pre-cutover gates: 92-row label report, row-level target report,
Q2 ledger, no-consumer confirmation. No implementation without
Hamid's explicit approval.
