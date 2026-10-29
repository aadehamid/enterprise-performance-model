"""Offline tests of the demo's data: determinism, the shapes the shared assets have, the provenance labels, and the
scenario's relabelling. Expected values are written out by hand from EPM-DEC-001-0097 and the EIA cache."""
import csv
import glob
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
    detail = rows("price_reference", "pricedetail")
    tenors = {}
    for r in detail:
        if str(r["PriceMasterId"]) in bench:
            tenors.setdefault(str(r["PriceMasterId"]), set()).add(r["RelativePeriodNum"])
    assert tenors["572"] == set(range(0, 7)) and tenors["747"] == set(range(0, 8))


def test_every_price_row_is_labelled():
    for system, table in (("price_reference", "pricedetail"), ("price_assessment", "mips_priceassessment"), ("production_accounting", "refinery_daily"),
                          ("rightangle", "deal"), ("price_reference", "pricemaster")):
        labels = {r["DemoProvenance"] for r in rows(system, table)}
        assert labels <= set(PROVENANCE), (system, table, labels)


def test_real_rows_are_eia_values():
    wti = public_data.load("wti")
    day = dt.date(2026, 10, 20)
    spot = [r for r in rows("price_reference", "pricedetail") if r["PriceMasterId"] == 747 and r["EffectiveStartDate"].date() == day]
    by_period = {r["RelativePeriodNum"]: r for r in spot}
    assert by_period[0]["SettlePrice"] == round(wti[day], 6) == 107.89 and by_period[0]["DemoProvenance"] == "real"
    assert by_period[1]["SettlePrice"] == 107.89 and by_period[1]["DemoProvenance"] == "spot-anchored"
    assert all(by_period[p]["DemoProvenance"] == "synthesized" for p in range(2, 8))


def test_nyh_ulsd_cash_is_real_and_its_basis_spot_anchored():
    groups = {r["ID"]: r for r in rows("price_assessment", "mips_priceassessmentgroup")}
    pgroups = {r["ID"]: r for r in rows("price_assessment", "mips_pricegroup")}
    found = {}
    for r in rows("price_assessment", "mips_priceassessment"):
        g = groups[r["PriceAssessmentGroupID"]]
        if g["Name"] == "NYH ULSD" and r["SortOrder"] == 1 and r["updated_at"].date() == dt.date(2026, 10, 20):
            found[pgroups[g["PriceGroupID"]]["Name"]] = r
    assert found["Cash"]["Value"] == 5.265 and found["Cash"]["DemoProvenance"] == "real"
    assert found["Basis"]["Value"] == 0.0 and found["Basis"]["DemoProvenance"] == "spot-anchored"


def test_refineries_are_mpcs_13_with_their_10k_capacities():
    refineries = rows("production_accounting", "refinery")
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
    rows_ = [r for r in rows("price_reference", "pricedetail") if r["PriceMasterId"] == 572 and r["EffectiveStartDate"].date() == dt.date(2026, 5, 4)]
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
    labelled = {("price_reference", "pricedetail"), ("price_reference", "pricemaster"), ("price_assessment", "mips_priceassessment"), ("production_accounting", "refinery_daily"),
                ("rightangle", "deal"), ("rightangle", "movement"), ("aspen_pims", "plan_target")}
    for system, table in labelled:
        t = TABLES[system][table]
        assert "DemoProvenance" in t.columns, (system, table)
        assert {r[t.columns.index("DemoProvenance")] for r in t.rows} <= set(PROVENANCE), (system, table)
    detail = rows("price_reference", "pricedetail")
    assert all(r["HighPrice"] is None and r["LowPrice"] is None for r in detail)
    assert "DemoProvenance AS Demo_Provenance_Label" in SQL_TEXT["03_silver.sql"].split("refinery_plan_target_fact")[1].split(";")[0]


def test_finding_15_assessment_groups_carry_their_own_units():
    units = {r["ID"]: r["Code"] for r in rows("price_assessment", "mips_unitofmeasure")}
    by_name = {r["Name"]: units[r["UnitOfMeasureID"]] for r in rows("price_assessment", "mips_priceassessmentgroup")}
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
        bound = {t.split(".")[-1] for t, _ in spec["tables"] if t.startswith("semantic_sem_commercial.")}
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
    manifest = {"price_reference/pricedetail": 10, "price_reference/pricemaster": 2}
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
    groups = {r["ID"]: r["Name"] for r in rows("price_assessment", "mips_priceassessmentgroup")}
    day = dt.date(2026, 10, 20)
    periods = {}
    for r in rows("price_assessment", "mips_priceassessment"):
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
    assert set(TABLES) == set(config.SYSTEMS) | set(config.HIDDEN_SYSTEMS) == set(re.findall(r"CREATE DATABASE (\w+);", init))
    assert not set(config.SYSTEMS) & set(config.HIDDEN_SYSTEMS)
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
        assert meta[key]["description"] and meta[key]["units"] and meta[key]["pulled_on"] == "2026-10-28", key
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


class _Cursor:
    def __init__(self, comment, fail_on=None):
        self.comment, self.fail_on, self.ran = comment, fail_on, []
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False
    def execute(self, st):
        if self.fail_on and st.startswith(self.fail_on):
            raise RuntimeError("SCHEMA_NOT_EMPTY")
        self.ran.append(st)
        self._rows = ({"SHOW CATALOGS": [("idp_sbx",)], "SHOW SCHEMAS IN idp_sbx": [("replica_landing",)],
                       "DESCRIBE CATALOG idp_sbx": [("Comment", self.comment)]}).get(st, [])
    def fetchall(self):
        return self._rows


class _Conn:
    def __init__(self, cur):
        self.cur = cur
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False
    def cursor(self):
        return self.cur


def _drops(cur):
    return [s for s in cur.ran if s.startswith("DROP")]


def test_purge_lists_without_dropping_unless_yes():
    from pricing_demo import databricks as dbx
    cur = _Cursor(dbx.DEMO_COMMENT)
    dbx.purge(execute=False, connection=(_Conn(cur), {}))
    assert _drops(cur) == []
    cur = _Cursor(dbx.DEMO_COMMENT)
    dbx.purge(execute=True, connection=(_Conn(cur), {}))
    assert _drops(cur) == dbx.purge_statements("idp_sbx")


def test_purge_refuses_a_catalog_the_demo_did_not_create():
    from pricing_demo import databricks as dbx
    cur = _Cursor("someone else's catalog")
    try:
        dbx.purge(execute=True, connection=(_Conn(cur), {}))
        raise AssertionError("purge ran on a catalog the demo does not own")
    except SystemExit as err:
        assert "--catalog idp_sbx" in str(err)
    assert _drops(cur) == []
    cur = _Cursor("someone else's catalog")
    dbx.purge(execute=True, catalog="idp_sbx", connection=(_Conn(cur), {}))
    assert _drops(cur) == dbx.purge_statements("idp_sbx")


def test_purge_stops_at_a_schema_that_holds_something_else():
    from pricing_demo import databricks as dbx
    cur = _Cursor(dbx.DEMO_COMMENT, fail_on="DROP SCHEMA")
    try:
        dbx.purge(execute=True, connection=(_Conn(cur), {}))
        raise AssertionError("purge went on past a failed schema drop")
    except RuntimeError:
        pass
    assert not any(s.startswith("DROP SCHEMA") for s in cur.ran)


# ---- The three-year extension (2026-10-28) ----

