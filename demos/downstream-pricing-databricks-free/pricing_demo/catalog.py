"""The reference data of the source systems: price masters, the MIPS sheet and group hierarchy, assessment groups.

Names and IDs the decision owner's files give are kept (EPM-DEC-001-0097 and market-data 1.0.0 hold them);
everything else is generated, and every generated name carries the provenance label "synthesized".
"""
from dataclasses import dataclass, field

BENCHMARKS = (
    # (Price Master ID, MPR name, display name, MIPS display name, unit, EIA key, max relative period)
    ("572", "ICE, Brent Crude (ICE), BRENT", "ICE BRENT", "ICE, BRENT ($-Bbl)", "$/Bbl", "brent", 6),
    ("747", "NYMEX, Crude Oil, Light Sweet (NYM), CUSH", "NYMEX WTI (CUSH)", "NYMEX WTI (Cush) ($-Bbl)", "$/Bbl", "wti", 7),
    ("750", "NYMEX, Natural Gas, HENRY", "NYMEX Natural Gas", "NYMEX Natural Gas ($-MMbtu)", "$/MMbtu", "henry_hub", 7),
    ("752", "NYMEX, Heating Oil No. 2 (NYM), NYHAR", "NYMEX HO", "NYMEX Heating Oil (cpg)", "$/gal", "nyh_ulsd", 7),
    ("9471", "NYMEX, RBOB, NYHAR", "NYMEX RBOB", "NYMEX RBOB (cpg)", "$/gal", "nyh_gasoline", 7),
)

# Regions of the crack-spread groups: code, label, gasoline leg, distillate leg, crude leg.
REGIONS = (
    ("NYMEX", "NYMEX", "nyh_gasoline", "nyh_ulsd", "wti"),
    ("CHI", "CHI", "chi_gasoline", "chi_ulsd", "wti"),
    ("GRP", "Group", "grp_gasoline", "grp_ulsd", "wti"),
    ("USGC", "USGC", "usgc_gasoline", "usgc_ulsd", "meh"),
    ("NYH", "NYH", "nyh_gasoline", "nyh_ulsd", "brent"),
    ("LA", "LA", "la_carbob", "la_carb_diesel", "ans"),
    ("SF", "SF", "sf_carbob", "sf_carb_diesel", "ans"),
    ("PNW", "PNW", "pnw_gasoline", "pnw_ulsd", "ans"),
    ("SLC", "SLC", "slc_gasoline", "slc_ulsd", "wti"),
    ("BLEND", "Blended", None, None, None),
    ("MPC", "MPC Internal Blended", None, None, None),
)
# Crack types: code, group-name pattern, gasoline weight, distillate weight, residual weight, minus RIN cost.
CRACK_TYPES = (
    ("321", "{r} 3-2-1 Crack", 2, 1, 0, False),
    ("321X", "{r} 3-2-1 Crack , ex-RIN", 2, 1, 0, True),
    ("6321", "{r} 6-3-2-1 Crack", 3, 2, 1, False),
    ("211", "{r} 2-1-1 Crack", 1, 1, 0, False),
)
# The crack series the decision owner's files and market-data 1.0.0 name: ID, MPR name, region, type,
# and the Executive Summary display name where the agent lists one.
NAMED_CRACKS = (
    ("39998", "NYMEX 3:2:1 crack spread", "NYMEX", "321", "NYMEX 3-2-1"),
    ("44934", "NYMEX 6-3-2-1 Crack Spread", "NYMEX", "6321", None),
    ("44935", "NYMEX 2-1-1 Crack Spread", "NYMEX", "211", None),
    ("37438", "CHI 3-2-1 Crack WTI, ex-RIN", "CHI", "321X", "Chi WTI 3-2-1 Ex RIN Prompt"),
    ("37439", "Group 3-2-1 Crack WTI, ex-RIN", "GRP", "321X", None),
    ("43870", "USGC 3-2-1 MEH Crack, ex-RIN", "USGC", "321X", "USGC 3-2-1 MEH Ex RIN Prompt"),
    ("36855", "LA 3-2-1 Crack ANS, ex-RIN", "LA", "321X", "LA ANS 3-2-1 Ex RIN Prompt"),
    ("37443", "PNW 3-2-1 Crack, ex-RIN", "PNW", "321X", "PNW ANS 3-2-1 Ex RIN Prompt"),
    ("37471", "SLC 3-2-1 Crack WTI, ex-RIN", "SLC", "321X", None),
    ("37464", "Blended 3-2-1 Crack, ex-RIN", "BLEND", "321X", "Blended Crack Ex Rin Prompt"),
    ("42023", "MPC Internal Blended 3-2-1 Crack, ex-RIN", "MPC", "321X", None),
)
# The files give the IDs 44934 and 44935 but not their names, so those two names are generated.
NAMES_GENERATED = {"44934", "44935"}
CRACK_SHEETS = ("Crack Spreads", "Crack Spreads - MPC", "Crack Spreads - 3rd Party")
CRACK_SERIES = 127  # 127 price masters in 44 groups, as the decision owner's crack view holds on 2026-10-25

# The Executive Summary groups the agent filters by: KPI group, sheet, parent group, group, unit, blends.
GASOLINE_BLENDS = ("CHI CBOB (Wolvy)", "Group CBOB", "LA CARBOB", "NYH CBOB", "PNW SUBOCTANE", "SF CARBOB", "SLC CBOB", "USGC CBOB")
DISTILLATE_BLENDS = ("CHI ULSD (Wolvy)", "Group ULSD", "LA CARB No. 2", "NYH ULSD", "PNW ULSD", "SF CARB No. 2", "SLC ULSD",
                     "USGC ULSD", "USGC JET")
