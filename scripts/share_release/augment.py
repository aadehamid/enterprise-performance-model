"""The augment folder: files kept outside the repository that the cut adds to the release, and the logical-model
package built from them inside the release (EPM-DEC-001-0113, decisions 2, 6 and 10).

    cut.sh ... --augment <folder> --approval <answers file> --approval-words "<the approving sentence>"

The folder holds, for each logical model, `<slug>.ttl` (ER Studio's export) and `<slug>.links.csv` (its links file,
in the columns `build_logical_model.py` reads). Any other file in it is ignored. The folder may be outside the
repository (the customer model's export sits in a gitignored folder) or inside it (a model kept in main later).

What the cut does with it, in order:
- `export.py` copies each model's two files into the release through the rewrite rules, as it copies every text
  file: the export lands as `logical-model/models/<slug>.erstudio.ttl` and the links file as
  `logical-model/models/<slug>.links.csv`. The rules move the module's own IRIs and every link target from
  w3id.org/lsc to w3id.org/mpc; ER Studio's namespace (https://www.erstudio.com/semanticmodel/) is not ours and no
  rule touches it.
- `rebuild.py` runs the release's own `build_logical_model.py` on the staged files, against the release's newest
  packages, so the layer links to the release's IRIs; registers `logical-model` as a released module in every place
  the release lists its modules (REGISTRATION below), each patch failing when its anchor is not found; and builds
  the package `releases/logical-model/1.0.0/` with the release's `build_module.py`: the module's vocabulary as
  `logical-model.ttl`, its shapes, each model's two graphs as they are, `catalog.ttl`, `CHANGELOG.md` and
  `manifest.json`, which lists each outside file with its path relative to the folder and its SHA-256. `release.json`
  lists them too. After the catalog is built, it rewrites every figure of the guide and the walkthrough that states
  the release set (FIGURES) to the figure of the release tree (release_figures).
- The leak gate and the release's own checks then run on everything, the built module included.

The package names the decision owner's approval: the cut refuses `--augment` until `--approval` names the saved
answers file, in the main checkout's answers folder, whose text holds the `--approval-words`, which must approve logical-model 1.0.0 by name (EPM-DEC-001-0113,
decision 10: the module's 1.0.0 waits for the decision owner's approval from one page).
"""
import datetime
import hashlib
import json
import os
import re

import manifest
import rules

ONT = "business_architecture/ontology"
MODULE, VERSION = "logical-model", "1.0.0"
MODELS = f"{ONT}/logical-model/models"  # where the staged inputs and the built graphs sit in the release
ANSWERS = "step4/review-evidence/decision-owner-answers"  # relative to the ontology folder, as every module's approval
ER_STUDIO = "https://www.erstudio.com/semanticmodel/"
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
         "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty")


class AugmentError(SystemExit):
    pass


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def models(folder):
    """[(slug, export path, links path)] for every model in the folder, by slug. Fails on an export without its links
    file or the reverse, on a slug the builder would refuse, and on a folder with no model."""
    if not os.path.isdir(folder):
        raise AugmentError(f"--augment {folder}: not a folder")
    names = set(os.listdir(folder))
    exports = {n[:-len(".ttl")] for n in names if n.endswith(".ttl") and not n.endswith((".erstudio.ttl", ".layer.ttl"))}
    links = {n[:-len(".links.csv")] for n in names if n.endswith(".links.csv")}
    problems = [f"{s}.ttl has no {s}.links.csv beside it" for s in sorted(exports - links)]
    problems += [f"{s}.links.csv has no {s}.ttl beside it" for s in sorted(links - exports)]
    problems += [f"{s}: a model's name must be lower-case words joined by hyphens" for s in sorted(exports & links) if not SLUG.match(s)]
    if not exports & links and not problems:
        problems.append("it holds no model: a model is <slug>.ttl with <slug>.links.csv beside it")
    if problems:
        raise AugmentError(f"--augment {folder}: " + "; ".join(problems))
    return [(s, os.path.join(folder, f"{s}.ttl"), os.path.join(folder, f"{s}.links.csv")) for s in sorted(exports & links)]


