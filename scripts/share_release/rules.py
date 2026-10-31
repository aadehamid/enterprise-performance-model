"""The rewrite rules of the share release (EPM-DEC-001-0110 and its amendment).

Each rule is a function from text to text, named, and applied in order to every text file the release
ships. `apply(text, path, record_dates)` returns the rewritten text and a count per rule, so the export
report can say which rule explains each difference between main and the release.

The rules, in order:
  1. iri:          w3id.org/lsc -> w3id.org/mpc (the IRI base; LSC becomes MPC in the release only).
  2. company:      the company's name behind LSC -> MPC; LSC as a word -> MPC; the rights line loses its owner.
  3. records:      every EPM-DEC-001-NNNN citation -> "the decision of <date>"; the series name -> "the decision records".
  4. answers:      every citation of the answers folder -> a subject matter expert's review comments.
  5. attribution:  words attributed to the decision owner -> attributed to a subject matter expert reviewing the documents.
  6. approvals:    "Claude, under the decision owner's delegation ..." -> the same attribution.
  7. hosts:        exe.dev and its host name -> a remote host; links to the published page and Eraser removed.
  8. repository:   this account's repositories and handle -> plain words; home-folder paths -> release paths.
  9. numbers:      issue and pull request numbers -> plain words.
 10. peers:        the nine company names -> U.S. refining peers; the peer evidence folder -> industry view;
                   the peer-tier wording -> the agreed source wording.
 11. underscores:  prefix__name -> prefix_name for the graph's prefixes, outside Python's own names.
 12. names:        the owner's name and handle in the skills -> the author.
"""
import re

# Rule 11's prefixes: the projection's fixed prefixes plus n10s's schema and SHACL prefixes.
GRAPH_PREFIXES = ("core", "orgm", "kpi", "pop", "party", "dp", "vs", "sys", "lane", "mkt", "plc", "auth", "con",
                  "skos", "dcterms", "org", "rdfs", "owl", "rdf", "prov", "oeo", "n4sch", "sh", "tv", "tech")
PEER_NAMES = [r"Valero Energy Corporation", r"Valero Energy", r"Valero", r"Phillips ?66", r"PBF Energy", r"PBF",
              r"HF ?Sinclair", r"HollyFrontier", r"Par\s+Pacific", r"Delek US", r"Delek", r"CVR Energy", r"CVR",
              r"Chevron Corporation", r"Chevron", r"Exxon ?Mobil", r"ExxonMobil", r"Exxon"]
# A link whose address names a peer (a filing on EDGAR, a news slug, an investor site) is withheld with the name.
PEER_URL = re.compile(r"https?://[^\s)\]\"'<>]*(?:pbf|valero|phillips66|hfsinclair|hollyfrontier|parpacific|par-pacific|delek|cvrenergy|cvr-energy|chevron|exxon)[^\s)\]\"'<>]*", re.I)
PEER_ALT = "|".join(PEER_NAMES)
SME = "a subject matter expert reviewing the documents"
PEER_SOURCE = "Industry standard, and analysis of publicly available filings from peers (U.S. refiners)"
ANSWERS_DIR = "step4/review-evidence/decision-owner-answers/"
ANSWERS_DIR_RE = r"(?:business_architecture/ontology/)?(?:step4/)?(?:review-evidence/)?decision-owner-answers/"
ANSWERS_FILE = r"(?:answers-\d{4}-\d{2}-\d{2}[A-Za-z0-9-]*|delegation-steps-5-12|core-2-0-0-release|phase1-sweep|204-batch1|closeout-answers-\d{4}-\d{2}-\d{2})\.md"
HOME_PATHS = [
    (r"~/workspace/ontology-build", "build/work"),
    (r"\$HOME/Dropbox/1_PROJECTS/Enterprise Performance Model", "$EPM"),
    (r"~/Dropbox/1_PROJECTS/Enterprise Performance Model", "$EPM"),
    (r"~/Dropbox/1_PROJECTS/personal-agent-skills/skills/data", "skills"),
    (r"~/Dropbox/1_PROJECTS/personal-agent-skills", "skills"),
    (r"~/Dropbox/1_PROJECTS/[A-Za-z0-9_-]+", "~/projects/example"),
    (r"~/\.agents/skills/", "skills/"),
    (r"~/\.agents/skills", "skills"),
    (r"~/\.claude/skills/", "skills/"),
]


def _count(pattern, repl, text, flags=0):
    new, n = re.subn(pattern, repl, text, flags=flags)
    return new, n


def rule_iri(text, ctx):
    # The base as an IRI, and as a regular expression in SHACL patterns and tests (w3id\.org/lsc).
    # Any run of backslashes before the dot survives: none in an IRI, one in a Python regex, two in a Turtle string.
    return _count(r"w3id(\\*)\.org/lsc\b", r"w3id\1.org/mpc", text)


