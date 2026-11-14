from pathlib import Path

import pytest

from neo4j_loader import ENV_PATH, Neo4jLoader


@pytest.fixture(scope="session")
def graph():
    """Neo4jLoader against the live graph, for read-only checks; skips when credentials are absent."""
    if not Path(ENV_PATH).exists():
        pytest.skip("neo4j_instance_credentials.env not found")
    loader = Neo4jLoader()
    yield loader
    loader.close()