def inputs(folder):
    """Each file the cut reads from the folder: its path relative to the folder and its SHA-256. Never the folder's
    own path, which names a folder of the machine the cut ran on."""
    out = []
    for _, export, links in models(folder):
        for path in (export, links):
            out.append({"path": os.path.relpath(path, folder), "sha256": sha256(path)})
    return out


# An approval names the release it approves (Codex's round 1: an unrelated "go ahead" must not pass the gate).
APPROVES = re.compile(r"\bapprov\w*\b.*\blogical-model\b.*\b1\.0\.0\b", re.I | re.S)
REFUSES = re.compile(r"\b(?:not|don't|do not|no|hold|reject\w*|wait)\b", re.I)


def approval(epm, path, words):
    """(the approval file relative to the ontology folder, the words) once the decision owner's approval is given:
    the file is a saved answers file of the main checkout and its body holds the words. Raises with what is missing."""
    hint = ("logical-model 1.0.0 waits for the decision owner's approval (EPM-DEC-001-0113, decision 10). Record it "
            f"in a saved answers file under business_architecture/ontology/{ANSWERS}/ of the main checkout, then cut "
            "again with --approval <that file> --approval-words \"<the sentence that approves it>\".")
    if not path or not words:
        raise AugmentError(f"refusing --augment without the approval: {hint}")
    folder = os.path.realpath(os.path.join(epm, ONT, ANSWERS))
    real = os.path.realpath(path)
    if os.path.dirname(real) != folder or not os.path.isfile(real):
        raise AugmentError(f"refusing --augment: --approval {path} is not a file of the answers folder. {hint}")
    with open(real, encoding="utf-8") as f:
        body = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)  # the decision owner's words sit in the body
    if not APPROVES.search(words) or REFUSES.search(words):
        raise AugmentError(f"refusing --augment: the words {words!r} do not approve logical-model 1.0.0 by name; the decision "
                           f"owner's approval names the release, such as \"approve logical-model 1.0.0\". {hint}")
    if words not in body:
        raise AugmentError(f"refusing --augment: the words {words!r} are not in the body of {os.path.basename(real)}. {hint}")
    return f"{ANSWERS}/{os.path.basename(real)}", words


def title(slug):
    """The model's title, from its slug: ER Studio's header names every export "Logical"."""
    return slug.replace("-", " ").capitalize()


def stage(release, folder, dates):
    """Copy each model's export and links file into the release through the rewrite rules. Returns {release path:
    rule counts}. The export keeps ER Studio's namespace: a rule that changed it would fail here."""
    report = {}
    os.makedirs(os.path.join(release, MODELS), exist_ok=True)
    for slug, export, links in models(folder):
        for src, name in ((export, f"{slug}.erstudio.ttl"), (links, f"{slug}.links.csv")):
            rel = f"{MODELS}/{name}"
            with open(src, encoding="utf-8") as f:
                text = f.read()
            new, counts = rules.apply(text, rel, dates)
            if text.count(ER_STUDIO) != new.count(ER_STUDIO):
                raise AugmentError(f"{name}: a rewrite rule changed ER Studio's namespace, which is never rewritten")
            with open(os.path.join(release, rel), "w", encoding="utf-8") as f:
                f.write(new)
            report[rel] = {"source": os.path.relpath(src, folder), "rules": counts}
    return report


def builder_args(slugs, check):
    """build_logical_model.py's arguments, run from the release's logical-model folder: each staged export (the copy
    is ER Studio's file, so <slug>.erstudio.ttl is rewritten as itself) and links file, into models/."""
    args = []
    for slug in slugs:
        args += ["--export", f"models/{slug}.erstudio.ttl", "--links", f"models/{slug}.links.csv", "--model", slug,
                 "--title", title(slug)]
    return ["build_logical_model.py", *args, "--out", "models", check]


def staged_slugs(release):
    folder = os.path.join(release, MODELS)
    return sorted(n[:-len(".links.csv")] for n in os.listdir(folder) if n.endswith(".links.csv"))


# ---- Registration: the places a release lists its modules, each patched with an anchor that must be found ----

