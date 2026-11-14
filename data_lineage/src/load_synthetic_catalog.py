"""Load a generated Lagos Refining & Supply Company (LSC) catalog into Neo4j.

Runs the steps of synthetic/ingest.cypher (built from lsc_data_model.json by the
mcp-neo4j-data-modeling ingest generator) over the JSONL files written by
generate_shareable_catalog.py, then checks the database against manifest.json.

Usage:
    .venv\\Scripts\\python.exe src\\load_synthetic_catalog.py --database lsc
    .venv\\Scripts\\python.exe src\\load_synthetic_catalog.py --database lsc --data synthetic_data

The target database must be empty or already hold an LSC catalog.
"""

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from neo4j.exceptions import ClientError

from neo4j_loader import Neo4jLoader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INGEST_PATH = PROJECT_ROOT / "synthetic" / "ingest.cypher"
DEFAULT_DATA = PROJECT_ROOT / "synthetic_data"
LSC_MARKER = "MATCH (d:DataSystem {name: 'Helios'})-[:HOSTS]->(:Schema) RETURN count(d) AS n"

STEP_HEADER = re.compile(r"^// step: (constraint|node|label|rel) (.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Step:
    kind: str
    target: str
    query: str

    @property
    def data_file(self) -> str | None:
        if self.kind == "node":
            return f"nodes/{self.target}.jsonl"
        if self.kind == "label":
            return f"labels/{self.target.replace(' ', '-')}.jsonl"
        if self.kind == "rel":
            return f"rels/{self.target}.jsonl"
        return None


def parse_steps(text: str) -> list[Step]:
    headers = list(STEP_HEADER.finditer(text))
    steps = []
    for header, nxt in zip(headers, [*headers[1:], None]):
        body = text[header.end(): nxt.start() if nxt else len(text)].strip().rstrip(";").strip()
        steps.append(Step(header.group(1), header.group(2).strip(), body))
    return steps


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def database_counts(loader: Neo4jLoader, steps: list[Step]) -> dict:
    counts = {"nodes": {}, "labels": {}, "rels": {}}
    for step in steps:
        if step.kind == "node":
            q = f"MATCH (n:`{step.target}`) RETURN count(n) AS n"
            counts["nodes"][step.target] = loader.run_query(q)[0]["n"]
        elif step.kind == "label":
            label, extra = step.target.split()
            q = f"MATCH (n:`{label}`:`{extra}`) RETURN count(n) AS n"
            counts["labels"][f"{label}:{extra}"] = loader.run_query(q)[0]["n"]
        elif step.kind == "rel":
            start, rel, end = step.target.split("-")
            q = f"MATCH (:`{start}`)-[r:`{rel}`]->(:`{end}`) RETURN count(r) AS n"
            counts["rels"][step.target] = loader.run_query(q)[0]["n"]
    return counts


def count_mismatches(expected: dict, actual: dict) -> list[str]:
    return [
        f"{group} {key}: database {actual[group].get(key, 0)} vs manifest {want}"
        for group, wants in expected.items()
        for key, want in wants.items()
        if actual[group].get(key, 0) != want
    ]


def assert_safe_target(loader: Neo4jLoader) -> None:
    total = loader.run_query("MATCH (n) RETURN count(n) AS n")[0]["n"]
    if total and not loader.run_query(LSC_MARKER)[0]["n"]:
        raise SystemExit(
            f"Refusing to load: database '{loader.database}' holds {total} nodes and no LSC catalog. "
            "Create an empty database (CREATE DATABASE lsc) and pass --database lsc."
        )


def community_constraint(query: str) -> str:
    """Community Edition has no NODE KEY; a uniqueness constraint keeps MERGE lookups indexed."""
    return query.replace("IS NODE KEY", "IS UNIQUE")


def create_constraint(loader: Neo4jLoader, query: str) -> None:
    try:
        loader.run_write(query)
    except ClientError:
        if "IS NODE KEY" not in query:
            raise
        loader.run_write(community_constraint(query))


def load(loader: Neo4jLoader, data: Path, steps: list[Step]) -> None:
    for step in steps:
        if step.kind == "constraint":
            create_constraint(loader, step.query)
            continue
        path = data / step.data_file
        if not path.exists():
            print(f"  skip {step.kind} {step.target}: no {step.data_file}")
            continue
        written = loader.write_batches(step.query, read_rows(path))
        print(f"  {step.kind:<5} {step.target}: {written} rows")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", required=True, help="Target Neo4j database, for example lsc")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    args = parser.parse_args()

    manifest = json.loads((args.data / "manifest.json").read_text(encoding="utf-8"))
    steps = parse_steps(INGEST_PATH.read_text(encoding="utf-8"))
    loader = Neo4jLoader(database=args.database)
    try:
        assert_safe_target(loader)
        print(f"Loading {manifest['company']} (seed {manifest['seed']}) into '{args.database}'")
        load(loader, args.data, steps)
        mismatches = count_mismatches(manifest["counts"], database_counts(loader, steps))
    finally:
        loader.close()
    if mismatches:
        raise SystemExit("Database does not match manifest:\n  " + "\n  ".join(mismatches))
    nodes = sum(manifest["counts"]["nodes"].values())
    rels = sum(manifest["counts"]["rels"].values())
    print(f"Database '{args.database}' matches manifest: {nodes} nodes, {rels} relationships")


if __name__ == "__main__":
    main()
