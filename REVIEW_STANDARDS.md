# Review standards

The judgement rules a reviewer applies to every pull request in this repo. Approval routing is in `APPROVAL_POLICY.md`.

Mechanical rules live in `scripts/check.sh` (the Step 4 gate, tests, published figures, decision-record consistency), which CI runs. Read its CI result rather than re-checking those by hand. This file holds only what a script cannot judge.

Each rule says what to block on and where it came from. A rule earns its place by catching a real defect; delete a rule when the decision behind it changes.

## Blocking rules

1. **Decided or Approved needs Hamid's recorded words.** Any text that marks something Decided or Approved, or attributes a decision or request to Hamid, quotes his words or links the record that does. A merge is not a decision. *Source: on-the-record attribution rule; AGENTS.md.*
2. **Claim only what has landed.** A record or document states as done only changes that are merged. A change still in an open PR, in this repo or another, is described as pending, with its PR number. *Source: PR #216 (EPM-DEC-001-0025 claimed a skill change still open in personal-agent-skills #5).*
3. **One rule, one wording, everywhere.** When a PR changes a status, a rule, a term or a figure, every document that states it agrees after the PR. Check the playbook, the decision records, the worklog, AGENTS.md, READMEs and the backlog, including text split across lines (`python3 scripts/epm_facts.py find "<text>"`). *Source: PRs #200, #212, #216 (a release gate and a decision status stated differently in different places).*
4. **Figures trace to the source, and counts follow structure.** Every figure in the diff matches `python3 scripts/epm_facts.py` and the PR body quotes its commit line. A count of rows is taken from the file's structure (table rows, listed IDs), never from a text search that also matches citations. *Source: PRs #208, #216 (counts written from summaries; IDs cited in rationale counted as rows).*
5. **External facts cite a primary source with a version.** Release notes, a changelog, a specification or a filing, with version and date. A version claim names the first release with full support, not a preview. An open issue tracker is a lead, not a source. *Source: enterprise-people-graph PR #1 (Jena's RDF 1.2 support, first misread from an open issue, then dated to a preview release).*
6. **A rule change is applied to everything that depends on it.** When a PR changes a method rule (a pipeline step, a release gate, a modeling rule), the later steps, checklists, examples and companion documents that rely on it change in the same PR. *Source: enterprise-people-graph PR #1 (Rule 4 changed, but the load step, checklist and learning guide still assumed the old rule); PR #216 (every HOLD still routed to the backlog after the gate changed).*
7. **Moved text keeps its approved wording.** When approved text moves between files, it moves word for word, with a note naming where it came from. Rewording approved text needs Hamid's recorded decision. *Source: PR #199 (the Step 4 evidence discipline moved to `step4/evidence-discipline.md`).*
8. **The playbook stays a method.** `business_architecture/ontology/ontology-playbook.md` holds company-neutral method. A project decision (an EPM IRI, an MPC choice, a ruling on one row) goes in an EPM-DEC-001 record and the worklog, and the playbook may cite it as an example in §7. *Source: EPM-DEC-001-0024.*
9. **Held rows reach the source author only through the recorded backlog.** Text that sends a held row to the source author outside the source-correction backlog contradicts EPM-DEC-001-0025. *Source: PR #216.*

## Not blocking

Report these as suggestions, not HOLDs: wording that is clear but could be tighter, a missing nice-to-have test, style within the clear-writing rules, and anything `scripts/check.sh` already enforces and CI passed.

## Changing this file

Add a rule only after it catches a real defect, with its source. Each change to this file goes through its own pull request; the reviewer applies the base-branch version to that pull request.
