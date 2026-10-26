"""Offline tests of the demo's data: determinism, the shapes the shared assets have, the provenance labels, and the
scenario's relabelling. Expected values are written out by hand from EPM-DEC-001-0097 and the EIA cache."""
import csv
import datetime as dt
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pricing_demo import catalog, generate, public_data  # noqa: E402
from pricing_demo.config import PROVENANCE  # noqa: E402

TABLES = generate.build()


def digest(tables):
    h = hashlib.sha256()
    for system in sorted(tables):
        for name in sorted(tables[system]):
            t = tables[system][name]
            h.update(repr((system, name, t.columns, t.rows)).encode())
    return h.hexdigest()


def rows(system, table):
    t = TABLES[system][table]
    return [dict(zip(t.columns, r)) for r in t.rows]


def test_the_same_seed_gives_the_same_rows():
    assert digest(generate.build()) == digest(TABLES)


def test_127_crack_series_in_44_groups_keep_the_named_ids():
    cracks = catalog.crack_masters()
    assert len(cracks) == 127 and len({m.group for m in cracks}) == 44
    named = {m.id: m.name for m in cracks if m.provenance == "real"}
    # EPM-DEC-001-0097 item 4 and market-data 1.0.0: the six primary regional series, the blends and the NYMEX crack.
    assert named["37438"] == "CHI 3-2-1 Crack WTI, ex-RIN"
    assert named["43870"] == "USGC 3-2-1 MEH Crack, ex-RIN"
    assert {"36855", "37439", "37443", "37471", "37464", "42023", "39998"} <= set(named)
    assert {m.id for m in cracks if m.provenance == "synthesized" and int(m.id) < 60000} == {"44934", "44935"}


def test_the_five_benchmarks_and_their_tenors():
    bench = {m.id: m for m in catalog.benchmark_masters()}
    assert set(bench) == {"572", "747", "750", "752", "9471"}
    detail = rows("mpr", "pricedetail")
    tenors = {}
    for r in detail:
        if str(r["PriceMasterId"]) in bench:
            tenors.setdefault(str(r["PriceMasterId"]), set()).add(r["RelativePeriodNum"])
    assert tenors["572"] == set(range(0, 7)) and tenors["747"] == set(range(0, 8))


def test_every_price_row_is_labelled():
    for system, table in (("mpr", "pricedetail"), ("mips", "mips_priceassessment"), ("prodacct", "refinery_daily"),
                          ("ctrm", "deal"), ("mpr", "pricemaster")):
        labels = {r["DemoProvenance"] for r in rows(system, table)}
        assert labels <= set(PROVENANCE), (system, table, labels)


def test_real_rows_are_eia_values():
    wti = public_data.load("wti")
    day = dt.date(2026, 10, 20)
    spot = [r for r in rows("mpr", "pricedetail") if r["PriceMasterId"] == 747 and r["EffectiveStartDate"].date() == day]
    by_period = {r["RelativePeriodNum"]: r for r in spot}
    assert by_period[0]["SettlePrice"] == round(wti[day], 6) == 107.89 and by_period[0]["DemoProvenance"] == "real"
    assert by_period[1]["SettlePrice"] == 107.89 and by_period[1]["DemoProvenance"] == "spot-anchored"
    assert all(by_period[p]["DemoProvenance"] == "synthesized" for p in range(2, 8))


def test_nyh_ulsd_cash_is_real_and_its_basis_spot_anchored():
    groups = {r["ID"]: r for r in rows("mips", "mips_priceassessmentgroup")}
    pgroups = {r["ID"]: r for r in rows("mips", "mips_pricegroup")}
    found = {}
    for r in rows("mips", "mips_priceassessment"):
        g = groups[r["PriceAssessmentGroupID"]]
        if g["Name"] == "NYH ULSD" and r["SortOrder"] == 1 and r["updated_at"].date() == dt.date(2026, 10, 20):
            found[pgroups[g["PriceGroupID"]]["Name"]] = r
    assert found["Cash"]["Value"] == 5.265 and found["Cash"]["DemoProvenance"] == "real"
    assert found["Basis"]["Value"] == 0.0 and found["Basis"]["DemoProvenance"] == "spot-anchored"