def test_the_window_is_three_years_of_eia_trading_days():
    assert (config.WINDOW_START, config.WINDOW_END) == (dt.date(2023, 10, 21), dt.date(2026, 10, 20))
    batches = rows("price_assessment", "mips_pricebatch")
    assert len(batches) == 748
    assert min(b["EffectiveDate"].date() for b in batches) >= config.WINDOW_START
    assert len(rows("price_reference", "pricedetail")) == 599148
    assert len(rows("price_assessment", "mips_priceassessment")) == 266288
    assert len(rows("production_accounting", "refinery_daily")) == 13 * 748 == 9724


def test_the_holiday_rules_reproduce_the_2026_list_and_cover_the_window():
    assert generate.exchange_holidays(dt.date(2026, 4, 1), dt.date(2026, 10, 20)) == [
        dt.date(2026, 4, 3), dt.date(2026, 5, 25), dt.date(2026, 6, 19), dt.date(2026, 7, 3), dt.date(2026, 9, 7)]
    holidays = rows("reference_data_hub", "holidaycalendar")
    assert len(holidays) == 30 and dt.date(2024, 3, 29) in {h["HolidayDate"] for h in holidays}  # Good Friday 2024


def test_unit_rows_match_the_refinery_runs_and_stay_within_capacity():
    units = rows("production_accounting", "unit_daily")
    assert len(units) == 76296 and {u["DemoProvenance"] for u in units} == {"synthesized"}
    runs = {(r["RefineryCode"], r["ProductionDate"]): r["CrudeRunsMbpd"] for r in rows("production_accounting", "refinery_daily")}
    for u in units:
        assert u["UnitThroughputMbpd"] <= u["UnitCapacityMbpd"] + 1e-9, u
        if u["UnitCode"] == "ATM":
            assert u["UnitThroughputMbpd"] == runs[(u["RefineryCode"], u["ProductionDate"])], u
    by_refinery = {}
    for u in units:
        by_refinery.setdefault(u["RefineryCode"], set()).add(u["UnitCode"])
    assert "HCK" in by_refinery["GB"] and "HCK" not in by_refinery["DT"]  # hydrocracking only from 250 mbpcd
    assert "CKR" in by_refinery["DT"] and "CKR" not in by_refinery["EP"]  # coking only from 140 mbpcd
    assert len(by_refinery) == 13 and all({"ATM", "VAC", "FCC", "REF", "DHT", "NHT", "GHT"} <= s for s in by_refinery.values())


def test_plan_targets_take_last_years_us_utilization_for_the_same_month():
    plans = rows("aspen_pims", "plan_target")
    assert len(plans) == 13 * 37 == 481  # October 2023 to October 2026
    util = public_data.load("us_utilization")
    gb_jan25 = next(p for p in plans if p["RefineryCode"] == "GB" and p["PlanMonth"] == dt.date(2025, 1, 1))
    year_ago = [v for d, v in util.items() if d.year == 2024 and d.month == 1]
    assert gb_jan25["PlannedUtilizationPct"] == round(min(sum(year_ago) / len(year_ago), 97.0), 1)
    assert gb_jan25["PlannedDistillateYieldPct"] == 35.5 and gb_jan25["DemoProvenance"] == "synthesized"


def test_freight_rises_fourfold_through_the_scenarios_spike_and_is_synthesized():
    freight = rows("rightangle", "freight_rate")
    assert len(freight) == 2 * 748 and {f["DemoProvenance"] for f in freight} == {"synthesized"}
    nyh = [f for f in freight if f["RouteCode"] == "USGC-NYH"]
    before = [f["RateUsdPerBbl"] for f in nyh if dt.date(2026, 7, 1) <= f["RateDate"] < dt.date(2026, 8, 15)]
    after = [f["RateUsdPerBbl"] for f in nyh if f["RateDate"] >= dt.date(2026, 10, 9)]
    assert sum(after) / len(after) > 3 * sum(before) / len(before)


def test_the_event_table_holds_the_events_the_use_cases_name_from_their_sources():
    events = rows("reference_data_hub", "market_event")
    assert {e["EventKey"] for e in events} == {"diesel_scarcity", "g7_release", "hurricane_isaias", "freight_spike",
                                               "turnaround_season", "dyed_diesel_order", "china_export_restart",
                                               "turnaround_rb", "turnaround_an"}
    scenario_text = open(os.path.join(ROOT, "SCENARIO.md")).read()
    for e in events:  # since E6 each event's evidence comes from a Parallel Decisions call (outside.py, step events)
        assert e["EvidenceStatus"] in {"confirmed", "not found", "uncertain", "unknown"}, e["EventKey"]
        assert e["EvidenceStatus"] == "unknown" or 0 <= e["EvidenceProbability"] <= 1
        assert all(u.startswith("http") for u in json.loads(e["EvidenceCitations"]))
        if e["SourceKind"] == "briefing":
            assert "dyed diesel" in scenario_text and "resume refined-product exports" in scenario_text
            assert "5. Pricing policy and global supply" in scenario_text
    isaias = next(e for e in events if e["EventKey"] == "hurricane_isaias")
    assert (isaias["StartDate"], isaias["Region"], isaias["Category"]) == (dt.date(2026, 10, 7), "Gulf Coast", "weather")


def test_eia_weekly_holds_every_padd_series_six_years_back_all_real():
    series = rows("eia_weekly", "series")
    values = rows("eia_weekly", "weekly_value")
    assert len(series) == 28 and len(values) == 8792
    assert {v["DemoProvenance"] for v in values} == {"real"}
    assert min(v["WeekEnding"] for v in values) >= config.WEEKLY_START
    ids = {s["SeriesId"] for s in series}
    assert {"PET.WDISTP11.W", "PET.WGTSTP31.W", "PET.W_NA_YUP_R30_PER.W", "PET.WCRRIP52.W", "PET.WDIEXUS2.W"} <= ids
    data_md = open(os.path.join(ROOT, "DATA.md")).read()
    for s in series:
        assert s["SeriesId"] in data_md, s["SeriesId"]


# ---- E2 (2026-10-28): plan versions, the decision log, its evidence and the hidden dossiers ----
from pricing_demo import decisions  # noqa: E402

ONTOLOGY = os.path.join(ROOT, "..", "..", "business_architecture", "ontology")


def _price(master, day):
    return next(float(r["SettlePrice"]) for r in rows("price_reference", "pricedetail")
                if r["PriceMasterId"] == master and r["RelativePeriodNum"] == 0 and r["EffectiveStartDate"].date() == day)


def test_e2_tables_hold_their_grains_and_counts():
    versions = rows("aspen_pims", "plan_version")
    assert len(versions) == 13 * 35 == 455  # December 2023 to October 2026: earlier plan dates have no prices behind them
    assert len({(v["RefineryCode"], v["PlanMonth"]) for v in versions}) == 455
    assert min(v["PlanMonth"] for v in versions) == dt.date(2023, 12, 1)
    assert len(rows("aspen_pims", "decision_log")) == len(rows("decision_truth", "decision_dossier")) == 10
    evidence = rows("aspen_pims", "decision_evidence")
    assert len(evidence) == 22 and len({e["EvidenceId"] for e in evidence}) == 22
    per_decision = {}
    for e in evidence:
        per_decision[e["DecisionId"]] = per_decision.get(e["DecisionId"], 0) + 1
    assert set(per_decision.values()) <= {2, 3} and set(per_decision) == {f"D{i:02d}" for i in range(1, 11)}
    for t in ("plan_version", "decision_log", "decision_evidence"):
        assert {r["DemoProvenance"] for r in rows("aspen_pims", t)} == {"synthesized"}
    assert all(r["Synthetic"] is True for r in rows("decision_truth", "decision_dossier"))


