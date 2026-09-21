# Step 3c Workbook Review — Agent Handoff

**Project:** `aadehamid/enterprise-performance-model` — governed downstream oil & gas SKOS process ontology
**Artifact under review:** `business_architecture/ontology/build/output/step3c-definition-authoring-workbook.xlsx` (503 rows)
**Process:** human-in-the-loop batch review with Hamid as sole approver and merger
**State at handoff (post PR #77):** `approved=477 pending=22 blocked=3 retired=1 blocking=0 questions=0 notes=15 open_ptc=1` · reference register last row **57** (`SRC-FASB-ASC326-001`) · batches 1–39 complete, PRs through **#77**

This document is the complete operating manual. A new agent following it can continue the review at the same quality. Everything in it was established by explicit decisions of Hamid's during batches 1–39; where a rule cites "bNN", that is the batch where Hamid locked it.

---

## 1. The core loop (one batch = one cycle)

Every batch follows the same eight steps, in order. **Never skip or reorder.**

1. **Sync main.** `git fetch origin main && git reset --hard origin/main`. Verify the last merged batch landed and nothing else touched the workbook (Hamid sometimes commits unrelated files, and once rewrote history — always inspect `git log` and, if surprised, diff the workbook against your expectation before proceeding).
2. **Scope the batch.** List the target rows from the workbook (slug, level, name, status, APQC candidate/score/triage, review notes). Batches are hierarchy-led and parent-first: an L4 with its L5 children, sized ~5–26 rows. Hamid decides splits ("split batch N as suggested") and merges ("take batch N whole") when you offer options.
3. **Research.** Downstream oil & gas is the frame. Use high-quality sources only: regulators (EPA, FTC, IRS, OFAC, CFPB, Treasury), standards bodies (API, FASB, PCI SSC), statutes (PMPA). Direct fetches to most .gov/standards sites are **egress-blocked** — verify via web-search result metadata, record the access date, and disclose the method ("verified via web search; direct fetch blocked") in the package and register entry.
4. **Deliver the review package in chat — before any workbook edit.** Format in §3. No exceptions: the package is always delivered and approved before a single cell changes.
5. **Wait for Hamid's review.** It always arrives as "approve with refinements." Apply **exactly** his refinements — his quoted wording goes in **verbatim** (see §4). Never silently improve, soften, or extend his text.
6. **Apply on a fresh branch.** `git checkout -B ontology/step3c-review-batch-NN origin/main`. Apply via a Python script (scaffold in §5) that edits **only** the workbook. Run the validation gate; fix any new note before committing (§6).
7. **Cell-diff verify** against HEAD (§7): only the expected rows (and expected register rows) changed; **names untouched**; all sheets, freeze panes, auto-filters, and data validations preserved.
8. **Commit, push, open a draft PR** (§8). **Never merge — Hamid merges.** Report in chat with the PR link, what was applied, the gate line, and what the next batch is. Then wait for "#NN merged" (with or without "continue") and start the next cycle.

---

## 2. Hard constraints (violating any of these is a failed batch)

- **Only the workbook file changes.** Never touch `downstream_process_map.json`, `step3-taxonomy.ttl`, `step2-identity-map.json`, generated reports, or build scripts. The validator writes `step3c-workbook-findings.md` into the cwd — `rm -f` it before committing.
- **Row names mirror the locked taxonomy and are never changed.** Preferred normalized labels go to `alt_labels` (subject to the collision rule, §4.2) and the naming queue (terminology notes + PR body). This holds even when Hamid supplies a "preferred normalized label" — record it, don't rename.
- **PTC rows are untouchable.** `CM-1-1-4-6` (retired) and `CM-1-1-4-6-1/-2/-3` (blocked) must never be redefined, re-parented, or status-changed; PTC-001 stays open (closes only in Step 3d); PTC-002 stays closed.
- **`pending` is never a parking state.** Every row in a batch moves to `approved` on Hamid's sign-off, or stays out of the batch entirely.
- **Approved rows have empty `open_questions`.** Open items go to terminology notes ("OPEN ISSUE" text) and the PR follow-ups section — never into `open_questions`.
- **Controlled vocabulary values must be exact:** `status` ∈ pending|approved|blocked|retired; `concept_type_check` ∈ process|capability|mixed/needs-review|not-process; `process_horizon` ∈ strategic|tactical|monthly|weekly|daily|intraday|event-driven|continuous|periodic|not-applicable|needs-review; relationship types ∈ enables|informed-by|uses-input|produces|constrained-by|governed-by|assures|triggers|requires|precedes|follows. `responsible_domain` is **not** vocabulary-controlled (b15) — free text, including cross-functional forms.
- **Never edit already-approved rows** — even when a new batch's review implies a change to one (e.g., a naming suggestion for an approved row goes to the PR naming queue only, row untouched — b29 AMPM precedent).
- **A quote, plan, forecast, credit, price, or payment is never created by a process that doesn't own it** — the boundary rules in §9 are load-bearing content, not decoration. New rows must be written consistent with them.

---

## 3. The review package format (delivered in chat)

Structure used every batch:

1. **Header + batch overview.** Slugs, row count, what the cluster is in downstream terms, and how it connects to already-locked rules ("this is the receiving end of…"). Confirm baseline state (gate counts) and that main is synced.
2. **A centerpiece rule (usually Q2).** Most batches propose one durable, quotable rule (see §9 catalog). Hamid frequently rewrites it into "canonical wording" — expect that and apply his version verbatim.
3. **Questions Q1–Q6** for his decision, always including:
   - **Q1:** concept types (process vs capability — test in §10), horizons per row, and `responsible_domain` (cross-functional proposal where warranted, §10).
   - Middle Qs: the batch's material boundary questions, each with a concrete proposal (recommend, don't survey).
   - **Last Q:** naming pass (queue + proposed alt labels, §4.2) and the register decision (new source proposed / considered-and-skipped, §4.4).
