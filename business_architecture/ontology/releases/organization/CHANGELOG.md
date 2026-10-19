# organization changelog

## 2.0.0 (2026-10-18)

Major. Approved by Hamid on 2026-10-18 ("Yes, approve 2.0.0 (Recommended)", saved in `step4/review-evidence/hamid-answers/answers-2026-10-18-night.md`). It carries his answers to the role questions (EPM-DEC-001-0045).

- Deprecated, never deleted: `role:rcvo-advisor` (replaced by `role:rvco-advisor`; "RCVO Advisor" becomes a hidden label, a misspelling), `role:refinery-technical-service-representative` (replaced by `role:refinery-technical-representative`) and `role:vp-clean-products-crude-trading-ngls-asphalt-petchem` (replaced by `role:vp-clean-products-rvco-crude-trading-ngls-asphalt-petchem`). Each keeps its triples and gains `owl:deprecated true` and `dcterms:isReplacedBy`. 60 roles, 57 live.
- Breaking: the three assignments that named a deprecated role now name its successor. They keep their IRIs and source text. 940 assignments, as before.
- Expanded names: ten roles take an expanded preferred label, with the source spelling kept as an alternative label: nine from the acronym answers (Refinery Value Chain Optimization Advisor, VP Refinery Value Chain Optimization, Continual Commercial Improvement Director, Clean Products Manager, Clean Products Value Chain Scheduler, Global Feedstocks Value Chain Manager, Economics and Planning Manager and Supervisor, Business Planning and Analysis), and Crude RFC, which becomes Crude Refinery Feedstock Coordinator and stays its own role.
- Added: definitions on four roles, and an editorial note with the evidence and its status on each answered role. Forecaster and PSM stay unresolved, each with its open question.
- Depends on `core` 2.0.0 by IRI (1.0.0 depended on `core` 1.0.0). `ref-mpc` 1.1.0 requires this release.

## 1.0.0 (2026-10-13)

Approved by Hamid on 2026-10-13 ("aprove now", saved in `step4/review-evidence/hamid-answers/answers-2026-10-13-session2.md`). The release is 1.0.0-rc.1 with the issued and modified dates set (2026-10-13) and the stage removed; nothing else changed. EPM-DEC-001-0037.

## 1.0.0-rc.1 (release candidate, not issued)

The first release candidate of the `organization` module. A module's first release is a major, so 1.0.0 is issued only when Hamid approves it (module policy, 2026-09-18; EPM-DEC-001-0037).

- The vocabulary and shapes: `orgm:ResponsibilityAssignment`, the RACI level list and `orgm:ControlRelationship` (EPM-DEC-001-0030).
- 60 roles from the role register (EPM-DEC-001-0031).
- 940 RACI assignments on 153 processes, one per source entry and role (EPM-DEC-001-0032).
- Depends on `core` 1.0.0 by IRI; imports nothing.