def test_e2_no_plan_assumption_uses_a_price_after_its_plan_date():
    versions = rows("aspen_pims", "plan_version")
    for v in versions:
        assert v["AssumptionsFromDate"] <= v["AssumptionsThroughDate"] <= v["PlanDate"] < v["PlanMonth"], v
    # Recompute two versions from the price detail: up to 20 trading days up to the plan date, nothing later.
    days = sorted({r["RateDate"] for r in rows("rightangle", "freight_rate")})
    for code, month in (("GB", dt.date(2026, 10, 1)), ("LA", dt.date(2024, 6, 1))):
        v = next(x for x in versions if x["RefineryCode"] == code and x["PlanMonth"] == month)
        window = [d for d in days if d <= v["PlanDate"]][-20:]
        assert (window[0], window[-1]) == (v["AssumptionsFromDate"], v["AssumptionsThroughDate"])
        master = v["BenchmarkCrackPriceMasterId"]
        assert v["AssumedBenchmarkCrackUsdPerBbl"] == round(sum(_price(master, d) for d in window) / 20, 4)
        assert v["AssumedWtiUsdPerBbl"] == round(sum(_price(747, d) for d in window) / 20, 4)


def test_e2_hidden_truth_is_never_replicated_or_built():
    assert "decision_truth" not in replicate.expected_tables()
    assert not any("decision_truth" in s for s in databricks.SCHEMAS)
    statements = [re.sub(r"^--.*$", "", text, flags=re.M) for text in SQL_TEXT.values()]  # comments may name it
    assert not any("decision_truth" in text or "decision_dossier" in text for text in statements)
    public = set(TABLES["aspen_pims"]["decision_log"].columns) | set(TABLES["aspen_pims"]["decision_evidence"].columns)
    hidden_only = {"Drivers", "Constraints", "Options", "ActualOutcome", "ActualOutcomeData", "GroundTruthRationale",
                   "KnownUncertainties"}
    assert hidden_only <= set(TABLES["decision_truth"]["decision_dossier"].columns) and not hidden_only & public
    dossiers = {r["DecisionId"]: r for r in rows("decision_truth", "decision_dossier")}
    for e in rows("aspen_pims", "decision_evidence"):
        d = dossiers[e["DecisionId"]]
        assert e["AuthoredAt"] <= d["DecisionTime"] + dt.timedelta(days=1)  # written at the decision, before any outcome
        assert d["ActualOutcome"] not in e["EvidenceText"] and d["GroundTruthRationale"] not in e["EvidenceText"]


def test_e2_every_dossier_entity_is_an_iri_the_ontology_holds():
    slugs = {r["slug"] for r in csv.DictReader(open(os.path.join(ONTOLOGY, "organization", "roles.csv")))}
    refineries = set(re.findall(r"refmpc:(refinery-[a-z-]+) a org:Site", open(os.path.join(ONTOLOGY, "ref-mpc", "ref-mpc.ttl")).read()))
    measures = {r["measure_id"] for r in csv.DictReader(open(os.path.join(ONTOLOGY, "kpi", "measure-classification.csv")))}
    for d in rows("decision_truth", "decision_dossier"):
        for iri in json.loads(d["AffectedEntities"]):
            assert iri.startswith("https://w3id.org/lsc/ontology/modules/"), (d["DecisionId"], iri)
            tail = iri.rsplit("/", 1)[1]
            if "/ref-mpc/" in iri:
                assert tail in refineries, iri
            elif "/organization/role/" in iri:
                assert tail in slugs, iri
            else:
                assert "/kpi/measure/" in iri and tail in measures, iri


def test_e2_every_role_refinery_and_measure_named_exists_in_the_ontology():
    slugs = {r["slug"] for r in csv.DictReader(open(os.path.join(ONTOLOGY, "organization", "roles.csv")))}
    refineries = set(re.findall(r"refmpc:(refinery-[a-z-]+) a org:Site", open(os.path.join(ONTOLOGY, "ref-mpc", "ref-mpc.ttl")).read()))
    identifiers = {r["identifier"] for r in csv.DictReader(open(os.path.join(ONTOLOGY, "kpi", "measure-identifiers.csv")))}
    for d in rows("aspen_pims", "decision_log"):
        assert set(d["OwnerRoleSlugs"].split(";")) <= slugs, d["DecisionId"]
        assert {i.rsplit("/", 1)[1] for i in d["RefineryIris"].split(";")} <= refineries, d["DecisionId"]
        assert set(d["MeasureIdentifiers"].split(";")) <= identifiers, d["DecisionId"]
    assert {e["AuthorRoleSlug"] for e in rows("aspen_pims", "decision_evidence")} <= slugs
    assert set(decisions.REFINERY_SLUG) == {r["RefineryCode"] for r in rows("production_accounting", "refinery")}


def test_e2_actual_outcomes_are_recomputed_from_the_demos_own_tables():
    dossiers = {r["DecisionId"]: json.loads(r["ActualOutcomeData"]) for r in rows("decision_truth", "decision_dossier")}
    daily = {(r["RefineryCode"], r["ProductionDate"]): r["CrudeRunsMbpd"] for r in rows("production_accounting", "refinery_daily")}
    days = sorted({d for _, d in daily})
    # D04: the Robinson turnaround's lost throughput against the 28 days before it.
    base = [daily[("RB", d)] for d in days if dt.date(2026, 8, 24) <= d <= dt.date(2026, 9, 20)]
    lost = sum(max(sum(base) / len(base) - daily[("RB", d)], 0) for d in days if dt.date(2026, 9, 21) <= d <= dt.date(2026, 10, 12))
    assert dossiers["D04"]["lost_throughput_mbbl"] == round(lost, 1)
    # D06: the system's distillate yield, October against September.
    dist = {(r["RefineryCode"], r["ProductionDate"]): r["DistillateYieldPct"] for r in rows("production_accounting", "refinery_daily")}
    sep = [v for (c, d), v in dist.items() if dt.date(2026, 9, 1) <= d <= dt.date(2026, 9, 19)]
    octo = [v for (c, d), v in dist.items() if d >= dt.date(2026, 10, 1)]
    assert dossiers["D06"]["change_points"] == round(round(sum(octo) / len(octo), 4) - round(sum(sep) / len(sep), 4), 4)
    # D07: the domestic freight premium over the ten trading days from the load date.
    freight = {(r["RouteCode"], r["RateDate"]): r["RateUsdPerBbl"] for r in rows("rightangle", "freight_rate")}
    span = [d for d in days if d >= dt.date(2026, 10, 9)][:10]
    premium = sum(freight[("USGC-NYH", d)] - freight[("USGC-NWE", d)] for d in span) / len(span)
    assert len(span) == dossiers["D07"]["trading_days"] == 8  # the window ends on 2026-10-20
    assert dossiers["D07"]["avg_domestic_premium_usd_per_bbl"] == round(premium, 4)
    # D08: WTI ten trading days after the G7 release decision, from the price detail (EIA's spot).
    later = [d for d in days if d >= dt.date(2026, 10, 2)]
    assert dossiers["D08"]["wti_ten_days_later"] == _price(747, later[10])


def test_e2_data_md_and_the_readme_describe_the_new_tables():
    data_md = open(os.path.join(ROOT, "DATA.md")).read()
    for name in ("plan_version", "decision_log", "decision_evidence", "decision_dossier", "decision_truth",
                 "refinery_plan_version_fact", "decision_dim", "decision_evidence_fact", "refinery_plan_backcast_fact",
                 "decision_evidence_detail_fact"):
        assert f"`{name}`" in data_md, name
    readme = open(os.path.join(ROOT, "README.md")).read()
    for name in ("decisions.py", "decision_truth"):
        assert name in readme, name


