"""Catalog status lifecycle for dim_kpi_metadata.

status values: proposed | approved | drifted | archived
definition_hash: sha256 hex of normalized live Metric View text
(SHOW CREATE TABLE / platform MV source for formula_object).
Not formula_version. Not gold published_ts.

Demo 2 / Track B. Shared by 06/08/09 store writes, 13 drift, 14 re-approve.
"""

from __future__ import annotations

import hashlib
import re
import time
from typing import Any

from config import run_statement, sql_str

STATUS_PROPOSED = "proposed"
STATUS_APPROVED = "approved"
STATUS_DRIFTED = "drifted"
STATUS_ARCHIVED = "archived"
STATUSES = (STATUS_PROPOSED, STATUS_APPROVED, STATUS_DRIFTED, STATUS_ARCHIVED)
APPROVAL_FIELDS = ("formula_pointer", "formula_object", "definition")

META_COLS = (
    "kpi_id",
    "name",
    "owner",
    "definition",
    "uom",
    "allowed_grain",
    "default_grain_rule",
    "gating_rule",
    "status",
    "formula_pointer",
    "formula_object",
    "formula_version",
    "ontology_iri",
    "as_of_date",
    "definition_hash",
)


def normalize_mv_text(text: str) -> str:
    """Strip trailing whitespace; keep the rest stable."""
    return (text or "").rstrip()


def hash_mv_text(text: str) -> str:
    return hashlib.sha256(normalize_mv_text(text).encode("utf-8")).hexdigest()


def fetch_live_mv_text(cur, formula_object: str) -> str:
    """Live Metric View source text for formula_object (SHOW CREATE TABLE)."""
    ident = str(formula_object).strip()
    if not ident:
        raise SystemExit("formula_object is empty; cannot fetch Metric View text")
    stmt = f"SHOW CREATE TABLE {ident}"
    rows = run_statement(cur, stmt)
    if not rows or rows[0][0] is None:
        raise SystemExit(f"SHOW CREATE TABLE returned no text for {ident}")
    return str(rows[0][0])


def live_definition_hash(cur, formula_object: str) -> str:
    return hash_mv_text(fetch_live_mv_text(cur, formula_object))


LOCKED_STATUSES = (STATUS_PROPOSED, STATUS_DRIFTED, STATUS_ARCHIVED)


def maybe_reset_approval(prev: dict[str, Any] | None, new: dict[str, Any]) -> dict[str, Any]:
    """If an approved row's pointer / object / definition changed, status=proposed.

    Does not auto-hash. Re-approve is required.
    Never promotes drifted|proposed|archived to approved (Gold/store republish
    is not re-approve).
    """
    out = dict(new)
    if not prev:
        return out
    prev_status = str(prev.get("status") or "")
    if prev_status != STATUS_APPROVED:
        if str(out.get("status") or "") == STATUS_APPROVED:
            out["status"] = prev_status
        return out
    changed = False
    for field in APPROVAL_FIELDS:
        if str(prev.get(field) or "") != str(out.get(field) or ""):
            changed = True
            break
    if changed:
        out["status"] = STATUS_PROPOSED
    return out


def _table_columns(cur, fq: str, table: str) -> set[str]:
    rows = run_statement(cur, f"DESCRIBE TABLE {fq}.{table}")
    return {str(r[0]).lower() for r in rows if r and r[0] and not str(r[0]).startswith("#")}


def ensure_definition_hash_column(cur, fq: str) -> None:
    """Keep the table. Never CREATE OR REPLACE. Add definition_hash if missing."""
    cols = _table_columns(cur, fq, "dim_kpi_metadata")
    if "definition_hash" in cols:
        print("definition_hash column already present.")
        return
    run_statement(
        cur,
        f"ALTER TABLE {fq}.dim_kpi_metadata ADD COLUMN definition_hash STRING",
        fetch=False,
    )
    print("Added definition_hash STRING (kept existing rows).")


def _as_row(cols: list[str], values: tuple) -> dict[str, Any]:
    return {c.lower(): values[i] for i, c in enumerate(cols)}


def fetch_kpi_row(cur, fq: str, kpi_id: str) -> dict[str, Any] | None:
    rows = run_statement(
        cur,
        f"SELECT * FROM {fq}.dim_kpi_metadata WHERE kpi_id = {sql_str(kpi_id)}",
    )
    if not rows:
        return None
    cols = [d[0] for d in cur.description]
    return _as_row(cols, tuple(rows[0]))


