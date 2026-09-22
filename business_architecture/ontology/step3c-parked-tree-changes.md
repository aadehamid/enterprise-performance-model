# Parked Tree Changes — Downstream Process Ontology

Structural changes that were identified during definition authoring, accepted in principle, and
deliberately **not** applied during a definition-review batch. Each entry stays open until the
consolidated repo-JSON tree pass.

**Why this file exists.** A definition-review batch may not edit `downstream_process_map.json`,
the taxonomy TTL, or build scripts. When a row cannot be defined without first moving it, the
decision is recorded here instead of being resolved silently inside a definition.

**Rules.**

- An entry is closed only by an explicit tree pass, never by a definition batch.
- A row that cannot be defined until its entry closes is `blocked`; a row that will not be defined
  at all is `retired`. Neither is left `pending`, because `pending` means queued for authoring and
  these rows are not. *(Amended 2026-09-18; the earlier rule kept them `pending`, which hid four
  unworkable rows inside the authoring queue.)*
- An affected row's `terminology_notes` must name its PTC ID so the two never drift apart.
- Closing an entry requires the checklist in that entry to be fully worked, not just the move applied.

**This register is enforced, not advisory.** `step3c-workbook-validate.py` reads this file on every
run and fails the gate when the two drift: a `blocked` or `retired` row that names no PTC, a row
citing a PTC that does not exist here, a `blocked` row still parked against an entry recorded as
Closed (`retired` may keep the citation as provenance), or an
open entry that no row cites. The gate also refuses to let the definition queue reach zero while any
entry is open — finding `step-3c-not-complete` — so Step 3c cannot be declared finished with a tree
change outstanding. The open count prints in the gate's summary line, which lands in every batch PR
body. See playbook §3, Step 3d.

| ID | Affected node | Status | Decision | Rows parked |
| --- | --- | --- | --- | --- |
| PTC-001 | `CM-1-1-4-6` Commercial Development | Open — partially resolved 2026-09-21 (PTC-001-B sub-decision open) | Option A, accepted by Hamid 2026-09-18; sub-decisions settled 2026-09-18; partial-resolution proposal approved by Hamid 2026-09-21 | 2 (1 retired tombstone, 1 blocked) |
| PTC-002 | `CM-1-2-5-2-3` Plan Optimal Feedstock Slate And Run Rate | **Closed** 2026-09-18 — no tree change required | Option 1, accepted by Hamid | 0 |

---

## PTC-001 — Commercial Development does not belong under Refinery Planning

**Raised:** 2026-09-18, review batch 01
**Accepted:** 2026-09-18 by Hamid (Option A); sub-decisions 1–4 settled 2026-09-18
**Status:** Open — partially resolved 2026-09-21 (tree pass executed; PTC-001-B strategy-ownership sub-decision open)
**Precedent:** handled the same way as the parked `IT Services` reparenting question recorded on
the approved `CM-1` record, which was likewise deferred rather than churning the tree mid-pass.

### Partial resolution — executed 2026-09-21

Hamid approved the revised consolidated proposal (`ptc-001-tree-proposal.md`,
four review adjustments adopted):

