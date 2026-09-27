# Verb → Predicate Mapping — CANDIDATE FOR REVIEW (not approved)

**Status:** draft for controlled review. No emission script may use this
mapping until Hamid approves it row by row.

**Locked input (Step 4 Q4, review-corrected):** a process-to-process
input dependency is `core:dependsOnOutputOf` (consumer → producer),
inverse `core:providesInputTo`. Never `core:usesInput` — a process is
not an input; its *output* is. The raw workbook verb is retained in
migration/provenance evidence on every emitted triple.

**Design rules applied:**
- No transitivity asserted on any sequencing property.
- Every property gets an explicit inverse.
- `core:consumes` / `core:produces` stay reserved for future identified
  InformationObject instances — not used here.

## Proposed mapping (1,302 emitting rows)

| Raw verb | Rows | Proposed predicate | Inverse | Kind | Notes / open question |
|---|---|---|---|---|---|
| uses-input | 219 | `core:dependsOnOutputOf` | `core:providesInputTo` | planned dependency | Q4-corrected. |
| informed-by | 150 | `core:dependsOnOutputOf` | `core:providesInputTo` | planned dependency | Informational dependency; same property as uses-input, raw verb preserved in evidence. **Q: merge or split?** |
| enables | 397 | `core:enables` | `core:enabledBy` | planned dependency | Capability enablement, not sequence. Largest class — spot-check semantics. |
| requires | 6 | `core:requires` | `core:requiredBy` | planned dependency | Prerequisite. **Q: merge into `dependsOnOutputOf`, or is "requires" stronger?** |
| precedes | 170 | `core:precedes` | `core:follows` | sequence | No transitivity. |
| follows | 176 | `core:follows` | `core:precedes` | sequence | Same pair as precedes, direction flipped at emission. |
| governed-by | 147 | `core:governedBy` | `core:governs` | governance | Process targets only; the 1 external-governance row is held until the external-reference property is designed. |
| constrained-by | 10 | `core:constrainedBy` | `core:constrains` | constraint | |
| constrains | 1 | `core:constrains` | `core:constrainedBy` | constraint | Single row; verify direction at emission. |
| triggers | 18 | `core:triggers` | `core:triggeredBy` | trigger | Event-driven initiation. |
| assures | 8 | `core:assures` | `core:assuredBy` | assurance | Smallest class; verify the 8 rows mean the same thing. |

**Total: 1,302 rows mapped. 12 deferred + 3 non-process rows emit no
process-dependency triple.**

## Open questions for review

1. Should `informed-by` merge into `dependsOnOutputOf`, or does the
   informational flavor deserve its own property?
2. Is `requires` distinct from `dependsOnOutputOf`, or a stronger
   shade of the same dependency?
3. `enables` (397 rows) — is it uniformly capability-enablement, or
   does it hide sequencing in some branches?
4. `assures` (8 rows) — single coherent meaning?
5. Should any of these be subproperties of a common
   `core:processDependency` for querying?