CRUDE_BLENDS = (
    ("Bakken - Patoka vs. WTI CMA", "Crude Reporting Sheet - Domestic Roll", "Bakken-Rockies", "wti", -2.10),
    ("Light Louisiana Sweet (LLS) vs. WTI Cushing", "Crude Reporting Sheet - Domestic Roll", "Domestic Gulf Coast", "wti", 2.40),
    ("Mars vs. WTI Cushing", "Crude Reporting Sheet - Domestic Roll", "Domestic Gulf Coast", "wti", -0.90),
    ("SYN vs. WTI CMA", "Crude Reporting Sheet - Domestic Roll", "Canadian", "wti", 1.20),
    ("WCS vs. WTI CMA", "Crude Reporting Sheet - Domestic Roll", "Canadian", "wti", -11.50),
    ("WTI - Magellan E Houston (MEH) vs. WTI Cushing", "Crude Reporting Sheet - Domestic Roll", "Permian-Houston-Corpus", "wti", 1.05),
    ("WTI - Midland vs. WTI Cushing", "Crude Reporting Sheet - Domestic Roll", "Permian-Houston-Corpus", "wti", 0.85),
    ("Alaska North Slope (ANS) vs. ICE Brent", "Crude Reporting Sheet Calendar Month Roll", "Domestic West Coast", "brent", -1.60),
    ("Platts USGC HSFO vs. ICE Brent", "Crude Reporting Sheet Calendar Month Roll", "Heavy Fuel Oil", "brent", -9.80),
    ("Platts USGC LSFO vs. ICE Brent", "Crude Reporting Sheet Calendar Month Roll", "Heavy Fuel Oil", "brent", -3.40),
)
# The three crude instruments whose pricing period shifts by two months (the agent's rule).
CRUDE_SHIFTED = {"Bakken - Patoka vs. WTI CMA": "30532", "SYN vs. WTI CMA": "79068", "WCS vs. WTI CMA": "79069"}
RENEWABLE_BLENDS = (
    # display name, unit as stored, base level, daily volatility
    ("CHI Biodiesel", "$/gal", 4.95, 0.012), ("HOBO", "$/gal", 1.10, 0.03), ("Biodiesel (D4) RIN", "$/RIN", 1.02, 0.02),
    ("CHI Ethanol", "$/gal", 1.86, 0.012), ("Ethanol (D6) RIN", "$/RIN", 0.98, 0.02), ("RVO", "$/gal", 0.118, 0.02),
    ("OPIS, LCFS", "$/credit", 0.62, 0.015), ("OPIS, Oregon CFS", "$/credit", 1.08, 0.015),
    ("CBOT SBO", "cents/lb", 51.2, 0.012), ("SBO Pretreatment Margin", "$/gal", 0.42, 0.04),
)
NGL_BLENDS = (("Propane Mt. Belvieu (Non-Tet)", "mb_propane"), ("Butane Mt. Belvieu (Non-Tet)", None))


@dataclass
class PriceMaster:
    id: str
    name: str
    display_name: str
    kind: str  # benchmark | crack | leg | assessment
    unit: str
    provenance: str  # of the name: real (the owner's files or market-data) or synthesized
    region: str = ""
    crack_type: str = ""
    group: str = ""
    sheet: str = ""
    mips_display: str = ""
    extra: dict = field(default_factory=dict)


def crack_groups():
    """The 44 crack-spread groups: 11 regions times 4 crack types."""
    groups = []
    for rcode, rlabel, *_ in REGIONS:
        for tcode, pattern, *_ in CRACK_TYPES:
            name = pattern.format(r=rlabel)
            sheet = "Crack Spreads - MPC" if rcode == "MPC" else ("Crack Spreads - 3rd Party" if tcode == "6321" else "Crack Spreads")
            groups.append((rcode, tcode, name, sheet))
    return groups


def crack_masters():
    """127 crack-spread price masters across the 44 groups; the named ones keep their IDs and names."""
    groups = crack_groups()
    by_key = {(r, t): (name, sheet) for r, t, name, sheet in groups}
    masters, used = [], set()
    for pid, name, rcode, tcode, display in NAMED_CRACKS:
        gname, sheet = by_key[(rcode, tcode)]
        provenance = "synthesized" if pid in NAMES_GENERATED else "real"
        masters.append(PriceMaster(pid, name, name, "crack", "$/Bbl", provenance, rcode, tcode, gname, sheet,
                                   display or name, {"variant": 0}))
        used.add((rcode, tcode, 0))
    variants = ("Prompt", "Month 1", "Month 2")  # up to three series a group holds
    next_id = 60001
    for v, suffix in enumerate(variants):  # every group gets its prompt series first, then the others in turn
        for rcode, tcode, gname, sheet in groups:
            if len(masters) >= CRACK_SERIES or (rcode, tcode, v) in used:
                continue
            if v == 0 and any(m.region == rcode and m.crack_type == tcode for m in masters):
                continue
            name = f"{gname.replace(' , ', ', ')} {suffix}"
            masters.append(PriceMaster(str(next_id), name, name, "crack", "$/Bbl", "synthesized", rcode, tcode, gname, sheet,
                                       name, {"variant": v}))
            used.add((rcode, tcode, v))
            next_id += 1
    assert len(masters) == CRACK_SERIES, len(masters)
    assert len({m.group for m in masters}) == len(groups) == 44
    return masters


def benchmark_masters():
    return [PriceMaster(pid, name, disp, "benchmark", unit, "real", sheet="Benchmark", group="Benchmark",
                        mips_display=mips, extra={"eia": eia, "max_period": maxp})
            for pid, name, disp, mips, unit, eia, maxp in BENCHMARKS]
