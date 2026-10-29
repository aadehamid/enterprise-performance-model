"""Outside context from Parallel Decisions: real public events beside the demo's synthetic data (use cases 19 to 21).

    uv run --group outside python -m pricing_demo.outside plan               # the calls each step needs, and how many are cached
    uv run --group outside python -m pricing_demo.outside run --step smoke   # one call, to check the key and the response
    uv run --group outside python -m pricing_demo.outside run --step events  # then monthly, diagnosis, forward

Four steps ask Parallel's Decisions API typed questions and keep every response in data/parallel/, so the tables are
built from the cache and a rerun spends nothing (a cached request is never sent again):
- events: whether each of the scenario's events in reference_data_hub.market_event happened, one call per event;
- monthly: a scan of each MPC refining region for each month from the window's first full one, November 2023, to
  October 2026, one call per region and month;
- diagnosis: what outside factor most affected each decision in the decision log in the 30 days after it, one call
  per decision, from the decision log's columns the agents see (never from decision_truth);
- forward: the three months after the window, by region: announced maintenance, OPEC+ and policy dates, EIA's outlook
  for diesel prices and NOAA's for temperature. A forward answer is always an inference, never an observation.

Each call sends the context in `state` and named questions in `questions`; the response holds a typed answer per
question and the citations the call drew on (Parallel, "Decisions API quickstart", docs.parallel.ai, read 2026-10-28).
The demo uses two question types: a noul, one probability that the condition is true, and a choice, a probability for
each option and a confidence from their spread (Typesafe, "Noul" and "Choice", docs.typesafe.ai, read 2026-10-28).
interpret() turns each answer into a value and a label:
- observed: a noul about the past at 0.7 or more (yes) or 0.3 or less (no), Typesafe's suggested starting thresholds;
- inferred: a choice about the past with a confidence of at least CHOICE_CONFIDENCE (the demo's choice), and every
  forward answer that is not unknown;
- unknown: a refusal, a noul between 0.3 and 0.7, or a choice below CHOICE_CONFIDENCE. These go to a person.
The citations belong to the call, not to one question, so each answer row points to its call's citations.

The key is PARALLEL_API_KEY, from the environment, the demo's .env or ~/.config/parallel/api.env, and is never printed. The calls go
through the parallel-web SDK's generic client.post, which keeps its authentication, retries and typed errors; the SDK
has no Decisions resource of its own.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re

from .config import DATA, WINDOW_END, WINDOW_START, env
from .decisions import IDENTIFIERS, REFINERY_IRI, REFINERY_SLUG

CACHE = os.path.join(DATA, "parallel")
STEPS = ("smoke", "events", "monthly", "diagnosis", "forward")
YES, NO = 0.7, 0.3  # Typesafe's suggested starting thresholds for a noul
CHOICE_CONFIDENCE = 0.3  # the demo's floor for a choice to count as an inference, not unknown
DIAGNOSIS_DAYS = 30
FORWARD_MONTHS = 3
ONTOLOGY = "https://w3id.org/lsc/ontology/modules/"
PRODUCT = ONTOLOGY + "party/product/"
SERIES = ONTOLOGY + "market-data/series/"
MEASURE = ONTOLOGY + "kpi/measure/"

# MPC's three refining regions (market-data regions.csv), the states their refineries sit in (ref-mpc), and the
# region's crack series (market-data series.csv). The refineries come from the generated refinery table.
REGIONS = {
    "Gulf Coast": {"slug": "gulf-coast", "where": "the U.S. Gulf Coast (Texas and Louisiana)",
                   "series": "crack-gulf-coast-3-2-1"},
    "Mid-Continent": {"slug": "mid-continent", "where": "the U.S. Mid-Continent (the Midwest, Rocky Mountains and West Texas)",
                      "series": "crack-mid-continent-3-2-1"},
    "West Coast": {"slug": "west-coast", "where": "the U.S. West Coast and Alaska (California, Washington and Alaska)",
                   "series": "crack-west-coast-3-2-1"},
}

# Each question names the ontology terms it is about: products (party), and measures (kpi) by their measure IDs.
# The forward look matches a signal to past decisions through the measures and the region's refineries; a forward
# question's signal says what an affirmative or directional answer means.
MONTHLY = {
    "refinery_disruption": {"type": "noul", "products": ["gasoline", "distillates"], "measures": ["crude-utilization"],
                            "ask": "Did an unplanned refinery outage, fire, hurricane or other weather event disrupt refining in {where} during {month}?"},
    "margin_driver": {"type": "choice", "products": ["gasoline", "distillates"], "measures": ["crack-spreads"],
                      "ask": "What most drove refining margins for refiners in {where} during {month}?",
                      "criteria": {"crude_supply": "Crude oil supply or crude price changes",
                                   "product_inventories": "High or low gasoline and diesel inventories",
                                   "weather": "Weather or storms disrupting refining or logistics",
                                   "policy": "Government policy, export restrictions or emergency stock releases",
                                   "logistics": "Freight, shipping or pipeline constraints",
                                   "demand": "Changes in fuel demand"}},
    "policy_action": {"type": "noul", "products": ["distillates", "gasoline"], "measures": ["distillate-prices"],
                      "ask": "Did a government action affecting U.S. refined products (an export restriction, a strategic reserve release, sanctions or a fuel-standard change) take effect during {month}?"},
}
DIAGNOSIS = {
    "outside_cause": {"type": "choice", "products": [], "measures": [],
                      "ask": "Which outside factor most affected how this decision turned out in the {days} days after it was made?",
                      "criteria": {"weather": "Weather, a hurricane or another natural event",
                                   "crude_market": "Crude oil prices or supply",
                                   "product_market": "Gasoline or diesel prices, inventories or demand",
                                   "policy": "Government policy, export restrictions or emergency stock releases",
                                   "logistics": "Freight, shipping or pipeline constraints",
                                   "none": "No major outside factor"}},
    "adverse_event": {"type": "noul", "products": [], "measures": [],
                      "ask": "Did a real-world event in the {days} days after the decision make its expected outcome less likely?"},
}
FORWARD = {
    "maintenance_announced": {"type": "noul", "signal": "Refinery maintenance is reported in {month}", "products": ["gasoline", "distillates"], "measures": ["crude-utilization"],
                              "ask": "Has planned refinery maintenance (a turnaround) been announced or reported for refineries in {where} during {month}?"},
    "opec_meeting": {"type": "noul", "signal": "An OPEC+ meeting is scheduled in {month}", "products": [], "measures": ["crude-prices"],
                     "ask": "Is an OPEC+ ministerial or monitoring committee meeting scheduled during {month}?"},
    "policy_deadline": {"type": "noul", "signal": "A U.S. fuel-policy date falls in {month}", "products": ["distillates", "gasoline"], "measures": ["distillate-prices"],
                        "ask": "Is a U.S. federal fuel-policy deadline or effective date (renewable fuel rules, sanctions, export rules or fuel taxes) scheduled during {month}?"},
    "distillate_outlook": {"type": "choice", "signal": "EIA's outlook has diesel prices {value} in {month} than in October 2026", "products": ["distillates"], "measures": ["distillate-prices"],
                           "ask": "According to the U.S. EIA's most recent Short-Term Energy Outlook, how are U.S. diesel prices expected to move in {month} compared with October 2026?",
                           "criteria": {"higher": "Higher than in October 2026", "about_the_same": "About the same",
                                        "lower": "Lower than in October 2026"}},
    "weather_outlook": {"type": "choice", "signal": "NOAA's outlook has temperatures {value} in {month}", "products": ["distillates"], "measures": ["crude-utilization"],
                        "ask": "According to NOAA's latest seasonal outlook, how are temperatures expected to compare with normal in {where} during {month}?",
                        "criteria": {"above_normal": "Above normal", "near_normal": "Near normal", "below_normal": "Below normal"}},
}
QUESTIONS = {"monthly": MONTHLY, "diagnosis": DIAGNOSIS, "forward": FORWARD}
EVENT_QUESTION = {"type": "noul", "ask": "Did this event happen as described, within these dates?"}


def month_label(day):
    return day.strftime("%B %Y")


def add_months(day, n):
    m = day.month - 1 + n
    return dt.date(day.year + m // 12, m % 12 + 1, 1)


def full_months():
    """The months the scan asks about: from the window's first full month, November 2023, to October 2026. The window
    ends on 20 October 2026, the last EIA spot date; October still counts, since the scan asks about the month."""
    first = add_months(WINDOW_START, 1) if WINDOW_START.day > 1 else WINDOW_START.replace(day=1)
    months, m = [], first
    while m <= WINDOW_END:
        months.append(m)
        m = add_months(m, 1)
    return months


def forward_months():
    return [add_months(WINDOW_END, n) for n in range(1, FORWARD_MONTHS + 1)]


def question_body(spec, **fields):
    body = {"type": spec["type"], "instructions": spec["ask"].format(**fields)}
    if spec["type"] == "choice":
        body["criteria"] = spec["criteria"]
    return body


def request_key(body):
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:16]


def requests(out):
    """Every request each step sends, in order: [(step, request_id, body, context)], from the generated tables."""
    refineries = {r[0]: {"name": r[1], "region": r[2]} for r in out["production_accounting"]["refinery"].rows}
    found = [("smoke", "smoke", {"state": {"region": "U.S. Gulf Coast refining (PADD 3)", "period": "October 2026"},
                                  "questions": {"hurricane_disruption": {
                                      "type": "noul",
                                      "instructions": "Did a hurricane or tropical storm disrupt U.S. Gulf Coast refinery operations during October 2026?"}}},
              {})]
    for r in out["reference_data_hub"]["market_event"].rows:
        event_id, key, title, category, region, code, start, end = r[:8]
        state = {"event": title, "region": region, "from": start.isoformat(), "to": end.isoformat()}
        if code:
            state["refinery"] = refineries[code]["name"]
        found.append(("events", f"event-{key}", {"state": state, "questions": {"happened": question_body(EVENT_QUESTION)}},
                      {"event_id": event_id}))
    for region, info in REGIONS.items():
        for m in full_months():
            fields = {"where": info["where"], "month": month_label(m)}
            found.append(("monthly", f"monthly-{info['slug']}-{m:%Y-%m}",
                          {"state": {"region": f"MPC's {region} refining region", "period": month_label(m)},
                           "questions": {k: question_body(q, **fields) for k, q in MONTHLY.items()}},
                          {"region": region, "start": m, "end": add_months(m, 1) - dt.timedelta(days=1)}))
    for r in out["aspen_pims"]["decision_log"].rows:
        decision_id, when, domain, statement, roles, codes, iris, measures, selected, expected = r[:10]
        names = [refineries[c]["name"] for c in codes.split(";") if c]
        regions = sorted({refineries[c]["region"] for c in codes.split(";") if c})
        end = when.date() + dt.timedelta(days=DIAGNOSIS_DAYS)
        state = {"decision": statement, "decided_on": when.date().isoformat(), "expected_outcome": expected,
                 "refineries": ", ".join(names) or "none named", "region": ", ".join(regions) or "United States",
                 "window": f"{when.date().isoformat()} to {end.isoformat()}"}
        found.append(("diagnosis", f"diagnosis-{decision_id}",
                      {"state": state, "questions": {k: question_body(q, days=DIAGNOSIS_DAYS) for k, q in DIAGNOSIS.items()}},
                      {"decision_id": decision_id, "start": when.date(), "end": end, "region": ", ".join(regions) or None}))
    for region, info in REGIONS.items():
        for m in forward_months():
            fields = {"where": info["where"], "month": month_label(m)}
            found.append(("forward", f"forward-{info['slug']}-{m:%Y-%m}",
                          {"state": {"region": f"MPC's {region} refining region", "month": month_label(m)},
                           "questions": {k: question_body(q, **fields) for k, q in FORWARD.items()}},
                          {"region": region, "start": m, "end": add_months(m, 1) - dt.timedelta(days=1)}))
    return found


def cache_path(request_id):
    return os.path.join(CACHE, f"{request_id}.json")


def cached(request_id, body):
    """The cached response for this exact request, or None. A changed request is a new request, never the old answer."""
    path = cache_path(request_id)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        saved = json.load(f)
    return saved if saved["request_key"] == request_key(body) else None


def api_key():
    key = env("PARALLEL_API_KEY")
    path = os.path.expanduser("~/.config/parallel/api.env")
    if not key and os.path.exists(path):
        for line in open(path):
            if line.strip().startswith("PARALLEL_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise SystemExit("PARALLEL_API_KEY is not set (environment, the demo's .env or ~/.config/parallel/api.env)")
    return key


# a trailing author byline ("... - by Dr. Jane Doe"): the repository names no person, so titles are kept without it
BYLINE = re.compile(r"\s*[-|:]?\s*\bby\s+(?:Dr\.\s+|Prof\.\s+)?[A-Z][\w'.-]*(?:\s+[A-Z][\w'.-]*)+\s*$")


def title_without_byline(title):
    return BYLINE.sub("", title or "")


def call(client, request_id, body, now=None):
    """Send one request and cache the response, its request and the time it was retrieved. Excerpts are dropped:
    the demo keeps each citation's URL and title only, the title without an author's byline."""
    response = dict(client.post("/v1/decisions", body=body, cast_to=object))
    citations = [{"url": c.get("url"), "title": title_without_byline(c.get("title"))}
                 for c in response.get("citations", [])]
    saved = {"request_id": request_id, "request_key": request_key(body), "request": body,
             "retrieved_at": (now or dt.datetime.now(dt.timezone.utc)).isoformat(timespec="seconds"),
             "mode": response.get("mode"), "answers": response.get("answers", {}), "citations": citations,
             "usage": response.get("usage")}
    os.makedirs(CACHE, exist_ok=True)
    with open(cache_path(request_id), "w") as f:
        json.dump(saved, f, indent=1, sort_keys=True)
        f.write("\n")
    return saved


def interpret(answer, forward=False):
    """(value, probability, confidence, label, refusal) for one typed answer. probability is the noul, or the chosen
    option's probability; confidence is the choice's confidence (a noul has none)."""
    kind = answer.get("type")
    if kind == "refusal":
        return None, None, None, "unknown", answer.get("refusal") or answer.get("reason") or "refusal"
    if kind == "noul":
        p = float(answer["noul"])
        value = "yes" if p >= YES else "no" if p <= NO else "uncertain"
        if value == "uncertain":
            return value, p, None, "unknown", None
        return value, p, None, "inferred" if forward else "observed", None
    if kind == "choice":
        value, conf = answer["choice"], float(answer.get("confidence") or 0.0)
        p = float(answer.get("probabilities", {}).get(value, 0.0))
        return value, p, conf, "inferred" if conf >= CHOICE_CONFIDENCE else "unknown", None
    return None, None, None, "unknown", f"unexpected answer type {kind}"


def links(spec, region, refineries, decision_codes=()):
    codes = decision_codes or [c for c, r in refineries.items() if r["region"] == region]
    return (";".join(REFINERY_IRI + REFINERY_SLUG[c] for c in codes),
            ";".join(PRODUCT + p for p in spec.get("products", [])),
            SERIES + REGIONS[region]["series"] if region in REGIONS else "",
            ";".join(MEASURE + m for m in spec.get("measures", [])))


def match(signal_measures, region, decisions, refineries):
    """Past decisions a forward signal touches through the ontology: same region (a refinery of the decision is in
    it) and a shared kpi measure (the decision's measure identifiers, the signal's measures)."""
    found = []
    for d in decisions:
        in_region = any(refineries[c]["region"] == region for c in d["codes"])
        if in_region and set(d["measures"]) & set(signal_measures):
            found.append(d["id"])
    return found


def measure_ids():
    """kpi measure ID -> identifier, from kpi/measure-identifiers.csv (the decision log names measures by identifier)."""
    import csv
    with open(IDENTIFIERS, newline="") as f:
        return {r["measure_id"]: r["identifier"] for r in csv.DictReader(f)}


def tables(out):
    """The outside-context tables from the cache, and market_event's evidence columns filled from the events step.
    Requests with no cached response leave no row; `plan` says how many are missing."""
    refineries = {r[0]: {"name": r[1], "region": r[2]} for r in out["production_accounting"]["refinery"].rows}
    identifier = measure_ids()
    decisions = [{"id": r[0], "codes": [c for c in r[5].split(";") if c], "measures": r[7].split(";") if r[7] else []}
                 for r in out["aspen_pims"]["decision_log"].rows]
    codes_of = {d["id"]: d["codes"] for d in decisions}
    events, forward, citations, evidence = [], [], [], {}
    for step, request_id, body, ctx in requests(out):
        saved = cached(request_id, body)
        if saved is None or step == "smoke":
            continue
        retrieved = dt.datetime.fromisoformat(saved["retrieved_at"]).replace(tzinfo=None)
        for rank, c in enumerate(saved["citations"], 1):
            citations.append((request_id, rank, c["url"], " ".join(title_without_byline(c["title"]).split()), retrieved, retrieved))
        if step == "events":
            value, p, _, label, refusal = interpret(saved["answers"]["happened"])
            status = {"yes": "confirmed", "no": "not found", "uncertain": "uncertain"}.get(value, "unknown")
            evidence[ctx["event_id"]] = (status, p, json.dumps([c["url"] for c in saved["citations"]]))
            continue
        specs = QUESTIONS[step]
        for key, spec in specs.items():
            answer = saved["answers"].get(key, {"type": "refusal", "refusal": "no answer returned"})
            value, p, conf, label, refusal = interpret(answer, forward=step == "forward")
            region = ctx.get("region")
            codes = []
            if step == "diagnosis":  # a decision's own refineries; the crack series of its first region
                codes = codes_of[ctx["decision_id"]]
            refinery_iris, product_iris, series_iri, measure_iris = links(spec, (region or "").split(", ")[0], refineries, codes)
            row = [f"{request_id}-{key}", step, region, ctx["start"], ctx["end"], ctx.get("decision_id"), key, spec["type"],
                   body["questions"][key]["instructions"], value, p, conf, label, refusal, request_id,
                   len(saved["citations"]), refinery_iris, product_iris, series_iri, measure_iris, retrieved, retrieved]
            if step != "forward":
                events.append(tuple(row))
                continue
            signal = value not in (None, "uncertain", "no", "about_the_same", "near_normal") and label == "inferred"
            matched = match([identifier[m] for m in spec["measures"]], region, decisions, refineries) if signal else []
            action = (f"{spec['signal'].format(month=month_label(ctx['start']), value=value.replace('_', ' '))} "
                      f"(inferred). Before planning {month_label(ctx['start'])}, review the backcast of {', '.join(matched)}: "
                      f"past decisions at this region's refineries on the same measures.") if matched else None
            forward.append(tuple(row) + (";".join(matched), action, "awaiting a person" if action else None))
    columns = ["ExternalEventId", "Step", "Region", "PeriodStart", "PeriodEnd", "DecisionId", "QuestionKey", "QuestionType",
               "Question", "Answer", "Probability", "Confidence", "EvidenceLabel", "Refusal", "CallId", "CitationCount",
               "RefineryIris", "ProductIris", "SeriesIri", "MeasureIris", "RetrievedAt", "updated_at"]
    return evidence, {
        "external_event": (columns, events),
        "forward_scan": (["ForwardSignalId"] + columns[1:] + ["MatchedDecisionIds", "SuggestedAction", "ApprovalStatus"], forward),
        "external_citation": (["CallId", "CitationRank", "Url", "Title", "RetrievedAt", "updated_at"], citations),
    }


def plan(out):
    counts = {}
    for step, request_id, body, _ in requests(out):
        total, have = counts.get(step, (0, 0))
        counts[step] = (total + 1, have + (cached(request_id, body) is not None))
    for step in STEPS:
        total, have = counts.get(step, (0, 0))
        print(f"{step}: {total} calls, {have} cached, {total - have} to send")
    return counts


def run(out, step, limit=None):
    from parallel import Parallel
    client = Parallel(api_key=api_key())
    sent = 0
    for s, request_id, body, _ in requests(out):
        if s != step or cached(request_id, body) is not None:
            continue
        if limit is not None and sent >= limit:
            break
        saved = call(client, request_id, body)
        sent += 1
        answers = ", ".join(f"{k}={interpret(a, forward=step == 'forward')[0]}" for k, a in saved["answers"].items())
        print(f"{request_id}: {answers}; {len(saved['citations'])} citations")
    print(f"{step}: sent {sent} calls")
    return sent


def main():
    from . import generate
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    r = sub.add_parser("run")
    r.add_argument("--step", choices=STEPS, required=True)
    r.add_argument("--limit", type=int, help="send at most this many calls")
    args = ap.parse_args()
    out = generate.build()
    if args.cmd == "plan":
        plan(out)
    else:
        run(out, args.step, args.limit)


if __name__ == "__main__":
    main()