# ---- E3 (2026-10-29): identifiers on every metric view, the market-price and unit views, the definitions views ----
IDENTIFIERS = {r["measure_id"]: r["identifier"]
               for r in csv.DictReader(open(os.path.join(ONTOLOGY, "kpi", "measure-identifiers.csv")))}
ID_PATTERN = r"(?:KPI|OPM)-\d{4}"


def _leading_ids(comment):
    """The identifiers a comment starts with, before its first colon; none for "No identifier: ..."."""
    head = comment.split(":", 1)[0]
    return set() if head == "No identifier" else set(re.findall(ID_PATTERN, head))


def metric_view_specs():
    """{view: {"comment", "tag", "measures": {name: {"comment", "display_name", "synonyms"}}}} from 05_metric_views.sql."""
    text = SQL_TEXT["05_metric_views.sql"]
    specs = {}
    for m in re.finditer(r"CREATE OR REPLACE VIEW \S+\.(\w+)\s+WITH METRICS.*?\$\$(.*?)\$\$", text, re.S):
        view, body = m.group(1), m.group(2)
        head, meas = body.split("\nmeasures:\n")
        measures = {}
        for chunk in meas.split("  - name: ")[1:]:
            def field(key):
                found = re.search(rf'^    {key}: "([^"]*)"', chunk, re.M)
                return found.group(1) if found else None
            synonyms = re.search(r"^    synonyms: \[(.*)\]", chunk, re.M)
            measures[chunk.split("\n", 1)[0].strip()] = {
                "comment": field("comment"), "display_name": field("display_name"),
                "synonyms": re.findall(r'"([^"]*)"', synonyms.group(1)) if synonyms else []}
        tag = re.search(rf"ALTER VIEW \S+\.{view}\s+SET TAGS \('epm_measure_identifiers' = '([^']*)'\)", text)
        specs[view] = {"comment": re.search(r'^comment: "([^"]*)"', head, re.M).group(1),
                       "tag": tag.group(1) if tag else "", "measures": measures}
    return specs


# Which identifiers each view's measures carry, written out by hand from kpi 1.3.0 and EPM-DEC-001-0109, decision 2.
VIEW_IDENTIFIERS = {
    "mpr_mips_crack_spread_price_fact_metrics_vw": {"KPI-0001"},
    "mips_mpr_executive_summary_fact_vw": {"KPI-0001", "OPM-0017", "OPM-0018", "OPM-0019", "OPM-0020", "OPM-0021"},
    "mips_mpr_benchmark_prices_fact_vw": {"OPM-0019"},
    "pricing_market_margin_metrics_vw": {"OPM-0017", "OPM-0018", "OPM-0019", "OPM-0020", "OPM-0021"},
    "refinery_operations_metrics_vw": {"OPM-0002", "OPM-0004", "OPM-0005", "OPM-0024", "OPM-0025", "OPM-0027"},
    "refinery_unit_operations_metrics_vw": {"OPM-0001"},
}
# Each definitions view: the metric views whose comments point to it, and identifiers it keeps beyond theirs.
DEFINITIONS = {
    "crack_spread_definitions_vw": ({"mpr_mips_crack_spread_price_fact_metrics_vw"}, set()),
    "executive_summary_definitions_vw": ({"mips_mpr_executive_summary_fact_vw", "mips_mpr_benchmark_prices_fact_vw"}, set()),
    "pricing_market_margin_definitions_vw": ({"pricing_market_margin_metrics_vw"}, {"OPM-0026"}),  # defined, not computed
    "refinery_operations_definitions_vw": ({"refinery_operations_metrics_vw", "refinery_unit_operations_metrics_vw"}, set()),
}


def test_e3_every_measure_carries_kpi_identifiers_or_says_it_has_none():
    specs = metric_view_specs()
    assert set(specs) == set(VIEW_IDENTIFIERS)
    known = set(IDENTIFIERS.values())
    for view, spec in specs.items():
        carried = set()
        for name, m in spec["measures"].items():
            assert m["comment"], (view, name)
            ids = _leading_ids(m["comment"])
            assert ids <= known, (view, name, ids - known)
            if ids:  # the display name and the synonyms carry them too, so Genie and BI tools can find the measure
                shown = set(re.findall(ID_PATTERN, m["display_name"] or ""))
                assert shown and shown <= ids, (view, name)
                assert ids <= set(m["synonyms"]) and len(m["synonyms"]) <= 10, (view, name)
            else:
                assert m["comment"].startswith("No identifier: "), (view, name)
            # No synonym or display name names an identifier the measure does not implement, in any letter case
            # (Pi, quick checks of c0504444 and its fix).
            named = " ".join(m["synonyms"] + [m["display_name"] or ""])
            assert {i.upper() for i in re.findall(ID_PATTERN, named, re.IGNORECASE)} == ids, (view, name)
            carried |= ids
        assert carried == VIEW_IDENTIFIERS[view], view
        assert spec["comment"].startswith("Implements ") and _leading_ids(spec["comment"]) == carried, view
        assert set(spec["tag"].split(" ")) == carried, view


def test_e3_kpi_0001_stays_crack_spreads_and_the_crack_agent_names_it():
    assert IDENTIFIERS["crack-spreads"] == "KPI-0001"
    crack = metric_view_specs()["mpr_mips_crack_spread_price_fact_metrics_vw"]["measures"]
    assert _leading_ids(crack["Avg_Crack_Spread"]["comment"]) == {"KPI-0001"}
    assert "KPI-0001" in open(os.path.join(ROOT, "genie", "crack-spread-price-analytics.md")).read()


def test_e3_the_new_views_hold_their_measures_and_skip_the_rm_margin_indicator():
    specs = metric_view_specs()
    ids = {view: {n: _leading_ids(m["comment"]) for n, m in s["measures"].items()} for view, s in specs.items()}
    assert ids["pricing_market_margin_metrics_vw"] == {
        "Gasoline_Market_Price": {"OPM-0017"}, "Distillate_Market_Price": {"OPM-0018"}, "Crude_Market_Price": {"OPM-0019"},
        "Price_Comparison": {"OPM-0020"}, "Additional_Market_Price": {"OPM-0021"}, "Record_Count": set()}
    assert ids["refinery_unit_operations_metrics_vw"] == {
        "Unit_Throughput_Mbpd": set(), "Unit_Capacity_Mbpd": set(), "Unit_Utilization_Pct": {"OPM-0001"}, "Record_Count": set()}
    # The R&M Margin Indicator's basis is not published (kpi 1.3.0), so no view computes it and the pricing view says so.
    assert IDENTIFIERS["rm-margin-indicator"] == "OPM-0026"
    assert not any("OPM-0026" in i for view in ids.values() for i in view.values())
    assert "OPM-0026 R&M Margin Indicator is not computed" in specs["pricing_market_margin_metrics_vw"]["comment"]
    pricing = SQL_TEXT["05_metric_views.sql"].split("VIEW ${catalog}.semantic_sem_commercial.pricing_market_margin_metrics_vw")[1]
    assert "source.SortColumns = 1" in pricing and "gold_commercial_core.mips_mpr_executive_summary_fact" in pricing
    # Spark reads 'NGL''s' as two adjacent literals, 'NGLs', so the NGL group needs a backslash (found on the live run).
    assert "''" not in SQL_TEXT["05_metric_views.sql"] and r"'NGL\'s'" in pricing
    unit = SQL_TEXT["05_metric_views.sql"].split("VIEW ${catalog}.semantic_sem_commercial.refinery_unit_operations_metrics_vw")[1]
    assert "gold_commercial_core.refinery_unit_operations_daily_fact" in unit
    assert "100 * SUM(Unit_Throughput_Mbpd) / SUM(Unit_Capacity_Mbpd)" in unit


