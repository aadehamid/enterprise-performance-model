#!/usr/bin/env python3
"""Rebuild inside the exported release, so every hash in it is true of the release (plan step 4).

    python3 scripts/share_release/rebuild.py --release <exported folder> --epm <main checkout>
        [--augment <folder> --approval <answers file> --approval-words <words>]

In order: freeze the process map at the commits the core builders read (from the main checkout's Git into
the release's release/frozen/); set EPM_SHARE_RELEASE so pins move to the newest set; rebuild every module's
source Turtle from its CSV; rebuild core 2.4.0 and each module's newest package; rebuild the catalog;
recompute the previous packages' manifest hashes; rebuild the projection manifest; rebuild the generated
pages; then verify each builder. With --augment, after the modules it builds each logical model the export staged, registers
the logical-model module in every place the release lists its modules and builds its package, and after the catalog it
rewrites the guide's and the walkthrough's figures from the release tree (augment.py). First of all it writes release.json at the tree's root, and after the freeze it adds a
dated note to the CHANGELOG of each module whose pins move, and re-pins the demo test's hash of the rewritten scenario. Writes `<release>-rebuild.json` beside the release with every step's
command, exit code and output tail. Exit 1 when any step fails.
"""
import argparse
import datetime
import hashlib
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import augment  # noqa: E402
import manifest  # noqa: E402
import procs  # noqa: E402
import scrubbing  # noqa: E402

DEPS = ["--with", "rdflib", "--with", "pyshacl", "--with", "openpyxl", "--with", "jsonschema",
        "--with", "markdown-it-py>=4,<5"]
ONT = "business_architecture/ontology"
SOURCE_BUILDERS = [
    ("authority", "build_source_tiers.py"), ("apqc", "build_apqc_elements.py"), ("population", "build_population.py"),
    ("kpi", "build_measures.py"), ("organization", "build_roles.py"), ("organization", "build_assignments.py"),
    ("party", "build_party.py"), ("system", "build_systems.py"), ("data-product", "build_data_products.py"),
    ("data-product", "build_pricing.py"), ("value-stream", "build_value_streams.py"), ("lane", "build_lanes.py"),
    ("market-data", "build_market_data.py"),
]  # technical-graph has no source builder: its vocabulary is written by hand, and its example graph is test data

# Each module after the ones it requires (build_module.py's depends_on).
MODULE_ORDER = ["organization", "kpi", "system", "party", "ref-mpc", "data-product", "value-stream", "lane",
                "market-data", "integration", "technical-graph"]


# The release's own documents and files: (template, where it lands in the release).
TEMPLATES = [("README.md", "README.md"), ("KNOWN-OPEN-ITEMS.md", "KNOWN-OPEN-ITEMS.md"), ("HOW-TO-UPDATE.md", "HOW-TO-UPDATE.md"),
             ("releases-previous-README.md", f"{ONT}/releases/previous/README.md"), ("root-conftest.py", "conftest.py"),
             ("pinned-tests.txt", "scripts/pinned-tests.txt"), ("check-pinned.sh", "scripts/check-pinned.sh"),
             ("build_core_template.py", f"{ONT}/release/build_core_template.py"),
             ("next_version.py", f"{ONT}/release/next_version.py"),
             ("clear-writing-SOURCES.md", "skills/clear-writing/SOURCES.md")]
SME = "a subject matter expert reviewing the documents"
FILE_MAP_ROW = re.compile(r"<tr><td><code>([^<]+)</code></td>.*?</tr>\n?")


def drop_dead_links(readme, tree):
    """A line of the README that links a walkthrough section goes when this tree's walkthrough has no such section."""
    path = os.path.join(tree, ONT, "epm-walkthrough.html")
    page = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            page = f.read()

    def keep(line):
        return all(f'id="{anchor}"' in page for anchor in re.findall(r"epm-walkthrough\.html#([\w-]+)", line))
    return "".join(line for line in readme.splitlines(True) if keep(line))


def prune_file_map(page, tree):
    """In the walkthrough's appendix, a row whose first cell names a path that is not in the tree goes. For a pattern
    (`folder/*`), the row stays when its folder is in the tree."""
    start = page.find('<section id="file-map"')
    if start < 0:
        return page
    end = page.index("</section>", start)

    def keep(row):
        path = html.unescape(row.group(1))
        base = path.split("*", 1)[0].rstrip("/")
        return row.group(0) if os.path.exists(os.path.join(tree, base)) else ""
    return page[:start] + FILE_MAP_ROW.sub(keep, page[start:end]) + page[end:]


