# The share release

One command builds a release of the ontology and demo for people outside the build, from `main` and the
skills repository's `main` (the decision of 2026-10-31, EPM-DEC-001-0110, and its amendment). This folder is
the tool; it never ships.

```sh
scripts/share_release/cut.sh --epm . --skills ../personal-agent-skills --out /tmp/release --env <stores env> \
    [--baseline <main's validate json>] [--store-rows <rows>|all] [--no-cleanroom] [--replace]
```

`cut.sh` runs the steps below in order and stops at the first failure: export, rebuild, gate, the store rows on
the test stores (`--env` names them; the projection's load-verify writes the release's own report and figures),
the release's `check.sh` from the folder and from a Git clone of it (`clonecheck.py`), the tree rows, the comparison with main, every snippet, the gate again, the zip, the
clean room, and with `--baseline` the validation report. Each step writes beside the output folder. By default
the store rows are the four that need no Databricks workspace; `--store-rows all` adds the driver, the live demo,
the technical graph and the store sync when the workspace is reachable. The command refuses an `--out` that is
the root, the home folder, a checkout or a parent of one, or a file; an existing folder that is not empty is
removed only with `--replace`, and only when its `release.json` is exactly the marker this tool writes
(`manifest.is_tool_marker`: the keys `release`, `built` and `mode`, the release name, the mode text, a date;
nothing else is accepted). Its last line names the rows that did not run and the two steps that follow by hand:
step 9, `cleanup.py --yes` from the ledger (`LEDGER_FILE` in `--env`), then `empty_stores.py` and a reload of the stores
from the release, not from main (the owner's instruction of 2026-11-01), and step 10, `publish.py branch --zip` and the push, which wait for the owner. The export alone is:

```sh
python3 scripts/share_release/export.py --epm . --skills ../personal-agent-skills --out /tmp/release
```

A new cut is a small edit: `manifest.py` holds its facts in one place (`RELEASE_NAME`, `RELEASE_BRANCH`, `CHECK_MINUTES`,
`MODULES`), and the documents the release adds are in `templates/`.

- `manifest.py` says what ships: the allowlist of paths, the two versions of each module, and the renames
  (the peer evidence folder becomes `reference/industry-view/`, the previous release of each module moves
  under `releases/previous/`, the skills land under `skills/<name>/`).
- `rules.py` holds the rewrite rules, in order, each named. `test_rules.py` pins each one on a planted line.
- `owner.py` reads the owner's names and handle from `EPM_RELEASE_OWNER_NAMES` or `~/.config/epm/owner-names.txt`,
  never from a tracked file; the export and the gate refuse to run without them.
- `export.py` copies the allowlist, applies the rules to every text file, keeps binaries byte for byte, and
  writes `<out>-report.json` beside the release with every rule's count per file, so each difference between
  `main` and the release traces to a rule. It reads no Git history.
- `rebuild.py` rebuilds packages, pages and hashes inside the release and writes its `check.sh` from
  `templates/check.sh`, with the test files found in the tree and the skills' checks from `validate.SKILL_CHECKS`,
  the one table the `skills-tests` row runs too (`skill_checks.py`). Its freeze step relies on the builders'
  release mode (`frozen_sources.py`, `build_module.package_folder`, `scripts/conftest.py`), merged into `main` by
  pull request #460 on 2026-11-01.
- `gate.py` fails on any name, handle, repository, host, peer (by name, ticker or EDGAR filing), record number
  (full or short form), issue number, left-out document, agent or review tool, agent-work phrase or double-underscore graph name; names match whole words;
  binaries and base64 data are read as the printable text inside them.
- `validate.py`, `stores.py` and `snippets.py` are the validation: each row judges what it finds (a planted
  violation fails it), every command exits nonzero on a failure, and no output file holds a password: every
  command runs through `procs.py` (its own process group, a deadline, the whole group killed on expiry) and every
  record through `scrubbing.py` (the secrets a command was given, inherited or that the run registered, masked).
  A document's snippet runs only under `snippets.POLICY`: a listed executable with its listed options, every
  path-like operand inside the tree, a Python script only from the tree, never `-c`.
- `publish.py` writes the zip (under the fixed root `epm-release`, refusing symlinks) and builds the orphan
  branch from that zip, with a neutral author and committer; `cleanroom.py` unpacks the zip in the container
  keeping each file's mode, runs `./scripts/check.sh`, and stops the container when its deadline passes. `cut.sh`
  runs its long steps under the same deadline (`STEP_TIMEOUT`, 7200 s by default).
- `vocabulary.py` holds the leak vocabulary the rules and the gate share (peers' tickers and EDGAR filers, with
  their source, the other repositories, the graph prefixes).
- `cleanup.py` removes only what the ledger names, refuses the root, the home folder, any folder holding a checkout
  and any catalog this run did not create (a test catalog's name starts with `epm_release_validate_`), and exits 0 only with proof that everything is gone.
- `empty_stores.py` empties the stores named on its command line before they are reloaded from the release.

The release is for people who only ever receive it (the decision's amendment of 2026-11-01). It names no agent or review
tool, and every decision in it reads as the subject matter expert's (rule 15). `HOW-TO-UPDATE.md` tells its readers how to
change what they got. `scripts/check.sh` in the release proves a copy is valid; `scripts/check-pinned.sh` asks whether it
still equals the release as shipped, using the list `templates/pinned-tests.txt`.

The option `--remove-internal` leaves `reference/internal/` out. It is off by default, and the plan says a
review report of what changes comes before anyone turns it on.
