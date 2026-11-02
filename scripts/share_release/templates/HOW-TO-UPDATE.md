# How to update this ontology

This release is your starting point. Your copy is yours to change: add a module, change a module, reword a definition, add a process. This guide says what to do and who decides. Use whichever tools you prefer to do it. Every command here has been run on this release.

**Who decides.** Your ontology owner is the person your organisation names to decide what the ontology means. A module owner is the person they name for one module. The ontology owner approves every major release and every module's first release. The module owner approves minor and patch releases. Until a module has an owner, the ontology owner decides for it.

**What the words mean.** A *module* is one part of the ontology with its own version, such as `kpi`. A *package* is one released version of a module: the folder `business_architecture/ontology/releases/<module>/<version>/`. A package never changes after its release. A change makes a new package.

Commands below start from the top folder of your copy unless they say otherwise. They use this shorthand, so define it first:

```sh
py() { uv run -q --no-project --with rdflib --with pyshacl --with openpyxl --with jsonschema --with pytest --with "markdown-it-py>=4,<5" python3 -B "$@"; }
ONT=business_architecture/ontology
```

The versions in the worked commands are those of this release as you received it. After your first change, read the one you hold, from `$ONT/release`: `py next_version.py current kpi`.

## Start here

1. Make your own copy. A Git clone keeps your history; an unpacked export works too. The process-map section says what changes without Git.
2. Check that the copy works before you change it. The script takes about {{CHECK_MINUTES}} minutes:

   ```sh
   bash scripts/check.sh
   ```

3. Run `scripts/check.sh` again after each change. It proves your copy is valid: every package equals a fresh build of its sources, the shapes conform, the competency questions answer and the tests pass. Do not share a change until it passes. In a Git copy, run `git add -A` first, because one test reads which generated pages Git tracks. The log shows skipped tests and a line that starts `FAIL a store request`. Both are expected. Most skipped tests read what this release does not hold, a few depend on your machine, and adding `-rs` to the script's pytest line prints each reason. The `FAIL` line is a test of a failure. The last line, `all checks passed`, tells you the result. Do not edit files while the script runs: it compares the tree at its start and end, and a change fails the run. Commit when it passes. To try one test file first, run `py -m pytest -q <file>`, which takes seconds.

## Patch, minor or major

Classify every change before you make it, then ask your owner to approve it. `skills/ontology/references/release.md` holds the full rules; rules 3 and 4 are the ones you use most.

| Kind | What it covers |
|---|---|
| Major | An IRI changes or a concept is removed; a definition's meaning changes; a hierarchy change alters what a concept means; any deprecation. A new module's first release, 1.0.0, also counts as a major of that module, so your ontology owner approves it |
| Minor | New concepts, aliases, references, instances or shapes that existing content already meets |
| Patch | Typos; clearer wording with the same meaning; an added example or scope note |

Use this test: would every query, report and answer made under the old definition still be correct under the new one? If yes, it is a patch or a minor. If no, or if you are unsure, it is a major.

**Never delete a term.** Mark it `owl:deprecated true`, add `dcterms:isReplacedBy` for its successor, keep its triples and say why in the changelog. Do this only in a major release.

## The release steps

Every change below ends with these steps. Run them once for the module you changed and once for each module that depends on it.

1. List the modules to release, in order. The first line is the one you changed. `core` is the exception: its list holds only the modules that depend on it, because you release `core` by hand first ("Change a process"):

   ```sh
   (cd $ONT/release && py dependents.py kpi)
   ```

2. Save the approval. Create the folder `$ONT/approvals/` if you have none, and write the sentence that approved the release in a file there, such as `$ONT/approvals/2026-11-01-kpi.md`. One file can cover all the modules of one change. That file is your decision record unless your team keeps its own.
3. For each module in that order, set its version, write its package, and move its old package. `next_version.py` does the edits; `pins` has no effect in this release, so leave it. A module that only takes the new version of what it requires gets a patch.

   ```sh
   cd $ONT/release
   py next_version.py start kpi 1.3.1 patch --why "Reworded Unit Utilization's definition; the meaning is the same." \
       --approver "The kpi module owner" --where "approvals/2026-11-01-kpi.md" --words "Approved as a patch."
   py build_module.py kpi --write
   cd ../../..
   ```

   `start` sets `version`, `issued`, `approver` and `approval` in the module's entry in `build_module.py`, and adds a section to the top of `$ONT/releases/<module>/CHANGELOG.md`, carrying forward any known gap. Edit that section when you have more to say. `start` leaves the entry's `decisions` list alone, so add your approval file there if you want the package's manifest to name it. Nothing fails without it. **The write stops if the version is already released and the content differs.** Raise the version first, because a released package never changes. Before the package is shared, you may correct it with `--rebuild-released`.

