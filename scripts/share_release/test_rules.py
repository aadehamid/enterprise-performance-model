"""Each rewrite rule, on a planted line, by hand."""
import pytest
import os

os.environ["EPM_RELEASE_OWNER_NAMES"] = "Ada Lovelace,Ada,adalove"  # a stand-in: no test names a person
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manifest  # noqa: E402
import rules  # noqa: E402

DATES = {"EPM-DEC-001-0038": "2026-10-13", "EPM-DEC-001-0044": "2026-10-18", "EPM-DEC-001-0102": "2026-10-25"}


def run(text, path="doc.md"):
    return rules.apply(text, path, DATES)


def test_iri_base_becomes_mpc():
    out, counts = run("<https://w3id.org/lsc/ontology/modules/core/Process> and `w3id.org/lsc`; r\"w3id\\.org/lsc\"; sh:pattern \"^https://w3id\\\\.org/lsc/ontology/process/\"")
    assert out == "<https://w3id.org/mpc/ontology/modules/core/Process> and `w3id.org/mpc`; r\"w3id\\.org/mpc\"; sh:pattern \"^https://w3id\\\\.org/mpc/ontology/process/\""
    assert counts["iri"] == 4


def test_company_name_and_lsc_become_mpc():
    out, _ = run('dcterms:title "LSC KPI Module 1.3.0"@en ; "SKOS taxonomy of Lagos Specialty Chemicals\' processes"')
    assert out == 'dcterms:title "MPC KPI Module 1.3.0"@en ; "SKOS taxonomy of MPC\'s processes"'


def test_rights_line_loses_its_owner_and_record():
    out, _ = run('dcterms:rights "© LSC. All rights reserved. Proprietary (EPM-DEC-001-0041). This work is based"')
    assert out == 'dcterms:rights "All rights reserved. Proprietary. This work is based"'


def test_record_citations_become_dates():
    out, _ = run("approved under EPM-DEC-001-0044 (EPM-DEC-001-0102, amendment of 2026-10-28); see [EPM-DEC-001-0038](EPM-DEC-001-0038-x.md).")
    assert out == "approved under the decision of 2026-10-18 (the decision of 2026-10-25, amendment of 2026-10-28); see the decision of 2026-10-13."


def test_turtle_citation_names_the_sme_and_date():
    out, _ = run('dcterms:bibliographicCitation "EPM-DEC-001-0038; the decision owner\'s words in step4/review-evidence/decision-owner-answers/answers-2026-10-13-session2.md"@en ;')
    assert out == 'dcterms:bibliographicCitation "decided on 2026-10-13 by a subject matter expert reviewing the documents"@en ;'


def test_html_record_link_becomes_text():
    out, _ = run('see <a href="../domain/decisions/decisions.html#EPM-DEC-001-0044">EPM-DEC-001-0044</a>.', "page.html")
    assert out == "see the decision of 2026-10-18."


def test_series_name_and_unknown_record():
    out, _ = run("the EPM-DEC-001 records; EPM-DEC-001-9999 is unknown")
    assert out == "the decision records; the decision of an earlier date is unknown"


def test_answers_folder_citations():
    out, _ = run("recorded in `answers-2026-10-25-queue-delegation.md`, blocks 2 and 3; see step4/review-evidence/decision-owner-answers/")
    assert "answers-2026" not in out and "decision-owner-answers" not in out
    assert "a subject matter expert" in out


def test_answers_source_iris_are_renamed():
    out, _ = run("dcterms:source src:decision-owner-answers-2026-10-27-systems ; <https://w3id.org/lsc/ontology/source/decision-owner-answers-2026-10-27-item-g>; csv cell decision-owner-answers-2026-10-24-systems")
    assert out == "dcterms:source src:sme-review-2026-10-27-systems ; <https://w3id.org/mpc/ontology/source/sme-review-2026-10-27-item-g>; csv cell sme-review-2026-10-24-systems"