def _sub(text, pattern, repl, where, flags=0, count=1):
    """Replace the anchor, which must occur exactly `count` times."""
    found = len(re.findall(pattern, text, flags))
    if found != count:
        raise AugmentError(f"registering {MODULE}: {where}: the anchor {pattern!r} was found {found} times, not {count}")
    return re.sub(pattern, repl, text, flags=flags)


def entry(slugs, approved, files, issued, dates):
    """The module's entry in build_module.py's MODULES, written as main writes every entry and then put through the
    rewrite rules, as the release's copy of build_module.py was."""
    graphs = [f"logical-model/models/{s}.{kind}.ttl" for s in slugs for kind in ("erstudio", "layer")]
    text = (
        "    # Added by the share release's cut from files kept outside the repository (EPM-DEC-001-0113): its first\n"
        "    # release, a major the decision owner approved. Each model's two graphs ship as they are (graphs); augment\n"
        "    # lists the outside files with their SHA-256.\n"
        f"    {json.dumps(MODULE)}: {{\n"
        "        \"title\": \"LSC Logical Model Module\",\n"
        "        \"description\": \"Logical data models exported from ER Studio Data Architect, each kept as two graphs: "
        "ER Studio's export as it is, in ER Studio's own namespace, and a layer of annotations that links its entities "
        "to the party, system and data-product modules. This package holds the module's vocabulary; each model's two "
        "graphs ship beside it.\",\n"
        f"        \"version\": {json.dumps(VERSION)}, \"stage\": None, \"approver\": \"The decision owner\", \"issued\": {json.dumps(issued)},\n"
        f"        \"approval\": ({json.dumps(approved[0])}, {json.dumps(approved[1])}),\n"
        "        \"parts\": [\"logical-model/vocabulary.ttl\"],\n"
        "        \"shapes\": [\"logical-model/shapes.ttl\"],\n"
        f"        \"graphs\": {json.dumps(graphs)},\n"
        f"        \"augment\": {json.dumps(files)},\n"
        "        \"depends_on\": [\"party\", \"system\", \"data-product\"],\n"
        "        \"decisions\": [\"EPM-DEC-001-0113\"],\n"
        "    },\n")
    return rules.apply(text, f"{ONT}/release/build_module.py", dates)[0]


def changelog(slugs, issued, dates):
    models_text = ", ".join(f"`{s}`" for s in slugs)
    text = (f"# logical-model\n\n## {VERSION} ({issued})\n\n"
            f"- [major] **First release.** The module's vocabulary (`lm:LogicalModel` and four annotation properties) and "
            f"shapes, with {len(slugs)} logical model{'s' if len(slugs) != 1 else ''}: {models_text}. Each model is two "
            "graphs: ER Studio's export as it is, in ER Studio's namespace (`<model>.erstudio.ttl`), and the annotation "
            "layer that links its entities to `party`, `system` and `data-product` (`<model>.layer.ttl`). The files "
            "the models were built from are listed, with their SHA-256, under `augment` in `manifest.json` "
            "(EPM-DEC-001-0113).\n")
    return rules.apply(text, f"{ONT}/releases/{MODULE}/CHANGELOG.md", dates)[0]


def number_word(n):
    return WORDS[n] if 0 <= n < len(WORDS) else str(n)


def word_number(w):
    """"twelve" -> 12, "12" -> 12."""
    return int(w.replace(",", "")) if w.replace(",", "").isdigit() else WORDS.index(w.lower())


def patch_build_module(text, ctx):
    return _sub(text, r"\n}\n\n\nRELEASED = ", lambda m: "\n" + ctx["entry"] + "}\n\n\nRELEASED = ", "build_module.py MODULES")


def patch_test_build_module(text, ctx):
    line = (f"APPROVALS[{json.dumps(MODULE)}] = ({json.dumps(ctx['approval'][0])}, {json.dumps(ctx['approval'][1])})"
            "  # added by the share release's cut\n")
    line = rules.apply(line, f"{ONT}/release/test_build_module.py", ctx["dates"])[0]
    return _sub(text, r"\n\n\ndef approval_holds\(", lambda m: "\n" + line + "\n\ndef approval_holds(", "test_build_module.py APPROVALS")


