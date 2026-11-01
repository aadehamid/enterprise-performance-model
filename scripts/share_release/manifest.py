"""What the share release holds: the allowlist of paths from this repository and the skills repository,
and the renames applied to paths. Everything not listed stays out (EPM-DEC-001-0110 and its amendment;
the step 1 inventory of 2026-10-31).

A rule is a glob relative to the repository root. `ship` copies; `out` leaves the path out even when an
earlier glob matched it. Rules are applied in order; the last matching rule wins.
"""
import fnmatch
import os
import re

# The facts of one cut, in one place: the next cut edits these and nothing else in this tool.
RELEASE_NAME = "EPM 1.0"
RELEASE_BRANCH = "share/epm-1.0"  # publish.py's default branch name
CHECK_MINUTES = "10"  # how long the release's check.sh takes, for the guide: the time of the last cut's check step

# The 11 modules and the versions the release ships: (newest, previous). main at 0ad29381, 2026-10-31.
MODULES = {
    "core": ("2.4.0", "2.3.0"),
    "data-product": ("1.2.0", "1.1.0"),
    "integration": ("2.5.0", "2.4.0"),
    "kpi": ("1.3.0", "1.2.0"),
    "lane": ("1.1.0", "1.0.0"),
    "market-data": ("1.1.0", "1.0.0"),
    "organization": ("2.2.0", "2.1.0"),
    "party": ("2.1.0", "2.0.0"),
    "ref-mpc": ("1.3.0", "1.2.0"),
    "system": ("1.5.0", "1.4.0"),
    "value-stream": ("1.2.0", "1.1.0"),
}
ONT = "business_architecture/ontology"

EPM_RULES = [
    # The ontology: sources, builders, regression, projection, validation, documents.
    ("ship", f"{ONT}/*"),
    ("out", f"{ONT}/releases/*"),                       # re-added per version below
    ("out", f"{ONT}/step4/*"),                          # re-added: the frozen inputs and the checks that still run
    ("ship", f"{ONT}/step4/baseline/*"),
    ("ship", f"{ONT}/step4/canonical-facts.csv"),
    ("ship", f"{ONT}/step4/scoped-sequence/*"),
    # step4/target-report's tests import the gate's helpers, so it stays out; the label report is data core's first
    # builder reads (build_core.py's LABELS), so it ships.
    ("ship", f"{ONT}/step4/label-report/*"),
    ("out", f"{ONT}/step3c-*.md"),
    ("out", f"{ONT}/lpg-projection/*"),
    ("out", f"{ONT}/trials/*"),
    ("out", f"{ONT}/projection/skill-run/store-tests-*.md"),
    ("out", f"{ONT}/projection/LOCAL-STORES.md"),  # the stores on the author's machine, with their login files
    ("out", f"{ONT}/projection/STORE-INVENTORY.md"),  # what those stores held when last audited
    # Business process, schema, reference, domain.
    ("ship", "business_architecture/business_process/*"),
    ("ship", "business_architecture/schema/*.schema.json"),
    ("ship", "business_architecture/reference/*"),
    ("ship", "business_architecture/domain/business-glossary.md"),
    ("ship", "business_architecture/domain/data-domain-register.md"),
    ("ship", "business_architecture/domain/customer_domain_problem_statement_v0.1.md"),
    ("ship", "business_architecture/domain/market-data-and-commercial-risk-draft.md"),
    ("ship", "business_architecture/domain/decision-packages/*"),
    # Only about the agents' reviews and merges, so it cannot be made neutral (the decision's amendment of 2026-11-01).
    ("out", "business_architecture/domain/decision-packages/2026-10-14/pr-reviews-262-266-269.md"),
    # The pricing demo (the owner, 2026-10-31: only the ontology and the pricing demo). The O2C demos stay out.
    ("ship", "demos/downstream-pricing-databricks-free/*"),
    # Scripts that build or validate.
    ("ship", "scripts/check.sh"),
    ("ship", "scripts/conftest.py"),  # skips the tests of checks whose inputs do not ship
    ("ship", "scripts/epm_facts.py"),
    ("ship", "scripts/test_epm_facts.py"),
    ("ship", "scripts/build_docs_html.py"),
    ("ship", "scripts/docs_template.html"),
    ("ship", "scripts/test_docs_html.py"),
    ("ship", "scripts/test_modules_guide.py"),
    ("ship", "scripts/test_check_script.py"),
    ("ship", "scripts/test_published_figures.py"),
    # The ontology guides the owner asked to keep.
    ("ship", "best-practices/*"),
    # Generated pages are rebuilt in the export, never copied.
    ("out", "*.html"),
    ("ship", f"{ONT}/epm-walkthrough.html"),
    ("ship", f"{ONT}/epm-ontology-guide.html"),
    ("ship", f"{ONT}/projection/ontology-stores-runbook.html"),
    ("ship", "scripts/docs_template.html"),  # the page template is a source, not a generated page
    ("ship", "best-practices/*.html"),
    ("ship", "demos/downstream-pricing-databricks-free/*.html"),
]
for m, (newest, previous) in MODULES.items():
    EPM_RULES.append(("ship", f"{ONT}/releases/{m}/{newest}/*"))
    EPM_RULES.append(("ship", f"{ONT}/releases/{m}/{previous}/*"))
    EPM_RULES.append(("ship", f"{ONT}/releases/{m}/CHANGELOG*.md"))
