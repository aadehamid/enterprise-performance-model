# EPM-DEC-001-0060: The full APQC PCF 7.2.2 element list in the graph; questions 40 and 43 answered by their graph part

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Competency questions 11 (which APQC elements have no local counterpart), 40 and 43, each partial; Phase E of EPM-DEC-001-0052 |
| Source | Claude Code session, 2026-10-19 |

## Context

Question 11 was partial: `core` 2.1.0 carries only the 251 APQC elements its processes reference, so the elements with no counterpart could not be listed. The repository vendors APQC's Downstream Petroleum PCF 7.2.2 workbook, whose "Combined" sheet lists 2,012 elements. Questions 40 and 43 were also partial. EPM-DEC-001-0019 says that for them only the part the graph supplies is tested: question 40's people catalog and question 43's Genie binding sit outside the graph.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **An `apqc` reference graph** holds all 2,012 elements, described as `core` describes the referenced ones (identifier, part of the PCF, title), plus each element's name and hierarchy ID. APQC stays a reference: nothing in it is a process of the map.
2. **Question 11 is answerable.** 1,761 elements have no local counterpart. The scope decisions explain whole areas of them; the query lists them, and a gap is a separate judgement.
3. **Questions 40 and 43 are answerable by their graph part,** as EPM-DEC-001-0019 says to test them: every live concept has one official definition in the release (40), and none has a second copy for an assistant to drift from (43). The people catalog and the Genie binding are consumers of that definition, outside the graph; the release package (Step 10) is where the official wording is published.

## Alternatives considered

- **Park question 11.** Not chosen: the workbook is in the repository and its licence allows the use with attribution.
- **Add the elements to `core`.** Not chosen: they are a reference, and a `core` release would carry 1,761 resources no process uses.

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/reference/APQC-PCF-Downstream-Petroleum-v7.2.2.xlsx`, sheets "Combined" and "Copyright and Attribution"; `business_architecture/ontology/apqc-scope-decisions.md`; EPM-DEC-001-0019, 0059.

## Consequences

- The regression stands at 30 answerable, 1 partial (Q7) and 13 waiting.
- In `core` 2.1.0, 16 concepts reference element 19948 ("Analyze internal operations"), among them CM 1.2.4.1.10 and CM 1.2.4.1.18, whose notes say "APQC: no meaningful candidate". The released package stays fixed; the next `core` release should check those references.