def fetch_all_kpi_rows(cur, fq: str) -> list[dict[str, Any]]:
    rows = run_statement(cur, f"SELECT * FROM {fq}.dim_kpi_metadata ORDER BY kpi_id")
    cols = [d[0] for d in cur.description]
    return [_as_row(cols, tuple(r)) for r in rows]


def _sql_val(col: str, value: Any) -> str:
    if value is None:
        return "NULL"
    if col == "as_of_date":
        text = str(value)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return f"DATE {sql_str(text)}"
        return f"DATE {sql_str(text[:10])}"
    return sql_str(str(value))


def write_kpi_row(cur, fq: str, row: dict[str, Any]) -> None:
    """DELETE + INSERT listed columns (includes definition_hash). Does not wipe others."""
    kpi_id = str(row["kpi_id"])
    cols = [c for c in META_COLS if c == "definition_hash" or c in row or True]
    # Always write the known column list so a missing hash becomes NULL.
    cols = list(META_COLS)
    values = ",\n  ".join(_sql_val(c, row.get(c)) for c in cols)
    run_statement(
        cur,
        f"DELETE FROM {fq}.dim_kpi_metadata WHERE kpi_id = {sql_str(kpi_id)}",
        fetch=False,
    )
    run_statement(
        cur,
        f"""INSERT INTO {fq}.dim_kpi_metadata (
  {", ".join(cols)}
)
SELECT
  {values}""",
        fetch=False,
    )


def upsert_kpi_row(cur, fq: str, new: dict[str, Any]) -> dict[str, Any]:
    """Store write path: compare previous row, maybe reset approval.

    First insert may write status=approved and set definition_hash.
    An already-approved row stays approved unless pointer/object/definition
    changed (then proposed). drifted|proposed|archived are never flipped to
    approved here — approve_kpi is the only re-approve path. definition_hash
    is not refreshed on a normal republish of an approved row.
    """
    ensure_definition_hash_column(cur, fq)
    kpi_id = str(new["kpi_id"])
    prev = fetch_kpi_row(cur, fq, kpi_id)
    out = dict(new)
    if prev:
        prev_status = str(prev.get("status") or "")
        if prev_status in LOCKED_STATUSES:
            out["status"] = prev_status
            if prev.get("definition_hash") not in (None, ""):
                out["definition_hash"] = prev.get("definition_hash")
            write_kpi_row(cur, fq, out)
            print(f"{kpi_id}: keep status={prev_status} (store will not approve).")
            return out
        out = maybe_reset_approval(prev, new)
        if str(out.get("status") or "") == STATUS_APPROVED:
            if prev.get("definition_hash") not in (None, ""):
                out["definition_hash"] = prev.get("definition_hash")
        elif prev.get("definition_hash") not in (None, "") and out.get("definition_hash") in (None, ""):
            out["definition_hash"] = prev.get("definition_hash")
        write_kpi_row(cur, fq, out)
        return out
    if str(out.get("status") or "") == STATUS_APPROVED:
        obj = str(out.get("formula_object") or "")
        if not obj:
            raise SystemExit(f"{kpi_id}: approved row missing formula_object")
        out["definition_hash"] = live_definition_hash(cur, obj)
    write_kpi_row(cur, fq, out)
    return out