def test_e3_each_measure_carries_the_identifiers_kpi_gives_its_measures():
    # Each measure is pinned to kpi measure slugs, and the identifiers come from measure-identifiers.csv, so a swapped
    # identifier in a comment, or a renumbering in kpi, fails here and not only in review (Pi, round 1 and quick check).
    prices = ["crack-spreads", "gasoline-prices", "distillate-prices", "crude-prices", "price-comparison",
              "additional-market-prices"]
    expected = {
        "mpr_mips_crack_spread_price_fact_metrics_vw": {
            "Avg_Crack_Spread": ["crack-spreads"], "Max_Crack_Spread": ["crack-spreads"],
            "Min_Crack_Spread": ["crack-spreads"], "Spread_Range": ["crack-spreads"], "Record_Count": []},
        "mips_mpr_executive_summary_fact_vw": {
            "assessment_amount": prices, "Previous_amount": prices, "ChangeValue": prices, "Record_Count": []},
        "mips_mpr_benchmark_prices_fact_vw": {"Avg_Settle_Price": ["crude-prices"], "Record_Count": []},
        "pricing_market_margin_metrics_vw": {
            "Gasoline_Market_Price": ["gasoline-prices"], "Distillate_Market_Price": ["distillate-prices"],
            "Crude_Market_Price": ["crude-prices"], "Price_Comparison": ["price-comparison"],
            "Additional_Market_Price": ["additional-market-prices"], "Record_Count": []},
        "refinery_operations_metrics_vw": {
            "Crude_Runs_Mbpd": [], "Crude_Capacity_Mbpcd": [], "Utilization_Pct": ["crude-utilization"],
            "Planned_Utilization_Pct": ["crude-utilization"], "Distillate_Yield_Pct": ["distillate-yield"],
            "Gasoline_Yield_Pct": ["gasoline-yield"], "Rm_Margin_Usd_Per_Bbl": ["rm-margin-per-barrel"],
            "Margin_Capture_Pct": ["margin-capture"], "Opex_Usd_Per_Bbl": ["refining-opex-per-barrel"],
            "Record_Count": []},
        "refinery_unit_operations_metrics_vw": {
            "Unit_Throughput_Mbpd": [], "Unit_Capacity_Mbpd": [], "Unit_Utilization_Pct": ["unit-utilization"],
            "Record_Count": []},
    }
    specs = metric_view_specs()
    assert set(expected) == set(specs)
    for view, measures in expected.items():
        want = {name: {IDENTIFIERS[slug] for slug in slugs} for name, slugs in measures.items()}
        assert {n: _leading_ids(m["comment"]) for n, m in specs[view]["measures"].items()} == want, view
    # The Executive Summary comment's body maps each assessment group to its measure; _leading_ids reads only the head.
    groups = (f"the crack sheets {IDENTIFIERS['crack-spreads']}, Gasoline Cash {IDENTIFIERS['gasoline-prices']}, "
              f"Diesel Cash {IDENTIFIERS['distillate-prices']}, the crude sheets and Benchmark {IDENTIFIERS['crude-prices']}, "
              f"Basis {IDENTIFIERS['price-comparison']}, Renewables and NGL's {IDENTIFIERS['additional-market-prices']}.")
    assert groups in specs["mips_mpr_executive_summary_fact_vw"]["measures"]["assessment_amount"]["comment"]


def test_e3_definitions_views_read_epm_triples_and_keep_their_views_identifiers():
    text = SQL_TEXT["06_definitions.sql"]
    base = text.split("measure_definitions_vw AS")[1].split(";\n")[0]
    assert "FROM ${epm_triples}" in base
    select = base.split("\nSELECT ", 1)[1].split("\nFROM ")[0]
    columns = [c.split()[-1].split(".")[-1] for c in select.replace("\n", " ").split(",")]  # each output column's name
    assert columns == ["Identifier", "Label", "Definition", "Grain", "Basis", "Not_To_Be_Confused_With", "Kind",
                       "Release_Graph", "Measure_Iri"]
    for predicate in ("dc/terms/identifier", "skos/core#prefLabel", "skos/core#definition", "kpi/grain", "kpi/basis",
                      "kpi/notToBeConfusedWith", "kpi/measureKind"):
        assert predicate in base, predicate
    specs = metric_view_specs()
    for name, (views, extra) in DEFINITIONS.items():
        kept = set(re.findall(ID_PATTERN, text.split(f"ontology_definitions.{name} AS")[1].split(";")[0]))
        assert kept == set().union(*(VIEW_IDENTIFIERS[v] for v in views)) | extra, name
        assert kept <= set(IDENTIFIERS.values()), name
        for v in views:
            assert specs[v]["comment"].endswith(f"Definitions: ontology_definitions.{name}."), v
    assert "ontology_definitions" in databricks.SCHEMAS
    assert databricks.BUILT["ontology_definitions"] == set(DEFINITIONS) | {"measure_definitions_vw"}
    assert databricks.BUILT["semantic_sem_commercial"] == set(VIEW_IDENTIFIERS)


def test_e3_statements_fill_in_the_catalog_and_the_triple_table():
    sts = databricks.statements(os.path.join(ROOT, "sql", "06_definitions.sql"), "cat", "ws.onto.epm_triples")
    assert len(sts) == 5 and all("${" not in s for s in sts)
    assert "FROM ws.onto.epm_triples" in sts[0] and sts[1].startswith("CREATE OR REPLACE VIEW cat.ontology_definitions.")
    views = databricks.statements(os.path.join(ROOT, "sql", "05_metric_views.sql"), "cat", "ws.onto.epm_triples")
    assert sum(s.startswith("ALTER VIEW cat.semantic_sem_commercial.") for s in views) == len(VIEW_IDENTIFIERS)


# ---- E4 (2026-10-29): four Genie agents, each reading its definitions view, and the supervisor over them ----
from pricing_demo import supervisor  # noqa: E402

# Each agent's metric views and its definitions view (EPM-DEC-001-0109, decisions 3 and 4).
AGENT_VIEWS = {
    "Crack Spread Price Analytics": ({"mpr_mips_crack_spread_price_fact_metrics_vw"}, "crack_spread_definitions_vw"),
    "Executive Summary KPIs Analytics": ({"mips_mpr_executive_summary_fact_vw", "mips_mpr_benchmark_prices_fact_vw"},
                                         "executive_summary_definitions_vw"),
    "Pricing and Market Margin Analytics": ({"pricing_market_margin_metrics_vw"}, "pricing_market_margin_definitions_vw"),
    "Refinery Operations Analytics": ({"refinery_operations_metrics_vw", "refinery_unit_operations_metrics_vw"},
                                      "refinery_operations_definitions_vw"),
}


def test_e4_each_agent_binds_its_metric_views_and_its_definitions_view():
    assert set(genie.AGENTS) == set(AGENT_VIEWS)
    for title, spec in genie.AGENTS.items():
        views, definitions = AGENT_VIEWS[title]
        bound = {t for t, _ in spec["tables"]}
        assert bound == {f"semantic_sem_commercial.{v}" for v in views} | {f"ontology_definitions.{definitions}"}, title
        # The definitions view is the one sql/06 builds for these metric views, and the instructions name it.
        assert DEFINITIONS[definitions][0] == views, title
        text = open(os.path.join(ROOT, "genie", spec["file"])).read()
        assert f"${{catalog}}.ontology_definitions.{definitions}`" in text, title
        assert "without `MEASURE()`" in text, title


