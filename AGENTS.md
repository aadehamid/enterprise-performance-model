# Agent instructions — Enterprise Performance Model

Shared instructions for coding agents working in this repo (Claude Code reads
this file via `CLAUDE.md`; Codex and Cursor read it directly). Start with
`README.md` for orientation and `EPM-FOUND-000.md` for the master index.

## Working rules

- **Every change goes through a pull request.** A reviewer merges or HOLDs.
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
- **Don't mark anything Decided or Approved without Hamid's recorded
  decision.** A merge alone doesn't decide or approve it.
- Before modeling the ontology, start at `business_architecture/ontology/README.md`.
  It points to the playbook (the method) and the worklog (the build record).

## Before every push

Run these before you open a pull request, and again before you push a review fix. Fixes get the same checks as first pushes.

1. **`scripts/check.sh` passes.** It runs the Step 4 gate, every test (including the check that published figures match the source), `epm_facts.py counts` and the decision-record check. CI and the pre-push hook (`git config core.hooksPath scripts/hooks`) run it too.
2. **Figures come from `python3 scripts/epm_facts.py`** (`counts`, `row REL-xxxxx`, `section <issue>`), never from memory or a summary. Quote its commit line in the PR body.
3. **External facts cite a primary source**: release notes, a changelog, a specification or a filing, with version and date. A version claim names the first release with full support, not a preview.
4. **A change reaches every place it applies.** Run `python3 scripts/epm_facts.py find "<text>"` for every status, rule, term or figure you change; it also finds text split across lines. When you change a rule, walk every section that depends on it.
5. **Codex reviews the diff, and every finding is fixed or answered.** Claude Code: `node ~/.claude/plugins/cache/openai-codex/codex/<version>/scripts/codex-companion.mjs adversarial-review --base main "<claims to verify>"`. Codex CLI: `codex review --base main` (it rejects a prompt combined with `--base`). Record any disagreement on a judgement call in the PR body.

Say in the PR body that these ran and what the review found.

## Agent skills

### Issue tracker

Issues are tracked in this repo's GitHub Issues via the `gh` CLI; PRs aren't a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

The default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context, using the EPM artifacts: business glossary EPM-GLOS-001 and decision records EPM-DEC-001 under `business_architecture/domain/`, plus the existing decision logs. See `docs/agents/domain.md`.
