# Parked Tree Changes — Downstream Process Ontology

Structural changes that were identified during definition authoring, accepted in principle, and
deliberately **not** applied during a definition-review batch. Each entry stays open until the
consolidated repo-JSON tree pass.

**Why this file exists.** A definition-review batch may not edit `downstream_process_map.json`,
the taxonomy TTL, or build scripts. When a row cannot be defined without first moving it, the
decision is recorded here instead of being resolved silently inside a definition.

**Rules.**

- An entry is closed only by an explicit tree pass, never by a definition batch.
- While an entry is open, every affected row stays `status = pending`.
- An affected row's `terminology_notes` must name its PTC ID so the two never drift apart.
- Closing an entry requires the checklist in that entry to be fully worked, not just the move applied.

| ID | Affected node | Status | Decision | Blocks |
| --- | --- | --- | --- | --- |
| PTC-001 | `CM-1-1-4-6` Commercial Development | Open — accepted, awaiting tree pass | Option A, accepted by Hamid 2026-09-18 | 4 rows |

---

## PTC-001 — Commercial Development does not belong under Refinery Planning

**Raised:** 2026-09-18, review batch 01
**Accepted:** 2026-09-18 by Hamid (Option A)
**Status:** Open — awaiting the consolidated repo-JSON tree pass
**Precedent:** handled the same way as the parked `IT Services` reparenting question recorded on
the approved `CM-1` record, which was likewise deferred rather than churning the tree mid-pass.

### Affected rows

| Slug | Level | Label | Current parent | Current status |
| --- | --- | --- | --- | --- |
| `CM-1-1-4-6` | 4 | Commercial Development | Refinery Planning | `pending`, `concept_type_check = mixed/needs-review` |
| `CM-1-1-4-6-1` | 5 | Develop Strategic Business Plan | Commercial Development | `pending`, untouched |
| `CM-1-1-4-6-2` | 5 | Plan Budgets | Commercial Development | `pending`, untouched |
| `CM-1-1-4-6-3` | 5 | Manage Site Specific Business Risk | Commercial Development | `pending`, untouched |

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

### Open sub-decisions to settle during the tree pass

These were not settled on 2026-09-18 and must be answered before the move is applied:

1. **Where does site/enterprise business planning live?** The L1 domain set has no Strategy node.
   Options: a new strategic-planning node under an existing L1; a site business-planning node
   under Refining as asset owner; or a new enterprise-level branch.
2. **Who owns non-financial, non-EHS site business risk?** Candidate is Refining as asset owner,
   bounded against EHS assurance and Finance. Confirm whether an enterprise risk-management
   capability should exist instead, since the taxonomy currently has none.
3. **Does `Commercial Development` survive anywhere?** Option A retires it. If a genuine site
   commercial business-development process exists, it needs its own definition and placement
   rather than inheriting this node.
4. **Does `Plan Budgets` split?** Confirm whether the operational planning input and the financial
   governance process are one node under Finance or two linked nodes.

### Closure checklist

- [ ] Sub-decisions 1–4 answered and recorded in the Architecture Decision Log.
- [ ] New parent nodes created in `downstream_process_map.json` with slugs assigned.
- [ ] Three L5 children reparented; `CM-1-1-4-6` retired or redefined.
- [ ] Affected workbook rows re-queued for definition authoring under their new parents.
- [ ] `CM-1-1-4-6` row set to `retired`, or given a definition if it survives.
- [ ] Identity map and taxonomy TTL regenerated.
- [ ] PTC-001 marked closed here with the date and decision-log reference.

The full structured question, with options and evidence, is preserved verbatim in the
`open_questions` cell of row `CM-1-1-4-6` in
`business_architecture/ontology/build/output/step3c-definition-authoring-workbook.xlsx`.
