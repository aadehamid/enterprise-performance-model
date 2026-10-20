<!-- The decision owner's words, verbatim from the Claude Code session of 2026-10-20. Context (Claude's words, kept in this comment so they do not enter the quote corpus): Block 1 is their message after Claude explained that admin merges still need the PR reviewer's MERGE. Then every Cursor check on PR #313's new head failed to start with "Your on-demand usage limit was reached". Asked who should give the PR verdict, the decision owner typed block 2. The Cursor agent CLI on Grok 4.7 then replied "You're out of usage. Switch to Auto, or ask your admin to increase your limit to continue."; asked again, they chose block 3, as the tool returned it. Claude Code's safety check then refused to merge on a verdict posted from the decision owner's account; asked how to proceed, they chose block 4 and then block 5, as the tool returned them, and added the two permission rules. Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

But cursor still ask to merge. correct? that is important that cursor finds no issue

Use cursor agent cli with GROK 4.7 as the reviwer.

Cursor CLI on Auto

Allow the merge script (Recommended)

Allow me to post reviews (Recommended)
