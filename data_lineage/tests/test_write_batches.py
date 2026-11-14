from neo4j_loader import Neo4jLoader


class _RecordingDriver:
    def __init__(self):
        self.runs = []

    def session(self, **_):
        driver = self

        class _Tx:
            def run(self, query, **params):
                driver.runs.append((query, params))

        class _Session:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def execute_write(self, fn, *args):
                return fn(_Tx(), *args)

        return _Session()


def _loader():
    loader = Neo4jLoader.__new__(Neo4jLoader)
    loader.driver = _RecordingDriver()
    loader.database = "test"
    return loader


def test_canonicalize_table_qn_returns_stored_spelling():
    lookup = {"sem_masterdata.product_vw": "sem_masterdata.Product_VW"}
    assert Neo4jLoader.canonicalize_table_qn(
        "sem_masterdata.Product_vw", lookup
    ) == "sem_masterdata.Product_VW"
    assert Neo4jLoader.canonicalize_table_qn(
        "sem_masterdata.Product_vw", lookup
    ) == "sem_masterdata.Product_VW"
    assert Neo4jLoader.canonicalize_table_qn("brand.new.Table", lookup) == "brand.new.Table"
    assert Neo4jLoader.canonicalize_table_qn(None, lookup) is None
    assert Neo4jLoader.canonicalize_table_qn("", lookup) == ""


def test_canonicalize_table_fields_rewrites_only_named_fields():
    lookup = {"a.b": "A.B"}
    rows = [{"qualifiedName": "a.b", "other": "a.b"}]
    Neo4jLoader.canonicalize_table_fields(rows, lookup, "qualifiedName")
    assert rows == [{"qualifiedName": "A.B", "other": "a.b"}]


def test_write_batches_splits_rows_into_500_row_transactions():
    loader = _loader()
    rows = [{"i": i} for i in range(1201)]

    assert loader.write_batches("Q", rows) == 1201
    assert [len(p["rows"]) for _, p in loader.driver.runs] == [500, 500, 201]
    assert [r for _, p in loader.driver.runs for r in p["rows"]] == rows


def test_write_batches_passes_extra_params_to_every_batch():
    loader = _loader()

    loader.write_batches("Q", [{}] * 3, batch_size=2, runStart="2026-01-01")

    assert [p["runStart"] for _, p in loader.driver.runs] == ["2026-01-01"] * 2


def test_write_batches_with_no_rows_runs_nothing():
    loader = _loader()

    assert loader.write_batches("Q", []) == 0
    assert loader.driver.runs == []
