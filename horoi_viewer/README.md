# Offline ontology reference

This folder builds a Party/Core reference and usage guide from the existing private release. Readers open `horoi_viewer/index.html` after unzipping the release. The page embeds its data, styles and scripts and needs no server or internet.

The overview explains the reading groups: business concepts, vocabulary, and rules and evidence. Module pages lead into terms and cross-module connections. Each term shows its definitions, scope notes, relationships, incoming statements and all recorded facts. The guide provides customer and process reading paths. Links to other modules open the full viewer already supplied in the release.

The design adapts Horoi's page styles at the commit in `config.json`. Horoi's upstream renderer lists OWL classes and properties using `rdfs:comment`. This adaptation supports the released SKOS terms, `skos:definition`, multiple namespaces and supporting nodes. `NOTICE.txt`, `vendor/LICENSE` and `vendor/upstream.json` record the source, licence and unchanged vendored bytes. It uses no Brick or RDF Garden code.

## Build

Use Python with the pinned RDFLib dependency:

```sh
uv run --with rdflib==7.6.0 python horoi_viewer/build.py \
  --source <clean-release-clone> --out <new-output>/horoi_viewer
```

The source must be the commit named by `config.json`. The builder checks the checkout's bytes and executable modes, refuses untracked documentation inputs, and uses the existing viewer reader to verify package hashes and keep blank nodes separate across files. It reads only current release packages and their catalog. It does not change packages, use live stores, or infer relationships. Supporting nodes and references from other modules provide context; Party and Core supply the pilot's main term navigation.

The output directory must be new or empty. The builder never deletes an existing output. It emits `index.html`, `build.json`, `LICENSE.txt` and `NOTICE.txt`. Keep that folder alongside the existing `viewer/` and `business_architecture/` directories so its relative links work.

## Add documentation to the release

This documentation-only route implements EPM-DEC-001-0114. It does not invoke the full cut, package builders, cleanup or store loaders.

```sh
uv run --with rdflib==7.6.0 python -m horoi_viewer.release stage \
  --source <clean-release-clone> --docs <new-output>/horoi_viewer \
  --out <new-staging-folder> --report <outside-staging>/comparison.json
```

Staging copies every tracked baseline file with its executable mode and adds only the four documentation files. Verification compares every baseline path, hash and executable mode. It also compares the embedded documentation data with the verified source packages. An extra file, missing file, changed byte, changed executable mode or changed semantic payload fails the comparison.

Use the repository's ZIP tool on the verified staging folder. Extract that exact ZIP, repeat the comparison and browser check, and publish the additions through a pull request in the private release repository. The original repository's reviewed implementation must land first. A documentation release tag does not change ontology module versions. No existing release file is edited, including the original viewer, README, manifests and projections.

## Verify

```sh
uv run --with pytest --with rdflib==7.6.0 python -m pytest -q horoi_viewer/test_reference.py
NODE_PATH=<node_modules> node horoi_viewer/test_browser.mjs \
  <staged-release>/horoi_viewer/index.html <evidence-folder>
```

The browser check uses `playwright-core` and installed Chrome. `CHROME_PATH` can select another Chrome executable. It opens the page through `file:`, blocks and counts HTTP requests, exercises desktop, tablet and phone navigation, follows links into the existing viewer, and saves screenshots and results. The evidence folder must already exist. Review the screenshots for readable layers, definitions and relationships; a passing script alone does not establish usability.

`scripts/check.sh` includes the Python tests. Browser validation also runs on the exact release artifact before publication. Build output and evidence stay outside the source checkout. The new release keeps all existing files unchanged, so it does not alter the existing release's tests or validation instructions.