4. **Full proposed row content** for every row: definition, scope_note (with inherited rules cited by batch number), in_scope, out_of_scope (pipe-separated, with **owner named in parentheses starting with an uppercase word of ≥3 letters** — validator rule, §6), terminology_notes plan, primary_purpose, concept_type + horizon, key_inputs, primary_output, related_concepts (vocabulary types only, locked names only), reference_sources (register IDs only).
5. **Proposed register entries** (if any) with all 9 columns drafted (§4.4).
6. **Closing:** expected gate line after approval, branch name, "draft PR", and what the next batch is.

Style: lead with what matters, cite prior batches by number ("the b14 payment-authority rule"), and keep every proposal decision-ready. Hamid reads closely and corrects wording — precision in the package saves a correction cycle.

---

## 4. Applying Hamid's review

### 4.1 Verbatim rule
Any wording Hamid marks "Use:", "Canonical wording:", "Recommended…", or quotes in a blockquote goes into the workbook **verbatim** (module-level string constants in the apply script, concatenated into scope notes). The terminology note records "review X adopted verbatim". When his wording *replaces* yours (he often corrects over-absolute phrasing — e.g., "never unbilled" → evidence-model wording, "decided here and nowhere else" → delegated-authority model), note the replacement in terminology_notes.

### 4.2 Alt labels and the naming queue (the "b18/b26/b28 lesson")
- The validator checks altLabel-vs-prefLabel collisions **case-insensitively, including against the row's own name**. Therefore: **case-only or punctuation-only** normalizations (capitalization, `&`→`and`, `/`→spacing, `- X`→`(X)`) go to the **queue only — never into `alt_labels`**.
- Word-level rewordings (added/removed/changed words) are collision-safe: record as `alt_labels` **and** queue.
- Check every proposed alt label against all prefLabels in the workbook before applying.
- The naming queue lives in each row's terminology_notes ("recorded as alt label and queued" / "queued, no alt label") and as a table in the PR body.

### 4.3 Vocabulary-missing relations (the b10/b23 precedent)
Hamid sometimes requests relation types not in the vocabulary (`informs`, `governs-change-to`, `may-follow`, `requires: <non-concept>`). Procedure: record his requested relation **verbatim in terminology_notes**, apply the nearest vocabulary term against a **locked row name** (or put `informed-by` on the receiving row if it's still pending; if the receiver is approved, note that it couldn't be added), and flag the substitution in the chat report and PR body. Never invent relation types or reference unauthored/invented target names.

