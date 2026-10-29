"""Plan versions, the decision log, its evidence items and the hidden decision dossiers (use cases 13 to 18).

build(out) reads the tables generate.build() has already made and returns new ones: aspen_pims.plan_version,
aspen_pims.decision_log and aspen_pims.decision_evidence, which the pipeline replicates, and decision_truth.decision_dossier,
which it never does (config.HIDDEN_SYSTEMS). Everything here is synthetic and seeded, and labelled so.

The shapes follow the decision owner's enterprise-context-engineering repository (README.md, "Use cases"): a dossier
holds the whole decision, the hidden truth the tests read; the agents see only the decision log's public columns and two
or three evidence items per decision, each showing part of the rationale. Every actual outcome is computed from the
demo's own tables after the decision, never written by hand, and every plan assumption uses only prices dated on or
before the plan's date (as-of-date context).
"""
import datetime as dt
import json
import statistics

from .config import WINDOW_END

SCENARIO_ID = "pricing-demo-2026-10-28"

# The benchmark crack each region's plan assumes: the same price masters the refinery operations gold table joins.
REGION_CRACK = {"Gulf Coast": 43870, "West Coast": 36855}
DEFAULT_CRACK = 37438  # Mid-Continent: CHI 3-2-1 Crack WTI, ex-RIN
WTI, NYH_ULSD, NYH_RBOB = 747, 752, 9471  # benchmark price masters (catalog.BENCHMARKS)
ASSUMPTION_DAYS = 20  # a plan assumes the average of the last 20 trading days up to its plan date
MIN_ASSUMPTION_DAYS = 10  # a plan whose plan date has fewer trading days behind it gets no version

REFINERY_IRI = "https://w3id.org/lsc/ontology/modules/ref-mpc/refinery-"
REFINERY_SLUG = {"GB": "galveston-bay", "GV": "garyville", "CB": "catlettsburg", "RB": "robinson", "DT": "detroit",
                 "EP": "el-paso", "SP": "st-paul-park", "CT": "canton", "MD": "mandan", "SL": "salt-lake-city",
                 "LA": "los-angeles", "AN": "anacortes", "KN": "kenai"}
ROLE_IRI = "https://w3id.org/lsc/ontology/modules/organization/role/"
MEASURE_IRI = "https://w3id.org/lsc/ontology/modules/kpi/measure/"


def ts(day, hour=18):
    return dt.datetime(day.year, day.month, day.day, hour)


class Data:
    """Indexes over the generated tables, so every number below comes from them."""

    def __init__(self, out):
        self.days = sorted({r[3] for r in out["rightangle"]["freight_rate"].rows})
        self.price = {}
        for r in out["price_reference"]["pricedetail"].rows:
            if r[4] == 0:  # RelativePeriodNum 0: the day's settle
                self.price[(r[1], r[2].date())] = float(r[9])
        self.refinery = {r[0]: {"name": r[1], "region": r[2], "cap": r[3]} for r in out["production_accounting"]["refinery"].rows}
        self.daily = {(r[0], r[1]): {"runs": float(r[2]), "gas": float(r[4]), "dist": float(r[5])}
                      for r in out["production_accounting"]["refinery_daily"].rows}
        self.freight = {(r[0], r[3]): float(r[4]) for r in out["rightangle"]["freight_rate"].rows}
        self.plans = {(r[0], r[1]): r for r in out["aspen_pims"]["plan_target"].rows}

    def crack_master(self, code):
        return REGION_CRACK.get(self.refinery[code]["region"], DEFAULT_CRACK)

    def between(self, start, end):
        return [d for d in self.days if start <= d <= end]

    def after(self, day, n):
        """The n-th trading day after `day` (n = 0: `day` itself if it is a trading day, else the next one)."""
        later = [d for d in self.days if d >= day]
        return later[n] if len(later) > n else None

    def mean(self, values):
        return round(statistics.fmean(values), 4)


