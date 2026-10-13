# Definitions and runs (Step 6)

The ontology holds process definitions; the systems that use it hold the runs (EPM-DEC-001-0016). This folder holds the pattern that links the two. The design is EPM-DEC-001-0034.

- `run-shapes.ttl`: the SHACL a consumer's run must meet. A run is a `prov:Activity` with exactly one qualified association whose `prov:hadPlan` is a live core process concept, and a start time. A further shape fails any core concept typed as a `prov:Activity`.
- `example-run.ttl`: one made-up run of a real process, for illustration. It is not data.
- `test_run_shapes.py`: the core release holds no runs, the example conforms, and broken runs fail. `scripts/check.sh` runs it.

To check your runs, validate them with `run-shapes.ttl` against the core release they follow.