def test_e4_the_new_agents_name_exactly_the_identifiers_their_definitions_view_keeps():
    for title in ("Pricing and Market Margin Analytics", "Refinery Operations Analytics"):
        views, definitions = AGENT_VIEWS[title]
        carried = set().union(*(VIEW_IDENTIFIERS[v] for v in views))
        text = open(os.path.join(ROOT, "genie", genie.AGENTS[title]["file"])).read()
        assert set(re.findall(ID_PATTERN, text)) == carried | DEFINITIONS[definitions][1], title
        assert set(re.findall(ID_PATTERN, genie.AGENTS[title]["description"])) == carried, title


def test_e4_no_genie_instruction_or_example_doubles_a_quote():
    # Spark reads 'NGL''s' as two adjacent literals, 'NGLs', which matches nothing (found on E3's live run).
    for spec in genie.AGENTS.values():
        text = open(os.path.join(ROOT, "genie", spec["file"])).read()
        assert "''" not in text and all("''" not in s for _, s in spec["examples"]), spec["file"]
    exec_spec = genie.AGENTS["Executive Summary KPIs Analytics"]
    assert r"'NGL\'s'" in open(os.path.join(ROOT, "genie", exec_spec["file"])).read()
    assert any(r"Price_Group_Name = 'NGL\'s' AND SortColumns = 1" in s for _, s in exec_spec["examples"])


def test_e4_supervisor_descriptions_come_from_the_definitions_rows_and_mark_what_no_view_computes():
    spec = genie.AGENTS["Pricing and Market Margin Analytics"]
    text = supervisor.description("Pricing and Market Margin Analytics", spec,
                                  [("OPM-0017", "Gasoline Market Pricing"), ("OPM-0026", "R&M Margin Indicator")], {"OPM-0017"})
    assert "pricing_market_margin_metrics_vw" in text and "ontology_definitions" not in text
    assert "OPM-0017 Gasoline Market Pricing;" in text and "OPM-0026 R&M Margin Indicator (defined, not computed)" in text
    # One tool per agent, with distinct names, each asking for one question.
    tools = supervisor.tools({t: "d" for t in genie.AGENTS})
    names = [t["function"]["name"] for t in tools]
    assert len(set(names)) == len(genie.AGENTS) and all(re.fullmatch(r"[a-z0-9_]+", n) for n in names)
    assert all(t["function"]["parameters"]["required"] == ["question"] for t in tools)
    assert ({supervisor.definitions_view(s) for s in genie.AGENTS.values()}
            == {f"ontology_definitions.{d}" for _, d in AGENT_VIEWS.values()})


def test_e4_descriptions_refuse_a_metric_view_without_its_identifier_tag(monkeypatch):
    # Without the tags every measure would read as "defined, not computed" (Pi, round 1): fail closed instead.
    def run(cur, sql):
        return [] if "table_tags" in sql else [("KPI-0001", "Crack Spreads Pricing")]
    monkeypatch.setattr(supervisor, "run", run)
    with pytest.raises(SystemExit, match="no epm_measure_identifiers tag"):
        supervisor.descriptions(None, "idp_sbx")


def test_e4_the_supervisor_names_the_regional_cracks_the_gold_margin_uses():
    case = re.search(r"CASE r\.Region_Name (.*?) END", SQL_TEXT["04_gold.sql"]).group(1)
    pairs = dict(re.findall(r"WHEN '([^']+)' THEN '(\d+)'", case)) | {"Mid-Continent": re.search(r"ELSE '(\d+)'", case).group(1)}
    names = {pm: name for pm, name, *_ in catalog.NAMED_CRACKS}
    for region, pm in pairs.items():
        assert f"{region}, {names[pm]} ({pm})" in supervisor.INSTRUCTIONS, region
    regions = {r["region"] for r in csv.DictReader(open(os.path.join(ROOT, "data", "public", "mpc_refineries.csv")))}
    assert regions == set(pairs)


# ---- E5 (2026-10-29): the technical graph, the decision trail, the Delta copy, the AuraDB test, the lineage test ----
from collections import Counter, defaultdict  # noqa: E402
from decimal import Decimal  # noqa: E402

from pricing_demo import aura_probe, aura_test, tech_graph  # noqa: E402

TV = tech_graph.VOCAB
OBJECT_CLASSES = {"ReplicaTable", "SilverTable", "GoldTable", "MetricView", "DefinitionsView", "TechGraphTable"}


def _graph(*names):
    from rdflib import Graph
    g = Graph()
    for name in names:
        g.parse(os.path.join(ROOT, "graph", name), format="turtle")
    return g


def _name(iri):
    return str(iri).rsplit("/", 1)[1]


def _pairs(g, predicate):
    from rdflib import URIRef
    found = defaultdict(set)
    for s, o in g.subject_objects(URIRef(TV + predicate)):
        found[_name(s)].add(_name(o))
    return found


def test_e5_the_graph_holds_every_object_the_build_creates_with_its_rows_and_last_refresh():
    nodes, _ = tech_graph.graph_rows(_graph("tech-graph.ttl"))
    assert 90 <= len(nodes) <= 120  # "about 100 nodes" (EPM-DEC-001-0109, decision 6)
    objects = {n["props"]["name"]: n for n in nodes if OBJECT_CLASSES & set(n["labels"])}
    assert set(objects) == {f"{s}.{n}" for _, s, n in databricks.created_objects()}
    assert all(isinstance(n["props"].get("rows"), int) and n["props"].get("lastRefresh") for n in objects.values())
    kinds = Counter(label for n in nodes for label in n["labels"][1:])
    assert kinds["SourceDatabase"] == len(config.SYSTEMS) + len(config.HIDDEN_SYSTEMS)
    assert kinds["GenieAgent"] == len(genie.AGENTS) and kinds["Orchestrator"] == kinds["Host"] == kinds["TripleTable"] == 1
    assert all(len(n["labels"]) == 2 for n in nodes)  # Tech and one class


def test_e5_each_metric_view_implements_the_measures_of_its_identifiers():
    slug = {identifier: s for s, identifier in IDENTIFIERS.items()}
    assert _pairs(_graph("tech-graph.ttl"), "implements") == {
        f"semantic_sem_commercial.{v}": {slug[i] for i in ids} for v, ids in VIEW_IDENTIFIERS.items()}


def test_e5_a_gold_table_walks_to_the_measures_its_metric_views_implement():
    g = _graph("tech-graph.ttl")
    readers = defaultdict(set)
    for down, ups in _pairs(g, "readsFrom").items():
        for up in ups:
            readers[up].add(down)
    implements = _pairs(g, "implements")
    gold = "gold_commercial_core.mips_mpr_executive_summary_fact"  # the walk's default start
    views = {v for v in readers[gold] if v.startswith("semantic_sem_commercial.")}
    assert views == {"semantic_sem_commercial.mips_mpr_executive_summary_fact_vw", "semantic_sem_commercial.pricing_market_margin_metrics_vw"}
    assert set().union(*(implements[v] for v in views)) == {
        "crack-spreads", "gasoline-prices", "distillate-prices", "crude-prices", "price-comparison", "additional-market-prices"}
    _, edges = tech_graph.graph_rows(g)
    for used in re.findall(r"\[:([A-Z_]+)\]", tech_graph.WALK):  # the walk names relationship types the loader makes
        assert used in {e["t"] for e in edges}, used


def test_e5_only_tech_nodes_and_edges_out_of_them_so_the_projection_counts_cannot_move():
    # The projection counts :Resource nodes and the edges between them (pipeline.py graph_hash; runbook, Check).
    nodes, edges = tech_graph.graph_rows(_graph("tech-graph.ttl", "decision-trail.ttl"))
    assert all(n["labels"][0] == "Tech" and "Resource" not in n["labels"] for n in nodes)
    uris = {n["props"]["uri"] for n in nodes}
    assert all(e["s"] in uris for e in edges)
    assert all(e["o"] in uris for e in edges if not e["ontology"])
    assert all(e["o"].startswith(tech_graph.ONTOLOGY) for e in edges if e["ontology"])