def test_attribution_of_quotes():
    out, _ = run('The decision owner said "yes" (the decision owner, 2026-09-19); the decision owner\'s words: "go".')
    assert out == 'a subject matter expert reviewing the documents said "yes" (a subject matter expert reviewing the documents, 2026-09-19); the words of a subject matter expert reviewing the documents: "go".'


def test_decision_owner_term_itself_stays():
    out, _ = run("The decision owner convenes the business leads; the decision owner is a subject matter expert.")
    assert out == "The decision owner convenes the business leads; the decision owner is a subject matter expert."


def test_approval_line():
    out, _ = run('"who": "Claude, under the decision owner\'s delegation (EPM-DEC-001-0028, amendment of 2026-10-25, evening)"')
    assert out == '"who": "a subject matter expert reviewing the documents"'


def test_an_agent_is_not_named_in_a_note_and_a_draft_keeps_its_word():
    out, _ = run('skos:editorialNote "Drafted by Claude from the repository; the definition is Claude\'s words (EPM-DEC-001-0044)."@en')
    assert out == 'skos:editorialNote "Drafted from the repository; the definition is written for this ontology (the decision of 2026-10-18)."@en'


def test_hosts_and_links():
    out, _ = run("run on the exe.dev VM, `databases.exe.xyz`; the [walkthrough](https://spacesheep.dev/space/abc) and https://app.eraser.io/workspace/XYZ")
    assert out == "run on a remote host, `source-postgres-host`; the walkthrough and a link not included in this release"


def test_walkthrough_rows_for_the_review_loop_are_dropped():
    out, _ = run("<table><tr><td>a</td></tr>\n<tr><td><code>~/.claude/handoffs/x/brief.md</code></td><td>The brief</td></tr>\n<tr><td>b</td></tr></table>", "epm-walkthrough.html")
    assert out == "<table><tr><td>a</td></tr>\n<tr><td>b</td></tr></table>"


def test_repository_names_and_home_paths():
    out, _ = run("clone https://github.com/adalove/enterprise-performance-model.git; `~/workspace/ontology-build`; $HOME/Dropbox/1_PROJECTS/Enterprise Performance Model; ~/.agents/skills/ontology-to-lpg")
    assert out == "clone this repository; `build/work`; $EPM; skills/ontology-to-lpg"


def test_public_github_links_stay():
    out, _ = run("[ROBOT](https://github.com/ontodev/robot/releases/tag/v1.9.10)")
    assert out == "[ROBOT](https://github.com/ontodev/robot/releases/tag/v1.9.10)"


def test_issue_and_pr_numbers():
    out, _ = run("fixed in PR #231 (#454); issue #457 is open; see #226 comment 613; the #226 pairs table")
    assert out == "fixed in an earlier change; an earlier change is open; see an earlier comment; the earlier change pairs table"
    out, _ = run("the five PRs (#108–#115) and #430-#448")
    assert out == "the five changes (earlier items) and earlier items"


def test_numbers_in_a_page_are_prose_not_colours():
    out, _ = run('<p>#455 holds the work; issues #430 to #448 are open.</p><td data-k="Issue">#455</td><style>a{color:#455;background:#fff}</style>', "guide.html")
    assert out == '<p>an earlier change holds the work; earlier items are open.</p><td data-k="Issue">an earlier change</td><style>a{color:#455;background:#fff}</style>'


def test_numbers_rule_leaves_code_and_css_alone():
    out, _ = run("h = hashlib.sha256()\ndef commit():\n    return x[:8]", "a.py")
    assert out == "h = hashlib.sha256()\ndef commit():\n    return x[:8]"
    out, _ = run("body{background:#fff;color:#000} a{color:#1a2b3c}", "p.html")
    assert out == "body{background:#fff;color:#000} a{color:#1a2b3c}"


def test_peer_names_and_lists():
    out, _ = run("against the same regions of Phillips 66 and Valero Energy; Chevron, Exxon Mobil, HF Sinclair and PBF Energy report it; Valero's target")
    assert out == "against the same regions of U.S. refining peers; U.S. refining peers report it; a U.S. refining peer's target"


