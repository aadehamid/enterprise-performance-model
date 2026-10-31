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
clean room, and with `--baseline` the validation report. Each step writes beside the output folder. The export
alone is:

```sh
python3 scripts/share_release/export.py --epm . --skills ../personal-agent-skills --out /tmp/release
```

- `manifest.py` says what ships: the allowlist of paths, the two versions of each module, and the renames
  (the peer evidence folder becomes `reference/industry-view/`, the previous release of each module moves
  under `releases/previous/`, the skills land under `skills/<name>/`).
- `rules.py` holds the rewrite rules, in order, each named. `test_rules.py` pins each one on a planted line.
- `export.py` copies the allowlist, applies the rules to every text file, keeps binaries byte for byte, and
  writes `<out>-report.json` beside the release with every rule's count per file, so each difference between
  `main` and the release traces to a rule. It reads no Git history.
- The rebuild of packages, pages and hashes (`rebuild.py`) and the leak gate (`gate.py`) follow in their own
  changes, as the plan's steps 4 and 5.

The option `--remove-internal` leaves `reference/internal/` out. It is off by default, and the plan says a
review report of what changes comes before anyone turns it on.