def patch_pipeline(text, ctx):
    text = _sub(text, r"\)\]\nINPUTS = ", lambda m: f'), ("{MODULE}", "{VERSION}")]\nINPUTS = ', "pipeline.py PACKAGES")
    text = _sub(text, r"(OWN = tuple\(MODULES_NS \+ m \+ \"/\" for m in \([^)]*?)\)\)",
                lambda m: m.group(1) + f', "{MODULE}"))', "pipeline.py OWN")
    return _sub(text, r"\n    \"skos\": str\(SKOS\)", lambda m: f"\n    \"lm\": MODULES_NS + \"{MODULE}/\",\n    \"skos\": str(SKOS)",
                "pipeline.py PREFIXES")


def patch_test_pipeline(text, ctx):
    return _sub(text, r"(self\.assertEqual\(pl\.PACKAGES, \[[^\]]*?)\)\]\)", lambda m: m.group(1) + f'), ("{MODULE}", "{VERSION}")])',
                "test_pipeline.py's pinned PACKAGES")


def patch_epm_config(text, ctx):
    cfg = json.loads(text)
    base = cfg["own_namespaces"][0].split("/modules/")[0] + "/modules/"
    cfg["own_namespaces"].append(f"{base}{MODULE}/")
    prefixes = list(cfg["prefixes"].items())
    at = next(i for i, (k, _) in enumerate(prefixes) if k == "skos")
    prefixes.insert(at, ("lm", f"{base}{MODULE}/"))
    cfg["prefixes"] = dict(prefixes)
    cfg["packages"][MODULE] = VERSION
    return json.dumps(cfg, indent=2) + "\n"


def patch_test_epm_facts(text, ctx):
    import ast
    m = re.search(r"(def test_module_map_lists_the_released_modules\(\):\n    names = .*\n    assert names == )(\[.*?\])\n", text, re.S)
    if not m:
        raise AugmentError(f"registering {MODULE}: test_epm_facts.py's module list was not found")
    names = sorted(ast.literal_eval(m.group(2)) + [MODULE])
    return text[:m.start(2)] + "[" + ", ".join(f'"{n}"' for n in names) + "]" + text[m.end(2):]


def patch_test_release_package_shapes(text, ctx):
    # The module's 1.0.0 is its only release, so it has no previous package.
    def less(m):
        return f"2 * len(newest) - {int(m.group(1) or 0) + 1}"
    return _sub(text, r"2 \* len\(newest\)(?: - (\d+))?", less, "test_release_package_shapes.py's count")


def patch_modules_md(text, ctx):
    row = (f"| `{MODULE}` | Logical data models and their links to the ontology | `logical-model/vocabulary.ttl`; each model's "
           "two graphs ship beside it as they are | `logical-model/shapes.ttl` |\n")
    text = _sub(text, r"(\n\| `[a-z-]+` \|[^\n]*\n)(\nThe module builder writes each `catalog\.ttl`)",
                lambda m: m.group(1) + row + m.group(2), "MODULES.md, the table of the three files of each package")
    note = (f" In this release, `{MODULE}` is released as `{VERSION}`, with the models listed in its `CHANGELOG.md`; "
            "its `example/` model is test data and ships in no package.")
    return _sub(text, r"(\nSome source folders are not packages of their own\.[^\n]*)\n", lambda m: m.group(1) + note + "\n",
                "MODULES.md, the folders that are not packages")


def patch_module_readme(text, ctx):
    status = (f"**Status:** released in this release as `{MODULE} {VERSION}`, with {len(ctx['slugs'])} logical model"
              f"{'s' if len(ctx['slugs']) != 1 else ''}: {', '.join('`' + s + '`' for s in ctx['slugs'])}. Each model's export "
              "and links file are in `models/`, with the two graphs the builder made from them; "
              "`../releases/logical-model/` holds the package. The made-up example stays test data.\n")
    return _sub(text, r"\n\*\*Status:\*\*[^\n]*\n", lambda m: "\n" + status, "logical-model/README.md, its status")