### 4.4 The reference register (need-driven)
- Add a source only when needed. The decision rule Hamid locked: **if a specific statute/standard is named in canonical row text, register it** (Reg B, ASC 606, ASC 326, OFAC, PCI DSS precedents); **if the legal statement is generic/unnamed or jurisdiction-undefined, record it as an open issue and register nothing** (unclaimed-property, consumer-debt precedents).
- Register columns (9): `source_id | organization | title | version_or_date | url_or_identifier | authority_type | permitted_use | relevance | status`. IDs follow `SRC-<ORG>-<TOPIC>-001`. Append after the last populated row (next is **row 58**), assert no duplicate ID.
- `permitted_use` is always scoped: what the source evidences, who owns the determinations it does *not* make ("fact-dependent… determined by <owner>… evidence only; does not determine process ownership or legal conclusions"). Hamid usually tightens this wording — apply his version.
- `version_or_date` records the access date and the verification method ("accessed YYYY-MM-DD (verified via web search; direct fetch blocked from build environment)").

### 4.5 Fact-dependent legal statements
The house pattern (used ~15 times): "Fact-dependent statement: where <condition>, <law/obligation> may apply depending on <facts>; applicability and required procedures are <Legal/Compliance/Tax/Finance>'s determination, and this process operates under the procedures they define." Never state a legal conclusion; always name the determining owner.

---

## 5. The apply script

One script per batch in the scratchpad (`apply_batchNN.py`), all following this scaffold:

```python
from openpyxl import load_workbook
WB = "business_architecture/ontology/build/output/step3c-definition-authoring-workbook.xlsx"
COMMON = {"concept_type_check": "process", "responsible_domain": "Commercial & Marketing",
          "open_questions": "", "parked_children": "", "status": "approved"}
# Verbatim refinement strings as module constants (RULE = "...", etc.), concatenated into scope notes.
ROWS = {"<slug>": {**COMMON, "process_horizon": "...", "definition": "...", "scope_note": "...",
                   "in_scope": "a | b | c", "out_of_scope": "x (Owner) | y (CM-1-2-3)",
                   "alt_labels": "...",  # only when collision-safe
                   "terminology_notes": "Batch NN (YYYY-MM-DD). ...",
                   "primary_purpose": "...", "reference_sources": "SRC-APQC-PCF-001",
                   "key_inputs": "a | b", "primary_output": "...",
                   "related_concepts": "uses-input: <Locked Name> | enables: <Locked Name>"}, ...}
NEW_SOURCES = [[...9 columns...]]  # omit entirely when no register change

def main():
    wb = load_workbook(WB); ws = wb["Review & authoring"]
    hdr = {c.value: i + 1 for i, c in enumerate(ws[1])}
    applied = set()
    for r in range(2, ws.max_row + 1):
        slug = ws.cell(row=r, column=hdr["slug"]).value
        if slug in ROWS:
            assert ws.cell(row=r, column=hdr["status"]).value == "pending", (slug, "not pending")
            for field, value in ROWS[slug].items():
                ws.cell(row=r, column=hdr[field]).value = value if value != "" else None
            applied.add(slug)
    assert not (set(ROWS) - applied)
    # Register append: find header row (col A == "source_id"), last populated row,
    # assert no duplicate source_id, write the 9 columns on the next row.
    wb.save(WB)
```

Conventions: list fields pipe-separated (` | `); terminology_notes open with `Batch NN (date).`; `related_concepts` as `type: Exact Locked Name | ...`; empty string → `None`. Sheet headers (Review & authoring): slug, level, name, breadcrumb, parent, is_stub, apqc_id, apqc_candidate, apqc_description, apqc_score, triage, apqc_decision, review_notes, definition, scope_note, in_scope, out_of_scope, alt_labels, parked_children, terminology_notes, concept_type_check, primary_purpose, reference_sources, open_questions, key_inputs, primary_output, related_concepts, responsible_domain, process_horizon, status.

---

## 6. The validation gate

```
python3 business_architecture/ontology/build/scripts/step3c-workbook-validate.py \
  --workbook business_architecture/ontology/build/output/step3c-definition-authoring-workbook.xlsx
```

**Healthy = `blocking=0 questions=0 notes=15 open_ptc=1`.** The 15 baseline notes are pre-intake `pre-intake-missing-phase-1` rows (CM-1, some L1s) — never grow that set. Delete the emitted `step3c-workbook-findings.md` before committing.

