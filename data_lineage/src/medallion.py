"""Medallion layer rules: the layer a schema belongs to, and which objects carry :Legacy.

Single source for the layer-assignment rules in AGENTS.md. Python record builders call
schema_layer / is_legacy; Cypher that classifies nodes already in the graph embeds
cypher_schema_layer / cypher_is_legacy_schema, which render the same rule table.
"""

from typing import Literal

Layer = Literal["Operational", "Replica", "Silver", "Gold", "Semantic"]

LEGACY_SCHEMAS = frozenset({"kh_core", "dwh_core", "persistence", "staging", "sem_comm_kh_mpc_rstd"})
LEGACY_SCHEMA_PREFIX = "dwh"

# First match wins. Pre-standard schemas come before the generic `_core` rule so that
# KH_Core and dwh_*_core stay Silver.
_LAYER_RULES: tuple[tuple[str, str | frozenset[str], Layer], ...] = (
    ("prefix", "sem_", "Semantic"),
    ("prefix", LEGACY_SCHEMA_PREFIX, "Silver"),
    ("in", LEGACY_SCHEMAS - {"sem_comm_kh_mpc_rstd"}, "Silver"),
    ("prefix", "replica", "Replica"),
    ("in", frozenset({"udm_core", "mdm_core"}), "Silver"),
    ("suffix", "_core", "Gold"),
)


_FLAG_TRUE = frozenset({"yes", "y", "true"})
_FLAG_FALSE = frozenset({"no", "n", "false"})
_FLAG_BLANK = frozenset({"", "nan", "none", "null", "<na>"})


def flag_bool(value):
    """Map a Yes/No source flag to a boolean.

    Yes and Y are true. No and N are false. Blank stays null.
    A value outside that set is returned unchanged.
    """
    if isinstance(value, bool) or value is None:
        return value
    try:
        if value != value:
            return None
    except TypeError:
        pass
    text = str(value).strip().lower()
    if text in _FLAG_BLANK:
        return None
    if text in _FLAG_TRUE:
        return True
    if text in _FLAG_FALSE:
        return False
    return value


def _url_text(web_url) -> str:
    if web_url is None:
        return ""
    try:
        if web_url != web_url:
            return ""
    except TypeError:
        pass
    text = str(web_url).strip()
    if text.lower() in _FLAG_BLANK:
        return ""
    return text


def report_key(name, web_url=None) -> str:
    """Identity of a new report. A non-empty webUrl, otherwise name: plus the name."""
    url = _url_text(web_url)
    if url:
        return url
    return f"name:{name}"


def resolve_report_key(name, web_url, stored) -> str:
    """Identity used to MERGE. A URL wins. A name-only row reuses the stored key."""
    url = _url_text(web_url)
    if url:
        return url
    existing = (stored or {}).get(name)
    if existing:
        return existing
    return f"name:{name}"


def stamp_report_keys(rows, lookup, name_field, url_field=None, key_field="reportKey"):
    """Write reportKey on each row from the URL, else the stored key for that name."""
    for row in rows:
        url = row.get(url_field) if url_field else None
        row[key_field] = resolve_report_key(row.get(name_field), url, lookup)
    return rows


def schema_of(qualified_name: str) -> str:
    return qualified_name.split(".", 1)[0].strip()


def schema_layer(schema: str | None) -> Layer | None:
    """Layer implied by the schema name, or None when the name follows no medallion rule."""
    s = (schema or "").strip().lower()
    if not s:
        return None
    for kind, pattern, layer in _LAYER_RULES:
        if (
            (kind == "prefix" and s.startswith(pattern))
            or (kind == "suffix" and s.endswith(pattern))
            or (kind == "in" and s in pattern)
        ):
            return layer
    return None


def is_legacy_schema(schema: str | None) -> bool:
    s = (schema or "").strip().lower()
    return s in LEGACY_SCHEMAS or s.startswith(LEGACY_SCHEMA_PREFIX)


def is_legacy(qualified_name: str, layer: str | None = None) -> bool:
    """True when the Table carries :Legacy: a pre-standard schema, or a Silver `union` table."""
    schema = schema_of(qualified_name) if "." in qualified_name else ""
    if is_legacy_schema(schema):
        return True
    table_name = qualified_name.rsplit(".", 1)[-1]
    return "union" in table_name.lower() and (layer or schema_layer(schema)) == "Silver"


def is_idp_schema(schema: str | None) -> bool:
    """A standard IDP (Synapse) schema: replica_*, sem_*, or *_core."""
    s = (schema or "").strip().lower()
    return s.startswith(("replica_", "sem_")) or s.endswith("_core")


def _cypher_list(values: frozenset[str]) -> str:
    return "[" + ", ".join(f"'{v}'" for v in sorted(values)) + "]"


def cypher_schema_layer(expr: str, default: Layer) -> str:
    """Cypher CASE expression equal to schema_layer(expr), falling back to `default`."""
    s = f"toLower({expr})"
    whens = []
    for kind, pattern, layer in _LAYER_RULES:
        if kind == "prefix":
            cond = f"{s} STARTS WITH '{pattern}'"
        elif kind == "suffix":
            cond = f"{s} ENDS WITH '{pattern}'"
        else:
            cond = f"{s} IN {_cypher_list(pattern)}"
        whens.append(f"WHEN {cond} THEN '{layer}'")
    return "CASE " + " ".join(whens) + f" ELSE '{default}' END"


def cypher_is_legacy_schema(expr: str) -> str:
    """Cypher boolean equal to is_legacy_schema(expr)."""
    s = f"toLower({expr})"
    return f"({s} IN {_cypher_list(LEGACY_SCHEMAS)} OR {s} STARTS WITH '{LEGACY_SCHEMA_PREFIX}')"
