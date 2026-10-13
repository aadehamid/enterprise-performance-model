# Phase 1 sweep: review brief

You are reviewing drafted answers to held relationship rows in the Enterprise Performance Model ontology. Another agent drafted them. Hamid, the ontology owner, approves the final register before anything is built, so your job is to find every answer he should not approve as written.

**Read-only.** Do not edit the answer files or the repository. Write only your two output files, named in your task.

## What to read first

All in this folder:

1. `drafting-guide.md`: the rules the drafters followed, the answer schema, and when to flag. Read the correction note under rule 2: an earlier version gave uses-input and governed-by in the wrong direction. Judge every answer by its `stored_fact` and sentence.
2. `research-mpc.md` (Marathon Petroleum evidence) and `research-industry.md` (peers and industry practice).
3. `rows-<issue>.jsonl`: each row's raw verb, source, candidate targets, hold set, backlog note, and every process's label, definition, scope note and parent.
4. The repository, read-only, at `/Users/hamidadesokan/Dropbox/1_PROJECTS/Enterprise Performance Model/business_architecture/ontology/step4/`:
   - `verb-predicate-mapping-v2.md`: predicate meanings, the canonical direction table, the governed-by emission guard, the triggers rule, the two-cycle rules.
   - `evidence-discipline.md`: affirmative citation and the nearness-only identity rule.
   - `source-workbook-backlog.md`: why each row is held, and Hamid's recorded positions.
   - `review-evidence/hamid-answers/204-batch1.md`, `205-batch1.md`, `205-batch2.md`: Hamid's own answers, as precedent.
   - `canonical-facts.csv`: the facts already stored.
   - `python3 /Users/hamidadesokan/Dropbox/1_PROJECTS/Enterprise\ Performance\ Model/scripts/epm_facts.py row REL-xxxxx` prints any row's status and history.

## Check every answer in your half

1. **Meaning.** Does the stored fact say what is true? `consumer core:dependsOnOutputOf producer`; `governed core:governedBy owner`; `target core:informedBy source` for informs; `target core:enabledBy source` for enables; `target core:triggeredBy source` for triggers. Read both processes' definitions and scope notes. Is the chosen predicate the best fit under the locked meanings in rule 2 of the guide, or does another fit better?
2. **The hold question.** Does the answer resolve the question the row is held for (the guide's rule 1 and the row's backlog note)?
3. **Identity.** For a retarget or a #201 row, is the named target an existing process with that slug, and is it chosen on evidence, not label similarity or nearness?
4. **Hierarchy.** If source and target are parent and child or ancestor and descendant, the answer is no relationship unless the child produces something specific the parent uses.
5. **Recorded positions.** Does any answer contradict something Hamid recorded in the backlog, the mapping document or his answer files? That must be flagged.
6. **Governed-by guard.** A governed-by answer passes only if the governed process applies policy, limits, rules, delegation or criteria that the other process owns.
7. **The sentence.** It names both processes with their slugs, states the relationship plainly, states any condition, and matches the stored fact.
8. **Evidence.** Each cited brief section exists and says what the answer claims. `mpc-sourced` is used only when MPC evidence covers the relationship itself.
9. **Flags.** Should an unflagged answer be flagged, or a flagged one be decided?
10. **Consistency.** Rows with the same pair, or the same pattern, get the same answer across the whole register, including the other half (all `answers-*.jsonl` files are in this folder).

## Output

Write `review-<half>.jsonl`, one object per answer you reviewed, in row order:

```json
{"row_id": "REL-00000", "issue": 201, "agree": true,
 "severity": "none | minor | major",
 "finding": "empty if you agree; otherwise what is wrong, in one to three plain sentences, citing the definition, record or brief you relied on",
 "suggested": "empty, or the answer you would give: verdict, stored_fact, and sentence"}
```

**major** means Hamid should not approve the answer as written: wrong meaning, wrong direction, wrong target, a contradicted record, hierarchy restatement, or a cited source that does not say what is claimed. **minor** means the answer stands but its wording, evidence list or confidence needs a fix.

Then write `review-<half>-summary.md`: counts by severity, the major findings in a list, any pattern you saw across many rows, and anything you could not check.

**Done when** every answer in your half has exactly one review object and the summary's counts match the file.
