"""Generate every source-system table, deterministically, from EIA's real prices, MPC's real capacities and the
scenario's event timeline.

    uv run python -m pricing_demo.generate          # print the table sizes

build() returns {system: {table: Table}}. Each price row carries DemoProvenance: "real" (an EIA value as published
on that date, or converted only in unit), "spot-anchored" (a formula of EIA values only, or an EIA value carried
from an earlier date) or "synthesized" (anything with a generated part). The same seed always gives the same rows: no clock, no network.
"""
import csv
import datetime as dt
import math
import os
import random
from dataclasses import dataclass

from . import catalog, public_data, timeline
from .config import DATA, SEED, SYSTEMS, WINDOW_END, WINDOW_START


# The units of measure, by the code an assessment group is quoted in (Kimi round 1, finding 15).
UNIT_IDS = {"$/Bbl": 1, "$/gal": 2, "$/MMbtu": 3, "cents/gal": 4, "$/unit": 5, "cents/lb": 6}


@dataclass
class Table:
    columns: list
    rows: list


def ts(day, hour=18):
    return dt.datetime(day.year, day.month, day.day, hour)


def month_start(day, plus=0):
    m = day.month - 1 + plus
    return dt.date(day.year + m // 12, m % 12 + 1, 1)


class Market:
    """Daily legs: real EIA prices where EIA publishes them, generated differentials elsewhere."""

    REAL = ("wti", "brent", "henry_hub", "nyh_ulsd", "usgc_ulsd", "usgc_gasoline", "nyh_gasoline", "usgc_jet",
            "mb_propane", "la_carbob", "la_carb_diesel")
    # Generated legs: base leg, mean differential ($/gal or $/bbl), daily noise, scenario sensitivities.
    DERIVED = {
        "chi_gasoline": ("usgc_gasoline", 0.12, 0.010), "grp_gasoline": ("usgc_gasoline", 0.05, 0.008),
        "pnw_gasoline": ("la_carbob", -0.18, 0.012), "slc_gasoline": ("usgc_gasoline", 0.22, 0.012),
        "sf_carbob": ("la_carbob", 0.04, 0.010),
        "chi_ulsd": ("usgc_ulsd", 0.10, 0.010), "grp_ulsd": ("usgc_ulsd", 0.06, 0.008),
        "pnw_ulsd": ("la_carb_diesel", -0.12, 0.012), "slc_ulsd": ("usgc_ulsd", 0.20, 0.012),
        "sf_carb_diesel": ("la_carb_diesel", 0.03, 0.010),
        "meh": ("wti", 1.05, 0.15), "ans": ("brent", -1.60, 0.20),
    }

    def __init__(self, rng):
        self.series = {k: public_data.load(k) for k in self.REAL}
        self.days = sorted(d for d in self.series["wti"] if WINDOW_START <= d <= WINDOW_END)
        self.values, self.provenance = {}, {}
        drift = {k: 0.0 for k in self.DERIVED}
        for day in self.days:
            for k in self.REAL:
                v, observed = self._last(k, day)
                # An EIA value counts as real only on its own date; one carried from an earlier date is spot-anchored
                # (Kimi round 1, finding 6).
                self.values[(k, day)], self.provenance[(k, day)] = v, ("real" if observed == day else "spot-anchored")
            scarcity = timeline.intensity("diesel_scarcity", day)
            storm = timeline.intensity("hurricane_isaias", day)
            for k, (base, mean, noise) in self.DERIVED.items():
                drift[k] = 0.92 * drift[k] + rng.gauss(0, noise)
                shock = 0.0
                if k.endswith("ulsd") or k.endswith("diesel"):
                    shock += 0.10 * scarcity  # distillate scarcity widens inland distillate premiums
                if k in ("chi_gasoline", "grp_gasoline", "slc_gasoline", "chi_ulsd", "grp_ulsd", "slc_ulsd"):
                    shock += 0.08 * storm  # inland markets lose Gulf supply during the hurricane
                self.values[(k, day)] = self.values[(base, day)] + mean + drift[k] + shock
                self.provenance[(k, day)] = "synthesized"
            rvo = 0.118 + 0.02 * math.sin(self.days.index(day) / 15) + rng.gauss(0, 0.002)
            self.values[("rvo", day)], self.provenance[("rvo", day)] = rvo, "synthesized"

    MAX_CARRY_DAYS = 7  # a long weekend and a holiday; a longer gap means the cache is incomplete

    def _last(self, key, day):
        """The latest EIA observation on or before `day`, and its date (Kimi round 1, finding 16: bounded)."""
        s = self.series[key]
        for back in range(self.MAX_CARRY_DAYS + 1):
            d = day - dt.timedelta(days=back)
            if d in s:
                return s[d], d
        raise ValueError(f"EIA series {key} has no observation in the {self.MAX_CARRY_DAYS} days before {day}")

    def leg(self, key, day):
        return self.values[(key, day)], self.provenance[(key, day)]


def worst(*labels):
    order = {"real": 0, "spot-anchored": 1, "synthesized": 2}
    return max(labels, key=order.get)


def crack_value(market, master, day):
    """The crack spread for one price master on one day, in $/bbl, and its provenance."""
    rcode, tcode = master.region, master.crack_type
    if rcode in ("BLEND", "MPC"):
        # MPC weights its blended crack by regional capacity: 42% Gulf Coast, 40% Mid-Continent, 18% West Coast
        # (MPC FY2025 Form 10-K, Item 7, as market-data 1.0.0 records it).
        parts = [crack_value(market, catalog.PriceMaster("", "", "", "crack", "", "", r, tcode), day) for r in ("USGC", "CHI", "LA")]
        weights = (0.42, 0.40, 0.18) if rcode == "BLEND" else (0.40, 0.40, 0.20)
        return sum(w * v for w, (v, _) in zip(weights, parts)), "synthesized" if rcode == "MPC" else worst(*(p for _, p in parts))
    region = next(r for r in catalog.REGIONS if r[0] == rcode)
    _, _, gas_key, dist_key, crude_key = region
    ctype = next(t for t in catalog.CRACK_TYPES if t[0] == tcode)
    _, _, wg, wd, wr, ex_rin = ctype
    gas, pg = market.leg(gas_key, day)
    dist, pd = market.leg(dist_key, day)
    crude, pc = market.leg(crude_key, day)
    resid = crude * 0.82  # residual fuel valued at a discount to crude (generated)
    total = wg + wd + wr
    value = (wg * gas * 42 + wd * dist * 42 + wr * resid) / total - crude
    labels = [pg, pd, pc] + (["synthesized"] if wr else [])
    if ex_rin:
        rvo, prvo = market.leg("rvo", day)
        value -= rvo * 42
        labels.append(prvo)
    label = worst(*labels)
    return value, ("spot-anchored" if label == "real" else label)


def forward(value, period, slope, rng):
    """A forward-curve point: backwardation of `slope` per month plus a little noise (generated)."""
    return value * (1 - slope * period) + rng.gauss(0, abs(value) * 0.004)


def build():
    rng = random.Random(SEED)
    market = Market(rng)
    days = market.days
    out = {s: {} for s in SYSTEMS}

    # ---- Commercial Reference Data Hub (KittyHawk): price services, holiday calendar, delivery periods ----
    out["kittyhawk"]["priceservice"] = Table(["Id", "Name", "PublisherId", "updated_at"], [
        (1, "MPR settlement service", 1, ts(WINDOW_START)), (2, "MIPS assessment service", 2, ts(WINDOW_START))])
    holidays = [dt.date(2026, 4, 3), dt.date(2026, 5, 25), dt.date(2026, 6, 19), dt.date(2026, 7, 3), dt.date(2026, 9, 7)]
    out["kittyhawk"]["holidaycalendar"] = Table(["Id", "Name", "HolidayDate", "updated_at"],
                                                [(i + 1, "NYMEX", d, ts(WINDOW_START)) for i, d in enumerate(holidays)])
    out["kittyhawk"]["deliveryperiodcategory"] = Table(["Id", "Name", "updated_at"], [
        (1, "Prompt", ts(WINDOW_START)), (2, "Monthly", ts(WINDOW_START)), (3, "Daily", ts(WINDOW_START))])

    # ---- Price Reference Master (MPR): price masters and daily price details ----
    benchmarks, cracks = catalog.benchmark_masters(), catalog.crack_masters()
    pm_rows = []
    for m in benchmarks + cracks:
        pm_rows.append((int(m.id), m.name, m.display_name, 1 if m.kind == "benchmark" else 2, 1, 2 if m.kind == "benchmark" else 1,
                        1, None, None, None, 1, 1, 1, 1, 1, 1, 1, 1, None, None, dt.date(2008, 2, 29), ts(WINDOW_START), m.provenance))
    out["mpr"]["pricemaster"] = Table(
        ["Id", "Name", "DisplayName", "ProductId", "PriceTypeId", "FrequencyId", "CountryId", "AreaStateId", "CityId",
         "FacilityId", "PublisherId", "PublisherCategoryId", "PublisherCurrencyId", "PublisherUnitOfMeasureId",
         "MprCurrencyId", "MprUnitOfMeasureId", "HolidayCalendarId", "ExpirationCalendarId", "PreviousId", "NextId",
         "PriceEffectiveDate", "updated_at", "DemoProvenance"], pm_rows)

    detail, pid = [], 1
    for day in days:
        scarcity = timeline.intensity("diesel_scarcity", day)
        for m in benchmarks:
            spot, label = market.leg(m.extra["eia"], day)
            slope = 0.004 + (0.010 * scarcity if m.id in ("752", "572", "747") else 0.0)
            for period in range(0, m.extra["max_period"] + 1):
                if period == 0:
                    value, prov = spot, label  # real on an EIA date, spot-anchored when carried from an earlier one
                elif period == 1:
                    # EIA: "Futures prices after April 5, 2024, are not available" (pet_pri_fut_s1_d, release 2026-10-21),
                    # so the spot is the front month.
                    value, prov = spot, "spot-anchored"
                else:
                    value, prov = forward(spot, period - 1, slope, rng), "synthesized"
                detail.append(_detail(pid, m, day, period, value, prov))
                pid += 1
        for m in cracks:
            value, label = crack_value(market, m, day)
            value += m.extra["variant"] * rng.gauss(0.15, 0.05)  # the group's variants differ slightly (generated)
            label = label if m.extra["variant"] == 0 else "synthesized"
            for period in range(0, 6):
                v = value if period == 0 else forward(value, period, 0.012 + 0.02 * scarcity, rng)
                detail.append(_detail(pid, m, day, period, v, label if period == 0 else "synthesized"))
                pid += 1
    out["mpr"]["pricedetail"] = Table(
        ["Id", "PriceMasterId", "EffectiveStartDate", "EffectiveEndDate", "RelativePeriodNum", "ContractPeriod",
         "ContractPeriodDate", "FlowDate", "CycleNum", "SettlePrice", "HighPrice", "LowPrice", "DataSource",
         "CDC_DELETED_FLAG", "updated_at", "DemoProvenance"], detail)

    # ---- Market Price Assessment System (MIPS): batches, sheets, groups, assessment groups, assessments ----
    out["mips"]["mips_currency"] = Table(["ID", "Code", "updated_at"], [(1, "USD", ts(WINDOW_START))])
    out["mips"]["mips_unitofmeasure"] = Table(["ID", "Code", "updated_at"],
                                              [(i, code, ts(WINDOW_START)) for code, i in UNIT_IDS.items()])
    batches = [(i + 1, ts(day, 17), "Published", "MIPS", ts(day, 17)) for i, day in enumerate(days)]
    out["mips"]["mips_pricebatch"] = Table(["ID", "EffectiveDate", "Status", "DataSource", "updated_at"], batches)
    batch_of = {day: i + 1 for i, day in enumerate(days)}

    sheet_names = ("Executive Summary", "Benchmark") + catalog.CRACK_SHEETS + (
        "Crude Reporting Sheet - Domestic Roll", "Crude Reporting Sheet Calendar Month Roll")
    sheets = {name: i + 1 for i, name in enumerate(sheet_names)}
    out["mips"]["mips_pricesheet"] = Table(["ID", "Name", "PriceBatchID", "Status", "CurrencyID", "UnitOfMeasureID", "updated_at"],
                                           [(sid, n, batches[-1][0], "Active", 1, 1, ts(WINDOW_START)) for n, sid in sheets.items()])
    groups, group_id = [], [0]

    def group(name, sheet, parent=None, level=1):
        group_id[0] += 1
        groups.append((group_id[0], parent, sheets[sheet], name, level, ts(WINDOW_START)))
        return group_id[0]

    top = {s: group(s if s != "Crude Reporting Sheet Calendar Month Roll" else "Crude Reporting Sheet", s, None, 0)
           for s in ("Executive Summary", "Benchmark", "Crude Reporting Sheet - Domestic Roll", "Crude Reporting Sheet Calendar Month Roll")}
    crack_parent = {s: group("Crack Spreads", s, None, 0) for s in catalog.CRACK_SHEETS}
    gasoline = group("Gasoline", "Executive Summary", top["Executive Summary"], 0)
    diesel = group("Diesel", "Executive Summary", top["Executive Summary"], 0)
    g = {
        ("Gasoline", "Basis"): group("Basis", "Executive Summary", gasoline), ("Gasoline", "Cash"): group("Cash", "Executive Summary", gasoline),
        ("Diesel", "Basis"): group("Basis", "Executive Summary", diesel), ("Diesel", "Cash"): group("Cash", "Executive Summary", diesel),
        "Renewables": group("Renewables", "Executive Summary", top["Executive Summary"]),
        "NGL's": group("NGL's", "Executive Summary", top["Executive Summary"]),
        "Benchmark": group("Benchmark", "Benchmark", top["Benchmark"]),
    }
    for name, sheet, sub, *_ in catalog.CRUDE_BLENDS:
        if (sheet, sub) not in g:
            g[(sheet, sub)] = group(sub, sheet, top[sheet])
    crack_group = {}
    for rcode, tcode, name, sheet in catalog.crack_groups():
        crack_group[name] = group(name, sheet, crack_parent[sheet])
    out["mips"]["mips_pricegroup"] = Table(["ID", "ParentPriceGroupID", "PriceSheetID", "Name", "LevelNumber", "updated_at"], groups)

    # Assessment groups: one per assessed series; each value function returns (value, provenance label).
    agroups, series = [], []

    def agroup(name, group_ref, sheet, price_master, unit_id, source, value_fn, periods=4):
        aid = len(agroups) + 1
        agroups.append((aid, 500000 + aid, int(price_master) if price_master else None, None,
                        int(price_master) if price_master else None, group_ref, sheets[sheet], name, source, 1, unit_id, ts(WINDOW_START)))
        series.append((aid, sheets[sheet], value_fn, periods, name))

    for m in benchmarks:
        agroup(m.mips_display, g["Benchmark"], "Benchmark", m.id, UNIT_IDS[m.unit], "MPR",
               lambda day, m=m: market.leg(m.extra["eia"], day), periods=1)
    crack_by_id = {m.id: m for m in cracks}
    crack_today = {}

    def crack_on(m, day):
        if (m.id, day) not in crack_today:
            crack_today[(m.id, day)] = crack_value(market, m, day)
        return crack_today[(m.id, day)]
    for m in cracks:
        agroup(m.mips_display, crack_group[m.group], m.sheet, m.id, 1, "MPR", lambda day, m=m: crack_on(m, day), periods=1)
    cash_keys = {"NYH CBOB": "nyh_gasoline", "USGC CBOB": "usgc_gasoline", "LA CARBOB": "la_carbob", "CHI CBOB (Wolvy)": "chi_gasoline",
                 "Group CBOB": "grp_gasoline", "PNW SUBOCTANE": "pnw_gasoline", "SF CARBOB": "sf_carbob", "SLC CBOB": "slc_gasoline",
                 "NYH ULSD": "nyh_ulsd", "USGC ULSD": "usgc_ulsd", "LA CARB No. 2": "la_carb_diesel", "USGC JET": "usgc_jet",
                 "CHI ULSD (Wolvy)": "chi_ulsd", "Group ULSD": "grp_ulsd", "PNW ULSD": "pnw_ulsd", "SF CARB No. 2": "sf_carb_diesel",
                 "SLC ULSD": "slc_ulsd"}
    for parent, blends, futures in (("Gasoline", catalog.GASOLINE_BLENDS, "nyh_gasoline"), ("Diesel", catalog.DISTILLATE_BLENDS, "nyh_ulsd")):
        for blend in blends:
            key = cash_keys[blend]
            agroup(blend, g[(parent, "Cash")], "Executive Summary", None, 2, "MIPS", lambda day, key=key: market.leg(key, day))

            def basis(day, key=key, fut=futures):
                (cash, pc), (futures_price, pf) = market.leg(key, day), market.leg(fut, day)
                label = worst(pc, pf)
                return cash - futures_price, ("spot-anchored" if label == "real" else label)
            agroup(blend, g[(parent, "Basis")], "Executive Summary", None, 2, "MIPS", basis)
    for blend, sheet, sub, base, mean in catalog.CRUDE_BLENDS:
        state = {"x": 0.0}

        def diff(day, mean=mean, state=state):
            state["x"] = 0.9 * state["x"] + rng.gauss(0, 0.25)
            return mean + state["x"] - 0.6 * timeline.intensity("g7_release", day), "synthesized"
        agroup(blend, g[(sheet, sub)], sheet, catalog.CRUDE_SHIFTED.get(blend), 1, "MIPS", diff)
    for blend, unit, level, vol in catalog.RENEWABLE_BLENDS:
        state = {"v": level}

        def walk(day, state=state, vol=vol):
            state["v"] *= math.exp(rng.gauss(0, vol))
            return state["v"], "synthesized"
        agroup(blend, g["Renewables"], "Executive Summary", None, UNIT_IDS.get(unit, UNIT_IDS["$/unit"]), "MIPS", walk)
    agroup("Propane Mt. Belvieu (Non-Tet)", g["NGL's"], "Executive Summary", None, 4, "MIPS",
           lambda day: (market.leg("mb_propane", day)[0] * 100, market.leg("mb_propane", day)[1]))  # cents per gallon, as the agent expects: a unit conversion
    agroup("Butane Mt. Belvieu (Non-Tet)", g["NGL's"], "Executive Summary", None, 4, "MIPS",
           lambda day: (market.leg("mb_propane", day)[0] * 100 * 1.18 + rng.gauss(0, 0.8), "synthesized"))
    out["mips"]["mips_priceassessmentgroup"] = Table(
        ["ID", "PersistentID", "PriceMasterID", "PriceMasterIDforCycles", "ReferenceID", "PriceGroupID", "PriceSheetID",
         "Name", "DataSource", "CurrencyID", "UnitOfMeasureID", "updated_at"], agroups)

    assessments, aid_seq, previous = [], 1, {}
    for day in days:
        scarcity = timeline.intensity("diesel_scarcity", day)
        for aid, sheet_id, value_fn, periods, name in series:
            base, base_label = value_fn(day)
            for sort in range(1, periods + 1):
                value = base if sort == 1 else forward(base, sort - 1, 0.008 + 0.012 * scarcity, rng)
                prev = previous.get((aid, sort))
                label = base_label if sort == 1 else "synthesized"
                assessments.append((aid_seq, aid, sheet_id, batch_of[day], month_start(day, sort - 1), round(value, 6),
                                    None if prev is None else round(prev, 6), 0, sort, ts(day, 17), label))
                previous[(aid, sort)] = value
                aid_seq += 1
    out["mips"]["mips_priceassessment"] = Table(
        ["ID", "PriceAssessmentGroupID", "PriceSheetID", "PriceBatchID", "PricePeriod", "Value", "PreviousValue",
         "CycleNum", "SortOrder", "updated_at", "DemoProvenance"], assessments)

    # ---- Refinery Production Accounting, Refinery Planning Model and CTRM ----
    refineries = list(csv.DictReader(open(os.path.join(DATA, "public", "mpc_refineries.csv"))))
    out["prodacct"]["refinery"] = Table(["RefineryCode", "RefineryName", "Region", "CrudeCapacityMbpcd", "updated_at"],
                                        [(r["refinery_code"], r["refinery_name"], r["region"], int(r["crude_capacity_mbpcd"]), ts(WINDOW_START))
                                         for r in refineries])
    util = public_data.load("us_utilization")
    production, plans, deals, moves = [], [], [], []
    for r in refineries:
        cap = int(r["crude_capacity_mbpcd"])
        for month in sorted({month_start(d) for d in days}):
            plans.append((r["refinery_code"], month, round(cap * 0.93, 1), 93.0, 47.0, 34.5, 18.5, ts(month), "synthesized"))
        for day in days:
            week = max(d for d in util if d <= day + dt.timedelta(days=6))
            u = util[week] / 100 + rng.gauss(0, 0.012)
            cut = timeline.HURRICANE_RUN_CUTS.get(r["refinery_code"], 0) * timeline.intensity("hurricane_isaias", day)
            for code, start, end in timeline.TURNAROUNDS:
                if code == r["refinery_code"] and start <= day <= end:
                    cut = max(cut, 0.35)
            runs = cap * max(min(u, 1.0) - cut, 0.0)
            dist_yield = 34.5 + 1.5 * timeline.intensity("diesel_scarcity", day) + rng.gauss(0, 0.6)
            gas_yield = 47.0 + rng.gauss(0, 0.6)
            production.append((r["refinery_code"], day, round(runs, 1), cap, round(gas_yield, 2), round(dist_yield, 2),
                               round(100 - gas_yield - dist_yield, 2), round(5.2 + rng.gauss(0, 0.3), 2), ts(day, 23), "synthesized"))
    deal_id = 1
    for day in days:
        freight = timeline.intensity("freight_spike", day)
        for _ in range(rng.randint(2, 5)):
            product = rng.choice(("Gasoline", "ULSD", "Jet", "Crude"))
            route = rng.choice((("USGC", "NYH", "Pipeline"), ("USGC", "Latin America", "Marine"), ("USGC", "Europe", "Marine"),
                                ("Midwest", "Midwest", "Truck"), ("PNW", "California", "Marine")))
            volume = rng.choice((25000, 50000, 100000, 300000))
            base_freight = {"Pipeline": 1.6, "Truck": 2.8, "Marine": 3.5}[route[2]]
            fpb = base_freight * (1 + (3.0 * freight if route[2] == "Marine" else 0.2 * freight)) + rng.gauss(0, 0.2)
            deals.append((deal_id, day, rng.choice(("Buy", "Sell")), product, route[0], route[1], volume, round(fpb, 2), ts(day, 20), "synthesized"))
            moves.append((deal_id, deal_id, route[2], route[0], route[1], day + dt.timedelta(days=rng.randint(1, 10)), volume,
                          round(volume * fpb, 2), ts(day, 21), "synthesized"))
            deal_id += 1
    out["prodacct"]["refinery_daily"] = Table(
        ["RefineryCode", "ProductionDate", "CrudeRunsMbpd", "CrudeCapacityMbpcd", "GasolineYieldPct", "DistillateYieldPct",
         "OtherYieldPct", "OpexUsdPerBbl", "updated_at", "DemoProvenance"], production)
    out["planning"]["plan_target"] = Table(
        ["RefineryCode", "PlanMonth", "PlannedCrudeRunsMbpd", "PlannedUtilizationPct", "PlannedGasolineYieldPct",
         "PlannedDistillateYieldPct", "PlannedOtherYieldPct", "updated_at", "DemoProvenance"], plans)
    out["ctrm"]["deal"] = Table(["DealId", "TradeDate", "Direction", "Product", "Origin", "Destination", "VolumeBbl",
                                 "FreightUsdPerBbl", "updated_at", "DemoProvenance"], deals)
    out["ctrm"]["movement"] = Table(["MovementId", "DealId", "Mode", "Origin", "Destination", "LoadDate", "VolumeBbl",
                                     "FreightCostUsd", "updated_at", "DemoProvenance"], moves)
    return out


def _detail(pid, m, day, period, value, provenance):
    contract = month_start(day, period)
    return (pid, int(m.id), ts(day), ts(day, 23), period, contract.strftime("%b%y").upper(), contract, None, 0,
            round(value, 6), None, None, "MPR", "N", ts(day, 18), provenance)


def sizes(tables):
    return {f"{s}.{t}": len(tab.rows) for s, ts_ in tables.items() for t, tab in ts_.items()}


if __name__ == "__main__":
    for name, n in sizes(build()).items():
        print(f"{name}: {n}")
