# EPM-DEC-001-0049: The decision owner is named by role, not by person

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-19) |
| Date | 2026-10-19 |
| Questions | Item 4 of the morning summary of 2026-10-19: how the repo names the person who decides |
| Source | Claude Code session, 2026-10-19 |

## Context

Until now the repo named the person who records decisions, approves releases and answers source questions by their personal name: in prose, in four review-file column names, a route type, a constant and the answers folder's name, in the release manifests' `approved_by`, in the core ontology's `dcterms:creator`, in one kpi source IRI, and in GitHub links that carried their account name. Read that way, an approval looked like one individual's.

## Decision

**The decision owner's decision:** neutral, generic wording. The repo names no person. Where it named them, it now names the role, "the decision owner", in every current file. Git history, commit authors and tags are not rewritten.

**What follows (Claude, carrying out that decision):**
1. **Prose.** The name becomes "the decision owner", and the pronouns that referred to them become singular "they". Words the decision owner wrote stay as written, except that a link inside a quote, which carried the account name, is replaced by a bracketed note: "[link removed under EPM-DEC-001-0049: …]" (EPM-DEC-001-0020 and 0022).
2. **Identifiers.** The answers folder is now `step4/review-evidence/decision-owner-answers/`. The columns are now `owner_words`, `owner_decision`, `owner_rationale` and `owner_answer`, the route type is now `owner-verdict`, and the constant is now `OWNER_APPROVED_GOVERNED_BY`. Scripts and tests read the new names.
3. **Links.** A GitHub link that carried the account name keeps its issue and comment number and drops the URL ("#207 comment 6137222677"). A link to another repository under that account names the repository. A saved answer's header names its source as a URN, as the source-question template now says. An absolute home-folder path starts at `~/`.
4. **Two kinds of IRI change, the only ones.** First, the kpi source node `src:planner-measure-list-2026-10-18` drops the name from its local name, in `kpi/measures.ttl` and in kpi 1.0.0 and 1.0.1. Second, the two scoped-sequence sources, which were GitHub comment URLs, are now URNs: `urn:epm:issue:205:comment:6115309253` and `urn:epm:issue:205:comment:6116668059`. The saved answers' headers, `scoped-sequences.csv`, `scoped-sequences.ttl` and core 1.0.0, 2.0.0 and 2.1.0 carry the same change, and `build_core.py` describes each URN as the GitHub comment it names. No other IRI changes.
5. **Released packages are edited in place.** Every package whose builder has `--write` (core 1.0.0, 2.0.0 and 2.1.0, organization 2.0.0, ref-mpc 1.1.0 and kpi 1.0.1) is rebuilt and passes `--verify`. Organization 1.0.0, ref-mpc 1.0.0 and kpi 1.0.0, which no builder rebuilds, have their files edited and their manifest hashes recomputed. Versions, release dates and tags stay as they were, and the decisions each package carries do not change.
6. **A guard.** `python3 scripts/epm_facts.py names` fails when a tracked file, or a path, contains the personal name, the family name or the GitHub username, in any case: every tracked path, symlinks included, and every part of an Office file: its raw XML, each cell or paragraph as Office displays it (joined from its text runs), and every decoded element text and attribute value, such as a sheet name or the author property. The names are built from fragments in the script, so the guard does not match itself. `scripts/check.sh` runs it, so CI and the pre-push hook do too, and `scripts/test_epm_facts.py` tests it.

## Alternatives considered

- **Rewrite git history as well.** Not chosen: the decision owner chose "All current files (Recommended)", which leaves history, commit authors and tags as they are.
- **Another term ("the approver", "the project owner").** Not chosen: the decision owner chose "the decision owner (Recommended)".
- **Leave released packages unchanged.** Not chosen: the released files named the person in `approved_by`, `dcterms:creator` and the kpi source IRI, and the decision covers every current file.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-19-after-run.md`, item 4: "neutral wording. Leave my name out of the repo. And also make it generic. Dont make it look like an individual is approving this. Make it generic ." The choices "All current files (Recommended)" and "the decision owner (Recommended)", and "keep A plus the guard", are saved in the same file.

## Evidence

The answers file named above. The replacement used one reviewed script with explicit patterns, kept outside the repo so that its patterns never enter it, and then a read of every changed line.

## Consequences

- A new text that names the decision owner fails `scripts/check.sh`.
- An answer saved from now on goes in `decision-owner-answers/`, and its header names the role.
- A reader of a release sees "The decision owner" as approver and creator. The decisions behind each release are unchanged.
