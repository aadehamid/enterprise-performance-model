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

Run these four checks before you open a pull request, and again before you push a fix for review feedback. Many misses in this repo came from review-fix pushes, so a fix gets the same checks as the first push.

`scripts/check.sh` runs the automated part (the Step 4 evidence gate, every test, `epm_facts.py counts` and `epm_facts.py decisions`) in about 3 seconds. CI runs it on every pull request, and the pre-push hook runs it locally once you enable it with `git config core.hooksPath scripts/hooks`.

1. **Figures come from the source file.** Recompute every count, total and ID list with a script that reads the source file (a CSV, the ledger, the workbook). A figure from memory, a summary or an earlier message does not count. For Step 4 and Phase 1 figures, use the shared tool rather than a script of your own: `python3 scripts/epm_facts.py counts` (ledger, gate, facts, Phase 1 rows, review holds, taxonomy), `row REL-xxxxx` (one row's status) and `section <issue>` (one issue's rows). Each prints the files it read and the commit; quote that line in the PR body. Add `--json` for machine-readable output. When a helper script classifies review rows, count a hold only from the `Hamid_decision` column, and count every non-blank cell there that records a hold, whatever its wording ("HOLD …", "Held for source correction", "Carry forward (remains held)"). Ignore other columns, such as `review_section` ("RECONCILED — already held"), and treat a blank `Hamid_decision` as no new verdict.
2. **External facts come from a primary source.** Cite release notes, a changelog, a specification or a filing, with its version and date. An open issue tracker, a search snippet or a third-party summary is a lead, not a source. A version claim names the first release that fully supports the feature, not the first preview.
3. **A change reaches every place it applies.** When you change a status, a rule, a term or a figure, search the whole repo for every mention of it, including text split across lines (`python3 scripts/epm_facts.py find "<text>"` reports both), and update each one. When you change a rule, walk every section that depends on it (later pipeline steps, checklists, examples, companion docs) before you push.
4. **An independent review runs on the diff.** Run a Codex review and fix what it finds before you push:
   - Claude Code (Codex plugin), with focus text: `node ~/.claude/plugins/cache/openai-codex/codex/<version>/scripts/codex-companion.mjs adversarial-review --base main "<what to check>"` (or `--scope working-tree` before a commit). In the focus text, name the claims to verify and the documents that must stay consistent.
   - Codex CLI, without focus text: `codex review --base main`, or `codex review --uncommitted` before a commit. The CLI rejects a prompt combined with `--base` or `--uncommitted`.
   Fix clear defects. Record any disagreement on a judgment call in the PR body for the reviewer, with your reasoning.

Done when all four hold, each as its check defines it:

- Every figure in the diff was recomputed by a script from its source file, reading the column check 1 names.
- Every external fact cites a primary source, and a version claim names the first release the source says fully supports the feature, not a preview.
- The repo-wide search, including text split across lines, finds no stale mention of anything you changed.
- The Codex review has no unaddressed finding.

Say in the PR body that the checks ran and what the review found.

## Agent skills

### Issue tracker

Issues are tracked in this repo's GitHub Issues via the `gh` CLI; PRs aren't a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

The default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context, using the EPM artifacts: business glossary EPM-GLOS-001 and decision records EPM-DEC-001 under `business_architecture/domain/`, plus the existing decision logs. See `docs/agents/domain.md`.
