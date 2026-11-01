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
  8. repository:   this account's repositories and handle -> plain words (any other repository of the account ->
                   "another repository"); home-folder paths -> release paths.
  9. numbers:      issue and pull request numbers -> plain words (a CSS colour such as "--text: #111" is not a number).
 10. peers:        the nine company names and their tickers -> U.S. refining peers; a peer's SEC filing link -> withheld
                   (MPC's and MPLX's own filings stay); the peer evidence folder -> industry view; the peer-tier
                   wording -> the agreed source wording.
 11. underscores:  prefix__name -> prefix_name for the graph's prefixes, outside Python's own names.
 12. names:        the owner's names and handle (from owner.py's configuration, never a tracked file) -> the author.
 13. left-out:     the rows and sentences that point at documents the release leaves out (the store notes, the
                   superseded projection guideline).
 14. previous-paths: a document's path to the release before the newest (releases/kpi/1.2.0/) -> its place in the
                   release, releases/previous/kpi/1.2.0/.
 15. agents:       agent names and agent work -> neutral wording, with every decision the subject matter expert's
                   (the decision's amendment of 2026-11-01). A draft keeps its status.

Rule 3 also rewrites the short forms that follow a citation ("EPM-DEC-001-0020, 0021 and 0036", "(0021)",
"amending 0021") when the number is a record in the record-dates map; a four-digit number that is not a known
record stays as it is.
"""
import re

import manifest
import owner
import vocabulary as V

ONT = "business_architecture/ontology"

# Rule 11's prefixes: the projection's fixed prefixes plus n10s's schema and SHACL prefixes (vocabulary.py).
GRAPH_PREFIXES = V.GRAPH_PREFIXES
PEER_NAMES = [r"Valero Energy Corporation", r"Valero Energy", r"Valero", r"Phillips ?66", r"PBF Energy", r"PBF",
              r"HF ?Sinclair", r"HollyFrontier", r"Par\s+Pacific", r"Delek US", r"Delek", r"CVR Energy", r"CVR",
              r"Chevron Corporation", r"Chevron", r"Exxon ?Mobil", r"ExxonMobil", r"Exxon"]
# The peers' stock tickers (vocabulary.PEER_TICKERS; case-sensitive: "psx" or "dino" in lower case is not a ticker).
# DK (Delek) is two letters, so it counts only inside a ticker list (MPC and MPLX count as list members) or in
# parentheses after a name; the others stand on their own.
TICKER = r"(?:" + "|".join(V.PEER_TICKERS) + r")"
TICKER_OR_DK = r"(?:" + "|".join(V.PEER_TICKERS) + r"|DK)"
LIST_TICKER = r"(?:" + "|".join(V.PEER_TICKERS + V.OWN_TICKERS) + r")"
TICKER_SEP = r"(?:,\s*|/|\s+and\s+|\s+or\s+)"
# A link whose address names a peer (a filing on EDGAR, a news slug, an investor site) is withheld with the name.
PEER_URL = re.compile(r"https?://[^\s)\]\"'<>|]*(?:pbf|valero|phillips66|hfsinclair|hollyfrontier|parpacific|par-pacific|delek|cvrenergy|cvr-energy|chevron|exxon)[^\s)\]\"'<>|]*", re.I)
# A filing on SEC EDGAR is named by the filer's CIK (vocabulary.PEER_CIKS, cited there; EDGAR writes it with or without
# leading zeroes) and the file by the ticker (vlo-20251231.htm): a peer's filing is withheld; MPC's, MPLX's and any
# other filer's (an industry exhibit) stay.
EDGAR_URL = re.compile(r"https?://(?:www\.)?sec\.gov/Archives/edgar/data/0*(?:" + "|".join(V.PEER_CIKS) + r")/[^\s)\]\"'<>|]*"
                       r"|https?://(?:www\.)?sec\.gov/Archives/edgar/data/\d+/[^\s)\]\"'<>|]*/(?:" + "|".join(V.PEER_SLUGS) + r")-\d{8}\.[^\s)\]\"'<>|]*", re.I)
PEER_FILING = "a public filing of a U.S. refining peer (link withheld)"
OTHER_REPOS = V.OTHER_REPOS
PEER_ALT = "|".join(PEER_NAMES)
SME = "a subject matter expert reviewing the documents"
PEER_SOURCE = "Industry standard, and analysis of publicly available filings from peers (U.S. refiners)"
ANSWERS_DIR = "step4/review-evidence/decision-owner-answers/"
ANSWERS_DIR_RE = r"(?:business_architecture/ontology/)?(?:step4/)?(?:review-evidence/)?decision-owner-answers/"
ANSWERS_FILE = r"(?:answers-\d{4}-\d{2}-\d{2}[A-Za-z0-9-]*|delegation-steps-5-12|core-2-0-0-release|phase1-sweep|204-batch1|closeout-answers-\d{4}-\d{2}-\d{2})\.md"
STYLE_SPAN = re.compile(r"<style\b[^>]*>.*?</style>|\bstyle\s*=\s*\"[^\"]*\"|\bstyle\s*=\s*'[^']*'", re.S | re.I)
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
    n = 0
    # The ontology skill's own test lists the record ID pattern as a term its guide must not hold; its fixture "see
    # EPM-DEC-001-0001" becomes "see the decision of <date>" below, so the pattern names that wording instead.
    skill_term = '("a project decision record", r"EPM-DEC|\\bEPM\\b")'
    if skill_term in text:
        text = text.replace(skill_term, '("a project decision record", r"the decision of \\d{4}-\\d{2}-\\d{2}|\\bEPM\\b")'); n += 1
    dates = ctx.get("record_dates", {})

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
    # The short forms after a citation: "the decision of DATE, 0021 and 0036", "the decisions of DATE to 0043",
    # "(0021)", "amending 0021". Only a number the record-dates map knows is a record; any other stays.
    known = lambda num: ("EPM-DEC-001-" + num) in dates

    def short_chain(m):
        head, rest = m.group(1), m.group(2)
        out, pos = head, 0
        for part in re.finditer(r"(, | and | or | to |; )(0\d{3})\b", rest):
            if not known(part.group(2)):
                break
            out += rest[pos:part.start()] + part.group(1) + f"the decision of {date_of('EPM-DEC-001-' + part.group(2))}"
            pos = part.end()
        return out + rest[pos:]
    text, k = _count(r"(the decisions? of \d{4}-\d{2}-\d{2}|the decision of an earlier date)((?:(?:, | and | or | to |; )0\d{3}\b)+)", short_chain, text); n += k
    text, k = _count(r"\((0\d{3})\)", lambda m: f"(the decision of {date_of('EPM-DEC-001-' + m.group(1))})" if known(m.group(1)) else m.group(0), text); n += k
    text, k = _count(r"\b(amending|amended by|amends|supersedes|superseded by) (0\d{3})\b",
                     lambda m: f"{m.group(1)} the decision of {date_of('EPM-DEC-001-' + m.group(2))}" if known(m.group(2)) else m.group(0), text); n += k
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
    account = "(?:" + "|".join(re.escape(x) for x in owner.owner_names()) + ")"  # the GitHub account, from the configuration
    text, k = _count(r"https?://github\.com/" + account + r"/enterprise-performance-model[A-Za-z0-9/_.#?=-]*", "this repository", text); n += k
    text, k = _count(r"https?://github\.com/" + account + r"/personal-agent-skills[A-Za-z0-9/_.#?=-]*", "the skills folder", text); n += k
    text, k = _count(r"https?://github\.com/" + account + r"/[A-Za-z0-9/_.#?=-]*", "another repository", text); n += k
    text, k = _count(r"\b" + account + r"/enterprise-performance-model\b", "this repository", text); n += k
    text, k = _count(r"\b" + account + r"/personal-agent-skills\b", "the skills folder", text); n += k
    text, k = _count(r"\benterprise-performance-model\b", "this repository", text); n += k
    text, k = _count(r"\bpersonal-agent-skills\b", "the skills folder", text); n += k
    for repo in OTHER_REPOS:
        # "<repo> #4", "<repo> PR #3" and "<repo> folder": the issue number goes with the name, whatever its length.
        text, k = _count(r"\b" + re.escape(repo) + r"(?:\s+(?:PRs?|pull requests?|issues?))?\s+#\d+\b", "another repository", text); n += k
        text, k = _count(r"\b" + re.escape(repo) + r"\b", "another repository", text); n += k
    text, k = _count(r"\b([Tt]he) another repository\b", r"\1 other repository", text); n += k
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
        # In a page, a number after a space, a tag or a bracket is prose; inside a <style> block or a style attribute
        # (or anywhere in a stylesheet), after a colon or an equals sign with any spaces between ("--text: #111"), it
        # is a colour and stays. "Issue: #455" in prose is a number.
        spans = [(0, len(text))] if ctx.get("path", "").endswith(".css") else [m.span() for m in STYLE_SPAN.finditer(text)]

        def prose_number(m):
            before = text[:m.start()].rstrip()
            in_css = any(a <= m.start() < b for a, b in spans)
            return m.group(0) if in_css and before.endswith((":", "=")) else "an earlier change"
        text, k = _count(r"(?<=[\s>(,])#(\d{2,4})(?![\da-fA-F])(?![\w-])", prose_number, text); n += k
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
    text, k = _count(EDGAR_URL, PEER_FILING, text); n += k
    text, k = _count(PEER_URL, "a public source naming a U.S. refining peer (link withheld)", text); n += k
    text, k = _count(r"\bthe Sinclair brand\b", "its brand", text); n += k
    text, k = _count(r"\b(?:" + PEER_ALT + r")'s\b", "a U.S. refining peer's", text); n += k
    text, k = _count(r"\b(?:" + PEER_ALT + r")\b", "a U.S. refining peer", text); n += k
    # The tickers: a list ("PSX, VLO and MPC" keeps MPC), a ticker after a name ("a U.S. refining peer (VLO)"), one alone.
    text, k = _count(r"\b(?:a U\.S\. refining peer|U\.S\. refining peers) \(" + TICKER_OR_DK + r"\)", "a U.S. refining peer", text); n += k
    text, k = _count(r"\b" + TICKER_OR_DK + r"(?:" + TICKER_SEP + TICKER_OR_DK + r")+(?:'s)?\b", "U.S. refining peers", text); n += k
    # DK beside MPC or MPLX ("DK and MPC", "MPLX/DK") is Delek's ticker; MPC and MPLX themselves stay.
    text, k = _count(r"\bDK(?=" + TICKER_SEP + LIST_TICKER + r"\b)", "a U.S. refining peer", text); n += k
    text, k = _count(r"\b(" + LIST_TICKER + TICKER_SEP + r")DK\b", r"\1a U.S. refining peer", text); n += k
    text, k = _count(r"\(" + TICKER_OR_DK + r"\)", "(a U.S. refining peer)", text); n += k
    text, k = _count(r"\b" + TICKER + r"'s\b", "a U.S. refining peer's", text); n += k
    text, k = _count(r"\b" + TICKER + r"\b", "a U.S. refining peer", text); n += k
    text, k = _count(r"\b(?:a|the) a U\.S\. refining peer\b", "a U.S. refining peer", text); n += k
    # At the start of a sentence, a line, a list item or a heading's clause, the phrase is capitalised.
    text, k = _count(r"(^|[.!?:]\s+|^\s*(?:[-*]|\d+\.)\s+(?:\*\*)?)a U\.S\. refining peer", r"\1A U.S. refining peer", text, re.M); n += k
    return text, n


def rule_left_out(text, ctx):
    """Sentences and table rows that point at documents the release leaves out (rule 13)."""
    n = 0
    text, k = _count(r"^\| `(?:LOCAL-STORES|STORE-INVENTORY)\.md` \|.*\n", "", text, re.M); n += k
    text, k = _count(r"<tr><td><code>business_architecture/ontology/projection/(?:LOCAL-STORES|STORE-INVENTORY)\.(?:md|html)</code></td>.*?</tr>\n?", "", text, re.S); n += k
    text, k = _count(r"Figures from <code>LOCAL-STORES\.md</code>, ", "Figures from ", text); n += k
    text, k = _count(r"Ports and names from <code>LOCAL-STORES\.md</code>;", "Ports and names from the stores runbook;", text); n += k
    text, k = _count(r"comes from <code>business_architecture/ontology/projection/LOCAL-STORES\.md</code> and the demo", "comes from the stores runbook and the demo", text); n += k
    text, k = _count(r"<code>projection/README\.md</code>, <code>LOCAL-STORES\.md</code>, then", "<code>projection/README.md</code>, then", text); n += k
    text, k = _count(r"([Ff]ollow(?:s|ing)) the guideline in `?\.\./lpg-projection/`? \(v2\.2\)", r"\1 the projection guideline, version 2.2,", text); n += k
    text, k = _count(r", and `\.\./lpg-projection/` keeps the v2\.2 copy as superseded evidence;", " (the v2.2 copy is not part of this release);", text); n += k
    # The page builder's entries for the two store notes: the builder skips a missing source, and the entry itself
    # names the note, so the entry goes.
    text, k = _count(r"^        single\(f\"\{ONT\}/projection/(?:LOCAL-STORES|STORE-INVENTORY)\.md\",\n[^\n]*\),\n", "", text, re.M); n += k
    # Table rows and list items that point at the superseded guideline folder.
    text, k = _count(r"^\| `lpg-projection/` \|.*\n", "", text, re.M); n += k
    text, k = _count(r"<tr><td><code>business_architecture/ontology/lpg-projection/[^<]*</code></td>.*?</tr>\n?", "", text, re.S); n += k
    text, k = _count(r", <code>LOCAL-STORES\.md</code>(?=[,<])", "", text); n += k
    text, k = _count(r"\(lpg-projection/, pin ([0-9a-f]+)\)", r"(the projection guideline, pin \1)", text); n += k
    text, k = _count(r"(?:`|<code>)?(?:business_architecture/ontology/projection/)?LOCAL-STORES\.(?:md|html)(?:`|</code>)?", "the stores runbook", text); n += k
    text, k = _count(r"(?:`|<code>)?(?:business_architecture/ontology/projection/)?STORE-INVENTORY\.(?:md|html)(?:`|</code>)?", "the store inventory of the original build (not in this release)", text); n += k
    if not ctx.get("path", "").startswith("skills/"):  # the skills name their own lpg-projection.md and container; their guide test lists "lpg-projection/" as a path to refuse
        text, k = _count(r"(?:`|<code>)?(?:\.\./|business_architecture/ontology/)?lpg-projection/(?:`|</code>)?", "the superseded projection guideline folder (not in this release)", text); n += k
    # The walkthrough's commands for core's earlier builders: they read the earlier packages, which the release
    # leaves out, so the release shows them as what was run, not as a command to run.
    text, k = _count(r"^(uv run [^\n]*python build_core(?:_next|_2_1)?\.py(?: --verify)?)$",
                     r"# run when that release was cut; its inputs are not in this release (the newest builder is build_core_2_4.py): \1", text, re.M); n += k
    return text, n


def rule_previous_paths(text, ctx):
    """A document's path to the release before the newest (releases/kpi/1.2.0/) names where it is in the release:
    releases/previous/kpi/1.2.0/ (manifest.py moves it). Term IRIs put the version after "releases/", so they do not
    match. The history folder's own files are left as cut."""
    path = ctx.get("path", "")
    if path.startswith(f"{ONT}/releases/previous/") or path.endswith((".py", ".sh")):
        return text, 0  # code resolves a package's path itself (build_module.resolve) and is not rewritten by pattern
    n = 0
    for m, (newest, previous) in manifest.MODULES.items():
        text, k = _count(rf"(?<!previous/)\breleases/{re.escape(m)}/{re.escape(previous)}(?![\d.])", f"releases/previous/{m}/{previous}", text); n += k
    return text, n


def rule_underscores(text, ctx):
    # prefix__name -> prefix_name for any lowercase prefix, in documents, pages, queries and data. Python's own
    # names start with the underscores, so no letter precedes them and they are left alone. Code (.py, .sh) is
    # not rewritten by pattern: it renames the graph itself behind a constant the export flips (rebuild.py).
    if ctx.get("path", "").endswith((".py", ".sh")):
        return text, 0
    return _count(r"\b([a-z][a-z0-9]*)__([A-Za-z])", r"\1_\2", text)


# Rule 15's patterns. A parenthetical, down to two levels of nesting (a quote that holds "(Recommended)").
_PAREN = r"\((?:[^()]|\((?:[^()]|\([^()]*\))*\))*\)"
_SME_DEC = "the subject matter expert's decision of"
REVIEWERS = r"(?:Kimi|Codex|Bugbot|Cursor|Pi)"
# What the build's agents and review tools did, as the release says it: (pattern, replacement), in order.
AGENT_TEXT = [
    # Approvals: the release's approver is the subject matter expert, with no route through a delegation.
    (r"Approved by Claude under the (?:[\w ]+'s )?delegation(?: " + _PAREN + r")?(?:, (?:which lets it approve the queue's minor releases|with the decision owner's alignment with the plan that names it))?(?: " + _PAREN + r")?",
     "Approved by a subject matter expert"),
    (r"approved by Claude under the (?:[\w ]+'s )?delegation", "approved by a subject matter expert"),
    (r"\b[Aa] minor Claude approved under the delegation\b", "a minor release a subject matter expert approved"),
    (r"\b[Aa] minor Claude approved\b", "a minor release a subject matter expert approved"),
    (r"Claude approved (those additions|it|the minor release) under the (?:[\w ]+'s )?delegation(?:, which lets it approve the queue's minor releases)?", r"a subject matter expert approved \1"),
    (r"Claude approved\b", "a subject matter expert approved"),
    (r"Claude approves\b", "the subject matter expert approves"),
    (r"The decision owner, or Claude under their recorded delegation", "The decision owner"),
    (r" or, under the delegation, by Claude\b", ""),
    (r"; Claude asked the decision owner before every release", "; the decision owner approved every release"),
    (r"Under the delegation, Claude applied", "The subject matter expert chose"),
    (r"Under the delegation \((the decisions? of [^)]*)\)", r"By \1"),
    (r"is Claude's, under the delegation \(([^)]*)\)", r"follows \1"),
    (r"\band approved under the delegation\b", "and approved by a subject matter expert"),
    (r"approved under the delegation\b", "approved by a subject matter expert"),
    (r"Claude's choice, delegated under the decision of", _SME_DEC),
    (r"Claude's design under the decision of", _SME_DEC),
    (r"(?:[Dd]elegated|[Dd]ecided) under the decision of", "under " + _SME_DEC),
    (r"\bClaude decides the open questions on the decision owner's behalf", "The subject matter expert decides the open questions"),
    # Who drafted a text: the text keeps its status, and loses the name.
    (r"\bDrafted by Claude\b", "Drafted"),
    (r"\bdrafted by Claude\b", "drafted"),
    (r"\bClaude drafted\b", "drafted"),
    (r"\b(is|are) Claude's words\b", r"\1 written for this ontology"),
    (r"\bClaude's words\b", "the ontology's own words"),
    (r"\bClaude's EPM working definition\b", "the EPM working definition"),
    (r"\bis Claude's, adapted\b", "is adapted"),
    (r"\bwith Claude's definitions\b", "with definitions written for this ontology"),
    (r"\bwith Claude's description\b", "with a description written for this ontology"),
    (r", Claude's guess,", ", a guess,"),
    (r"\bas Claude's guess\b", "as a guess"),
    (r"a recommendation Claude called a guess", "a recommendation marked as a guess"),
    (r"accepting Claude's recommendation on (\S+), which Claude said was a guess", r"accepting a recommendation on \1, marked as a guess"),
    (r"\bClaude's recommendation\b", "a recommendation"),
    (r"\bClaude's reading\b", "the reading"),
    (r"\bClaude's context\b", "the context"),
    (r",? by Claude\b", ""),
    (r" \(Claude\)", ""),
    (r"\bClaude Code session of\b", "session of"),
    (r"(?:<strong>)?\*{0,2}Built with:\*{0,2}(?:</strong>)? Kailey and Claude Code\.\s*", ""),
    (r"\bKailey\b", "a subject matter expert"),
    # The skills' instructions: what to do, with the tool left open.
    (r"\(skills, CLAUDE\.md, AGENTS\.md\)", "(skills and instruction files)"),
    (r"\(a skill, CLAUDE\.md, AGENTS\.md, a prompt\)", "(a skill, an instruction file, a prompt)"),
    (r"\bClaude is writing its own answer\b", "You are writing your own answer"),
    (r"\bWhen Claude writes its own response\b", "When you write your own response"),
    (r"sounds like ChatGPT/AI", "sounds like AI"),
    (r"the one in the Anthropic skills directory \(rules 1 to 31\) and the Cursor fork in cursor/plugins \(rules 32 and 33, and the strict dash rule\)",
     "a public skill of that name (rules 1 to 31) and a fork of it (rules 32 and 33, and the strict dash rule)"),
    (r"^\| The user asks to tune, calibrate, or personalize these rules \|.*\n", ""),
    (r' If the user says "calibrate my writing rules", "recalibrate", or "update my writing rules from my sessions", this skill owns that task\.', ""),
    # A review cited as a parenthetical, or as the head of a comment, goes; what it found stays.
    (REVIEWERS + r"'s review\b", "a review"),
    (r"\bafter a Cursor HOLD\b", "after a later review"),
    (r"[ \t]?\([^()\"\n]*\b" + REVIEWERS + r"\b(?:'s)?[^()\"\n]*\)", ""),
    (r"[ \t]?\(" + REVIEWERS + r"\b(?:'s)?[^()\"\n]*\)", ""),
    (r"[ \t]?\(findings? \d+[^()\"\n]*\)", ""),
    (r"(?m)^([ \t]*#[ \t]*)(?:[^:\n]{0,40}\b)?" + REVIEWERS + r"\b[^:\n]*:[ \t]*", r"\1"),
    (r"(?m)^([ \t]*#[ \t]*-*[ \t]*)" + REVIEWERS + r" round \d+ findings[ \t]*", r"\1Regressions "),
    (r'("""[ \t]*)' + REVIEWERS + r" round \d+,? [^:\n]*:[ \t]*", r"\1"),
    # What remains of the process that built this.
    (r"\bAGENTS\.md\b", "the project's instructions"),
    (r"\bCLAUDE\.md\b", "the project's instructions"),
    (r"the project's instructions, Working rules \(evidence order\)", "the evidence order"),
    (r"the project's instructions, Working rules", "the working rules"),
    (r"the project's `the project's instructions`", "the project's instructions"),
    (r"\bA pull request changes one module\b", "A release changes one module"),
    (REVIEWERS + r" round \d+(?:,? findings? [\d, and]+)?\.?", ""),
    (r"(?:of|in) (?:the first independent review|review round \d+)", "of an earlier review"),
    (r"\bFrom review round \d+\b", "From a later review"),
    (r"\b(?:review|Review) rounds?\b", "review"),
    (r"\bthe independent review\b", "a review"),
    (r"\ban independent review\b", "a review"),
    (r"\bindependent (reviewers?|review)\b", r"\1"),
    (r"\ba PR verdict\b", "a review"),
    (r"\bthe PR verdict\b", "the review"),
    (r", a review and the Cursor verdict pass\b", " and a review pass"),
    # Delegation as the build used it. The business term stays: the delegation of authority, a documented delegation.
    (r"Yes, delegate as described \(Recommended\)", "Approved as described"),
    (r"Claude, under the delegation, (\w+)", r"The subject matter expert \1"),
    (r"\bUnder the delegation, no\b", "No"),
    (r"\bunder the (?:subject matter expert's|decision owner's) delegation\b", "on the subject matter expert's approval"),
    (r",? under the delegation\b(?! of\b)", ""),
    (r"(?:[Dd]elegated|[Dd]ecided) under\s+(?:#\s*)?the decision of", "under " + _SME_DEC),
    # The build's pull requests.
    (r"\b(noted|carried) in the batch (\d+) PR\b", r"\1 in batch \2 of the process-map work"),
    (r"\bsee naming PR\b", "see the naming pass"),
    (r"\bA change is a pull request and a release\b", "A change is a new release"),
    (r"\bfails its PR\b", "fails its check"),
    (r"\bso on every PR\b", "so on every change"),
    (r"\bin the item G pull request, ", ""),
    (r"\bthe same pull request\b", "the same change"),
    (r"\bbefore opening a pull request\b", "before you share a change"),
    (r"<h3([^>]*)>The agent skills and the review loop</h3>", r"<h3\1>The skills</h3>"),
    (r"<code>the project's instructions</code> names the skills every agent loads: <code>clear-writing</code> for anything a person reads and <code>way-of-working</code> for any change\. ", ""),
    (r" Every change went through a pull request: [^<]*?\(<code>the project's instructions</code>[^)]*\)\.", " Every change passed the checks and a review before it was accepted."),
    (r"Every change goes through a pull request: [^<]*?\(the project's instructions\)\.", "Every change passes the checks and a review before it is accepted."),
    (r"\bagent skills\b", "skills"),
    (r"\bAgent skills\b", "Skills"),
    (r" \((?:<code>)?the project's instructions(?:</code>)?(?:, \"Working rules\"(?: and \"Before every push\")?)?\)", ""),
    (r"\ba subject matter expert approved by a subject matter expert\b", "a subject matter expert approved"),
    (r", then <code>the project's instructions</code> \(how every change is made and reviewed\)", ""),
    (r"\bthe evidence order in the project's instructions\b", "the evidence order"),
    (r"<code>the skills folder/skills/", "<code>skills/"),
    # The demo's scenario and its guard.
    (r" \(the decision owner: \"Remove any mention of ChatGPT\", [\d-]+\)", ""),
    (r"\(a subject matter expert[^()\n]{0,60}\"Remove any mention of ChatGPT\", [\d-]+\)", ""),
    (r'"FACT" in body or "ChatGPT" in body', '"FACT" in body'),
    (r'"FACT" not in body and "ChatGPT" not in body', '"FACT" not in body'),
    (r"The template's databricks-claude-sonnet-4-5\s+(#\s*)?is not served here\.", r"The template's default model is not served here."),
    (r"\ban OpenAI-style key\b", "a secret-key shape"),
    # The worklog does not ship (the decision's amendment of 2026-11-01).
    (r"the worklog \(the build record\),\s+", ""),
    (r"^\|[^\n]*ontology-worklog[^\n]*\n", ""),
    (r"\s+and this project's decision records\s+\(`\.\./domain/decisions/`, the decision records\)", ""),
    (r",? and\s+the worklog's plan table for where the build stands\. The worklog was named\s+`ontology-playbook\.md` until [\d-]+\.", "."),
    (r"project decisions get an the decision records record and a dated worklog\s+entry,", "project decisions get a decision record,"),
    (r"The worklog's plan\s+table \(`step4/playbook/ontology-worklog\.md` §2\) is authoritative for step\s+status: ", ""),
    (r" \(`step4/playbook/ontology-worklog\.md`, 3d-c\)", ""),
    (r' \(<code>step4/playbook/ontology-worklog\.md</code>, §1 "What we are building"; (the first sections of this page describe the map)\)', r" (\1)"),
    (r' The worklog \(<code>[^<]*ontology-worklog\.md</code>, §2 "The plan"\) records how this build walked the steps\.', ""),
    (r"<li><code>[^<]*ontology-worklog\.md, §1</code>:[^<]*</li>", ""),
    (r"(?:,| and) <code>step4/playbook/ontology-worklog\.md</code>", ""),
    (r"\|ontology-worklog\b", ""),
    # The release keeps no saved answers, so its skill says where an approval is kept.
    (r"and pin it in a test that reads it from the saved answer\.", "and keep the saved approval beside your decision records."),
]
# A row of a page's table that names an agent describes the build's own tooling: the row goes.
AGENT_ROW = re.compile(r"<tr>(?:(?!</tr>).)*?(?:\b(?:Claude|Codex|Kimi|Bugbot|Herdr|herdr|Anthropic|OpenAI|ChatGPT|Rex)\b|Cursor (?:bot|PR|app)|way-of-working|rex-review|pi-review|gpt-\d|AGENTS\.md|CLAUDE\.md|APPROVAL_POLICY|REVIEW_STANDARDS|ontology-worklog)(?:(?!</tr>).)*?</tr>\n?", re.S)


# "PR" is also public relations, in the APQC framework's names and the process map's text; those stay.
PR_WORD = re.compile(r"(?<!\.\d )(?<!\()\bPR\b(?! campaigns?\b| program\b| all\b|\)| strategy\b)")


def rule_agents(text, ctx):
    """Agent names and agent work (rule 15): the release names no agent and no review tool, and every decision reads
    as the subject matter expert's. A draft keeps its status. The demo's own Genie agents and supervisor, PROV-O's
    prov:Agent and prov:SoftwareAgent, and a database cursor are not touched."""
    n = 0
    if ctx.get("path", "").endswith(".html"):
        text, k = AGENT_ROW.subn("", text); n += k
    for pattern, repl in AGENT_TEXT:
        text, k = _count(pattern, repl, text, re.M); n += k
    if not ctx.get("path", "").startswith("skills/"):  # the skills teach any project, which may use pull requests
        text, k = _count(r"\bskills/(?:data|writing|engineering)/", "skills/", text); n += k
        text, k = _count(r"\b[Pp]ull requests\b", "changes", text); n += k
        text, k = _count(r"\bA pull request\b", "A change", text); n += k
        text, k = _count(r"\b[Pp]ull request\b", "change", text); n += k
        text, k = _count(r"\bPRs\b", "changes", text); n += k
        text, k = _count(PR_WORD, "change", text); n += k
    if ctx.get("path", "").endswith(".py"):  # the period a removed citation leaves at the start of a line
        text, k = _count(r'(?m)^([ \t]*(?:#[ \t]*)?)\.(?= |"""|$)', r"\1", text); n += k
    if ctx.get("path", "") == "scripts/test_epm_facts.py":  # a fixture's second speaker, in the check's own test
        text, k = _count(r"\bCodex\b", "Reviewer", text); n += k
    return text, n


def rule_names(text, ctx):
    n = 0
    for name in owner.owner_names():
        text, k = _count(r"\b" + re.escape(name) + r"'s\b", "the author's", text); n += k
        text, k = _count(r"\b" + re.escape(name) + r"\b", "the author", text); n += k
    return text, n


def rule_skills_layout(text, ctx):
    """The skills land under skills/<name>/ in the release, not skills/<group>/<name>/: the playbook builder's
    page list and its test name the release's layout."""
    if not ctx.get("path", "").startswith("skills/scripts/"):
        return text, 0
    n = 0
    for group in ("data", "writing", "engineering", "planning", "research"):
        text, k = _count(rf"skills/{group}/", "", text); n += k
        text, k = _count(rf'"skills", "{group}", ', "", text); n += k  # os.path.join(HERE, "..", "skills", "data", ...)
    return text, n


RULES = [
    ("skills_layout", rule_skills_layout),
    ("iri", rule_iri), ("company", rule_company), ("records", rule_records), ("answers", rule_answers),
    ("attribution", rule_attribution), ("approvals", rule_approvals), ("hosts", rule_hosts),
    ("repository", rule_repository), ("numbers", rule_numbers), ("peers", rule_peers), ("left-out", rule_left_out),
    ("previous-paths", rule_previous_paths), ("underscores", rule_underscores), ("agents", rule_agents), ("names", rule_names),
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
