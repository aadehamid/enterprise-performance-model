# Step 9 validation shapes

Shapes that run against the released modules without changing them. They join each module's release shapes at its next release.

- `controlled-values.ttl`: every code-list property takes its values from its own list (EPM-DEC-001-0035). Since 2026-10-18 they are part of the `core` 2.1.0 release shapes (EPM-DEC-001-0044); this file stays their source. `core` 2.1.0 and the organization module's RACI assignments conform.
- `test_all_module_shapes.py`: the Step 9 gate (EPM-DEC-001-0065). Every shape file of `core` 2.2.0 (since 2026-10-22; 2.1.0 before) and the modules, run together on the graph the regression loads, finds zero violations; a cross-module break must fail. `scripts/check.sh` runs it.
- `test_controlled_values.py`: the release (`core` 2.2.0 since 2026-10-22, which carries 2.1.0's shapes unchanged) conforms, a value from the wrong list fails, and every code-list property of `core` has a shape here or in the release shapes (`core:businessDomain` is checked by the release's own shape). `scripts/check.sh` runs it.

The evidence-link shapes (every canonical fact links to its source evidence, and every fact node to its triple) are in the `core` 2.1.0 release shapes, with the build check that each node's rows match the mapping (EPM-DEC-001-0044).
