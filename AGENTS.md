# Agent instructions — Enterprise Performance Model

Shared instructions for coding agents working in this repo (Claude Code reads
this file via `CLAUDE.md`; Codex and Cursor read it directly). Start with
`README.md` for orientation and `EPM-FOUND-000.md` for the master index.

## Skills every agent loads

- **Writing for a person:** load the `clear-writing` skill first and follow it.
  That covers every reply, status update, doc, README, commit message, PR
  description and issue body, and any text the user asks you to edit. Subagents
  load it too.
- **Changing the repo:** load the `way-of-working` skill first and follow it.
  Where this file or `REVIEW_STANDARDS.md` sets its own rule, that rule wins.

## Working rules

- **Every change goes through a pull request.** A reviewer merges or HOLDs.
  Under EPM-DEC-001-0028 the PR reviewer posts MERGE or HOLD, and Claude merges
  on a MERGE for the current head. If the only unmet requirement is the approving
  review (the approval agent asked for a human), Claude merges with admin
  privileges once `checks` has passed, and says so on the PR (the 2026-10-20 admin-merge amendment).
  Address review feedback on the same branch. Don't start unrelated work while
  a PR is open.
- **`business_architecture/` takes precedence** over other folders. The process
  authority is `business_architecture/business_process/` and
  `business_architecture/schema/`. Suggest process-map changes as proposals;
  don't edit the process map directly.
- **Evidence must be close to Downstream Oil & Gas.** Order: Marathon
  Petroleum (MPC) filings and public materials (`business_architecture/reference/mpc/`),
  then U.S. refining peers' SEC filings (`business_architecture/reference/downstream-peers/`),
  then downstream-specific industry sources. Generic frameworks are support
  only. Cite every fact.
- **Don't mark anything Decided or Approved without the decision owner's recorded
  decision.** A merge alone doesn't decide or approve it. Since 2026-10-12,
  EPM-DEC-001-0028 delegates the open questions of emitting the ontology and
  updating its playbook to Claude, and since 2026-10-13 those of Steps 5 to 12: a decision in that scope made from the
  evidence order above and recorded as "delegated under EPM-DEC-001-0028"
  counts as Decided. It also sets the independent review at one or two rounds
  per PR, and names the reviewers.
- **Reviewing a pull request?** Apply `REVIEW_STANDARDS.md` (what blocks a merge) and
  `APPROVAL_POLICY.md` (when a human must review). Authors can read it before pushing.
- Before modeling the ontology, start at `business_architecture/ontology/README.md`.
  It points to the playbook (the method) and the worklog (the build record).

## Before every push

Run these before you open a pull request, and again before you push a review fix. Fixes get the same checks as first pushes, except that the independent review in item 5 runs at most twice per PR (EPM-DEC-001-0028).

1. **`scripts/check.sh` passes.** It runs the Step 4 gate, every test (including the check that published figures match the source), `epm_facts.py counts`, the decision-record and quote checks, the check that no tracked file names the decision owner (`epm_facts.py names`, EPM-DEC-001-0049), and a check that the Step 4 pin is in the branch's history. CI and the pre-push hook (`git config core.hooksPath scripts/hooks`) run it too.
2. **Figures come from `python3 scripts/epm_facts.py`** (`counts`, `row REL-xxxxx`, `section <issue>`), never from memory or a summary. Quote its commit line in the PR body.
3. **External facts cite a primary source**: release notes, a changelog, a specification or a filing, with version and date. A version claim names the first release with full support, not a preview.
4. **A change reaches every place it applies.** Run `python3 scripts/epm_facts.py sweep main`: for every line the branch changed, it lists the places that still hold the old wording, and marks those with a dated note. Then run `python3 scripts/epm_facts.py find "<text>"` for every status, rule, term or figure you change in other words; it also finds text split across lines. When you change a rule, walk every section that depends on it. When a change adds a value to a set (a ledger bucket, a status, a route) or replaces an instruction, also search the bare old figure (`686`, not `686 held`), the set's other members (`structured flow`), and the old instruction's words (`#226`, `waits for`). Review rounds on PR #231 found statements of each kind that the change had missed. When you add a dated note to a statement, also search each record ID that statement cites, in its full, short and range forms (`EPM-DEC-001-0040`, `0040`, `0040 to 0043`): on #299 another copy of the sentence, citing the same record, was missed by the sweep by wording.
5. **A different model reviews the diff, and every finding is fixed or answered.**
   Commit first; the review reads committed work only.
   - **Who reviews:** the `way-of-working` skill's "Who reviews" table
     (`references/changing.md`), as the decision owner set it on 2026-10-13 (EPM-DEC-001-0028,
     amendment of 2026-10-18). While the Cursor bot is available, Pi gives the
     independent review (`pi-review.sh --role independent`) and the Cursor bot gives
     the PR verdict. When the bot is not available, the Cursor agent CLI on Grok 4.6
     gives the independent review (`herdr-review.sh --kind cursor`) and Pi gives the
     PR verdict (`pi-review.sh --role pr`). The merged commit's two reviews come from
     different tools. While Cursor is out of usage, the Cursor agent CLI on Auto gives
     the PR verdict instead and Pi the independent review (EPM-DEC-001-0028, later
     amendment of 2026-10-20).
   - **Rounds:** at most two per PR (EPM-DEC-001-0028). Round 1 reviews the whole
     branch. Round 2 runs only if round 1 found something, and reviews the fix
     commit. A fix after round 2 gets item 1 and CI, and the PR body says it had
     no third review.
   - **If the independent reviewer the row names cannot run**, Claude Code runs `node ~/.claude/plugins/cache/openai-codex/codex/<version>/scripts/codex-companion.mjs adversarial-review --base main "<claims to verify>"`,
     and Codex CLI runs `codex review --base main` (it rejects a prompt combined with `--base`).

   Record any disagreement on a judgement call in the PR body.

Say in the PR body that these ran and what the review found. The body has a "Sweep" section: what `sweep main` reported and what the `find` searches covered, and why each place it left unchanged is right as it stands.

## Agent skills

### Issue tracker

Issues are tracked in this repo's GitHub Issues via the `gh` CLI; PRs aren't a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

The default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context, using the EPM artifacts: business glossary EPM-GLOS-001 and decision records EPM-DEC-001 under `business_architecture/domain/`, plus the existing decision logs. See `docs/agents/domain.md`.
