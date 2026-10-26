# EPM-DEC-001-0101: The ontology playbook moves into the ontology skill as its guide, with three new sections

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-25, for the move and the three sections; how each is applied delegated under EPM-DEC-001-0028, amendment of 2026-10-25, evening) |
| Date | 2026-10-25 |
| Questions | Item E: where does the ontology playbook live, and what does it add on modules, the integration module and deciding between sources? |
| Source | Claude Code sessions of 2026-10-24 and 2026-10-25; `answers-2026-10-25-item-e.md` |

## Context

The ontology playbook (`business_architecture/ontology/ontology-playbook.md`) has been a domain-neutral method since 2026-10-23, and `epm_facts.py playbook` kept it free of EPM records, companies and paths. The `ontology` skill in personal-agent-skills runs the same method as a gated procedure, with the rules in its references, so the two documents stated many rules twice. On 2026-10-24 the decision owner asked for three additions: the integration-module pattern, how to decide between sources, and why to split an ontology into modules. On 2026-10-25 they asked whether the playbook should move into the skill, Claude recommended it, and the decision owner's queue for the session reads: "Item E: the three playbook sections, and move the ontology playbook into the ontology skill."

## Decision

The decision owner's words are quoted below.

**What follows (Claude, under EPM-DEC-001-0028, amendment of 2026-10-25, evening):**

1. **The playbook becomes the `ontology` skill's narrative guide,** `skills/data/ontology/references/playbook.md` in personal-agent-skills. Each step names the reference that holds its rules, and the guide points to them instead of restating them; where the two differ, the reference wins.
2. **The three sections are written in the guide, in the skill's terms,** each pointing to the rule it explains: "Why split an ontology into modules" (§2, beside the module policy), "Deciding between sources" (§2, after source of truth and scope) and "The integration-module pattern" (end of Step 7), with one worked case in the guide's library-lending domain.
3. **The skill's consumer rule follows EPM-DEC-001-0097, item 6:** an agent may quote a measure's value taken through the source the catalog binds to that measure, naming it; computing a value from the graph and quoting from an unbound source stay refused.
4. **The neutrality guard moves with the guide** as the skill's `scripts/test_playbook_guide.py`, with its fixed list of terms and a test that each kind is caught. The checks that read EPM's released packages and tracked paths stay behind, because the skill cannot see them; review catches the rest, as REVIEW_STANDARDS.md rule 5 says. `epm_facts.py playbook`, its tests and its `check.sh` line are removed.
5. **EPM deletes its copy.** Live documents point to the skill's guide; the worklog's §8 evidence map stays and illustrates the guide section by section. Released packages and historical records that cite `ontology-playbook.md` keep their citations, because a released package never changes and a record states what was true when it was written.

## Alternatives considered

- **Keep the playbook in EPM and copy it to the skill.** Not chosen: two copies of one method drift, and the skill already holds the rules.
- **Keep the guard's package and path checks in the skill.** Not chosen: they read one repository's releases and files, which a general skill cannot see.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-25-item-e.md`: "can you add this and the decision tier to the plan to be added to the Playbook? Even though the playbook is generic... these are great exmaple of how to think about an Integration module and how to make decisions on sources. Also add a section in the playbook about why it is important to vreak an ontology into modules like we did here."; "4. Should we move to he ontology skills itesef since the Playbook is a guide on how to create an ontology. what do you think?"; "Item E: the three playbook sections, and move the ontology playbook into the ontology skill."

## Evidence

- personal-agent-skills, branch `ontology/playbook-guide`: `references/playbook.md`, `references/integration.md`, `scripts/test_playbook_guide.py`, `SKILL.md`, `README.md`.
- The skill's rules the new sections explain: `foundations.md`, policies 3 and 8; `integration.md`, rules 25 to 28.

## Consequences

- `scripts/check.sh` no longer runs a playbook check; the skill's `scripts/check.sh` runs the guide's test.
- REVIEW_STANDARDS.md rule 5 and the ontology README name the guide's new home.