def test_refineries_are_mpcs_13_with_their_10k_capacities():
    refineries = rows("prodacct", "refinery")
    assert len(refineries) == 13 and sum(r["CrudeCapacityMbpcd"] for r in refineries) == 2986


def test_the_sql_holds_the_shared_names_and_columns():
    sql = open(os.path.join(ROOT, "sql", "04_gold.sql")).read() + open(os.path.join(ROOT, "sql", "05_metric_views.sql")).read()
    for name in ("gold_commercial_core.mpr_mips_crack_spread_price_fact", "gold_commercial_core.mips_mpr_executive_summary_fact",
                 "semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw",
                 "semantic_sem_commercial.mips_mpr_executive_summary_fact_vw",
                 "semantic_sem_commercial.mips_mpr_benchmark_prices_fact_vw"):
        assert name in sql, name
    for field in ("MIPS_Groups_Text", "Price_Master_Name", "Effective_Month", "Relative_Period_Number", "Avg_Crack_Spread",
                  "Spread_Range", "MIPSDisplayName", "Parent_Price_group_name", "SortColumns", "Blend", "Avg_Settle_Price"):
        assert re.search(rf"- name: {field}\b", sql), field
    # The benchmark view's known defect is kept on purpose: every instrument x100, and the 160-day window.
    assert "Settle_Price_Amount * 100 ELSE" in sql and "INTERVAL 160 DAYS" in sql


def test_the_scenario_is_relabelled():
    text = open(os.path.join(ROOT, "SCENARIO.md")).read()
    body = text.split("-->", 1)[1]
    assert "FACT" not in body and "ChatGPT" not in body and body.count("**Scenario") == 30


def test_the_eia_cache_names_each_series():
    with open(os.path.join(ROOT, "data", "public", "eia_series.csv")) as f:
        meta = {r["key"]: r for r in csv.DictReader(f)}
    assert meta["wti"]["series_id"] == "PET.RWTC.D" and meta["nyh_gasoline"]["series_id"] == "PET.EER_EPMRU_PF4_Y35NY_DPG.D"
    assert set(meta) == set(public_data.EIA_SERIES)


# ---- Kimi round 1 findings ----
import json  # noqa: E402
import shutil  # noqa: E402
import types  # noqa: E402

import pytest  # noqa: E402

from pricing_demo import config, databricks, genie, load_postgres, replicate, scenario  # noqa: E402

SQL_TEXT = {f: open(os.path.join(ROOT, "sql", f)).read() for f in os.listdir(os.path.join(ROOT, "sql"))}


def metric_views():
    """{view name: (dimensions, measures)} parsed from 05_metric_views.sql."""
    views = {}
    for m in re.finditer(r"CREATE OR REPLACE VIEW \S+\.(\w+)\s+WITH METRICS.*?\$\$(.*?)\$\$", SQL_TEXT["05_metric_views.sql"], re.S):
        body = m.group(2)
        dims = body.split("measures:")[0]
        meas = body.split("measures:")[1]
        views[m.group(1)] = (set(re.findall(r"- name: (\w+)", dims)), set(re.findall(r"- name: (\w+)", meas)))
    return views


def test_finding_6_a_carried_eia_value_is_spot_anchored_not_real():
    # 2026-05-04: Brent has no EIA observation that day; the generator carries May 1's value (118.26).
    brent = public_data.load("brent")
    assert dt.date(2026, 5, 4) not in brent and brent[dt.date(2026, 5, 1)] == 118.26
    rows_ = [r for r in rows("mpr", "pricedetail") if r["PriceMasterId"] == 572 and r["EffectiveStartDate"].date() == dt.date(2026, 5, 4)]
    period0 = next(r for r in rows_ if r["RelativePeriodNum"] == 0)
    assert period0["SettlePrice"] == 118.26 and period0["DemoProvenance"] == "spot-anchored"


