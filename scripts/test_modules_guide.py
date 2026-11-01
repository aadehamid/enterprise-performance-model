"""Every Turtle example in business_architecture/ontology/MODULES.md is quoted from a released package.

Each ```turtle block follows a `<!-- module: <name> -->` line. The test parses the block and fails
when any of its triples is not in the newest release of that module, so a release that drops or
changes a quoted triple breaks this test until the guide is updated.

Run: uv run --with pytest --with rdflib python -m pytest -q scripts/test_modules_guide.py
"""
import os
import re
import sys

import pytest
import rdflib
from rdflib.namespace import XSD

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import epm_facts  # noqa: E402

GUIDE = os.path.join(epm_facts.ROOT, "business_architecture", "ontology", "MODULES.md")
BLOCK = re.compile(r"<!-- module: ([\w-]+) -->\n```turtle\n(.*?)```", re.S)


def quoted_blocks(text):
    return BLOCK.findall(text)


def plain(term):
    """RDF 1.1 reads a literal with no tag or type as xsd:string; rdflib keeps the two apart."""
    if isinstance(term, rdflib.Literal) and term.datatype == XSD.string:
        return rdflib.Literal(str(term))
    return term


def missing_triples(module, turtle, releases=epm_facts.RELEASES):
    release = {tuple(plain(t) for t in triple) for triple in epm_facts.newest_graph(module, releases)}
    block = rdflib.Graph().parse(data=turtle, format="turtle")
    return sorted(str(t) for t in block if tuple(plain(x) for x in t) not in release)


def test_every_turtle_block_names_its_module():
    text = open(GUIDE, encoding="utf-8").read()
    assert text.count("```turtle") == len(quoted_blocks(text))


@pytest.mark.parametrize("module,turtle", quoted_blocks(open(GUIDE, encoding="utf-8").read()))
def test_each_quoted_triple_is_in_the_newest_release_of_its_module(module, turtle):
    assert missing_triples(module, turtle) == []


def test_a_triple_the_release_no_longer_holds_fails(tmp_path):
    folder = tmp_path / "lane" / "1.0.0"
    folder.mkdir(parents=True)
    (folder / "manifest.json").write_text("{}")
    (folder / "lane.ttl").write_text("<urn:p> <urn:officeLane> <urn:front> .\n")
    assert missing_triples("lane", "<urn:p> <urn:officeLane> <urn:front> .\n", str(tmp_path)) == []
    assert missing_triples("lane", "<urn:p> <urn:officeLane> <urn:back> .\n", str(tmp_path)) != []


def test_the_files_table_lists_what_the_builder_packages():
    """"The three files of each package": every part and shape file the module builder names is in its module's row."""
    import ast
    with open(epm_facts.MODULE_BUILDER, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    modules = next(ast.literal_eval(n.value) for n in tree.body
                   if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "MODULES")
    with open(GUIDE, encoding="utf-8") as f:
        rows = {cells[1].strip("` "): cells for cells in (line.split("|") for line in f if line.startswith("| `"))}
    for module, spec in modules.items():
        for part in spec["parts"]:
            assert f"`{part}`" in rows[module][3], (module, part)
        for shape in spec["shapes"]:
            if not shape.startswith("releases/"):  # a pinned module's shapes, named in words
                assert f"`{shape}`" in rows[module][4], (module, shape)
    assert set(rows) >= set(modules) | {"core"}
