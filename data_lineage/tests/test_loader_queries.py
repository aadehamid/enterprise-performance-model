import importlib
import pkgutil
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
LOADER_MODULES = sorted(m.name for m in pkgutil.iter_modules([str(SRC)]) if m.name.startswith("load_"))


def _module_queries():
    for name in LOADER_MODULES:
        module = importlib.import_module(name)
        for attr, value in vars(module).items():
            if attr.isupper() and isinstance(value, str) and ("MATCH" in value or "MERGE" in value):
                yield pytest.param(value, id=f"{name}.{attr}")


@pytest.mark.integration
@pytest.mark.parametrize("query", list(_module_queries()))
def test_loader_query_plans(graph, query):
    """EXPLAIN plans the query without running it, so syntax errors surface without writing."""
    with graph.driver.session(database=graph.database) as session:
        session.run("EXPLAIN " + query, rows=[], qn="", layer="Silver", tableName="").consume()
