"""Read queries against any local or remote database through a SQLAlchemy URL.

URL examples (put one in SOURCE_DB_URL):
    sqlite:///source.db
    duckdb:///synthetic_data/source.duckdb
    postgresql+psycopg://user:<password>@localhost:5432/lsc_source
    mssql+pyodbc://localhost\\SQLEXPRESS/lsc_source?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes
"""

import os

import pandas as pd
from sqlalchemy import create_engine, text


def query_database(query: str, url: str | None = None, **params) -> pd.DataFrame:
    """Run one read query and return its rows; `url` defaults to SOURCE_DB_URL."""
    url = url or os.getenv("SOURCE_DB_URL")
    if not url:
        raise ValueError("No database URL: pass url= or set SOURCE_DB_URL")
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            return pd.read_sql_query(text(query), conn, params=params or None)
    finally:
        engine.dispose()