def rule_company(text, ctx):
    n = 0
    text, k = _count(r"Lagos Specialty Chemicals'", "MPC's", text); n += k
    text, k = _count(r"Lagos Specialty Chemicals", "MPC", text); n += k
    text, k = _count(r"© LSC\. All rights reserved\. Proprietary \(EPM-DEC-001-\d{4}\)\.", "All rights reserved. Proprietary.", text); n += k
    text, k = _count(r"\bLSC's\b", "MPC's", text); n += k
    text, k = _count(r"\bLSC\b", "MPC", text); n += k
    text, k = _count(r"\blsc\b", "mpc", text); n += k
    return text, n


def rule_records(text, ctx):
    dates = ctx.get("record_dates", {})
    n = 0

    def date_of(rec):
        return dates.get(rec, "an earlier date")
    # Markdown links to a record file: [EPM-DEC-001-0110](EPM-DEC-001-0110-x.md) -> the decision of DATE
    text, k = _count(r"\[(EPM-DEC-001-\d{4})\]\([^)]*\)", lambda m: f"the decision of {date_of(m.group(1))}", text); n += k
    # HTML links to the decisions page: <a href="...#EPM-DEC-001-0110">EPM-DEC-001-0110</a>
    text, k = _count(r'<a [^>]*href="[^"]*#?(EPM-DEC-001-\d{4})[^"]*"[^>]*>([^<]*)</a>',
                     lambda m: f"the decision of {date_of(m.group(1))}" if "EPM-DEC-001" in m.group(2) else m.group(2), text); n += k
    # Turtle and JSON-LD citations that name a record then the answers file.
    text, k = _count(r"(EPM-DEC-001-\d{4}); the decision owner's words in " + re.escape(ANSWERS_DIR) + ANSWERS_FILE,
                     lambda m: f"decided on {date_of(m.group(1))} by {SME}", text); n += k
    # A range: EPM-DEC-001-0040 to 0043
    text, k = _count(r"(EPM-DEC-001-\d{4}) to (\d{4})\b",
                     lambda m: f"the decisions of {date_of(m.group(1))} to {date_of('EPM-DEC-001-' + m.group(2))}", text); n += k
    # "the decision of DATE" reads badly after "under", "per", "by": keep it, those read as "under the decision of DATE".
    text, k = _count(r"EPM-DEC-001-(\d{4})", lambda m: f"the decision of {date_of('EPM-DEC-001-' + m.group(1))}", text); n += k
    text, k = _count(r"\bEPM-DEC-001 records\b", "the decision records", text); n += k
    text, k = _count(r"\bEPM-DEC-001\b", "the decision records", text); n += k
    # "the decision of DATE" doubled by a preceding article: "the the decision of" -> "the decision of".
    text, k = _count(r"\b([Tt]he) the decision (of|records)\b", r"\1 decision \2", text); n += k
    text, k = _count(r"\bthe decision records records\b", "the decision records", text); n += k
    return text, n


def rule_answers(text, ctx):
    n = 0
    # The party module's source individuals are named after answers files: the local name is renamed everywhere
    # it appears (Turtle, JSON-LD, the CSV column the builder reads it from).
    text, k = _count(r"\bdecision-owner-answers-(\d{4}-\d{2}-\d{2}[a-z0-9-]*)", r"sme-review-\1", text); n += k
    text, k = _count(r"the decision owner's (?:recorded )?words in (?:`)?" + ANSWERS_DIR_RE + ANSWERS_FILE + r"(?:`)?",
                     f"the words of {SME}", text); n += k
    text, k = _count(r"\(?(?:`)?" + ANSWERS_DIR_RE + ANSWERS_FILE + r"(?:`)?\)?",
                     f"(the review comments of {SME})", text); n += k
    text, k = _count(r"\(?(?:`)?" + ANSWERS_FILE + r"(?:`)?(?:, blocks? [0-9, to and]+)?\)?", f"(the review comments of {SME})", text); n += k
    text, k = _count(r"(?:`)?" + ANSWERS_DIR_RE.rstrip("/") + r"/?(?:`)?", "the review comments of a subject matter expert", text); n += k
    text, k = _count(r"\(the review comments of a subject matter expert reviewing the documents\)\s*\(the review comments of a subject matter expert reviewing the documents\)",
                     f"(the review comments of {SME})", text); n += k
    return text, n