def patch_open_items(text, ctx):
    return _sub(text, r"\n\| Releasing the logical-model module \|[^\n]*\n", lambda m: "\n", "OPEN-ITEMS.md, the logical-model row")


# ---- Figures: every statement of the guide and the walkthrough that names the release set ----
#
# Each figure that states the release set as it is (module counts, the catalog, the releases folder, the total, the
# graphs a store holds from the releases) is rewritten to the figure of this release's tree, computed by
# release_figures after the package and the catalog are built; the figure it replaces stays beside it as history where
# the sentence dates it. Each edit is anchored and stops the cut when its anchor is missing. test_augment.py's
# FIGURE_CLASSES lists every figure of the two pages, with this rewrite or the reason it stays.

def release_figures(release):
    """The figures the guide and walkthrough state, from the release tree as built: the modules and their newest
    releases (epm_facts.py's module list), the triples of the newest releases loaded together, the catalog's
    datasets, the releases folder's version folders, files and size, and the named graphs and triples the stores
    load from the releases (each newest module's Turtle and, beside it, each release graph epm-run.json names)."""
    import importlib
    import sys
    import rdflib
    releases = os.path.join(release, ONT, "releases")
    sys.path.insert(0, os.path.join(release, "scripts"))
    try:
        facts = importlib.import_module("epm_facts")
        mods = facts.module_releases(releases, os.path.join(release, ONT, "release", "build_module.py"))
    finally:
        sys.path.pop(0)
        sys.modules.pop("epm_facts", None)
    whole = rdflib.Graph()
    with open(os.path.join(release, ONT, "projection", "skill-run", "epm-run.json"), encoding="utf-8") as f:
        release_graphs = json.load(f)["release_graphs"]
    graphs = quads = 0
    for m in mods:
        folder = os.path.join(releases, m["module"], m["newest"])
        whole += rdflib.Graph().parse(os.path.join(folder, f"{m['module']}.ttl"), format="turtle")
        for name in [m["module"], *release_graphs]:
            quads += len(rdflib.Graph().parse(os.path.join(folder, f"{name}.ttl"), format="turtle"))
            graphs += 1
    catalog = rdflib.Graph().parse(os.path.join(releases, "catalog.ttl"), format="turtle")
    versions = files = size = 0
    for root, dirs, names in os.walk(releases):
        versions += sum(1 for d in dirs if re.fullmatch(r"\d+\.\d+\.\d+", d))
        files += len(names)
        size += sum(os.path.getsize(os.path.join(root, n)) for n in names)
    lm = next((m for m in mods if m["module"] == MODULE), {})  # none in main's tree
    return {"modules": len(mods), "total": len(whole), "triples": lm.get("triples"), "requires": lm.get("requires"),
            "catalog": len(set(catalog.objects(None, rdflib.URIRef("http://www.w3.org/ns/dcat#dataset")))),
            "versions": versions, "files": files, "mb": round(size / 1e7) * 10,
            "graphs_per_module": 1 + len(release_graphs), "graphs": graphs, "quads": quads}


def _edits(text, page, edits):
    for where, pattern, repl, *opts in edits:
        text = _sub(text, pattern, repl, f"{page}, {where}", *opts)
    return text


def _added():
    return f"{MODULE} {VERSION}"


