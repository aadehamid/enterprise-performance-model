#!/usr/bin/env python3
"""15_edit_reset_prove.py — approved catalog edit → proposed; restore + re-approve.

Temporarily changes Unbilled definition text, asserts status=proposed,
restores the original definition, re-approves. Does not leave the row dirty.
SQL/Python prove (not Genie). Demo 2 / Track B.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_status import (  # noqa: E402
    STATUS_APPROVED,
    STATUS_PROPOSED,
    apply_catalog_update,
    approve_kpi,
    fetch_kpi_row,
)
from config import connect, settings  # noqa: E402

KPI = "KPI-O2C-UNBILLED-USD"
PROBE = " [edit-reset-probe]"


def main() -> int:
    cfg = settings()
    print(f"Edit-resets-approval prove on {KPI} @ {cfg.fq}")
    with connect(cfg) as conn:
        with conn.cursor() as cur:
            prev = fetch_kpi_row(cur, cfg.fq, KPI)
            if not prev:
                raise SystemExit(f"{KPI} missing")
            original_def = str(prev.get("definition") or "")
            if original_def.endswith(PROBE):
                original_def = original_def[: -len(PROBE)]
            print(f"  start status={prev.get('status')} definition={original_def!r}")

            applied = apply_catalog_update(
                cur, cfg.fq, KPI, {"definition": original_def + PROBE}
            )
            mid = fetch_kpi_row(cur, cfg.fq, KPI)
            if not mid or str(mid.get("status")) != STATUS_PROPOSED:
                raise SystemExit(
                    f"FAIL: expected status=proposed after definition edit, "
                    f"got {(mid or {}).get('status')!r} applied={applied.get('status')!r}"
                )
            if not str(mid.get("definition") or "").endswith(PROBE):
                raise SystemExit("FAIL: probe definition not written")
            print(f"  after edit: status={mid.get('status')} (proposed ok)")

            apply_catalog_update(cur, cfg.fq, KPI, {"definition": original_def})
            approve_kpi(cur, cfg.fq, KPI)
            end = fetch_kpi_row(cur, cfg.fq, KPI)
            if not end:
                raise SystemExit(f"{KPI} missing after restore")
            if str(end.get("status")) != STATUS_APPROVED:
                raise SystemExit(f"FAIL: expected approved after restore, got {end.get('status')!r}")
            if str(end.get("definition") or "") != original_def:
                raise SystemExit(
                    f"FAIL: definition not restored, got {end.get('definition')!r}"
                )
            if not str(end.get("definition_hash") or ""):
                raise SystemExit("FAIL: definition_hash empty after re-approve")
            print(
                f"  after restore+re-approve: status={end.get('status')} "
                f"hash={str(end.get('definition_hash'))[:12]}… definition restored"
            )
    print("PASS: edit-reset proposed then restored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
