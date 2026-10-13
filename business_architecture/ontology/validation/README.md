# Step 9 validation shapes

Shapes that run against the released modules without changing them. They join each module's release shapes at its next release.

- `controlled-values.ttl`: every code-list property takes its values from its own list (EPM-DEC-001-0035). `core` 1.0.0 and the organization module conform.
- `test_controlled_values.py`: the release conforms, a value from the wrong list fails, and every code-list property of `core` has a shape. `scripts/check.sh` runs it.

The evidence-link shape (every fact links to its source evidence) waits for the next `core` release, which must first carry evidence in the graph. EPM-DEC-001-0035 records the proposal.