def test_peer_links_are_withheld_and_a_name_split_across_lines_is_found():
    out, _ = run("| https://www.sec.gov/Archives/edgar/data/1534504/000153450426000010/pbf-20251231.htm | 2026-10-20 |\n\"url\": \"https://www.qcintel.com/article/delek-starts-maintenance\"\npeers (Par\nPacific) is here")
    assert out == "| a public filing of a U.S. refining peer (link withheld) | 2026-10-20 |\n\"url\": \"a public source naming a U.S. refining peer (link withheld)\"\npeers (a U.S. refining peer) is here"
    out, _ = run("[the 10-K](https://www.sec.gov/Archives/edgar/data/1510295/mpc-20251231.htm)")
    assert out == "[the 10-K](https://www.sec.gov/Archives/edgar/data/1510295/mpc-20251231.htm)"


def test_peer_source_wording_and_folder():
    out, _ = run("U.S. refining peers' SEC filings, as read into business_architecture/reference/downstream-peers/.")
    assert out == "Industry standard, and analysis of publicly available filings from peers (U.S. refiners), as read into business_architecture/reference/industry-view/."


def test_single_underscores():
    out, _ = run("MATCH (c:skos__Concept)-[:skos__broader]->(b) RETURN c.skos__prefLabel; `lib__Work`; __init__.py; __main__")
    assert out == "MATCH (c:skos_Concept)-[:skos_broader]->(b) RETURN c.skos_prefLabel; `lib_Work`; __init__.py; __main__"


def test_code_keeps_its_separators_for_the_rename_step():
    out, _ = run('probe = s.run("MATCH (r:org__Role) RETURN r.skos__prefLabel")', "pipeline.py")
    assert out == 'probe = s.run("MATCH (r:org__Role) RETURN r.skos__prefLabel")'


def test_third_party_syntax_with_two_underscores_is_not_a_graph_name():
    out, _ = run("mf query --group-by ticket_terminal,metric_time__day")
    assert out == "mf query --group-by ticket_terminal,metric_time__day"


def test_a_peer_brand_inside_a_quoted_filing():
    out, _ = run("licensing fees for the use of the Sinclair brand")
    assert out == "licensing fees for the use of its brand"


def test_the_playbook_builder_names_the_release_layout():
    out, _ = run('"out": "skills/data/ontology/references/ontology-build-playbook.html", "sources": ["skills/data/ontology/references/playbook.md"]', "skills/scripts/build_playbook_html.py")
    assert out == '"out": "ontology/references/ontology-build-playbook.html", "sources": ["ontology/references/playbook.md"]'
    out, _ = run("see skills/data/ontology/SKILL.md", "skills/ontology/README.md")
    assert out == "see skills/data/ontology/SKILL.md"


def test_owner_name_in_skills():
    out, _ = run("Ada Lovelace's guideline, by Ada (adalove)")
    assert out == "the author's guideline, by the author (the author)"


def test_manifest_ships_the_two_versions_and_leaves_older_ones_out():
    r = manifest.EPM_RULES
    assert manifest.disposition("business_architecture/ontology/releases/core/2.4.0/core.ttl", r) == "ship"
    assert manifest.disposition("business_architecture/ontology/releases/core/2.3.0/core.ttl", r) == "ship"
    assert manifest.disposition("business_architecture/ontology/releases/core/2.2.0/core.ttl", r) == "out"
    assert manifest.disposition("business_architecture/ontology/step4/review-evidence/decision-owner-answers/a.md", r) == "out"
    assert manifest.disposition("business_architecture/ontology/step4/baseline/step3-taxonomy.ttl", r) == "ship"
    assert manifest.disposition("business_architecture/ontology/step4/target-report/test_context_pass.py", r) == "out"
    assert manifest.disposition("business_architecture/ontology/step4/label-report/label-dispositions-v1.2.csv", r) == "ship"
    assert manifest.disposition("business_architecture/domain/decisions/EPM-DEC-001-0001-x.md", r) == "out"
    assert manifest.disposition("business_architecture/domain/decision-packages/2026-10-14/README.md", r) == "ship"
    assert manifest.disposition("business_architecture/domain/decision-packages/2026-10-14/pr-reviews-262-266-269.md", r) == "out"
    assert manifest.disposition("business_architecture/ontology/step4/playbook/ontology-worklog.md", r) == "out"
    assert manifest.disposition("business_architecture/ontology/README.html", r) == "out"
    assert manifest.disposition("scripts/docs_template.html", r) == "ship"
    assert manifest.disposition("business_architecture/ontology/epm-walkthrough.html", r) == "ship"
    assert manifest.disposition("AGENTS.md", r) == "out"
    assert manifest.disposition("demos/downstream-pricing-databricks-free/pricing_demo/genie.py", r) == "ship"
    assert manifest.disposition("demos/o2c-unbilled-semantic-layer/README.md", r) == "out"
    assert manifest.disposition("demos/README.md", r) == "out"
    assert manifest.disposition("architecture/EPM-ARCH-MEANING-vs-COMPUTE.jpg", r) == "out"
    assert manifest.disposition("EPM_Homelab/00-x.md", r) == "out"


