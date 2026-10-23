<!-- The decision owner's words, verbatim from the Claude Code session of 2026-10-23 (the ontology's close-out). Context (Claude's words, kept in this comment so they do not enter the quote corpus). The body has 10 blocks, separated by blank lines.
The decision owner said they wanted to close the items waiting on them so the ontology could close. Claude asked the questions with the AskUserQuestion tool, one item at a time, each with options and a recommendation.
Block 1: "How should we settle Q17 so the ontology can close?" Options: 1 "Park until sharing (Recommended)": park Q17 by a recorded decision until the ontology is first shared with business consumers, when the business confirms meanings; 2 "Build the relation now, assign later"; 3 "Assign per module now". The decision owner typed block 1.
Blocks 2 to 4: the three MPC-P10 questions. P10.1 (onboarding): "Add a new L5 (Recommended)", CM 1.3.7.1.7 Coordinate Customer Onboarding under CM 1.3.7.1, Set Up Prospect kept as the card-program case; "Widen Set Up Prospect"; "Change nothing". P10.2 (the Order to Cash credit review's link): "CM 1.3.7.4.2 (Recommended)"; "CM 1.3.7.4.3"; "Leave unlinked". P10.3: "Add Customer Master (Recommended)", on the Marketing & Sales line, produced by CM 1.3.7.1.1; "Don't add it". Block 2 answers P10.1, block 3 P10.2, block 4 P10.3.
Block 5: "Product codes: the PIDX and OEO mappings wait for product values. How should we close this?" Options: "10-K slate in party (Recommended)": product values from the refined-product categories in MPC's FY2025 Form 10-K, each cited, mapped to PIDX product codes by identifier and to OEO fuel classes, in a party minor release; "New Product module"; "Park with the business".
Block 6: "Your answers so far need six releases. None changes a released IRI. Do you approve building and issuing them?" The six: core 2.3.0 (the new L5), value-stream 1.1.0 (the credit review's link, ranges for produces and consumes), data-product 1.1.0 (Customer Master), party 1.1.0 (the 10-K product values with their PIDX and OEO mappings, the lifecycle linked to the new process, and its projection fixes), kpi 1.1.1 (one range) and integration 1.0.1 (its projection fixes). Options: "Approve all six (Recommended)"; "Approve, but ask per tag"; "Not yet". The question undercounted two modules' projection fixes (it said 7 for party and 3 for integration; `projection/pipeline.py` lists 8 and 5); Claude told the decision owner straight after the answer, and the modules and kind of fix are as asked.
Block 7: "Which reviewer should we use for this close-out?" Options: "Keep Codex (Recommended)", with Codex giving the independent review and the Cursor bot the PR verdict; "I'll add Ollama credits".
Block 8: after Claude listed the eight pull requests, the decision owner set the session goal with block 8.
Block 9: later in the session, after the PR reviewer held that the extra fixes had no recorded yes, Claude asked: "Correction to the release approval: party 1.1.0 carries 8 projection fixes (not 7) and integration 1.0.1 carries 5 (not 3). The extra ones: party gets a cardinality shape for `feeds`, and integration gets cardinality shapes for `authority:rank` and `authority:evidenceTier`. Each adds a shape only; none changes a released IRI. Do you approve the releases with 8 and 5?" Options: "Approve 8 and 5 (Recommended)"; "Only the original 7 and 3".
Block 10: later in the session, after research showed PIDX publishes no IRIs and its codes name company-requested traded grades grouped in one-letter families dated 2015, Claude asked how party 1.1.0 should handle PIDX. Options: "Family codes, flagged (Recommended)": each product records its PIDX family letter as a plain identifier, with the PIDX workbook as its source, PIDX's copyright notice and a note that the family list dates from 2015; no IRIs; the close-out package asks the business to confirm the letters with PIDX; "No PIDX now, to the business".
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

I agree with 1. Can we document this as a package to go with the ontology so that we know what to close out with the business.

Add a new L5 (Recommended)

CM 1.3.7.4.2 (Recommended)

Add Customer Master (Recommended)

10-K slate in party (Recommended)

Approve all six (Recommended)

Keep Codex (Recommended)

aligned. keep gooing until the ontology is done after addressing all the outstanding question. stop the goal gracefully when you are completely done

Approve 8 and 5 (Recommended)

Family codes, flagged (Recommended)
