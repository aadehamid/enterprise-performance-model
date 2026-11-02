"""What is newest on disk, and what a write may overwrite. Standard library only, so any builder can import it.

A builder or test that needs "the current core" asks here, so a new core release needs no edit to them. On `main` the
newest core is the one the builders were written against, so nothing changes there.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.dirname(HERE)
CORE_BUILDER = re.compile(r"^build_core_(\d+)_(\d+)\.py$")


def newest_version(module, ontology=ONTOLOGY):
    """A module's newest version folder in releases/<module>/ that holds a manifest, by number, never by text."""
    folder = os.path.join(ontology, "releases", module)
    versions = [v for v in os.listdir(folder)
                if re.match(r"^\d+\.\d+\.\d+$", v) and os.path.isfile(os.path.join(folder, v, "manifest.json"))]
    if not versions:
        raise FileNotFoundError(f"{folder} holds no released package")
    return max(versions, key=lambda v: tuple(int(x) for x in v.split(".")))


def core_file(name="core.ttl", ontology=ONTOLOGY):
    """A file of the newest core package."""
    return os.path.join(ontology, "releases", "core", newest_version("core", ontology), name)


def core_builder(release=HERE):
    """The module name of the newest numbered core builder, build_core_<major>_<minor>; importing it gives its VERSION
    and BASE. A patch of core is a new builder too, named for its major and minor."""
    found = [(int(m.group(1)), int(m.group(2)), f) for f in os.listdir(release) for m in [CORE_BUILDER.match(f)] if m]
    if not found:
        raise FileNotFoundError(f"{release} holds no build_core_<major>_<minor>.py")
    return max(found)[2][:-3]


def refuse_overwrite(out, files, what, rebuild_released=False):
    """Stop before a write changes a released package: a released package never changes, so a change needs a new
    version. A package that does not exist yet, or a write that changes nothing, passes. `--rebuild-released` is for a
    rebuild of the whole set from its sources, which changes what the packages are built from."""
    if rebuild_released or not os.path.isfile(os.path.join(out, "manifest.json")):
        return
    changed = []
    for name, text in sorted(files.items()):
        path = os.path.join(out, name)
        if not os.path.exists(path):
            changed.append(name)
            continue
        with open(path, encoding="utf-8") as f:
            if f.read() != text:
                changed.append(name)
    if changed:
        raise SystemExit(f"{what} is already released and this build differs in {', '.join(changed)}. A released package "
                         "never changes: raise the version first, then write. To restore what the sources say, without "
                         "a new version, pass --rebuild-released.")