def test_release_paths():
    assert manifest.release_path("business_architecture/reference/downstream-peers/a.md", "epm") == "business_architecture/reference/industry-view/a.md"
    assert manifest.release_path("business_architecture/ontology/releases/core/2.3.0/core.ttl", "epm") == "business_architecture/ontology/releases/previous/core/2.3.0/core.ttl"
    assert manifest.release_path("skills/data/ontology/SKILL.md", "skills") == "skills/ontology/SKILL.md"
    assert manifest.release_path("scripts/build_playbook_html.py", "skills") == "skills/scripts/build_playbook_html.py"
    assert manifest.disposition("skills/writing/clear-writing/calibration.md", manifest.SKILLS_RULES) == "out"
    assert manifest.disposition("skills/engineering/way-of-working/SKILL.md", manifest.SKILLS_RULES) == "out"


def test_a_peer_phrase_that_starts_a_sentence_is_capitalised():
    out, _ = rules.apply("Valero reported a margin. Then Valero said more.\n- Valero also did.\n### 3. Risk: Valero shows it\nShell, Chevron and BP cut.", "x.md")
    assert out == ("A U.S. refining peer reported a margin. Then a U.S. refining peer said more.\n- A U.S. refining peer also did.\n"
                   "### 3. Risk: A U.S. refining peer shows it\nShell, a U.S. refining peer and BP cut.")


def test_rows_and_sentences_that_point_at_left_out_documents():
    out, _ = rules.apply("| `README.md` | here |\n| `LOCAL-STORES.md` | the stores |\n| `STORE-INVENTORY.md` | what |\n| `x.md` | y |\n", "a/README.md")
    assert out == "| `README.md` | here |\n| `x.md` | y |\n"
    out, _ = rules.apply("following the guideline in `../lpg-projection/` (v2.2) with Rule 4a, and `../lpg-projection/` keeps the v2.2 copy as superseded evidence; this stays", "a.md")
    assert out == "following the projection guideline, version 2.2, with Rule 4a (the v2.2 copy is not part of this release); this stays"


def test_the_two_store_notes_stay_out():
    r = manifest.EPM_RULES
    assert manifest.disposition("business_architecture/ontology/projection/LOCAL-STORES.md", r) == "out"
    assert manifest.disposition("business_architecture/ontology/projection/STORE-INVENTORY.md", r) == "out"
    assert manifest.disposition("business_architecture/ontology/projection/README.md", r) == "ship"


def test_the_guide_tests_record_term_follows_its_fixture():
    src = '    ("a project decision record", r"EPM-DEC|\\bEPM\\b"),\n    ("see EPM-DEC-001-0001", "a project decision record"),\n'
    out, _ = rules.apply(src, "skills/ontology/scripts/test_playbook_guide.py", {"EPM-DEC-001-0001": "2026-10-05"})
    assert '("a project decision record", r"the decision of \\d{4}-\\d{2}-\\d{2}|\\bEPM\\b")' in out
    assert '("see the decision of 2026-10-05", "a project decision record")' in out


