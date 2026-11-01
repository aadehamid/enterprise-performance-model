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
        r = snippets.run_shell("# from nowhere\nls", tree, {}, state)
        assert r["lines"][0] == {"line": "# from nowhere", "ran": False, "reason": "folder not in the tree"}
        r = snippets.run_shell('DIR=' + os.path.join(tree, "a") + '; mkdir -p "$DIR"', tree, {}, state)
        assert state["vars"]["DIR"] == os.path.join(tree, "a") and not r["failed"]
        r = snippets.run_shell('ls "$DIR/b"', tree, {}, state)
        assert r["lines"][0]["ran"] and "x.txt" in r["lines"][0]["tail"]
        r = snippets.run_shell('ls "$OTHER"', tree, {}, state)
        assert r["lines"][0]["ran"] is False and "OTHER" in r["lines"][0]["reason"]
