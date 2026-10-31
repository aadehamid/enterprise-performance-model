<!-- The decision owner's words, verbatim from the Claude Code session of 2026-10-31, as the local release plan (release-cut/PLAN.md, gitignored) preserved them: the plan kept the sentences it quotes, not every message whole, so some blocks are the quoted sentences of one message. Context (Claude's words, kept in this comment so they do not enter the quote corpus).
Block 1: the request. The decision owner asked for a release of the ontology and demo to share with colleagues outside the build, and listed what it must contain.
Block 2: what the release must do for its readers, and the branch they want.
Block 3: the validation after the cut.
Block 4: the seven points Claude put to the decision owner after the first scan, answered in order: the term "decision owner"; internal documents and systems; an option to remove them; claims resting on peers; the name LSC; namespace approval; names in the graph; and the quotes.
Block 5: asked what "--" meant, the decision owner said it was the graph's long separator (vs__Stage), not an em dash in prose.
Block 6: all links go through the latest release.
Block 7: the decision owner accepted every recommendation in the plan's "Decisions" list.
Block 8: the work to do after the first release (the technical graph module, lineage, the in-sync plan), and the viewer.
Block 9: later the same day, the decision owner replaced the statement that the first release goes to colleagues.
Block 10: the technical graph and Databricks.
Block 11: the ontology viewer.
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

I plan to cut a release that I can share with my colleagues who were not part of this process.

the latest from each module release and the release before the latest

I dont want any mention of this repo or my name.

termed industry view or something like that

Essentially all refrences are valid except for peers, which we wil call industry view or best practices.

all of the business process in json, the final version

all of the scripts used either to build or validate

the demos and all of its code

a copy of my personal agent skills, eg ontology, ontology t lpg, clear writing, playbboks - ontology and projections

the docs with all the chnages made above

must be able to do everything we have done here as the ntology and demo goes.

an prropriatley names release branch that I can zip and share with others and that we can always update if we add anything new in main.

The most important thing is the validation after cut. itMUST WORK like it didi when we did this from main. We must test EVERYTHIN and delet the data created to test it when we are done.

decsions owner means an SME. I think we can leave it if the changes to a subject matter extert is too big of a work.

internal documents and is fine and we can leave the files.

We shuld add a line in the release plan with an option to also remove the internal files and systems. So that anyone buiding this can choose. of course anything that will change if we want to remove this internal docs and systems muts be shared for review first if we choose the latter route.

claims resting on peers stay in, but must be presentend as both industry standard and analysis of publickly available filings from peers - U.S refiners

the LSC that we use bith in the namespaces and others should be MPC instead. Let us add that to th release cut

namespaces will be reviewed and approve by the Data, Analtyics, and Insight team. This will only be in the release part. main stays the same as the original from which we can cut relleases.

make sure to use imsple normal underscore between names in the tripple instaed of the em dashes. em dashess "--" should never be used in the graph or anywahere in the release. for exmaple "vs__Stage" should be ""vs_Stage""

couch the quote as coming from an SME that is reviewing the documents

the loonger version of the separartor was what I meant i ddi not know how to show it so i used "--"

let us also make sure that the ontology that we will cut all links must be through the latest release. The release before that is just to demonstarte that we release ontology in releases.

i agree with all yur recoommendation in the release cut

yes, build it after the first release. I will do them once we confirm the release, and then cut another release. The complete first release must go to the coleagues. Please, add all of them to the plan to do after the first release cut. we wll then do a follow up release once we take care of the other ontology work with another release to make it complete fully.

let us leave OPEN_ITEM.md out of this plan for now. it will be handled sepaately. By the way when I finish with (1) I will not share with coleague until I complete all of theother tasks and do another release to update the previous one to a full version. It is then that I will share with colleague as a complete picture.

the technical graph should not be projected to Databricks since databrick already have technical graph in delta table