def test_the_earlier_core_builders_commands_become_notes():
    src = "# from business_architecture/ontology/release\nuv run --with rdflib python build_core_next.py --verify\nuv run --with rdflib python build_core_2_4.py --verify\n"
    out, _ = rules.apply(src, "business_architecture/ontology/epm-walkthrough.html")
    assert out == ("# from business_architecture/ontology/release\n# run when that release was cut; its inputs are not in this release "
                   "(the newest builder is build_core_2_4.py): uv run --with rdflib python build_core_next.py --verify\n"
                   "uv run --with rdflib python build_core_2_4.py --verify\n")


def test_the_skills_layout_rule_covers_path_join_tuples():
    out, _ = rules.apply('sys.path.insert(0, os.path.join(HERE, "..", "skills", "data", "ontology", "scripts"))\n', "skills/scripts/test_playbook_html.py")
    assert out == 'sys.path.insert(0, os.path.join(HERE, "..", "ontology", "scripts"))\n'


def test_the_owners_names_come_from_the_configuration_and_become_the_author():
    out, _ = run("Ada Lovelace's note; by Ada Lovelace; Ada asked; handle adalove; Adam stays")
    assert out == "the author's note; by the author; the author asked; handle the author; Adam stays"


def test_the_pages_mentions_of_the_store_notes_go():
    src = ('<tr><td><code>business_architecture/ontology/projection/LOCAL-STORES.html</code></td><td>x</td></tr>\n'
           '<tr><td><code>a.html</code></td><td>y</td></tr>\nFigures from <code>LOCAL-STORES.md</code>, <code>MODULES.md</code>; '
           'Ports and names from <code>LOCAL-STORES.md</code>; comes from <code>business_architecture/ontology/projection/LOCAL-STORES.md</code> and the demo; '
           'Start with <code>projection/README.md</code>, <code>LOCAL-STORES.md</code>, then <code>pipeline.py</code>')
    out, _ = rules.apply(src, "business_architecture/ontology/epm-walkthrough.html")
    assert out == ('<tr><td><code>a.html</code></td><td>y</td></tr>\nFigures from <code>MODULES.md</code>; '
                   'Ports and names from the stores runbook; comes from the stores runbook and the demo; '
                   'Start with <code>projection/README.md</code>, then <code>pipeline.py</code>')


def test_another_repository_of_the_account_and_its_issue_numbers():
    out, _ = run("the enterprise-people-graph folder points to it (enterprise-people-graph\n  #4); re-pinned (enterprise-people-graph PR #3); in enterprise-people-graph")
    assert out == "the other repository folder points to it (another repository); re-pinned (another repository); in another repository"
    assert "enterprise-people-graph" not in out


def test_peer_tickers_in_news_titles_and_evidence_tables():
    out, _ = run("Oil Above $90 Puts PSX, VLO and MPC in Focus; Valero (VLO) | Phillips 66 (PSX) | HF Sinclair (DINO); PSX uses crude capacity; XOM/CVX report; (DK) too; DK, VLO")
    assert out == ("Oil Above $90 Puts U.S. refining peers and MPC in Focus; a U.S. refining peer | a U.S. refining peer | a U.S. refining peer; "
                   "a U.S. refining peer uses crude capacity; U.S. refining peers report; (a U.S. refining peer) too; U.S. refining peers")
    out, _ = run("the DK stays, so does psx in lower case and a DINOSAUR")  # DK alone, lower case and a longer word are not tickers
    assert out == "the DK stays, so does psx in lower case and a DINOSAUR"