def apply_catalog_update(cur, fq: str, kpi_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """One-off UPDATE helper: load prev, merge, maybe_reset_approval, write."""
    ensure_definition_hash_column(cur, fq)
    prev = fetch_kpi_row(cur, fq, kpi_id)
    if not prev:
        raise SystemExit(f"{kpi_id} missing from dim_kpi_metadata")
    new = dict(prev)
    new.update(updates)
    return upsert_kpi_row(cur, fq, new)


def migrate_certified_to_approved(cur, fq: str) -> int:
    """certified → approved. Does not wipe the table."""
    ensure_definition_hash_column(cur, fq)
    rows = run_statement(
        cur,
        f"""UPDATE {fq}.dim_kpi_metadata
SET status = {sql_str(STATUS_APPROVED)}
WHERE status = 'certified'""",
        fetch=False,
    )
    leftover = run_statement(
        cur,
        f"SELECT COUNT(*) FROM {fq}.dim_kpi_metadata WHERE status = 'certified'",
    )
    n = int(leftover[0][0]) if leftover else 0
    if n:
        raise SystemExit(f"migrate: {n} row(s) still status=certified")
    print("Migrated status certified → approved.")
    return n


def fill_approved_hashes(cur, fq: str) -> None:
    """Fill definition_hash only when empty. approve_kpi is the only refresh."""
    ensure_definition_hash_column(cur, fq)
    for row in fetch_all_kpi_rows(cur, fq):
        if str(row.get("status") or "") != STATUS_APPROVED:
            continue
        obj = str(row.get("formula_object") or "")
        if not obj:
            raise SystemExit(f"{row.get('kpi_id')}: approved row missing formula_object")
        stored = str(row.get("definition_hash") or "")
        if stored:
            print(f"  {row['kpi_id']}: hash present (re-approve to refresh)")
            continue
        live_hash = live_definition_hash(cur, obj)
        run_statement(
            cur,
            f"""UPDATE {fq}.dim_kpi_metadata
SET definition_hash = {sql_str(live_hash)}
WHERE kpi_id = {sql_str(str(row['kpi_id']))}""",
            fetch=False,
        )
        print(f"  {row['kpi_id']}: definition_hash filled {live_hash[:12]}…")


def approve_kpi(cur, fq: str, kpi_id: str) -> dict[str, Any]:
    """Re-approve: refresh definition_hash from live MV text, set status=approved."""
    ensure_definition_hash_column(cur, fq)
    row = fetch_kpi_row(cur, fq, kpi_id)
    if not row:
        raise SystemExit(f"{kpi_id} missing from dim_kpi_metadata")
    obj = str(row.get("formula_object") or "")
    if not obj:
        raise SystemExit(f"{kpi_id}: missing formula_object")
    live_hash = live_definition_hash(cur, obj)
    run_statement(
        cur,
        f"""UPDATE {fq}.dim_kpi_metadata
SET status = {sql_str(STATUS_APPROVED)},
    definition_hash = {sql_str(live_hash)}
WHERE kpi_id = {sql_str(kpi_id)}""",
        fetch=False,
    )
    print(f"Re-approved {kpi_id}; hash={live_hash[:12]}…")
    out = dict(row)
    out["status"] = STATUS_APPROVED
    out["definition_hash"] = live_hash
    return out


def drift_check(cur, fq: str) -> list[dict[str, Any]]:
    """Compare live MV hash to stored hash. Mismatch → drifted IFF currently approved.

    proposed and archived are left alone even when the live hash differs.
    Prints skipped-not-approved when the row is not approved. Does not edit the view.
    """
    ensure_definition_hash_column(cur, fq)
    results: list[dict[str, Any]] = []
    for row in fetch_all_kpi_rows(cur, fq):
        kpi_id = str(row.get("kpi_id") or "")
        old = str(row.get("status") or "")
        if old != STATUS_APPROVED:
            print(f"{kpi_id}\told={old}\tnew={old}\tskipped-not-approved")
            results.append(
                {"kpi_id": kpi_id, "old_status": old, "new_status": old, "match": None}
            )
            continue
        obj = str(row.get("formula_object") or "")
        stored = str(row.get("definition_hash") or "")
        live_hash = live_definition_hash(cur, obj) if obj else ""
        match = bool(stored) and stored == live_hash
        new = old
        if not match:
            new = STATUS_DRIFTED
            for attempt in range(4):
                try:
                    run_statement(
                        cur,
                        f"""UPDATE {fq}.dim_kpi_metadata
SET status = {sql_str(STATUS_DRIFTED)}
WHERE kpi_id = {sql_str(kpi_id)}
  AND status = {sql_str(STATUS_APPROVED)}""",
                        fetch=False,
                    )
                    break
                except Exception as exc:
                    if 'CONCURRENT' not in str(exc) or attempt == 3:
                        raise
                    time.sleep(1.5 * (attempt + 1))
        flag = "match" if match else "mismatch"
        print(f"{kpi_id}\told={old}\tnew={new}\t{flag}")
        results.append(
            {
                "kpi_id": kpi_id,
                "old_status": old,
                "new_status": new,
                "match": match,
                "stored_hash": stored,
                "live_hash": live_hash,
            }
        )
    return results