when we have completed the full release of the ontology we should use https://github.com/morluto/rea to create an ontology viewer like https://openenergyplatform.org/viewer/oeo/ to view our ontology using https://github.com/leonxlnx/taste-skill

The veiwer is where most people will go to review the ontology

The viewer should be built on one ontology release only.

<!-- Later on 2026-10-31, the grill of what the step 1 inventory found that the plan did not settle. Context (Claude's words). Claude asked whether to run the rest of the plan as one goal; the decision owner asked for the grill first and added that the 21 use cases need not be tested (block 12). The questions and options, as put (Markdown stripped), with the recommended option first:
Block 13. Open point 1 of 11. "Every release manifest has an approval block naming an answers file and quoting you, and each core module's Turtle cites the answers file. The answers folder does not ship. What should the release's packages say?" Options: 1 "SME attribution, file out, words kept (Recommended)": approval.who becomes "a subject matter expert reviewing the documents", the file name comes out, your words stay; core's citations read "EPM-DEC-001-0044; approved by a subject matter expert reviewing the documents on 2026-10-18". 2 "Drop the approval block entirely". 3 "Keep words and file name". The decision owner typed block 13.
Block 14. Open point 2. "Tool names (Claude, Codex, Cursor, Kimi) appear in 88 release files, 110 records and 11 demo code files, mostly in approval lines, worklog notes and review provenance. The leak gate does not fail on them today. What stays?" Options: 1 "Keep where they name the tool that did the work (Recommended)": the walkthrough's tools table and the worklog keep them; approval lines lose them, since the SME attribution replaces those. 2 "Remove every tool name". 3 "Keep all as they are".
Block 15. Open point 3. "68 records quote working instructions, such as "yes, extend the delegation to steps 5 to 12." (46 records), "yes, keep it private" (7) and "go ahead with the item F decision record." Decision 3 says you reattribute or drop each. How?" Options: 1 "Reattribute all, same as other quotes (Recommended)": each reads as from "a subject matter expert reviewing the documents"; no per-quote list. 2 "Drop the working-instruction quotes". 3 "List all 68 for me to answer one by one".
Block 16. Open point 4. "19 of the 137 cached Parallel answers are third-party market reports that name peers. Rewriting them changes the text the re-judge reads, so re-judged verdicts may differ from main's. What should the release do?" Options: 1 "Rewrite them, report any verdict change under this rule (Recommended)". 2 "Keep peer names inside third-party quotations only". 3 "Drop those 19 cached answers".
Block 17. Follow-up on point 1. "You said references like "EPM-DEC-001-0044" must not show up anywhere, because readers are not aware of these documents. Decision 3 in the plan ships the decision records themselves, with quotes reattributed. The record numbers are cited in 486 other files (9,305 places), among them the ontology's Turtle, where a term's dcterms:source names the record that decided it. Which do you mean?" Options: 1 "Records do not ship; every citation comes out (Recommended)": the 110 records and decisions page stay out; in the ontology, a term's record citation becomes a plain provenance note ("decided on 2026-10-18 by a subject matter expert reviewing the documents"); in docs, the number is dropped or replaced by a date; the glossary and READMEs lose their record links. 2 "Records ship under a neutral name, citations kept". 3 "Records ship as they are; only the manifests and citations in packages lose the numbers".
Block 18. Open point 5. "Chevron and Exxon Mobil are not in the seven-peer evidence folder, but MPC's own 10-K names them as the comparators of its benchmark measure, and the kpi module carries that text (8 release files, 2 population files). Are they peers for the rewrite?" Options: 1 "Yes, treat them as peers (Recommended)": no company but MPC and MPLX is named in any comparison. 2 "No, keep them".
Block 19. Open point 6, first asked as "The Step 4 evidence gate reads the review evidence and the answers, which do not ship, and the Git pin. The release's check script drops the gate, its ledger and its tests; the taxonomy ships as the frozen baseline the builders read. Confirm?" The decision owner typed block 19. Asked again with the explanation (the gate is step4/evidence-gate.py, which checks the review's bookkeeping: that each evidence CSV cites the pinned commit, that the 1,318 mentions add up, that canonical-facts.csv holds 640 facts with no contradictions, and that the reviewer verdicts and label decisions are present; it needs the review evidence, the reviewer answers and the Git pin, none of which ship), options: 1 "Yes, drop it; the check script says why (Recommended)". 2 "No, ship the review evidence so it can run". The decision owner chose block 20.
Block 21. Open point 7, first asked as "These stay out under Decision 5 unless you want them: the 2026-10-14 decision packages (written to you as "you"), the Step 3c reviewer notes, the old lpg-projection guideline (now the skill), the open-ontologies trial notes, the O2C research files, and best-practices. Which should ship after all?" (several allowed). Options: "None; leave all out (Recommended)", "best-practices (7 files)", "O2C research files (3 files)", "Decision packages (6 files)". The decision owner chose "None; leave all out (Recommended)", "O2C research files (3 files)" and "Decision packages (6 files)" and typed block 21. Asked again with best-practices described (seven general guides written early in the project: a production-ready ontology guide, a controlled-vocabulary practice guide in Markdown and HTML, two pages on 100 enterprise KPIs, and two images; no shipped file links them) and asked to confirm what ships from the group, options: "O2C research files (3)", "Decision packages (6)", "best-practices (7)", "Nothing from this group". The decision owner chose blocks 22 and 23; this second answer is the one applied.
Block 24. Open point 8. "The clear-writing skill holds calibration.md, your personal rule weights, and every skill has a SOURCES.md that names where its content came from (two name you). What ships?" Options: 1 "SOURCES rewritten, calibration.md out (Recommended)". 2 "Both out". 3 "Both in, rewritten".
Block 25. Open point 9. "Decision 6 ships the way-of-working skill only if recipients should adopt the working method (pull requests, the check script, independent and PR reviews). Its README and sources name you and the repositories and would be rewritten. Should it ship?" Options: 1 "No, leave it out (Recommended)". 2 "Yes, ship it rewritten".
Block 26. Open point 10. "The release before the latest goes under its own folder, releases/previous/, with a README saying it is history only: nothing loads it, and its pins may name versions the release does not ship (for example system 1.2.0). Confirm the folder and that rule?" Options: 1 "Confirm (Recommended)". 2 "Different folder name". 3 "Rebuild the previous set's pins too".
Block 27. Point 11. "You said the 21 use cases need not be tested in this release, and that they alone used the Databricks daily limit. The plan has two acceptance checks: the live run (acceptance run --repeat 3, the one that uses the limit) and the offline re-judge of the ten recorded runs, which reads the recorded answers and judges them again. Which is skipped?" Options: 1 "Skip the live run only (Recommended)": the offline re-judge still runs if it needs no Databricks; the recorded runs ship as they are; the acceptance code ships and the README says it was not run on the release. 2 "Skip both". 3 "Skip both and leave the recorded runs out". -->

yes, grill me now. In this release we do not have to test the 21 use cases that we were validating in main by the way. That is the only think that contributed to Databrick daily limit.

O like Option 1. In addition I do not want refrences like ""EPM-DEC-001-0044;" shows up anywhere. The people that will consume the release are not aware of these documents

Keep where they name the tool that did the work (Recommended)

Reattribute all, same as other quotes (Recommended)

Rewrite them, report any verdict change under this rule (Recommended)

Records do not ship; every citation comes out (Recommended)

Yes, treat them as peers (Recommended)

what is this gate

Yes, drop it; the check script says why (Recommended)

what do we mean by this best practices?

Decision packages (6)

best-practices (7)

SOURCES rewritten, calibration.md out (Recommended)

No, leave it out (Recommended)

Confirm (Recommended)

Skip the live run only (Recommended)