def test_peer_filings_on_edgar_are_withheld_and_own_and_industry_filings_stay():
    out, _ = run("https://www.sec.gov/Archives/edgar/data/1534504/000153450426000010/pbf-20251231.htm and https://www.sec.gov/Archives/edgar/data/999/000/vlo-20251231.htm")
    assert out == "a public filing of a U.S. refining peer (link withheld) and a public filing of a U.S. refining peer (link withheld)"
    kept = ("https://www.sec.gov/Archives/edgar/data/1510295/000151029526000010/mpc-20251231.htm | "
            "https://www.sec.gov/Archives/edgar/data/1552000/000155200026000009/mplx-20251231.htm | "
            "https://www.sec.gov/Archives/edgar/data/67646/000119312503054119/dex991.htm")
    out, _ = run(kept)
    assert out == kept


def test_short_record_numbers_after_a_citation():
    dates = {**DATES, "EPM-DEC-001-0020": "2026-10-06", "EPM-DEC-001-0021": "2026-10-07", "EPM-DEC-001-0036": "2026-10-12", "EPM-DEC-001-0040": "2026-10-14", "EPM-DEC-001-0043": "2026-10-16"}
    out, _ = rules.apply("see EPM-DEC-001-0020, 0021 and 0036; EPM-DEC-001-0040 to 0043; (EPM-DEC-001-0038, amending 0021); the guideline (0021); EPM-DEC-001-0044, 0999", "a.md", dates)
    assert out == ("see the decision of 2026-10-06, the decision of 2026-10-07 and the decision of 2026-10-12; the decisions of 2026-10-14 to 2026-10-16; "
                   "(the decision of 2026-10-13, amending the decision of 2026-10-07); the guideline (the decision of 2026-10-07); the decision of 2026-10-18, 0999")
    out, _ = rules.apply("Catalogue record 0042, field 700; W-0042; (0042) is unknown here", "a.md", dates)
    assert out == "Catalogue record 0042, field 700; W-0042; (0042) is unknown here"  # a number that is not a known record stays


def test_css_colours_after_a_colon_with_a_space_stay():
    out, _ = run("<style>  :root { --bg: #fff; --text: #111; --muted: #555; } body { color: #111; }</style> <p>#455 holds the work</p>", "page.html")
    assert out == "<style>  :root { --bg: #fff; --text: #111; --muted: #555; } body { color: #111; }</style> <p>an earlier change holds the work</p>"


def test_references_to_the_left_out_documents_in_prose_code_and_pages():
    out, _ = run("Logins come from the files LOCAL-STORES.md names; none is printed.\nNEO4J_STORES = {  # LOCAL-STORES.md; the driver", "sync_stores.py")
    assert out == "Logins come from the files the stores runbook names; none is printed.\nNEO4J_STORES = {  # the stores runbook; the driver"
    out, _ = run('<figcaption>Counts from <code>business_architecture/ontology/projection/STORE-INVENTORY.md</code>, 2026-10-29.</figcaption>', "walk.html")
    assert out == "<figcaption>Counts from the store inventory of the original build (not in this release), 2026-10-29.</figcaption>"
    out, _ = run("| `lpg-projection/` | The superseded v2.2 copy |\n| `projection/` | The projection |\n", "business_architecture/ontology/README.md")
    assert out == "| `projection/` | The projection |\n"
    out, _ = run('"guideline": "v2.2 (lpg-projection/, pin 8ce9ada)"', "business_architecture/ontology/projection/projection-manifest.json")
    assert out == '"guideline": "v2.2 (the projection guideline, pin 8ce9ada)"'
    out, _ = run("Follows the guideline in ../lpg-projection/ (v2.2) with Rule 4 set to 4a", "business_architecture/ontology/projection/pipeline.py")
    assert out == "Follows the projection guideline, version 2.2, with Rule 4 set to 4a"
    src = ('        single(f"{ONT}/projection/README.md",\n               "How the released packages are projected."),\n'
           '        single(f"{ONT}/projection/LOCAL-STORES.md",\n               "Where each store lives."),\n'
           '        single(f"{ONT}/projection/STORE-INVENTORY.md",\n               "What each store holds now."),\n'
           '        single(f"{ONT}/projection/skill-run/README.md",\n               "How the driver runs."),\n')
    out, _ = run(src, "scripts/build_docs_html.py")
    assert out == ('        single(f"{ONT}/projection/README.md",\n               "How the released packages are projected."),\n'
                   '        single(f"{ONT}/projection/skill-run/README.md",\n               "How the driver runs."),\n')
    out, _ = run("read `references/lpg-projection.md`; the container lpg-projection on 17687; urn:lpg-projection:graph:; r\"lpg-projection/|ontology-worklog\"", "skills/ontology/scripts/test_playbook_guide.py")
    assert 'r"lpg-projection/"' in out and "ontology-worklog" not in out and "references/lpg-projection.md" in out  # the skills' own names stay


