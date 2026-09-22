# R1 Hierarchy-Consumer Inventory — Team Checklist

**Status (2026-09-22):** NOT REQUIRED at foundation stage — Hamid confirmed no consumers exist yet.
Retained as the standing instrument for the first consumer connection; Gate 2 then reactivates.

**Purpose (when consumers exist):** Gate 2 of the R1 Refining structural reclassification requires proof, not assumption,
that no hierarchy-dependent consumer silently breaks when 40 concepts move from
Commercial & Marketing → Planning & Scheduling to the Refining L1 (plus the 2-row tombstone
re-anchor). This checklist is the fill-in instrument. The repository cannot enumerate these
assets — the owning team must.

**Scope of the change (what to search for):** any asset referencing these old paths or the
concepts beneath them:

```text
Downstream Operations > Commercial & Marketing > Planning & Scheduling > Refinery Planning
Downstream Operations > Commercial & Marketing > Planning & Scheduling > Refinery Scheduling
```

…including every descendant path (42 rows in `r1-path-compatibility-register.md`), plus
`parent_slug`, `level`, breadcrumb, or scheme-membership references to the moved concepts.
Search both the display labels and the slugs (`CM-1-1-4*`, `CM-1-1-7*`); labels are presentation
metadata, but legacy assets may have hardcoded them.

**How to search:** string/path match on "Refinery Planning", "Refinery Scheduling",
"Commercial & Marketing > Planning", `CM-1-1-4`, `CM-1-1-7` in each asset class below.
Record hits even when the reference looks incidental — path-prefix filters are the highest risk.

## A. Power BI / semantic models

| Asset (report / dataset / model) | Owner | Old path reference found (quote it) | Dependency type (hierarchy def / field parameter / display text / filter) | Disposition | Notes |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## B. RLS / OLS and security mappings

| Rule / role / mapping | Owner | Path or grouping referenced | Disposition | Notes |
|---|---|---|---|---|
|  |  |  |  |  |

Pay special attention to any string/path comparison against the old Commercial & Marketing branch
(e.g. `PATHCONTAINS`, `startswith("Commercial")`, L1/L2 group membership tests). A valid ontology
change that silently moves a concept out of a security group is the top residual risk.

## C. Catalog / business glossary / metadata

| Catalog record / glossary term | Owner | Keyed on (breadcrumb / parent_slug / level / scheme) | Disposition | Notes |
|---|---|---|---|---|
|  |  |  |  |  |

## D. Data products and integrations

| Data product / integration / downstream JSON | Owner | Field consumed (parent_slug / level / breadcrumb / membership) | Disposition | Notes |
|---|---|---|---|---|
|  |  |  |  |  |

## E. Saved queries, reports, navigation

| Saved SPARQL / SQL / report / navigation tree | Owner | Hierarchy traversal or breadcrumb logic | Disposition | Notes |
|---|---|---|---|---|
|  |  |  |  |  |

Old-breadcrumb queries must be repointed or retired deliberately — not left to return empty.

## F. Dispositions (use exactly these)

- `Updated` — asset repointed to the new path; change verified.
- `No consumer` — searched; nothing references the moved paths.
- `Compatibility mapping published` — asset cannot move before merge; old→new mapping recorded
  (attach it) so the cutover is explicit.
- `Sign-off required` — owner must explicitly accept the change before merge.

## G. Attestation

For each asset class above, the owner signs that the search was performed:

```text
Asset class: _______________  Owner: _______________  Date: _______________
Search method: _______________
Result: [ ] hits dispositioned above  [ ] no references found
Signature: _______________
```

**Unknown consumers:** if an asset class cannot be fully searched, say so explicitly and record
`Sign-off required` — do not default to `No consumer`. Absence of evidence is not evidence of
absence; the merge gate treats unsearched surface as a blocker, not a pass.

---

**Return:** completed checklist + updated `r1-path-compatibility-register.csv` dispositions.
The R1 implementation PR is built only after both are in hand.
