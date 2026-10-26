"""Real public data the demo uses, cached in data/public/ so a run needs no network.

    uv run python -m pricing_demo.public_data --refresh   # re-pull from the EIA Open Data API (needs EIA_API_KEY)

Every series is cited by its EIA series ID; eia_series.csv records the description, unit and the date pulled.
The key is read from the environment or from ~/.config/eia/api.env and is never printed.
"""
import argparse
import csv
import datetime as dt
import json
import os
import urllib.request

from .config import DATA, WINDOW_END, WINDOW_START

EIA_SERIES = {
    # key used in the demo: (EIA series ID, what it stands for in the demo)
    "wti": ("PET.RWTC.D", "NYMEX WTI (Cushing) front month: the WTI Cushing spot"),
    "brent": ("PET.RBRTE.D", "ICE Brent front month: the Europe Brent spot"),
    "henry_hub": ("NG.RNGWHHD.D", "NYMEX Natural Gas front month: the Henry Hub spot"),
    "nyh_ulsd": ("PET.EER_EPD2DXL0_PF4_Y35NY_DPG.D", "NYMEX Heating Oil front month and NYH ULSD cash"),
    "usgc_ulsd": ("PET.EER_EPD2DXL0_PF4_RGC_DPG.D", "USGC ULSD cash"),
    "usgc_gasoline": ("PET.EER_EPMRU_PF4_RGC_DPG.D", "USGC CBOB cash: Gulf Coast conventional regular"),
    "nyh_gasoline": ("PET.EER_EPMRU_PF4_Y35NY_DPG.D",
                     "NYMEX RBOB front month and NYH CBOB cash: NY Harbor conventional regular (EIA publishes no NYH RBOB spot)"),
    "usgc_jet": ("PET.EER_EPJK_PF4_RGC_DPG.D", "USGC Jet cash"),
    "mb_propane": ("PET.EER_EPLLPA_PF4_Y44MB_DPG.D", "Propane Mt. Belvieu"),
    "la_carbob": ("PET.EER_EPMRR_PF4_Y05LA_DPG.D", "LA CARBOB cash: Los Angeles reformulated RBOB regular"),
    "la_carb_diesel": ("PET.EER_EPD2DC_PF4_Y05LA_DPG.D", "LA CARB No. 2 cash: Los Angeles ULSD CARB diesel"),
    "us_utilization": ("PET.WPULEUS3.W", "U.S. refinery utilization, weekly (Weekly Petroleum Status Report)"),
    "us_crude_runs": ("PET.WCRRIUS2.W", "U.S. refiner net input of crude oil, weekly"),
    "us_gasoline_stocks": ("PET.WGTSTUS1.W", "U.S. total gasoline stocks, weekly"),
    "us_distillate_stocks": ("PET.WDISTUS1.W", "U.S. distillate stocks, weekly"),
}


def eia_key():
    key = os.environ.get("EIA_API_KEY", "").strip()
    path = os.path.expanduser("~/.config/eia/api.env")
    if not key and os.path.exists(path):
        for line in open(path):
            if line.strip().startswith("EIA_API_KEY"):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise SystemExit("EIA_API_KEY is not set (environment or ~/.config/eia/api.env)")
    return key


def refresh():
    key, today = eia_key(), dt.date.today().isoformat()
    meta = []
    for name, (series, role) in EIA_SERIES.items():
        url = f"https://api.eia.gov/v2/seriesid/{series}?api_key={key}"
        try:
            rows = json.load(urllib.request.urlopen(url, timeout=60))["response"]["data"]
        except Exception as e:  # never echo the URL, which holds the key
            raise SystemExit(f"EIA request for {series} failed: {type(e).__name__}") from None
        rows = sorted((r for r in rows if WINDOW_START - dt.timedelta(days=14) <= dt.date.fromisoformat(r["period"]) <= WINDOW_END),
                      key=lambda r: r["period"])
        with open(os.path.join(DATA, "public", f"eia_{name}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["period", "value"])
            w.writerows((r["period"], r["value"]) for r in rows)
        meta.append((name, series, rows[0].get("series-description", ""), rows[0].get("units", ""), role, today))
        print(f"{name}: {series}, {len(rows)} rows")
    with open(os.path.join(DATA, "public", "eia_series.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "series_id", "description", "units", "demo_role", "pulled_on"])
        w.writerows(meta)


def load(name):
    """{date: value} for one cached series."""
    with open(os.path.join(DATA, "public", f"eia_{name}.csv"), newline="") as f:
        return {dt.date.fromisoformat(r["period"]): float(r["value"]) for r in csv.DictReader(f) if r["value"] not in ("", None)}


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
