"""
db.py
=====
Database connection and helper functions for WTCell.

All database interactions are centralised here so that the Streamlit front-end
(app.py) and any future CLI/batch tooling share the same connection logic and
query primitives.

Environment variables (set in .env or the host environment):
  DB_HOST     — PostgreSQL host          (default: localhost)
  DB_PORT     — PostgreSQL port          (default: 5432)
  DB_NAME     — Database name            (default: wtcell)
  DB_USER     — Database user            (default: wtcell_user)
  DB_PASSWORD — Database password        (required)
"""

import os
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras          # for RealDictCursor
from psycopg2 import OperationalError

# ---------------------------------------------------------------------------
# Module-level logger
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Connection configuration (read from environment variables).
# DB_PASSWORD MUST be set in the environment — there is no hard-coded default.
# The docker-compose.yml injects the value explicitly for the dev stack.
# If DB_PASSWORD is missing the application will fail to connect and surface
# a clear OperationalError rather than silently using a known credential.
# ---------------------------------------------------------------------------

DB_CONFIG: Dict[str, Any] = {
    "host":     os.getenv("DB_HOST",  "localhost"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME",  "wtcell"),
    "user":     os.getenv("DB_USER",  "wtcell_user"),
    "password": os.getenv("DB_PASSWORD"),  # required — no default
}

# Warn operators (not raise) so that Streamlit can display a friendly error
# on the UI rather than crashing at import time.
if not DB_CONFIG["password"]:
    logger.warning(
        "DB_PASSWORD environment variable is not set.  "
        "The application will be unable to connect to the database.  "
        "Set DB_PASSWORD in your .env file or host environment."
    )


# ===========================================================================
# Connection management
# ===========================================================================

def get_connection() -> psycopg2.extensions.connection:
    """
    Open and return a new psycopg2 connection using the module-level DB_CONFIG.

    Raises
    ------
    psycopg2.OperationalError
        If the database cannot be reached (wrong credentials, host, port …).
    """
    conn = psycopg2.connect(**DB_CONFIG)
    # Use autocommit=False (the default) so that callers control transactions.
    return conn


@contextmanager
def get_cursor(dict_cursor: bool = True):
    """
    Context manager that yields a database cursor and handles commit/rollback.

    Parameters
    ----------
    dict_cursor : bool
        If True (default), yield a ``RealDictCursor`` so that rows are
        returned as dicts (column_name → value) rather than plain tuples.

    Yields
    ------
    psycopg2 cursor

    Example
    -------
    ::

        with get_cursor() as cur:
            cur.execute("SELECT * FROM organisms")
            rows = cur.fetchall()
    """
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


# ===========================================================================
# Read helpers
# ===========================================================================

def fetch_all_organisms() -> List[Dict]:
    """
    Return all rows from the ``organisms`` table, ordered by common name.

    Returns
    -------
    list of dict
        Each dict contains: organism_id, common_name, scientific_name,
        ncbi_taxon_id, nomenclature_authority.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT organism_id, common_name, scientific_name,
                   ncbi_taxon_id, nomenclature_authority
            FROM   organisms
            ORDER  BY common_name
            """
        )
        return cur.fetchall()


def fetch_all_cell_types() -> List[Dict]:
    """
    Return all rows from the ``cell_types`` table, ordered by standardized_name.

    Returns
    -------
    list of dict
        Each dict contains: cell_type_id, standardized_name, cell_ontology_id,
        aliases.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT cell_type_id, standardized_name, cell_ontology_id, aliases
            FROM   cell_types
            ORDER  BY standardized_name
            """
        )
        return cur.fetchall()


