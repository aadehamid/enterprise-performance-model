#!/usr/bin/env python3
"""13_status_drift.py — compare live Metric View text to definition_hash.

For each approved dim_kpi_metadata row: SHOW CREATE the formula_object,
hash, compare to stored definition_hash. Mismatch → status=drifted.
proposed and archived are left alone (prints skipped-not-approved).
Does not change the Metric View. Number is not approved until steward re-approves.

Also: --migrate adds definition_hash, certified → approved, fills hashes.

Demo 2 / Track B. Not MetricFlow.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_status import (  # noqa: E402
    drift_check,
    fill_approved_hashes,
    migrate_certified_to_approved,
)
from config import connect, settings  # noqa: E402


def migrate(cur, fq: str) -> None:
    print("======== MIGRATE catalog status ========")
    migrate_certified_to_approved(cur, fq)
    print("Fill definition_hash from live Metric View text:")
    fill_approved_hashes(cur, fq)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    do_migrate = "--migrate" in args
    cfg = settings()
    print(f"Catalog status drift check against {cfg.fq}")
    print("Does not change Metric Views. Token not printed.")
    with connect(cfg) as conn:
        with conn.cursor() as cur:
            if do_migrate:
                migrate(cur, cfg.fq)
            print("\n======== DRIFT CHECK ========")
            results = drift_check(cur, cfg.fq)
    mismatches = [r for r in results if r.get("match") is False]
    print(f"\nChecked {len(results)} row(s); {len(mismatches)} mismatch(es).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