def plan_versions(d):
    """One version per refinery and plan month: made on the 15th of the month before, assuming the average of the 20
    trading days up to that date (never later), with the plan target's runs and yields."""
    rows, vid = [], 1
    for (code, month), plan in sorted(d.plans.items()):
        prior = dt.date(month.year - (month.month == 1), (month.month - 2) % 12 + 1, 15)
        window = [x for x in d.days if x <= prior][-ASSUMPTION_DAYS:]
        if len(window) < MIN_ASSUMPTION_DAYS:
            continue  # no price data precedes this plan date: October and November 2023
        crack = d.crack_master(code)
        rows.append((vid, code, month, prior, 1, window[0], window[-1],
                     d.mean([d.price[(crack, x)] for x in window]), crack,
                     d.mean([d.price[(WTI, x)] for x in window]), d.mean([d.price[(NYH_ULSD, x)] for x in window]),
                     d.mean([d.price[(NYH_RBOB, x)] for x in window]),
                     plan[2], plan[3], plan[4], plan[5], ts(prior, 16), "synthesized"))
        vid += 1
    return rows


def pre_storm_util(d, code, start, end):
    return d.mean([100 * d.daily[(code, x)]["runs"] / d.refinery[code]["cap"] for x in d.between(start, end)])


def recovery_day(d, code, after, baseline_util, share=0.9):
    for x in d.days:
        if x > after and 100 * d.daily[(code, x)]["runs"] / d.refinery[code]["cap"] >= share * baseline_util:
            return x
    return None


def lost_margin(d, code, start, end, base_start, base_end):
    """Throughput lost against the pre-turnaround average, and its margin at the region's crack, in $ million."""
    base = statistics.fmean([d.daily[(code, x)]["runs"] for x in d.between(base_start, base_end)])
    lost = [(base - d.daily[(code, x)]["runs"], d.price[(d.crack_master(code), x)]) for x in d.between(start, end)]
    mbbl = sum(max(v, 0.0) for v, _ in lost)  # thousand barrels: runs are thousand barrels a day, one row a day
    usd_m = sum(max(v, 0.0) * 1000 * c for v, c in lost) / 1e6
    return round(mbbl, 1), round(usd_m, 2), len(lost)


