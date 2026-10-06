# Review standards

The judgement rules a reviewer applies to every pull request in this repo. Approval routing is in `APPROVAL_POLICY.md`.

Mechanical rules live in `scripts/check.sh` (the Step 4 gate, tests, published figures, decision-record consistency), which CI runs. Read its CI result rather than re-checking those by hand. This file holds only what a script cannot judge.

Each rule says what to block on and where it came from. A rule earns its place by catching a real defect; delete a rule when the decision behind it changes.

## Blocking: AGENTS.md requirements, checked on the diff

AGENTS.md owns these requirements; this file does not restate them. Block when the diff breaks one:

- **Working rules:** nothing is marked Decided or Approved without Hamid's recorded decision.
- **Before every push**, items 3 and 4: external facts cite a primary source with the full-support version, and a change (including a rule change) reaches every place and every dependent section it applies to.

## Blocking: reviewer judgements

1. **Quotes match the record.** Where text attributes a decision or a request to Hamid, the quoted words exist in the cited record or session, and the text claims no more than they say. *Source: on-the-record attribution rule.*
2. **Claim only what has landed.** A record or document states as done only changes that are merged. A change still in an open PR, in this repo or another, is described as pending, with its PR number. *Source: PR #216 (EPM-DEC-001-0025 claimed a skill change still open in personal-agent-skills #5).*
3. **Figures outside CI's coverage trace to the source, over the right population.** CI checks the published Step 4 figures (`scripts/test_published_figures.py`). For any other figure in the diff, such as one in a new document, an issue body or the PR body, check it against `python3 scripts/epm_facts.py`. For every count, check that it counts the population the sentence claims: rows, not mentions; listed rows, not IDs cited in rationale text. *Source: PRs #208, #216 (counts written from summaries; IDs cited in rationale counted as rows).*
4. **Moved text keeps its approved wording.** When approved text moves between files, it moves word for word, with a note naming where it came from. Rewording approved text needs Hamid's recorded decision. *Source: PR #199 (the Step 4 evidence discipline moved to `step4/evidence-discipline.md`).*
5. **The playbook stays a method.** `business_architecture/ontology/ontology-playbook.md` holds company-neutral method. A project decision (an EPM IRI, an MPC choice, a ruling on one row) goes in an EPM-DEC-001 record and the worklog, and the playbook may cite it as an example in §7. *Source: EPM-DEC-001-0024.*
6. **Held rows reach the source author only through the recorded backlog.** Text that sends a held row to the source author outside the source-correction backlog contradicts EPM-DEC-001-0025. *Source: PR #216.*

## Not blocking

Report these as suggestions, not HOLDs: wording that is clear but could be tighter, a missing nice-to-have test, style within the clear-writing rules, and anything `scripts/check.sh` already enforces and CI passed.

## Changing this file

Add a rule only after it catches a real defect, with its source. Each change to this file goes through its own pull request; the reviewer applies the base-branch version to that pull request.
