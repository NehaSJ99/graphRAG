import os
from typing import Optional, Dict, Any, List

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

from langchain_community.utilities import SQLDatabase  
from langchain.sql_database import SQLDatabase  

# Load env variables
load_dotenv()

# Connection details from environment
DATABRICKS_SERVER_HOST = os.getenv('DATABRICKS_SERVER_HOST')
DATABRICKS_HTTP_PATH = os.getenv('DATABRICKS_HTTP_PATH')
DATABRICKS_ACCESS_TOKEN = os.getenv('DATABRICKS_ACCESS_TOKEN')
CATALOG_NAME = os.getenv('CATALOG_NAME')
SCHEMA_NAME = os.getenv('SCHEMA_NAME')
# Correct connection string for SQLAlchemy
connection_string = (
    f"databricks://token:{DATABRICKS_ACCESS_TOKEN}@{DATABRICKS_SERVER_HOST}:443"
    f"/?http_path={DATABRICKS_HTTP_PATH}&catalog={CATALOG_NAME}&schema={SCHEMA_NAME}"
)

_ENGINE: Optional[Engine] = None


def _require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env var: {name}")
    return val


def _build_connection_string() -> str:
    """Return the Databricks SQLAlchemy URI built from environment variables."""
    return connection_string


def get_engine() -> Engine:
    """Return a module-level singleton SQLAlchemy Engine for Databricks."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(connection_string, future=True)
    return _ENGINE


def execute_sql(query: str, params: Optional[Dict[str, Any]] = None) -> List[Any]:
    """Execute a SQL statement and return all rows.

    Params can be a dictionary for bound parameters.
    """
    eng = get_engine()
    with eng.connect() as conn:
        result = conn.execute(text(query), params or {})
        return list(result.fetchall())


def get_sqldb(include_tables: Optional[List[str]] = None) -> SQLDatabase:
    """Return a LangChain SQLDatabase bound to the shared engine.

    include_tables optionally limits schema introspection to a subset.
    """
    eng = get_engine()
    try:
        if include_tables:
            return SQLDatabase.from_engine(eng, include_tables=include_tables)  # type: ignore[arg-type]
        return SQLDatabase.from_engine(eng)  # type: ignore[arg-type]
    except Exception:
        # Fallback for older versions
        if include_tables:
            return SQLDatabase(engine=eng, include_tables=include_tables)  # type: ignore[call-arg]
        return SQLDatabase(engine=eng)  # type: ignore[call-arg]


def list_tables() -> None:
    rows = execute_sql("SHOW TABLES")
    for row in rows:
        print(row)


if __name__ == "__main__":
    list_tables()
