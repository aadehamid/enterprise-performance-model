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

## Agent skills

### Issue tracker

Issues are tracked in this repo's GitHub Issues via the `gh` CLI; PRs aren't a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

The default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context, using the EPM artifacts: business glossary EPM-GLOS-001 and decision records EPM-DEC-001 under `business_architecture/domain/`, plus the existing decision logs. See `docs/agents/domain.md`.