def test_a_documents_path_to_a_previous_package_moves_to_the_history_folder():
    out, _ = run("released as 1.2.0 (`../releases/kpi/1.2.0/`) then 1.3.0 (`../releases/kpi/1.3.0/`); cd business_architecture/ontology/releases/kpi/1.2.0 && shasum", "business_architecture/ontology/kpi/README.md")
    assert out == "released as 1.2.0 (`../releases/previous/kpi/1.2.0/`) then 1.3.0 (`../releases/kpi/1.3.0/`); cd business_architecture/ontology/releases/previous/kpi/1.2.0 && shasum"
    out, _ = run("<https://w3id.org/mpc/ontology/modules/kpi/releases/1.2.0/kpi.ttl>; releases/previous/kpi/1.2.0/kpi.ttl", "a.ttl")
    assert out == "<https://w3id.org/mpc/ontology/modules/kpi/releases/1.2.0/kpi.ttl>; releases/previous/kpi/1.2.0/kpi.ttl"
    out, _ = run('"shapes": ["releases/party/2.0.0/shapes.ttl"]', "business_architecture/ontology/release/build_module.py")
    assert out == '"shapes": ["releases/party/2.0.0/shapes.ttl"]'  # code resolves the path itself
    out, _ = run("see releases/kpi/1.2.0/kpi.ttl", "business_architecture/ontology/releases/previous/kpi/1.2.0/CHANGELOG.md")
    assert out == "see releases/kpi/1.2.0/kpi.ttl"  # the history folder is left as cut


def test_dk_beside_mpc_or_mplx_is_a_ticker_and_the_two_stay():
    out, _ = run("see DK and MPC report; MPLX/DK; MPC, DK and VLO; the DK stays; MPC and MPLX")
    assert out == "see a U.S. refining peer and MPC report; MPLX/a U.S. refining peer; MPC, U.S. refining peers; the DK stays; MPC and MPLX"


def test_a_zero_padded_cik_is_the_same_filer():
    out, _ = run("https://www.sec.gov/Archives/edgar/data/0001035002/000162828026011499/a10k.htm and https://www.sec.gov/Archives/edgar/data/0001510295/000151029526000010/mpc-20251231.htm")
    assert out == "a public filing of a U.S. refining peer (link withheld) and https://www.sec.gov/Archives/edgar/data/0001510295/000151029526000010/mpc-20251231.htm"


def test_in_a_page_a_number_after_a_colon_is_a_colour_only_inside_css():
    out, _ = run('<p>Issue: #455 remains open</p><style>a{color: #455}</style><div style="color: #111">#222 is open</div>', "p.html")
    assert out == '<p>Issue: an earlier change remains open</p><style>a{color: #455}</style><div style="color: #111">an earlier change is open</div>'
    out, _ = run("--text: #111; a: #222", "p.css")
    assert out == "--text: #111; a: #222"


