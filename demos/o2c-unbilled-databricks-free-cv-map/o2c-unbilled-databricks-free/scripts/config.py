"""Shared env + SQL helpers for the Databricks Free O2C Unbilled Mac runner.

Demo 2 / Track B. Not MetricFlow. Not demo 1.
Databricks scripts refuse if DATABRICKS_TOKEN is missing.
Lakebase scripts refuse if LAKEBASE_PASSWORD is missing.
Act 0 uses existing project dataexpert-day1 / database databricks_postgres /
schema o2c_unbilled only. Never DROP other schemas. Never invent a host.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from databricks import sql
from databricks.sql.client import Connection, Cursor

PACK_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PACK_ROOT / ".env"


def load_dotenv(path: Path = ENV_PATH) -> None:
    """Load KEY=VALUE lines from .env without overriding a real environment."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass(frozen=True)
class Settings:
    host: str
    warehouse_id: str
    catalog: str
    schema: str
    token: str

    @property
    def server_hostname(self) -> str:
        return (
            self.host.removeprefix("https://")
            .removeprefix("http://")
            .split("/")[0]
            .rstrip("/")
        )

    @property
    def http_path(self) -> str:
        return f"/sql/1.0/warehouses/{self.warehouse_id}"

    @property
    def fq(self) -> str:
        return f"{self.catalog}.{self.schema}"


