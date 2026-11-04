# Ontology viewer

The viewer shows one released ontology from the private release repository. Recipients unzip the shared release and open `viewer/index.html`. The page embeds its data, JavaScript and fonts, so it works offline with no installation or server.

The viewer opens on Module overview. The top navigation separates Modules, Value streams and Customer views. Module overview lists every released module with its recorded description, version and term count. Selecting a module opens its vocabulary groups, declared dependencies and links into the complete term browser. An optional dependency diagram links to the same module overviews. The Order to Cash and Commercial Hydrocarbon Lifecycle buttons open their definitions, trigger, outcome and ordered stages directly. Each stage exposes its process links. Module and stream overviews support drilldown, return navigation, browser history and reload.

Search ontology is available from every view. Search modules by name or description, business views by name, and terms by label, definition or IRI. Search results group these destinations separately. Term-type filters narrow both global search and the term browser. Breadcrumbs return to earlier views while preserving searches, filters and expanded sections during the session. Browser Back and Forward also restore the navigation trail. Reload preserves the destination; browsing state is kept only while the page stays open. Module navigation includes a hierarchy and an alphabetical fallback for terms without parents or with cycles. Selecting a term opens its definitions, scope notes, sources, module versions and relationships. Evidence, anonymous restrictions and constraints remain available through property links and the supporting-node search option. On a phone, choosing a term opens its detail pane; Back to terms returns to navigation.

Choosing the value-stream module lists the released value streams first. Each opens its stages in their recorded sequence, then their processes and realized core processes. Links to the containing stage or stream provide a way back. The module's vocabulary remains searchable and accessible in the hierarchy.

The top navigation opens Customer lifecycle and Customer conceptual model directly. The lifecycle lists the released business stages alphabetically, with definitions, process links and corresponding system stages. Systems appear under the system stage that records them; no business-stage sequence or direct system mapping is inferred. The conceptual diagram arranges the 17 customer entities in three presentation groups. Its edges come from declared property domains and ranges, subclass links and disjoint links between those entities. Selecting an entity highlights its edges and filters an equivalent relationship table. Properties, classes and lifecycle links open the existing term details, with a return button to the overview. Both overviews support browser history and reload. The conceptual model and module dependency diagrams provide Zoom in, Zoom out, Fit diagram and Full screen controls. Escape exits full screen. Both diagrams scroll within their frames on phones; the conceptual relationship table remains available as text.

The diagram is a view of the conceptual entities, not a replacement for the full ontology browser. Attributes, code lists and system extensions remain in All ontology. Its arrows do not imply required fields, cardinalities or instance relationships. The separate customer logical model remains in the logical-model module.

## Data boundary

The input is `share/epm-1.0` at `81f2f63b128820854a25204641b6899d55051ae3`. The builder checks the Git commit, refuses local changes under `releases/`, and verifies each manifest-listed Turtle file against its SHA-256. It reads the current package of each module and the top-level release catalog from that pinned tree. It includes the customer schema and technical-graph vocabulary. It does not read main, candidate packages, earlier releases, examples, live stores or technical-graph records.

A term is a named class, property, concept, concept scheme or designed individual. The displayed total excludes supporting nodes, whose counts appear separately in Release details. Supporting nodes are evidence, bibliographic sources, constraints, package metadata and anonymous RDF nodes. All source triples remain inspectable. Literal language and datatype values are preserved; English labels display without an `@en` suffix.

The shared figures command uses the same parser:

```sh
uv run --with rdflib python scripts/epm_facts.py viewer --tree <release-clone>
```

## Build and cut

```sh
uv run --with rdflib python business_architecture/ontology/viewer/build.py \
  --source <release-clone> --out <outside-checkout>/viewer/index.html
```

The implementation lives here. Build output belongs in the cut's output folder. For the shared release, use `scripts/share_release/cut.sh --viewer-source <release-clone>` along with its other required arguments. The cut requires its current Turtle packages and release catalog to equal the pinned inputs after the exact source-title substitution in `scripts/epm_source_descriptions.py`. That substitution implements the image-source removal requested in EPM-DEC-001-0110, amendment of 2026-11-04, while retaining neutral customer-input provenance; every other byte difference stops the cut. The viewer then reads the verified cut's packages. The cut reconstructs the emitted page's RDF, checks it against those packages and verifies the tested page is byte-identical to the page it ships. Do not copy a preview into the release or push the release branch directly.

This guide describes the build workflow. The cut supplies separate viewing instructions beside the page. The embedded page remains a snapshot of the release as received; changing packages does not refresh it.

The tests use synthetic RDF and cover package hashes, exclusions, customer schema inclusion, blank-node separation, restrictions, script-safe embedding and cut/source mismatches. Browser checks must also exercise the generated page through `file://`, with network requests blocked, and inspect desktop, tablet and phone layouts.

Run the parser tests with the optional private release check:

```sh
EPM_VIEWER_RELEASE_SOURCE=<release-clone> uv run --with pytest --with rdflib \
  python -m pytest -q business_architecture/ontology/viewer/test_viewer.py
```

The browser test uses `playwright-core` and an installed Chrome browser. Set `NODE_PATH` to the directory containing that package. Set `CHROME_PATH` if Chrome is not at its standard macOS location.

```sh
NODE_PATH=<node_modules> node business_architecture/ontology/viewer/test_browser.mjs \
  <outside-checkout>/viewer/index.html
```

The browser test checks search, module and hierarchy navigation, preserved hierarchy state, graph rendering, term links, copying an IRI, supporting-node coverage and phone navigation. It fails on script errors or HTTP requests.

## Design and dependencies

The app uses plain HTML, CSS, JavaScript and SVG. No graph library is needed. The cut pins RDFLib to 7.6.0 for parsing Turtle; no RDF parser runs in the browser. IBM Plex Sans is embedded under the [SIL Open Font License 1.1](fonts/OFL.txt), also available inside the generated page. Font source: [Google Fonts, IBM Plex Sans](https://github.com/google/fonts/tree/main/ofl/ibmplexsans), retrieved 2026-11-03.

The OEO viewer supplied behavior references for search, hierarchy and term details. Its [terms of use](https://openenergyplatform.org/legal/tou/), read 2026-11-03, identify source code as AGPLv3 unless otherwise noted. This implementation copies no OEO code, data or assets.
