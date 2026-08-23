#!/usr/bin/env python3
"""07_genie.py — one Genie Agent for all three certified Metric Views.

Run AFTER 08_complex_metric.py and 09_temp_adjusted.py so
contract_vs_list_usd and temp_adjusted_delivered_usd exist.
Ad hoc KPI path only. Points at the three Metric Views. Does not author
a second formula. Does not Export-to-metric-view. Never prints the
token, host, or warehouse id. Demo 2 / Track B. Not MetricFlow.
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

TITLE = "O2C certified KPIs"
OLD_TITLE = "O2C Unbilled (certified)"

Q_UNBILLED = "What is total unbilled USD as of 2026-08-01?"
Q_CONTRACT = "What is delivered contract USD as of 2026-08-01?"
Q_TEMP = "What is temp-adjusted delivered USD as of 2026-08-01?"


def _hid(label: str) -> str:
    return (label.encode().hex() + "0" * 32)[:32]


def view_ids(catalog: str, schema: str) -> dict[str, str]:
    fq = f"{catalog}.{schema}"
    return {
        "unbilled": f"{fq}.unbilled_usd",
        "contract": f"{fq}.contract_vs_list_usd",
        "temp": f"{fq}.temp_adjusted_delivered_usd",
        "catalog": f"{fq}.dim_kpi_metadata",
    }


def general_instruction_text(views: dict[str, str]) -> str:
    """Configure → Text / General instructions (serialized_space.instructions.text_instructions).

    Official Genie API: this is the UI Text-tab field. update_space has no separate
    general_instructions / sql_instructions parameter. Write one content string so
    the Text box and the conversation prompt stay the same on the next script run.
    """
    unbilled, contract, temp = views["unbilled"], views["contract"], views["temp"]
    catalog = views["catalog"]
    return f"""---
name: o2c-certified-kpis
description: Look up dim_kpi_metadata.status first. MEASURE() only when status = approved. If drifted, proposed, or archived, do not give a number. As-of is 2026-08-01.
---

# Catalog status (do this first, every turn)

STOP. Query {catalog} before any MEASURE().

SELECT kpi_id, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
-- or KPI-O2C-CONTRACT-VS-LIST-USD / KPI-O2C-TEMP-ADJUSTED-USD

Read the status cell.
- approved → immediately MEASURE() on the matching Metric View in this same turn and report the official dollars and tickets. Do not stop after the status query. Do not ask the user to proceed.
- drifted / proposed / archived → reply only: "The number is not approved (status=<status>). I will not give a number." Stop. Do not MEASURE(). Do not include a dollar figure, ticket count, or remembered value.

{catalog} is status only. It is not the number. Gold is not a source.

# Route

If the question does not name a KPI, ask which one (Unbilled / contract-vs-list / temp-adjusted). Do not guess between contract-vs-list and temp-adjusted on a vague delivered USD.

- Unbilled USD → {unbilled}, measure unbilled_usd. Grains: enterprise | payer | sold_to | site. Unsliced = enterprise.
- Contract vs list / delivered contract USD → {contract}, measure delivered_contract_usd. Grains: enterprise | sold_to | product. Unsliced = enterprise. Other measures on that view are query-only, still MEASURE().
- Temp-adjusted delivered USD → {temp}, measure temp_adjusted_usd. Grains: enterprise | product | site. Unsliced = enterprise.

# Do

- Lookup status first. MEASURE() only when status = approved.
- Say payer, sold-to, or site. Never say "customer".
- If they name a grain, GROUP BY only that grain.
- Filter the named party with equality on that role only (WHERE payer = 'Apex Fuels LLC').
- If they asked for a payer total, lead with the payer number. Extra product/site charts only if they asked.
- A sold-to lifting at another site is a real cross-terminal ticket, not a data error.

# Don't

- Do not ILIKE '%name%' OR across payer / sold_to / site.
- Do not GROUP BY ALL extra dimensions unless they asked for a breakdown.
- Do not invent a second formula, query fct_unbilled or raw_*, or use Export-to-metric-view.
- Do not author SQL for the user to run. Do not Export-to-metric-view.
- Do not call sold-to a "customer location."
- Do not give a number when status is drifted, proposed, or archived.

