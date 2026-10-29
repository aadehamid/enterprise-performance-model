"""Real public data the demo uses, cached in data/public/ so a run needs no network.

    uv run python -m pricing_demo.public_data --refresh   # re-pull from the EIA Open Data API (needs EIA_API_KEY)

Every series is cited by its EIA series ID; eia_series.csv records the description, unit and the date pulled.
The key is read from the environment, then the demo's .env, then ~/.config/eia/api.env, and is never printed.
"""
import argparse
import csv
import datetime as dt
import json
import os
import urllib.request

from . import config
from .config import DATA, WEEKLY_START, WINDOW_END, WINDOW_START

EIA_SERIES = {
    # key used in the demo: (EIA series ID, what it stands for in the demo)
    "wti": ("PET.RWTC.D", "NYMEX WTI (Cushing) front month: the WTI Cushing spot"),
    "brent": ("PET.RBRTE.D", "ICE Brent front month: the Europe Brent spot"),
    "henry_hub": ("NG.RNGWHHD.D", "NYMEX Natural Gas front month: the Henry Hub spot"),
    "nyh_ulsd": ("PET.EER_EPD2DXL0_PF4_Y35NY_DPG.D", "NYMEX Heating Oil front month and NYH ULSD cash"),
    "usgc_ulsd": ("PET.EER_EPD2DXL0_PF4_RGC_DPG.D", "USGC ULSD cash"),
    "usgc_gasoline": ("PET.EER_EPMRU_PF4_RGC_DPG.D", "USGC CBOB cash: Gulf Coast conventional regular"),
    "nyh_gasoline": ("PET.EER_EPMRU_PF4_Y35NY_DPG.D",
                     "NYMEX RBOB front month and NYH CBOB cash: NY Harbor conventional regular (EIA spot table, release 2026-10-21: no NYH RBOB spot)"),
    "usgc_jet": ("PET.EER_EPJK_PF4_RGC_DPG.D", "USGC Jet cash"),
    "mb_propane": ("PET.EER_EPLLPA_PF4_Y44MB_DPG.D", "Propane Mt. Belvieu"),
    "la_carbob": ("PET.EER_EPMRR_PF4_Y05LA_DPG.D", "LA CARBOB cash: Los Angeles reformulated RBOB regular"),
    "la_carb_diesel": ("PET.EER_EPD2DC_PF4_Y05LA_DPG.D", "LA CARB No. 2 cash: Los Angeles ULSD CARB diesel"),
    "us_utilization": ("PET.WPULEUS3.W", "U.S. refinery utilization, weekly (Weekly Petroleum Status Report)"),
    "us_crude_runs": ("PET.WCRRIUS2.W", "U.S. refiner net input of crude oil, weekly"),
    "us_gasoline_stocks": ("PET.WGTSTUS1.W", "U.S. total gasoline stocks, weekly"),
    "us_distillate_stocks": ("PET.WDISTUS1.W", "U.S. distillate stocks, weekly"),
}

# EIA's weekly series by PADD (Weekly Petroleum Status Report), for the eia_weekly source database: key -> (series ID,
# measure, area). Product supplied and exports are published weekly for the U.S. only, so they have no PADD rows.
PADDS = (("R10", "PADD 1 East Coast"), ("R20", "PADD 2 Midwest"), ("R30", "PADD 3 Gulf Coast"),
         ("R40", "PADD 4 Rocky Mountain"), ("R50", "PADD 5 West Coast"), ("NUS", "U.S."))
EIA_WEEKLY = {}
for _code, _area in PADDS:
    _p = {"R10": "1", "R20": "2", "R30": "3", "R40": "4", "R50": "5"}.get(_code)
    EIA_WEEKLY[f"distillate_stocks_{_code.lower()}"] = (f"PET.WDISTP{_p}1.W" if _p else "PET.WDISTUS1.W", "distillate_stocks", _area)
    EIA_WEEKLY[f"gasoline_stocks_{_code.lower()}"] = (f"PET.WGTSTP{_p}1.W" if _p else "PET.WGTSTUS1.W", "gasoline_stocks", _area)
    EIA_WEEKLY[f"utilization_{_code.lower()}"] = (f"PET.W_NA_YUP_{_code}_PER.W" if _p else "PET.WPULEUS3.W", "refinery_utilization", _area)
    EIA_WEEKLY[f"crude_runs_{_code.lower()}"] = (f"PET.WCRRIP{_p}2.W" if _p else "PET.WCRRIUS2.W", "crude_runs", _area)
EIA_WEEKLY["distillate_supplied_nus"] = ("PET.WDIUPUS2.W", "distillate_product_supplied", "U.S.")
EIA_WEEKLY["gasoline_supplied_nus"] = ("PET.WGFUPUS2.W", "gasoline_product_supplied", "U.S.")
EIA_WEEKLY["distillate_exports_nus"] = ("PET.WDIEXUS2.W", "distillate_exports", "U.S.")
EIA_WEEKLY["gasoline_exports_nus"] = ("PET.W_EPM0F_EEX_NUS-Z00_MBBLD.W", "gasoline_exports", "U.S.")