def test_e5_every_link_to_the_ontology_names_a_resource_it_holds():
    from rdflib import Graph, URIRef
    held = Graph()
    for module in ("kpi", "organization", "ref-mpc", "data-product", "system"):
        for path in sorted(os.listdir(os.path.join(ONTOLOGY, module))):
            if path.endswith(".ttl"):
                held.parse(os.path.join(ONTOLOGY, module, path), format="turtle")
    _, edges = tech_graph.graph_rows(_graph("tech-graph.ttl", "decision-trail.ttl"))
    targets = {e["o"] for e in edges if e["ontology"]}
    missing = sorted(t for t in targets if (URIRef(t), None, None) not in held)
    assert targets and not missing, missing[:5]


def test_e5_the_decision_trail_is_prov_o_from_the_visible_tables_only():
    from rdflib import RDF, URIRef
    g = _graph("decision-trail.ttl")
    prov = tech_graph.PROV
    activities = set(g.subjects(RDF.type, URIRef(prov + "Activity")))
    items = set(g.subjects(RDF.type, URIRef(prov + "Entity")))
    assert len(activities) == len(rows("aspen_pims", "decision_log")) == 10
    assert len(items) == len(rows("aspen_pims", "decision_evidence")) == 22
    for item in items:  # each item was used by its decision or generated by it, never both
        used = set(g.subjects(URIRef(prov + "used"), item))
        made = set(g.objects(item, URIRef(prov + "wasGeneratedBy")))
        assert len(used | made) == 1 and not (used and made), item
    assert all(set(g.objects(d, URIRef(prov + "wasAssociatedWith"))) for d in activities)
    text = " ".join(str(o) for o in g.objects())
    for d in rows("decision_truth", "decision_dossier"):  # nothing only the hidden dossiers hold
        assert d["ActualOutcome"] not in text and d["GroundTruthRationale"] not in text


def test_e5_the_lineage_comparison_names_edges_found_in_only_one_place():
    found = tech_graph.compare_lineage(
        designed_tables={"a", "b", "c", "x"}, designed={("a", "b"), ("b", "c"), ("x", "b")},
        observed={("a", "b"), ("c", "b"), ("z", "b")}, present={"a", "b", "c", "z"})
    assert found == {"designed_only": [("b", "c")], "observed_only": [("c", "b")], "matched": [("a", "b")],
                     "designed_not_built": [("x", "b")]}  # z is outside the design; x is not built
    assert tech_graph.demo_name("synapse_dev.replica_mips.mips_currency") == "replica_price_assessment.mips_currency"
    assert tech_graph.demo_name("synapse_dev.replica_kittyhawk.priceservice") == "replica_reference_data_hub.priceservice"
    assert tech_graph.demo_name("idp_sbx.silver_udm_core.mpr_price_detail_fact") == "silver_udm_core.mpr_price_detail_fact"


def test_e5_the_steps_follow_the_readme_run_block_and_each_points_to_the_next():
    from rdflib import URIRef
    g = _graph("tech-graph.ttl")
    ordered = [str(n) for _, n in sorted((int(o), g.value(s, URIRef(TV + "name")))
                                          for s, o in g.subject_objects(URIRef(TV + "order")))]
    readme = open(os.path.join(ROOT, "README.md")).read()
    commands = re.findall(r"(?m)^uv run (?:--group (?:graph|outside) )?python -m (pricing_demo\.[a-z_]+(?: [a-z]+(?= ))?)", readme)
    assert ordered == list(dict.fromkeys(commands))
    assert sum(len(v) for v in _pairs(g, "next").values()) == len(ordered) - 1


def test_e5_every_quality_check_has_a_result_and_covers_nodes_the_graph_holds():
    from rdflib import RDF, URIRef
    g = _graph("tech-graph.ttl")
    checks = set(g.subjects(RDF.type, URIRef(TV + "QualityCheck")))
    assert {str(g.value(c, URIRef(TV + "name"))) for c in checks} >= {
        "replica-matches-manifest", "built-objects-hold-rows", "metric-views-tagged", "rows-labelled",
        "decision-truth-hidden", "designed-vs-observed-lineage"}
    assert all(str(g.value(c, URIRef(TV + "result"))) in ("pass", "fail", "differs", "skipped") for c in checks)
    typed = set(g.subjects(RDF.type, None))
    assert all(o in typed for c in checks for o in g.objects(c, URIRef(TV + "checks")))


def test_e5_literals_reach_neo4j_as_it_stores_them_and_edge_types_read_like_cypher():
    from rdflib import URIRef
    assert tech_graph.neo4j_value(Decimal("5")) == 5 and isinstance(tech_graph.neo4j_value(Decimal("5")), int)
    assert tech_graph.neo4j_value(Decimal("2.5")) == 2.5
    assert tech_graph.neo4j_value(dt.datetime(2026, 10, 29, 12)) == "2026-10-29T12:00:00"
    assert tech_graph.edge_type(URIRef(tech_graph.PROV + "wasGeneratedBy")) == "WAS_GENERATED_BY"
    assert tech_graph.edge_type(URIRef(TV + "readsFrom")) == "READS_FROM"


def test_e5_the_aura_test_writes_the_login_to_a_secret_scope_and_never_prints_it():
    assert aura_test.SCOPE == aura_probe.SCOPE == "epm-neo4j"
    assert set(aura_test.KEYS) == {"uri", "username", "password"}
    for module in (aura_probe, aura_test):
        prints = re.findall(r"print\((.*)\)", open(module.__file__).read())
        assert prints and not any(re.search(r"\b(uri|user|password|login)\b", p) for p in prints), prints
    assert aura_test.probe_line('noise\nAURA_PROBE {"dns": {"ok": true}}\n') == {"dns": {"ok": True}}


def test_e5_the_tech_graph_tables_are_built_empty_and_purged_and_every_query_runs():
    made = set(databricks.created_objects())
    assert {("TABLE", "tech_graph", "tech_graph_nodes"), ("TABLE", "tech_graph", "tech_graph_edges")} <= made
    assert "tech_graph" in databricks.SCHEMAS and "tech_graph" not in databricks.BUILT
    assert "''" not in SQL_TEXT["07_tech_graph.sql"]  # Spark reads '' as two literals (E3)
    assert set(os.listdir(tech_graph.SPARQL)) == set(tech_graph.GRAPH_QUERIES + tech_graph.TRAIL_QUERIES) | {"wiring.rq"}


def test_e5_the_driver_login_is_the_newest_run_env(tmp_path):
    # After a driver run with --skip rebuild only the first container's login is current (Bugbot on PR E5).
    from pricing_demo import tech_graph
    rebuild, first = tmp_path / "rebuild.env", tmp_path / "first.env"
    rebuild.write_text("PASSWORD=old\n")
    first.write_text("PASSWORD=new\n")
    os.utime(rebuild, (1, 1))
    assert tech_graph.login_file((str(rebuild), str(first))) == str(first)
    assert tech_graph.login_file((str(rebuild), str(tmp_path / "missing.env"))) == str(rebuild)
    with pytest.raises(SystemExit):
        tech_graph.login_file((str(tmp_path / "missing.env"),))


# ---- E6 (2026-10-29): the outside context from Parallel Decisions (pricing_demo/outside.py) ----
from pricing_demo import outside  # noqa: E402

