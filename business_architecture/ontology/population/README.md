# population: what a measure counts

What each measure includes and excludes, in business words, where its public source states it (competency question 28). The statements hang on the kpi module's measure IRIs, so the released kpi package stays as it is. *2026-10-22:* `kpi` 1.1.0 carries these files in its package (EPM-DEC-001-0079). EPM-DEC-001-0062 records the choice.

| File | What |
|---|---|
| `population.csv` | Eight MPC-defined measures, each with what it includes, what it excludes where MPC says, and the evidence row |
| `vocabulary.ttl` | `pop:includes`, `pop:excludes` and `pop:populationEvidence` |
| `build_population.py`, `population.ttl` | The build. `--verify` fails unless `population.ttl` equals a fresh build. `scripts/check.sh` runs it |
| `test_population.py` | Tests: the build is current, the counts, the eight decided measures and every statement pinned to MPC's wording, and no other measure carries a population |

The other 33 measures have no population here, because no source states one: 31 from the planning team's list, the R&M Margin Indicator and turnaround lost margin. None is written in its place. Crack spreads is on the planning team's list too, but MPC states what its benchmark series exclude.
