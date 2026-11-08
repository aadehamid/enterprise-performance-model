# Offline ontology reference

This folder builds a reference and usage guide for every current ontology module from the existing private release. Readers open `horoi_viewer/index.html` after unzipping the release. The page embeds its data, styles and scripts and needs no server or internet.

The overview explains the reading groups: business concepts, vocabulary, and rules and evidence. Module pages lead into terms and cross-module connections. Each term shows its definitions, scope notes, relationships, incoming statements and all recorded facts. The guide provides customer and process reading paths. Cross-module term links stay in the reference. The original full viewer remains available as an alternative view.

The design adapts Horoi's page styles at the commit in `config.json`. Horoi's upstream renderer lists OWL classes and properties using `rdfs:comment`. This adaptation supports the released SKOS terms, `skos:definition`, multiple namespaces and supporting nodes. `NOTICE.txt`, `vendor/LICENSE` and `vendor/upstream.json` record the source, licence and unchanged vendored bytes. It uses no Brick or RDF Garden code.

## Guided explorers

The reference includes every current module from the pinned release under the 2026-11-07 amendments to EPM-DEC-001-0114. Process, Customer lifecycle and both value-stream explorers offer guided entry points across those modules. Publication still requires review of the final candidate.

Open **Processes** to expand the process tree from its roots. Select an item to read its definition, find its parent and children, and follow its connections. Levels come from the released taxonomy; the viewer does not stop at a fixed depth. The tree follows `skos:broader`, which describes hierarchy rather than workflow order. Multiple parents remain visible. Cycles stop expanding and link back to the existing item.

Open **Customer lifecycle** and choose a stage. The stage list is alphabetical because the source does not assert a sequence. Follow `stageProcess` to a process or `correspondsTo` to a system stage. Follow that stage's `stageSystem` statement to a system. Each connection card keeps the subject, predicate and object in their original order. Incoming connections can be followed without reversing their meaning.

Open **Value streams** and choose Commercial Hydrocarbon Lifecycle or Order to Cash. Each view shows the recorded trigger, outcome and stage positions. Open a stage to choose one of its processes, then follow its connections into the process tree, capabilities, data products, measures or other concepts. The sidebar keeps the starting value stream available throughout the path.

Stage membership follows `hasStage`; process membership follows `hasProcess`. Stage order follows the numeric `sequence` values. Processes within a stage are listed alphabetically because membership does not establish their execution order. Missing, ambiguous or shared stage positions are disclosed. The `feeds`, `informs` and `loopsTo` connections keep their recorded meanings. A value-stream process and the process-map concept it `realizes` remain separate items, even when their labels match.

The connection trail retains the statements followed, including across modules. Parent and child links retain that trail. Selecting a new item in the process or customer sidebar, or in process ancestry, starts a new trail. Value-stream stage and process choices start a recorded path from their stream. A repeat visit returns to the earlier item; after 100 hops the link explicitly starts a new trail. The explorer and primary reference can inspect connected concepts across every included module.

Run the focused explorer checks with:

```sh
node horoi_viewer/test_explorer_model.cjs
NODE_PATH=<node_modules> node horoi_viewer/test_explorers.mjs \
  <staged-release>/horoi_viewer/index.html <evidence-folder>
```

These checks cover hierarchy depth, multiple parents, cycles, duplicate labels, asserted trails, complete adjacent statements, real customer and value-stream paths, stage ordering and membership, keyboard navigation, browser history and offline layouts. The Python reference suite also runs the model checks and requires Node.js. Run the existing reference checks as well. Full repository checks and independent review follow reader agreement on the design.

## Build

Use Python with the pinned RDFLib dependency:

```sh
uv run --with rdflib==7.6.0 python horoi_viewer/build.py \
  --source <clean-release-clone> --out <new-output>/horoi_viewer
```

The source must be the commit named by `config.json`. The builder checks the checkout's bytes and executable modes, refuses untracked documentation inputs, and uses the existing viewer reader to verify package hashes and keep blank nodes separate across files. It preserves literal lexical forms, languages and datatypes. It reads only current release packages and their catalog. It does not change packages, use live stores, or infer relationships. With `modules` set to `all` in `config.json`, the builder derives the navigation scope from every current release manifest. Supporting nodes remain reachable through term details and the Rules and evidence search group. The technical-graph vocabulary and logical-model module are included; operational technical-graph datasets and historical package versions remain outside the source set.

The output directory must be new or empty. The builder never deletes an existing output. It emits `index.html`, `build.json`, `LICENSE.txt` and `NOTICE.txt`. Keep that folder alongside the existing `viewer/` and `business_architecture/` directories so its relative links work.

## Add documentation to the release

This documentation-only route implements EPM-DEC-001-0114. It does not invoke the full cut, package builders, cleanup or store loaders.

```sh
uv run --with rdflib==7.6.0 python -m horoi_viewer.release stage \
  --source <clean-release-clone> --docs <new-output>/horoi_viewer \
  --out <new-staging-folder> --report <outside-staging>/comparison.json
```

Staging copies every tracked baseline file with its permissions and adds only the four documentation files. Verification compares every baseline path, hash and permission mode. It compares the embedded data with the verified source packages and regenerates all four documentation files for an exact byte comparison. An extra file, missing file, changed byte, changed permission mode or changed semantic payload fails the comparison. Verify a staging folder or extracted archive without Git metadata. The comparison has no filename exemptions, including `.git`; a Git checkout must first be staged as shown above.

Choose a new audit report path in an existing directory outside the source, generated documentation and staging folders. The command refuses to replace an existing report. A failed build or staging command can leave output for inspection; choose a new folder when retrying. Only a successful verification produces an audit report.

Use the repository's ZIP tool on the verified staging folder. Extract that exact ZIP, repeat the comparison and browser check, and prepare the additions for a pull request in the private release repository. Obtain the decision owner's review of the final candidate and address their feedback before merging that release pull request or publishing the release. The original repository's reviewed implementation must land first. A documentation release tag does not change ontology module versions. No existing release file is edited, including the original viewer, README, manifests and projections.

## Verify

```sh
uv run --with pytest --with rdflib==7.6.0 python -m pytest -q horoi_viewer/test_reference.py
NODE_PATH=<node_modules> node horoi_viewer/test_browser.mjs \
  <staged-release>/horoi_viewer/index.html <evidence-folder>
```

The browser check uses `playwright-core` and installed Chrome. `CHROME_PATH` can select another Chrome executable. It opens the page through `file:`, blocks and counts HTTP requests, exercises desktop, tablet and phone navigation, follows links into the existing viewer, and saves screenshots and results. The evidence folder must already exist. Review the screenshots for readable layers, definitions and relationships; a passing script alone does not establish usability.

`scripts/check.sh` includes the Python tests. Browser validation also runs on the exact release artifact before publication. Build output and evidence stay outside the source checkout. The new release keeps all existing files unchanged, so it does not alter the existing release's tests or validation instructions.