def fetch_markers(
    organism_id: Optional[int] = None,
    cell_type_id: Optional[int] = None,
    tissue_filter: Optional[str] = None,
) -> List[Dict]:
    """
    Query the ``markers`` table with optional filters.

    Parameters
    ----------
    organism_id : int, optional
        Restrict results to markers for this organism.
    cell_type_id : int, optional
        Restrict results to markers for this cell type.
    tissue_filter : str, optional
        Case-insensitive substring to match against the ``tissue`` column.

    Returns
    -------
    list of dict
        Joined result including organism common name and cell type standardized
        name for display convenience.
    """
    conditions: List[str] = []
    params: List[Any] = []

    if organism_id is not None:
        conditions.append("m.organism_id = %s")
        params.append(organism_id)

    if cell_type_id is not None:
        conditions.append("m.cell_type_id = %s")
        params.append(cell_type_id)

    if tissue_filter:
        conditions.append("m.tissue ILIKE %s")
        params.append(f"%{tissue_filter}%")

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    sql = f"""
        SELECT
            m.marker_id,
            o.common_name        AS organism,
            o.nomenclature_authority,
            ct.standardized_name AS cell_type,
            ct.cell_ontology_id,
            m.gene_symbol,
            m.gene_id,
            m.tissue,
            m.platform,
            m.submission_source,
            m.submitter_email,
            m.date_submitted
        FROM   markers       m
        JOIN   organisms     o  ON o.organism_id   = m.organism_id
        JOIN   cell_types    ct ON ct.cell_type_id = m.cell_type_id
        {where_clause}
        ORDER  BY m.date_submitted DESC, m.marker_id DESC
    """

    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


# ===========================================================================
# Write helpers
# ===========================================================================

def insert_marker(
    organism_id: int,
    cell_type_id: int,
    gene_symbol: str,
    gene_id: str,
    tissue: Optional[str],
    platform: Optional[str],
    submission_source: Optional[str],
    submitter_email: str,
) -> int:
    """
    Insert a new validated marker record and return its ``marker_id``.

    Parameters
    ----------
    organism_id       : int   — FK to organisms.organism_id
    cell_type_id      : int   — FK to cell_types.cell_type_id
    gene_symbol       : str   — Already-normalised gene symbol
    gene_id           : str   — NCBI Gene ID or Ensembl Gene ID
    tissue            : str or None — Tissue / UBERON term
    platform          : str or None — Sequencing platform
    submission_source : str or None — PMID, DOI, or internal dataset ID
    submitter_email   : str   — Researcher email

    Returns
    -------
    int
        The newly created ``marker_id``.

    Raises
    ------
    psycopg2.IntegrityError
        If a duplicate (organism, cell_type, gene_symbol, tissue, platform)
        combination already exists in the table.
    """
    sql = """
        INSERT INTO markers
            (organism_id, cell_type_id, gene_symbol, gene_id,
             tissue, platform, submission_source, submitter_email)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING marker_id
    """
    with get_cursor() as cur:
        cur.execute(
            sql,
            (
                organism_id,
                cell_type_id,
                gene_symbol,
                gene_id,
                tissue or None,
                platform or None,
                submission_source or None,
                submitter_email,
            ),
        )
        row = cur.fetchone()
        return row["marker_id"]


def insert_cell_type(
    standardized_name: str,
    cell_ontology_id: Optional[str],
    aliases: Optional[str],
) -> int:
    """
    Insert a new cell type record and return its ``cell_type_id``.

    Parameters
    ----------
    standardized_name : str        — Canonical cell type name
    cell_ontology_id  : str or None — CL:XXXXXXX accession (optional)
    aliases           : str or None — Comma-separated synonyms (optional)

    Returns
    -------
    int
        The newly created ``cell_type_id``.
    """
    sql = """
        INSERT INTO cell_types (standardized_name, cell_ontology_id, aliases)
        VALUES (%s, %s, %s)
        RETURNING cell_type_id
    """
    with get_cursor() as cur:
        cur.execute(
            sql,
            (
                standardized_name.strip(),
                cell_ontology_id.strip() if cell_ontology_id else None,
                aliases.strip() if aliases else None,
            ),
        )
        row = cur.fetchone()
        return row["cell_type_id"]


# ===========================================================================
# Utility
# ===========================================================================

def test_connection() -> bool:
    """
    Attempt a lightweight query to verify that the database is reachable.

    Returns
    -------
    bool
        True if the connection succeeds, False otherwise.
    """
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1")
        return True
    except OperationalError as exc:
        logger.error("Database connection test failed: %s", exc)
        return False
