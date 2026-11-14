# Vendored: neo4j-cypher-skill

| | |
|---|---|
| Source | https://github.com/neo4j-contrib/neo4j-skills/tree/main/neo4j-cypher-skill |
| Upstream commit | `39247b9c4ab20062aefd1cfe83c040167ef9ee83` (2026-10-21) |
| Version | 1.0.30 (`SKILL.md` frontmatter) |
| Vendored on | 2026-10-31 |
| License | MIT, Copyright (c) 2026 Neo4j Contrib (`LICENSE`, copied from the upstream repo root) |

Files are an unmodified copy of the upstream folder. Only `LICENSE` and this file were added.

This copy is for coding agents writing or reviewing loader and fix Cypher. The portal backend does not load it; the portal's runtime skill is `../cypher-query-generator/`, which carries an adapted subset of `references/syntax-traps.md` as `references/cypher_syntax_traps.md`.

## Update

```powershell
git clone --depth 1 https://github.com/neo4j-contrib/neo4j-skills.git $env:TEMP\neo4j-skills
git -C $env:TEMP\neo4j-skills log -1 --format="%H %cI"
Get-ChildItem .agents\skills\neo4j-cypher-skill -Exclude VENDORED.md | Remove-Item -Recurse -Force
Copy-Item -Recurse $env:TEMP\neo4j-skills\neo4j-cypher-skill\* .agents\skills\neo4j-cypher-skill\
Copy-Item $env:TEMP\neo4j-skills\LICENSE .agents\skills\neo4j-cypher-skill\LICENSE
Remove-Item -Recurse -Force $env:TEMP\neo4j-skills
```

Then update the commit, version and date above, diff upstream `references/syntax-traps.md` against the previous version, and carry relevant changes into `../cypher-query-generator/references/cypher_syntax_traps.md` (keeping its Cypher 5 / read-only adaptations).