4. When every module in the list is written, finish each one. This moves the old package to `$ONT/releases/previous/<module>/`, which keeps every earlier package, and changes the version in `$ONT/projection/pipeline.py` (`PACKAGES`) and `$ONT/projection/skill-run/epm-config.json` (`packages`):

   ```sh
   (cd $ONT/release && py next_version.py finish kpi 1.3.0)
   ```

5. Rebuild what follows from the packages, and check:

   ```sh
   (cd $ONT/release && py build_catalog.py --write)
   (cd $ONT/projection && py pipeline.py build)
   (cd $ONT/regression && py run.py)
   git add -A
   bash scripts/check.sh
   ```

   After a change, the script prints a note that the projection report describes an earlier build, until you project into Neo4j again. The note does not fail the check.

## Change a concept's definition

The worked example changes the definition of the measure Unit Utilization in `kpi`. The wording changes and the meaning does not, so it is a patch.

1. Find where the definition lives. A release is built from its sources, never edited in `releases/`. Most sources are tables and Turtle files in the module's folder, so search there for the text. A file that starts "Built by" is generated: edit the source it names. For `lane`, that is `business_architecture/business_process/office_lanes.json`, and rewording a lane there is still a release of `lane`.

   ```sh
   grep -n "unit-utilization" $ONT/kpi/measure-details.csv
   ```

2. Edit the text in that file. Keep the citation of its source. If the new wording rests on a new source, cite it.
3. Rebuild the module's source file. Each module has its own builder in its folder, listed in `scripts/check.sh`:

   ```sh
   (cd $ONT/kpi && py build_measures.py --write)
   ```

4. Follow the release steps for `kpi`.
5. Search the whole copy for the old wording, and update each document that quotes it. No check catches a copy of a sentence. This command leaves out this guide, which quotes the wording as its example, and the packages, which never change. In a plain folder with no Git, use `grep -rn` and skip the same paths. For this example:

   ```sh
   git grep -n "as a share of its constrained capacity" -- . ':!HOW-TO-UPDATE.*' ':!business_architecture/ontology/releases/'
   ```

If the meaning changed, the release is a major, and your ontology owner approves it.

## Add a concept or property

The worked example adds a property `kpi:reviewCadence`. It adds and removes nothing else, so it is a minor.

1. Add the term to the module's `vocabulary.ttl`, with `rdfs:label`, `skos:definition`, and its source in `dcterms:bibliographicCitation`. Copy a neighbouring term of the same kind, because the module's tests may ask for more: `kpi`'s ask for one `rdfs:range` and one kind. When the source is your owner's request, cite the file that holds their approval.
2. Add what checks it to the module's `shapes.ttl`. Each property on a class states its cardinality in a `sh:property` line on that class's shape. If the module also has a closed shape, add the property to its `sh:ignoredProperties` list too. `kpi/shapes.ttl` needs both: the `sh:property` line on `shp:Measure`, and the list on `shp:NoValuesOnMeasures`.
3. For a value on instances, add a column to the module's table and to its builder, then run the builder with `--write`. Use the table that holds fields of the same kind, such as `kpi/measure-details.csv` for a measure's `grain` and `basis`. Give every row the column, even when it is empty, because a short row passes with no warning. A concept in a code list is a new row in that table.
4. Add a test that names the term, in the module's `test_*.py`.
5. Follow the release steps for the module.

## Change a process

The process map is the source of the taxonomy in `core`. Every module depends on `core`, so this is the widest change. A change to an existing process's meaning is a major. A new process is a minor.