Known checks that bite:
- **`altlabel-collision` (QUESTION):** case-insensitive vs all prefLabels including the row's own name → §4.2 rule.
- **`out-of-scope-owner` (NOTE):** every `out_of_scope` cell needs an owner phrase (`owned by|belongs to|sibling|see |under `) **or** a parenthetical matching `\((CM-[\d-]+|L\d…|[A-Z][^()]{2,})\)` — i.e., a slug or a parenthetical starting with an **uppercase word of 3+ characters**. `(governance owners)` and `(IT)` both fail; `(Finance)`, `(CM-1-3-8-1)`, `(IT / Process Excellence)` pass. This recurred in batches 31, 35, 38 — capitalize owners in every out_of_scope parenthetical.
- If a run comes back `notes=16` (or worse), read the findings file, fix the cell(s), update the apply script to match (so the record stays true), re-run to the clean baseline, **then** commit.

---

## 7. Cell-diff verification (after every apply, before every commit)

```python
# git show HEAD:<workbook path> > scratchpad/wb_headNN.xlsx ; then:
# load old and new; assert sheetnames equal; per sheet assert freeze_panes,
# auto_filter.ref, len(data_validations.dataValidation) equal; collect changed rows;
# assert Review & authoring changed rows == exactly the batch slugs, with the
# name column unchanged on every one; assert Reference register changed rows ==
# exactly the expected new rows (or unchanged); assert every other sheet unchanged.
```

Sheets: `Start Here — Decisions & Phases`, `Review & authoring`, `Column guide`, `Controlled vocabularies`, `Reference register`, `External mappings`. Print a PASS line per sheet; abort on any surprise.

---

## 8. Git and PR mechanics

- **Branch:** `ontology/step3c-review-batch-NN` from `origin/main`, fresh each batch.
- **Commit message:** `Step 3c: review batch NN — <cluster short name>` + a paragraph summarizing what was approved and which review refinements were applied verbatim + the gate line. End every commit with the attribution block the session's system reminder specifies (Co-Authored-By + Claude-Session lines). Never put model identifiers anywhere else in pushed content.
- **Push:** `git push -u origin <branch>`; on network failure retry ×4 with 2/4/8/16s backoff.
- **PR:** created via the GitHub MCP tool (`mcp__github__create_pull_request`, `draft: true` — reload the tool via ToolSearch after MCP reconnects, which happen constantly). Body structure: `⚠️ Do not merge without Hamid's review.` header → batch summary → "Review refinements applied" (bulleted, "verbatim" flagged) → register additions (if any) → naming-queue table → "Standing follow-ups (from Hamid's open questions)" → gate line → "Next: batch NN+1…". End with the generated-with footer + session URL per the system reminder.
- **Never merge, never mark ready-for-review.** Hamid merges and says "#NN merged".
- If remote main was rewritten (happened once — a client-name scrub): reset local main to origin, verify the rewrite didn't touch the workbook, report it to Hamid, continue.

---

## 9. Durable rules catalog (cite these; new rows must be consistent with them)

**Cross-cutting architecture rules (Decision-Log grade, quote by name):**
- **Governed Submission and Stewardship Rule (b31):** accountable processes decide business content; master-data stewardship validates authority/completeness, applies via controlled workflows, effective-dates, versions, preserves lineage, distributes. Submitters never write directly; stewardship never self-authorizes decisions.
- **Billing Integrity Rule (b36):** bills only from validated, linked, governed inputs; corrections only as controlled document events with original-document linkage; nothing edited in place or deleted.
- **Cash Application Integrity Rule (b37):** receipts applied only per remittance evidence and approved rules; every exceptional amount is an owned, aged exception item; a payment alters nothing it pays against.
- **Receivables Resolution Separation Rule (b38):** disputes adjudicate on evidence; collections recover without adjudicating/adjusting/writing off; Finance owns allowances and write-offs; nothing netted, absorbed, or forgiven outside authority.
- **Accounting Execution Rule (b39):** O2C accounting executes under Finance/Tax-approved policy/calendars/delegations; close only with evidenced feeds or a documented Finance-approved exception (compensating control, owner, plan, aging/true-up).
- **Resolution-routing rule (b35):** the service capability owns the *commercial customer-request experience* (intake→closure coordination), answers only from governed data, routes all substance to owning processes; **safety/quality/environmental/security signals escalate immediately** outside normal prioritization; the service record references, never becomes, the incident record.
- **Credit authority rule (b34):** Finance owns appetite/reserves/impairment; Credit decides limits, risk codes, holds, releases, credit-driven closure under policy and delegation; consuming processes apply, never override; exceptions via delegation/escalation.
- **No-self-exception (b28, generalized):** implementers submit to governed controls (Price Master Data, etc.), never deploy into them; nobody waives a control they apply.

