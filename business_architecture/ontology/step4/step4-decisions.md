# Step 4 decision log (working)

Decisions taken with Hamid, one at a time. Folded into the design proposal revision once all are recorded.

## Q1 — Vocabulary namespace (2026-09-22): APPROVED

`core:` (`https://w3id.org/lsc/ontology/modules/core/`) for reusable vocabulary — classes and properties.
`proc:` (`https://w3id.org/lsc/ontology/process/`) stays instance-only.

*Correction 2026-09-26: the IRI above was first recorded as `…/ontology/core/`; corrected to the locked Step 1 URI policy (`…/ontology/modules/core/`). See "IRI fork correction" below.*

Refinements (from external review, adopted):
- Term IRIs stable and unversioned (`core:ProcessDefinition`, never `core/1.0.0/...`).
- Ontology IRI `https://w3id.org/lsc/ontology/modules/core`; version IRI `https://w3id.org/lsc/ontology/modules/core/1.0.0`;
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
`https://w3id.org/lsc/ontology/modules/core/1.0.0`). 1.0.0 becomes the baseline
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

## Scope-note range citation route (2026-09-26, Hamid)

A bounded range citation, written in the source's scope note, that
explicitly covers the target and is affirmative, counts as a citation
route for Rule 5. Recorded as a separate route, "scope-note range
citation", auditable separately from whole-slug and label citations.
Applied in the uses-input pass: REL-00447 (CM-1-2-5-1-3/-4) and
REL-00564 (CM-1-3-1-1 through -5). Range-shaped citations in exclusion
contexts (REL-01278, REL-01279) do not qualify.

## Scope-note label citation route (2026-09-26, Hamid)

