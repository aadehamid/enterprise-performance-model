# Definition Reviewer Instructions — Downstream Process Ontology (Step 3c)

## What this is

We are building a formal ontology (SKOS taxonomy) of our downstream
operations — every business process from L0 (Downstream Operations) down
to L6, 680 concepts in total. 192 already have definitions. **488 do not.**
Your job: write the missing definitions in the workbook, to an
enterprise-grade bar, so they can be merged into the taxonomy.

## The workbook

`step3c-definition-authoring-workbook.xlsx`, sheet **"Review & authoring"**.

- **Blue columns** — read-only context: where the concept sits
  (`breadcrumb`, `parent`), and the Step 3b APQC review (`apqc_candidate`,
  `apqc_description`, `triage`, `apqc_decision`, `review_notes`).
- **Green columns** — read-only review context from the APQC cross-check.
- **Yellow columns** — yours to fill (see below).
- Sheet **"Column guide"** maps every field to its ontology target.

The 15 already-finished rows are marked `approved` — use them as the
quality reference.

## How to work a row

1. **Read the breadcrumb and the parent's definition first.** A child
   must fit inside its parent's scope, never contradict it.
2. **Check the APQC columns.** If `apqc_decision` is `adopted`, the
   definition is done. If `rejected`, do not reuse that candidate — the
   `review_notes` say why. `review-link` means "worth reading for ideas,
   not for copying."
3. **Work level by level** — all L4s before L5s. Parent definitions make
   children's boundaries much easier to draw.
4. **Fill the yellow columns** (column-by-column below).
5. **Set `status` to `approved`** when the row is done. Leave it
   `pending` if you are unsure — a pending row is simply skipped, never
   merged half-baked.
6. **Return the file** to Hamid (or push it to the repo at
   `business_architecture/ontology/build/output/`). The assistant then
   runs a mechanical check plus a full semantic review, and **every
   doubt comes back to you as a question**. Nothing merges until your
   answers resolve them.

## Column by column

| Column | What to write |
|---|---|
| `definition` | 1–2 sentences: what the process **is and does**. Say what it accomplishes, not what it is called. |
| `scope_note` | What it covers, plus the boundary sentences: what it explicitly **excludes**, and which sibling owns the excluded part. |
| `in_scope` | Activities/cases that belong here (feeds the scope note). |
| `out_of_scope` | Activities/cases that do **not** belong here — and who owns them instead. Always name the owner. |
| `alt_labels` | Synonyms / alternate names, separated by `|`. |
| `parked_children` | narrower concepts you notice while defining, separated by `|`. They become new nodes later — don't model them now. |
| `terminology_notes` | Wording decisions (e.g. why "production horizons" not "run schedules") so nobody reopens them. |
| `status` | `pending` → `approved`. Only `approved` rows merge. |

## The quality bar

1. **Define, don't label.** ❌ "Refinery Planning is the refinery
   planning function…" ✅ "Deciding what the refinery should buy, run,
   make, and target for each production horizon, within commercial and
   technical constraints."
2. **Classify by primary purpose, not asset location.** A tank, berth,
   or lab can serve different domains — ask what the *activity* is for.
3. **Bound every definition.** If you can't say what's out of scope,
   the definition isn't finished.
4. **Keep siblings disjoint.** Two siblings must never claim the same
   activity. When in doubt, put the boundary question in
   `terminology_notes` and leave the row `pending`.
5. **Use terms consistently.** The same word means the same thing in
   every row.
6. **Park, don't smuggle.** Future concepts go in `parked_children`;
   limits/thresholds stay out entirely (constraints are a parked module).
7. **Write from domain knowledge.** If you're guessing, say so in
   `terminology_notes` — the review will catch it and ask.

## Boundary rules (locked — follow, don't reopen)

- **Supply Chain Mgmt** decides *what should move, be made, held, or
  replenished, where and when*. **Commercial & Marketing** decides *for
  which customer/market, under what offer, price, contract, or margin*.
- **Refining** transforms material; **Midstream** receives, stores,
  transfers, and transports it.
- **Finance** owns financial governance and transactions; business
  domains own the operational event that creates them.
- **Shared Services** is a delivery model, not a second Finance/HR/IT —
  it executes delegated services; the functional owner keeps policy and
  accountability.
- **EHS** owns standards, assurance, and reporting; asset owners execute
  the work.
- **Legal & Corp Comm** covers legal services plus internal corporate
  communications. Government, investor, and public/media relations are
  out of scope.
- **Backcasting** compares actuals against the *approved plan and its
  contemporaneous assumptions* — never a later reforecast.

## What not to do

- Don't edit `downstream_process_map.json` or the taxonomy `.ttl`
  directly — the workbook is the only input.
- Don't copy APQC text verbatim; adapt it and keep the provenance note.
- Don't invent KPIs, metrics, or system names inside a definition.
- Don't mark a row `approved` to "get through the list" — pending is
  always the safe choice.
