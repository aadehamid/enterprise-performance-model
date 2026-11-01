"""The four shipped skills' own checks, one table for the skills-tests validation row (validate.py) and for the
release's check.sh (rebuild.py renders it): (skill, folder inside the skill, command, kind). A "tests" command must
report "Ran N tests" with N > 0 (unittest exits 0 on zero tests); a "check" command must exit 0. The skill "" is
the skills folder itself (the playbook pages' test, itself a unittest suite).
"""
import shlex

SKILL_CHECKS = [
    ("ontology", "scripts", ["uv", "run", "-q", "--no-project", "--with", "rdflib", "--with", "pyyaml", "--with", "pyshacl",
                             "python3", "-m", "unittest", "discover", "-q", "-p", "test_*.py"], "tests"),
    ("ontology", "", ["uv", "run", "-q", "--no-project", "--with", "pyyaml", "python3", "scripts/check_sssom.py", "templates/mappings.sssom.tsv"], "check"),
    ("ontology-to-lpg", "scripts", ["uv", "run", "-q", "--no-project", "--with", "rdflib", "--with", "pyshacl", "--with", "mcp-neo4j-data-modeling==0.8.2",
                                    "python3", "-m", "unittest", "-q", "test_projection", "test_engine_gate", "test_modeling", "test_explore", "test_run_projection"], "tests"),
    ("rdf-store", "scripts", ["uv", "run", "-q", "--no-project", "--with", "pyoxigraph", "python3", "-m", "unittest", "-q", "test_rdf_store"], "tests"),
    ("", "", ["uv", "run", "-q", "--no-project", "--with", "markdown-it-py>=4,<5", "python3", "scripts/test_playbook_html.py"], "tests"),
]


def render():
    """The skill section of the release's check.sh."""
    lines = []
    for skill, folder, cmd, kind in SKILL_CHECKS:
        cwd = "/".join(p for p in ("skills", skill, folder) if p)
        runner = "run_tests" if kind == "tests" else "run"
        lines.append(f"(cd {cwd} && {runner} {' '.join(shlex.quote(a) for a in cmd)})")
    return "\n".join(lines)


def name_of(skill, cmd, kind):
    """The row name of one check: the skill for its tests, skill:script for a check."""
    return skill if kind == "tests" and skill else f"{skill or 'skills'}:{next(a for a in cmd if a.endswith('.py')).rsplit('/', 1)[-1]}"
