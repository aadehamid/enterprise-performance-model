#!/usr/bin/env python3
"""01_connect.py — prove the Free warehouse answers from this Mac.

SELECT current_user(), current_catalog(); print warehouse.
Demo 2 / Track B. Not MetricFlow.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import connect, run_statement, settings  # noqa: E402


def main() -> None:
    cfg = settings()
    print("Databricks Free — local uv connect")
    print(f"  host         = {cfg.server_hostname}")
    print(f"  warehouse_id = {cfg.warehouse_id}")
    print(f"  http_path    = {cfg.http_path}")
    print(f"  catalog      = {cfg.catalog}")
    print(f"  schema       = {cfg.schema}")
    print("  token        = (set, not printed)")

    try:
        from databricks.sdk import WorkspaceClient

        w = WorkspaceClient(host=cfg.host, token=cfg.token)
        wh = w.warehouses.get(id=cfg.warehouse_id)
        print(f"  warehouse    = {wh.name}  state={wh.state}")
    except Exception as exc:  # SDK is optional extra info
        print(f"  warehouse    = (SDK lookup skipped: {exc})")

    with connect(cfg) as conn:
        with conn.cursor() as cur:
            run_statement(
                cur,
                "SELECT current_user() AS current_user, "
                "current_catalog() AS current_catalog, "
                "current_schema() AS current_schema",
            )
    print("\nConnect ok. Next: uv run python scripts/02_load.py")


if __name__ == "__main__":
    main()