def provenance_removed(manifest):
    """A manifest without its record list and approval file; the approver reads as the subject matter expert."""
    manifest = dict(manifest)
    manifest.pop("decisions", None)
    for key in ("approval", "approved_by"):
        if isinstance(manifest.get(key), dict):
            manifest[key] = {k: v for k, v in manifest[key].items() if k not in ("file", "recorded_in")}
            if "who" in manifest[key]:
                manifest[key]["who"] = SME
    return manifest


class Rebuild:
    def __init__(self, release, epm, augment_folder=None, approval=None):
        self.release, self.epm = os.path.abspath(release), os.path.abspath(epm)
        self.augment, self.approval = augment_folder, approval  # approval: (file relative to the ontology folder, words)
        self.steps = []
        self.env = dict(os.environ, EPM_SHARE_RELEASE="1", PYTHONDONTWRITEBYTECODE="1")
        for k in list(self.env):
            if k.startswith("GIT_"):
                del self.env[k]

    def run(self, name, args, cwd, deps=True, timeout=7200):
        """One builder or script, with a deadline: a stalled download or process is a failed step, not a hung cut."""
        cmd = ["uv", "run", "-q", "--no-project", *DEPS, "python3", *args] if deps else args
        try:
            r = procs.run(cmd, timeout=timeout, cwd=os.path.join(self.release, cwd), env=self.env)
            rc, tail = r.returncode, (r.stdout + r.stderr)[-1500:]
        except procs.Expired as exc:
            r, rc, tail = None, -1, f"timed out after {timeout} s: {exc.partial[-1000:]}"
        self.steps.append({"step": name, "cwd": cwd, "command": scrubbing.scrub(" ".join(args)), "returncode": rc, "tail": scrubbing.scrub(tail)})
        if rc != 0:
            raise SystemExit(f"{name} failed in {cwd}: {' '.join(args)}\n{tail}")
        return r

    def freeze(self):
        """The process map at each pinned commit, frozen from main's Git, then rewritten by the same rules as the rest."""
        self.run("freeze", ["frozen_sources.py", "--freeze", "--repo", self.epm], f"{ONT}/release")
        sys.path.insert(0, HERE)
        import export as ex
        import rules
        dates = ex.record_dates(self.epm)
        folder = os.path.join(self.release, ONT, "release", "frozen")
        counts = {}
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(folder, name)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            new, c = rules.apply(text, f"{ONT}/release/frozen/{name}", dates)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            for k, v in c.items():
                counts[k] = counts.get(k, 0) + v
        self.steps.append({"step": "rewrite frozen", "rules": counts, "returncode": 0})

    def previous_hashes(self):
        """The history folder's manifests name the files' hashes as rewritten, and lose their provenance fields (the
        record list, the approval file, where the approval was recorded), keeping who approved as the subject matter
        expert (EPM-DEC-001-0110, amendment: the manifests' decisions and approval.file come out). The newest
        packages' manifests are written by the builders in release mode the same way."""
        base = os.path.join(self.release, ONT, "releases", "previous")
        done = []
        for module in sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))):
            for version in sorted(os.listdir(os.path.join(base, module))):
                folder = os.path.join(base, module, version)
                mpath = os.path.join(folder, "manifest.json")
                if not os.path.isfile(mpath):
                    continue
                with open(mpath) as f:
                    manifest = json.load(f)
                manifest = provenance_removed(manifest)
                for fname in manifest.get("files", {}):
                    with open(os.path.join(folder, fname), "rb") as f:
                        manifest["files"][fname] = hashlib.sha256(f.read()).hexdigest()
                with open(mpath, "w") as f:
                    f.write(json.dumps(manifest, indent=2) + "\n")
                done.append(f"{module}/{version}")
        self.steps.append({"step": "previous-hashes", "packages": done, "returncode": 0})

    def check_script(self):
        """The release's scripts/check.sh, from the template, with every test file in the release listed."""
        tests = sorted(os.path.relpath(os.path.join(root, f), self.release)
                       for root, dirs, files in os.walk(self.release) for f in files
                       if f.startswith("test_") and f.endswith(".py") and "__pycache__" not in root
                       and not os.path.relpath(root, self.release).startswith("skills"))  # the skills' tests run their own way
        import shlex
        import skill_checks
        with open(os.path.join(HERE, "templates", "check.sh")) as f:
            text = (f.read().replace("{{TEST_FILES}}", " \\\n".join("  " + shlex.quote(t) for t in tests))
                    .replace("{{SKILL_CHECKS}}", skill_checks.render()))
        text = manifest.fill(text)
        if self.augment:  # the logical-model package and its models' build, before the catalog's verify
            text = augment.patch_check_sh(text, {"slugs": augment.staged_slugs(self.release)})
        out = os.path.join(self.release, "scripts", "check.sh")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as f:
            f.write(text)
        os.chmod(out, 0o755)
        self.steps.append({"step": "check script", "tests": len(tests), "returncode": 0})

    def run_config(self):
        """The skill driver's run configuration asks for single underscores in the kept graph (EPM-DEC-001-0110)."""
        path = os.path.join(self.release, ONT, "projection", "skill-run", "epm-run.json")
        with open(path) as f:
            cfg = json.load(f)
        cfg["separator"] = "_"
        with open(path, "w") as f:
            f.write(json.dumps(cfg, indent=2) + "\n")
        self.steps.append({"step": "run config: separator", "returncode": 0})

    def documents(self):
        """The newcomer's entry point (plan step 6): the root README, the known open items, the history folder's README,
        and the glossary's one definition of "decision owner"."""
        for name, dest in TEMPLATES:
            with open(os.path.join(HERE, "templates", name)) as f:
                text = self.augment_blocks(manifest.fill(f.read()))
            if name == "README.md":
                text = drop_dead_links(text, self.release)
            out = os.path.join(self.release, dest)
            os.makedirs(os.path.dirname(out) or self.release, exist_ok=True)
            with open(out, "w") as f:
                f.write(text)
            os.chmod(out, 0o755 if name.endswith((".sh", "next_version.py")) else 0o644)
        self.walkthrough()
        glossary = os.path.join(self.release, "business_architecture", "domain", "business-glossary.md")
        with open(glossary) as f:
            text = f.read()
        header = "| Term | Definition | Avoid | Source | Status |\n|---|---|---|---|---|\n"
        row = ("| Decision owner | The subject matter expert who reviewed the documents and recorded each decision the build "
               "relied on; the sources and documents name the role, never the person. Words attributed to \"a subject matter "
               "expert reviewing the documents\" are theirs. | \"the owner\" (also an owner of a process or of data) | "
               "The release's README, \"Names, namespaces and terms\" | Draft |\n")
        if header not in text:
            raise SystemExit("the glossary's table header is not where this expects it")
        if "| Decision owner |" not in text:
            text = text.replace(header, header + row, 1)
        with open(glossary, "w") as f:
            f.write(text)
        self.steps.append({"step": "documents", "returncode": 0})

    def walkthrough(self):
        """The release's own "How to change the ontology" replaces that section of the walkthrough (main's page keeps its
        own), and the file map's rows name only files this tree holds."""
        path = os.path.join(self.release, ONT, "epm-walkthrough.html")
        with open(path, encoding="utf-8") as f:
            page = f.read()
        with open(os.path.join(HERE, "templates", "walkthrough-change.html"), encoding="utf-8") as f:
            section = self.augment_blocks(f.read())
        page, n = re.subn(r'<section id="change".*?</section>\n?', lambda m: section, page, count=1, flags=re.S)
        if n != 1:
            raise SystemExit('the walkthrough has no section id="change"')
        page = prune_file_map(page, self.release)
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        self.steps.append({"step": "walkthrough", "returncode": 0})

    def release_marker(self):
        """release.json at the tree's root: what this tree is. The builders, the projection and the demo read release
        mode from it (build_module.SHARE_RELEASE), so no environment variable is needed to use the release. It names
        no folder of the machine it was cut on: the checkout's name could be the repository's."""
        files = {"module": augment.MODULE, "version": augment.VERSION, "files": augment.inputs(self.augment)} if self.augment else None
        marker = manifest.marker(datetime.date.today().isoformat(), files)  # the exact marker cut.sh and every reader accept
        with open(os.path.join(self.release, "release.json"), "w") as f:
            f.write(json.dumps(marker, indent=2) + "\n")
        self.steps.append({"step": "release.json", "returncode": 0})

    def changelog_notes(self):
        """Each module whose pins move to the newest set gets a dated note at the end of its CHANGELOG (the source the
        package copies), so the package's text and its manifest agree on what it was built against."""
        code = ("import json, build_module as bm\n"
                "out = {}\n"
                "for name, m in bm.MODULES.items():\n"
                "    moved = {d: [v, bm.newest_on_disk(d)] for d, v in m.get('pins', {}).items() if bm.newest_on_disk(d) != v}\n"
                "    if moved: out[name] = moved\n"
                "print(json.dumps(out))\n")
        r = self.run("moved pins", ["-c", code], f"{ONT}/release")
        moved = json.loads(r.stdout.strip().splitlines()[-1])
        today = datetime.date.today().isoformat()
        for name, deps in sorted(moved.items()):
            built = ", ".join(f"{d} {new}" for d, (old, new) in sorted(deps.items()))
            was = ", ".join(f"{d} {old}" for d, (old, new) in sorted(deps.items()))
            note = (f"\n*Share release, {today}:* in this release the newest package is built against {built}, the newest "
                    f"package of each module it requires (its `manifest.json` says so). The notes above that name "
                    f"{was} describe the pins at the time of the original release.\n")
            path = os.path.join(self.release, ONT, "releases", name, "CHANGELOG.md")
            with open(path, encoding="utf-8") as f:
                if "*Share release, " in f.read():  # a rerun of the rebuild adds no second note
                    continue
            with open(path, "a", encoding="utf-8") as f:
                f.write(note)
        self.steps.append({"step": "changelog notes", "modules": moved, "returncode": 0})

    def scenario_pin(self):
        """The demo's test pins the hash of SCENARIO.md's body; the rules rewrite that body (record references and
        agent wording; its peer names stay, as market news), so the pin is recomputed for the rewritten body and the
        test's note says so."""
        demo = os.path.join(self.release, "demos", "downstream-pricing-databricks-free")
        with open(os.path.join(demo, "SCENARIO.md"), encoding="utf-8") as f:
            body = f.read().split("-->", 1)[1]
        digest = hashlib.sha256(body.encode()).hexdigest()
        test = os.path.join(demo, "tests", "test_demo.py")
        with open(test, encoding="utf-8") as f:
            text = f.read()
        m = re.search(r'(    assert hashlib\.sha256\(body\.encode\(\)\)\.hexdigest\(\) == ")([0-9a-f]{64})(")', text)
        if not m:
            raise SystemExit("scenario pin: the demo test's pinned hash was not found")
        text = text.replace(m.group(0), m.group(1) + digest + m.group(3), 1)
        note = "    # Pinned on "
        if "Re-pinned by the share release" not in text:  # a rerun of the rebuild adds no second note
            text = text.replace(note, "    # Re-pinned by the share release's rebuild for the rewritten body (the rules rewrite the records and other "
                                  "references to the build in it).\n" + note, 1)
        with open(test, "w", encoding="utf-8") as f:
            f.write(text)
        self.steps.append({"step": "scenario pin", "was": m.group(2), "now": digest, "returncode": 0})

    def augment_blocks(self, text):
        """A template's parts that describe the augment folder's module (between <!-- augment --> and <!-- /augment -->,
        each on its own line) stay, without the marker lines, only in a release cut with --augment."""
        block = re.compile(r"^<!-- augment -->\n(.*?)^<!-- /augment -->\n", re.S | re.M)
        return block.sub(lambda m: m.group(1) if self.augment else "", text)

    def augment_module(self):
        """The logical-model package from the models the export staged (augment.py): build each model's graphs with the
        release's own builder, register the module and build its package. augment_figures patches the pages after the catalog."""
        import export as ex
        dates = ex.record_dates(self.epm)
        ctx = augment.context(self.release, self.epm, self.approval, self.augment, dates)
        lm = f"{ONT}/logical-model"
        self.run("logical models", augment.builder_args(ctx["slugs"], "--write"), lm)
        augment.write_changelog(self.release, ctx, dates)
        places = augment.apply(self.release, augment.REGISTRATION, ctx)
        self.run(f"module {augment.MODULE}", ["build_module.py", augment.MODULE, "--write", "--rebuild-released"], f"{ONT}/release")
        self.augment_ctx = ctx
        self.steps.append({"step": "augment", "models": ctx["slugs"], "registered": places, "returncode": 0})

    def augment_figures(self):
        """The guide's and the walkthrough's figures, from the release tree once the package and the catalog are built
        (augment.release_figures): each statement of the release set says this release's figure."""
        code = (f"import json, sys\nsys.path.insert(0, {HERE!r})\nimport augment\n"
                "print(json.dumps(augment.release_figures('.')))\n")
        r = self.run("figures", ["-c", code], ".")
        fig = json.loads(r.stdout.strip().splitlines()[-1])
        ctx = augment.figure_context(self.augment_ctx, fig)
        places = augment.apply(self.release, augment.FIGURES, ctx)
        self.steps.append({"step": "augment figures", "figures": fig, "patched": places, "returncode": 0})

    def all(self):
        self.release_marker()
        self.freeze()
        self.changelog_notes()
        self.scenario_pin()
        self.check_script()
        self.run_config()
        self.documents()
        # The history folder's hashes first: core 2.4.0's manifest records core 2.3.0's manifest hash.
        self.previous_hashes()
        for folder, script in SOURCE_BUILDERS:
            self.run(f"source {folder}/{script}", [script, "--write"], f"{ONT}/{folder}")
        self.run("core 2.4.0", ["build_core_2_4.py", "--write", "--rebuild-released"], f"{ONT}/release")
        for m in MODULE_ORDER:
            self.run(f"module {m}", ["build_module.py", m, "--write", "--rebuild-released"], f"{ONT}/release")
        if self.augment:
            self.augment_module()
        self.run("catalog", ["build_catalog.py", "--write"], f"{ONT}/release")
        if self.augment:
            self.augment_figures()
        self.run("projection manifest", ["pipeline.py", "build"], f"{ONT}/projection")
        self.run("pages", ["scripts/build_docs_html.py"], ".")
        if os.path.exists(os.path.join(self.release, "skills", "scripts", "build_playbook_html.py")):
            self.run("playbook pages", ["skills/scripts/build_playbook_html.py"], ".")
        # Verify: every builder agrees with what it wrote.
        for folder, script in SOURCE_BUILDERS:
            self.run(f"verify {folder}/{script}", [script, "--verify"], f"{ONT}/{folder}")
        self.run("verify core 2.4.0", ["build_core_2_4.py", "--verify"], f"{ONT}/release")
        for m in MODULE_ORDER + ([augment.MODULE] if self.augment else []):
            self.run(f"verify module {m}", ["build_module.py", m, "--verify"], f"{ONT}/release")
        if self.augment:
            self.run("verify logical models", augment.builder_args(augment.staged_slugs(self.release), "--verify"),
                     f"{ONT}/logical-model")
        self.run("verify catalog", ["build_catalog.py", "--verify"], f"{ONT}/release")
        self.run("verify projection manifest", ["pipeline.py", "build", "--verify"], f"{ONT}/projection")
        self.run("verify pages", ["scripts/build_docs_html.py", "--check"], ".")

    def write_report(self):
        with open(self.release.rstrip("/") + "-rebuild.json", "w") as f:
            json.dump(self.steps, f, indent=1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--release", required=True)
    ap.add_argument("--epm", required=True, help="the main checkout, read for the frozen process maps")
    ap.add_argument("--augment", default="", help="the folder of logical models the export staged (augment.py)")
    ap.add_argument("--approval", default="", help="with --augment: the decision owner's saved answers file")
    ap.add_argument("--approval-words", default="", help="with --augment: the words in it that approve logical-model 1.0.0")
    a = ap.parse_args(argv)
    approval = augment.approval(a.epm, a.approval, a.approval_words) if a.augment else None
    rb = Rebuild(a.release, a.epm, a.augment or None, approval)
    try:
        rb.all()
    finally:
        rb.write_report()
    print(f"rebuilt: {len(rb.steps)} steps, all passed")


if __name__ == "__main__":
    main()