OUTSIDE = outside.requests(TABLES)


def test_e6_interpret_follows_typesafe_thresholds_and_labels():
    assert outside.interpret({"type": "noul", "noul": 0.7})[::3] == ("yes", "observed")
    assert outside.interpret({"type": "noul", "noul": 0.3})[::3] == ("no", "observed")
    assert outside.interpret({"type": "noul", "noul": 0.5})[::3] == ("uncertain", "unknown")
    assert outside.interpret({"type": "noul", "noul": 0.9}, forward=True)[3] == "inferred"  # never observed ahead
    choice = {"type": "choice", "choice": "weather", "probabilities": {"weather": 0.5, "policy": 0.5}, "confidence": 0.31}
    assert outside.interpret(choice) == ("weather", 0.5, 0.31, "inferred", None)
    assert outside.interpret({**choice, "confidence": 0.29})[3] == "unknown"
    assert outside.interpret({"type": "refusal"})[3] == "unknown"


def test_e6_the_requests_cover_each_region_month_decision_event_and_forward_month():
    steps = Counter(step for step, *_ in OUTSIDE)
    assert steps == {"smoke": 1, "events": 9, "monthly": 108, "diagnosis": 10, "forward": 9}
    months = outside.full_months()
    assert (months[0], months[-1], len(months)) == (dt.date(2023, 11, 1), dt.date(2026, 10, 1), 36)
    assert outside.forward_months() == [dt.date(2026, 11, 1), dt.date(2026, 12, 1), dt.date(2027, 1, 1)]


def test_e6_a_diagnosis_reads_only_the_decision_log_the_agents_see():
    hidden = {"Drivers", "Constraints", "Options", "ActualOutcome", "ActualOutcomeData", "GroundTruthRationale",
              "KnownUncertainties"}
    dossiers = {d["DecisionId"]: d for d in rows("decision_truth", "decision_dossier")}
    for step, request_id, body, ctx in OUTSIDE:
        if step != "diagnosis":
            continue
        assert set(body["state"]) == {"decision", "decided_on", "expected_outcome", "refineries", "region", "window"}
        text = json.dumps(body)
        for field in hidden:  # no dossier-only text reaches the request
            value = dossiers[ctx["decision_id"]][field]
            assert value in (None, "", "[]", "{}") or str(value) not in text, (request_id, field)


def test_e6_every_request_is_cached_and_no_cache_keeps_an_excerpt_or_a_key():
    for step, request_id, body, _ in OUTSIDE:
        saved = outside.cached(request_id, body)
        assert saved is not None, request_id
        raw = open(outside.cache_path(request_id)).read()
        assert "excerpts" not in raw and "PARALLEL_API_KEY" not in raw and "x-api-key" not in raw
        assert all(set(c) == {"url", "title"} for c in saved["citations"])


def test_e6_a_call_caches_the_response_and_a_changed_request_is_not_answered_from_it(tmp_path, monkeypatch):
    monkeypatch.setattr(outside, "CACHE", str(tmp_path))

    class Client:
        def post(self, path, body, cast_to):
            assert path == "/v1/decisions" and cast_to is object
            return {"mode": "fast", "answers": {"q": {"type": "noul", "noul": 0.8}},
                    "citations": [{"url": "https://example.org/a", "title": "A", "excerpts": ["long text"]}]}

    body = {"state": {"x": 1}, "questions": {"q": {"type": "noul", "instructions": "Is it?"}}}
    saved = outside.call(Client(), "r1", body, now=dt.datetime(2026, 10, 29, tzinfo=dt.timezone.utc))
    assert saved["citations"] == [{"url": "https://example.org/a", "title": "A"}]
    assert outside.cached("r1", body)["answers"]["q"]["noul"] == 0.8
    assert outside.cached("r1", {**body, "state": {"x": 2}}) is None


def test_e6_the_tables_link_each_answer_to_iris_the_ontology_holds():
    hub = TABLES["reference_data_hub"]
    events, forward = hub["external_event"], hub["forward_scan"]
    assert (len(events.rows), len(forward.rows), len(hub["external_citation"].rows)) == (344, 45, 1360)
    refineries = set(re.findall(r"refmpc:(refinery-[a-z-]+) a org:Site", open(os.path.join(ONTOLOGY, "ref-mpc", "ref-mpc.ttl")).read()))
    products = set(re.findall(r"modules/party/product/([a-z0-9-]+)", "".join(
        open(os.path.join(ONTOLOGY, "party", f)).read() for f in os.listdir(os.path.join(ONTOLOGY, "party")) if f.endswith(".ttl"))))
    series = {r["slug"] for r in csv.DictReader(open(os.path.join(ONTOLOGY, "market-data", "series.csv")))}
    measures = {r["measure_id"] for r in csv.DictReader(open(os.path.join(ONTOLOGY, "kpi", "measure-classification.csv")))}
    known = {"/ref-mpc/": refineries, "/party/product/": products, "/market-data/series/": series, "/kpi/measure/": measures}
    for table in (events, forward):
        c = table.columns
        for r in table.rows:
            for col in ("RefineryIris", "ProductIris", "SeriesIri", "MeasureIris"):
                for iri in filter(None, (r[c.index(col)] or "").split(";")):
                    part = next(k for k in known if k in iri)
                    assert iri.rsplit("/", 1)[1] in known[part], iri


def test_e6_forward_answers_are_never_observed_and_a_suggestion_waits_for_a_person():
    forward = TABLES["reference_data_hub"]["forward_scan"]
    c = forward.columns
    assert {r[c.index("EvidenceLabel")] for r in forward.rows} <= {"inferred", "unknown"}
    suggested = [r for r in forward.rows if r[c.index("SuggestedAction")]]
    assert suggested
    log = {r["DecisionId"] for r in rows("aspen_pims", "decision_log")}
    for r in suggested:
        assert r[c.index("EvidenceLabel")] == "inferred" and r[c.index("ApprovalStatus")] == "awaiting a person"
        assert set(r[c.index("MatchedDecisionIds")].split(";")) <= log


def test_e6_the_outside_tables_flow_through_the_replica_and_silver_layers():
    replica, silver = SQL_TEXT["02_replica.sql"], SQL_TEXT["03_silver.sql"]
    for t in ("external_event", "forward_scan", "external_citation"):
        assert f"replica_reference_data_hub.{t} AS" in replica and f"replica_reference_data_hub.{t};" in silver
    assert {"external_event_fact", "forward_scan_fact"} <= databricks.BUILT["silver_udm_core"]
    assert "external_citation_dim" in databricks.BUILT["silver_mdm_core"]


def test_e6_citation_titles_name_no_person():
    # The repository names no person; a source's byline is dropped from its title (Pi, round 1 on E6).
    from pricing_demo import outside
    assert outside.title_without_byline("The Diesel Forecast - by Dr. Jane Doe") == "The Diesel Forecast"
    assert outside.title_without_byline("Refinery outages rise by 5% in PADD 3") == "Refinery outages rise by 5% in PADD 3"
    # a page about a person is kept only as its host (Bugbot on #407); an article URL stays whole
    assert outside.kept_citation("https://muckrack.com/a-reporter/articles", "Articles by A Reporter") == {
        "url": "https://muckrack.com", "title": "A person's profile page (not kept)"}
    assert outside.kept_citation("https://www.energy.gov/articles/spr-exchange", "SPR exchange")["url"].endswith("/spr-exchange")
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "parallel", "*.json"))):
        for c in json.load(open(path)).get("citations", []):
            assert not outside.BYLINE.search(c["title"] or ""), (path, c["title"])
            assert not outside.PROFILE.search(c["url"] or ""), (path, c["url"])
