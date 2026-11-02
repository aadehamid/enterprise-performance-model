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
  lists them too.
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

def _sub(text, pattern, repl, where, flags=0):
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise AugmentError(f"registering {MODULE}: {where}: the anchor {pattern!r} was not found")
    return new


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


def recount(text, old, new):
    """"eleven modules" -> "twelve modules", "the eleven newest releases", "the same eleven packages"."""
    return re.sub(rf"\b{number_word(old)}\b(?=(?: newest)? (?:modules|releases|packages)\b)", number_word(new), text)


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


def patch_guide(text, ctx):
    old, new = ctx["count_main"], ctx["count_release"]
    text = _sub(text, rf'(<div class="k">Modules</div><div class="v">){old}(</div>)', lambda m: f"{m.group(1)}{new}{m.group(2)}",
                "the guide's module count")
    text = recount(text, old, new)
    total = re.search(r'<div class="k">Triples</div><div class="v">([\d,]+)</div>', text)
    if not total:
        raise AugmentError(f"registering {MODULE}: the guide's total was not found")
    old_total, new_total = total.group(1), f"{ctx['total']:,}"
    # Each statement of the total is rewritten on purpose (the Cursor HOLD on #474): the stat, the script's printout and
    # the whole-ontology table name today's total; the "since" sentence keeps the earlier total as its history.
    text = _sub(text, r'(<div class="k">Triples</div><div class="v">)[\d,]+(</div>)',
                lambda m: f"{m.group(1)}{new_total}{m.group(2)}", "the guide's total")
    text = _sub(text, rf"(which prints ){re.escape(old_total)}( triples)", lambda m: f"{m.group(1)}{new_total}{m.group(2)}",
                "the guide's script printout")
    text = _sub(text, rf"(for the whole ontology \(){re.escape(old_total)}( triples\))",
                lambda m: f"{m.group(1)}{new_total}{m.group(2)}", "the guide's whole-ontology total")
    text = _sub(text, rf"(loaded together, ){re.escape(old_total)}( triples since )",
                lambda m: f"{m.group(1)}{new_total}{m.group(2)}{MODULE} {VERSION} (in this release; {old_total} since ",
                "the guide's dated total")
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
    text = _sub(text, r'\n<h2 id="questions">', lambda m: card + '\n<h2 id="questions">', "the guide's module cards")
    row = (f'<tr><td>{MODULE}</td><td class="n" data-k="Newest">{VERSION}</td><td data-k="Requires">{ctx["requires"]}</td></tr>\n')
    return _sub(text, r"(The newest version of each module, from its manifest\.(?:(?!</tbody>).)*?)(</tbody>)",
                lambda m: m.group(1) + row + m.group(2), "the guide's table of newest versions", re.S)


def patch_walkthrough(text, ctx):
    new = recount(text, ctx["count_main"], ctx["count_release"])
    if new == text:
        raise AugmentError(f"registering {MODULE}: the walkthrough states no module count")
    return new


def patch_check_sh(text, ctx):
    import shlex
    lines = ("(cd $ONT/release && run with_deps python build_module.py logical-model --verify)\n"
             "# The logical models of this release must equal a fresh build from their exports and links files.\n"
             f"(cd $ONT/logical-model && run with_deps python {shlex.join(builder_args(ctx['slugs'], '--verify'))})")
    return _sub(text, r"\n\(cd \$ONT/release && run with_deps python build_catalog\.py --verify\)",
                lambda m: "\n" + lines + m.group(0), "check.sh, before the catalog's verify")


# Every place the release lists its modules, in the order they are patched. The first group comes before the builds
# (the builder, its tests and the documents that need no figure); the guide needs the built package's figures.
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
    (f"{ONT}/epm-walkthrough.html", patch_walkthrough),
]
FIGURES = [(f"{ONT}/epm-ontology-guide.html", patch_guide)]


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
