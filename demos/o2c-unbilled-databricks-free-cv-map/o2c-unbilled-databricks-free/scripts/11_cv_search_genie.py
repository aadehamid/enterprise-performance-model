#!/usr/bin/env python3
"""11_cv_search_genie.py — second Genie Agent: O2C vocabulary search.

Search only. Preferred label + stable ID. Never a dollar.
Does NOT find/update the certified agent titled O2C certified KPIs.
Does NOT attach Metric Views, gold, fct_*, raw_*, dim_customer,
sap_partner, sf_account, tas_lift, ra_business_associate, or
dim_kpi_metadata. Hunt stubs stay off both Genies. Never prints token, host, or warehouse id.
Demo 2 / Track B. Pattern from 07_genie.py.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import settings  # noqa: E402
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import DatabricksError

TITLE = "O2C vocabulary search"
CERTIFIED_TITLE = "O2C certified KPIs"
Q_CUSTOMER = "What is customer?"
Q_RG = "What is RG?"
Q_APEX = "What is APEX-PAYER?"
Q_CONS = "What is CONS-4412?"

FORBIDDEN_DOLLARS = ("179934", "115960", "179,934", "115,960")
SOLD_TO = "id:sold-to"
LIFT = "id:loading-authorized-party"
SOLD_LABEL = "sold-to"
LIFT_LABEL = "loading-authorized party"



def scrub(exc: object) -> str:
    """Strip host / warehouse / account / token tails from SDK errors."""
    text = f"{getattr(exc, 'error_code', None) or ''} {exc}".strip()
    if " Config:" in text:
        text = text.split(" Config:", 1)[0].rstrip()
    if " Env:" in text:
        text = text.split(" Env:", 1)[0].rstrip()
    text = re.sub(r"https?://\S+", "(host omitted)", text)
    text = re.sub(r"warehouse_id=\S+", "warehouse_id=(omitted)", text)
    text = re.sub(r"account_id=\S+", "account_id=(omitted)", text)
    text = re.sub(r"workspace_id=\S+", "workspace_id=(omitted)", text)
    text = re.sub(r"token=\S+", "token=(omitted)", text)
    return text


def _hid(label: str) -> str:
    return (label.encode().hex() + "0" * 32)[:32]


def table_ids(catalog: str, schema: str) -> dict[str, str]:
    fq = f"{catalog}.{schema}"
    return {
        "term": f"{fq}.cv_term",
        "alias": f"{fq}.cv_alias",
        "map": f"{fq}.cv_map",
        "lookup": f"{fq}.cv_lookup",
    }


def lookup_or_join(fq: str, q: str, use_function: bool) -> str:
    if use_function:
        return f"SELECT term_id, preferred_label FROM {fq}.cv_lookup('{q}')"
    lit = q.replace("'", "''")
    return (
        "SELECT DISTINCT t.term_id, t.preferred_label "
        f"FROM {fq}.cv_alias a "
        f"JOIN {fq}.cv_term t ON t.term_id = a.term_id "
        f"WHERE lower(a.alias) = lower('{lit}') "
        "UNION "
        "SELECT DISTINCT t.term_id, t.preferred_label "
        f"FROM {fq}.cv_term t "
        f"WHERE lower(t.preferred_label) = lower('{lit}') "
        f"OR lower(t.term_id) = lower('{lit}') "
        "UNION "
        "SELECT DISTINCT t.term_id, t.preferred_label "
        f"FROM {fq}.cv_map m "
        f"JOIN {fq}.cv_term t ON t.term_id = m.term_id "
        f"WHERE m.term_id IS NOT NULL AND lower(m.local_key) = lower('{lit}')"
    )


def general_instruction_text(ids: dict[str, str], use_function: bool) -> str:
    fq_term, fq_alias, fq_map = ids["term"], ids["alias"], ids["map"]
    lookup = ids["lookup"]
    do_lookup = (
        f"run SELECT term_id, preferred_label FROM {lookup}('…')"
        if use_function
        else f"join {fq_term} + {fq_alias} + {fq_map} (alias, preferred_label, term_id, local_key)"
    )
    return f"""---
name: o2c-vocabulary-search
description: Search only. Preferred label + stable ID. Never a dollar. Use when the user asks what a party word or code means (customer, RG, APEX-PAYER, CONS-4412, payer, sold-to, bill-to, ship-to, lift customer).
---

