"""
Trigger Testing Script for Description Optimization.

Automates the trigger evaluation workflow from the Agent Skills spec.
Since we can't programmatically invoke an agent client, this script provides
an interactive CLI that guides the user through testing each query and captures
structured results.

Workflow:
  1. Reads trigger queries from a JSON file (train or validation)
  2. For each query, displays it and asks the user whether the skill triggered
  3. Supports multiple runs per query (spec recommends 3x) for non-determinism
  4. Computes pass rates and identifies failures
  5. Snapshots the current SKILL.md description (so each iteration is traceable)
  6. Outputs structured results to JSON

Usage:
    python test_triggers.py --queries evals/train_trigger_queries.json --runs 3 --skill-md ../SKILL.md --output iter1_train.json
    python test_triggers.py --queries evals/validation_trigger_queries.json --runs 1 --skill-md ../SKILL.md --output iter1_val.json

Post-optimization verification:
    python test_triggers.py --queries evals/verification_trigger_queries.json --runs 1 --skill-md ../SKILL.md
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime


def extract_description(skill_md_path):
    """Extract the description field from SKILL.md frontmatter."""
    if not skill_md_path or not os.path.exists(skill_md_path):
        return None
    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Match YAML frontmatter description block
    match = re.search(r'description:\s*>\s*\n(.*?)(?=\n\w+:)', content, re.DOTALL)
    if match:
        return " ".join(match.group(1).strip().split())
    return None


def run_interactive_test(queries_file, runs_per_query, output_file, skill_md_path=None):
    """Run interactive trigger testing."""
    with open(queries_file, "r") as f:
        data = json.load(f)

    queries = data["queries"]
    skill_name = data.get("skill_name", "unknown")
    description = extract_description(skill_md_path)
    results = []

    print(f"\n{'='*70}")
    print(f"  TRIGGER TESTING — {os.path.basename(queries_file)}")
    print(f"  Skill: {skill_name}")
    if description:
        print(f"  Description: {description[:80]}...")
    print(f"  Queries: {len(queries)} | Runs per query: {runs_per_query}")
    print(f"{'='*70}")
    print()
    print("  For each query, paste it into your agent client (e.g., VS Code")
    print("  Copilot Chat) and observe whether the skill activates.")
    print()
    print("  Enter: y = triggered, n = did not trigger, s = skip")
    print(f"{'='*70}\n")

    for q in queries:
        qid = q["id"]
        prompt = q["prompt"]
        should_trigger = q["should_trigger"]
        category = q.get("category", "")

        print(f"\n--- Query {qid} ({category}) ---")
        print(f"  Prompt: \"{prompt}\"")
        print(f"  Expected: {'SHOULD trigger' if should_trigger else 'should NOT trigger'}")

        trigger_count = 0
        run_results = []
        skipped = False

        for run in range(1, runs_per_query + 1):
            while True:
                suffix = f" [run {run}/{runs_per_query}]" if runs_per_query > 1 else ""
                answer = input(f"  Did skill trigger?{suffix} (y/n/s): ").strip().lower()
                if answer in ("y", "n", "s"):
                    break
                print("  Please enter y, n, or s")

            if answer == "s":
                skipped = True
                break
            triggered = answer == "y"
            run_results.append(triggered)
            if triggered:
                trigger_count += 1

        if skipped:
            print("  → Skipped")
            results.append({
                "id": qid,
                "prompt": prompt,
                "should_trigger": should_trigger,
                "category": category,
                "skipped": True,
                "passed": None,
                "trigger_rate": None
            })
            continue

        trigger_rate = trigger_count / runs_per_query
        # A query passes if:
        # - should_trigger=true AND trigger_rate >= 0.5 (triggered at least half the time)
        # - should_trigger=false AND trigger_rate == 0 (never triggered)
        if should_trigger:
            passed = trigger_rate >= 0.5
        else:
            passed = trigger_rate == 0

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  → {status} (trigger_rate: {trigger_rate:.2f})")

        results.append({
            "id": qid,
            "prompt": prompt,
            "should_trigger": should_trigger,
            "category": category,
            "skipped": False,
            "triggers": trigger_count,
            "runs": runs_per_query,
            "trigger_rate": trigger_rate,
            "passed": passed,
            "run_results": run_results
        })

    # Compute summary
    tested = [r for r in results if not r.get("skipped")]
    passed_count = sum(1 for r in tested if r["passed"])
    failed_count = sum(1 for r in tested if not r["passed"])
    total = len(tested)
    pass_rate = round(passed_count / total, 2) if total > 0 else 0

    should_trigger_results = [r for r in tested if r["should_trigger"]]
    should_not_trigger_results = [r for r in tested if not r["should_trigger"]]

    st_passed = sum(1 for r in should_trigger_results if r["passed"])
    snt_passed = sum(1 for r in should_not_trigger_results if r["passed"])

    failures = [r for r in tested if not r["passed"]]

    output = {
        "queries_file": os.path.basename(queries_file),
        "skill_name": skill_name,
        "description_snapshot": description,
        "timestamp": datetime.now().isoformat(),
        "runs_per_query": runs_per_query,
        "results": results,
        "summary": {
            "total_tested": total,
            "total_skipped": len(results) - total,
            "passed": passed_count,
            "failed": failed_count,
            "pass_rate": pass_rate,
            "should_trigger": {
                "total": len(should_trigger_results),
                "passed": st_passed,
                "pass_rate": round(st_passed / len(should_trigger_results), 2) if should_trigger_results else 0
            },
            "should_not_trigger": {
                "total": len(should_not_trigger_results),
                "passed": snt_passed,
                "pass_rate": round(snt_passed / len(should_not_trigger_results), 2) if should_not_trigger_results else 0
            }
        },
        "failures": [{
            "id": f["id"],
            "prompt": f["prompt"],
            "should_trigger": f["should_trigger"],
            "category": f.get("category", ""),
            "trigger_rate": f["trigger_rate"]
        } for f in failures]
    }

    # Print summary
    print(f"\n{'='*70}")
    print(f"  RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"  Overall: {passed_count}/{total} passed ({pass_rate:.0%})")
    print(f"  Should-trigger:     {st_passed}/{len(should_trigger_results)} passed")
    print(f"  Should-NOT-trigger: {snt_passed}/{len(should_not_trigger_results)} passed")

    if failures:
        print(f"\n  FAILURES ({len(failures)}):")
        for f in failures:
            direction = "should have triggered but didn't" if f["should_trigger"] else "should NOT have triggered but did"
            print(f"    • [{f.get('category','')}] \"{f['prompt'][:60]}...\" — {direction}")

        print(f"\n  OPTIMIZATION HINTS:")
        st_failures = [f for f in failures if f["should_trigger"]]
        snt_failures = [f for f in failures if not f["should_trigger"]]
        if st_failures:
            categories = set(f.get("category", "") for f in st_failures)
            print(f"    → Description may be too NARROW. Missing categories: {categories}")
            print(f"      Add broader concepts (not specific keywords) for these areas.")
        if snt_failures:
            categories = set(f.get("category", "") for f in snt_failures)
            print(f"    → Description may be too BROAD. False-triggering categories: {categories}")
            print(f"      Add specificity about what the skill does NOT do.")

    # Write output
    if output_file:
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\n  Results written to: {output_file}")
    else:
        print(f"\n  (Use --output <file> to save results to JSON)")

    print()
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Interactive trigger testing for skill description optimization"
    )
    parser.add_argument("--queries", "-q", required=True,
                        help="Path to trigger queries JSON file")
    parser.add_argument("--runs", "-r", type=int, default=1,
                        help="Number of runs per query (default: 1, spec recommends 3)")
    parser.add_argument("--output", "-o",
                        help="Path to write results JSON")
    parser.add_argument("--skill-md", "-s",
                        help="Path to SKILL.md to snapshot the description (recommended)")
    args = parser.parse_args()

    if not os.path.exists(args.queries):
        print(f"ERROR: File not found: {args.queries}")
        sys.exit(1)

    run_interactive_test(args.queries, args.runs, args.output, args.skill_md)


if __name__ == "__main__":
    main()
