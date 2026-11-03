# The share release

One command builds a release of the ontology and demo for people outside the build, from `main` and the
skills repository's `main` (the decision of 2026-10-31, EPM-DEC-001-0110, and its amendment). This folder is
the tool; it never ships.

```sh
scripts/share_release/cut.sh --epm . --skills ../personal-agent-skills --out /tmp/release --env <stores env> \
    [--baseline <main's validate json>] [--store-rows <rows>|all] [--no-cleanroom] [--replace] \
    [--augment <folder> --approval <answers file> --approval-words <words>]
```

`cut.sh` runs the steps below in order and stops at the first failure: export, rebuild, gate, the store rows on
the test stores (`--env` names them; the release's own `rebuild_stores.py` writes its report and figures),
the release's `check.sh` from the folder and from a Git clone of it (`clonecheck.py`), the tree rows, the comparison with main, every snippet, the gate again, the zip, the
clean room, and with `--baseline` the validation report. Each step writes beside the output folder. By default
the store rows are the four that need no Databricks workspace; `--store-rows all` adds the driver, the live demo,
the technical graph and the store sync when the workspace is reachable. The command refuses an `--out` that is
the root, the home folder, a checkout or a parent of one, or a file; an existing folder that is not empty is
removed only with `--replace`, and only when its `release.json` is exactly the marker this tool writes
(`manifest.is_tool_marker`: the keys `release`, `built` and `mode`, the release name, the mode text, a date, and,
for a cut with `--augment`, the key `augment` in the shape `manifest.marker` writes; nothing else is accepted). Its last line names the rows that did not run and the two steps that follow by hand:
step 9, `cleanup.py --yes` from the ledger (`LEDGER_FILE` in `--env`), then, from the release's root, `python3 business_architecture/ontology/projection/rebuild_stores.py --env <file> --empty`, which empties and reloads the stores
from the release, not from main (the owner's instruction of 2026-11-01), and ends with `sync_stores.py check`: the release is done only when every store reads current, ontology and technical graph; and step 10, `publish.py branch --zip` and the push, which wait for the owner. `--augment <folder>` adds files kept outside `main` (EPM-DEC-001-0113): each logical model in the folder, `<slug>.ttl`
(ER Studio's export) with `<slug>.links.csv` beside it, joins the release in a `logical-model` 1.0.0 package that
`main` does not have. The folder may be outside the repository, as the customer model's gitignored
`release-cut/augment/logical-model/` is, or inside it. The export copies each model's two files into
`logical-model/models/` through the rewrite rules; the rebuild runs the release's own `build_logical_model.py` on them,
registers the module in every place the release lists its modules (`augment.REGISTRATION`: `build_module.py`'s
`MODULES` and its test's approvals, the projection's `PACKAGES`, `OWN` and `PREFIXES`, `epm-config.json`, the module
lists and counts that `test_epm_facts.py` and `test_release_package_shapes.py` pin, `MODULES.md`, the module's README,
`OPEN-ITEMS.md`), builds the package with `build_module.py` (the vocabulary as `logical-model.ttl`, the shapes, each
model's two graphs as they are, `catalog.ttl`, `CHANGELOG.md`, `manifest.json`) and adds its two checks to the
release's `check.sh`. After the catalog is built, it rewrites each figure of the guide and the walkthrough that states
the release set (`augment.FIGURES`: module counts, the total, the catalog, the `releases/` folder's versions, files
and size, the graphs and triples the stores load, the release records) to the figure `augment.release_figures` reads
from the release tree, adds the module's card and rows, and keeps the figure it replaces beside it where the sentence
dates it. So the release counts one module more than `main`. Each patch stops the cut when its anchor is not found.
`test_augment.py`'s `FIGURE_CLASSES` lists every figure of the two pages, with that rewrite or why it stays.
`release.json` and the package's `manifest.json` list each outside file under `augment`, with its path relative to
the folder and its SHA-256, never the folder's own path. The gate, the release's checks, the comparison
(`validate.py compare --augment`, whose `augment` row checks the hashes and the staged copies) and the clone's check
(`clonecheck.py --augment`, whose last line says it ran with the folder) run on everything. The rules move the
module's own `lm:` IRIs and the link targets to `w3id.org/mpc`; ER Studio's namespace,
`https://www.erstudio.com/semanticmodel/`, is never rewritten, and the gate does not treat its host as a host of the
build. The package names the decision owner's approval, so the cut refuses `--augment`, before it removes anything,
until `--approval` names a saved answers file in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/`
of the `--epm` checkout and `--approval-words` is a sentence of that file's body that approves logical-model 1.0.0 by name, such as "approve logical-model 1.0.0"; an unrelated "go ahead" or a refusal does not pass (EPM-DEC-001-0113, decision 10).
Without `--augment` the cut is unchanged. The release's `README.md`, `HOW-TO-UPDATE.md` ("Add a logical model") and
the walkthrough's "How to change the ontology" carry their augment parts (between `<!-- augment -->` lines in
`templates/`) only in a release cut with `--augment`.

The export alone is:

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
- `gate.py` fails on any name, handle, repository, host, peer (by name, ticker or EDGAR filing, except in market
  news, below), record number (full or short form), issue number (also inside the IRI of an answer given as an issue comment), left-out document, the left-out `way-of-working` skill, agent or review tool, agent-work phrase or double-underscore graph name; a name matches when no letter or digit touches it, so it also fails inside an identifier such as `test_x_y`, and "Adam" or "metadata" do not match;
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
  their source, the other repositories, the graph prefixes) and `MARKET_NEWS`, the market news whose peer names
  stay: the demo's cached Parallel search results and its `SCENARIO.md` (EPM-DEC-001-0112, point 7). The peer rule
  leaves those files as they are and the gate's three peer text checks skip them (a file name is still checked); every other check still runs on them.
- `cleanup.py` removes only what the ledger names, refuses the root, the home folder, any folder holding a checkout
  and any catalog this run did not create (a test catalog's name starts with `epm_release_validate_`), and exits 0 only with proof that everything is gone.

The release is for people who only ever receive it (the decision's amendment of 2026-11-01). It names no agent or review
tool, and every decision in it reads as the subject matter expert's (rule 15). `HOW-TO-UPDATE.md` tells its readers how to
change what they got. `scripts/check.sh` in the release proves a copy is valid; `scripts/check-pinned.sh` asks whether it
still equals the release as shipped, using the list `templates/pinned-tests.txt`.

The option `--remove-internal` leaves `reference/internal/` out. It is off by default, and the plan says a
review report of what changes comes before anyone turns it on.
