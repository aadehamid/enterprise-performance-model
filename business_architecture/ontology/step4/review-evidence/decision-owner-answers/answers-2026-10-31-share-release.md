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