def test_finding_16_a_gap_in_the_cache_raises_instead_of_looping():
    market = object.__new__(generate.Market)
    market.series = {"x": {}, "late": {dt.date(2026, 10, 1): 1.0}}
    with pytest.raises(ValueError):
        market._last("x", dt.date(2026, 5, 4))
    with pytest.raises(ValueError):
        market._last("late", dt.date(2026, 5, 4))
    assert market._last("late", dt.date(2026, 10, 3)) == (1.0, dt.date(2026, 10, 1))


def test_finding_9_every_price_and_operations_table_is_labelled_and_no_high_low_is_generated():
    labelled = {("mpr", "pricedetail"), ("mpr", "pricemaster"), ("mips", "mips_priceassessment"), ("prodacct", "refinery_daily"),
                ("ctrm", "deal"), ("ctrm", "movement"), ("planning", "plan_target")}
    for system, table in labelled:
        t = TABLES[system][table]
        assert "DemoProvenance" in t.columns, (system, table)
        assert {r[t.columns.index("DemoProvenance")] for r in t.rows} <= set(PROVENANCE), (system, table)
    detail = rows("mpr", "pricedetail")
    assert all(r["HighPrice"] is None and r["LowPrice"] is None for r in detail)
    assert "DemoProvenance AS Demo_Provenance_Label" in SQL_TEXT["03_silver.sql"].split("refinery_plan_target_fact")[1].split(";")[0]


def test_finding_15_assessment_groups_carry_their_own_units():
    units = {r["ID"]: r["Code"] for r in rows("mips", "mips_unitofmeasure")}
    by_name = {r["Name"]: units[r["UnitOfMeasureID"]] for r in rows("mips", "mips_priceassessmentgroup")}
    assert by_name["NYMEX Natural Gas ($-MMbtu)"] == "$/MMbtu"
    assert by_name["NYMEX Heating Oil (cpg)"] == by_name["NYMEX RBOB (cpg)"] == "$/gal"
    assert by_name["ICE, BRENT ($-Bbl)"] == "$/Bbl"
    assert by_name["CBOT SBO"] == "cents/lb"


def test_finding_4_every_metric_view_defines_record_count_and_counts_uses_it():
    for view, (_, measures) in metric_views().items():
        assert "Record_Count" in measures, view

    class Cursor:
        def __init__(self):
            self.queries = []

        def execute(self, q):
            self.queries.append(q)

        def fetchall(self):
            return [(7,)]
    cur = Cursor()
    assert databricks.count(cur, "c.semantic_sem_commercial.refinery_operations_metrics_vw", metric_view=True) == 7
    assert cur.queries == ["SELECT MEASURE(Record_Count) FROM c.semantic_sem_commercial.refinery_operations_metrics_vw"]


def test_finding_8_the_executive_summary_view_passes_every_gold_column_through():
    gold = SQL_TEXT["04_gold.sql"].split("mips_mpr_executive_summary_fact AS")[1].split("FROM")[0]
    gold = re.sub(r"\([^()]*\)", "(x)", gold)  # a function's arguments are not output columns
    columns = set(re.findall(r"(\w+)\s*(?=,|\n|$)", gold.split("SELECT", 1)[1]))  # each output column's name
    assert len(columns) == 24, sorted(columns)
    dims, measures = metric_views()["mips_mpr_executive_summary_fact_vw"]
    assert columns - dims - measures == set(), columns - dims - measures


def test_findings_2_and_3_every_measure_an_agent_names_is_in_a_view_it_binds():
    views = metric_views()
    for title, spec in genie.AGENTS.items():
        bound = {t.split(".")[-1] for t, _ in spec["tables"]}
        allowed = set().union(*(views[b][1] for b in bound))
        text = open(os.path.join(ROOT, "genie", spec["file"])).read() + " ".join(s for _, s in spec["examples"])
        named = set(re.findall(r"MEASURE\((\w+)\)", text))
        assert named and named <= allowed, (title, named - allowed)
        # Examples read only the views the agent binds, never gold.
        assert "gold_commercial_core" not in " ".join(s for _, s in spec["examples"])
    exec_text = open(os.path.join(ROOT, "genie", "executive-summary-kpis-analytics.md")).read()
    assert "MEASURE(assessment_amount) / MEASURE(Record_Count)" in exec_text
    benchmark_rules = exec_text.split("Benchmark Prices: ")[1].split("\n")[0]
    assert "Avg_Settle_Price" in benchmark_rules and "It has no `assessment_amount`" in benchmark_rules


