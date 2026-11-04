# View the ontology

Open `viewer/index.html` in a browser after unzipping the release. The page contains its ontology data, scripts and fonts. It works offline and needs no installation or server.

The viewer opens on Module overview. The top navigation separates Modules, Value streams and Customer views. Use Module overview to find a module by name or description, read its purpose and see its vocabulary and dependencies. The optional module dependency diagram opens the same overviews. Use Browse all terms to enter that module's complete search and hierarchy. The Order to Cash and Commercial Hydrocarbon Lifecycle buttons open each stream's ordered stages directly; expand a stage's processes or open its details to drill down. Breadcrumbs and return buttons take you back while keeping your searches, filters and expanded sections. This browsing state lasts until you close or reload the page.

Use Search ontology from any view. Find modules by name or description, business views by name, and terms by label, definition or IRI. Use Term type to narrow the terms to classes, properties, concepts or another released type. All ontology also provides these filters and the module hierarchy. Select a term to read its definition, source and relationships. Select a connected term to follow a relationship. Expand All properties and evidence to inspect the recorded predicates and values. Include evidence and constraints to find supporting nodes directly.

Choose the value-stream module to list the value streams. Open a stream to see its stages in sequence, then open a stage to see its processes. Each process links to the core processes it realizes. Use Part of to return to the containing stage or stream.

Use Customer lifecycle in the top navigation to see the business stages. Open Processes and systems under a stage to follow its process links and corresponding system stages. The stages are listed alphabetically; the release does not define a mandatory sequence.

Use Customer conceptual model to see the customer entities together. Select an entity to highlight its connections, read its definition and filter the relationship list. Open an entity or property to inspect its full details; the return button takes you back to the model. Use Zoom in, Zoom out, Fit diagram or Full screen to explore the diagram. Escape exits full screen. The module dependency diagram has the same controls. Each diagram scrolls within its frame on a narrow screen. The conceptual model connections are also listed as text. Arrows show declared domains and ranges, subclass links and disjoint links. They do not imply required fields or cardinalities. Attributes, code lists and system extensions remain in All ontology; the separate customer logical model is in the logical-model module.

Release details identifies the source release, the Turtle inputs and their checksums. Counts distinguish ontology terms from evidence, constraints and package metadata. Technical-graph vocabulary is included; runtime records and example datasets are not viewer inputs.

This page shows the ontology as received. Editing files beside it does not refresh its embedded data. A newly cut viewer is needed to view a later release. Read `HOW-TO-UPDATE.md` at the release root for changes to the ontology itself.
