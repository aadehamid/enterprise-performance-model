"""Which modules a change to one module re-releases, in the order to release them.

    python3 dependents.py kpi     # kpi first, then each module that depends on it, each after what it requires

A released package names the versions it requires, so a new version of a module means a new version of every module
that depends on it, directly or not. core counts as required by all that name it.
"""
import argparse
import sys

import build_module as bm


def dependents(module, modules=None):
    """`module` (when it is in the table), then every module that depends on it, each after what it requires."""
    modules = bm.MODULES if modules is None else modules
    reached = {module}
    while True:
        more = {m for m, spec in modules.items() if m not in reached and reached & set(spec["depends_on"])}
        if not more:
            break
        reached |= more
    ordered = []
    pending = sorted(m for m in reached if m in modules)
    while pending:
        ready = [m for m in pending if not (set(modules[m]["depends_on"]) & (set(pending) - {m}))]
        if not ready:
            raise SystemExit(f"a dependency cycle among {pending}")
        ordered += ready
        pending = [m for m in pending if m not in ready]
    return ordered


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("module")
    a = ap.parse_args(argv)
    if a.module != "core" and a.module not in bm.MODULES:
        sys.exit(f"{a.module} is not a module: {', '.join(['core'] + sorted(bm.MODULES))}")
    print("\n".join(dependents(a.module)))


if __name__ == "__main__":
    main()
