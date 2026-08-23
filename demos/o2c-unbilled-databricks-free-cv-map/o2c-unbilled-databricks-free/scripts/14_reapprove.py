#!/usr/bin/env python3
"""14_reapprove.py — steward re-approve: refresh hash from live MV, status=approved.

Usage: uv run python scripts/14_reapprove.py [KPI-O2C-UNBILLED-USD]
Used after the Metric View is reverted (or after an edit-reset restore).
Demo 2 / Track B. Not MetricFlow.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_status import approve_kpi, fetch_kpi_row  # noqa: E402
from config import connect, settings  # noqa: E402

DEFAULT_KPI = "KPI-O2C-UNBILLED-USD"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    kpi_id = args[0] if args else DEFAULT_KPI
    cfg = settings()
    print(f"Re-approve {kpi_id} on {cfg.fq}")
    with connect(cfg) as conn:
        with conn.cursor() as cur:
            approve_kpi(cur, cfg.fq, kpi_id)
            row = fetch_kpi_row(cur, cfg.fq, kpi_id)
    if not row:
        raise SystemExit(f"{kpi_id} missing after re-approve")
    digest = str(row.get("definition_hash") or "")
    print(f"status={row.get('status')} hash={digest[:12]}… pointer={row.get('formula_pointer')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