def patch_guide(text, ctx):
    n, w, added = ctx["modules"], number_word(ctx["modules"]), _added()
    total = f"{ctx['total']:,}"
    card = (f'\n<section class="mod" id="m-{MODULE}">\n<h3>{MODULE} <span class="pill">{VERSION}</span> '
            f'<span class="pill">{ctx["triples"]:,} triples</span></h3>\n<div class="two">\n<div>\n'
            "<p><strong>Holds</strong> logical data models exported from ER Studio Data Architect, each as two graphs: "
            "ER Studio's export as it is, in ER Studio's own namespace, and a layer of annotations that says which "
            "model each entity belongs to, which system its data comes from, which <code>party</code> concept it "
            "describes and which <code>data-product</code> table builds it. The triple count is the module's "
            "vocabulary; each model's two graphs ship beside it in the package.</p>\n"
            f"<p><strong>In this release:</strong> {', '.join('<code>' + s + '</code>' for s in ctx['slugs'])}.</p>\n"
            "</div>\n</div>\n"
            f"<p class=\"note\">Links: <code>lm:sourceSystem</code>, <code>lm:describes</code> and <code>lm:implementedBy</code> "
            f"from an ER Studio entity to the ontology. Requires {ctx['requires']}.</p>\n</section>\n")
    row = f'<tr><td>{MODULE}</td><td class="n" data-k="Newest">{VERSION}</td><td data-k="Requires">{ctx["requires"]}</td></tr>\n'
    return _edits(text, "the guide", [
        ("the title's module count", r"(why it is split into )\w+( modules)", lambda m: f"{m.group(1)}{w}{m.group(2)}"),
        ("the snapshot notice", r"(the store figures are still those of the last load, of the \w+ earlier modules\.)",
         lambda m: (f"{m.group(1)} The module and triple counts on this page also count <code>{MODULE}</code> {VERSION}, added in this "
                    "release, which the module map does not draw; the copy section's and the catalog's figures are "
                    "those of this release's own <code>releases/</code> folder.")),
        ("the module count", r'(<div class="k">Modules</div><div class="v">)\d+(</div>)', lambda m: f"{m.group(1)}{n}{m.group(2)}"),
        ("the total", r'(<div class="k">Triples</div><div class="v">)[\d,]+(</div><div class="d">in the )\w+( newest releases together)',
         lambda m: f"{m.group(1)}{total}{m.group(2)}{w}{m.group(3)}"),
        ("why modules", r"(It is )\w+( modules because)", lambda m: f"{m.group(1)}{w}{m.group(2)}"),
        ("the module map's lead", r"(every one except <code>ref-mpc</code>) and (<code>technical-graph</code>);",
         lambda m: f"{m.group(1)}, {m.group(2)} and <code>{MODULE}</code>;"),
        ("the module map's caption", r"(<figcaption>Teal marks <code>kpi</code>.*?)(</figcaption>)",
         lambda m: f"{m.group(1)} <code>{MODULE}</code> {VERSION}, added in this release, is not drawn; it requires {ctx['requires']}.{m.group(2)}", re.S),
        ("the walk's total", r"(It runs over the )\w+( newest releases loaded together, )([\d,]+)( triples since )([^;(]*?) \((\d{4}-\d{2}-\d{2}); ([^)]*)\)",
         lambda m: (f"{m.group(1)}{w}{m.group(2)}{total}{m.group(4)}{added}, in this release ({m.group(3)} since "
                    f"{m.group(5)}, {m.group(6)}; {m.group(7)})")),
        ("the script's printout", r"(which prints )([\d,]+)( triples and \d+ rows) \(([^)]*)\)",
         lambda m: f"{m.group(1)}{total}{m.group(3)} in this release ({m.group(2)} before {added}; {m.group(4)})"),
        ("the module cards", r'\n<h2 id="questions">', lambda m: card + m.group(0)),
        ("the stores' master copy", r"(as Turtle: )(\w+)( modules since )([^(]*?) \((\d{4}-\d{2}-\d{2})\)(, and the stores hold)",
         lambda m: f"{m.group(1)}{w}{m.group(3)}{added}, in this release ({m.group(2)} since {m.group(4)}, {m.group(5)}){m.group(6)}"),
        ("the copy bundle", r"(In all: )(\d+)( files and three links\. That is )(\d+)( release files, )(\d+)( pages and data files to understand it, and )(\d+)( files)",
         lambda m: (f"{m.group(1)}{ctx['files'] + int(m.group(6)) + int(m.group(8))}{m.group(3)}{ctx['files']}{m.group(5)}"
                    f"{m.group(6)}{m.group(7)}{m.group(8)}{m.group(9)}")),
        ("the copy diagram's label", r"(the releases folder with )\w+( modules)", lambda m: f"{m.group(1)}{w}{m.group(2)}"),
        ("the copy diagrams", r"\d+ modules · \d+ versions · \d+ files",
         lambda m: f"{n} modules · {ctx['versions']} versions · {ctx['files']} files", 0, 2),
        ("the releases folder", r"(\d+) modules, (\d+) version folders and (\d+) files, about \d+ MB \(since ([^)]*)\)",
         lambda m: (f"{n} modules, {ctx['versions']} version folders and {ctx['files']} files, about {ctx['mb']} MB, in this "
                    f"release ({m.group(1)} modules, {m.group(2)} version folders and {m.group(3)} files on main since {m.group(4)})")),
        ("the catalog's packages", r"(The DCAT catalog of all )\d+( released packages)",
         lambda m: f"{m.group(1)}{ctx['catalog']}{m.group(2)} in this release"),
        ("the whole-ontology total", r"(for the whole ontology \()[\d,]+( triples\))", lambda m: f"{m.group(1)}{total}{m.group(2)}"),
        ("the table of newest versions", r"(The newest version of each module, from its manifest\.(?:(?!</tbody>).)*?)(</tbody>)",
         lambda m: m.group(1) + row + m.group(2), re.S),
    ])