1. Add the node to `business_architecture/business_process/downstream_process_map.json`, with its `id`, `level`, `name` and `description`. The builder makes the description's first sentence the definition and the rest the scope note, so put the whole definition in the first sentence.
2. Add its row to `$ONT/build/output/step2-identity-map.json`, beside its siblings, with the same fields as they have. The description belongs in the map only. Copy `minted` and `deprecated` from a sibling: `false` for an ordinary new process.
3. Save the approval, as the release steps say, because the builder below names it. Commit, and note the commit before your change and the commit of the change. `scripts/check.sh` does not pass on this commit, because the map has a node that `core` lacks yet, so do not share it. The builder compares the two copies of the map. In a plain folder with no Git, choose a label for each instead, at least 12 letters or digits long.
4. Save both copies under `$ONT/release/frozen/`. Each file's name starts with the first 12 characters of its commit or label:

   ```sh
   M=business_architecture/business_process/downstream_process_map.json
   git show <earlier commit>:$M > $ONT/release/frozen/<first 12 of earlier>-downstream_process_map.json
   git show <your commit>:$M > $ONT/release/frozen/<first 12 of yours>-downstream_process_map.json
   ```

5. Copy the core builder and fill in the block it marks. `build_core_template.py` follows `build_core_2_3.py`, the builder that added a node. To change an existing node's ID or description, read `build_core_2_2.py`, which applies those changes.

   ```sh
   cp $ONT/release/build_core_template.py $ONT/release/build_core_2_5.py
   ```

   These names are for the first change to this release. A later change raises them. A patch of `core` is a new builder too, named for its major and minor.

6. Write its changelog, `$ONT/releases/core/CHANGELOG-2.5.0.md`, in the form of `CHANGELOG-2.4.0.md` beside it: the title line `# core changelog`, a heading with the version and date, one sentence on the kind of release, and a line per change.
7. Add a short test, `$ONT/release/test_build_core_2_5.py`, that says what the release adds and that it removes no IRI. Add it to the test list in `scripts/check.sh`.
8. Write the package and move the old one:

   ```sh
   (cd $ONT/release && py build_core_2_5.py --write)
   mkdir -p $ONT/releases/previous/core && mv $ONT/releases/core/2.4.0 $ONT/releases/previous/core/2.4.0
   ```

   `scripts/check.sh` reads the newest core builder and the builders read the newest core package, so neither needs an edit.
9. Rebuild every module's source files, since they read `core`. The list is in `scripts/check.sh`, after the comment on each module's source Turtle. Each runs from its folder with `--write`.
10. Follow the release steps for the modules `dependents.py core` lists. For `core` itself, you have already written the package and moved the old one, so change its version by hand in `PACKAGES` and in `epm-config.json`.

## Add a module

Copy `$ONT/lane/`, the smallest module: a README, `vocabulary.ttl`, `shapes.ttl`, a build script, its output and its test. Keep the shape of its build script and test, and rewrite their content: `test_lanes.py` pins `lane`'s versions, and `build_lanes.py` reads two JSON files outside the folder. Read `skills/ontology/references/new-module.md` first. It says when a new module is the right answer, and it holds the full method for a large module. For a small module, this section is enough. Name the competency question the existing modules cannot answer. Your ontology owner approves a module's first release, and names its owner. Write that name in the approval file, because no other field holds it.

`next_version.py` works on modules already in `MODULES`, so write this first entry and changelog by hand. Each module has a table or a Turtle source and one builder. `build_lanes.py` is in the `lane` folder, and `kpi` is built by `build_measures.py`. Name yours for what it builds, and give it `--write` and `--verify`.

Register the module in every place below. A place you miss fails a check or leaves the module out of a store.

