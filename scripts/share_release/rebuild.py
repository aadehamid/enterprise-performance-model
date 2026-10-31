#!/usr/bin/env python3
"""Rebuild inside the exported release, so every hash in it is true of the release (plan step 4).

    python3 scripts/share_release/rebuild.py --release <exported folder> --epm <main checkout>

In order: freeze the process map at the commits the core builders read (from the main checkout's Git into
the release's release/frozen/); set EPM_SHARE_RELEASE so pins move to the newest set; rebuild every module's
source Turtle from its CSV; rebuild core 2.4.0 and each module's newest package; rebuild the catalog;
recompute the previous packages' manifest hashes; rebuild the projection manifest; rebuild the generated
pages; then verify each builder. Writes `<release>-rebuild.json` beside the release with every step's
command, exit code and output tail. Exit 1 when any step fails.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

DEPS = ["--with", "rdflib", "--with", "pyshacl", "--with", "openpyxl", "--with", "jsonschema",
        "--with", "markdown-it-py>=4,<5"]
ONT = "business_architecture/ontology"
SOURCE_BUILDERS = [
    ("authority", "build_source_tiers.py"), ("apqc", "build_apqc_elements.py"), ("population", "build_population.py"),
    ("kpi", "build_measures.py"), ("organization", "build_roles.py"), ("organization", "build_assignments.py"),
    ("party", "build_party.py"), ("system", "build_systems.py"), ("data-product", "build_data_products.py"),
    ("data-product", "build_pricing.py"), ("value-stream", "build_value_streams.py"), ("lane", "build_lanes.py"),
    ("market-data", "build_market_data.py"),
]
# Each module after the ones it requires (build_module.py's depends_on).
MODULE_ORDER = ["organization", "kpi", "system", "party", "ref-mpc", "data-product", "value-stream", "lane",
                "market-data", "integration"]


class Rebuild:
    def __init__(self, release, epm):
        self.release, self.epm = os.path.abspath(release), os.path.abspath(epm)
        self.steps = []
        self.env = dict(os.environ, EPM_SHARE_RELEASE="1", PYTHONDONTWRITEBYTECODE="1")
        for k in list(self.env):
            if k.startswith("GIT_"):
                del self.env[k]

    def run(self, name, args, cwd, deps=True):
        cmd = ["uv", "run", "-q", "--no-project", *DEPS, "python3", *args] if deps else args
        r = subprocess.run(cmd, cwd=os.path.join(self.release, cwd), env=self.env, capture_output=True, text=True)
        tail = (r.stdout + r.stderr)[-1500:]
        self.steps.append({"step": name, "cwd": cwd, "command": " ".join(args), "returncode": r.returncode, "tail": tail})
        if r.returncode != 0:
            raise SystemExit(f"{name} failed in {cwd}: {' '.join(args)}\n{tail}")
        return r

    def freeze(self):
        self.run("freeze", ["frozen_sources.py", "--freeze", "--repo", self.epm], f"{ONT}/release")

    def previous_hashes(self):
        """The history folder's manifests name the files' hashes as rewritten; nothing else in them changes."""
        base = os.path.join(self.release, ONT, "releases", "previous")
        done = []
        for module in sorted(os.listdir(base)):
            for version in sorted(os.listdir(os.path.join(base, module))):
                folder = os.path.join(base, module, version)
                mpath = os.path.join(folder, "manifest.json")
                if not os.path.isfile(mpath):
                    continue
                with open(mpath) as f:
                    manifest = json.load(f)
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
                       if f.startswith("test_") and f.endswith(".py") and "__pycache__" not in root)
        with open(os.path.join(HERE, "templates", "check.sh")) as f:
            text = f.read().replace("{{TEST_FILES}}", " \\\n".join("  " + t for t in tests))
        out = os.path.join(self.release, "scripts", "check.sh")
        with open(out, "w") as f:
            f.write(text)
        os.chmod(out, 0o755)
        self.steps.append({"step": "check script", "tests": len(tests), "returncode": 0})

    def all(self):
        self.freeze()
        self.check_script()
        for folder, script in SOURCE_BUILDERS:
            self.run(f"source {folder}/{script}", [script, "--write"], f"{ONT}/{folder}")
        self.run("core 2.4.0", ["build_core_2_4.py", "--write"], f"{ONT}/release")
        for m in MODULE_ORDER:
            self.run(f"module {m}", ["build_module.py", m, "--write"], f"{ONT}/release")
        self.run("catalog", ["build_catalog.py", "--write"], f"{ONT}/release")
        self.previous_hashes()
        self.run("projection manifest", ["pipeline.py", "build"], f"{ONT}/projection")
        self.run("pages", ["scripts/build_docs_html.py"], ".")
        if os.path.exists(os.path.join(self.release, "skills", "scripts", "build_playbook_html.py")):
            self.run("playbook pages", ["skills/scripts/build_playbook_html.py"], ".")
        # Verify: every builder agrees with what it wrote.
        for folder, script in SOURCE_BUILDERS:
            self.run(f"verify {folder}/{script}", [script, "--verify"], f"{ONT}/{folder}")
        self.run("verify core 2.4.0", ["build_core_2_4.py", "--verify"], f"{ONT}/release")
        for m in MODULE_ORDER:
            self.run(f"verify module {m}", ["build_module.py", m, "--verify"], f"{ONT}/release")
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
    a = ap.parse_args(argv)
    rb = Rebuild(a.release, a.epm)
    try:
        rb.all()
    finally:
        rb.write_report()
    print(f"rebuilt: {len(rb.steps)} steps, all passed")


if __name__ == "__main__":
    main()
