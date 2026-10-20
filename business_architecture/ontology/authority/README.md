# authority: which source wins

Competency question 44 asks which definition is authoritative when two sources disagree, and how that is marked. This module gives every source the modules cite an evidence tier, from the evidence order in `AGENTS.md`: (1) the process authority and the decision owner's own material, (2) Marathon Petroleum, (3) U.S. refining peers, (4) downstream industry and regulatory sources, (5) generic frameworks, support only. For a concept that cites several sources, a source in its best tier is authoritative. EPM-DEC-001-0059 records the choice.

| File | What |
|---|---|
| `vocabulary.ttl` | The `evidenceTier` property and the five tiers, each with its rank |
| `source-tiers.csv` | The 60 cited sources, each with its tier: 9 in tier 1, 1 in tier 2, 1 in tier 3, 41 in tier 4 and 8 in tier 5 |
| `build_source_tiers.py`, `source-tiers.ttl` | The build. `--verify` fails unless `source-tiers.ttl` equals a fresh build. `scripts/check.sh` runs it |
| `test_source_tiers.py` | Tests: the build is current, every source the release and modules cite has a tier, and sample tiers match the record |
