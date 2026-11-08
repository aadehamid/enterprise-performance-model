# EPM-DEC-001-0110: A release of the ontology and demo for colleagues outside the build: what it holds, what is rewritten, how it is validated, and what follows it

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-31, for the release's scope, the rewrites, the validation, the order of the releases and the work after them; the build choices delegated under EPM-DEC-001-0028) |
| Date | 2026-10-31 |
| Questions | The decision owner asked for a release to share with colleagues who were not part of the build. What it holds; whether it may name the repository, the decision owner or a peer; what "decision owner" means to a reader; whether internal documents stay; what LSC becomes; how the graph's names are written; how the decision owner's quotes read; which release the links go through; how the cut is validated; and what work follows the first release |
| Source | Claude Code session of 2026-10-31; `answers-2026-10-31-share-release.md`, blocks 1 to 30 |

## Context

*2026-11-07:* EPM-DEC-001-0114 authorizes a documentation-only Party/Core reference release. It adds documentation to the existing release without rebuilding ontology packages, changing existing release files, or removing or reloading data and projections. The full-cut sequence below still applies to other kinds of release.

The ontology is done (EPM-DEC-001-0107) and its documents were tightened for the cut (#456, #458). The decision owner then asked for a release that colleagues outside the build can use, holding the newest release of each module and the one before it, every build and validation script, the demos, a copy of the agent skills used, and the documents. Nothing in it may name the repository or the decision owner, and no peer may be named (*2026-11-02:* except in market news: EPM-DEC-001-0112, point 7). Claude scanned `main` and put seven points to the decision owner, then a plan whose "Decisions" list carried a recommendation for each open choice. The plan lives outside the repository (`release-cut/`, gitignored), because it names what the release must hide.

What Claude found, from the repository on 2026-10-31 (`git grep`, `git ls-files`):

- Seven peers are named in 50 tracked files, among them every `kpi` release's Turtle and JSON-LD; 132 files use the word peer.
- The pattern `decision[ _-]?owner`, case-insensitive, matches 11,610 times in 700 files; the plain phrase "decision owner" is in 688 of them. 277 of the 700 are structured files: Turtle (63), CSV (61), Python (55), JSON (54), JSON-LD (39), SQL (3), shell (1) and YAML (1). The matches include identifiers (`decision_owner`, `DecisionOwnerRoles`, `DecisionOwnerAnswers`) and ontology role terms.
- The IRI base `w3id.org/lsc` is in 479 files.
- Every release manifest and each `core` release's Turtle cite an answers file in `step4/review-evidence/decision-owner-answers/`, which does not ship.
- Builders and checks read Git history (`git show`, tags, the Step 4 pin), which a zip has none of.
- Neo4j's n10s plugin writes graph names as `prefix__name` (`vs__Stage`); the round trip and the in-graph SHACL read those names.
- 12 of the 24 dependency links between the newest packages name an older version, because a released package never changes after a later release of what it depends on.

## Decision

**The decision owner's decisions:**

1. **The release and who it is for:** "I plan to cut a release that I can share with my colleagues who were not part of this process." It holds "the latest from each module release and the release before the latest", "all of the business process in json, the final version", "all of the scripts used either to build or validate", "the demos and all of its code", "a copy of my personal agent skills, eg ontology, ontology t lpg, clear writing, playbboks - ontology and projections" and "the docs with all the chnages made above". Its readers "must be able to do everything we have done here as the ntology and demo goes." It lives on "an prropriatley names release branch that I can zip and share with others and that we can always update if we add anything new in main."
2. **No repository, no name, no peer:** "I dont want any mention of this repo or my name." Peers are "termed industry view or something like that": "Essentially all refrences are valid except for peers, which we wil call industry view or best practices."
3. **The validation:** "The most important thing is the validation after cut. itMUST WORK like it didi when we did this from main. We must test EVERYTHIN and delet the data created to test it when we are done."
4. **"Decision owner":** "decsions owner means an SME. I think we can leave it if the changes to a subject matter extert is too big of a work."
5. **Internal documents and systems:** "internal documents and is fine and we can leave the files." With an option: "We shuld add a line in the release plan with an option to also remove the internal files and systems. So that anyone buiding this can choose. of course anything that will change if we want to remove this internal docs and systems muts be shared for review first if we choose the latter route."
6. **Claims resting on peers:** "claims resting on peers stay in, but must be presentend as both industry standard and analysis of publickly available filings from peers - U.S refiners"
7. **The name LSC:** "the LSC that we use bith in the namespaces and others should be MPC instead. Let us add that to th release cut"
8. **Namespace approval:** "namespaces will be reviewed and approve by the Data, Analtyics, and Insight team. This will only be in the release part. main stays the same as the original from which we can cut relleases."
9. **Names in the graph, and the release as a whole:** "make sure to use imsple normal underscore between names in the tripple instaed of the em dashes. em dashess "--" should never be used in the graph or anywahere in the release. for exmaple "vs__Stage" should be ""vs_Stage""". Asked what the dashes meant: "the loonger version of the separartor was what I meant", that is, the `__` separator n10s writes between a prefix and a name (`vs__Stage`), which the release must hold nowhere, not an em dash in prose.
10. **The decision owner's quotes:** "couch the quote as coming from an SME that is reviewing the documents"
11. **All links through the latest release:** "let us also make sure that the ontology that we will cut all links must be through the latest release. The release before that is just to demonstarte that we release ontology in releases."
12. **The plan's recommendations:** "i agree with all yur recoommendation in the release cut". The recommendations accepted are the plan's, in Claude's words, not the decision owner's: (1) keep each module's version numbers inside a new edition, for example EPM 1.0, with hashes rebuilt, since recipients never see the originals; (2) every shipped version rebuilds from frozen inputs, with no rebuild of older versions and no Git history; (3) ship the decision records with the quotes reattributed, keep the worklog only if it passes the gate, and list the working-instruction quotes for the decision owner to reattribute or drop (*2026-10-31, the grill:* superseded; no record ships and every such quote is reattributed, amendment items 1 and 3 below); (4) the IRI base, superseded by decision 7 above; (5) the pricing demo and both O2C demos are the demos, and the early folders stay out unless a shipped file needs them (*2026-10-31, later:* superseded; only the pricing demo ships, amendment item 13); (6) the skills `ontology`, `ontology-to-lpg`, `rdf-store` and `clear-writing`, plus `way-of-working` only if recipients should adopt the working method (*2026-10-31, the grill:* "No, leave it out (Recommended)", amendment item 9); (7) APQC with its notice, and DPROD and other PDFs only where a build needs them, each licence checked; (8) a neutral contact line the decision owner fills in when sharing, or none; (9) the demo defaults to local Docker for Postgres and drops the exe.dev option, recipients bring their own Databricks, EIA key and optional AuraDB and Parallel keys, and the cached Parallel answers ship; (10) a second, temporary Aura instance and a separate Databricks workspace for the test, each deleted afterwards (*2026-10-31, later:* for AuraDB the decision owner chose the fallback of reusing and restoring the existing database, amendment item 12).
13. **What follows the first release:** "yes, build it after the first release. I will do them once we confirm the release, and then cut another release." and "Please, add all of them to the plan to do after the first release cut. we wll then do a follow up release once we take care of the other ontology work with another release to make it complete fully." Later the same day, replacing the sentence that the first release goes to the colleagues: "let us leave OPEN_ITEM.md out of this plan for now. it will be handled sepaately. By the way when I finish with (1) I will not share with coleague until I complete all of theother tasks and do another release to update the previous one to a full version. It is then that I will share with colleague as a complete picture."
14. **The technical graph and Databricks:** "the technical graph should not be projected to Databricks since databrick already have technical graph in delta table"
15. **A viewer, after the full release:** "when we have completed the full release of the ontology we should use https://github.com/morluto/rea to create an ontology viewer like https://openenergyplatform.org/viewer/oeo/ to view our ontology using https://github.com/leonxlnx/taste-skill". "The veiwer is where most people will go to review the ontology" and "The viewer should be built on one ontology release only."

**What follows (Claude, under EPM-DEC-001-0028):**

1. **The release is generated, never edited.** One command exports an allowlist of paths from `main` and the skills repository's `main`, applies rewrite rules, rebuilds every package, page and hash, runs a leak gate that fails on any name, handle, repository, host, peer or issue number (*2026-11-02:* the cut can also read files kept outside `main`, `cut.sh --augment <folder>`, recording their hashes in the manifest, and the gate scans what it builds from them: EPM-DEC-001-0113, points 2 and 6; *2026-11-02:* except peer names in market news, which the rewrite rules and the gate are to leave in place: EPM-DEC-001-0112, point 7), and writes an orphan branch with one commit and a zip of its tree. Updating the release means running the command again. The export script, its rules and the gate live in `main` under `scripts/share_release/` and do not ship.
2. **"Decision owner" stays** and is defined once, in the glossary and the release's README, as a subject matter expert: the rename would touch 11,610 matches in 700 files, 277 of them structured, with identifiers and role terms among them, which is the case the decision owner's words leave the term in.
3. **Peers:** every claim stays; its source reads "Industry standard, and analysis of publicly available filings from peers (U.S. refiners)"; no peer is named, and no peer claim reads as MPC's. *2026-11-02:* peer names in market news, the cached Parallel answers and the demo's `SCENARIO.md`, stay, and the release README is to say so from the follow-up release on (EPM-DEC-001-0112, point 7).
4. **LSC becomes MPC in the release only:** IRIs (`w3id.org/lsc` to `w3id.org/mpc`), module titles and every other use, with all hashes rebuilt; `main` keeps LSC. The release's README says the IRIs identify terms, resolve nowhere and are not issued by Marathon, and that the namespaces will be reviewed and approved by the Data, Analytics and Insight team, a future review. The leak gate checks that this note is absent from `main` and present in the release.
5. **The latest set is the ontology.** Each newest package is rebuilt so its manifest, `dcterms:requires` and catalog record name only the newest versions; terms link by IRI, so only the pins move, and a pin move that changes anything else stops the cut. The release before is history only, under `releases/previous/` with a README, rewritten and hash-verified, loaded by nothing; its pins may name versions the release does not ship, such as `system` 1.2.0, and the README says so.
6. **Single underscores everywhere in the release:** in the graph (labels, relationship types, property keys), in every Cypher query, document and generated file, and in code. The leak gate fails on `__` between names anywhere in the release; Python's own names such as `__init__.py` and `__main__` are language syntax, not separators between names, and stay (Claude's reading). The graph is tested before the export is written: a per-term mapping in n10s first (its reference page names the setting); a rename after the checks second; and if neither keeps 0 lost, 0 added and equal hashes, the result goes to the decision owner. No check is loosened.
7. **Quotes:** each stays, attributed to "a subject matter expert reviewing the documents"; citations of the answers folder come out; the answers folder and night logs do not ship. The working-instruction quotes go to the decision owner as a list (*2026-10-31, the grill:* no list; every one is reattributed, amendment item 3).
8. **Validation** runs against a baseline saved from `main` first, in a clean room with no GitHub access and only the zip (*2026-11-02:* the clean room proves the release on its own, since the zip holds every module the cut built; when the cut read an augment folder, `validate.py compare --augment` and `clonecheck.py --augment` check the folder's files against the hashes the release records: EPM-DEC-001-0113), over every area the plan lists (setup, checks, business process, builders, ontology content, underscores, latest links, the LSC rename, SHACL and the regression, projection pipeline and driver, technical graph, sync, demos offline and live, acceptance, other demos (*2026-10-31, later:* none; only the pricing demo ships, amendment item 13), skills, documents, every snippet, the store map, the in-sync strategy and the leak gate). A difference passes only if a rewrite rule explains it. The live acceptance tests vary by model, so re-judged runs must match exactly and a new live run is reported beside `main`'s (*2026-10-31, the grill:* the live run is skipped on the release; the offline re-judge runs if it needs no Databricks, amendment item 11). Test data is deleted from a ledger and shown gone; `main`'s stores read the same before and after; the first release is validated and not shared.
9. **After the first release,** on `main` through its own pull requests: a vocabulary module for the technical graph (the first use of `references/new-module.md`), lineage from Databricks (#457), and the in-sync plan (#455, #426) (*2026-11-02:* and the logical-model module, whose `1.0.0` the cut waits for: EPM-DEC-001-0113, point 10). The technical graph is not projected into the ontology's Databricks table: Databricks already holds it as the Delta copy EPM-DEC-001-0109 (decision 7) records, `tech_graph_nodes` and `tech_graph_edges`, and that copy stays as it is. A second release, the full version, is then cut with the same command and validated against a new baseline; that is the version shared with colleagues. The viewer starts only after it.
10. **Question 17:** sharing the full version with business consumers meets EPM-DEC-001-0086's trigger. Claude asks the decision owner before the zip is shared and records the answer. *2026-11-02:* asked; the decision owner answered that the release may be cut and shared with Q17 still open, listed in `OPEN-ITEMS.md` (EPM-DEC-001-0086, amendment of 2026-11-02).

## Amendment, 2026-10-31 (later): the grill of what the inventory found

Step 1's inventory of every tracked path found eleven points the plan did not settle. Claude put each to the decision owner with a recommendation (`answers-2026-10-31-share-release.md`, blocks 12 to 27). The decisions:

1. **Approval provenance in the packages:** "O like Option 1. In addition I do not want refrences like ""EPM-DEC-001-0044;" shows up anywhere. The people that will consume the release are not aware of these documents". Asked whether that means the decision records do not ship, since their numbers are cited in hundreds of other files (the question said 486; the count of files holding a full record number outside the records, the review evidence and the pages is 482): "Records do not ship; every citation comes out (Recommended)". This supersedes recommendation (3) under decision 12 above, which shipped the decision records with their quotes reattributed and listed the working-instruction quotes for the decision owner.
2. **Tool names:** "Keep where they name the tool that did the work (Recommended)".
3. **Quotes that are working instructions:** "Reattribute all, same as other quotes (Recommended)".
4. **Peer names inside the cached Parallel answers:** "Rewrite them, report any verdict change under this rule (Recommended)". *2026-11-02:* superseded for market news by EPM-DEC-001-0112, point 7: peer names in the cached Parallel answers and in the demo's `SCENARIO.md` stay.
5. **Chevron and Exxon Mobil:** "Yes, treat them as peers (Recommended)".
6. **The Step 4 gate:** asked "what is this gate", then, with the explanation: "Yes, drop it; the check script says why (Recommended)".
7. **Folders the plan left out:** asked "what do we mean by this best practices?", then, with the folder described: "Decision packages (6)" and "best-practices (7)" ship; the Step 3c reviewer notes, the old `lpg-projection` guideline, the trial notes and the O2C research files stay out.
8. **The skills' personal files:** "SOURCES rewritten, calibration.md out (Recommended)".
9. **`way-of-working`:** "No, leave it out (Recommended)".
10. **The previous set's folder:** "Confirm (Recommended)", to the question whether the release before the latest goes under its own folder, `releases/previous/`, with a README saying it is history only, nothing loads it, and its pins may name versions the release does not ship.
11. **The 21 use cases:** "In this release we do not have to test the 21 use cases that we were validating in main by the way. That is the only think that contributed to Databrick daily limit." Asked which of the two acceptance checks is skipped: "Skip the live run only (Recommended)".
12. **AuraDB for the test** (block 28), asked which fallback to use when a second free AuraDB instance is not available, option 1 being to skip the Aura copy step and report it untested and option 2 to point the test at main's Aura and reload main's data afterwards: "2. clean out Aura... then load with data you want to test. When you are done clean out the data in Aura again and load data from main." So, in place of recommendation (10)'s second instance, the test empties the owner's AuraDB, loads its data, then empties it again and reloads `main`'s, proven by `sync_stores.py check`.
13. **The scope, restated** (blocks 29 and 30): "all the playbooks (ontology, projection, guides, walkthrough should also be included. and all the scripts we use anywhere to create, validate, load and so on the ontology. A copy of all of the bsuienss json processes needs to be part of the release cut as well." and "only things that ontology related and the pricing demo. all other files no related to any of this should not be part of the release." So the two O2C demos come out; the pricing demo, the ontology, its documents, playbooks, scripts and the business process JSON stay, rewritten for a reader who has never seen the repository.

**What follows (Claude, under EPM-DEC-001-0028):**

- **No decision record ships, and no record number appears in the release.** The 110 records, their index and page come out, and so does every record number elsewhere: on `main` at 0ad29381, outside the records folder, the Step 4 review evidence and the generated pages, 482 files hold a record number (`EPM-DEC-001-` and four digits) in 9,305 places (`git grep`; 545 files and 10,738 places with the review evidence and the pages counted). In the ontology a term's record citation becomes a provenance note with the date and "a subject matter expert reviewing the documents"; in documents the number is dropped or replaced by the date; the manifests' `decisions` and `approval.file` fields come out and `approval.who` reads "a subject matter expert reviewing the documents". The leak gate fails on `EPM-DEC-001`. The six decision packages ship rewritten the same way.
- **Tool names** stay where a sentence says which tool did the work (the walkthrough's tools table, the worklog) and come out of approval lines. The gate does not fail on them.
- **Every quote** of the decision owner outside the records, working instructions included, is attributed to "a subject matter expert reviewing the documents".
- **Peers** are the seven companies the evidence cites plus Chevron and Exxon Mobil: no company but MPC and MPLX is named in a comparison, in the cached Parallel answers included (*2026-11-02:* except market news, where peer names stay: EPM-DEC-001-0112, point 7). A re-judged verdict that changes after that rewrite is reported as explained by it.
- **The release's check script** drops the Step 4 gate, its ledger, its tests and the pin check, and says why; the taxonomy ships as the frozen `baseline/` the builders read.
- **The skills** ship without `calibration.md` and without `way-of-working`; each `SOURCES.md` is rewritten.
- **The test stores (Claude's build choice, under EPM-DEC-001-0028):** AuraDB as the decision owner directed in item 12; Databricks keeps the existing Free Edition workspace and uses its own catalog and schema names for the test, deleted afterwards, in place of the separate workspace recommendation (10) named, since the live acceptance run, the one heavy use of the workspace, is skipped.
- **The acceptance tests:** the live run is skipped on the release and its README says so; the offline re-judge of the ten recorded runs runs if it needs no Databricks; the code and the recorded runs ship. With the live run out, the validation no longer depends on Databricks Free Edition's daily limit.

## Amendment, 2026-11-01: the release is a base its readers update, and it names no agent

A trial of the cut found that a recipient could make four ordinary changes only by editing code and tests, and that `check.sh` went green only with 22 tests excluded. The decision owner then set what the release is for (`answers-2026-11-01-share-release-recipients.md`, blocks 1 to 5):

1. **The release's job:** "The releseas I share will b ethe base for them. So what I really wants to communictae out is how they can update what they get." The readers are not told to cut a release; they are told how to add a module, change a module and change a definition.
2. **No agent named:** "We should also not name any agents (e.g. claude, cursor and so on) in the release." This supersedes amendment item 2 above ("Tool names"), for agents and review tools. Other tools the build uses keep their names.
3. **The reader:** "whoever is going to consume it is not aware of the work we did here. So all agents name or anything related to agents must be neutral . and all decisions by SME."
4. **The fixes:** "I am am aligned with your recommendation. All must be throughly validated." The recommendation was the list that follows.
5. **The stores after a cut:** "Let us drop the ontology in local neo4j (empty it), jena (empty it), Databrick (empty it), Aura (empty it)." and "Then repopulate them with only ontology from the private release repo." This supersedes "load data from main" in amendment item 12 above.

**What follows (Claude, under EPM-DEC-001-0028):**

- **`main` keeps its history unchanged; only the release is neutral.** A rule rewrites agent names and agent work in the release, and the leak gate fails a cut in which a name or an agent-work phrase survives. A draft keeps its status, so it never reads as approved. The demo's Genie agents and supervisor, `prov:Agent` and `prov:SoftwareAgent` as W3C terms, and the database `cursor` stay.
- **Build history:** the worklog stays out, since recommendation (3) under decision 12 kept it only if it passes the gate and it is the build's own record. The decision packages still ship rewritten, as amendment item 7 says, except `pr-reviews-262-266-269.md`, which is only about the agents' reviews and merges and cannot be made neutral. The pull request that lands this lists each file.
- **The release passes its checks from a Git clone and from a plain folder,** and the cut's validation runs both.
- **The tests that pin the release to its first state are a separate, optional group.** The release's `check.sh` proves the ontology is valid; whether it still equals the release as shipped is a question only until the recipient's first change.
- **Builders, the regression and tests read the newest version on disk,** `--write` refuses to overwrite a released package whose version was not bumped, and `main` keeps every check it has today.
- **The release's guide** (`HOW-TO-UPDATE.md`) replaces the walkthrough's instructions in the release only, through a template in `scripts/share_release/`. Step 9 of the tool reloads the stores from the release, not from `main` (item 5 above).

## Alternatives considered

- **An ordinary branch merged from `main`.** Not chosen: rewritten text conflicts on every merge, and the branch's history carries author names, PR numbers and peer mentions.
- **Renaming "decision owner" to "subject matter expert".** Not chosen: 11,610 matches in 700 files, identifiers and ontology role terms among them; the decision owner's words leave the term in when the change is too big.
- **Keeping the IRI base `w3id.org/lsc` in the release.** The plan's first recommendation; superseded by the decision owner's answer that LSC becomes MPC.
- **Shipping every version of every module.** Not chosen: the decision owner asked for the newest and the one before.
- **Removing internal documents and systems by default.** Not chosen: the decision owner keeps them, with a reviewed option to remove them.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-31-share-release.md`:

- "I plan to cut a release that I can share with my colleagues who were not part of this process."
- "I dont want any mention of this repo or my name."
- "Essentially all refrences are valid except for peers, which we wil call industry view or best practices."
- "The most important thing is the validation after cut. itMUST WORK like it didi when we did this from main. We must test EVERYTHIN and delet the data created to test it when we are done."
- "decsions owner means an SME. I think we can leave it if the changes to a subject matter extert is too big of a work."
- "internal documents and is fine and we can leave the files."
- "claims resting on peers stay in, but must be presentend as both industry standard and analysis of publickly available filings from peers - U.S refiners"
- "the LSC that we use bith in the namespaces and others should be MPC instead. Let us add that to th release cut"
- "namespaces will be reviewed and approve by the Data, Analtyics, and Insight team. This will only be in the release part. main stays the same as the original from which we can cut relleases."
- "make sure to use imsple normal underscore between names in the tripple instaed of the em dashes. em dashess "--" should never be used in the graph or anywahere in the release."
- "couch the quote as coming from an SME that is reviewing the documents"
- "let us also make sure that the ontology that we will cut all links must be through the latest release. The release before that is just to demonstarte that we release ontology in releases."
- "i agree with all yur recoommendation in the release cut"
- "yes, build it after the first release. I will do them once we confirm the release, and then cut another release."
- "By the way when I finish with (1) I will not share with coleague until I complete all of theother tasks and do another release to update the previous one to a full version. It is then that I will share with colleague as a complete picture."
- "the technical graph should not be projected to Databricks since databrick already have technical graph in delta table"
- "The viewer should be built on one ontology release only."
- "In this release we do not have to test the 21 use cases that we were validating in main by the way. That is the only think that contributed to Databrick daily limit."
- "The people that will consume the release are not aware of these documents"
- "Records do not ship; every citation comes out (Recommended)"
- "Yes, drop it; the check script says why (Recommended)"
- "Skip the live run only (Recommended)"

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-11-01-share-release-recipients.md`:

- "what i really want is not to tell people to do release cut like we did here."
- "The releseas I share will b ethe base for them. So what I really wants to communictae out is how they can update what they get."
- "We should also not name any agents (e.g. claude, cursor and so on) in the release."
- "So all agents name or anything related to agents must be neutral . and all decisions by SME."
- "I am am aligned with your recommendation. All must be throughly validated."
- "Then repopulate them with only ontology from the private release repo."

## Evidence

- `business_architecture/ontology/releases/` (50 version folders of 11 modules; the newest set's 12 older pins, read from each manifest's `requires` on 2026-10-31).
- `business_architecture/reference/downstream-peers/` (the seven peers the evidence cites); `git grep -il` for their names: 50 files.
- `business_architecture/ontology/release/build_core_2_2.py`, `build_core_next.py`, `projection/sync_stores.py` (`git show`); `scripts/check.sh` (the Step 4 pin); `scripts/test_published_figures.py` (`git archive`).
- `business_architecture/reference/README.md` (the APQC notice that must travel with all copies; EPM-DEC-001-0078).
- EPM-DEC-001-0049 (the repository names the decision owner by role); EPM-DEC-001-0086 (question 17 parked until the ontology is first shared with business consumers).
- n10s (neosemantics) 4.0 documentation, "Importing RDF Data" (https://neo4j.com/labs/neosemantics/4.0/import/, read 2026-10-31): under the default `handleVocabUris` setting a property such as `http://neo4j.org/vocab/sw#name` "has been shortened to `ns0__name` (notice the double underscore separator used between the prefix and the local name in the URI)"; `IGNORE` keeps local names only and `KEEP` keeps full URIs. "Configuring Neo4j to use RDF data" (https://neo4j.com/labs/neosemantics/4.0/config/, read 2026-10-31): the default is `SHORTEN`; the full list of settings is in the Reference section, which the underscore test reads before it runs.
- morluto/rea, `LICENSE` (MIT) at commit d54a4661 (2026-10-31), newest release rea-agents-6.8.0 (2026-10-25); leonxlnx/taste-skill, `LICENSE` (MIT) at commit 12af471f (2026-10-24), release v2.1.5 (2026-10-24); both read with `gh api` on 2026-10-31. The MIT claim covers those commits.

## Consequences

- The plan for the cut, its inventory of every tracked path, and the validation report stay outside the repository in `release-cut/` (gitignored) until the export script and gate land under `scripts/share_release/`.
- EPM-DEC-001-0086 carries a dated note: the full version's sharing is the trigger to ask question 17.
- Every change on `main` for the cut goes through a pull request with `scripts/check.sh`, the independent review and the Cursor verdict; both repositories end private; major releases, Market Data accountability and question 17 stay with the decision owner.

## Amendment, 2026-11-03: ship the viewer through the cut

The decision owner instructed (`answers-2026-11-03-viewer.md`):

> The owner wants the viewer shipped inside the shared release, through the cut; record that decision first.

The viewer ships inside the shared release through the cut. This supersedes the local plan's statement that it is not part of either release. Decision 15 and consequence 9 still set the start after the full release. EPM-DEC-001-0112's confirmation has met that condition.

The request pins the viewer's input to `share/epm-1.0` at `81f2f63b`, from its Turtle or JSON-LD, with no store. The scope interview is recorded below. At this scope decision, implementation and publication were pending.

EPM-DEC-001-0112 records the earlier confirmation at `2b3f02e2`. The later viewer request explicitly selects `81f2f63b`; it does not change that historical confirmation or claim that the two commits have identical contents.

The same request requires asking the decision owner before making any repository public, and returning all repositories to private when the work ends. This applies to every repository used for the viewer work. The viewer ships through the existing release cut; this decision creates no separate viewer repository.

## Amendment, 2026-11-03: viewer scope

The scope interview is saved in `answers-2026-11-03-viewer.md`, rounds 1 and 2. The decision owner accepted the recommendations for questions 1, 3, 4 and 5 with "aligned". For question 2, the decision owner answered:

> A viwier should be able to view all the ontology using the viewer. We do not have to exclude anything except the tecchnical graph

Asked whether to retain the technical-graph vocabulary and exclude its records, the decision owner answered:

> keep the vocabulary

The accepted recommendations, quoted from the saved questions:

- Question 1: "I recommend plain labels and definitions first, with IRIs, predicates and provenance expandable."
- Question 3: "I recommend classes, properties, concepts, concept schemes and designed individuals, including system attributes. Show evidence nodes within relationship details, with separate counts. Exclude technical-graph records and example datasets."
- Question 4: "I recommend the selected term and its immediate relationships, with controls to expand further. Every term remains searchable and reachable through hierarchy or module navigation."
- Question 5: "I recommend a read-only first release: browse, search, inspect and copy term identifiers. Comments, editing and saved review work stay outside this version."

The whole ontology includes the customer schema. The earlier request that the customer model stays out of `main` still applies. Build code may live in `main`; the cut supplies the customer model from the release inputs. The separate logical-model view suggested in question 2 was not specifically accepted and is a presentation choice, not a requirement attributed to the decision owner.

The decision owner also clarified the source boundary in `answers-2026-11-03-viewer.md`:

> by the way only released ontology in the private release repo will be viewed from the user. makes sesne

The viewer's user-facing data comes only from the released ontology in the private release repository.

## Amendment, 2026-11-03: value-stream navigation

The decision owner requested in `answers-2026-11-03-viewer.md`:

> for value stream, can we make sure that we can list the two value streams that we have. and then be able to drill into each one of the value stream

The viewer must list the released value streams and let the reader drill into each. The stages, their sequence and their process links come from the released ontology. The full module vocabulary remains accessible.

## Amendment, 2026-11-03: viewer heading and customer navigation

The decision owner requested the title "MPC Business Process and Architecture Ontology" in `answers-2026-11-03-viewer.md`. Additional heading information was requested as advice and remained undecided at this point. The reviewed-design amendment below settles the subtitle.

The decision owner then requested clearer customer navigation, quoting the preceding explanation in full:

> do you think we can do below. not easy to see at the moment
> The conceptual model is currently browsable term by term; there is no dedicated whole-model diagram yet. Likewise, the lifecycle lacks a prominent entry point. Both need clearer navigation to make them easy to find.

This adds a whole-model diagram and a prominent lifecycle entry point to the viewer scope. The earlier selected-term graph remains available for inspecting each term. Implementation and publication of these additions were pending at this decision. *2026-11-04:* completed with PR #491 and the viewer release, as recorded below.

Implementation approach: derive definitions, lifecycle links and relationships from the pinned released RDF. Presentation groups arrange the conceptual entities without changing the ontology. The release records lifecycle stages without a mandatory sequence, so their overview must not invent one.

## Amendment, 2026-11-03: reviewed viewer design and release authorization

The decision owner requested in `answers-2026-11-03-viewer.md`:

> by the way remove "One release" from the heading

This settles the subtitle question above. The implementation uses "Definitions and relationships". The same answers file records the request for separate module, value-stream and customer navigation, with direct Order to Cash and Commercial Hydrocarbon Lifecycle entries.

The decision owner required design review before repository-wide checks:

> I think we should do a review before we do repository checks. Validation that everything exists in the viewer is important. But we should be able to review at a faster iteration. Once we align on a design we can do full validation and repository check before we pubslish and cut a new release with the viewer.

The reviewed implementation provides a module landing page, breadcrumbs that preserve browsing state, global search, term-type filters and diagram zoom, fit and full-screen controls. This describes the implementation presented for review; it does not change the released ontology or its vocabulary.

After reviewing the viewer, the decision owner said:

> Looks great! Any other improvement you will suggest or should we release this.

The decision owner then authorized the release:

> go ahead and cut a new release. Once this is done do we have anything else that is outstanding or is this it?

The owner-review checkpoint is satisfied. Comprehensive checks, independent review, the Cursor PR verdict and the release cut remain required before publication. Implementation merge and publication were pending at this decision. *2026-11-04:* completed with PR #491 and the viewer release, as recorded below. This authorization does not close Q17, Market Data accountability or the other open business questions.

The saved permission for temporary repository visibility is:

> you can swithc the repo to public while working. Switch back to private when you are done working

All repositories must end private. The customer model remains outside `main`; the cut supplies it from the existing approved release inputs.

## Amendment, 2026-11-04: maintenance after the viewer release

### Context and completed release

PR #491 merged the viewer as `ae9be6d3` after independent review, Cursor's MERGE verdict and the repository checks. The cut published the viewer on the private release branch at `5132e75f`. Cut validation, the offline browser check and a fresh-reader check passed. The production reload from that release passed, with every ontology, technical-graph and logical-model sync marker current. The release report and logs are retained under the ignored `release-cut/` folder.

The agent's maintenance list comprised the standalone demo test command's missing pyshacl dependency, citation-check issue #428, catalog-fallback issue #384 and legacy-example issue #18. The agent proposed completing these after the viewer release and batching recipient-facing changes into one follow-up cut. This is context for the owner's messages, not a quotation of them.

### Decision and recorded words

The decision owner said in `answers-2026-11-04-viewer-maintenance.md`:

> We can park the forst and the second. Whats the third one about?

> Can you take up the third category then as part of the goal once you finish all the release. By the way, is it gonna affect? Are we gonna have to make another release when we finish the third category

> Okay, go ahead and that will conclude the go then. Once you finish the maintenance. Does this make sense? Is it clear to you what we need to do tonight while I'm asleep?

The same answers file records the additional request:

> can you investigate the below as well
> The repository's documents still link to the old diagrams: MODULES.md, README.md and the ontology guide. Changing those links needs a pull request,

### Follow-through

The agent will complete the maintenance list and investigate the diagram links through separate PRs, with the existing checks and reviewers. The follow-up release uses the existing cut and validation process. Business decisions and pricing-demo acceptance remain parked. No change to ontology meaning or vocabulary is planned; an unresolved modeling choice stays open. The later instruction below requires removal of image-source references from the documents before the follow-up release. This work grants no new business-model decision or paid service.

The earlier temporary-visibility permission and requirement to finish with every repository private still apply. The customer model remains outside `main`. The alternative of leaving all maintenance for another session was not chosen. Maintenance and its follow-up release remain pending.


### Later instruction: remove image-source references

The same answers file records the request to check where the documents say images were used as a source and remove those image references, with the timing specified as:

> before we do the follow up release.

The following implementation approach is the agent's reading of that request: replace references to customer images as sources with neutral customer-input descriptions in authored documentation and recipient-facing provenance, including the viewer. Other source formats stay as they are. This changes how those image sources are described, not which inputs support the ontology. Original saved answers remain verbatim audit evidence. Existing frozen packages remain historical inputs. The follow-up release must remove image-source references from its documents before publication, as requested above. The agent plans to apply the replacement method through the cut and check the generated documents, viewer and source text, including a comparison that rejects unrelated ontology changes.
