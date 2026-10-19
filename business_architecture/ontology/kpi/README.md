# kpi: measure definitions

The `kpi` module defines the measures that Hamid's planning team uses and that MPC publishes. It holds definitions only, never values (EPM-DEC-001-0005). Its namespace is `https://w3id.org/lsc/ontology/modules/kpi/`; it depends on `core` 2.1.0 for process IRIs and uses W3C ORG's `org:Role` by IRI.

| File | What |
|---|---|
| `measure-classification.csv` | One row per distinct measure: its class, whether it is a KPI candidate, the personas who use it, what it is compared against, MPC's counterpart, the reason and the evidence (EPM-DEC-001-0042) |
| `measure-details.csv` | Each measure's definition, grain, basis, aliases, the measures it is not to be confused with and how, and the core processes it informs (EPM-DEC-001-0043) |
| `personas.csv` | The four planning personas, with plan type and horizon |
| `vocabulary.ttl`, `shapes.ttl` | The module's terms and SHACL shapes, with a stated cardinality on every property (EPM-DEC-001-0043) |
| `build_measures.py`, `measures.ttl` | The build: three tables in, 41 measure definitions and 4 personas out. `python3 build_measures.py` prints the figures; `--verify` fails unless `measures.ttl` equals a fresh build. `scripts/check.sh` runs it |
| `test_measures.py` | Tests: the vocabulary is well formed, the build is current and reconciles, SHACL accepts the module and rejects broken measures, and no person's name from the measure list is in any tracked text file (every extension; binary files skipped), in any case, hyphenated, CamelCase or accented spelling |

The module is released as 1.0.0 (`../releases/kpi/1.0.0/`), approved by Hamid, and requires core 2.1.0.

Where the rows come from: Hamid's planner measure list of 2026-10-18, which stays outside the repository (EPM-DEC-001-0040), and MPC's public measures (`../../reference/mpc/mpc-performance-measures-evidence.md`).

Personas are planning roles, not people: Prompt Planner (prompt month, hourly and daily schedule), Short-Term Planner (M+1 to M+3 LP plan), Distribution Planner (distribution plan, prompt to M+3) and Mid-Term Planner (M+4 to M+36).

## Classes

| Class | Meaning |
|---|---|
| `kpi` | Designated as one of the few measures of a stated objective, with a target and an owner |
| `operational-metric` | A recurring performance measure of a unit, asset or flow, watched by exception |
| `plan-variance-diagnostic` | Actual results, or a plan, compared with a plan, forecast, plan version or history, for one period |
| `market-indicator` | An external price, spread or benchmark the region cannot influence |
| `decision-support-indicator` | A value computed from market prices and the planning model to start or rank a decision |
| `tracker-or-report` | A list, status or schedule; no formula, unit or grain |
| `alert` | An event raised when a condition is met |
| `not-a-measure` | A capability request, parked for a later phase |

`kpi_candidate = yes` marks an operational metric that the evidence makes a strong KPI candidate. It becomes a KPI only by a recorded decision that names its target and owner.