def first_day(series):
    """The earliest date a refresh keeps: weekly series reach back a year before the window, for the plan targets'
    prior-year months; daily series start two weeks before it, so the window's first day has a value to carry."""
    return WINDOW_START - dt.timedelta(days=400 if series.endswith(".W") else 14)


def eia_key():
    """The EIA key from the environment, then the demo's .env (as .env.example and the README name it), then
    ~/.config/eia/api.env. Never printed (Cursor Bugbot on #380)."""
    key = config.env("EIA_API_KEY", "").strip()
    path = os.path.expanduser("~/.config/eia/api.env")
    if not key and os.path.exists(path):
        for line in open(path):
            if line.strip().startswith("EIA_API_KEY"):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise SystemExit("EIA_API_KEY is not set (environment, the demo's .env, or ~/.config/eia/api.env)")
    return key


def refresh(fetch=None, folder=None):
    """Pull every series, check each, and only then replace the cache, all files at once (Kimi round 1, finding 21).
    A failed or empty response leaves the cache exactly as it was."""
    folder = folder or os.path.join(DATA, "public")
    today = dt.date.today().isoformat()
    if fetch is None:
        key = eia_key()

        def fetch(series):
            url = f"https://api.eia.gov/v2/seriesid/{series}?api_key={key}"
            try:
                return json.load(urllib.request.urlopen(url, timeout=60))["response"]["data"]
            except Exception as e:  # never echo the URL, which holds the key
                raise SystemExit(f"EIA request for {series} failed: {type(e).__name__}") from None
    pulled, meta = {}, []
    for name, (series, role) in EIA_SERIES.items():
        rows = sorted((r for r in fetch(series) if first_day(series) <= dt.date.fromisoformat(r["period"]) <= WINDOW_END),
                      key=lambda r: r["period"])
        if not rows or any(r.get("value") in (None, "") for r in rows):
            raise SystemExit(f"EIA series {series} returned no usable rows in the window; the cache is unchanged")
        pulled[name] = rows
        meta.append((name, series, rows[0].get("series-description", ""), rows[0].get("units", ""), role, today))
    weekly, weekly_meta = [], []
    for name, (series, measure, area) in EIA_WEEKLY.items():
        rows = sorted((r for r in fetch(series) if WEEKLY_START <= dt.date.fromisoformat(r["period"]) <= WINDOW_END),
                      key=lambda r: r["period"])
        if not rows or any(r.get("value") in (None, "") for r in rows):
            raise SystemExit(f"EIA series {series} returned no usable rows from {WEEKLY_START}; the cache is unchanged")
        weekly += [(name, series, r["period"], r["value"]) for r in rows]
        weekly_meta.append((name, series, measure, area, rows[0].get("series-description", ""), rows[0].get("units", ""), today))
    staging = folder + ".staging"
    os.makedirs(staging, exist_ok=True)
    for name, rows in pulled.items():
        with open(os.path.join(staging, f"eia_{name}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["period", "value"])
            w.writerows((r["period"], r["value"]) for r in rows)
    with open(os.path.join(staging, "eia_series.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "series_id", "description", "units", "demo_role", "pulled_on"])
        w.writerows(meta)
    with open(os.path.join(staging, "eia_weekly.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "series_id", "period", "value"])
        w.writerows(weekly)
    with open(os.path.join(staging, "eia_weekly_series.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "series_id", "measure", "area", "description", "units", "pulled_on"])
        w.writerows(weekly_meta)
    for file in sorted(os.listdir(staging)):  # every file is complete before any is replaced
        os.replace(os.path.join(staging, file), os.path.join(folder, file))
    os.rmdir(staging)
    for name, rows in pulled.items():
        print(f"{name}: {EIA_SERIES[name][0]}, {len(rows)} rows")
    print(f"eia_weekly: {len(EIA_WEEKLY)} series, {len(weekly)} rows")


def load(name):
    """{date: value} for one cached series."""
    with open(os.path.join(DATA, "public", f"eia_{name}.csv"), newline="") as f:
        return {dt.date.fromisoformat(r["period"]): float(r["value"]) for r in csv.DictReader(f) if r["value"] not in ("", None)}


def weekly():
    """[(key, series ID, week ending, value)] from the eia_weekly cache, and {key: metadata row}."""
    with open(os.path.join(DATA, "public", "eia_weekly.csv"), newline="") as f:
        values = [(r["key"], r["series_id"], dt.date.fromisoformat(r["period"]), float(r["value"])) for r in csv.DictReader(f)]
    with open(os.path.join(DATA, "public", "eia_weekly_series.csv"), newline="") as f:
        meta = {r["key"]: r for r in csv.DictReader(f)}
    return values, meta


def series_meta():
    with open(os.path.join(DATA, "public", "eia_series.csv"), newline="") as f:
        return {r["key"]: r for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    if ap.parse_args().refresh:
        refresh()


if __name__ == "__main__":
    main()