def make_replica(folder, manifest_tables, files):
    os.makedirs(folder, exist_ok=True)
    for key in files:
        os.makedirs(os.path.dirname(os.path.join(folder, key)), exist_ok=True)
        open(os.path.join(folder, f"{key}.parquet"), "w").close()
    with open(os.path.join(folder, "manifest.json"), "w") as f:
        json.dump({"tables": manifest_tables}, f)


def test_finding_5_an_empty_partial_or_mismatched_replica_is_refused(tmp_path):
    expected = {f"{s}/{t}": 3 for s, ts in replicate.expected_tables().items() for t in ts}
    rows3 = lambda file: 3  # noqa: E731  stands in for reading each Parquet footer
    with pytest.raises(SystemExit):
        replicate.check_replica(str(tmp_path / "none"), rows_of=rows3)  # no manifest at all
    partial = dict(list(expected.items())[:-1])
    make_replica(str(tmp_path / "partial"), partial, partial)
    with pytest.raises(SystemExit):
        replicate.check_replica(str(tmp_path / "partial"), rows_of=rows3)  # a table missing from the run
    make_replica(str(tmp_path / "nofile"), expected, list(expected)[:-1])
    with pytest.raises(SystemExit):
        replicate.check_replica(str(tmp_path / "nofile"), rows_of=rows3)  # a file missing
    make_replica(str(tmp_path / "ok"), expected, expected)
    with pytest.raises(SystemExit):
        replicate.check_replica(str(tmp_path / "ok"), rows_of=lambda file: 0)  # empty files
    assert replicate.check_replica(str(tmp_path / "ok"), rows_of=rows3) == expected


class BuiltCursor:
    """Answers SHOW TABLES with every expected object (less `missing`) and each count with `rows`."""

    def __init__(self, missing=None, rows=5, empty=None):
        self.missing, self.rows, self.empty = missing, rows, empty

    def execute(self, q):
        self.q = q

    def fetchall(self):
        if self.q.startswith("SHOW TABLES"):
            schema = self.q.rsplit(".", 1)[1]
            return [("c", n, False) for n in sorted(databricks.BUILT[schema]) if n != self.missing]
        return [(0 if self.empty and self.q.endswith(self.empty) else self.rows,)]


def test_finding_5_build_checks_every_silver_gold_and_view_object():
    with pytest.raises(SystemExit):
        databricks.check_built(BuiltCursor(missing="refinery_operations_daily_fact"), "c")
    databricks.check_built(BuiltCursor(), "c")


def test_pi_round_2_finding_2_an_empty_built_table_or_view_fails():
    with pytest.raises(SystemExit):
        databricks.check_built(BuiltCursor(empty="gold_commercial_core.mips_mpr_executive_summary_fact"), "c")
    with pytest.raises(SystemExit):
        databricks.check_built(BuiltCursor(empty="semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw"), "c")


def test_pi_round_2_finding_2_a_same_count_replica_from_another_run_fails():
    manifest = {"mpr/pricedetail": 10, "mpr/pricemaster": 2}
    taken = "2026-10-26T01:00:00"

    class Cursor:
        def __init__(self, stamp):
            self.stamp = stamp

        def execute(self, q):
            self.q = q

        def fetchall(self):
            n = 10 if "pricedetail" in self.q else 2
            return [(n, dt.datetime.fromisoformat(self.stamp), dt.datetime.fromisoformat(self.stamp))]
    with pytest.raises(SystemExit):  # the volume still holds the run before: same counts, older stamp
        databricks.check_replica_tables(Cursor("2026-10-25T22:00:00"), "c", manifest=manifest, taken=taken)
    databricks.check_replica_tables(Cursor(taken), "c", manifest=manifest, taken=taken)