EPM_RULES.append(("ship", f"{ONT}/releases/catalog.ttl"))

SKILLS_RULES = [
    ("ship", "skills/data/ontology/*"),
    ("ship", "skills/data/ontology-to-lpg/*"),
    ("ship", "skills/data/rdf-store/*"),
    ("ship", "skills/writing/clear-writing/*"),
    ("out", "skills/writing/clear-writing/calibration.md"),
    # The skill's upkeep: its evals and calibration read a person's own sessions, and README and SOURCES describe
    # keeping it current upstream. The release writes a short SOURCES.md of its own (templates/).
    ("out", "skills/writing/clear-writing/evals/*"),
    ("out", "skills/writing/clear-writing/scripts/*"),
    ("out", "skills/writing/clear-writing/references/calibrate.md"),
    ("out", "skills/writing/clear-writing/README.md"),
    ("out", "skills/writing/clear-writing/SOURCES.md"),
    ("ship", "scripts/build_playbook_html.py"),
    ("ship", "scripts/playbook_template.html"),
    ("ship", "scripts/test_playbook_html.py"),
]

# Where a shipped path lands in the release, when not at the same place.
PATH_RENAMES = [
    ("business_architecture/reference/downstream-peers/", "business_architecture/reference/industry-view/"),
]
# The previous release of each module moves under releases/previous/.
for m, (newest, previous) in MODULES.items():
    PATH_RENAMES.append((f"{ONT}/releases/{m}/{previous}/", f"{ONT}/releases/previous/{m}/{previous}/"))

# Skills land under skills/<name>/ in the release.
SKILLS_PREFIX = "skills/"


def disposition(path, rules):
    """'ship' or 'out' for one repository-relative path."""
    out = "out"
    for kind, pattern in rules:
        if fnmatch.fnmatchcase(path, pattern) or (pattern.endswith("/*") and path.startswith(pattern[:-1])):
            out = kind
    return out


def release_path(path, source):
    """Where a shipped path lands, relative to the release root. `source` is 'epm' or 'skills'."""
    if source == "skills":
        if path.startswith("skills/"):
            return SKILLS_PREFIX + path.split("/", 2)[2]  # skills/data/ontology/x -> skills/ontology/x
        return "skills/" + path  # scripts/build_playbook_html.py -> skills/scripts/...
    for old, new in PATH_RENAMES:
        if path.startswith(old):
            return new + path[len(old):]
    return path


def shipped(paths, rules):
    return [p for p in paths if disposition(p, rules) == "ship"]


def newest_version(versions):
    """The newest of version strings such as "1.9.0" and "1.10.0", by number, never by text (1.10.0 is newer)."""
    return max(versions, key=lambda v: tuple(int(x) for x in v.split(".")))


VERSION_FOLDER = re.compile(r"^\d+\.\d+\.\d+$")


def newest_on_disk(tree, module):
    """A module's newest version folder in a tree, by number; the newest must be a complete package (its
    manifest.json present), or the tree is wrong and this stops rather than fall back to an older one."""
    folder = os.path.join(tree, ONT, "releases", module)
    versions = [v for v in os.listdir(folder) if VERSION_FOLDER.match(v) and os.path.isdir(os.path.join(folder, v))]
    if not versions:
        raise SystemExit(f"{folder} holds no version folder")
    newest = newest_version(versions)
    if not os.path.isfile(os.path.join(folder, newest, "manifest.json")):
        raise SystemExit(f"{folder}/{newest} is the newest version but has no manifest.json: an incomplete package")
    return newest


# The release marker this tool writes at a release tree's root (rebuild.py), and the only one it accepts: exactly
# these keys, this release name, this mode text, and a date. cut.sh removes an existing output folder only when its
# marker is exactly this; every reader of release mode in this tool asks is_release(); the builders read the same
# file by its presence (build_module.SHARE_RELEASE).
RELEASE_MARKER = "release.json"
RELEASE_MODE = ("share release: each module's builder builds against the newest package of every module it requires; "
                "the Neo4j projection names labels, relationship types and property keys with one underscore")
MARKER_KEYS = ("release", "built", "mode")


def fill(text):
    """A template with this cut's facts in place."""
    return text.replace("{{RELEASE_NAME}}", RELEASE_NAME).replace("{{CHECK_MINUTES}}", CHECK_MINUTES)


def marker(built):
    """The marker's content for a release built on the given date (YYYY-MM-DD)."""
    return {"release": RELEASE_NAME, "built": built, "mode": RELEASE_MODE}


def is_tool_marker(path):
    """True only for a release.json this tool wrote: the exact keys and values of marker(), a well-formed date."""
    import json
    try:
        with open(path, encoding="utf-8") as f:
            m = json.load(f)
    except (OSError, ValueError):
        return False
    return (isinstance(m, dict) and tuple(sorted(m)) == tuple(sorted(MARKER_KEYS)) and isinstance(m.get("built"), str)
            and bool(re.match(r"^\d{4}-\d{2}-\d{2}$", m["built"])) and m == marker(m["built"]))


def is_release(tree):
    """A release tree carries this tool's marker at its root (the rebuild writes it first)."""
    return is_tool_marker(os.path.join(tree, RELEASE_MARKER))