# Example

Status check then approved Unbilled for payer Apex Fuels LLC:

SELECT status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD';
-- only if status = approved:
SELECT payer, MEASURE(unbilled_usd) AS unbilled_usd, MEASURE(unbilled_ticket_count) AS tickets
FROM {unbilled}
WHERE payer = 'Apex Fuels LLC'
GROUP BY payer
"""


def serialized_space(views: dict[str, str]) -> str:
    unbilled, contract, temp = views["unbilled"], views["contract"], views["temp"]
    catalog = views["catalog"]
    q_ids = [_hid(f"q{i}") for i in range(1, 13)]
    e_ids = [_hid(f"e{i}") for i in range(1, 13)]
    i1 = _hid("i1")
    q_status = _hid("qstatus")
    e_status = _hid("estatus")
    samples = [
        {"id": q_status, "question": ["What is the catalog status of Unbilled USD?"]},
        {"id": q_ids[0], "question": [Q_UNBILLED]},
        {"id": q_ids[1], "question": ["What is unbilled USD by payer?"]},
        {"id": q_ids[2], "question": ["What is unbilled USD by sold_to?"]},
        {"id": q_ids[3], "question": ["What is unbilled USD by site?"]},
        {"id": q_ids[4], "question": [Q_CONTRACT]},
        {"id": q_ids[5], "question": ["What is delivered contract USD by product?"]},
        {"id": q_ids[6], "question": ["What is delivered contract USD by sold_to?"]},
        {"id": q_ids[7], "question": [Q_TEMP]},
        {"id": q_ids[8], "question": ["What is temp-adjusted USD by site?"]},
        {"id": q_ids[9], "question": ["What is temp-adjusted USD by product?"]},
        {"id": q_ids[10], "question": ["What is unbilled USD for payer Apex Fuels LLC?"]},
        {"id": q_ids[11], "question": ["What is unbilled USD by sold_to for Apex Fuels Houston Rack?"]},
    ]
    examples = [
        {
            "id": e_status,
            "question": ["What is the catalog status of Unbilled USD?"],
            "sql": [
                f"SELECT kpi_id, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'"
            ],
        },
        {
            "id": e_ids[0],
            "question": [Q_UNBILLED],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'",
                "SELECT MEASURE(unbilled_usd) AS unbilled_usd, "
                f"MEASURE(unbilled_ticket_count) AS tickets FROM {unbilled}",
            ],
        },
        {
            "id": _hid("e_approved_unbilled"),
            "question": ["What is official approved total unbilled USD as of 2026-08-01?"],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'",
                "SELECT MEASURE(unbilled_usd) AS unbilled_usd, "
                f"MEASURE(unbilled_ticket_count) AS tickets FROM {unbilled}",
            ],
        },
        {
            "id": e_ids[1],
            "question": ["What is unbilled USD by payer?"],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'",
                f"SELECT payer, MEASURE(unbilled_usd) AS unbilled_usd FROM {unbilled} GROUP BY payer",
            ],
        },
        {
            "id": e_ids[2],
            "question": ["What is unbilled USD by sold_to?"],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'",
                f"SELECT sold_to, MEASURE(unbilled_usd) AS unbilled_usd FROM {unbilled} GROUP BY sold_to",
            ],
        },
        {
            "id": e_ids[3],
            "question": ["What is unbilled USD by site?"],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'",
                f"SELECT site, MEASURE(unbilled_usd) AS unbilled_usd FROM {unbilled} GROUP BY site",
            ],
        },
        {
            "id": e_ids[4],
            "question": [Q_CONTRACT],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-CONTRACT-VS-LIST-USD'",
                "SELECT MEASURE(delivered_contract_usd) AS delivered_contract_usd, "
                f"MEASURE(delivered_ticket_count) AS tickets FROM {contract}",
            ],
        },
        {
            "id": e_ids[5],
            "question": ["What is delivered contract USD by product?"],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-CONTRACT-VS-LIST-USD'",
                f"SELECT product, MEASURE(delivered_contract_usd) AS delivered_contract_usd FROM {contract} GROUP BY product",
            ],
        },
        {
            "id": e_ids[6],
            "question": ["What is delivered contract USD by sold_to?"],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-CONTRACT-VS-LIST-USD'",
                f"SELECT sold_to, MEASURE(delivered_contract_usd) AS delivered_contract_usd FROM {contract} GROUP BY sold_to",
            ],
        },
        {
            "id": e_ids[7],
            "question": [Q_TEMP],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-TEMP-ADJUSTED-USD'",
                "SELECT MEASURE(temp_adjusted_usd) AS temp_adjusted_usd, "
                f"MEASURE(delivered_ticket_count) AS tickets FROM {temp}",
            ],
        },
        {
            "id": e_ids[8],
            "question": ["What is temp-adjusted USD by site?"],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-TEMP-ADJUSTED-USD'",
                f"SELECT site, MEASURE(temp_adjusted_usd) AS temp_adjusted_usd FROM {temp} GROUP BY site",
            ],
        },
        {
            "id": e_ids[9],
            "question": ["What is temp-adjusted USD by product?"],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-TEMP-ADJUSTED-USD'",
                f"SELECT product, MEASURE(temp_adjusted_usd) AS temp_adjusted_usd FROM {temp} GROUP BY product",
            ],
        },
        {
            "id": e_ids[10],
            "question": ["What is unbilled USD for payer Apex Fuels LLC?"],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'",
                "SELECT payer, MEASURE(unbilled_usd) AS unbilled_usd, "
                "MEASURE(unbilled_ticket_count) AS tickets "
                f"FROM {unbilled} WHERE payer = 'Apex Fuels LLC' GROUP BY payer",
            ],
        },
        {
            "id": e_ids[11],
            "question": ["What is unbilled USD by sold_to for Apex Fuels Houston Rack?"],
            "sql": [
                f"SELECT kpi_id, name, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'",
                "SELECT sold_to, MEASURE(unbilled_usd) AS unbilled_usd "
                f"FROM {unbilled} WHERE sold_to = 'Apex Fuels Houston Rack' GROUP BY sold_to",
            ],
        },
    ]
    space = {
        "version": 2,
        "config": {
            "sample_questions": sorted(samples, key=lambda x: x["id"]),
        },
        "data_sources": {
            "metric_views": sorted(
                [
                    {
                        "identifier": unbilled,
                        "description": [
                            "Unbilled USD Metric View. MEASURE(unbilled_usd) only when dim_kpi_metadata.status = approved."
                        ],
                    },
                    {
                        "identifier": contract,
                        "description": [
                            "Delivered contract USD. Published measure delivered_contract_usd. MEASURE() only when status = approved."
                        ],
                    },
                    {
                        "identifier": temp,
                        "description": [
                            "Temp-adjusted delivered USD. Published measure temp_adjusted_usd. MEASURE() only when status = approved."
                        ],
                    },
                ],
                key=lambda x: x["identifier"],
            ),
            "tables": sorted(
                [
                    {
                        "identifier": catalog,
                        "description": [
                            "KPI catalog. Look up status first. MEASURE() only when status = approved. If drifted, proposed, or archived: not approved (status=<status>) and do not give a number."
                        ],
                    }
                ],
                key=lambda x: x["identifier"],
            ),
        },
        "instructions": {
            # Configure → Text / General instructions. Official seat is text_instructions
            # (single content string). No separate general_instructions field on update_space.
            "text_instructions": [
                {
                    "id": i1,
                    "content": [general_instruction_text(views)],
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
    for key in ("metric_views", "tables"):
        for item in sources.get(key) or []:
            ident = item.get("identifier") if isinstance(item, dict) else None
            if ident:
                ids.append(ident)
    return ids


def extract_sql_and_answer(msg) -> tuple[str | None, str | None, str]:
    """Return (sql, answer_text, blob_for_numbers)."""
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


def sql_is_forbidden(sql_text: str) -> bool:
    low = sql_text.lower()
    if "fct_unbilled" in low:
        return True
    if "raw_tickets" in low or "raw_parties" in low or "raw_products" in low:
        return True
    if "raw_" in low and "from" in low:
        return True
    if "gallons_net" in low:
        return True
    if "contract_price" in low and "*" in low:
        return True
    return False


def has_measure_on(sql_text: str, view_ident: str) -> bool:
    low = sql_text.lower()
    if "measure(" not in low:
        return False
    view_low = view_ident.lower()
    short = view_low.split(".")[-1]
    return view_low in low or f".{short}" in low or f"`{short}`" in low


def numbers_match(blob: str, dollars: str, tickets: str) -> bool:
    compact = re.sub(r"[,\s]", "", blob)
    return dollars.replace(",", "") in compact and tickets in compact


def ask(w: WorkspaceClient, space_id: str, question: str):
    print(f"\nAsking: {question}")
    try:
        msg = w.genie.start_conversation_and_wait(
            space_id=space_id,
            content=question,
            timeout=timedelta(minutes=8),
        )
    except DatabricksError as exc:
        print(f"  conversation failed: {getattr(exc, 'error_code', None)} {exc}")
        return None, None, None, f"API blocker: {getattr(exc, 'error_code', None)} {exc}"
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


def grade(
    label: str,
    sql_text: str | None,
    blob: str,
    view_ident: str,
    dollars: str,
    tickets: str,
) -> bool:
    if not sql_text:
        print(f"  {label}: FAIL (no SQL)")
        return False
    if sql_is_forbidden(sql_text):
        print(f"  {label}: FAIL (SQL used fct_unbilled / gallons_net * contract / raw_*)")
        return False
    used_measure = has_measure_on(sql_text, view_ident)
    matched = numbers_match(blob or "", dollars, tickets)
    if used_measure and matched:
        print(f"  {label}: PASS (MEASURE() on {view_ident.split('.')[-1]}; {dollars} / {tickets})")
        return True
    if used_measure and not matched:
        print(f"  {label}: FAIL (MEASURE() on the right family, numbers did not match {dollars} / {tickets})")
        return False
    if matched:
        print(f"  {label}: FAIL (numbers match but SQL is not MEASURE() on {view_ident.split('.')[-1]})")
        return False
    print(f"  {label}: FAIL (need MEASURE() on {view_ident.split('.')[-1]} and {dollars} / {tickets})")
    return False


def main() -> int:
    cfg = settings()
    views = view_ids(cfg.catalog, cfg.schema)
    print("Genie Agent — ad hoc KPI path for three Metric Views + dim_kpi_metadata")
    print(f"  catalog.schema = {cfg.catalog}.{cfg.schema}")
    print("  sources        =")
    for key in ("unbilled", "contract", "temp", "catalog"):
        print(f"    - {views[key]}")
    print("  token          = (set, not printed)")
    print("  host           = (from .env, not printed)")
    print("  warehouse      = (from .env, id not printed)")

    w = WorkspaceClient(host=cfg.host, token=cfg.token)

    try:
        spaces = list_spaces(w)
    except DatabricksError as exc:
        print(f"list_spaces failed: {getattr(exc, 'error_code', None)} {exc}")
        print("Free gap or entitlement issue. See scripts/07_genie.md.")
        return 2

    print(f"  existing agents = {len(spaces)}")
    for s in spaces:
        print(f"    - {s.title}")

    new_agent = find_by_title(spaces, TITLE)
    old_agent = find_by_title(spaces, OLD_TITLE)
    leftover_old = False
    space_id = None
    payload = serialized_space(views)
    description = (
        "Ad hoc KPI path for the three Metric Views plus dim_kpi_metadata. "
        "Lookup status first. MEASURE() only when status = approved."
    )

    if new_agent:
        space_id = new_agent.space_id
        print(f"\nUpdating existing {TITLE!r}")
        try:
            w.genie.update_space(
                space_id=space_id,
                title=TITLE,
                description=description,
                serialized_space=payload,
                warehouse_id=cfg.warehouse_id,
            )
            print("Updated serialized_space (3 metric views + dim_kpi_metadata).")
        except DatabricksError as exc:
            print(f"update_space failed: {getattr(exc, 'error_code', None)} {exc}")
            print("See scripts/07_genie.md for official UI fallback.")
            return 3
        if old_agent:
            leftover_old = True
    elif old_agent:
        space_id = old_agent.space_id
        print(f"\nUpdating leftover {OLD_TITLE!r} → {TITLE!r} (same agent, three views)")
        try:
            w.genie.update_space(
                space_id=space_id,
                title=TITLE,
                description=description,
                serialized_space=payload,
                warehouse_id=cfg.warehouse_id,
            )
            print("Updated title + serialized_space.")
        except DatabricksError as exc:
            print(f"update_space failed: {getattr(exc, 'error_code', None)} {exc}")
            print(f"Old agent {OLD_TITLE!r} is leftover (update not applied).")
            leftover_old = True
            print(f"Creating {TITLE!r} pointed at the three Metric Views")
            try:
                created = w.genie.create_space(
                    warehouse_id=cfg.warehouse_id,
                    serialized_space=payload,
                    title=TITLE,
                    description=description,
                    parent_path=parent_path(w),
                )
                space_id = created.space_id
                print("Created new agent.")
            except DatabricksError as exc2:
                print(f"create_space failed: {getattr(exc2, 'error_code', None)} {exc2}")
                print("See scripts/07_genie.md for official UI fallback.")
                return 3
    else:
        print(f"\nCreating {TITLE!r} pointed at the three Metric Views")
        try:
            created = w.genie.create_space(
                warehouse_id=cfg.warehouse_id,
                serialized_space=payload,
                title=TITLE,
                description=description,
                parent_path=parent_path(w),
            )
            space_id = created.space_id
            print("Created new agent.")
        except DatabricksError as exc:
            print(f"create_space failed: {getattr(exc, 'error_code', None)} {exc}")
            print("See scripts/07_genie.md for official UI fallback.")
            return 3

    if leftover_old:
        print(
            f"NOTE: leftover agent titled {OLD_TITLE!r} still exists. "
            "Not deleted (trash_space exists but was not used)."
        )

    attached: list[str] = []
    try:
        got = w.genie.get_space(space_id, include_serialized_space=True)
        attached = source_identifiers(getattr(got, "serialized_space", None))
        print(f"\nAgent title = {getattr(got, 'title', TITLE)}")
        print(f"  attached sources ({len(attached)}):")
        for ident in attached:
            print(f"    - {ident}")
    except DatabricksError as exc:
        print(f"get_space failed: {getattr(exc, 'error_code', None)} {exc}")
        print(f"Agent title = {TITLE} (get_space blocked; assuming create/update payload)")
        attached = list(views.values())

    expected = {views["unbilled"], views["contract"], views["temp"], views["catalog"]}
    attached_set = set(attached)
    if not expected.issubset(attached_set):
        missing = expected - attached_set
        print(f"WARN: attached sources missing {sorted(missing)}")
    else:
        print("  3 Metric Views + dim_kpi_metadata attached (no fct/raw/gold).")
    extra = [i for i in attached if i not in expected]
    if extra:
        print(f"WARN: extra sources attached: {extra}")

    cases = [
        ("Unbilled", Q_UNBILLED, views["unbilled"], "179934", "12"),
        ("Contract", Q_CONTRACT, views["contract"], "110064", "7"),
        ("Temp-adjusted", Q_TEMP, views["temp"], "256066", "17"),
    ]
    results: list[bool] = []
    blockers: list[str] = []
    for label, question, view_ident, dollars, tickets in cases:
        sql_text, _answer, blob, blocker = ask(w, space_id, question)
        if blocker:
            blockers.append(f"{label}: {blocker}")
            print(f"  {label}: FAIL ({blocker})")
            results.append(False)
            continue
        results.append(grade(label, sql_text, blob or "", view_ident, dollars, tickets))

    print("\n── live test ────────────────────────────────────────────────")
    print(f"  agent title     = {TITLE}")
    print(f"  attached        = {len(expected & attached_set)} of 4 expected (3 MV + catalog)")
    for label, ok in zip((c[0] for c in cases), results):
        print(f"  {label:14} = {'PASS' if ok else 'FAIL'}")
    if blockers:
        print("  API blockers:")
        for b in blockers:
            print(f"    - {b}")

    if all(results):
        print("PASS: one agent, MEASURE() on each approved view, numbers match.")
        return 0
    print("FAIL: one or more live questions did not MEASURE() the right view with the official number.")
    return 5


if __name__ == "__main__":
    raise SystemExit(main())
