# Source-author questions for a Phase 1 batch

How to ask the decision owner, as source author, about a batch of held rows, so that each answer maps straight onto a verdict. Learned in #205: batch 1 offered yes/no on a whole-process sequence, the decision owner answered with scoped sequences, and #225 needed a redo; batch 2 used the three answers below and went through in one pass.

## Before posting

- **Read each row's facts from the files, not from memory.** Verb, source and target slugs and labels: `target-report/target-dispositions-v2.csv`. The scope-note wording: the Step 3c workbook. The hold reason: the batch's routes or review file.
- **Check the hierarchy before describing it.** Read `skos:broader` in `build/output/step3-taxonomy.ttl`. A target can be the source's parent, an ancestor further up, or unrelated; say which (PR #228 called an ancestor "its own parent").
- **Put the sentence where the evidence rule reads it:** the scope note of the row's workbook source. For a `follows` row, that is the process that follows.

## The answers to offer

Phrase each question as the predicate's locked definition, then offer every answer the ontology can store. For `core:precedes`:

- **(a) Whole-process order.** The earlier process finishes before the later one starts. Show the sentence you would add. The row emits.
- **(b) Scoped order.** The order holds per trade, cycle, period, item or version, or only under a condition. The decision owner gives the wording. The sentence goes into the scope note, and the row gets an APPROVE verdict as a scoped sequence: add it to `scoped-sequence/scoped-sequences.csv` with a scope unit from the existing list (EPM-DEC-001-0026, Q17). `build.py` ties every row to an approved source and today reads only the #226 summary and the #205 batches, so extend its `approvals()` to read the new batch's review file and saved answer in the same PR. If no scope unit fits, or the answer does not fit the scoped-sequence definition, ask the decision owner for a design round instead.
- **(c) No sequence.** The row stays held with that reason and counts as done.

Ask for one line per question (`1: a`, `2: b — <wording>`, `3: c`).

## Posting and recording

- **Label every comment you post through the decision owner's account.** Open it with "Posted by Claude:" so they can tell your questions from their answers.
- **Save their answer verbatim** in `review-evidence/decision-owner-answers/<issue>-<batch>.md`, with the source in the header comment as a URN, `verbatim from urn:epm:issue:<issue>:comment:<comment id>` (a GitHub URL carries the account name, which `epm_facts.py names` rejects; EPM-DEC-001-0049). If their comment did not save and they give the answer in a session, post it word for word with an attribution line, and leave that line out of the saved file.
- **Quote only what the saved file says.** `scripts/epm_facts.py quotes` (run by `check.sh`) checks, word for word and with punctuation, against all saved answers together:
  - in each review file with an `owner_words` column: that column (blank fails), `scope_note_sentence`, and each quoted span in `semantic_reason` and `owner_decision`. An ellipsis (…) splits a span, and only parts of three or more words are checked;
  - every block quote in `source-workbook-backlog.md`, as a CommonMark parser reads it (including quotes nested in lists);
  - each quoted span (in double quotes, straight or curly) and each block-quote paragraph in the "The decision owner's recorded words" section of EPM-DEC-001 records from 0026 on. Text in single quotes is not read as a quote, so quote the decision owner with double quotes or a block quote. Quotes are compared as displayed text (emphasis markers dropped) with the saved answers rendered the same way, and a quote must fall inside one paragraph, heading, list item or code block of an answer, as whole words: a quote's first and last words may differ from the saved text only by punctuation outside them, so quote a whole token ("workers’", "Q1(approve") rather than part of it. A saved answer block that contains raw HTML or an image cannot be quoted from. A Decided record there must quote at least one span of three or more words, the record may have only one such section and exactly one Status row in its table, and raw HTML, an image or an invisible format character (such as a zero-width space) anywhere in the record is reported: write checked records in plain Markdown. Records 0001 to 0025 quote sessions that were never saved and are not checked.

  So give each batch's review file an `owner_words` column, or nothing in it is checked. It does not check paraphrases, quoted parts of one or two words, quotes outside a decision record's recorded-words section, the ledger or the worklog, or that a quote comes from the comment its row cites: state no more than their answer says, and cite the right comment.
