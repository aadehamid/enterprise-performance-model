# Proposed process-contract schema extensions

**Status:** Proposed (Candidate). Not process authority. No schema or instance file has been changed.
**Origin:** [EPM-PPC-UPDATE-PLAN](../../ARCHIVE/EPM-PPC-UPDATE-PLAN_Existing_Artifacts.md), section "business_architecture/business_process and schema"; [EPM-ARCH-PPC-003](../../architecture/EPM-ARCH-PPC-003_Process_Conformance_and_Executable_Semantics_Extension.md).
**Last updated:** 2026-10-02

## Purpose

Evaluate which fields would let the process-authority files act as a designed-process contract that executable consumers can validate instances against. Add only fields that are reusable EPM semantics. Do not add PPC-specific simulation details.

The process-authority files remain `business_architecture/business_process/` and `business_architecture/schema/`. This note does not change that.

## Current coverage in `value_stream.schema.json`

Observed on 2026-10-02 from `business_architecture/schema/value_stream.schema.json`.

- Value stream: `id`, `name`, `domain`, `description`, `trigger`, `outcome`.
- Capabilities: `id`, `name`, `alignsToProcessGroups`.
- Stages: `id`, `name`, `sequence`, `processes`.
- Flows between nodes: `from`, `to`, `kind`, `note`.
- Process entries: `id`, `capabilityId`, `linkedProcessIds`, `produces`, `consumes`.
- `gapAnalysis` items.

`data_product_portfolio.schema.json` is out of scope for this note.

## Candidate extensions

| Need (from EPM-ARCH-PPC-003 section 3) | Already present | Gap to evaluate |
|---|---|---|
| Stable process, stage, activity IDs | Process and stage IDs | Stable activity and event IDs, if activities are not yet modeled as addressable nodes |
| Sequence, precedence, allowed transitions | Stage `sequence`; `flows` (`from`, `to`, `kind`) | Whether `flows` can carry process-level and activity-level transitions, and which `kind` values are governed |
| Trigger and end conditions | Value-stream `trigger` and `outcome` | Process-level trigger and end conditions |
| Roles | `office_lanes.json` overlay (front, middle, back, operations; not process IDs) | Whether process-level role assignment is wanted |
| Inputs and outputs | `produces`, `consumes` | None identified |
| Decisions | None | Decision nodes (see FOUND-001 decisions) |
| Events | None | Business events that processes emit or react to |
| Capability and value-stream relationships | `capabilityId`; stage-to-capability use | None identified |
| Measurement opportunities | None | Measurement hooks: which activity or event generates which measurement (FOUND-005) |
| Valid alternate and exception paths | `flows.kind` may partly cover | A governed way to mark an exception or alternate path as valid |

## Rules for accepting an extension

1. It is reusable across consumers, not specific to one simulator.
2. It is optional in the schema, so existing instance files stay valid.
3. It has an owner and an example in the instance files.
4. It does not make a consumer's process instances part of EPM business architecture.
5. It is recorded as a decision (EPM-DEC-001, once it exists) before the schema changes.

## Open questions

- Which activity-level files exist today. `downstream_process_map.json` and `office_lanes.json` were not inspected for this note.
- Whether decisions and events belong in the value-stream schema or in a separate process schema.