**Ownership locks (the "who decides" table):**
- **Finance:** risk appetite, reserves/impairment/write-offs (Bad Debt Allowance), accounting policy/elections, revenue-recognition policy, costing methods, close calendar/sign-off, consolidation, loyalty-liability accounting, valuation (b26 lock excludes transfer/tax/royalty/accounting from commercial valuation).
- **Treasury:** banking/lockbox/acquirer arrangements, payment instruments, funds movement. **b14 payment-authority rule:** commercial processes prepare/validate/submit authorized instructions/requests — never move funds.
- **Tax:** positions, interpretations, filings, taxability rules, transfer-pricing policy; commercial processes apply via governed tax master data and prepare recommendations for Tax approval.
- **Legal/Compliance:** legal determinations everywhere (PMPA franchise remedies — fact-dependent statement, SRC-PMPA-001; Robinson-Patman — b23 wording; ECOA/Reg B; sanctions/AML frameworks with KYC as execution-only; consumer-collection conduct; competition-information rule b21/b23).
- **Credit (b11→b34):** the credit envelope; card limits/order releases/terms eligibility operate within it, never increase it.
- **Security:** card-data controls & PCI scope determination (fact-dependent on data handling/architecture, not branding — b29), access/identity standards, fraud investigation & forensics (program processes detect/respond/escalate only).
- **IT:** platform administration, application security, deployment, integration ops (b31 technical-controls distinction — business owns configuration content).
- **Quality/EHS/Operations:** product disposition, incidents, physical work; **physical operations own custody transfer/measurement evidence** — O2C receives/links/validates/retains, never creates or restates (b33; API MPMS as context only).
- **Marketing rules (b21–b27):** analysis informs, never decides (durable analysis rule); three-layer rule (Analysis→Strategy develops/recommends/maintains approved direction→Execution operationalizes); KPI Store boundary (evidence-layer metrics → candidate KPIs only via KPI Store; no process approves/publishes KPIs); forecast-vs-target-vs-plan glossary (b27, extended b32 revenue plan, b33 order-book forecast — operational signals are non-committal); release-authority rule (execution executes released deliverables, approves nothing); consent/contactability rule (consume, never create; suppression "without undue delay"); personal-data governance statement (b21) on every personal-data row.
- **Channel/partner (b26/b28/b30):** no-implied-obligations (nothing beyond executed agreements); onboarding coordinates through control owners, each retaining its control; quotes carry approved legal status per the legal/contract framework (b32 qualified form); brand rights obtained never granted; provider standards consumed never certified; narrow Commercial Agreement Compliance reading (never an enterprise compliance catch-all); commercial audit is agreement-rights audit, distinct from Internal Audit.

**Splits that keep pairs of rows distinct:** Develop Quote vs Issue Quotes & Renewals (compose vs issue); Manage Contract & Order vs Establish Commercial Terms & Contracts (deal vs framework), with Contract Management (b09, CM-1-2-1-2) keeping the legal/trading contract lifecycle; transaction-time vs compliance-time Determine Taxability (b36/b39); Report Franchise Performance vs the reported-sales audit; case records vs master data (b35); reconciliation "settlement" vs Trading Settlement (b37 terminology guard); royalty-stream administration vs collections execution (b39).

---

## 10. Concept types, horizons, domains

- **Capability test:** children are heterogeneous *concurrent controls* over an ongoing operation → `capability` (Insight & Metrics b21, Licensing & IP b26, Loyalty & Cards b29, Master Data b31, Commercial Terms b32, Credit & Risk b34, Service b35, Receivables Resolution b38, Accounting & Compliance b39). Children form a *lifecycle with variants* → `process` (Order Fulfillment b33, Billing b36, Cash Application b37, Rebates b29). When it's arguable, present both readings with a recommendation — Hamid decides (he flipped b38 to capability, kept b36/b37 process).
- **All capabilities are `continuous`.** Horizon reflects the operating signal: `daily` used sparingly and justified (Sales Pricing b28, Credit Card Transactions b29, order allocation-adjacent rows b33, billing runs b36, receipts/application/reconciliations b37). When Hamid prefers `event-driven` with cycles, record the cycle statement verbatim in the scope note (b33 allocation pattern). "Continuous with periodic cycles within" is a legitimate pattern (b30 inspections).
- **`responsible_domain`:** default `Commercial & Marketing`; cross-functional on L4s where control authority genuinely sits elsewhere, using Hamid's exact framing each time (b26 parenthetical style; b31 long parenthetical; b34+ em-dash style, e.g. `Cross-functional — Finance / Tax / O2C Operations / Legal / Commercial Administration`). Children usually keep Commercial & Marketing as the operating home; the L4 scope note states that placement assigns no single owner.