def patch_walkthrough(text, ctx):
    n, w, added = ctx["modules"], number_word(ctx["modules"]), _added()
    per = number_word(ctx["graphs_per_module"])
    row = (f"      <tr><td><code>{MODULE}</code></td><td>Logical data models exported from ER Studio Data Architect, each as "
           "two graphs: ER Studio's export as it is and a layer of annotations; added in this release</td><td><code>"
           f"{MODULE}/README.md</code>, <code>build_logical_model.py</code></td><td><code>sourceSystem</code> to system, "
           "<code>describes</code> to party, <code>implementedBy</code> to data-product</td></tr>\n")
    return _edits(text, "the walkthrough", [
        ("the overview's modules", r'(font-weight="700">)\d+( modules</text>)', lambda m: f"{m.group(1)}{n}{m.group(2)}"),
        ("the overview's catalog", r'(font-weight="700" fill="#fff">)\d+( releases</text>)', lambda m: f"{m.group(1)}{ctx['catalog']}{m.group(2)}"),
        ("the module map's caption", r"(is not drawn \(the guide's module map shows it\)\.)",
         lambda m: f"{m.group(1)} <code>{MODULE}</code> {VERSION}, added in this release, is drawn in neither map."),
        ("the module table", r"(\n      <tr><td><code>technical-graph</code></td>[^\n]*\n)", lambda m: m.group(1) + row),
        ("the CI's packages", r"(checks the same )(\w+)( packages in CI) \((\w+) until ([^)]*)\)",
         lambda m: f"{m.group(1)}{w}{m.group(3)} in this release, with {added} ({m.group(2)} on main; {m.group(4)} until {m.group(5)})"),
        ("the local Neo4j's expectation", r"(printed), ([\d,]+) and ([\d,]+) on these releases, and (\d+) release records",
         lambda m: (f"{m.group(1)} ({m.group(2)} and {m.group(3)} on main's {number_word(word_number(m.group(4)))} modules, "
                    f"before {added} was added in this release), and {n} release records")),
        ("Jena's expectation", r"Expect (\d+) graphs and ([\d,]+) triples on these releases: (\w+) graphs for each of (\d+) modules \((\d+) and ([\d,]+) for the (\w+) before ([^)]*)\)",
         lambda m: (f"Expect {ctx['graphs']} graphs and {ctx['quads']:,} triples on these releases: {per} graphs for each of "
                    f"{n} modules ({m.group(1)} and {m.group(2)} for the {number_word(word_number(m.group(4)))} before {added}, "
                    f"added in this release; {m.group(5)} and {m.group(6)} for the {m.group(7)} before {m.group(8)})")),
        ("Databricks' expectation", r"this returns (\d+) and (\d+) for these releases \((\d+) and (\d+) for the (\w+) before ([^,]*), (which the table holds until its next reload)\)",
         lambda m: (f"this returns {ctx['quads']} and {ctx['graphs']} for these releases ({m.group(1)} and {m.group(2)} before "
                    f"{added}, added in this release; {m.group(3)} and {m.group(4)} for the {m.group(5)} before {m.group(6)}, "
                    f"{m.group(7)})")),
        ("the catalog's releases", r"(The catalog lists )(\d+)( releases) \((\d+) until ([^;]*); ",
         lambda m: f"{m.group(1)}{ctx['catalog']}{m.group(3)} in this release (on main, {m.group(2)} since {m.group(5)}, and {m.group(4)} until then; "),
        ("the module list", r"(Expect )(\w+)( modules, newest [^(]*)\((\w+) until ([^)]*)\)",
         lambda m: f"{m.group(1)}{w}{m.group(3)}({m.group(2)} until {added}, added in this release; {m.group(4)} until {m.group(5)})"),
        ("the record's figures", r"(after a record), ([\d,]+) nodes, ([\d,]+) relationships, ([\d,]+) triples and (\d+) inferred \(since ([^)]*)\)",
         lambda m: (f"{m.group(1)} on this release, the run's nodes, relationships and inferences over {ctx['total']:,} "
                    f"triples (on main since {m.group(6)}: {m.group(2)} nodes, {m.group(3)} relationships, {m.group(4)} "
                    f"triples and {m.group(5)} inferred)")),
    ])