# When to use

The user asks what a party word or code means: customer, RG, PY, AG, SP, APEX-PAYER, CONS-4412, payer, sold-to, bill-to, ship-to, site, lift customer, loading-authorized party.

# Do

- {do_lookup}.
- Return every matching preferred_label + term_id.
- If two hits, return both and say the word is overloaded.
- "customer" matches Sold-To (`id:sold-to`) AND Loading-Authorized Party (`id:loading-authorized-party`). Return both. Do not pick one.
- RG / PY / paying party / APEX-PAYER → Payer (`id:payer`).
- CONS-4412 → Loading-Authorized Party (`id:loading-authorized-party`). Wrong sense for Unbilled. Not a payer.

# Don't

- Never MEASURE().
- Never a dollar.
- Never attach or query unbilled_usd / gold / fct / raw / dim_customer / sap_partner / sf_account / tas_lift / ra_business_associate / dim_kpi_metadata.
- Never pick one sense of "customer" and hide the other.
- Never say a certified Unbilled number.
"""


def serialized_space(ids: dict[str, str], use_function: bool, include_lookup_source: bool) -> str:
    fq = ids["term"].rsplit(".", 1)[0]
    q_ids = [_hid(f"vq{i}") for i in range(1, 5)]
    e_ids = [_hid(f"ve{i}") for i in range(1, 5)]
    i1 = _hid("vi1")
    samples = [
        {"id": q_ids[0], "question": [Q_CUSTOMER]},
        {"id": q_ids[1], "question": [Q_RG]},
        {"id": q_ids[2], "question": [Q_APEX]},
        {"id": q_ids[3], "question": [Q_CONS]},
    ]
    examples = [
        {
            "id": e_ids[0],
            "question": [Q_CUSTOMER],
            "sql": [lookup_or_join(fq, "customer", use_function)],
        },
        {
            "id": e_ids[1],
            "question": [Q_RG],
            "sql": [lookup_or_join(fq, "RG", use_function)],
        },
        {
            "id": e_ids[2],
            "question": [Q_APEX],
            "sql": [lookup_or_join(fq, "APEX-PAYER", use_function)],
        },
        {
            "id": e_ids[3],
            "question": [Q_CONS],
            "sql": [lookup_or_join(fq, "CONS-4412", use_function)],
        },
    ]
    tables = [
        {
            "identifier": ids["term"],
            "description": ["Controlled vocabulary preferred labels, scope notes, and optional ontology_iri bind (not a replacement of term_id). Search only. Never a dollar."],
        },
        {
            "identifier": ids["alias"],
            "description": ["Aliases. The word customer maps to two term_ids (Sold-To and Loading-Authorized Party)."],
        },
        {
            "identifier": ids["map"],
            "description": ["Live local keys to term_id. Empty term_id means no map. Search only."],
        },
    ]
    data_sources = {
        "tables": sorted(tables, key=lambda x: x["identifier"]),
    }
    if include_lookup_source:
        # Function identifier, not a table. API rejected cv_lookup under tables.
        data_sources["functions"] = [
            {
                "identifier": ids["lookup"],
                "description": [
                    "Table function. SELECT term_id, preferred_label FROM cv_lookup('customer') returns every match."
                ],
            }
        ]
    space = {
        "version": 2,
        "config": {
            "sample_questions": sorted(samples, key=lambda x: x["id"]),
        },
        "data_sources": data_sources,
        "instructions": {
            "text_instructions": [
                {
                    "id": i1,
                    "content": [general_instruction_text(ids, use_function)],
                }
            ],
            "example_question_sqls": sorted(examples, key=lambda x: x["id"]),
        },
    }
    return json.dumps(space, separators=(",", ":"))


def list_spaces(w: WorkspaceClient) -> list:
    resp = w.genie.list_spaces()
    return list(getattr(resp, "spaces", None) or [])


def find_by_title(spaces: list, title: str):
    for s in spaces:
        if (getattr(s, "title", "") or "") == title:
            return s
    return None


def parent_path(w: WorkspaceClient) -> str | None:
    try:
        me = w.current_user.me()
        return f"/Users/{me.user_name}" if me.user_name else None
    except Exception:
        return None


def source_identifiers(serialized: str | None) -> list[str]:
    if not serialized:
        return []
    try:
        payload = json.loads(serialized)
    except json.JSONDecodeError:
        return []
    sources = payload.get("data_sources") or {}
    ids: list[str] = []
    for key in ("metric_views", "tables", "functions", "views"):
        for item in sources.get(key) or []:
            ident = item.get("identifier") if isinstance(item, dict) else None
            if ident:
                ids.append(ident)
    return ids


def extract_sql_and_answer(msg) -> tuple[str | None, str | None, str]:
    payload = msg.as_dict() if hasattr(msg, "as_dict") else {}
    sql_text = None
    texts: list[str] = []
    blobs: list[str] = []

    content = getattr(msg, "content", None) or payload.get("content")
    if content:
        texts.append(str(content))
        blobs.append(str(content))

    for att in payload.get("attachments") or []:
        q = att.get("query") or {}
        for key in ("query", "sql", "statement"):
            if q.get(key) and not sql_text:
                sql_text = q[key]
        if q.get("description"):
            texts.append(str(q["description"]))
        if q.get("query"):
            blobs.append(str(q["query"]))
        result = q.get("query_result") or q.get("statement_response") or {}
        if result:
            blobs.append(json.dumps(result, default=str))
        text = att.get("text") or {}
        if text.get("content"):
            texts.append(str(text["content"]))
            blobs.append(str(text["content"]))

    qr = payload.get("query_result")
    if qr:
        blobs.append(json.dumps(qr, default=str))

    answer = "\n".join(t for t in texts if t).strip() or None
    blob = "\n".join(blobs)
    return sql_text, answer, blob


def ask(w: WorkspaceClient, space_id: str, question: str):
    print(f"\nAsking: {question}")
    try:
        msg = w.genie.start_conversation_and_wait(
            space_id=space_id,
            content=question,
            timeout=timedelta(minutes=8),
        )
    except DatabricksError as exc:
        print(f"  conversation failed: {scrub(exc)}")
        return None, None, None, f"API blocker: {scrub(exc)}"
    print(f"  status = {getattr(msg, 'status', None)}")
    sql_text, answer, blob = extract_sql_and_answer(msg)
    if sql_text:
        print("  generated SQL:")
        print(sql_text)
    else:
        print("  generated SQL: (none in attachments)")
    if answer:
        print(f"  answer = {answer}")
    elif blob:
        print(f"  result blob (truncated) = {blob[:400]}")
    return sql_text, answer, blob, None


def has_both_senses(sql_text: str | None, blob: str) -> bool:
    hay = f"{sql_text or ''}\n{blob or ''}".lower()
    sold = SOLD_TO in hay or ("sold-to" in hay and "id:sold" in hay) or re.search(r"\bsold-to\b", hay)
    lift = (
        LIFT in hay
        or "loading-authorized party" in hay
        or "loading-authorized-party" in hay
        or "id:loading-authorized-party" in hay
    )
    return bool(sold) and bool(lift)


def has_dollar_leak(sql_text: str | None, blob: str) -> bool:
    hay = f"{sql_text or ''}\n{blob or ''}"
    if re.search(r"MEASURE\s*\(", hay, re.I):
        return True
    compact = re.sub(r"[,\s]", "", hay)
    return any(d.replace(",", "") in compact for d in FORBIDDEN_DOLLARS)


def grade_search(sql_text: str | None, blob: str) -> bool:
    both = has_both_senses(sql_text, blob)
    leak = has_dollar_leak(sql_text, blob)
    if both and not leak:
        print("  What is customer?: PASS (both IDs / labels; no MEASURE() / dollar leak)")
        return True
    if not both:
        print("  What is customer?: FAIL (did not return both id:sold-to and id:loading-authorized-party)")
        return False
    print("  What is customer?: FAIL (dollar / MEASURE leak)")
    return False


def lookup_function_exists(w: WorkspaceClient, fq_lookup: str) -> bool:
    """Best-effort: do not print warehouse id. SQL via warehouse is done in 10."""
    # 10 already created or fell back. We detect by trying get on the function
    # through the SQL warehouses API would print ids — skip. Infer from name
    # by listing functions in the schema if the SDK exposes it.
    try:
        catalog, schema, name = fq_lookup.split(".")
        for fn in w.functions.list(catalog_name=catalog, schema_name=schema):
            if getattr(fn, "name", "") == name or getattr(fn, "full_name", "") == fq_lookup:
                return True
    except Exception:
        return False
    return False


def upsert_search_agent(
    w: WorkspaceClient,
    cfg,
    ids: dict[str, str],
    use_function: bool,
) -> tuple[str | None, list[str]]:
    description = "search only. Preferred label + stable ID. Never a dollar."
    include_lookup = use_function
    payload = serialized_space(ids, use_function, include_lookup)
    spaces = list_spaces(w)
    print(f"  existing agents = {len(spaces)}")
    for s in spaces:
        print(f"    - {s.title}")
        if (getattr(s, "title", "") or "") == CERTIFIED_TITLE:
            print("      (certified agent listed; will not update it)")

    agent = find_by_title(spaces, TITLE)
    space_id = None

    def _create_or_update(body: str) -> str:
        if agent:
            print(f"\nUpdating existing {TITLE!r} (title only; not {CERTIFIED_TITLE!r})")
            w.genie.update_space(
                space_id=agent.space_id,
                title=TITLE,
                description=description,
                serialized_space=body,
                warehouse_id=cfg.warehouse_id,
            )
            print("Updated serialized_space (cv tables; no Metric Views).")
            return agent.space_id
        print(f"\nCreating {TITLE!r} (cv search only)")
        created = w.genie.create_space(
            warehouse_id=cfg.warehouse_id,
            serialized_space=body,
            title=TITLE,
            description=description,
            parent_path=parent_path(w),
        )
        print("Created new agent.")
        return created.space_id

    try:
        space_id = _create_or_update(payload)
    except DatabricksError as exc:
        if include_lookup:
            print(
                f"create/update with cv_lookup source failed: {scrub(exc)}\n"
                "Retrying with the three cv tables only (example SQL still uses lookup/join)."
            )
            payload = serialized_space(ids, use_function, include_lookup_source=False)
            try:
                space_id = _create_or_update(payload)
            except DatabricksError as exc2:
                print(f"create/update failed: {scrub(exc2)}")
                print("See scripts/11_cv_search_genie.md for official UI fallback.")
                return None, []
        else:
            print(f"create/update failed: {scrub(exc)}")
            print("See scripts/11_cv_search_genie.md for official UI fallback.")
            return None, []

    attached: list[str] = []
    try:
        got = w.genie.get_space(space_id, include_serialized_space=True)
        attached = source_identifiers(getattr(got, "serialized_space", None))
        print(f"\nSearch agent title = {getattr(got, 'title', TITLE)}")
        print(f"  attached sources ({len(attached)}):")
        for ident in attached:
            print(f"    - {ident}")
    except DatabricksError as exc:
        print(f"get_space failed: {scrub(exc)}")
        attached = [ids["term"], ids["alias"], ids["map"]]

    forbidden = []
    for ident in attached:
        short = ident.split(".")[-1].lower()
        if short.startswith("unbilled") or short.startswith("fct_") or short.startswith("raw_"):
            forbidden.append(ident)
        if short in {"gold_kpi_value", "dim_customer", "sap_partner", "sf_account", "tas_lift", "ra_business_associate", "dim_kpi_metadata", "contract_vs_list_usd", "temp_adjusted_delivered_usd"}:
            forbidden.append(ident)
    if forbidden:
        print(f"FAIL: search agent attached forbidden sources: {forbidden}")
        return space_id, attached
    return space_id, attached


def assert_certified_untouched(w: WorkspaceClient, cfg) -> tuple[object | None, list[str], bool]:
    """Read-only. Do not update. Fail only if cv_* is now attached."""
    fq = f"{cfg.catalog}.{cfg.schema}"
    expected = {
        f"{fq}.unbilled_usd",
        f"{fq}.contract_vs_list_usd",
        f"{fq}.temp_adjusted_delivered_usd",
    }
    spaces = list_spaces(w)
    certified = find_by_title(spaces, CERTIFIED_TITLE)
    if not certified:
        print(f"\nWARN: {CERTIFIED_TITLE!r} not in list_spaces (cannot live-ask).")
        return None, [], False
    try:
        got = w.genie.get_space(certified.space_id, include_serialized_space=True)
    except DatabricksError as exc:
        print(f"get_space({CERTIFIED_TITLE!r}) failed: {scrub(exc)}")
        return certified, [], False
    attached = source_identifiers(getattr(got, "serialized_space", None))
    print(f"\nCertified agent title = {getattr(got, 'title', CERTIFIED_TITLE)} (read-only; not updated)")
    print(f"  attached sources ({len(attached)}):")
    for ident in attached:
        print(f"    - {ident}")
    hunt_stubs = {"dim_customer", "sap_partner", "sf_account", "tas_lift", "ra_business_associate"}
    stub_hit = [i for i in attached if i.split(".")[-1].lower() in hunt_stubs]
    cv_hit = [i for i in attached if re.search(r"(^|[.])cv_", i)]
    changed = bool(cv_hit or stub_hit)
    if stub_hit:
        print(f"  FAIL: certified agent now has hunt stubs attached: {stub_hit}")
    if cv_hit:
        print(f"  FAIL: certified agent now has cv_* attached: {cv_hit}")
    elif expected.issubset(set(attached)) and not stub_hit:
        print("  PASS: still the three Metric Views; no cv_*; no hunt stubs.")
    else:
        missing = expected - set(attached)
        print(f"  WARN: get_space missing {sorted(missing)} (not treated as a cv_* change)")
    return certified, attached, changed


def main() -> int:
    cfg = settings()
    ids = table_ids(cfg.catalog, cfg.schema)
    fq = f"{cfg.catalog}.{cfg.schema}"
    print("Genie Agent — O2C vocabulary search (second agent; search only)")
    print(f"  catalog.schema = {fq}")
    print("  token          = (set, not printed)")
    print("  host           = (from .env, not printed)")
    print("  warehouse      = (from .env, id not printed)")
    print(f"  will not update {CERTIFIED_TITLE!r}")

    w = WorkspaceClient(host=cfg.host, token=cfg.token)

    try:
        use_function = lookup_function_exists(w, ids["lookup"])
    except Exception:
        use_function = False
    print(f"  cv_lookup function attachable = {use_function}")

    try:
        space_id, attached = upsert_search_agent(w, cfg, ids, use_function)
    except DatabricksError as exc:
        print(f"list/create failed: {scrub(exc)}")
        print("Free gap or entitlement issue. See scripts/11_cv_search_genie.md.")
        return 2

    if space_id is None:
        return 3

    forbidden = [
        i
        for i in attached
        if i.split(".")[-1].lower()
        in {
            "unbilled_usd",
            "contract_vs_list_usd",
            "temp_adjusted_delivered_usd",
            "gold_kpi_value",
            "dim_customer",
            "sap_partner",
            "sf_account",
            "tas_lift",
            "ra_business_associate",
            "dim_kpi_metadata",
        }
        or i.split(".")[-1].lower().startswith(("fct_", "raw_"))
    ]
    if forbidden:
        print(f"FAIL: search agent attached KPI/fact sources: {forbidden}")
        return 4

    sql_text, _answer, blob, blocker = ask(w, space_id, Q_CUSTOMER)
    if blocker:
        print(f"  What is customer?: FAIL ({blocker})")
        search_ok = False
    else:
        search_ok = grade_search(sql_text, blob or "")

    certified, cert_attached, cert_changed = assert_certified_untouched(w, cfg)
    cert_sql = cert_answer = cert_blob = None
    if certified and not cert_changed:
        print(f"\n── certified Genie live-ask (read-only contrast) ──")
        print("Expected pedagogy: it will guess (no map attached). That is OK.")
        cert_sql, cert_answer, cert_blob, cert_blocker = ask(w, certified.space_id, Q_CUSTOMER)
        if cert_blocker:
            print(f"  certified ask blocker (not a fail): {cert_blocker}")
        else:
            print("  certified guess recorded (do not fail the script for a guess).")

    print("\n── live test ────────────────────────────────────────────────")
    print(f"  search agent     = {TITLE}")
    print(f"  search sources   = {attached}")
    print(f"  search customer  = {'PASS' if search_ok else 'FAIL'}")
    print(f"  certified title  = {CERTIFIED_TITLE}")
    print(f"  certified sources= {cert_attached}")
    if cert_sql:
        print("  certified SQL    =")
        print(cert_sql)
    if cert_answer:
        print(f"  certified answer = {cert_answer}")

    if cert_changed:
        print("FAIL: certified agent was changed (cv_* attached).")
        return 6
    if not search_ok:
        print("FAIL: vocabulary-search Genie did not return both senses without a dollar.")
        return 5
    print("PASS: search Genie returned both customer senses; certified agent untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
