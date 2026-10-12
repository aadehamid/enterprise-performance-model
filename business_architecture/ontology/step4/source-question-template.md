# Source-author questions for a Phase 1 batch

How to ask Hamid, as source author, about a batch of held rows, so that each answer maps straight onto a verdict. Learned in #205: batch 1 offered yes/no on a whole-process sequence, Hamid answered with scoped sequences, and #225 needed a redo; batch 2 used the three answers below and went through in one pass.

## Before posting

- **Read each row's facts from the files, not from memory.** Verb, source and target slugs and labels: `target-report/target-dispositions-v2.csv`. The scope-note wording: the Step 3c workbook. The hold reason: the batch's routes or review file.
- **Check the hierarchy before describing it.** Read `skos:broader` in `build/output/step3-taxonomy.ttl`. A target can be the source's parent, an ancestor further up, or unrelated; say which (PR #228 called an ancestor "its own parent").
- **Put the sentence where the evidence rule reads it:** the scope note of the row's workbook source. For a `follows` row, that is the process that follows.

## The answers to offer

Phrase each question as the predicate's locked definition, then offer every answer the ontology can store. For `core:precedes`:

- **(a) Whole-process order.** The earlier process finishes before the later one starts. Show the sentence you would add. The row emits.
- **(b) Scoped order.** The order holds per trade, cycle, period, item or version, or only under a condition. Hamid gives the wording. The sentence goes into the scope note, and the row gets an APPROVE verdict as a scoped sequence: add it to `scoped-sequence/scoped-sequences.csv` with a scope unit from the existing list (EPM-DEC-001-0026, Q17). `build.py` ties every row to an approved source and today reads only the #226 summary and the #205 batches, so extend its `approvals()` to read the new batch's review file and saved answer in the same PR. If no scope unit fits, or the answer does not fit the scoped-sequence definition, ask Hamid for a design round instead.
- **(c) No sequence.** The row stays held with that reason and counts as done.

Ask for one line per question (`1: a`, `2: b — <wording>`, `3: c`).

## Posting and recording

- **Label every comment you post through Hamid's account.** Open it with "Posted by Claude:" so he can tell your questions from his answers.
- **Save his answer verbatim** in `review-evidence/hamid-answers/<issue>-<batch>.md`, with the source URL in the header comment. If his comment did not save and he gives the answer in a session, post it word for word with an attribution line, and leave that line out of the saved file.
- **Quote only what the saved file says.** `scripts/epm_facts.py quotes` (run by `check.sh`) checks, word for word and with punctuation, against all saved answers together:
  - in each review file with a `hamid_words` column: that column (blank fails), `scope_note_sentence`, and each quoted span in `semantic_reason` and `Hamid_decision`. An ellipsis (…) splits a span, and only parts of three or more words are checked;
  - every block quote in `source-workbook-backlog.md`, as a CommonMark parser reads it (including quotes nested in lists);
  - each quoted span in the "Hamid's recorded words" section of EPM-DEC-001 records from 0026 on. A Decided record there must quote at least one span of three or more words in visible text (HTML comments are not read), and may have only one such section. Records 0001 to 0025 quote sessions that were never saved and are not checked.

  So give each batch's review file a `hamid_words` column, or nothing in it is checked. It does not check paraphrases, quoted parts of one or two words, quotes outside a decision record's recorded-words section, the ledger or the worklog, or that a quote comes from the comment its row cites: state no more than his answer says, and cite the right comment.
