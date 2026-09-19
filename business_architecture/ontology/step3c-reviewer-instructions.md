# Definition Reviewer Instructions — Downstream Process Ontology (Step 3c)

**Locked version:** v2026-09-19b (PTC parking rule: blocked/retired, not pending)

This is the same class of follow-up as #30: the workbook contract changed, so this guide and `step3c-workbook-validate.py` were rewritten to match it. Locked boundary rules and the 10-point quality bar are unchanged. Phase 1 fields are required on **new** approvals. The 15 rows approved in #29 stay `approved` with empty Phase 1 until a later backfill pass — they are flagged by the validator as `NOTE`, not silently waived and not blocked.

## What this is

We are building a controlled SKOS concept scheme—a downstream oil-and-gas process taxonomy—covering modeled process concepts from L0 (**Downstream Operations**) through L6. It currently contains 680 concepts. The published taxonomy still has 192 definitions (the #29 merge). The authoring workbook, after review batch 01 (#32), holds **20 `approved` / 483 `pending`** rows. The five new approvals have not been merged via `step3-skos-taxonomy.py --authored` yet.

The reviewer’s job is to research, author, and quality-review missing definitions in the workbook to an enterprise-grade standard so that approved rows can be merged into the taxonomy. The domain focus is **downstream oil and gas**.

The reviewer must use available high-quality references to inform definitions and boundaries, including authoritative regulatory sources where relevant; recognized industry bodies, standards, and guidance; credible technical and academic sources, and appropriate primary organization documentation. External references are evidence and context—not text to copy and not an authority that overrides the approved taxonomy, its parent hierarchy, or Hamid’s documented decisions.

When uncertain, the reviewer must ask Hamid a clear question in `open_questions` and leave the row `pending`. Do not make an assumption merely to complete a row.

## What a concept represents

Each workbook row represents a business process or process capability at the level implied by its hierarchy position—not an organizational unit, asset, job title, system, KPI, document, policy, project, control, data object, or implementation detail.

Define the recurring business activity and its intended outcome. Confirm that in `concept_type_check` (`process` or `capability`). If a row appears not to represent a process or capability, set `concept_type_check` to `mixed/needs-review` or `not-process`, record the concern in `open_questions`, and leave the row `pending` for Hamid’s decision. Do not force a definition.

## The workbook

Use `business_architecture/ontology/build/output/step3c-definition-authoring-workbook.xlsx`. It is a **6-sheet semantic-intake workbook** (since #31), not a single authoring sheet.

| Sheet | Role |
| --- | --- |
| **Start Here — Decisions & Phases** | Purpose, process-concept rule, locked boundaries, escalation, Phase 1 → 2 → 3 workflow |
| **Review & authoring** | The working queue (503 rows) |
| **Column guide** | Field-by-field fill rules and ontology targets |
| **Controlled vocabularies** | Governed values for `status`, `concept_type_check`, `process_horizon`, and relation types |
| **Reference register** | Reusable `source_id`s. Register a source here before citing it |
| **External mappings** | Reviewed cross-scheme mappings only. Leave empty unless Hamid has accepted a mapping |

Structural tree moves accepted during review but **not** applied in a definition batch are recorded in `business_architecture/ontology/step3c-parked-tree-changes.md` (PTC IDs). An open PTC parks every affected row as `blocked` (cannot be defined until the tree pass) or `retired` (will not be defined). Never leave it `pending` — `pending` means queued for authoring. Put the PTC ID in `terminology_notes`. `retired` may keep that citation after the PTC closes; `blocked` may not.

On **Review & authoring**:

- **Blue columns** are read-only hierarchy context: concept identity, level, `breadcrumb`, `parent`, and related taxonomy context.
- **Green columns** are read-only Step 3b APQC cross-check context: `apqc_candidate`, `apqc_description`, `triage`, `apqc_decision`, and `review_notes`.
- **Yellow columns** are reviewer-authoring fields. Phase 1 yellow fields are required before `approved`. Phase 2 yellow fields are optional-but-preferred.
- The finished rows marked `approved` are quality references. Use their structural discipline—not merely their wording—as the standard. The five batch-01 rows (`CM-1-1-2-10/11/12/13`, `CM-1-1-4-7`) are the intake-complete examples; the 15 pre-intake approvals are definition-complete but Phase-1-empty.

## How to work a row

1. **Read the breadcrumb and parent definition first.** A child must fit inside the parent’s scope, be more specific than the parent, and never contradict it.
2. **Read adjacent and plausible sibling concepts.** Define the activity by its primary purpose and establish a material boundary where overlap is credible.
3. **Check the APQC columns.**
   - `adopted` means the APQC item is an approved reference input or mapping decision. It does **not** mean the local definition is complete. Confirm the local definition and scope note are appropriate to this taxonomy.
   - `rejected` means do not reuse the candidate. Read `review_notes` for the documented reason.
   - `review-link` means the item is contextual evidence only—not a local definition, placement decision, or exact semantic match. Use it for ideas, not copying.
4. **Use high-quality external references where helpful.** Prefer primary and authoritative material. Add the source to the **Reference register** first, then cite its `source_id` from `reference_sources`. Reconcile external wording with the taxonomy’s hierarchy and locked boundary decisions. Do not copy source text verbatim.
5. **Work parent-first.** Normally complete L4 concepts before their L5 children, then L6. If a parent is ambiguous, resolve or escalate it before defining its children.
6. **Fill every Phase 1 yellow column.** Fill Phase 2 columns when the evidence supports them; do not invent inputs, outputs, or relations to look complete.
7. **Run the parent test and sibling-boundary test.** If either fails, do not force the row through.
8. **Set `status` to `approved` only when complete and defensible.** Leave it `pending` if any material uncertainty remains and the row is still authorable. Use `blocked` after Hamid parks a row that cannot be defined until its PTC closes. Use `retired` when the node will not be defined (the PTC may still be open). Pending, blocked, and retired rows are never merged.
9. **Return the workbook to Hamid or commit it to a reviewer branch.** Do not overwrite `main` directly. The assistant runs the mechanical validation and a full semantic review before any merge. Every unresolved doubt goes back to Hamid as a question.

## Column by column

| Column | What to write | Ontology / workflow target | Phase |
| --- | --- | --- | --- |
| `definition` | One or two sentences defining what the process **is and does**: its recurring activity and intended outcome. State what it accomplishes, not what it is called. | `skos:definition` (`@en`; required for every approved concept) | Phase 1 — required |
| `scope_note` | A concise statement of what the concept covers plus at least one meaningful boundary. Every approved row requires a non-empty scope note. Explicitly state exclusions and ownership when real ambiguity or overlap exists; do not manufacture boilerplate exclusions. | `skos:scopeNote` (`@en`) | Phase 1 — required |
| `in_scope` | Activities, cases, or outcomes that belong here. These inputs are folded into the final scope note. | Folded into `skos:scopeNote` | Phase 1 — supporting |
| `out_of_scope` | Activities or cases that do not belong here. Name the owning sibling or domain **only when it is already established** in the taxonomy. If the owner is absent, uncertain, cross-cutting, or needs a future concept, document the question in `open_questions`, use `parked_children` / a PTC where appropriate, and leave the row `pending`. | Folded into `skos:scopeNote` | Phase 1 — supporting |
| `alt_labels` | Genuine synonyms, abbreviations, alternate spellings, or established alternate names, separated by ` \| `. Do not add broader, narrower, merely related, or potentially colliding terms. | `skos:altLabel` (`@en`) | Phase 1 — supporting |
| `parked_children` | A genuinely distinct recurring subprocess or capability that merits its own future node, separated by ` \| `. Do not place data fields, systems, documents, policies, KPIs, controls, thresholds, roles, or implementation steps here. Tree *moves* of existing nodes go in `step3c-parked-tree-changes.md`, not here. | Future `skos:narrower` concepts | Phase 1 — supporting |
| `terminology_notes` | Wording and modeling decisions that should not be reopened (for example why “production horizons” is used instead of “run schedules”). Structured questions for Hamid go in `open_questions`, not here. | Editorial note on the authoring record | Phase 1 — supporting |
| `concept_type_check` | Controlled value: `process`, `capability`, `mixed/needs-review`, or `not-process`. | Future `rdf:type` / model-governance classification. Not emitted yet. | Phase 1 — required on new approvals |
| `primary_purpose` | One concise statement of the decision, outcome, or recurring responsibility the concept principally serves. | Candidate property (for example `dpo:primaryPurpose`). Not emitted yet. | Phase 1 — required on new approvals |
| `reference_sources` | One or more `source_id`s from the Reference register, separated by ` \| `. Add a relevance note only where needed. | `dcterms:source`; richer PROV-O later. Register citations are checked now; RDF emission is later. | Phase 1 — required on new approvals |
| `open_questions` | Structured unresolved question (see **When uncertain**). Must be empty on an `approved` row. | `skos:editorialNote` while unresolved; never merged as an assertion | Phase 1 — required when a question exists |
| `key_inputs` | Conceptual business inputs only, separated by ` \| `. No tables, columns, APIs, applications, or files. | Future input relation. Not emitted yet. | Phase 2 — optional-preferred |
| `primary_output` | Principal decision, plan, instruction, record, or outcome produced. | Future output relation. Not emitted yet. | Phase 2 — optional-preferred |
| `related_concepts` | Typed syntax `relation: Canonical Concept Label`, entries separated by ` \| `. Relation from the controlled `relationship_type` list. | Typed relations; `skos:related` only for genuinely associative links. Not emitted yet. | Phase 2 — optional-preferred |
| `responsible_domain` | Canonical taxonomy domain accountable for primary purpose, policy, and decision authority — not necessarily the executor. | Future accountable-owner relation. Not emitted yet. | Phase 2 — optional-preferred |
| `process_horizon` | Controlled value from the Controlled vocabularies sheet. | Future temporal/cadence model. Not emitted yet. | Phase 2 — optional-preferred |
| `status` | `pending` → `approved` when the row passes all checks. `blocked` = parked on an open PTC (or equivalent). `retired` = will not be defined; citation may survive PTC close. Only `approved` rows merge. | Workflow gate for `step3-skos-taxonomy.py --authored` | Workflow |

Provenance on merge: each approved row is merged with `dcterms:source` recording that it is human-authored, approved by Hamid, and dated. Phase 1/2 enrichment fields are **not** emitted as RDF in this step.

## Quality bar

1. **Define, do not label.**
   - Not acceptable: “Refinery Planning is the refinery planning function…”
   - Acceptable: “Develop the commercially optimal refinery production plan by selecting feedstock, operating-mode, throughput, yield, and quality targets within feasible commercial and technical constraints.”
2. **State the primary purpose.** Classify an activity by the decision, outcome, or recurring responsibility it primarily serves—not by the asset, department, application, report, or data source involved. Write that statement in `primary_purpose` as well as embodying it in `definition`.
3. **Bound every concept.** Every approved row must have a non-empty `scope_note` containing at least one meaningful boundary. Use a concise boundary where the concept is naturally narrow; give explicit exclusions and ownership when ambiguity is material.
4. **Pass the parent test.** A child must be a more specific recurring activity inside the parent’s scope. Test it as: “This process is a way of carrying out [parent process].” If that is false, placement or definition requires review. If the row cannot be defined without moving it, open a PTC, set the row `blocked` or `retired`, and put the PTC ID in `terminology_notes`.
5. **Keep siblings disjoint.** Siblings must not claim the same primary activity. If two siblings plausibly overlap, document the boundary question in `open_questions` and keep the row `pending` until Hamid decides.
6. **Use terms consistently.** A material term should mean the same thing throughout the scheme. Reuse approved terminology unless there is a documented reason to introduce a different term.
7. **Park, do not smuggle.** Put a genuinely distinct future process/capability in `parked_children`. Put an accepted-but-unapplied tree move in `step3c-parked-tree-changes.md`. Do not turn a definition into a hidden hierarchy, add unapproved children, or model constraints, thresholds, rules, data objects, systems, or KPIs as process concepts.
8. **Write from evidence and domain knowledge.** Use high-quality references where they improve factual accuracy or boundary clarity. Cite registered `source_id`s. Adapt rather than copy. If the evidence conflicts, is incomplete, or does not settle the taxonomy decision, explain the issue and ask Hamid.
9. **Preserve the planning baseline.** Where the concept is a backcasting or lookback process, compare actuals with the approved plan and its contemporaneous assumptions and constraints—not a later reforecast or hindsight-adjusted baseline.
10. **Do not broaden to hide uncertainty.** A definition that says everything is usually wrong. Keep the primary purpose narrow and make unresolved adjacent responsibilities explicit.

## Locked boundary rules

Follow these decisions. Do not reopen them in ordinary authoring. If a row appears to conflict with a locked rule, record the conflict precisely and ask Hamid.

- **Supply Chain Management** decides what should move, be made, held, or replenished, where and when. **Commercial & Marketing** decides for which customer or market, under what offer, price, contract, or margin objective.
- **Refining** transforms material. **Midstream** receives, stores, transfers, and transports it.
- **Finance** owns financial governance and transactions. Business domains own the operational event that creates the financial effect.
- **Shared Services** is a service-delivery model, not a second Finance, HR, IT, or other functional domain. It executes delegated services; the functional owner retains policy and accountability.
- **EHS & Government Reporting** owns standards, assurance, regulatory reporting, and enterprise coordination of incidents, releases, investigations, corrective actions, and emergency response. Asset and functional owners execute the operational work and assigned corrective actions.
- **Legal & Corporate Communications** covers legal services, legal-risk management, governance support, internal corporate communications, and approved enterprise messaging. Government, investor, public/community, and media relations are out of scope unless separately modeled.
- **Regional Optimization** determines the commercially preferred, feasible regional supply-and-disposition plan. **Supply Chain Management** coordinates broader cross-functional supply-chain planning and feasibility. Operating domains execute the physical work.
- **Regional Backcasting** compares actual regional outcomes with the approved plan and contemporaneous assumptions to explain variance and improve subsequent planning.
- **Refinery Planning** sets the commercially optimal refinery production-plan targets. **Refining** owns detailed unit-operation scheduling, tank/transfer and blend execution, process control, maintenance, turnaround execution, and safe operational departures from plan.
- **Distribution Backcasting** compares distribution actuals with the approved distribution plan and contemporaneous assumptions to explain variance and improve subsequent distribution planning. It does not dispatch equipment or operate terminals and transportation assets.

## When uncertain

Do not guess, invent an owner, infer a constraint, or broaden a definition merely to complete a row. Leave `status` as `pending` and record the issue in `open_questions` using this format:

- **Question:** The exact decision or ambiguity requiring Hamid’s answer.
- **Context:** The current concept, parent, relevant siblings, and any locked boundary rule involved.
- **Options:** The competing interpretations, placements, or boundaries.
- **Evidence:** Relevant APQC context and high-quality sources consulted, summarized rather than copied.
- **Recommendation:** Your recommendation, clearly identified as a recommendation rather than an approved decision.

If the answer is a tree move, add or update a PTC in `step3c-parked-tree-changes.md` and put the PTC ID in `terminology_notes`. Hamid resolves the question before the row can become `approved` or be merged.

## What not to do

- Do not edit `downstream_process_map.json` or the taxonomy `.ttl` directly. The workbook is the authoritative input for this authoring pass. Tree moves go through a PTC, then a later JSON/TTL pass.
- Do not overwrite `main` directly. Return the workbook to Hamid or commit it to a dedicated reviewer branch for review and PR.
- Do not copy APQC or any external source verbatim. Adapt source material to the defined concept and preserve the project’s provenance convention.
- Do not invent `source_id`s or paste free-form URLs into `reference_sources`. Register the source first.
- Do not invent KPIs, thresholds, metrics, system names, data fields, organizational roles, or implementation details inside a definition unless the taxonomy concept itself explicitly requires them.
- Do not create an apparent synonym that is actually a broader, narrower, related, or competing concept.
- Do not mark a row `approved` merely to reduce the queue. `pending` is always the correct status when a material question remains. `mixed/needs-review` and `not-process` cannot be `approved`.
- Do not assume the label, APQC candidate, asset location, or organizational owner alone establishes a concept’s intended meaning. Use hierarchy, definitions, scope, boundaries, evidence, and Hamid’s decisions together.
