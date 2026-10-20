# population: what a measure counts

What each measure includes and excludes, in business words, where its public source states it (competency question 28). The statements hang on the kpi module's measure IRIs, so the released kpi package stays as it is. EPM-DEC-001-0062 records the choice.

| File | What |
|---|---|
| `population.csv` | Eight MPC-defined measures, each with what it includes, what it excludes where MPC says, and the evidence row |
| `vocabulary.ttl` | `pop:includes`, `pop:excludes` and `pop:populationEvidence` |
| `build_population.py`, `population.ttl` | The build. `--verify` fails unless `population.ttl` equals a fresh build. `scripts/check.sh` runs it |
| `test_population.py` | Tests: the build is current, the counts, statements pinned to MPC's wording, and no planner measure carries an invented population |

The 33 measures from the planning team's list have no population here: the list does not state one, and none is written in its place.
