# Cypher Syntax Traps

Common mistakes LLMs make when writing Cypher, and the form that works on this graph. Check every query against this table before returning it.

The `lsc` database runs on Neo4j 2025.06 with **default language Cypher 5**. Cypher 25-only syntax (`LET`, `FILTER` clause, `INSERT`, `coll.*` functions) fails here. The portal is read-only, so write-clause traps are omitted.

| Invalid | Correct |
|---|---|
| `ORDER BY n.prop AS alias DESC` | `ORDER BY n.prop DESC` — `AS` not allowed in ORDER BY |
| `ORDER BY n.score DESC NULLS LAST` | `ORDER BY n.score DESC` — NULLS LAST is SQL, not Cypher |
| `ORDER BY preAggVar` after aggregating RETURN | Use the RETURN alias: `RETURN count(m) AS cnt ORDER BY cnt` |
| `count(r WHERE r.rating = 5)` | `sum(CASE WHEN r.rating = 5 THEN 1 ELSE 0 END)` or `count(CASE WHEN ... THEN 1 END)` |
| `collect(x ORDER BY y)` | Preceding `WITH ... ORDER BY y` clause, or `COLLECT { MATCH ... RETURN x ORDER BY y }` |
| `rank() OVER (PARTITION BY ...)` | Not valid — use `collect({v:v}) AS ranked UNWIND range(0, size(ranked)-1) AS idx` |
| `UNWIND list AS x WHERE x > 5` | `UNWIND list AS x WITH x WHERE x > 5` |
| `least(a,b)` / `greatest(a,b)` | `CASE WHEN a < b THEN a ELSE b END` |
| `-- SQL comment` | `// Cypher comment` |
| `SELECT`, `GROUP BY`, `HAVING`, `JOIN` | Cypher aggregates implicitly by the non-aggregated RETURN/WITH keys; filter aggregates with `WITH ... WHERE` |
| `FILTER x IN list WHERE ...` / `LET x = expr` | `[x IN list WHERE ...]` / `WITH expr AS x` — `FILTER` and `LET` clauses are Cypher 25 only |
| `coll.sort(list)` / `apoc.coll.sort(list)` | Sort rows with `ORDER BY` before `collect()` |
| `id(n)` | `elementId(n)` |
| `CALL { WITH x ... }` | `CALL (x) { ... }` — importing WITH is deprecated |
| `n.dateProp >= date('2025-01-01')` on ZONED DATETIME | Use `.year` accessor or `datetime()` literal |
| `duration.between(d1,d2).inDays` (error) or `.days` for total days | `duration.inDays(d1,d2).days` — total days; `.days` alone is component (Jan 1 → Mar 15 = 14) |
| `WHERE n.x = null` | `WHERE n.x IS NULL` |
| `WHERE n.x <> null` | `WHERE n.x IS NOT NULL` |
| `MATCH (n:A) MATCH (m:A)` without join predicate | Causes CartesianProduct — add `WHERE` join condition |
| `COLLECT { (a)-[:R]->(b) }` | `COLLECT { MATCH (a)-[:R]->(b) RETURN b }` — bare pattern invalid |
| `COLLECT { MATCH ... RETURN x, y }` | `COLLECT {}` must return exactly one column |
| `min()` / `max()` as scalar in `range()` | Use `CASE WHEN size(l) < 3 THEN size(l)-1 ELSE 2 END` — these are aggregations |
| `(a)-[:REL]-{2,4}-(b)` bare quantifier | Wrap in node group: `(a)(()-[:REL]->()){2,4}(b)` |
| `2 IN [1, null, 3]` expecting `false` | Returns `null` — guard source list with IS NOT NULL |
| `n.$key` dynamic property | `n[$key]` — dot notation with parameter is SyntaxError |
| `(a)-[:R]-(b)` expecting one direction | Returns matches in both directions — use `(a)-[:R]->(b)` |
| `RETURN DISTINCT a, b` deduplicates `a` | `RETURN DISTINCT` deduplicates complete rows, not individual columns |
| `toInteger(null)` throws | `toIntegerOrNull(null)` returns `null` safely |

Lineage traversal keeps the project rule `-[:DERIVED_FROM*1..5]->`; do not rewrite it as a quantified path pattern.

Adapted from `references/syntax-traps.md` in [neo4j-contrib/neo4j-skills](https://github.com/neo4j-contrib/neo4j-skills) `neo4j-cypher-skill` v1.0.30 (MIT, Copyright (c) 2026 Neo4j Contrib).