def patch_check_sh(text, ctx):
    import shlex
    lines = ("(cd $ONT/release && run with_deps python build_module.py logical-model --verify)\n"
             "# The logical models of this release must equal a fresh build from their exports and links files.\n"
             f"(cd $ONT/logical-model && run with_deps python {shlex.join(builder_args(ctx['slugs'], '--verify'))})")
    return _sub(text, r"\n\(cd \$ONT/release && run with_deps python build_catalog\.py --verify\)",
                lambda m: "\n" + lines + m.group(0), "check.sh, before the catalog's verify")


# Every place the release lists its modules, in the order they are patched, before the builds (the builder, its tests
# and the documents that state no figure). The guide and the walkthrough state figures, so FIGURES patches them after
# the package and the catalog are built.
REGISTRATION = [
    (f"{ONT}/release/build_module.py", patch_build_module),
    (f"{ONT}/release/test_build_module.py", patch_test_build_module),
    (f"{ONT}/projection/pipeline.py", patch_pipeline),
    (f"{ONT}/projection/test_pipeline.py", patch_test_pipeline),
    (f"{ONT}/projection/skill-run/epm-config.json", patch_epm_config),
    ("scripts/test_epm_facts.py", patch_test_epm_facts),
    (f"{ONT}/validation/test_release_package_shapes.py", patch_test_release_package_shapes),
    (f"{ONT}/MODULES.md", patch_modules_md),
    (f"{ONT}/logical-model/README.md", patch_module_readme),
    (f"{ONT}/OPEN-ITEMS.md", patch_open_items),
]
# The pages' figures, once the package and the catalog are built (rebuild.py's augment_figures).
FIGURES = [(f"{ONT}/epm-ontology-guide.html", patch_guide), (f"{ONT}/epm-walkthrough.html", patch_walkthrough)]


def apply(release, places, ctx):
    done = []
    for rel, fn in places:
        path = os.path.join(release, rel)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        with open(path, "w", encoding="utf-8") as f:
            f.write(fn(text, ctx))
        done.append(rel)
    return done


def context(release, epm, approved, folder, dates, issued=None):
    """What the patches need: the slugs, the entry, the approval as the release writes it, the counts."""
    slugs = staged_slugs(release)
    issued = issued or datetime.date.today().isoformat()
    return {"slugs": slugs, "issued": issued, "approval": approved, "dates": dates,
            "entry": entry(slugs, approved, inputs(folder), issued, dates),
            "count_main": len(manifest.MODULES), "count_release": len(manifest.MODULES) + 1}


def write_changelog(release, ctx, dates):
    folder = os.path.join(release, ONT, "releases", MODULE)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "CHANGELOG.md"), "w", encoding="utf-8") as f:
        f.write(changelog(ctx["slugs"], ctx["issued"], dates))
