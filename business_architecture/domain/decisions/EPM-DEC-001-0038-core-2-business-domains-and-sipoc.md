# EPM-DEC-001-0038: core 2.0.0: business domains as a code list, SIPOC planned inputs and outputs

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-13: SIPOC, the domain split, the 2.0.0 release and the SIPOC backlog; the build choices delegated under EPM-DEC-001-0028); *2026-10-19:* the decision owner accepted #266 and #269 as merged, after the fact (EPM-DEC-001-0050) |
| Date | 2026-10-13 |
| Questions | What the process map's `sioc` field means; whether the `core:responsibleDomain` values are org units or business domains, and how "Commercial & Marketing" splits; how those answers and the two missing ranges reach `core` |
| Source | Claude Code session, 2026-10-13 |

## Context

- **`sioc`.** The process map holds a `sioc` field on 153 processes with four lists: suppliers, inputs, outputs and customers. The playbook says to confirm an ambiguous field's meaning before naming terms after it (EPM-DEC-001-0034 put the question to the decision owner).
- **`responsibleDomain`.** `core` 1.0.0 carries `core:responsibleDomain` as an interim literal with five values: Commercial & Marketing (456), Finance-enabled Supply & Trading (13), Cross-functional (12), Finance (2) and Refining (2). Step 4's Q7 left it for Step 5 to map "where the operating model evidences the relationship (some labels are business domains, not org units)".
- **Ranges.** `core` 1.0.0 gives `core:earlierProcess` and `core:laterProcess` no `rdfs:range` (EPM-DEC-001-0036 lists them as release gaps).

## Decision

**The decision owner's decisions:**
1. `sioc` is SIPOC: suppliers, inputs, process, outputs and customers. The process is the node itself.
2. The domain values are business domains, not org units. "Commercial & Marketing" is two domains. CM 1.3 is Marketing; CM 1.1 and CM 1.2 are Commercial; CM 1.4 (IT Services) is its own domain.

**How they reach `core` (Claude, under the delegation):**
3. **A business domain code list.** `core:BusinessDomain` holds seven concepts: Commercial, Marketing, IT Services, Finance-enabled Supply & Trading, Finance, Refining and Cross-functional. A new object property, `core:businessDomain`, links each concept that carries a 1.0.0 `core:responsibleDomain` value to one of them: 485 concepts, of which 463 are of kind process and 22 of kind capability. Today that is 205 Commercial, 251 Marketing, 13 Finance-enabled Supply & Trading, 12 Cross-functional, 2 Finance and 2 Refining; no CM 1.4 process has a domain label yet. A Cross-functional process keeps the note that names its domains.
4. **`core:responsibleDomain` is deprecated, not removed.** It is marked `owl:deprecated true`, and its values stay, so consumers that read it keep working while they move to `core:businessDomain`.
5. **Planned inputs and outputs.** `core:plannedInput` and `core:plannedOutput` carry the SIPOC inputs and outputs as governed literals, one per item (the 2026-09-22 flow decision: no flow nodes). That is 362 inputs and 219 outputs on 153 processes. Suppliers and customers stay parked: they name roles and systems, which need their own mapping.
6. **The two ranges.** `core:earlierProcess` and `core:laterProcess` get `rdfs:range skos:Concept`.
7. **A major release, built as a candidate.** A deprecation makes this 2.0.0 (module policy: majors are the decision owner's). `release/build_core_next.py` builds it from the released 1.0.0 graph, so 1.0.0 stays as built from its pinned evidence. It wrote `releases/core/2.0.0-rc.1/` with no issued date until the decision owner approved the release.
8. **The release.** The decision owner approved core 2.0.0 on 2026-10-13. The builder now writes `releases/core/2.0.0/`: the candidate's content with `dcterms:issued` and `dcterms:modified` set to 2026-10-13 and the stage removed. The candidate package is removed, as 1.0.0-rc.1 was at the 1.0.0 cut. The manifest and the tests name the sentence that approved it. The merge commit gets the tag `core-v2.0.0`.

**The decision owner's decision on the rest (2026-10-13):**
9. The live processes with no SIPOC in the process map (504 on core 2.0.0, listed by the Q8 query `regression/queries/q08a-no-planned-flows.rq`) are the source author's backlog. The ontology does not draft inputs and outputs for them. When the process map gains a SIPOC field, the next core build carries it.

Left out: the evidence nodes on canonical facts (EPM-DEC-001-0035), which wait for the decision owner's walkthrough.

### For the decision owner

1. ~~Approve core 2.0.0.~~ Approved 2026-10-13 (item 8). The projection (EPM-DEC-001-0036) and the regression then moved to 2.0.0 in their own change. That closed the two listed release gaps, and question 8 is answerable from the planned inputs and outputs.
2. **Consider moving CM 1.4 IT Services under the enabling functions** (`L1-process-excellence-it`). That changes the process map, so it is a proposal for the source author.

## Alternatives considered

- **Change the `core:responsibleDomain` values in place.** Rejected: consumers filtering on "Commercial & Marketing" would break silently, and a literal is not a governed list.
- **Mint org units for the domains.** Rejected: The decision owner decided they are business domains.
- **Mint nodes for inputs and outputs.** Rejected by the 2026-09-22 flow decision until a use case needs one flow traced.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-13-session2.md`. On `sioc`: "it is SIPOC: SIPOC stands for Suppliers, Inputs, Process, Outputs, and Customers. It describes a process’s boundaries and the things that flow into and out of it." On the domains: "They two separate business domains: Commercial and Marketing". On the split: "Option 2: 1.3 Marketing; 1.1, 1.2 Commercial; 1.4 its own". On the processes without SIPOC, saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/sipoc-scope.md`: "option 1, treat it as source author's backlog." On the release, saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/core-2-0-0-release.md`: "No one uses the ontology yet. I approve the core 2.0.0 releas". The build choices (items 3 to 7) are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and the decision owner can reverse them.

## Evidence

`downstream_process_map.json` (`sioc` on 153 processes; the CM 1 tree); `releases/core/1.0.0/`; Step 4 Q7 (`step4/step4-decisions.md`); EPM-DEC-001-0034, 0035, 0036; the worklog's flow decision of 2026-09-22.

## Consequences

- `scripts/check.sh` runs `build_core_next.py --verify` and `test_build_core_next.py`.
- Core 1.0.0, its builder and its tests are unchanged.
- The decision owner stated on 2026-10-13 that no one uses the ontology yet, so on that date deprecating `core:responsibleDomain` broke no consumer.
- This supersedes the plan, in EPM-DEC-001-0029 and EPM-DEC-001-0030, to link `core:responsibleDomain` to org units; both records carry a dated note.