---

## 11. Remaining work

**Authorable (19 rows):**
- **`CM-1-3-9` — Service & Support (15 rows, 3 L4s):** `-9-1` Service & Support Enablement (L4 + Define Operating Model, Manage Operations, Manage Service Employees, Manage Facilities, Manage Technology, Manage Contact Center); `-9-2` Service & Support Delivery (L4 + Manage Data, Manage Customer, Fulfill Service Event); `-9-3` Service & Support Measurement (L4 + Measure Service Infrastructure, Measure Service Employees, Measure Service Effectiveness). Expect heavy inheritance from b35 (service capability boundaries, resolution routing), b31 (data/records distinctions), b24 (operating model as blueprint), and the KPI Store/measurement rules on the -9-3 rows. Watch generic names ("Manage Data", "Manage Customer") — they need tight downstream-service readings and disambiguating alt labels.
- **`CM-1-3-10` — terminal commercial operations (4 L4s, no children):** Setup and Maintain Customer In Terminal, Process Forecast and Nominations, Manage Allocation, Capture Deal. These border the supply-chain/trading branches: nominations and allocation must respect the SC/logistics boundaries (b33 commercial/physical split, pipeline nomination evidence), Capture Deal must not collide with trading deal capture (b11/b14 territory — differentiate as commercial terminal-sales deal capture or route the question to Hamid), and terminal customer setup is the b28/b31/b34 onboarding/KYC/credit receiving end (loading-authorized party role).
- Batch sizing suggestion: offer 40 = CM-1-3-9 (15 rows), 41 = CM-1-3-10 (4 rows), with the option to take them whole — Hamid decides.

**Held (not yours to author without instruction):**
- `CM-1-1-3-5-3 Process Business Renewal Request` — pending Hamid's business confirmation.
- `L0-downstream-operations`, `L0-enabling-functions` — L0 roots, pending; raise their disposition (author, backfill pass, or leave) with Hamid at the end.
- PTC-001 rows (retired/blocked) — untouchable; PTC-001 closes in Step 3d.
- The 15 pre-intake notes — backfill in a later authored pass, per the validator's own instruction.

**After the last batch (required):** update `business-process-architecture-playbook.md` — append the final batch-log entries, move any new durable rules into its decision log, and regenerate the source-to-process traceability appendix (`python3 business_architecture/ontology/build/scripts/step3c-source-traceability.py`) so it reflects the finished workbook. Then: the naming-pass queue (accumulated in terminology notes and PR bodies), the open-issue log (location master-data child, unclaimed-property jurisdictions, consent-data ownership, etc. — all recorded in PR follow-up sections), and Step 3d (PTC resolution) are the known next workstreams — Hamid directs them.

---

## 12. Working relationship notes

- Hamid's reviews are long, structured, and authoritative: an outcome line, per-question rulings ("Approve with…"), verbatim wording blocks, an "Artifact Update Block" at the end. The Artifact Update Block lists artifacts (decision logs, glossaries) that are **out of scope** — only the workbook changes; acknowledge once that their substance is captured in PR follow-ups.
- His messages sometimes duplicate (the same review sent twice) — check whether it's already applied before re-applying anything.
- When he corrects you (over-absolute wording, wrong classification, missing boundary), apply the correction verbatim, name it in the terminology note and PR ("review X adopted verbatim, replacing …"), and carry the corrected pattern forward to future batches — corrections are precedents.
- Report format after applying: PR link first, then what was applied (his refinements named), the verification (gate line + cell-diff), any wrinkle honestly (validator note fixed, MCP reconnects, history rewrite), and what's next. Concise, complete sentences, no invented shorthand.
- Everything is evidence-first: if you didn't verify it (search, workbook read, gate run), don't claim it.
