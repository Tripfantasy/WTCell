"""
db.py
=====
Database connection and helper functions for WTCell.

All database interactions are centralised here so that the Streamlit front-end
(app.py) and any future CLI/batch tooling share the same connection logic and
query primitives.

Environment variable / secret:
  NEON_DATABASE_URL — full PostgreSQL URL
    e.g. postgresql://user:password@host/dbname?sslmode=require
"""

import os
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError

logger = logging.getLogger(__name__)


def require_database_url() -> str:
    """
    Return database URL from environment.

    Raises RuntimeError if NEON_DATABASE_URL is missing.
    """
    url = os.getenv("NEON_DATABASE_URL")
    if url:
        return url

    logger.error(
        "NEON_DATABASE_URL is not set. Set it in Streamlit secrets or local .env."
    )
    raise RuntimeError(
        "NEON_DATABASE_URL is missing. Please configure it before running the app."
    )


# ===========================================================================
# Connection management
# ===========================================================================

def get_connection() -> psycopg2.extensions.connection:
    """
    Open and return a new psycopg2 connection using NEON_DATABASE_URL.
    """
    conn = psycopg2.connect(require_database_url())
    return conn


@contextmanager
def get_cursor(dict_cursor: bool = True):
    conn = get_connection()
    cursor_factory = psycopg2.extras.RealDictCursor if dict_cursor else None
    cur = conn.cursor(cursor_factory=cursor_factory)
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

# ...keep the rest of your existing helper functions unchanged...
