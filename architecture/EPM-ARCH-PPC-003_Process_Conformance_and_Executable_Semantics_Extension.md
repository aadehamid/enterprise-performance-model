# EPM-ARCH-PPC-003 — Process Conformance and Executable Semantics Extension

**Status:** Proposed  
**Purpose:** Extend EPM's machine-readable process authority into an explicit designed-process contract for executable consumers.

## 1. Existing strength
EPM already separates business-architecture pattern documents from process-authority instance files under `business_architecture/business_process/` and schemas.

This is valuable for PPC because process definitions can become executable validation inputs.

## 2. Designed versus executed
```text
EPM designed process
      ↓
consumer process instance/event log
      ↓
conformance analysis
      ↓
performance relationship
```

EPM owns the designed process. PPC or another consumer owns the executed instance.

## 3. Minimum process contract
Where practical, process-authority schemas should expose:
- stable process/stage/activity IDs;
- sequence/precedence or allowed transitions;
- trigger/end conditions;
- roles;
- inputs/outputs;
- decisions;
- events;
- capability relationships;
- value-stream/stage relationships;
- measurement opportunities;
- valid alternate/exception paths where governed.

## 4. Performance relationship
Process conformance can connect designed business architecture to cycle time, rework, handoff delay, OTIF, DSO, demurrage, margin and other outcomes.

EPM should model these relationships semantically without asserting causality merely from process correlation.

## 5. Competency tests
Examples:
- Which capability does this process realize?
- Which value-stream stage uses that capability?
- Which activities generate measurements?
- Which decisions occur in this process?
- Which KPIs measure this process/outcome?
- Which data products supply those metrics?

## 6. Consumer feedback
PPC can reveal missing transitions, ambiguous stage boundaries or undocumented exceptions. Reusable changes return through EPM governance.