| Slug | Resolution |
| --- | --- |
| `CM-1-1-4-6-2` Plan Budgets | Reparented to new L2 **Financial Planning and Performance Management** under Finance (`L2-financial-planning-and-performance-management`); level 5 → 3; workbook `blocked` → `pending` → `approved` (PR #87, 2026-09-21) |
| `CM-1-1-4-6-3` → **Coordinate Site Business Risk Management** | Reparented to new L2 **Refinery Performance and Risk Coordination** under Refining (`L2-refinery-performance-and-risk-coordination`); renamed (prior name kept as altLabel); level 5 → 3; workbook `blocked` → `pending` → `approved` (PR #87, 2026-09-21) |
| `CM-1-1-4-6` Commercial Development | Tombstoned as `owl:deprecated` (kept in JSON/identity map/TTL, removed from active navigation); workbook stays `retired` |
| `CM-1-1-4-6-1` Develop Strategic Business Plan | Stays `blocked` under **PTC-001-B** (below); kept as the tombstone's child so the blocked row is never orphaned |

Deviations from the proposal's §7, recorded: the tombstone keeps its one parked child
(proposal said "no children") — this is the orphan-safe reading of the reviewer's
"keep its parent" option, and preserves the blocked row's historical traceability until
PTC-001-B rehomes it. The two new L2s were Candidate architecture nodes: structurally
approved via the proposal, and definition-authored as `approved` workbook rows via
PR #87 (2026-09-21) — hybrid risk cadence and capability-level performance-oversight
notes included per the independent review.

### PTC-001-B — Strategy-ownership decision (open)

**Question:** Is enterprise strategic-business planning owned by
(A) Corporate Planning within Finance,
(B) Corporate Strategy / Corporate Development, or
(C) an executive cross-functional governance process?

**Evidence required:** operating model, executive/Board planning calendar,
delegated authority, corporate-planning charter, current planning artifacts.

**Constraint:** no new Strategy L1 without a charter-level decision (sub-decision 1,
2026-09-18, stands). Do not place the row under Finance as a side effect.

**Blocked row:** `CM-1-1-4-6-1` Develop Strategic Business Plan (workbook `blocked`,
terminology_notes cites PTC-001-B; the gate resolves the citation to PTC-001, which
remains open until PTC-001-B closes).

**Hold confirmed 2026-09-22 (Hamid):** PTC-001-B is an intentional governance
hold, not incomplete work — Step 3d closed with this exception. The row stays
`blocked` under the tombstone so it is never orphaned. Do not place it under
Finance as a side effect; no Strategy L1 without a charter-level decision.
Review trigger: strategy operating-model definition, corporate-planning charter
approval, or enterprise architecture/charter revision.

### Affected rows (post-tree-pass, 2026-09-21)

| Slug | Level | Label | Current parent | Current status |
| --- | --- | --- | --- | --- |
| `CM-1-1-4-6` | 4 | Commercial Development | Refinery Planning | `retired` (owl:deprecated tombstone) |
| `CM-1-1-4-6-1` | 5 | Develop Strategic Business Plan | Commercial Development (tombstone) | `blocked`, PTC-001-B |
| `CM-1-1-4-6-2` | 3 | Plan Budgets | Financial Planning and Performance Management (Finance) | `pending` |
| `CM-1-1-4-6-3` | 3 | Coordinate Site Business Risk Management | Refinery Performance and Risk Coordination (Refining) | `pending` |
| `L2-financial-planning-and-performance-management` | 2 | Financial Planning and Performance Management | Finance | `pending` (Candidate) |
| `L2-refinery-performance-and-risk-coordination` | 2 | Refinery Performance and Risk Coordination | Refining | `pending` (Candidate) |

### Affected rows (pre-tree-pass, 2026-09-18) — historical

| Slug | Level | Label | Current parent | Current status |
| --- | --- | --- | --- | --- |
| `CM-1-1-4-6` | 4 | Commercial Development | Refinery Planning | `retired`, `not-process` |
| `CM-1-1-4-6-1` | 5 | Develop Strategic Business Plan | Commercial Development | `blocked`, destination undecided |
| `CM-1-1-4-6-2` | 5 | Plan Budgets | Commercial Development | `blocked`, destination Finance |
| `CM-1-1-4-6-3` | 5 | Manage Site Specific Business Risk | Commercial Development | `blocked`, destination undecided |

Statuses set 2026-09-18. `retired` here means "will not be defined", not "removed from the tree" —
all four nodes are still present in `downstream_process_map.json` until the Step 3d tree pass.

### The problem

`CM-1-1-4` Refinery Planning is approved as the commercially optimal refinery production plan —
crude slate, throughput, yield, and specification targets on a monthly horizon. None of the three
L5 children under Commercial Development is a refinery production-planning activity:

- **Plan Budgets** contradicts the locked rule that Finance owns financial governance.
- **Develop Strategic Business Plan** is a strategic-horizon activity inside a monthly
  production-planning branch.
- **Manage Site Specific Business Risk** has no owner in the current tree. The only risk nodes are
  Credit Risk and Market Risk under Supply And Trading, and EHS owns EHS risk only.

The parent node itself carries no local meaning. Its label came through Step 3b as a WEAK /
REVIEW LINK match against the APQC element "Manage employee development."

Defining `CM-1-1-4-6` in place would silently endorse budgeting and strategic planning under
Refinery Planning. That is why no definition was authored.

### Accepted decision — Option A

1. Retire `Commercial Development` as a child of `Refinery Planning`.
2. Reparent `Plan Budgets` to **Finance**, with Refining supplying the operational basis.
3. Create a new home outside Planning & Scheduling for `Develop Strategic Business Plan`.
4. Create a new home outside Planning & Scheduling for `Manage Site Specific Business Risk`.

Steps 3 and 4 require **new nodes** — this is why the change cannot be a simple move. Two of the
three children have no destination in the current tree.

### Why Option A is not executable as written

Verified against `downstream_process_map.json` 2026-09-18. Only **Commercial & Marketing** is
decomposed — Planning & Scheduling (7), Supply And Trading (7), Marketing (10) — and 492 of the 503
workbook rows sit under it. Finance, Refining, Midstream, Supply Chain Mgmt., Shared Services,
Process Excellence & IT, Human Resources, Legal & Corp Comm, and EHS & Gov Reporting each have **no
children at all**. There is no destination node for any of the three L5 children, including the
reparenting of `Plan Budgets` to Finance, which reads like a simple move but is not.

This makes the tree pass larger than moving three nodes: it requires decomposing at least one
undecomposed L1 far enough to give them a parent. Recorded here so the scope is not rediscovered.

### Sub-decisions — settled 2026-09-18

1. **Where does site/enterprise business planning live?** *Undecided, deliberately.* No new Strategy
   L1 — the ten L1 definitions are approved baseline and changing the L1 set is a charter-level
   decision, not an ontology-batch one. `Develop Strategic Business Plan` stays unplaced until the
   L1 question is taken up on its own terms.
2. **Who owns non-financial, non-EHS site business risk?** *Undecided, deliberately.* Refining is
   the sensible owner as asset owner, but Refining is undecomposed. Confirmed that the taxonomy has
   no enterprise risk capability anywhere: the only risk nodes are credit, market, and inventory
   risk, all inside Supply And Trading, and EHS owns EHS risk only. Whether that capability should
   exist is a domain-architecture question, carried forward into the tree pass.
3. **Does `Commercial Development` survive anywhere?** **No — retired.** No local meaning, WEAK APQC
   provenance against "Manage employee development," and all children leave. If a genuine site
   commercial business-development process exists, it gets its own node and definition rather than
   inheriting this one.
4. **Does `Plan Budgets` split?** **No — one node under Finance.** The refinery's operational input
   to budgeting is already carried by the Refinery Optimization case basis (`CM-1-1-4-7-1` to `-6`)
   and the Refinery Planning outputs approved in batch 02. A second node would duplicate that work.

Sub-decisions 1 and 2 stay open by choice, not by neglect: both are larger than this entry, and
forcing them here would set domain architecture as a side effect of a definition batch.

### Closure checklist

- [x] Sub-decisions 3 and 4 answered (2026-09-18). 1 and 2 deliberately deferred as L1/domain-set
      questions — record them in the Architecture Decision Log when that artifact exists.
- [x] New parent nodes created in `downstream_process_map.json` with slugs assigned (2026-09-21:
      `L2-financial-planning-and-performance-management` under Finance,
      `L2-refinery-performance-and-risk-coordination` under Refining).
- [x] Two L5 children reparented (2026-09-21); `CM-1-1-4-6` tombstoned as `owl:deprecated`
      rather than removed — deletion would orphan the still-blocked `CM-1-1-4-6-1`, whose slug
      encodes that parentage. The tombstone keeps the parked child until PTC-001-B rehomes it.
- [x] Affected workbook rows re-queued for definition authoring under their new parents (2026-09-21:
      `CM-1-1-4-6-2` and `CM-1-1-4-6-3` `blocked` → `pending`; two new Candidate L2 rows appended).
- [x] `CM-1-1-4-6` row set to `retired` (2026-09-18) — it does not survive, so no definition is owed.
- [ ] Identity map and taxonomy TTL regenerated.
- [x] Two currently undecomposed L1s decomposed one level to host the moved children (Finance,
      Refining — minimal Candidate branches, 2026-09-21).
- [ ] PTC-001 marked closed here with the date and decision-log reference — **waiting on PTC-001-B**.
- [x] Parked row statuses lifted from `blocked` to `pending` as each child got a real parent
      (2026-09-21). `CM-1-1-4-6-1` stays `blocked` against the still-open entry, citing PTC-001-B.
      `CM-1-1-4-6` stays `retired` and keeps the PTC-001 citation as provenance.

The full structured question, with options and evidence, is preserved verbatim in the
`open_questions` cell of row `CM-1-1-4-6` in
`business_architecture/ontology/build/output/step3c-definition-authoring-workbook.xlsx`.

---

## PTC-002 — Slate and run-rate planning appears in two branches

**Raised:** 2026-09-18, review batch 02
**Status:** **Closed** 2026-09-18 — Option 1 accepted by Hamid, no tree change required
**Decided by:** Hamid

### Affected rows

| Slug | Level | Label | Branch | Current status |
| --- | --- | --- | --- | --- |
| `CM-1-2-5-2-3` | 5 | Recommend Feedstock Slate And Run Rate | Supply And Trading > Crude/Feed Demand Management | `executed` 2026-09-21 — renamed from `Plan Optimal Feedstock Slate And Run Rate` (PR #89); the PTC-002 decide-vs-advise boundary (Refinery Planning decides, S&T recommends) is preserved and recorded in `terminology_notes` |

### The problem

`CM-1-1-4` Refinery Planning is approved as owning the commercially optimal refinery production
plan, explicitly including crude slate and throughput targets. On its label, `CM-1-2-5-2-3` claims
the same two decisions from inside Supply And Trading.

This is not the locked SCM-versus-Commercial boundary, and it is not resolved by it. Both nodes sit
inside Commercial & Marketing. The question is which branch decides slate and run rate, and what
the other one does instead.

### Why it was not resolved in batch 02

Batch 02 defined `CM-1-1-4-7-2 Evaluate Crude & Feedstock` bounded strictly as evaluation —
assessing suitability and economic value — with slate approval left explicitly with Refinery
Planning. That definition holds whichever way PTC-002 is decided, so the batch did not need the
answer. Reconciling the two nodes is a tree change and out of scope for a definition batch.

### Options

1. **Refinery Planning decides; Supply And Trading advises.** `CM-1-2-5-2-3` is redefined as the
   trading-side recommendation of an economically attractive feedstock slate, feeding the plan but
   not setting it. Smallest change, no move.
2. **Retire `CM-1-2-5-2-3` as a duplicate.** Its intent is already carried by `CM-1-1-4-7-2` plus
   `CM-1-1-4-7` Refinery Optimization.
3. **Split by horizon.** Supply And Trading plans the forward-quarter indicative slate for
   procurement; Refinery Planning sets the binding monthly plan. Requires both definitions to state
   the horizon boundary explicitly, or the overlap returns.

### Decision — Option 1, accepted 2026-09-18

**Refinery Planning decides; Supply And Trading advises.** `CM-1-1-4` sets the binding crude slate
and run rate. `CM-1-2-5-2-3` is the trading-side recommendation of an economically attractive
feedstock slate and run rate, feeding the plan without setting it. It preserves the locked Refinery
Planning accountability, keeps a trading activity that genuinely exists, and moves no node.

Option 2 was rejected because the trading-side recommendation is real work that would lose its home.
Option 3 was rejected because a horizon split only holds if both definitions restate it, and the
overlap returns the moment one is reworded.

Because no node moves, this entry needed no tree pass and is closed here. What survives is a
**definition constraint**, recorded in `terminology_notes` on `CM-1-2-5-2-3`: whoever authors that
row must scope it as advisory and must not claim the slate or throughput decision. The row stays
`pending` — it belongs to the Supply And Trading cluster and gets its definition in that batch.

### Closure checklist

- [x] Option chosen (Option 1, 2026-09-18). Record in the Architecture Decision Log when that
      artifact exists.
- [x] `CM-1-2-5-2-3` re-scoped: advisory boundary written into `terminology_notes` as a binding
      constraint on its future definition.
- [x] Horizon boundary — not applicable, Option 3 not chosen.
- [x] `terminology_notes` on `CM-1-1-4-7-2` updated to point at the resolution.
- [x] PTC-002 marked closed here, 2026-09-18.
