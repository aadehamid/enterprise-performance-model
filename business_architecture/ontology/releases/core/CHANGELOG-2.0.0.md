# core changelog

## 2.0.0 (2026-10-13)

A major release, because it deprecates a property. Built from the released 1.0.0 graph; 1.0.0 is unchanged. Hamid approved it on 2026-10-13 (module policy, 2026-09-18; EPM-DEC-001-0038; his words in `step4/review-evidence/hamid-answers/core-2-0-0-release.md`). It was built first as the candidate 2.0.0-rc.1, which this release replaces with the same content plus its issued and modified dates.

- **Business domains as a code list.** New `core:businessDomain` links each concept that carries a 1.0.0 `core:responsibleDomain` value (485: 463 processes and 22 capabilities) to the new `core:BusinessDomain` list: Commercial, Marketing, IT Services, Finance-enabled Supply & Trading, Finance, Refining, Cross-functional. "Commercial & Marketing" splits by branch, as Hamid decided on 2026-10-13: CM 1.3 Marketing; CM 1.1 and CM 1.2 Commercial; CM 1.4 IT Services.
- **Deprecated:** `core:responsibleDomain` (`owl:deprecated true`). Its values stay so current consumers keep working; use `core:businessDomain`.
- **Planned inputs and outputs.** New `core:plannedInput` and `core:plannedOutput` carry the inputs and outputs of the process map's SIPOC field (`sioc`), which Hamid confirmed is SIPOC.
- **Ranges.** `core:earlierProcess` and `core:laterProcess` now have `rdfs:range skos:Concept` (projection guideline Rule 1).
- Shapes: a stated cardinality for each new property, and the business domain values checked against their list.
