# Live Testing Checklist — Cypher Query Generator Skill

Run these steps when your agent client (VS Code + Copilot Agent Mode) is set up and the skill is loaded.

**Prerequisites:**
- VS Code with Copilot Agent Mode enabled
- Skill folder at `.agents/skills/cypher-query-generator/`
- Neo4j instance running with `governancemetadata` database
- Python venv activated with `neo4j` and `python-dotenv` installed

---

## Step 1: Trigger Testing — Train Set

Test whether the skill activates on the right prompts.  
Run each query 3 times in Copilot Chat to account for non-determinism.

```powershell
cd ".agents\skills\cypher-query-generator"
python scripts/test_triggers.py -q evals/train_trigger_queries.json -r 3 -s SKILL.md -o ..\..\..\cypher-query-generator-workspace\iteration-1\train_results.json
```

**If failures are found:**
- Review the failures and optimization hints printed by the script
- Revise the `description` field in `SKILL.md` (address general categories, not specific keywords)
- Re-run in a new iteration folder:

```powershell
python scripts/test_triggers.py -q evals/train_trigger_queries.json -r 3 -s SKILL.md -o ..\..\..\cypher-query-generator-workspace\iteration-2\train_results.json
```

## Step 2: Trigger Testing — Validation Set

After train set passes, test generalization on the held-out validation set.  
**Do NOT use validation failures to revise the description** — that causes overfitting.

```powershell
python scripts/test_triggers.py -q evals/validation_trigger_queries.json -r 1 -s SKILL.md -o ..\..\..\cypher-query-generator-workspace\iteration-1\validation_results.json
```

## Step 3: Pick Best Description

If you ran multiple iterations, compare **validation pass rates** across iterations.  
Pick the description with the highest validation pass rate — it may not be the latest one.

## Step 4: Fresh Verification (Post-Optimization)

After finalizing the description, run 8 never-seen queries as a sanity check:

```powershell
python scripts/test_triggers.py -q evals/verification_trigger_queries.json -r 1 -s SKILL.md -o ..\..\..\cypher-query-generator-workspace\verification_results.json
```

## Step 5: Output Quality — Without-Skill Baseline

Run the 7 eval prompts in a Copilot session **WITHOUT the skill loaded** (rename or move the `.agents/skills/` folder temporarily). Paste the generated Cypher into the script:

```powershell
python scripts/run_evals.py -e evals/evals.json -i 1 --interactive --mode without_skill -w ..\..\..\cypher-query-generator-workspace
```

This writes results to `without_skill/` subdirectories and **auto-computes the `delta`** in `benchmark.json` (since `with_skill` data already exists from our earlier run).

## Step 6: Human Review

Open each `feedback.json` in the workspace and add your notes after reviewing the query results in Neo4j Browser:

```
cypher-query-generator-workspace/iteration-1/eval-*/feedback.json
```

---

## Quick Reference — Script Commands

| Script | Purpose | Key Flags |
|---|---|---|
| `test_triggers.py` | Trigger testing | `-q` queries, `-r` runs, `-s` SKILL.md, `-o` output |
| `validate_cypher.py` | Validate single query | `-q` query, `-f` file, `-o` output |
| `run_evals.py` | Batch eval runner | `-e` evals.json, `-i` iteration, `--interactive` |