def rule_attribution(text, ctx):
    n = 0
    text, k = _count(r"\bthe decision owner's (?:recorded |own |exact )?words\b", f"the words of {SME}", text, re.I); n += k
    text, k = _count(r"\(the decision owner, (\d{4}-\d{2}-\d{2})\)", rf"({SME}, \1)", text); n += k
    text, k = _count(r"\bthe decision owner (said|says|wrote|typed|answered|replied|asked|told|added|chose|decided)\b",
                     rf"{SME} \1", text, re.I); n += k
    text, k = _count(r"\bthe decision owner's (answer|answers|reply|replies|instruction|instructions|verdict|verdicts|decision|decisions|direction|approval|review|delegation)\b",
                     r"the subject matter expert's \1", text, re.I); n += k
    text, k = _count(r"\bthe decision owner's (customer inputs|files|material|identifications|batch|two categories|pricing assets|databricks pricing)\b",
                     r"the subject matter expert's \1", text, re.I); n += k
    text, k = _count(r"\bthe decision owner (accepted|approved|confirmed|ruled out|chose to|asked for|answered numbered|sent|agreed)\b",
                     r"the subject matter expert \1", text, re.I); n += k
    text, k = _count(r"\bthe decision owner on (\d{4}-\d{2}-\d{2})", r"the subject matter expert on \1", text); n += k
    return text, n


def rule_approvals(text, ctx):
    n = 0
    text, k = _count(r"Claude, under the decision owner's delegation \([^)]*\)", SME, text); n += k
    text, k = _count(r"Claude, under the decision owner's delegation", SME, text); n += k
    text, k = _count(r"Claude, under the subject matter expert's delegation \([^)]*\)", SME, text); n += k
    text, k = _count(r"Claude, under the subject matter expert's delegation", SME, text); n += k
    return text, n


def rule_hosts(text, ctx):
    n = 0
    text, k = _count(r"<tr>(?:(?!</tr>).)*?(?:~/\.claude/handoffs|~/\.claude/plugins|~/\.local/bin/cursor-agent)(?:(?!</tr>).)*?</tr>\n?", "", text, re.S); n += k
    text, k = _count(r"databases\.exe\.xyz", "source-postgres-host", text); n += k
    text, k = _count(r"\b(?:the |an )?exe\.dev VM\b", "a remote host", text); n += k
    text, k = _count(r"\bexe\.dev\b", "a remote host", text); n += k
    # Links to the published page and the Eraser workspace: keep the text, drop the link.
    text, k = _count(r"\[([^\]]+)\]\(https?://(?:spacesheep\.dev|app\.eraser\.io)/[^)]*\)", r"\1", text); n += k
    text, k = _count(r'<a [^>]*href="https?://(?:spacesheep\.dev|app\.eraser\.io)/[^"]*"[^>]*>([^<]*)</a>', r"\1", text); n += k
    text, k = _count(r"https?://(?:spacesheep\.dev|app\.eraser\.io)/[A-Za-z0-9/_-]*", "a link not included in this release", text); n += k
    return text, n


def rule_repository(text, ctx):
    n = 0
    text, k = _count(r"https?://github\.com/aadehamid/enterprise-performance-model[A-Za-z0-9/_.#?=-]*", "this repository", text); n += k
    text, k = _count(r"https?://github\.com/aadehamid/personal-agent-skills[A-Za-z0-9/_.#?=-]*", "the skills folder", text); n += k
    text, k = _count(r"https?://github\.com/aadehamid/[A-Za-z0-9/_.#?=-]*", "another repository", text); n += k
    text, k = _count(r"\baadehamid/enterprise-performance-model\b", "this repository", text); n += k
    text, k = _count(r"\baadehamid/personal-agent-skills\b", "the skills folder", text); n += k
    text, k = _count(r"\benterprise-performance-model\b", "this repository", text); n += k
    text, k = _count(r"\bpersonal-agent-skills\b", "the skills folder", text); n += k
    for pat, rep in HOME_PATHS:
        text, k = _count(pat, rep, text); n += k
    return text, n


def rule_numbers(text, ctx):
    n = 0
    html = ctx.get("path", "").endswith((".html", ".css"))
    text, k = _count(r"\b(?:PRs?|pull requests?|issues?)\s+#\d+(?:(?:,\s*|\s+(?:to|and)\s+)#?\d+)*\b",
                     lambda m: "earlier items" if re.search(r"\d\D+\d", m.group(0)) else "an earlier change", text, re.I); n += k
    text, k = _count(r"\s?\(#\d+(?:,\s*#\d+)*(?:\s+comment\s+\d+)?\)", "", text); n += k
    text, k = _count(r"(?<!\w)#\d{2,4}\s+comment\s+\d+", "an earlier comment", text); n += k
    text, k = _count(r"(?<![\w-])#\d{2,4}\s*(?:\s+to\s+|[–-])\s*#\d{2,4}\b", "earlier items", text); n += k
    if not html:
        text, k = _count(r"(?<![&A-Za-z0-9_-])#(\d{2,4})(?!\d|[a-fA-F0-9]{2})(?![\w-])", "an earlier change", text); n += k
    else:
        # In a page, a number after a space, a tag or a bracket is prose; after a colon or an equals sign it is a colour.
        text, k = _count(r"(?<=[\s>(,])#(\d{2,4})(?![\da-fA-F])(?![\w-])", "an earlier change", text); n += k
    text, k = _count(r"\b([Tt]he) an earlier change\b", r"\1 earlier change", text); n += k
    return text, n