| Place | What to add |
|---|---|
| `$ONT/release/build_module.py` | An entry in `MODULES`: title, description, version, stage (`None`), approver, approval, issued, parts, shapes, `depends_on`, pins and decisions |
| `$ONT/releases/<module>/CHANGELOG.md` | A new file: a title line, then the section for its first release |
| `scripts/check.sh` | The builder's `--verify`, `build_module.py <module> --verify`, and the test file in the test list |
| `$ONT/projection/pipeline.py` | `PACKAGES`, `OWN` and `PREFIXES` |
| `$ONT/projection/skill-run/epm-config.json` | The version under `packages`, the namespace under `own_namespaces`, the prefix under `prefixes` |
| `$ONT/regression/` | Its questions in `expected.csv`, a query in `queries/`, and the module's files in the list in `run.py` |
| `$ONT/validation/test_all_module_shapes.py` | Its `shapes.ttl` in `SHAPE_FILES` |
| `$ONT/competency-questions.md` | Each new question, numbered after the last, in the section it fits or a new one. "Locked" there, and "44 questions" in `$ONT/epm-ontology-guide.html` and `$ONT/regression/run.py`, describe this release's set: your owner may add to it. No check reads the count, so change it where your readers use it |
| `scripts/epm_facts.py` | An entry in the `coverage` table, if processes link to the module |
| `$ONT/MODULES.md` | A section on the module, with a `<!-- module: name -->` example, and a row in the table under "The three files of each package" |
| `scripts/build_docs_html.py` | The module's folder in `MODULE_READMES`, then run the builder for its HTML page |
| `$ONT/authority/source-tiers.csv` | A row with its evidence tier, for each `dcterms:source` the module cites; `build_source_tiers.py` and `vocabulary.ttl` in that folder define the five tiers: 1 process authority, 2 MPC, 3 peers, 4 industry and 5 framework. Choose the tier of the kind of source it is. Run `build_source_tiers.py --write` in that folder. This table is part of `integration`, so release `integration` as a minor after your module. A source written only as a `dcterms:bibliographicCitation` needs no row |
| `$ONT/placement/vocabulary.ttl` | Optional. A placement kind for a property that links to a process, as `lane:officeLane` has, if a competency question reads it |
| `$ONT/projection/skill-run/queries.json` | Optional. A saved "walk" that starts from one of the module's terms |
| `integration`'s entry in `build_module.py` | Not now, unless the row above releases it. Add the module to `depends_on` the next time `integration` is released, if `integration` links to it. A tier row is not a link |

Then build, in this order, starting with the module's own builder:

```sh
(cd $ONT/<module> && py build_<your builder>.py --write)
(cd $ONT/release && py build_module.py <module> --write)
# Only if you added a row to source-tiers.csv: rebuild the table and release integration, as the release steps say.
(cd $ONT/authority && py build_source_tiers.py --write)
# 2.6.0 and 2.5.0 fit the release as you received it. Read yours: next_version.py current integration.
(cd $ONT/release && py next_version.py start integration 2.6.0 minor --why "Adds the new module's source." --approver "Your ontology owner" --where "approvals/your-file.md" --words "The sentence that approved it.")
(cd $ONT/release && py build_module.py integration --write)
(cd $ONT/release && py next_version.py finish integration 2.5.0)
# Then, always:
(cd $ONT/release && py build_catalog.py --write)
(cd $ONT/projection && py pipeline.py build)
py scripts/build_docs_html.py
git add -A
bash scripts/check.sh
```

## The cascade

A package names the exact version of each module it requires. So a new version of a module means a new version of every module that depends on it. `dependents.py` lists them, each after what it requires. Raise each version before you write its package, and write them in that order. A module that only takes the new version of what it requires gets a patch, with a changelog line that says so. A change to `core` reaches every module, so use a loop. It patches each module on the list and then finishes them all, and it stops at the first failing step. For any other module, change the list to `py dependents.py <module>`, and start the loop with `for m in $(echo "$list" | tail -n +2)`, which leaves out the module you released yourself.

```sh
(
  set -e
  cd $ONT/release
  moved=""
  list="$(py dependents.py core)"
  for m in $list; do
    old=$(py next_version.py current "$m"); new="${old%.*}.$(( ${old##*.} + 1 ))"
    py next_version.py start "$m" "$new" patch --why "Takes the new version of what it requires; nothing else changes." \
        --approver "Your ontology owner" --where "approvals/your-file.md" --words "The sentence that approved it."
    py build_module.py "$m" --write
    moved="$moved $m:$old"
  done
  for pair in $moved; do py next_version.py finish "${pair%:*}" "${pair#*:}"; done
)
```

## Keep the catalog, regression and projection current

