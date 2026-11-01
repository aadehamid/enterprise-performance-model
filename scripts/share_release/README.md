# The share release

One command builds a release of the ontology and demo for people outside the build, from `main` and the
skills repository's `main` (the decision of 2026-10-31, EPM-DEC-001-0110, and its amendment). This folder is
the tool; it never ships.

```sh
scripts/share_release/cut.sh --epm . --skills ../personal-agent-skills --out /tmp/release --env <stores env> \
    [--baseline <main's validate json>] [--no-cleanroom]
```

`cut.sh` runs the steps below in order and stops at the first failure: export, rebuild, gate, the store rows on
the test stores (`--env` names them; the projection's load-verify writes the release's own report and figures),
the release's `check.sh`, the tree rows, the comparison with main, every snippet, the gate again, the zip, the
clean room, and with `--baseline` the validation report. Each step writes beside the output folder. By default
the store rows are the four that need no Databricks workspace; `--store-rows all` adds the driver, the live demo,
the technical graph and the store sync when the workspace is reachable. The command refuses an `--out` that is
the root, the home folder, a checkout or a parent of one, or a folder holding anything but a release. Its last
line names the rows that did not run and the two steps that follow by hand: step 9, `cleanup.py --yes` from the
ledger (`LEDGER_FILE` in `--env`) with the AuraDB reload from main, and step 10, `publish.py branch` and the
push, which wait for the owner. The export alone is:

```sh
python3 scripts/share_release/export.py --epm . --skills ../personal-agent-skills --out /tmp/release
```

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
  the one table the `skills-tests` row runs too. It needs the builders' release mode (`frozen_sources.py`,
  `build_module.package_folder`, `scripts/conftest.py`), which the branch `release/builders-frozen-sources` adds.
- `gate.py` fails on any name, handle, repository, host, peer (by name, ticker or EDGAR filing), record number
  (full or short form), issue number, left-out document or double-underscore graph name; names match whole words;
  binaries and base64 data are read as the printable text inside them.
- `validate.py`, `stores.py` and `snippets.py` are the validation: each row judges what it finds (a planted
  violation fails it), every command exits nonzero on a failure, and no output file holds a password.
- `publish.py` writes the zip and the orphan branch from the same file list, the branch with a neutral author
  and committer; `cleanroom.sh` unpacks the zip keeping each file's mode and runs `./scripts/check.sh`.
- `cleanup.py` removes only what the ledger names, refuses the root, the home folder and any folder holding a
  checkout, and exits 0 only with proof that everything is gone.

The option `--remove-internal` leaves `reference/internal/` out. It is off by default, and the plan says a
review report of what changes comes before anyone turns it on.