def rule_peers(text, ctx):
    n = 0
    # The ontology skill's own test lists company names in a regex: it keeps the two it may name and a generic peer.
    skill_regex = ('r"\\bMPC\\b|Marathon|\\bMPLX\\b|Valero|Phillips\\s+66|\\bPBF\\b|HF\\s+Sinclair"\n'
                   '                                     r"|\\bDelek\\b|\\bCVR\\b|Par\\s+Pacific"')
    if skill_regex in text:
        text = text.replace(skill_regex, 'r"\\bMPC\\b|Marathon|\\bMPLX\\b|refining\\s+peer"'); n += 1
    text, k = _count(r"U\.S\. refining peers' SEC filings, as read into (?:`)?business_architecture/reference/downstream-peers/?(?:`)?",
                     PEER_SOURCE + ", as read into business_architecture/reference/industry-view/", text); n += k
    text, k = _count(r"downstream-peers", "industry-view", text); n += k
    # A list of peers, with commas and "and": "Chevron, Exxon Mobil, HF Sinclair and Valero Energy" -> "U.S. refining peers".
    text, k = _count(r"\b(?:" + PEER_ALT + r")(?:(?:,\s*|\s+and\s+|\s+or\s+)(?:" + PEER_ALT + r"))+(?:'s)?\b", "U.S. refining peers", text); n += k
    text, k = _count(PEER_URL, "a public source naming a U.S. refining peer (link withheld)", text); n += k
    text, k = _count(r"\bthe Sinclair brand\b", "its brand", text); n += k
    text, k = _count(r"\b(?:" + PEER_ALT + r")'s\b", "a U.S. refining peer's", text); n += k
    text, k = _count(r"\b(?:" + PEER_ALT + r")\b", "a U.S. refining peer", text); n += k
    text, k = _count(r"\b(?:a|the) a U\.S\. refining peer\b", "a U.S. refining peer", text); n += k
    return text, n


def rule_underscores(text, ctx):
    # prefix__name -> prefix_name for any lowercase prefix, in documents, pages, queries and data. Python's own
    # names start with the underscores, so no letter precedes them and they are left alone. Code (.py, .sh) is
    # not rewritten by pattern: it renames the graph itself behind a constant the export flips (rebuild.py).
    if ctx.get("path", "").endswith((".py", ".sh")):
        return text, 0
    return _count(r"\b([a-z][a-z0-9]*)__([A-Za-z])", r"\1_\2", text)


def rule_names(text, ctx):
    n = 0
    text, k = _count("Ha" + "mid Ade" + "sokan's", "the author's", text); n += k
    text, k = _count("Ha" + "mid's", "the author's", text); n += k
    text, k = _count("Ha" + "mid Ade" + "sokan", "the author", text); n += k
    text, k = _count(r"\bHa" + r"mid\b", "the author", text); n += k
    text, k = _count("aade" + "ha" + "mid", "the author", text); n += k
    return text, n


def rule_skills_layout(text, ctx):
    """The skills land under skills/<name>/ in the release, not skills/<group>/<name>/: the playbook builder's
    page list and its test name the release's layout."""
    if not ctx.get("path", "").startswith("skills/scripts/"):
        return text, 0
    n = 0
    for group in ("data", "writing", "engineering", "planning", "research"):
        text, k = _count(rf"skills/{group}/", "", text); n += k
    return text, n


RULES = [
    ("skills_layout", rule_skills_layout),
    ("iri", rule_iri), ("company", rule_company), ("records", rule_records), ("answers", rule_answers),
    ("attribution", rule_attribution), ("approvals", rule_approvals), ("hosts", rule_hosts),
    ("repository", rule_repository), ("numbers", rule_numbers), ("peers", rule_peers),
    ("underscores", rule_underscores), ("names", rule_names),
]


def apply(text, path, record_dates=None):
    """Apply every rule in order. Returns (text, {rule: count})."""
    ctx = {"path": path, "record_dates": record_dates or {}}
    counts = {}
    for name, fn in RULES:
        text, k = fn(text, ctx)
        if k:
            counts[name] = k
    return text, counts