- **Catalog:** `build_catalog.py --write` rebuilds `$ONT/releases/catalog.ttl` from the packages on disk.
- **Regression:** `regression/run.py` runs the competency questions. A new question goes in `regression/expected.csv`, with its query in `regression/queries/`.
- **Projection manifest:** `pipeline.py build` checks the projection's rules and records the hash of every input. `scripts/check.sh` fails until you run it after a change.

## Project into Neo4j and Jena

The packages are the source. Neo4j and Jena are copies that you can empty and reload. `scripts/check.sh` does not need them: when the stores are behind, it prints a note and still passes. One command, `rebuild_stores.py`, loads both from an environment file, in about five minutes. You need Docker, Java 11 or later and ROBOT 1.9.10 at `~/epm-lpg/robot.jar`; the script refuses any other file. By default the local Neo4j listens on port 17711 and Jena on 13031. `$ONT/epm-walkthrough.html`, "Connect and load every store", says how to get ROBOT and explains each step, and `$ONT/projection/ontology-stores-runbook.html` shows each store hands on.

1. Copy the environment file outside your copy, and let only yourself read it. The script refuses a file that others can read. Every key has a default, so for these two stores you can leave the file as it is.

   ```sh
   mkdir -p ~/.config/epm
   cp $ONT/projection/skill-run/environment.example ~/.config/epm/qa.env
   chmod 600 ~/.config/epm/qa.env
   ```

2. List the steps. This changes nothing. Name the two stores, because the default is all four, and the other two need logins:

   ```sh
   python3 $ONT/projection/rebuild_stores.py --env ~/.config/epm/qa.env --store driver --store jena --plan
   ```

3. Load the stores. **`--empty` replaces what the two stores hold.** Without it, the script refuses a store that holds data.

   ```sh
   python3 $ONT/projection/rebuild_stores.py --env ~/.config/epm/qa.env --store driver --store jena --empty
   ```

   The script stops at the first failing step and names it. The load fails if it lost a triple, added one or found a violation. The script also takes the result into `$ONT/projection/` and checks the stores against your packages.
4. Commit `inferred.nt`, `projection-manifest.json` and `projection-report.json` from `$ONT/projection/`. `scripts/check.sh` then stops printing its note, and `python3 scripts/epm_facts.py projection` prints the new figures.
5. To see later which store is behind your newest packages:

   ```sh
   (cd $ONT/projection && uv run -q --no-project --with rdflib --with neo4j python sync_stores.py check --ref worktree --store driver --store jena)
   ```

## The optional check against this release

`scripts/check-pinned.sh` asks a different question from `scripts/check.sh`: does your copy still equal {{RELEASE_NAME}} as shipped? Its tests pin versions, counts, approvals and the figures in the guide. They pass on the release as shipped. After your first change some of them fail, and that means only that your copy has moved on. Ignore them from then on, or edit `scripts/pinned-tests.txt` when you want your own pins.

The documents that state figures or versions, such as `$ONT/epm-ontology-guide.html` and the module READMEs that name a core version, describe {{RELEASE_NAME}}. They do not update themselves. Update the ones your readers use.

## The namespace

The IRIs begin with `https://w3id.org/mpc/ontology/`. Keep them as working names unless you have a reason to change them. They identify terms and resolve nowhere. A term's IRI is its identity, so a change is a major release of every module.

If you do change the namespace, do it first, before other changes, and with your ontology owner's approval:

1. Raise `core` and every module to the next major version, following the sections above.
2. Replace the base in the sources: the module folders, the process map's identity map, the builders, `$ONT/projection/`, the shapes and the regression queries.
3. Leave `$ONT/releases/previous/` alone. Those packages keep the old IRIs, because a released package never changes.
4. Write every package again in the order `dependents.py core` prints, and run `scripts/check.sh`.

## What you can ignore

These describe how the ontology was first built. You need none of them to update it:

- `$ONT/epm-walkthrough.html`, Part 2, and `$ONT/build/`, apart from the identity map named above.
- `$ONT/step4/` and the older core builders, `build_core_next.py` and `build_core_2_1.py`, which rebuild earlier releases.
- `$ONT/release/frozen/`, apart from the copies you add.
- `business_architecture/domain/decision-packages/`, questions put to the subject matter expert during the build.
- `$ONT/business-closeout.md`, and any note in a README or changelog dated before you received this release.
