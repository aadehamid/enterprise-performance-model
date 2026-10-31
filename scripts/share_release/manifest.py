"""What the share release holds: the allowlist of paths from this repository and the skills repository,
and the renames applied to paths. Everything not listed stays out (EPM-DEC-001-0110 and its amendment;
the step 1 inventory of 2026-10-31).

A rule is a glob relative to the repository root. `ship` copies; `out` leaves the path out even when an
earlier glob matched it. Rules are applied in order; the last matching rule wins.
"""
import fnmatch
import os

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
    # step4/target-report and label-report are Step 4 review outputs; their tests import the gate's helpers, so they stay out.
    ("ship", f"{ONT}/step4/playbook/ontology-worklog.md"),
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
