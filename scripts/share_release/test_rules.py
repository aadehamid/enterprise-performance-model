"""Each rewrite rule, on a planted line, by hand."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manifest  # noqa: E402
import rules  # noqa: E402

DATES = {"EPM-DEC-001-0038": "2026-10-13", "EPM-DEC-001-0044": "2026-10-18", "EPM-DEC-001-0102": "2026-10-25"}


def run(text, path="doc.md"):
    return rules.apply(text, path, DATES)


def test_iri_base_becomes_mpc():
    out, counts = run("<https://w3id.org/lsc/ontology/modules/core/Process> and `w3id.org/lsc`")
    assert out == "<https://w3id.org/mpc/ontology/modules/core/Process> and `w3id.org/mpc`"
    assert counts["iri"] == 2


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
    out, _ = run("dcterms:source src:decision-owner-answers-2026-10-27-systems ; <https://w3id.org/lsc/ontology/source/decision-owner-answers-2026-10-27-item-g>")
    assert out == "dcterms:source src:sme-review-2026-10-27-systems ; <https://w3id.org/mpc/ontology/source/sme-review-2026-10-27-item-g>"


def test_attribution_of_quotes():
    out, _ = run('The decision owner said "yes" (the decision owner, 2026-09-19); the decision owner\'s words: "go".')
    assert out == 'a subject matter expert reviewing the documents said "yes" (a subject matter expert reviewing the documents, 2026-09-19); the words of a subject matter expert reviewing the documents: "go".'


def test_decision_owner_term_itself_stays():
    out, _ = run("The decision owner convenes the business leads; the decision owner is a subject matter expert.")
    assert out == "The decision owner convenes the business leads; the decision owner is a subject matter expert."


def test_approval_line():
    out, _ = run('"who": "Claude, under the decision owner\'s delegation (EPM-DEC-001-0028, amendment of 2026-10-25, evening)"')
    assert out == '"who": "a subject matter expert reviewing the documents"'


def test_tool_names_stay_where_they_name_the_tool():
    out, _ = run('skos:editorialNote "Drafted by Claude from the repository; the definition is Claude\'s words (EPM-DEC-001-0044)."@en')
    assert out == 'skos:editorialNote "Drafted by Claude from the repository; the definition is Claude\'s words (the decision of 2026-10-18)."@en'


def test_hosts_and_links():
    out, _ = run("run on the exe.dev VM, `databases.exe.xyz`; the [walkthrough](https://spacesheep.dev/space/abc) and https://app.eraser.io/workspace/XYZ")
    assert out == "run on a remote host, `source-postgres-host`; the walkthrough and a link not included in this release"


def test_walkthrough_rows_for_the_review_loop_are_dropped():
    out, _ = run("<table><tr><td>a</td></tr>\n<tr><td><code>~/.claude/handoffs/x/brief.md</code></td><td>The brief</td></tr>\n<tr><td>b</td></tr></table>", "epm-walkthrough.html")
    assert out == "<table><tr><td>a</td></tr>\n<tr><td>b</td></tr></table>"


def test_repository_names_and_home_paths():
    out, _ = run("clone https://github.com/aadehamid/enterprise-performance-model.git; `~/workspace/ontology-build`; $HOME/Dropbox/1_PROJECTS/Enterprise Performance Model; ~/.agents/skills/ontology-to-lpg")
    assert out == "clone this repository; `build/work`; $EPM; skills/ontology-to-lpg"


def test_public_github_links_stay():
    out, _ = run("[ROBOT](https://github.com/ontodev/robot/releases/tag/v1.9.10)")
    assert out == "[ROBOT](https://github.com/ontodev/robot/releases/tag/v1.9.10)"


def test_issue_and_pr_numbers():
    out, _ = run("fixed in PR #231 (#454); issue #457 is open; see #226 comment 613; the #226 pairs table")
    assert out == "fixed in an earlier change; an earlier change is open; see an earlier comment; the earlier change pairs table"


def test_numbers_rule_leaves_code_and_css_alone():
    out, _ = run("h = hashlib.sha256()\ndef commit():\n    return x[:8]", "a.py")
    assert out == "h = hashlib.sha256()\ndef commit():\n    return x[:8]"
    out, _ = run("body{background:#fff;color:#000} a{color:#1a2b3c}", "p.html")
    assert out == "body{background:#fff;color:#000} a{color:#1a2b3c}"


def test_peer_names_and_lists():
    out, _ = run("against the same regions of Phillips 66 and Valero Energy; Chevron, Exxon Mobil, HF Sinclair and PBF Energy report it; Valero's target")
    assert out == "against the same regions of U.S. refining peers; U.S. refining peers report it; a U.S. refining peer's target"


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


def test_owner_name_in_skills():
    out, _ = run("Ha" + "mid Ade" + "sokan's guideline, by Ha" + "mid (aade" + "ha" + "mid)")
    assert out == "the author's guideline, by the author (the author)"


def test_manifest_ships_the_two_versions_and_leaves_older_ones_out():
    r = manifest.EPM_RULES
    assert manifest.disposition("business_architecture/ontology/releases/core/2.4.0/core.ttl", r) == "ship"
    assert manifest.disposition("business_architecture/ontology/releases/core/2.3.0/core.ttl", r) == "ship"
    assert manifest.disposition("business_architecture/ontology/releases/core/2.2.0/core.ttl", r) == "out"
    assert manifest.disposition("business_architecture/ontology/step4/review-evidence/decision-owner-answers/a.md", r) == "out"
    assert manifest.disposition("business_architecture/ontology/step4/baseline/step3-taxonomy.ttl", r) == "ship"
    assert manifest.disposition("business_architecture/domain/decisions/EPM-DEC-001-0001-x.md", r) == "out"
    assert manifest.disposition("business_architecture/domain/decision-packages/2026-10-14/README.md", r) == "ship"
    assert manifest.disposition("business_architecture/ontology/README.html", r) == "out"
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