def test_pi_round_2_observation_5_the_three_shifted_crude_series_carry_the_two_month_lag():
    groups = {r["ID"]: r["Name"] for r in rows("mips", "mips_priceassessmentgroup")}
    day = dt.date(2026, 10, 20)
    periods = {}
    for r in rows("mips", "mips_priceassessment"):
        if r["updated_at"].date() == day and r["SortOrder"] == 1:
            periods[groups[r["PriceAssessmentGroupID"]]] = r["PricePeriod"]
    for name in catalog.CRUDE_SHIFTED:
        assert periods[name] == dt.date(2026, 8, 1), name
    assert periods["Mars vs. WTI Cushing"] == periods["NYH ULSD"] == dt.date(2026, 10, 1)


def test_finding_7_replication_is_full_snapshot_only():
    import inspect
    assert "since" not in inspect.signature(replicate.replicate).parameters
    assert "--since" not in open(os.path.join(ROOT, "pricing_demo", "replicate.py")).read().split('"""', 2)[2]


def test_finding_11_one_catalog_rule_for_every_step():
    class Cursor:
        def __init__(self, catalogs, idp_schemas):
            self.catalogs, self.idp_schemas = catalogs, idp_schemas

        def execute(self, q):
            self.q = q

        def fetchall(self):
            return [(c,) for c in self.catalogs] if self.q == "SHOW CATALOGS" else [(s,) for s in self.idp_schemas]
    env = {"DEMO_CATALOG": "workspace"}
    assert databricks.current_catalog(Cursor(["workspace", "idp_sbx"], ["default"]), env) == "workspace"  # visible, not ours
    assert databricks.current_catalog(Cursor(["workspace"], []), env) == "workspace"
    assert databricks.current_catalog(Cursor(["workspace", "idp_sbx"], ["replica_landing"]), env) == "idp_sbx"


def test_finding_20_a_database_commits_only_after_every_table_loaded(monkeypatch):
    committed = []

    class Conn:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def commit(self):
            committed.append(True)

    fake = types.SimpleNamespace(connect=lambda dsn: Conn())
    monkeypatch.setitem(sys.modules, "psycopg", fake)

    def failing(conn, tables):
        raise RuntimeError("COPY failed midway")
    monkeypatch.setattr(load_postgres, "load_database", failing)
    with pytest.raises(RuntimeError):
        load_postgres.load(TABLES)
    assert committed == []


def test_finding_21_a_failed_refresh_leaves_the_cache_byte_for_byte(tmp_path):
    folder = tmp_path / "public"
    shutil.copytree(os.path.join(ROOT, "data", "public"), folder)
    before = {p: open(os.path.join(folder, p), "rb").read() for p in os.listdir(folder)}
    calls = []

    def fetch(series):
        calls.append(series)
        if len(calls) == 3:
            return []  # one series comes back empty
        return [{"period": "2026-10-20", "value": "1.0", "series-description": "x", "units": "y"}]
    with pytest.raises(SystemExit):
        public_data.refresh(fetch=fetch, folder=str(folder))
    after = {p: open(os.path.join(folder, p), "rb").read() for p in os.listdir(folder)}
    assert after == before


def test_finding_22_one_registry_of_source_systems():
    init = open(os.path.join(ROOT, "docker", "init", "01_databases.sql")).read()
    assert set(TABLES) == set(config.SYSTEMS) == set(re.findall(r"CREATE DATABASE (\w+);", init))
    assert {s for s in databricks.SCHEMAS if s.startswith("replica_") and s != "replica_landing"} == {f"replica_{s}" for s in config.SYSTEMS}
    assert set(replicate.expected_tables()) == set(config.SYSTEMS)
    replica_sql = set(re.findall(r"replica_(\w+)\.(\w+) AS", SQL_TEXT["02_replica.sql"]))
    assert replica_sql == {(s, t) for s, ts in replicate.expected_tables().items() for t in ts}