@pytest.mark.parametrize("before,after", [
    ("Drafted by Claude from the subject matter expert's customer inputs", "Drafted from the subject matter expert's customer inputs"),
    ("the definition is Claude's words (the decision of 2026-10-23).", "the definition is written for this ontology (the decision of 2026-10-23)."),
    ("each defined from the inputs in Claude's words.", "each defined from the inputs in the ontology's own words."),
    ("Claude's design under the decision of 2026-10-12", "the subject matter expert's decision of 2026-10-12"),
    ("Approved by Claude under the delegation, which lets it approve the queue's minor releases (\"Yes, delegate as described (Recommended)\", saved in (the file)).",
     "Approved by a subject matter expert."),
    ("1.1.0, a minor Claude approved under the delegation, is in", "1.1.0, a minor release a subject matter expert approved, is in"),
    ("Under the delegation (the decision of 2026-10-18), four roles stay", "By the decision of 2026-10-18, four roles stay"),
    ("the scope note is Claude's, under the delegation (the decision of 2026-10-18, MPC-P07).", "the scope note follows the decision of 2026-10-18, MPC-P07."),
    ("x = 1  # bounded (Kimi round 1, finding 11)", "x = 1  # bounded"),
    ("    # Codex on step 2: a long text grows.", "    # a long text grows."),
    ("    # Cursor's HOLD on an earlier change: a named record.", "    # a named record."),
    ("It runs twice (finding 5).", "It runs twice."),
    ("**Built with:** Kailey and Claude Code.\n**Started:** now", "**Started:** now"),
    ("the process-map question set (Kailey, 2026-09-17)", "the process-map question set (a subject matter expert, 2026-09-17)"),
    ("See AGENTS.md first", "See the project's instructions first"),
    ("is a follow-up noted in the batch 08 PR.", "is a follow-up noted in batch 08 of the process-map work."),
])
def test_agents_rewrites_names_and_work(before, after):
    assert rules.rule_agents(before, {"path": "x.py"})[0] == after


@pytest.mark.parametrize("kept", [
    "The delegation of authority is set by Market Risk Management.",  # a business term
    "within the documented delegation of claim-settlement authority",
    "cur = conn.cursor()",  # a database cursor
    "class Cursor:\n    pass",
    "td { cursor: pointer; }",
    "a prov:Agent and a prov:SoftwareAgent",
    "the four Genie agents and the supervisor",
    "It waits for its owners to confirm it.",  # a draft keeps its status
    "public relations (PR) strategy",
])
def test_agents_leaves_what_is_not_the_build(kept):
    assert rules.rule_agents(kept, {"path": "x.py"})[0] == kept


def test_agents_keeps_a_tuple_of_strings_in_code():
    src = 'for subject in ("the reviewer", "Kimi"):'
    assert "(" in rules.rule_agents(src, {"path": "x.py"})[0].split("in ")[1]


def test_agents_removes_a_page_row_about_the_builds_tooling():
    src = "<tr><td><code>AGENTS.md</code></td><td>x</td></tr>\n<tr><td>keep</td></tr>\n"
    assert rules.rule_agents(src, {"path": "a.html"})[0] == "<tr><td>keep</td></tr>\n"


def test_agents_leaves_the_skills_own_pull_requests():
    src = "through a pull request"
    assert rules.rule_agents(src, {"path": "skills/ontology/references/release.md"})[0] == src
    assert rules.rule_agents(src, {"path": "README.md"})[0] == "through a change"


def test_the_demos_remote_machine_and_tunnel_are_reworded():
    src = "Postgres, one database per source system (the exe.dev VM through an SSH tunnel; the local Docker container is the fallback)"
    assert run(src, "demos/downstream-pricing-databricks-free/README.md")[0] == "Postgres, one database per source system (the local Docker container; `SOURCE_PG_DSN` names another host)"
    assert run("then from the exe.dev VM through the tunnel", "demos/downstream-pricing-databricks-free/README.md")[0] == "then from a remote host"
    assert "through an SSH tunnel" in run("reached through an SSH tunnel", "other.md")[0]  # only the demo's README


def test_the_demos_tunnel_instructions_go():
    src = ("change `SOURCE_PG_DSN`; nothing else names the host. Since 2026-10-28 the source databases (seven, with `x`) also run on an exe.dev VM, "
           "`databases.exe.xyz`, where Postgres listens only on the VM's localhost. Open a tunnel, `ssh -N -L 1:2 databases.exe.xyz`. The local container stays as the fallback.")
    assert run(src, "demos/downstream-pricing-databricks-free/README.md")[0] == "change `SOURCE_PG_DSN`; nothing else names the host."
