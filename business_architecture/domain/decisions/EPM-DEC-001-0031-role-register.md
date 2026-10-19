# EPM-DEC-001-0031: The role register: how the process map's RACI role strings become roles

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028); its questions answered by Hamid, EPM-DEC-001-0045 (2026-10-18) |
| Date | 2026-10-13 |
| Questions | Step 5, slice 2: which of the RACI role strings in the process map name the same role, and how a team, a qualifier or a compound string is handled |
| Source | Claude Code session, 2026-10-13, under Hamid's extension of the delegation to Steps 5 to 12 (EPM-DEC-001-0028, amended in #252) |

## Context

The process map, `business_architecture/business_process/downstream_process_map.json`, holds a `raci` object on 153 processes. Its lists hold 913 entries, written as 91 distinct strings. Many strings are spellings of one role: "Refinery Scheduler", "Refinery scheduler", "Refinery Schedulers" and "Refinery schedulers". Some name a team ("Risk Group"), some add a qualifier ("Distribution planner (optional)"), and 11 name two or three roles at once ("Supply Coordinators/Traders").

EPM-DEC-001-0030 makes each RACI entry an `orgm:ResponsibilityAssignment` that names one `org:Role`. The roles must exist before the assignments do (slice 3).

The repository does not expand the acronyms in the role strings (CCI, CP, CPVC, E&P, GFVC, PSM, RCVO, RVCO, BP&A, RFC, RO). No MPC or peer filing in `business_architecture/reference/` names these roles.

## Decision

`business_architecture/ontology/organization/role-register.csv` maps each of the 91 strings to one or more of the 60 roles in `roles.csv`. `build_roles.py` checks the register against the process map and writes `roles.ttl`. The rules:

1. **Merge only on the surface of the text.** Two strings name the same role only when they differ in case, plural, punctuation, or "&" against "and". Nothing is merged on a guess at what an acronym or a title means.
2. **A qualifier stays with the entry, not the role.** "Distribution planner (optional)" maps to Distribution Planner. The qualifier is kept in the register, and slice 3 keeps the full source string on each assignment (`orgm:sourceRoleText`).
3. **A compound string is split into its roles.** "Supply Coordinators/Traders" maps to Supply Coordinator and Trader. Slice 3 then emits one assignment per role.
4. **A team named in a RACI list becomes a role, with a scope note.** Six strings name a team: BP&A, Operations, Regional Planning Team, Risk Group, Site Tactical Team and Tech Services. Each becomes an `org:Role` whose scope note says it stands for the team acting as one RACI party. The org units themselves come in slice 5.
5. **Each role gets one English name** (`skos:prefLabel`). A different spelling of the whole role, with no qualifier, is kept as `skos:altLabel`.
6. **Role IRIs** are `https://w3id.org/lsc/ontology/modules/organization/role/{slug}`, the `…/modules/{module}` pattern of the URI policy.

The result: 60 roles, 54 positions and 6 teams. Splitting the 11 compound strings turns the 913 entries into 940 role references. `build_roles.py` prints the figures.

### Questions for Hamid

*2026-10-18:* answered by Hamid; organization 2.0.0 carries the answers (EPM-DEC-001-0045). Forecaster and PSM stay open.

These do not block the build. Each would merge two roles, or define one, if Hamid confirms it. `roles.csv` holds each one in its `question` column.

- **RCVO Advisor** (written once) and **RVCO Advisor** (written 32 times): one role misspelt?
- **Forecaster** and **Refinery Technical Service Representative** appear only inside two compound strings. Are they the Local Refinery Forecaster and the Refinery Technical Representative?
- **The two VP strings** differ only in RVCO. Are they one VP?
- **Crude RFC**: is it the crude Refinery Feedstock Coordinator?
- **The acronyms** (CCI, CP, CPVC, E&P, GFVC, PSM, RVCO, BP&A, RO): what does each stand for? The answers become role definitions.

## Alternatives considered

- **Merge by meaning now** (RCVO into RVCO, Forecaster into Local Refinery Forecaster). Rejected: the evidence is the spelling alone, and a wrong merge would assign one role's responsibilities to another. Splitting later costs more than merging later.
- **Model teams as `org:OrganizationalUnit`, assigned directly.** Rejected for this slice: EPM-DEC-001-0030 gives an assignment exactly one `org:Role`, and changing that shape for six strings would widen every query that asks who is accountable. Slice 5 links the units.
- **Put the whole register to Hamid before building on it.** Rejected: under rule 1 the register applies only mechanical rules, which the delegation covers. The judgement calls are listed above, for Hamid to answer when convenient.

## Hamid's recorded words

Hamid extended the delegation in the Claude Code session on 2026-10-13 (saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-steps-5-12.md`): "yes, extend the delegation to steps 5 to 12." Hamid did not make the choices above himself. Claude made them under that delegation, and Hamid can reverse any of them.

## Evidence

`downstream_process_map.json` (`raci` on 153 processes); EPM-DEC-001-0030; `ontology-playbook.md`, Step 5; the URI policy in `step4/playbook/ontology-worklog.md`. A search of the repository for each acronym found no expansion.

## Consequences

- `scripts/check.sh` runs `build_roles.py --verify` and `test_roles.py`. A new role string in the process map fails the check until the register maps it.
- Slice 3 emits the assignments from this register.
- An answer to a question above changes `roles.csv` and the register in a later PR, and records the answer here.
