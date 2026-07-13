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


# ===========================================================================
# Connection test
# ===========================================================================

def test_connection() -> bool:
    """Return True if the database is reachable, False otherwise."""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1")
        return True
    except Exception as exc:
        logger.warning("Database connection test failed: %s", exc)
        return False


# ===========================================================================
# Read helpers
# ===========================================================================

def fetch_all_organisms() -> List[Dict]:
    """Return all organisms ordered by common name."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT organism_id, common_name, scientific_name,
                   ncbi_taxon_id, nomenclature_authority
            FROM organisms
            ORDER BY common_name
            """
        )
        return [dict(row) for row in cur.fetchall()]


def fetch_all_cell_types() -> List[Dict]:
    """Return all cell types ordered by standardized name."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT cell_type_id, standardized_name, cell_ontology_id, aliases
            FROM cell_types
            ORDER BY standardized_name
            """
        )
        return [dict(row) for row in cur.fetchall()]


def fetch_cell_types_with_markers() -> List[Dict]:
    """Return only cell types that have at least one marker entry."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT ct.cell_type_id, ct.standardized_name, ct.cell_ontology_id
            FROM cell_types ct
            JOIN markers m ON m.cell_type_id = ct.cell_type_id
            ORDER BY ct.standardized_name
            """
        )
        return [dict(row) for row in cur.fetchall()]


def fetch_markers(
    organism_id: Optional[int] = None,
    cell_type_id: Optional[int] = None,
    tissue_filter: Optional[str] = None,
) -> List[Dict]:
    """
    Return marker rows joined with organism and cell-type metadata.

    All parameters are optional filters; omitting them returns all rows.
    Column names match the rename map used in app.py.
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

    query = f"""
        SELECT
            m.marker_id,
            o.common_name            AS organism,
            o.nomenclature_authority,
            ct.standardized_name     AS cell_type,
            ct.cell_ontology_id,
            m.gene_symbol,
            m.gene_id,
            m.tissue,
            m.platform,
            m.submission_source,
            m.submitter_email,
            m.lab_affiliation,
            m.date_submitted
        FROM markers m
        JOIN organisms  o  ON o.organism_id  = m.organism_id
        JOIN cell_types ct ON ct.cell_type_id = m.cell_type_id
        {where_clause}
        ORDER BY m.marker_id
    """
    with get_cursor() as cur:
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def fetch_database_stats() -> Dict[str, List[Dict]]:
    """
    Return summary counts used by the Database Summary page.

    Returns a dict with three keys:
      - by_organism  : [{organism, count}, …]
      - by_cell_type : [{cell_type, count}, …]
      - by_tissue    : [{tissue, count}, …]
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT o.common_name AS organism, COUNT(*) AS count
            FROM markers m
            JOIN organisms o ON o.organism_id = m.organism_id
            GROUP BY o.common_name
            ORDER BY count DESC
            """
        )
        by_organism = [dict(row) for row in cur.fetchall()]

        cur.execute(
            """
            SELECT ct.standardized_name AS cell_type, COUNT(*) AS count
            FROM markers m
            JOIN cell_types ct ON ct.cell_type_id = m.cell_type_id
            GROUP BY ct.standardized_name
            ORDER BY count DESC
            """
        )
        by_cell_type = [dict(row) for row in cur.fetchall()]

        cur.execute(
            """
            SELECT COALESCE(tissue, 'Unknown') AS tissue, COUNT(*) AS count
            FROM markers
            GROUP BY tissue
            ORDER BY count DESC
            """
        )
        by_tissue = [dict(row) for row in cur.fetchall()]

    return {
        "by_organism": by_organism,
        "by_cell_type": by_cell_type,
        "by_tissue": by_tissue,
    }


# ===========================================================================
# Write helpers
# ===========================================================================

def insert_cell_type(
    standardized_name: str,
    cell_ontology_id: Optional[str] = None,
    aliases: Optional[str] = None,
) -> int:
    """Insert a new cell type and return its cell_type_id."""
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO cell_types (standardized_name, cell_ontology_id, aliases)
            VALUES (%s, %s, %s)
            RETURNING cell_type_id
            """,
            (standardized_name, cell_ontology_id, aliases),
        )
        row = cur.fetchone()
        return row["cell_type_id"]


def insert_marker(
    organism_id: int,
    cell_type_id: int,
    gene_symbol: str,
    gene_id: str,
    tissue: Optional[str] = None,
    platform: Optional[str] = None,
    submission_source: Optional[str] = None,
    submitter_email: str = "",
    lab_affiliation: Optional[str] = None,
) -> int:
    """Insert a new marker record and return its marker_id."""
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO markers
                (organism_id, cell_type_id, gene_symbol, gene_id,
                 tissue, platform, submission_source, submitter_email, lab_affiliation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING marker_id
            """,
            (
                organism_id, cell_type_id, gene_symbol, gene_id,
                tissue, platform, submission_source, submitter_email, lab_affiliation,
            ),
        )
        row = cur.fetchone()
        return row["marker_id"]
