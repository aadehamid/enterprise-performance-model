"""The snippet runner's classification and its shell state (plan step 7, "Every snippet")."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snippets  # noqa: E402


def test_databricks_sql_is_not_sparql():
    assert snippets.kind_of({"lang": "", "text": "SELECT e.source, t.object\nFROM idp_sbx.tech_graph.edges e"}) == "sql"
    assert snippets.kind_of({"lang": "", "text": "SELECT a, MEASURE(b) AS m\nFROM v GROUP BY ALL"}) == "sql"
    assert snippets.kind_of({"lang": "", "text": "PREFIX x: <u>\nSELECT ?s WHERE { ?s a x:T }"}) == "sparql"
    assert snippets.kind_of({"lang": "", "text": "SELECT ?s WHERE { ?s ?p ?o }"}) == "sparql"


def test_a_from_comment_sets_the_folder_and_variables_carry_across_blocks():
    with tempfile.TemporaryDirectory() as tree:
        os.makedirs(os.path.join(tree, "a", "b"))
        with open(os.path.join(tree, "a", "b", "x.txt"), "w") as f:
            f.write("hi\n")
        state = {}
        r = snippets.run_shell("# from a/b\ncat x.txt", tree, {}, state)
        assert r["lines"][0]["ran"] and r["lines"][0]["returncode"] == 0 and "hi" in r["lines"][0]["tail"]
        r = snippets.run_shell("# from a\nls .\n# from a/b\ncat x.txt", tree, {}, state)
        assert [x["returncode"] for x in r["lines"]] == [0, 0] and "hi" in r["lines"][1]["tail"]
        r = snippets.run_shell("# from nowhere\nls .", tree, {}, state)  # the block stops: nothing runs in the wrong folder
        assert r["lines"][0] == {"line": "# from nowhere", "ran": False, "reason": "folder not in the tree", "failed_folder": True}
        assert r["lines"][1]["ran"] is False and "stopped" in r["lines"][1]["reason"] and r["failed"] == [r["lines"][0]] and r["stopped_at"] == "# from nowhere"
        r = snippets.run_shell("cd nowhere\nls .", tree, {}, state)
        assert r["lines"][1]["ran"] is False and r["failed"] == [r["lines"][0]]
        r = snippets.run_shell("cd nowhere\nls .", tree, {}, state, strict=False)  # a skill's example folder: listed, not failed
        assert r["lines"][1]["ran"] is False and r["failed"] == [] and r["stopped_at"] == "cd nowhere"
        r = snippets.run_shell("# from repository root\nls a", tree, {}, state)
        assert r["lines"][0]["ran"] and r["lines"][0]["returncode"] == 0 and "b" in r["lines"][0]["tail"]
        os.makedirs(os.path.join(tree, "skills", "s", "scripts"))
        r = snippets.run_shell('# from $SKILLS/s/scripts\nls .\ncd "$EPM/a"\nls .', tree, {}, state)  # the reader's variables are the tree's
        assert [x.get("returncode", x.get("ran")) for x in r["lines"]] == [0, True, 0] and "b" in r["lines"][2]["tail"]
        r = snippets.run_shell('DIR=' + os.path.join(tree, "a") + '; mkdir -p "$DIR"', tree, {}, state)
        assert state["vars"]["DIR"] == os.path.join(tree, "a") and not r["failed"]
        r = snippets.run_shell('ls "$DIR/b"', tree, {}, state)
        assert r["lines"][0]["ran"] and "x.txt" in r["lines"][0]["tail"]
        r = snippets.run_shell('ls "$OTHER"', tree, {}, state)
        assert r["lines"][0]["ran"] is False and "OTHER" in r["lines"][0]["reason"]


def test_every_document_in_the_tree_is_read_once():
    with tempfile.TemporaryDirectory() as tree:
        for rel in ("README.md", "README.html", "guide.html", "a/b.md", "scripts/docs_template.html", "skills/scripts/playbook_template.html", ".venv/x.md", "__pycache__/y.md", "c.txt"):
            os.makedirs(os.path.dirname(os.path.join(tree, rel)) or tree, exist_ok=True)
            with open(os.path.join(tree, rel), "w") as f:
                f.write("x")
        assert snippets.documents(tree) == ["README.md", "a/b.md", "guide.html"]


def test_the_test_neo4j_login_comes_from_env_or_the_store_rows_login_file():
    with tempfile.TemporaryDirectory() as d:
        assert snippets.neo4j_login({}) == ""
        assert snippets.neo4j_login({"IMPORT_DIR": d}) == ""
        with open(os.path.join(d, "validate-neo4j.env"), "w") as f:
            f.write("NEO4J_URI=bolt://localhost:17799\nNEO4J_PASSWORD=fromfile\n")
        assert snippets.neo4j_login({"IMPORT_DIR": d}) == "fromfile"
        assert snippets.neo4j_login({"IMPORT_DIR": d, "TEST_NEO4J_PASSWORD": "given"}) == "given"