def decisions(d):
    """Ten decisions tied to the scenario's events, each with its actual outcome computed from the tables."""
    out = []

    def add(key, when, domain, statement, roles, refineries, measures, drivers, constraints, options, selected,
            expected, actual_text, actual_data, rationale, uncertainties, evidence):
        out.append({"id": key, "time": when, "domain": domain, "statement": statement, "roles": roles,
                    "refineries": refineries, "measures": measures, "drivers": drivers, "constraints": constraints,
                    "options": options, "selected": selected, "expected": expected, "actual": actual_text,
                    "actual_data": actual_data, "rationale": rationale, "uncertainties": uncertainties, "evidence": evidence})

    # D01, D02: run cuts ahead of Hurricane Isaias (timeline.HURRICANE_RUN_CUTS: GV 45%, GB 20% at the peak).
    for key, code, target in (("D01", "GV", 55), ("D02", "GB", 80)):
        base = pre_storm_util(d, code, dt.date(2026, 9, 22), dt.date(2026, 10, 6))
        storm = d.between(dt.date(2026, 10, 7), dt.date(2026, 10, 15))
        low = min(100 * d.daily[(code, x)]["runs"] / d.refinery[code]["cap"] for x in storm)
        name = d.refinery[code]["name"].split(",")[0]
        add(key, dt.datetime(2026, 10, 6, 8), "operations",
            f"Cut crude runs at {name} to about {target}% of capacity ahead of Hurricane Isaias",
            ["regional-planning-manager", "refinery-scheduler"], [code], ["OPM-0002", "OPM-0024"],
            ["Hurricane Isaias forecast to reach the Gulf Coast on October 7", "Power and dock outages expected at the site"],
            ["Crude tankage near its limit", "Product shipments by water suspended during the storm"],
            [f"Cut runs to about {target}% of capacity", "Run through at planned rates", "Shut the crude unit down"],
            f"Cut runs to about {target}% of capacity",
            f"Crude utilization no lower than about {target}% during the storm (October 7 to 15)",
            f"Lowest utilization during the storm {low:.1f}%, against {base:.1f}% before it",
            {"pre_storm_utilization_pct": base, "lowest_storm_utilization_pct": round(low, 4)},
            "A controlled cut kept the units warm for a fast restart while limiting storm exposure; a full shutdown would "
            "have cost more days to restart than the storm was expected to last.",
            ["The storm's track and the length of the power outage were uncertain on October 6"],
            [("meeting_note", dt.datetime(2026, 10, 5, 16), "regional-planning-manager",
              f"Storm call: Isaias forecast to come ashore on the 7th. {name} to plan a run cut; scheduling to confirm tankage."),
             ("plan_change", dt.datetime(2026, 10, 6, 7), "refinery-scheduler",
              f"Plan change: {name} crude runs to about {target}% of capacity from October 7 until the all-clear.")])

    # D03: restart Garyville as power returns.
    base = pre_storm_util(d, "GV", dt.date(2026, 9, 22), dt.date(2026, 10, 6))
    back = recovery_day(d, "GV", dt.date(2026, 10, 15), base)
    days_back = None if back is None else len(d.between(dt.date(2026, 10, 16), back))
    add("D03", dt.datetime(2026, 10, 14, 9), "operations",
        "Restart Garyville's units as power returns, rather than wait for a full site inspection",
        ["refinery-econ-and-planning-supervisor", "refinery-scheduler"], ["GV"], ["OPM-0002"],
        ["Power restored to the site on October 14", "Distillate cracks high, so lost throughput is costly"],
        ["Each unit restarts only after its own walk-down"],
        ["Restart unit by unit as power returns", "Wait for a full site inspection first"],
        "Restart unit by unit as power returns",
        "Crude runs back above 90% of pre-storm runs within 3 trading days after October 15",
        "Not back above 90% of pre-storm runs by the window's end" if back is None else
        f"Back above 90% of pre-storm runs on {back.isoformat()}, {days_back} trading day(s) after October 15",
        {"pre_storm_utilization_pct": base, "recovery_date": None if back is None else back.isoformat(),
         "trading_days_after_storm": days_back},
        "High distillate cracks made every lost day expensive, and the unit-by-unit walk-downs kept the restart safe.",
        ["Whether storm damage would show up only after restart"],
        [("approval", dt.datetime(2026, 10, 14, 8), "refinery-econ-and-planning-supervisor",
          "Approved: restart unit by unit as power returns, each after its walk-down."),
         ("meeting_note", dt.datetime(2026, 10, 14, 7), "refinery-scheduler",
          "Power back at the site this morning. Crude unit first, then the FCC; products to stay in tankage until docks reopen.")])

    # D04, D05: hold the turnarounds as scheduled (timeline.TURNAROUNDS).
    for key, code, start, end, when in (("D04", "RB", dt.date(2026, 9, 21), dt.date(2026, 10, 12), dt.datetime(2026, 8, 20, 10)),
                                        ("D05", "AN", dt.date(2026, 10, 1), dt.date(2026, 10, 25), dt.datetime(2026, 9, 1, 10))):
        base_start = start - dt.timedelta(days=28)
        mbbl, usd_m, n = lost_margin(d, code, start, end, base_start, start - dt.timedelta(days=1))
        name = d.refinery[code]["name"].split(",")[0]
        add(key, when, "planning", f"Hold the {name} turnaround on schedule from {start.isoformat()}, rather than defer it",
            ["regional-planning-director", "refinery-planner"], [code], ["OPM-0030", "OPM-0029"],
            ["Inspection intervals due on the crude and vacuum units", "Contractor crews booked for the autumn"],
            ["Deferral beyond the season needs an engineering sign-off"],
            ["Hold the turnaround on schedule", "Defer it to the spring", "Shorten its scope"],
            "Hold the turnaround on schedule",
            f"Lost margin from the turnaround under $25 million at the crack expected for the season",
            f"Lost throughput {mbbl:,.1f} thousand barrels over {n} trading days to {min(end, WINDOW_END).isoformat()}, "
            f"worth ${usd_m:,.2f} million at the region's crack on each day"
            + (" (the turnaround runs past the window's end, so the rest is not counted)" if end > WINDOW_END else ""),
            {"lost_throughput_mbbl": mbbl, "lost_margin_usd_million": usd_m, "trading_days": n},
            "The units' inspection intervals ran out before the spring, and the booked crews made the autumn window "
            "cheaper than a deferral.",
            ["How high cracks would run during the outage"],
            [("meeting_note", when - dt.timedelta(days=2), "refinery-planner",
              f"Turnaround review for {name}: crews booked; inspection intervals due this autumn."),
             ("approval", when, "regional-planning-director", f"Approved: {name} turnaround stays on schedule."),
             ("plan_change", when + dt.timedelta(days=1), "refinery-planner",
              f"Plan change: {name} crude runs cut for the turnaround, {start.isoformat()} to {end.isoformat()}.")])

    # D06: shift yields toward distillate while diesel is scarce (timeline diesel_scarcity, from 2026-09-20).
    sep = d.between(dt.date(2026, 9, 1), dt.date(2026, 9, 19))
    octo = d.between(dt.date(2026, 10, 1), WINDOW_END)
    codes = sorted(d.refinery)
    before = d.mean([d.daily[(c, x)]["dist"] for c in codes for x in sep])
    after = d.mean([d.daily[(c, x)]["dist"] for c in codes for x in octo])
    add("D06", dt.datetime(2026, 9, 25, 11), "planning",
        "Raise distillate yield targets across the system while diesel is scarce",
        ["e-and-p-manager", "refinery-planning-engineer"], codes, ["OPM-0004", "OPM-0005"],
        ["Distillate cracks above gasoline cracks", "Export bans tightening world diesel supply"],
        ["Hydrotreating capacity limits how far the yield can move"],
        ["Raise distillate yield by about 1.5 points", "Hold yields at plan"],
        "Raise distillate yield by about 1.5 points",
        "System distillate yield in October about 1.5 points above September's",
        f"Distillate yield {after:.2f}% in October against {before:.2f}% in September, a change of {after - before:+.2f} points",
        {"september_distillate_yield_pct": before, "october_distillate_yield_pct": after,
         "change_points": round(after - before, 4)},
        "With distillate the scarce product, each barrel moved from gasoline to diesel earned the wider crack.",
        ["How long the export bans would last"],
        [("meeting_note", dt.datetime(2026, 9, 24, 15), "e-and-p-manager",
          "Diesel cracks running well above gasoline. Planning to look at a yield shift across the system."),
         ("plan_change", dt.datetime(2026, 9, 25, 12), "refinery-planning-engineer",
          "Plan change: distillate yield targets up about 1.5 points at every refinery from October 1.")])

    # D07: ship a ULSD cargo to New York Harbor rather than export it to Northwest Europe.
    load = d.after(dt.date(2026, 10, 9), 0)
    span = [x for x in d.days if x >= load][:10]
    premium = d.mean([d.freight[("USGC-NYH", x)] - d.freight[("USGC-NWE", x)] for x in span])
    add("D07", dt.datetime(2026, 10, 9, 9), "commercial",
        "Ship a ULSD cargo to New York Harbor by Jones Act tanker rather than export it to Northwest Europe",
        ["cpvc-scheduler", "commercial-scheduler"], ["GV"], ["OPM-0018", "OPM-0028"],
        ["East Coast distillate stocks low", "Export arbitrage closing as freight rose"],
        ["Jones Act tankers are scarce", "The cargo must load within ten days"],
        ["Ship to New York Harbor", "Export to Northwest Europe"],
        "Ship to New York Harbor",
        "The domestic freight premium over export freight stays under $1.00/bbl through loading",
        f"The domestic freight premium averaged ${premium:.2f}/bbl over the {len(span)} trading days from "
        f"{load.isoformat()} to the window's end",
        {"load_date": load.isoformat(), "trading_days": len(span), "avg_domestic_premium_usd_per_bbl": premium},
        "Low East Coast stocks promised a strong delivered price, and the closing arbitrage made the export riskier.",
        ["Whether Jones Act freight would keep rising with the spot market"],
        [("meeting_note", dt.datetime(2026, 10, 8, 16), "commercial-scheduler",
          "Cargo options for the ULSD barrel: East Coast stocks are low; Europe still open but freight moving fast."),
         ("approval", dt.datetime(2026, 10, 9, 9), "cpvc-scheduler", "Approved: ship to New York Harbor.")])

    # D08: defer crude purchases after the G7 reserve release (timeline g7_release, from 2026-10-02).
    day0 = d.after(dt.date(2026, 10, 2), 0)
    day10 = d.after(day0, 10)
    wti0, wti10 = d.price[(WTI, day0)], (None if day10 is None else d.price[(WTI, day10)])
    change = None if wti10 is None else round(wti10 - wti0, 4)
    add("D08", dt.datetime(2026, 10, 2, 14), "commercial",
        "Defer part of November's crude purchases after the G7 emergency-stock release",
        ["crude-planning-and-optimization-director", "crude-oil-trader"], ["GB", "GV"], ["OPM-0019"],
        ["The G7 announced a coordinated release of emergency stocks", "Crude briefly fell on the news"],
        ["Crude tankage at the Gulf Coast refineries"],
        ["Defer part of the purchases", "Buy as planned"],
        "Defer part of the purchases",
        "WTI at least $2.00/bbl lower ten trading days later",
        "Fewer than ten trading days remained in the window" if change is None else
        f"WTI moved from ${wti0:.2f} on {day0.isoformat()} to ${wti10:.2f} on {day10.isoformat()}, {change:+.2f}/bbl",
        {"decision_day": day0.isoformat(), "wti_decision_day": wti0, "wti_ten_days_later": wti10, "change_usd_per_bbl": change},
        "The release looked large enough to soften prompt crude for a few weeks.",
        ["Whether product tightness would hold crude up despite the release"],
        [("meeting_note", dt.datetime(2026, 10, 2, 12), "crude-oil-trader",
          "G7 release announced. Crude off about $2 intraday; worth waiting on part of November's barrels."),
         ("approval", dt.datetime(2026, 10, 2, 14), "crude-planning-and-optimization-director",
          "Approved: defer part of November's purchases.")])

    # D09: hold export nominations flat as China restarts product exports (BRIEFING_EVENTS china_export_restart).
    day0 = d.after(dt.date(2026, 10, 8), 0)
    day8 = d.after(day0, 8)
    p0, p8 = d.price[(NYH_ULSD, day0)], (None if day8 is None else d.price[(NYH_ULSD, day8)])
    cents = None if p8 is None else round(100 * (p8 - p0), 4)
    add("D09", dt.datetime(2026, 10, 8, 10), "commercial",
        "Hold Gulf Coast ULSD export nominations flat as China restarts product exports",
        ["commercial-scheduler"], ["GB", "GV"], ["OPM-0018"],
        ["About 3.7 million metric tons of Chinese product exports approved for October"],
        ["Existing term contracts"],
        ["Hold nominations flat", "Raise them to catch high prices"],
        "Hold nominations flat",
        "NYH ULSD at least 5 cents/gal lower within 8 trading days",
        "Fewer than eight trading days remained in the window" if cents is None else
        f"NYH ULSD moved from ${p0:.4f} to ${p8:.4f}/gal by {day8.isoformat()}, {cents:+.2f} cents/gal",
        {"decision_day": day0.isoformat(), "nyh_ulsd_decision_day": p0, "nyh_ulsd_eight_days_later": p8,
         "change_cents_per_gal": cents},
        "Chinese supply returning was expected to ease Atlantic diesel prices.",
        ["How much of the Chinese supply would reach the Atlantic basin"],
        [("meeting_note", dt.datetime(2026, 10, 8, 9), "commercial-scheduler",
          "China's holiday is over and export quotas are out. Keep November nominations where they are for now."),
         ("plan_change", dt.datetime(2026, 10, 8, 11), "commercial-scheduler",
          "Nomination change: none. Gulf Coast ULSD export nominations for November held at the current level.")])

    # D10: hold runs through the weakest stretch of the Gulf Coast crack before the scenario's events.
    usgc = [(x, d.price[(43870, x)]) for x in d.days if x < dt.date(2026, 8, 1)]
    best = min(range(len(usgc) - 19), key=lambda i: statistics.fmean(v for _, v in usgc[i:i + 20]))
    day0, crack0 = usgc[best + 19]
    day20 = d.after(day0, 20)
    crack20 = d.price[(43870, day20)]
    add("D10", dt.datetime(day0.year, day0.month, day0.day, 15), "planning",
        "Hold Gulf Coast crude runs through a weak crack rather than cut them",
        ["e-and-p-manager", "regional-planning-manager"], ["GB", "GV"], ["KPI-0001", "OPM-0002"],
        ["The USGC 3-2-1 crack at its weakest 20-day average of the period"],
        ["Term crude already committed", "Product supply contracts"],
        ["Hold runs", "Cut runs by 10%"],
        "Hold runs",
        "The USGC 3-2-1 crack at least $3.00/bbl higher 20 trading days later",
        f"The USGC 3-2-1 crack moved from ${crack0:.2f} on {day0.isoformat()} to ${crack20:.2f} on {day20.isoformat()}, "
        f"{crack20 - crack0:+.2f}/bbl",
        {"decision_day": day0.isoformat(), "crack_decision_day": crack0, "crack_twenty_days_later": crack20,
         "change_usd_per_bbl": round(crack20 - crack0, 4)},
        "Committed crude and contract supply made a cut costly, and the crack was expected to recover.",
        ["Whether weak demand would keep the crack low"],
        [("meeting_note", dt.datetime(day0.year, day0.month, day0.day, 13), "regional-planning-manager",
          "Gulf crack at the low end of its range. Planning to hold runs; term barrels already committed."),
         ("approval", dt.datetime(day0.year, day0.month, day0.day, 15), "e-and-p-manager",
          "Approved: Gulf Coast crude runs stay at plan.")])
    return out


