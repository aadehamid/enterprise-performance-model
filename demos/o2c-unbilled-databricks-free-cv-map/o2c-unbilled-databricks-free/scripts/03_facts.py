#!/usr/bin/env python3
"""03_facts.py — run sql/02_facts.sql with {{catalog}} / {{schema}} substituted.

Builds dim_* + fct_unbilled (certified population). Expect 12 / $179,934.00.
Demo 2 / Track B. Not MetricFlow.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import PACK_ROOT, connect, run_script, settings, substitute  # noqa: E402


def main() -> None:
    cfg = settings()
    path = PACK_ROOT / "sql" / "02_facts.sql"
    sql_text = substitute(path.read_text(encoding="utf-8"), cfg)
    print(f"Running {path} against {cfg.fq}")

    with connect(cfg) as conn:
        with conn.cursor() as cur:
            run_script(cur, sql_text)

    print("\nFacts ok if fct_unbilled = 12 tickets / $179,934.00.")
    print("Next: uv run python scripts/04_metric_view.py")


if __name__ == "__main__":
    main()