A scope-note citation by the target's exact unique current preferred
label counts as a citation route for Rule 5, recorded separately from
slug citations. Applied: REL-00862 ("Maintain Price & Discount Master
Data"), REL-01029 ("Manage Credit Card Transactions"), REL-00873
("Establish Credit Limit & Risk Code" — supersession reversed).

## Rule section 3 precedent reworded (2026-09-26)

REL-00214 had no citation route and was held in the uses-input pass;
its fact was removed and the attached enables mention REL-00152 held
with it. Precedent now reads: "REL-00436 attaches as duplicate
provenance on the independently-evidenced uses-input fact (REL-00447,
via scope-note range citation)."

## G1a count refresh (2026-09-26)

Count refresh, not a rule change. The G1a "75 mentions emit" (from 77 approved)
is now 33 emitting after the 2026-09-26 uses-input pass held 42 G1a mentions
(k=42). The "77 → 75" line now reads "77 → 33". Rule text unchanged; only the
counts reflect the applied pass.

## G1b reverse-fact gate check amended (2026-09-26, Hamid)

Amends approved rule text in section 4. The G1b gate check "reverse informed-by
fact present through its own row-level evidence" is now conditional: the reverse
fact is present **if** the reverse row has a route (stable-ID identity,
affirmative citation, two-way inverse pair, or approved decision); otherwise the
reverse row is held with no fact.

Reason: The informed-by pass holds 15 reverse informed-by rows that lack a route.
When both sides of a G1b pair are held, the relationship disappears from the
graph entirely. The 15 pairs are on the backlog (contradiction-pair-C pattern).

## Informed-by pass applied (2026-09-26, Hamid approved)

139 emitting `informed-by` rows reviewed under the strict citation test:

- **24 rows stand** under rule 4 (stable-ID identity; no rule 5 route required):
  7 with an affirmative citation + 17 without (REL-00017, REL-00025, REL-00055,
  REL-00071, REL-00123, REL-00136, REL-00365, REL-00877, REL-00905, REL-01107,
  REL-01147, REL-01177, REL-01190, REL-01207, REL-01229, REL-01282, REL-01283).
- **20 label-only rows promote** on an affirmative citation, recorded
  `D:hamid-verdict` (REL-00114, REL-00116, REL-00141, REL-00224, REL-00244,
  REL-00418, REL-00434, REL-00706, REL-00739, REL-00775, REL-00776, REL-00826,
  REL-00948, REL-01110, REL-01140, REL-01196, REL-01202, REL-01232, REL-01244,
  REL-01272).
- **95 rows held**: 55 exclusion/boundary-only citations, 1 counterpart
  citation with information flowing the wrong way (REL-00476, new hold label
  "counterpart, opposite flow"), 39 with no citation.

New hold label: "counterpart, opposite flow" — for rows where the citation
shows information flowing the wrong way (source → target, not target →
source). Signals a potential verb fix, not a target fix.

Totals: 761 → 666 emitting; 542 → 637 held; 603 → 508 facts.
Conservation: 666 + 637 + 12 + 1 + 2 = 1,318. ✓

## Governed-by pass: 10 supersessions (Hamid 2026-09-26)

The 2026-09-25 row-level governed-by approvals are not approved decision
evidence (recorded architecture decisions only: PR #110, PR #119). Each row
below was re-tested with the strict citation test (slug, unique label, range
— affirmative only). None carries an affirmative citation. Each is now:

**HOLD / D:hamid-verdict / NoAffirmativeCitation / Supersedes2026-09-25Approval**

The 2026-09-25 rationale is retained in provenance as superseded, not deleted.
Scope conditions on REL-00907, REL-01228, and REL-01256 lapse with the hold.
All ten are routed to the source workbooks for correction.

- **REL-00050**: 2026-09-25 rationale (superseded): "Inventory monitoring
  operates against policy-set min/max/safety-stock/operating-limit rules
  (set-versus-apply)."
- **REL-00067**: 2026-09-25 rationale (superseded): "Replenishment explicitly
  operates within approved inventory policies and projected stock against
  policy levels."
- **REL-00394**: 2026-09-25 rationale (superseded): "External compliance
  monitoring checks obligations against the exact compliance
  policies/procedures."
- **REL-00399**: 2026-09-25 rationale (superseded): "Internal trade-control
  monitoring verifies controls against compliance-program requirements and
  policies."
- **REL-00406**: 2026-09-25 rationale (superseded): "RIN reporting coordination
  operates under trading compliance program requirements, reporting controls,
  escalation model."
- **REL-00907**: 2026-09-25 rationale (superseded): "SCOPE: IP, licensing,
  protected-mark, and Legal/IP governance boundaries only — not all
  operational brand-standard content." Scope condition lapses.
- **REL-00937**: 2026-09-25 rationale (superseded): "Financing/payment-method
  definition depends on Treasury-approved instruments and Credit-approved
  exposure/eligibility rules."
- **REL-01005**: 2026-09-25 rationale (superseded): "Self-billing operates
  only under executed agreements; commercial terms/contracts establish the
  governing agreement framework."
- **REL-01228**: 2026-09-25 rationale (superseded): "SCOPE:
  trading-compliance, reporting, market-rule, and policy boundaries
  applicable to confirmations — not the full commercial/operational
  confirmation lifecycle." Scope condition lapses.
- **REL-01256**: 2026-09-25 rationale (superseded): "SCOPE: credit-control
  gates within fulfillment (no-self-exception rule) — not all
  order/fulfillment decisions." Scope condition lapses.
## Triggers pass: 2 stand, 5 promote, 11 hold (Hamid 2026-09-26)

**STAND (rule 4, stable-ID):** REL-00725, REL-00897. Keep emitting; basis only.

**PROMOTE (D:hamid-verdict):** REL-00127, REL-00235, REL-00236, REL-00246,
REL-00901. Keep emitting; basis → D:hamid-verdict 2026-09-26.

**HOLD (11):** The 2026-09-26 row-level "Trigger pattern" approvals are not
approved decision evidence (recorded architecture decisions only: PR #110,
PR #119). Each row was re-tested: an affirmative citation for `triggers`
must tie the source's event or result to the target (trigger, route to,
refer, escalate, hand off). A statement of where work is done does not
count. None of the 11 carries such a citation. Each is now:

**HOLD / D:hamid-verdict / NoAffirmativeTriggerLink / Supersedes2026-09-26Approval**

The 2026-09-26 "Trigger pattern" rationale is retained in provenance as
superseded, not deleted. All eleven are routed to the source workbooks for
correction.

Exclusion/boundary citations (REL-00009 precedent):
- **REL-00049**: scope excludes replenishment planning (CM-1-1-3-7-9); states
  what the source does *not* do, not that its exceptions invoke the target.
- **REL-00291**: "this process surfaces; limit actions are taken at
  CM-1-2-2-3-6" — states where limit actions happen, not that monitoring
  findings trigger them.
- **REL-00892**: boundary-only citation; no event-to-target link.
- **REL-00163**: scope says "excludes acting on the findings — amendments and
  renewals run through Manage Existing Contract" — states where amendments
  are done, not that monitoring findings start them (same wording class as
  REL-00291).

No citation:
- **REL-00169**, **REL-00170**, **REL-00252**: no slug/label/range citation.
- **REL-00396**, **REL-00398**, **REL-00400**, **REL-00403**: sibling
  compliance-monitor rows with trigger-like semantics, but sibling nearness
  alone is not a route for `triggers`.

**Totals:** 646→635 emitting, 657→668 held, 488→477 facts. Conservation 1,318 ✓

## Precedes/follows pass (2026-09-26 approved, AMENDED 2026-09-27)

38 STAND (rule 4, stable-ID). 256 PROMOTE (D:hamid-verdict / Rule 5 sequence route).
20 HOLD (D:hamid-verdict). **NOT basis-only** — 20 facts removed.

### Amendment 2026-09-27 (Hamid HOLD review)
Evidence Discipline Rule 5 (lock): non-sibling precedes/follows needs an
*affirmative* sequence citation (or two-way). Exclusion/boundary/owned-by is
NOT a route (REL-00009 precedent applies to sequence verbs).

**20 holds:**
- 6 ExclusionBoundaryCitation, no two-way (approval did not cover): REL-01223, REL-01227,
  REL-01241, REL-01289, REL-01291, REL-01294.
- 14 exclusion/boundary/owned-by/reference-data as sole route: REL-00008, REL-00068,
  REL-00112, REL-00149 (owned-by); REL-00193, REL-00200, REL-00206,
  REL-00307 (reference-data), REL-00319, REL-00351, REL-00374, REL-00930 (excludes/out-of-scope);
  REL-00184 ("may be handled by"), REL-00188 (boundary list).
- REL-00426 KEPT: scope has affirmative handoff ("submitting a payment
  request... to the designated AP/Treasury process").

Each hold: **HOLD / D:hamid-verdict / Supersedes2026-09-26Approval**.
All 20 facts verified unique single-row; zero knock-on.

**Totals:** 635 − 20 = **615** emitting; 668 + 20 = **688** held;
477 − 20 = **457** facts. Conservation: 615 + 688 + 12 + 1 + 2 = 1,318. ✓
Precedes facts: 202 − 20 = **182**.

Route breakdown (256 promotions): citation-only rows re-tested against full
scope text; affirmative sequence required (arrive from, route to, executes
through, come from).

Zero reciprocal core:precedes pairs (182 facts checked). Hard gate GREEN.

**Totals (amended 2026-09-27):** 615 emitting / 688 held / 457 facts.
Conservation: 615 + 688 + 12 + 1 + 2 = 1,318. ✓

Raw `B follows A` retained in provenance; canonical fact remains `A core:precedes B`.

### Precedes/follows supersessions (Hamid 2026-09-27, amending 2026-09-26 approval)

The 2026-09-26 precedes/follows approval did not cover rows without an
affirmative sequence citation. Each row below was re-tested 2026-09-27
against the full scope text (Evidence Discipline Rule 5). Each is now:

**HOLD / D:hamid-verdict / NoAffirmativeSequenceCitation / ExclusionBoundaryCitation / Supersedes2026-09-26Approval**

- **REL-01223**: ExclusionBoundaryCitation — source cites target as "owned by Regional Optimization (CM-1-1-2)"; boundary context only, not sequence.
- **REL-01227**: ExclusionBoundaryCitation — source cites target in "excludes settlement … (CM-1-2-4-1)"; boundary only, not sequence.
- **REL-01241**: ExclusionBoundaryCitation — source cites target in "Excludes the monthly plan itself, owned by … (CM-1-1-4)"; boundary only, not sequence.
- **REL-01289**: ExclusionBoundaryCitation — source cites target in "Excludes trade capture (CM-1-2-1-3)"; boundary only, not sequence.
- **REL-01291**: ExclusionBoundaryCitation — source cites target in "Excludes … settlement and invoicing (CM-1-2-4-1)"; boundary only, not sequence.
- **REL-01294**: ExclusionBoundaryCitation — source lists target (CM-1-2-4-2-4) in boundary dump; no sequence verb.
- **REL-00008**: "owned by Regional Optimization (CM-1-1-2)" — who owns what, not sequence.
- **REL-00068**: "owned by Physical Distribution Scheduling (CM-1-1-3-6)" — not sequence.
- **REL-00112**: "owned by Refinery Planning and Optimization (CM-1-1-4)" — not sequence.
- **REL-00149**: "owned by Perform RINs/REC Actualization (CM-1-2-3-1-7)" — not sequence.
- **REL-00184**: "may be handled by" — conditional, not affirmative sequence.
- **REL-00188**: target in branch list, then excluded — not sequence.
- **REL-00193**: "excludes confirmation with the counterparty" — exclusion.
- **REL-00200**: "excludes storage settlement" — exclusion.
- **REL-00206**: "excludes confirmation" — exclusion.
- **REL-00319**: "Excludes trade capture" — exclusion.
- **REL-00351**: "Excludes transmission deal capture" — exclusion.
- **REL-00374**: "Excludes settlement calculation and invoice validation" — exclusion.
- **REL-00930**: "Out of scope: Quote content composition" — exclusion.
- **REL-00307**: "division-of-interest references maintained under Manage Lease Contract (CM-1-2-1-2-8)" is reference-data usage, not sequence; "Excludes lease contract administration" is boundary.

All 20 routed to source workbooks for correction.

## Requires pass (2026-09-25 approved; evidence package 2026-09-27)

Definition: `core:requires` — the source cannot validly start, proceed, or
reach its controlled state without the target, its completed control, or its
required condition. Not merely inferred because the target later
consumes/calculates/uses related information.

5 APPROVE (D:hamid-verdict 2026-09-25). 1 HOLD (D:hamid-verdict 2026-09-25).
**NOT basis-only** — 1 fact not emitted.

**5 approved:**
- REL-00158: CM-1-2-1-2-1 (Create New Counterparty) requires CM-1-2-2-1-1
  (Perform Counterparty Credit Reviews). Genuine precondition: credit clearance
  must precede creation of the authorized counterparty and settlement records.
- REL-00168: CM-1-2-1-2-3 (Terminate/Novate Counterparty) requires CM-1-2-2-1-3
  (Manage Collateral). Valid closure-control prerequisite: collateral and
  related obligations must be closed, settled, transferred, or queued before
  the counterparty record is deactivated or transitioned.
- REL-00247: CM-1-2-2-2-3 (Manage Trade Modifications) requires CM-1-2-1-3
  (Trade Capture). Clear lifecycle dependency: a post-execution amendment,
  allocation, or termination can only update a trade record that exists in
  controlled trade capture.
- REL-00872: CM-1-3-6-6-1 (Set Up Prospect) requires CM-1-3-7-4-6 (Perform KYC
  Due Diligence). Legitimate onboarding gate: KYC due diligence is initiated
  before governed customer/member/card-account records are established.
- REL-00873: CM-1-3-6-6-1 (Set Up Prospect) requires CM-1-3-7-4-2 (Establish
  Credit Limit & Risk Code). Restored 2026-09-26; supersession reversed;
  basis: scope-note label citation. Scope note: credit-controlled onboarding
  prerequisite only.

**1 held:**
- REL-00208: CM-1-2-1-3-8 (Capture Structured Deals) requires CM-1-2-2-3-15
  (Manage Commodity Valuations). **HOLD / D:hamid-verdict**. The asserted
  requires relation is not sufficiently supported as a prerequisite gate, and
  the proposed remap to core:dependsOnOutputOf would alter source meaning at
  emission time. Emit no triple. Route for source-workbook relationship review
  and correction.

No count changes — all 5 approved facts already stored in canonical-facts.csv.

## Assures pass (approved; evidence package 2026-09-27)

Definition: `core:assuredBy` — the assurance activity performs a defined
governance, compliance, quality, review, control-testing, or equivalent
oversight role over the assured thing or outcome. Not operational support,
supply, documentation, evidence, balancing, fulfillment, feeding, or mere
necessity.

5 APPROVE (D:hamid-verdict). 3 HOLD (D:hamid-verdict).
**NOT basis-only** — 3 facts not emitted.

**5 approved:**
- REL-00401: CM-1-2-4-2-11 (Manage Tax Compliance) assuredBy CM-1-2-4-3-5
  (Manage Taxes). Manage Tax Compliance reviews registrations, licensing,
  exemption certificates, filing-calendar compliance, tax-determination
  controls, and gaps.
- REL-00719: CM-1-3-4-2-2 (Conduct Research) assuredBy CM-1-3-4-2-3 (Manage
  Research). Manage Research owns commissioning, standards, quality, and
  completion of studies while Conduct Research performs them.
- REL-00801: CM-1-3-5-3-4 (Develop / Update Campaigns) assuredBy CM-1-3-5-3-7
  (Manage Use Of Brand). Manage Use Of Brand applies brand standards through
  material review and escalation of deviations.
- REL-01269: CM-1-2-1 (Trading Management) assuredBy CM-1-2-4-3 (Regulatory &
  Compliance). Regulatory & Compliance maintains policies and procedures,
  monitors regulatory and internal-policy adherence, oversees
  compliance-supporting controls.
- REL-01270: CM-1-2-4-1 (Settlements) assuredBy CM-1-2-4-3 (Regulatory &
  Compliance). Same cross-cutting regulatory and compliance control function
  assures the compliance condition of Settlements without conducting
  settlement operations.

**3 held:**
- REL-00355: **HOLD / D:hamid-verdict**. Manage Settlement Documents controls
  documents used to execute and evidence settlements — operational support
  and evidence management, not sufficiently explicit independent assurance.
  Emit no triple.
- REL-00385: **HOLD / D:hamid-verdict**. Documentation, workpapers,
  reconciliation evidence, and controlled reporting support or evidence
  Accounting but do not establish that the source performs assurance over
  Accounting. Emit no triple.
- REL-01106: **HOLD / D:hamid-verdict**. Crude/Feed Supply Management manages
  the feedstock supply position and associated risks; it does not assure
  Crude/Feed Demand Management. The existing core:assuredBy fact is removed;
  emit no substitute.

No count changes — all 5 approved facts already stored in canonical-facts.csv.

## Constrained-by pass (approved; evidence package 2026-09-27)

Definition: `core:constrainedBy` — stored from the bounded activity, decision,
or outcome to its binding constraint source. Excludes advice, broad
association, ownership, sequencing, and optional considerations.

10 APPROVE (D:hamid-verdict). 1 HOLD (D:hamid-verdict).
**NOT basis-only** — 1 fact not emitted.

**10 approved:**
- REL-00015: CM-1-1-2-10 (Allocate Crude and Feedstock) constrainedBy
  CM-1-1-3-7 (Inventory Management).
- REL-00018: CM-1-1-2-11 (Allocate Finished Products) constrainedBy
  CM-1-1-3-7 (Inventory Management).
- REL-00024: CM-1-1-2-13 (Plan Finished Goods Inventory) constrainedBy
  CM-1-1-3-7 (Inventory Management).
- REL-00087: CM-1-1-4-7-2 (Evaluate Crude & Feedstock) constrainedBy
  CM-1-1-4-7-5 (Capture Refinery Level Constraints).
- REL-00091: CM-1-1-4-7-3 (Capture Crude Availability) constrainedBy
  CM-1-1-4-7-5 (Capture Refinery Level Constraints).
- REL-00099: CM-1-1-4-7-5 (Capture Refinery Level Constraints) constrainedBy
  CM-1-1-4-7-8 (Perform Scenario Analysis).
- REL-00103: CM-1-1-4-7-6 (Capture Inventory) constrainedBy CM-1-1-3-7
  (Inventory Management).
- REL-00574: CM-1-3-10-2 (Process Customer Lifting Forecasts and Nominations)
  constrainedBy CM-1-3-10-3 (Manage Terminal Lifting Allocation).
- REL-00894: CM-1-3-6-6-5 (Handle Card Limits) constrainedBy CM-1-3-7-4-2
  (Establish Credit Limit & Risk Code).
- REL-01284: CM-1-1-4-7 (Refinery Optimization) constrainedBy CM-1-1-3-7
  (Inventory Management).

**1 held:**
- REL-00097: **HOLD / D:hamid-verdict**. The broad Refining target has no
  supplied definition and does not provide evidence that it is a constraint
  source for Capture Refinery Level Constraints. Retain the context hold,
  emit no triple.

No count changes — all 10 approved facts already stored in canonical-facts.csv.