def build(out):
    d = Data(out)
    versions = plan_versions(d)
    log, dossiers, evidence = [], [], []
    for x in decisions(d):
        refineries = [REFINERY_IRI + REFINERY_SLUG[c] for c in x["refineries"]]
        log.append((x["id"], x["time"], x["domain"], x["statement"], ";".join(x["roles"]), ";".join(x["refineries"]),
                    ";".join(refineries), ";".join(x["measures"]), x["selected"], x["expected"], x["time"], "synthesized"))
        entities = refineries + [ROLE_IRI + r for r in x["roles"]] + x["measures"]
        dossiers.append((x["id"], SCENARIO_ID, x["time"], x["domain"], x["statement"], json.dumps(x["roles"]),
                         json.dumps(entities), json.dumps(x["drivers"]), json.dumps(x["constraints"]), json.dumps(x["options"]),
                         x["selected"], "approved", x["expected"], x["actual"], json.dumps(x["actual_data"], sort_keys=True),
                         x["rationale"], json.dumps(x["uncertainties"]), True, ts(WINDOW_END)))
        for i, (kind, when, role, text) in enumerate(x["evidence"], 1):
            evidence.append((f"EV-{x['id']}-{i}", x["id"], kind, when, role, text, True, when, "synthesized"))
    return {
        "aspen_pims": {
            "plan_version": (["PlanVersionId", "RefineryCode", "PlanMonth", "PlanDate", "VersionNum", "AssumptionsFromDate",
                              "AssumptionsThroughDate", "AssumedBenchmarkCrackUsdPerBbl", "BenchmarkCrackPriceMasterId",
                              "AssumedWtiUsdPerBbl", "AssumedNyhUlsdUsdPerGal", "AssumedNyhRbobUsdPerGal",
                              "PlannedCrudeRunsMbpd", "PlannedUtilizationPct", "PlannedGasolineYieldPct",
                              "PlannedDistillateYieldPct", "updated_at", "DemoProvenance"], versions),
            "decision_log": (["DecisionId", "DecisionTime", "DecisionDomain", "Statement", "OwnerRoleSlugs", "RefineryCodes",
                              "RefineryIris", "MeasureIdentifiers", "SelectedOption", "ExpectedOutcome", "updated_at",
                              "DemoProvenance"], log),
            "decision_evidence": (["EvidenceId", "DecisionId", "EvidenceKind", "AuthoredAt", "AuthorRoleSlug", "EvidenceText",
                                   "Synthetic", "updated_at", "DemoProvenance"], evidence),
        },
        "decision_truth": {
            "decision_dossier": (["DecisionId", "ScenarioId", "DecisionTime", "DecisionDomain", "DecisionStatement",
                                  "DecisionOwnerRoles", "AffectedEntities", "Drivers", "Constraints", "Options",
                                  "SelectedOption", "ApprovalStatus", "ExpectedOutcome", "ActualOutcome", "ActualOutcomeData",
                                  "GroundTruthRationale", "KnownUncertainties", "Synthetic", "updated_at"], dossiers),
        },
    }