def test_finding_23_the_scenario_body_is_pinned_and_the_transform_makes_only_two_edits():
    body = open(os.path.join(ROOT, "SCENARIO.md")).read().split("-->", 1)[1]
    # Pinned on 2026-10-25 after comparing the transform of the decision owner's original line by line: 1,194 lines in,
    # 1,193 out, no line changed beyond the two permitted edits.
    assert hashlib.sha256(body.encode()).hexdigest() == "63e4e77ab7e511a42a0f23538357fa6171912074838f2216f1a7da2e78cf7d1a"
    fixture = "# T\n\n> **Note:** This file consolidates the briefings produced elsewhere.\n**FACT:** a figure.\n**FACT — Oct 9:** b.\nkeep me\n"
    out = scenario.transform(fixture).split("-->", 1)[1]
    assert out == "\n# T\n\n**Scenario:** a figure.\n**Scenario — Oct 9:** b.\nkeep me\n"
    with pytest.raises(ValueError):
        scenario.transform("a FACT left bare\n")


def test_finding_24_every_cached_series_matches_the_code_and_the_readme():
    with open(os.path.join(ROOT, "data", "public", "eia_series.csv")) as f:
        meta = {r["key"]: r for r in csv.DictReader(f)}
    readme = open(os.path.join(ROOT, "README.md")).read()
    assert set(meta) == set(public_data.EIA_SERIES) and len(meta) == 15
    for key, (series, role) in public_data.EIA_SERIES.items():
        assert meta[key]["series_id"] == series and meta[key]["demo_role"] == role, key
        assert meta[key]["description"] and meta[key]["units"] and meta[key]["pulled_on"] == "2026-10-25", key
        assert series in readme, series


def test_finding_10_postgres_listens_on_this_machine_only():
    compose = open(os.path.join(ROOT, "docker", "docker-compose.yml")).read()
    ports = re.findall(r'- "([^"]+)"', compose)
    assert ports == ["127.0.0.1:55432:5432"]


def test_bugbot_380_the_eia_key_is_read_from_the_demos_env(tmp_path, monkeypatch):
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))  # no ~/.config/eia/api.env
    monkeypatch.setattr(config, "ROOT", str(tmp_path))
    (tmp_path / ".env").write_text("SOURCE_PG_DSN=x\nEIA_API_KEY=from-dotenv\n")
    assert public_data.eia_key() == "from-dotenv"
    (tmp_path / ".env").write_text("EIA_API_KEY=\n")
    with pytest.raises(SystemExit):
        public_data.eia_key()


def test_bugbot_380_every_example_reads_its_view_only_with_measure():
    for spec in genie.AGENTS.values():
        for _, sql in spec["examples"]:
            assert "MAX(" not in sql and "gold_commercial_core" not in sql
            # Every read of a metric view (each "FROM {c}.semantic_sem_commercial.<view>") belongs to a SELECT that
            # names a MEASURE() and, when it groups, groups by dimensions: split the statement at each view read and
            # check the text between the nearest SELECT and that read (Pi on a1fd341: the old regex matched nothing).
            reads = [m.start() for m in re.finditer(r"FROM \{c\}\.semantic_sem_commercial\.", sql)]
            assert reads, sql
            for at in reads:
                select = sql.rfind("SELECT", 0, at)
                assert "MEASURE(" in sql[select:at], sql[select:at]
            for sub in re.findall(r"MEASURE\(Record_Count\) AS n FROM [^)]*", sql):
                assert "GROUP BY" in sub, sub


def test_purge_drops_only_what_the_build_creates_and_no_schema_by_cascade():
    from pricing_demo import databricks as dbx
    drops = dbx.purge_statements("cat")
    assert not any("CASCADE" in d for d in drops)
    made = {(s, n) for _, s, n in dbx.created_objects()}
    for schema, names in dbx.BUILT.items():
        assert {(schema, n) for n in names} <= made
    assert {s for s, _ in made} == set(dbx.SCHEMAS[1:])
    assert f"DROP VOLUME IF EXISTS cat.{dbx.VOLUME}" in drops
    assert drops[-len(dbx.SCHEMAS):] == [f"DROP SCHEMA IF EXISTS cat.{s}" for s in reversed(dbx.SCHEMAS)]
    assert sum(d.startswith(("DROP TABLE", "DROP VIEW")) for d in drops) == len(made)