def settings() -> Settings:
    load_dotenv()
    host = os.environ.get("DATABRICKS_HOST", "").strip()
    warehouse_id = os.environ.get("DATABRICKS_WAREHOUSE_ID", "").strip()
    catalog = os.environ.get("DATABRICKS_CATALOG", "workspace").strip() or "workspace"
    schema = os.environ.get("DATABRICKS_SCHEMA", "o2c_unbilled").strip() or "o2c_unbilled"
    token = os.environ.get("DATABRICKS_TOKEN", "").strip()

    missing: list[str] = []
    if not host:
        missing.append("DATABRICKS_HOST")
    if not warehouse_id:
        missing.append("DATABRICKS_WAREHOUSE_ID")
    if not token:
        missing.append("DATABRICKS_TOKEN")
    if missing:
        names = ", ".join(missing)
        print(
            f"Refusing to run: missing {names}.\n"
            f"Copy .env.example → .env in {PACK_ROOT} and fill the values.\n"
            "Never commit the real token. See README 'Run from your Mac (uv)'.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    if "azuredatabricks.net" in host.lower():
        print(
            "DATABRICKS_HOST looks like Azure Databricks. This pack is Free Edition "
            "(*.cloud.databricks.com). Stop and sign in at login.databricks.com.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    return Settings(
        host=host,
        warehouse_id=warehouse_id,
        catalog=catalog,
        schema=schema,
        token=token,
    )


def connect(cfg: Settings | None = None) -> Connection:
    cfg = cfg or settings()
    return sql.connect(
        server_hostname=cfg.server_hostname,
        http_path=cfg.http_path,
        access_token=cfg.token,
        catalog=cfg.catalog,
        schema=cfg.schema,
    )


def substitute(sql_text: str, cfg: Settings) -> str:
    return sql_text.replace("{{catalog}}", cfg.catalog).replace("{{schema}}", cfg.schema)


def split_sql(text: str) -> list[str]:
    """Split on ';' that are not inside strings, comments, or $$ YAML blocks."""
    stmts: list[str] = []
    buf: list[str] = []
    i = 0
    n = len(text)
    in_single = False
    in_line_comment = False
    in_block_comment = False
    in_dollar = False
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_line_comment:
            buf.append(c)
            if c == "\n":
                in_line_comment = False
            i += 1
            continue
        if in_block_comment:
            buf.append(c)
            if c == "*" and nxt == "/":
                buf.append(nxt)
                i += 2
                in_block_comment = False
                continue
            i += 1
            continue
        if in_dollar:
            buf.append(c)
            if c == "$" and nxt == "$":
                buf.append(nxt)
                i += 2
                in_dollar = False
                continue
            i += 1
            continue
        if in_single:
            buf.append(c)
            if c == "'":
                if nxt == "'":
                    buf.append(nxt)
                    i += 2
                    continue
                in_single = False
            i += 1
            continue
        if c == "-" and nxt == "-":
            buf.append(c)
            buf.append(nxt)
            i += 2
            in_line_comment = True
            continue
        if c == "/" and nxt == "*":
            buf.append(c)
            buf.append(nxt)
            i += 2
            in_block_comment = True
            continue
        if c == "$" and nxt == "$":
            buf.append(c)
            buf.append(nxt)
            i += 2
            in_dollar = True
            continue
        if c == "'":
            buf.append(c)
            in_single = True
            i += 1
            continue
        if c == ";":
            stmt = "".join(buf).strip()
            if _has_sql(stmt):
                stmts.append(stmt)
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    tail = "".join(buf).strip()
    if _has_sql(tail):
        stmts.append(tail)
    return stmts


def _has_sql(stmt: str) -> bool:
    stripped: list[str] = []
    for line in stmt.splitlines():
        cut = line.split("--", 1)[0].strip()
        if cut:
            stripped.append(cut)
    body = " ".join(stripped).strip()
    return bool(body) and not body.startswith("/*")


def print_sql(sql_text: str) -> None:
    print()
    print("── SQL ──────────────────────────────────────────────────────────")
    print(sql_text.rstrip() + ("" if sql_text.rstrip().endswith(";") else ";"))
    print("────────────────────────────────────────────────────────────────")


def print_grid(columns: list[str], rows: list) -> None:
    str_rows = [[_cell(v) for v in row] for row in rows]
    widths = [len(c) for c in columns]
    for row in str_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    header = " | ".join(c.ljust(widths[i]) for i, c in enumerate(columns))
    rule = "-+-".join("-" * w for w in widths)
    print(header)
    print(rule)
    if not str_rows:
        print("(0 rows)")
        return
    for row in str_rows:
        print(" | ".join(row[i].ljust(widths[i]) for i in range(len(columns))))
    print(f"({len(str_rows)} row{'s' if len(str_rows) != 1 else ''})")


def _cell(value: object) -> str:
    if value is None:
        return "NULL"
    return str(value)


def run_statement(cursor: Cursor, sql_text: str, *, fetch: bool = True) -> list:
    print_sql(sql_text)
    cursor.execute(sql_text)
    if not fetch or cursor.description is None:
        print("(no result set)")
        return []
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    print_grid(cols, rows)
    return rows


def run_script(cursor: Cursor, sql_text: str) -> None:
    for stmt in split_sql(sql_text):
        run_statement(cursor, stmt)



# ---------------------------------------------------------------------------
# Shared seed table specs (CSV → Lakebase ODS → Databricks raw_*)
# ---------------------------------------------------------------------------

DATA_DIR = PACK_ROOT / "data"

# csv, lakebase ops table, databricks raw table, [(col, spark_type, value_kind)]
# value_kind: str | ts | date | num
TABLES: list[tuple[str, str, str, list[tuple[str, str, str]]]] = [
    (
        "parties.csv",
        "parties",
        "raw_parties",
        [
            ("party_id", "STRING", "str"),
            ("party_name", "STRING", "str"),
            ("legal_name", "STRING", "str"),
            ("party_class", "STRING", "str"),
            ("tax_id", "STRING", "str"),
            ("hq_city", "STRING", "str"),
            ("hq_state", "STRING", "str"),
        ],
    ),
    (
        "party_roles.csv",
        "party_roles",
        "raw_party_roles",
        [
            ("party_id", "STRING", "str"),
            ("role_code", "STRING", "str"),
        ],
    ),
    (
        "products.csv",
        "products",
        "raw_products",
        [
            ("product_code", "STRING", "str"),
            ("product_name", "STRING", "str"),
            ("product_family", "STRING", "str"),
            ("contract_price_usd", "DECIMAL(10, 3)", "num"),
            ("list_price_usd", "DECIMAL(10, 3)", "num"),
            ("expansion_per_f", "DECIMAL(10, 5)", "num"),
            ("uom", "STRING", "str"),
        ],
    ),
    (
        "terminals.csv",
        "terminals",
        "raw_terminals",
        [
            ("terminal_code", "STRING", "str"),
            ("terminal_name", "STRING", "str"),
            ("city", "STRING", "str"),
            ("state", "STRING", "str"),
            ("mode", "STRING", "str"),
        ],
    ),
    (
        "tickets.csv",
        "tickets",
        "raw_tickets",
        [
            ("ticket_id", "STRING", "str"),
            ("bol_ts", "TIMESTAMP", "ts"),
            ("terminal_code", "STRING", "str"),
            ("sold_to_id", "STRING", "str"),
            ("payer_id", "STRING", "str"),
            ("bill_to_id", "STRING", "str"),
            ("product_code", "STRING", "str"),
            ("gallons_net", "DECIMAL(12, 2)", "num"),
            ("gallons_gross", "DECIMAL(12, 2)", "num"),
            ("temperature_f", "DECIMAL(5, 1)", "num"),
            ("status", "STRING", "str"),
        ],
    ),
    (
        "invoices.csv",
        "invoices",
        "raw_invoices",
        [
            ("invoice_id", "STRING", "str"),
            ("invoice_date", "DATE", "date"),
            ("payer_id", "STRING", "str"),
            ("bill_to_id", "STRING", "str"),
            ("invoice_status", "STRING", "str"),
            ("invoice_amount_usd", "DECIMAL(18, 2)", "num"),
            ("line_count", "INT", "num"),
        ],
    ),
    (
        "invoice_lines.csv",
        "invoice_lines",
        "raw_invoice_lines",
        [
            ("invoice_id", "STRING", "str"),
            ("ticket_id", "STRING", "str"),
            ("product_code", "STRING", "str"),
            ("line_gallons_net", "DECIMAL(12, 2)", "num"),
            ("line_amount_usd", "DECIMAL(18, 2)", "num"),
        ],
    ),
]

EXPECTED_RAW = {
    "raw_parties": 8,
    "raw_party_roles": 10,
    "raw_products": 3,
    "raw_terminals": 3,
    "raw_tickets": 19,
    "raw_invoices": 6,
    "raw_invoice_lines": 6,
}

EXPECTED_OPS = {
    "parties": 8,
    "party_roles": 10,
    "products": 3,
    "terminals": 3,
    "tickets": 19,
    "invoices": 6,
    "invoice_lines": 6,
}

ALLOWED_LAKEBASE_PROJECT = "dataexpert-day1"
ALLOWED_LAKEBASE_DATABASE = "databricks_postgres"
ALLOWED_LAKEBASE_SCHEMA = "o2c_unbilled"


def pg_type(spark_type: str) -> str:
    if spark_type == "STRING":
        return "TEXT"
    if spark_type == "TIMESTAMP":
        return "TIMESTAMP"
    if spark_type == "DATE":
        return "DATE"
    if spark_type == "INT":
        return "INTEGER"
    if spark_type.startswith("DECIMAL"):
        return "NUMERIC" + spark_type[len("DECIMAL") :]
    raise ValueError(f"no Postgres mapping for {spark_type}")


def sql_str(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def sql_literal(value: object, kind: str) -> str:
    if value is None or value == "":
        return "NULL"
    if kind == "str":
        return sql_str(str(value))
    if kind == "ts":
        return f"TIMESTAMP {sql_str(str(value).replace('T', ' '))}"
    if kind == "date":
        return f"DATE {sql_str(str(value))}"
    if kind == "num":
        return str(value)
    raise ValueError(f"unknown kind {kind}")


def values_as_select(fq_table: str, cols: list[tuple[str, str, str]], rows: list) -> str:
    """CREATE OR REPLACE TABLE fq AS SELECT CAST… FROM VALUES … (idempotent)."""
    if not rows:
        raise SystemExit(f"no rows for {fq_table}")
    names = [c[0] for c in cols]
    casts = ",\n  ".join(f"CAST({name} AS {typ}) AS {name}" for name, typ, _ in cols)
    value_lines = []
    for row in rows:
        if isinstance(row, dict):
            cells = ", ".join(sql_literal(row[name], kind) for name, _typ, kind in cols)
        else:
            cells = ", ".join(sql_literal(row[i], kind) for i, (_n, _t, kind) in enumerate(cols))
        value_lines.append(f"  ({cells})")
    values = ",\n".join(value_lines)
    alias = ", ".join(names)
    return (
        f"CREATE OR REPLACE TABLE {fq_table} AS\n"
        f"SELECT\n  {casts}\n"
        f"FROM VALUES\n{values}\n"
        f"AS v({alias})"
    )


@dataclass(frozen=True)
class LakebaseSettings:
    host: str
    database: str
    user: str
    password: str
    schema: str
    port: int = 5432

    @property
    def fq(self) -> str:
        return self.schema


def lakebase_settings() -> LakebaseSettings:
    """Act 0: existing dataexpert-day1 / databricks_postgres / o2c_unbilled only."""
    load_dotenv()
    host = os.environ.get("LAKEBASE_HOST", "").strip()
    database = os.environ.get("LAKEBASE_DATABASE", "databricks_postgres").strip() or "databricks_postgres"
    user = os.environ.get("LAKEBASE_USER", "").strip()
    password = os.environ.get("LAKEBASE_PASSWORD", "").strip()
    schema = os.environ.get("LAKEBASE_SCHEMA", "o2c_unbilled").strip() or "o2c_unbilled"

    missing: list[str] = []
    if not host:
        missing.append("LAKEBASE_HOST")
    if not user:
        missing.append("LAKEBASE_USER")
    if not password:
        missing.append("LAKEBASE_PASSWORD")
    if missing:
        names = ", ".join(missing)
        print(
            f"Refusing to run: missing {names}.\n"
            f"Copy .env.example → .env in {PACK_ROOT} and fill Lakebase values "
            f"from the Connect dialog on existing project {ALLOWED_LAKEBASE_PROJECT}.\n"
            "Do not create a second Lakebase project. Never commit the password.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    if database != ALLOWED_LAKEBASE_DATABASE:
        print(
            f"Refusing to run: LAKEBASE_DATABASE={database!r}. "
            f"Act 0 is locked to {ALLOWED_LAKEBASE_DATABASE} on {ALLOWED_LAKEBASE_PROJECT}.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    if schema != ALLOWED_LAKEBASE_SCHEMA:
        print(
            f"Refusing to run: LAKEBASE_SCHEMA={schema!r}. "
            f"Only {ALLOWED_LAKEBASE_SCHEMA} is allowed. "
            "Do not write into other day1 schemas.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    return LakebaseSettings(
        host=host,
        database=database,
        user=user,
        password=password,
        schema=schema,
    )


def lakebase_connect(lb: LakebaseSettings | None = None):
    """psycopg connection. sslmode=require (official Lakebase connection strings)."""
    import psycopg

    lb = lb or lakebase_settings()
    return psycopg.connect(
        host=lb.host,
        port=lb.port,
        dbname=lb.database,
        user=lb.user,
        password=lb.password,
        sslmode="require",
    )
