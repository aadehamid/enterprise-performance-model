# EPM-DEC-001-0063: The R2 backlog: each item out of scope for now, with the trigger that brings it back

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Worklog row 3d-d, the R2 backlog "open by design" since 2026-09-22; Phase E of EPM-DEC-001-0052, the 3d-d backlog |
| Source | Claude Code session, 2026-10-19 |

## Context

The R2 backlog (worklog row 3d-d and its 2026-09-22 entry) holds four items: (1) an operating-execution layer (unit-operation scheduling, line-ups, blend execution, process control, operating procedures); (2) maintenance and turnaround ownership; (3) an R2 Refinery Vocabulary and Operating-Lifecycle package (turnaround against normal and emergency shutdown, startup, plan against schedule); (4) a review of where Energy & Utility Management sits, triggered by an R2 refinery energy, utilities and environmental performance scope decision. Since then MPC-P02b (EPM-DEC-001-0047, PR #292) gave Refining its ID and filled RF 1.2 Refinery Asset Reliability and Turnaround Coordination with five steps that coordinate the commercial and planning side of turnarounds. RF 1.2's own description and steps RF 1.2.1 and RF 1.2.3 keep the maintenance work itself outside the process. The process map is the commercial, planning and logistics map of the downstream business; the repository's competency questions ask nothing about unit operations.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **Operating-execution layer: out, for now.** No competency question needs it and the map has no such processes. *Trigger:* the process map gains an operating-execution L2 by an accepted proposal, or the decision owner asks for it.
2. **Maintenance and turnaround ownership: answered for the map's scope.** RF 1.2 owns the commercial and planning side of turnarounds (scope, schedule against the plan, commercial impacts, restart assumptions, cost review), as P02b set out. Who owns maintenance strategy, inspection and turnaround execution is outside the map and stays with the refinery maintenance function. *Trigger:* the operating-execution layer comes in (item 1). The next `core` release should review RF 1.2's Candidate status, since its open ownership question is answered for the map's scope.
3. **R2 Refinery Vocabulary and Operating-Lifecycle package: out, for now.** Its distinctions belong to the operating-execution layer; the turnaround steps already separate the planned turnaround they coordinate from the maintenance work. *Trigger:* item 1's trigger.
4. **Energy & Utility Management stays where it is** (CM 1.1.7.3, under CM 1.1.7 Refinery Production Planning and Scheduling). Its review trigger, a scope decision on refinery energy, utilities and environmental performance, has not occurred. *Trigger:* unchanged.
5. **PTC-001-B stays a hold by design** (the decision owner, 2026-09-22), as worklog row 3d-b records.

## Alternatives considered

- **Model the operating-execution layer now.** Not chosen: no source in the repository describes those processes, and no question asks about them.
- **Leave the backlog open.** Not chosen: the ontology is complete only when each open item is decided in or out (EPM-DEC-001-0052, Phase E).

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/ontology/step4/playbook/ontology-worklog.md`, row 3d-d and the R2 backlog entry of 2026-09-22; `business_architecture/business_process/downstream_process_map.json`, RF 1.2 and its five steps; EPM-DEC-001-0047 (P02b).

## Consequences

- Worklog row 3d-d is decided: every item is out with a trigger, or answered for the map's scope.
