"""The leak vocabulary the rewrite rules (rules.py) and the leak gate (gate.py) share, so a peer, a repository or a
graph prefix added later reaches both at once. Nothing here names a person; the owner's names come from owner.py.
"""
import re

# Market news: the pricing demo's cached Decision API (Parallel) search results and the decision owner's briefing
# collection, SCENARIO.md. Peer names in these files stay in the release (EPM-DEC-001-0112, point 7): the peer rule
# leaves them as they are and the gate does not fail on a peer in their text (a file name that names a peer still fails). Every other check still applies to them, and
# every other file, each ontology module and every other demo file included, names no peer.
MARKET_NEWS = re.compile(r"^demos/downstream-pricing-databricks-free/(?:SCENARIO\.md|data/parallel/[^/]+\.json)$")

# The peers' stock tickers, as the cached market news and the evidence tables write them (case-sensitive: "psx" or
# "dino" in lower case is not a ticker). DK (Delek) is two letters, so it counts only beside another ticker, MPC or
# MPLX, or in parentheses; the others stand on their own.
PEER_TICKERS = ("VLO", "PSX", "PBF", "DINO", "PARR", "CVI", "CVX", "XOM")
# Tickers that are not peers but mark a ticker list: a two-letter ticker beside them is a ticker, not a word.
OWN_TICKERS = ("MPC", "MPLX")

# The peers' filers on SEC EDGAR, by Central Index Key. Source: the SEC's ticker-to-CIK file,
# https://www.sec.gov/files/company_tickers.json, retrieved 2026-10-31: VLO 1035002 (Valero Energy Corp/TX), PSX 1534701
# (Phillips 66), PBF 1534504 (PBF Energy Inc.), DINO 1915657 (HF Sinclair Corp), PARR 821483 (Par Pacific Holdings,
# Inc.), DK 1694426 (Delek US Holdings, Inc.), CVI 1376139 (CVR Energy Inc), CVX 93410 (Chevron Corp), XOM 2115436
# (ExxonMobil Holdings Corp). Two predecessor filers whose earlier filings are still on EDGAR, from the SEC's company
# search (https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=<cik>, same date): 34088 (Exxon Mobil Corp,
# the filer before the 2025 holding company) and 48039 (HollyFrontier Corp, before the HF Sinclair merger of 2022).
# The same file gives MPC 1510295 (Marathon Petroleum Corp) and MPLX 1552000 (MPLX LP), whose filings the release
# may link; any other filer (an industry exhibit, for example) is not a peer. How a CIK is written: the SEC's
# "Accessing EDGAR Data" page (https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data,
# last modified 2021-03-23, read 2026-11-01) shows Archives paths with the CIK without leading zeroes
# (/Archives/edgar/data/51143/), while the SEC's own data files write it as ten digits with leading zeroes
# (company_tickers.json above; the submissions API's CIK##########.json, same page). The rules and the gate accept
# both spellings in a path, so a link written either way is caught; they make no claim about which spelling EDGAR
# serves.
PEER_CIKS = ("1035002", "1534701", "1534504", "1915657", "821483", "1694426", "1376139", "93410", "2115436", "34088", "48039")
# The ticker a filing's file name starts with (vlo-20251231.htm), lower case, HFC for HollyFrontier's old filings.
PEER_SLUGS = ("vlo", "psx", "pbf", "dino", "parr", "dk", "cvi", "cvx", "xom", "hfc")

# Other repositories of the same account that a document may name (not this one and not the skills repository).
OTHER_REPOS = ("enterprise-people-graph",)

# The projection's fixed prefixes plus n10s's schema and SHACL prefixes: a double underscore after any of these is
# the graph's separator (rule 11 rewrites it, the gate fails on it).
GRAPH_PREFIXES = ("core", "orgm", "kpi", "pop", "party", "dp", "vs", "sys", "lane", "mkt", "plc", "auth", "con",
                  "skos", "dcterms", "org", "rdfs", "owl", "rdf", "prov", "oeo", "n4sch", "sh", "tv", "tech")
# The prefixes the n10s fixture files may write with the double separator (the skill's library example and the
# pipeline's own test of the names it renames): a closed list, read from those files. Every other prefix, this
# ontology's module prefixes included, fails the gate even there.
FIXTURE_PREFIXES = ("lib", "my", "app", "n4sch", "ns", "nope", "rdf", "rdfs", "skos", "org", "dcterms")
