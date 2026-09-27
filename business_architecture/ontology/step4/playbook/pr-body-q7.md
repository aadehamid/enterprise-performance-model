# DO NOT MERGE — awaiting Hamid's review

## What this PR does

Documents the Step 4 Q7 responsible-domain interim treatment in the
playbook's decision log (Modeling).

## Change inventory

`business_architecture/ontology/ontology-playbook.md` only — one new
decision-log entry:

- **Responsible-domain interim treatment (2026-09-22).** Step 4 keeps
  `responsible_domain` as a governed literal on the process, explicitly
  interim — no org nodes minted in 1.0.0. Step 5 (ORG/RACI) designs the
  org model and replaces the labels with references to real org
  units/roles; the controlled list makes that migration mechanical.
  Notes the evidence (10 distinct values, 456/485 "Commercial &
  Marketing", value in the exceptions) and the cross-functional
  normalization (governed "Cross-functional" value, detail in a note).

## Deliberately unchanged

- Everything else, including the open versioning (PR #111) and Q5
  (PR #112) playbook PRs.

## How to review

Read the new entry. Check it matches the approach as you understood it
— particularly that "explicitly interim, replaced by Step 5" is the
right contract for the team.
