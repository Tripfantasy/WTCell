"""
validation.py
=============
Gene symbol and gene ID validation logic for WTCell.

Validation rules by organism (driven by nomenclature_authority field):

  HGNC  (Human / Homo sapiens):
    - Symbol must be converted to ALL UPPERCASE before storage.
    - Optionally verified against the live HGNC REST API.

  MGI   (Mouse / Mus musculus):
    - Symbol must follow standard mouse capitalization:
      first letter uppercase, remaining letters lowercase
      (e.g. "Cd3e", not "CD3E" or "cd3e").
    - Optionally verified against the MyGene.info API (mouse taxon 10090).

  Other authorities:
    - Only format normalisation is applied; no remote API call is made.

Gene ID validation (applied to all organisms):
  - NCBI Gene ID  : string of one or more digits only  (e.g. "916")
  - Ensembl Gene ID: ENSG / ENSMUSG / ENS<species>G + 11 digits
                     (e.g. "ENSG00000198851", "ENSMUSG00000000001")
  - Exactly one valid ID form is required.
"""

import os
import re
import logging
from typing import Optional, Tuple

import requests

# ---------------------------------------------------------------------------
# Module-level logger
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# HGNC REST API — fetch approved symbol
HGNC_API_URL = "https://rest.genenames.org/fetch/symbol/{symbol}"
HGNC_HEADERS = {"Accept": "application/json"}

# MyGene.info API — supports both human and mouse lookups
MYGENE_API_URL = "https://mygene.info/v3/query"

# Timeout for external API calls (seconds).
# 8 s balances responsiveness against slow remote APIs while leaving enough
# headroom for legitimate round-trips to genenames.org / mygene.info.
# Override via the API_TIMEOUT_SECONDS environment variable if needed.
API_TIMEOUT = int(os.getenv("API_TIMEOUT_SECONDS", "8"))

# ---------------------------------------------------------------------------
# Shared constants — also imported by app.py for consistent validation
# ---------------------------------------------------------------------------

# Email validation: explicit character-class pattern that avoids catastrophic
# backtracking (ReDoS).  Checks for a non-empty local part, exactly one '@',
# a domain with at least one label, and a dot separator.
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

# Pre-compiled regex patterns for gene ID formats
_RE_NCBI_GENE_ID    = re.compile(r"^\d+$")
_RE_ENSEMBL_GENE_ID = re.compile(r"^ENS[A-Z]*G\d{11}$")


# ===========================================================================
# Gene symbol normalisation
# ===========================================================================

def normalize_gene_symbol(symbol: str, nomenclature_authority: str) -> str:
    """
    Normalise a gene symbol string according to the organism's nomenclature
    authority rules.

    Parameters
    ----------
    symbol : str
        Raw gene symbol as entered by the user.
    nomenclature_authority : str
        The authority string stored in ``organisms.nomenclature_authority``
        (e.g. 'HGNC', 'MGI', 'ZFIN').

    Returns
    -------
    str
        The normalised symbol ready for database storage.

    Raises
    ------
    ValueError
        If the symbol is empty after stripping whitespace.
    """
    symbol = symbol.strip()
    if not symbol:
        raise ValueError("Gene symbol must not be empty.")

    authority = nomenclature_authority.upper()

    if authority == "HGNC":
        # HGNC rule: gene symbols are ALL UPPERCASE (e.g. "CD3E", "TP53").
        return symbol.upper()

    if authority == "MGI":
        # MGI rule: first letter uppercase, rest lowercase (e.g. "Cd3e", "Trp53").
        # This handles multi-word / hyphenated symbols gracefully by lowercasing
        # the whole string first, then capitalising the very first character.
        normalised = symbol.lower()
        # Guard: after lowercasing the symbol is guaranteed non-empty (whitespace
        # was already stripped and emptiness was checked above), but be explicit.
        if not normalised:
            raise ValueError("Gene symbol must not be empty.")
        return normalised[0].upper() + normalised[1:]

    # For all other authorities (ZFIN, RGD, FlyBase, WormBase …) we return the
    # symbol trimmed of whitespace but otherwise unchanged, deferring to whatever
    # case the submitter used.
    return symbol


# ===========================================================================
# Gene ID format validation
# ===========================================================================

def validate_gene_id_format(gene_id: str) -> bool:
    """
    Check whether *gene_id* matches a known stable identifier format.

    Accepted formats
    ----------------
    * NCBI Gene ID  — one or more digits, e.g. "916"
    * Ensembl Gene ID — ``ENS[optional species code]G`` followed by 11 digits,
      e.g. "ENSG00000198851" (human), "ENSMUSG00000000001" (mouse),
      "ENSDARG00000000001" (zebrafish).

    Returns
    -------
    bool
        True if the format is valid, False otherwise.
    """
    gid = gene_id.strip()
    return bool(_RE_NCBI_GENE_ID.match(gid) or _RE_ENSEMBL_GENE_ID.match(gid))


# ===========================================================================
# Remote API validation — HGNC
# ===========================================================================

def validate_symbol_hgnc(symbol: str) -> Tuple[bool, str]:
    """
    Query the HGNC REST API to confirm the symbol is an *approved* HGNC symbol.

    The symbol passed in should already be normalised (uppercase) by
    :func:`normalize_gene_symbol`.

    Parameters
    ----------
    symbol : str
        Uppercase gene symbol.

    Returns
    -------
    (is_valid, message) : Tuple[bool, str]
        *is_valid* — True if the symbol is found as an approved HGNC entry.
        *message*  — Human-readable status / error text.
    """
    url = HGNC_API_URL.format(symbol=symbol)
    try:
        resp = requests.get(url, headers=HGNC_HEADERS, timeout=API_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # HGNC response structure: {"response": {"numFound": N, "docs": [...]}}
        num_found = data.get("response", {}).get("numFound", 0)
        if num_found > 0:
            # Confirm the returned document carries 'status': 'Approved'
            docs = data["response"]["docs"]
            approved = any(d.get("status") == "Approved" for d in docs)
            if approved:
                return True, f"'{symbol}' is an approved HGNC symbol."
            else:
                return False, (
                    f"'{symbol}' was found in HGNC but is not approved "
                    f"(it may be deprecated or an alias)."
                )
        else:
            return False, f"'{symbol}' was not found in the HGNC database."
    except requests.exceptions.Timeout:
        logger.warning("HGNC API timed out for symbol '%s'.", symbol)
        return True, (
            "HGNC API timed out — symbol format accepted but could not be "
            "verified online. Proceeding with caution."
        )
    except requests.exceptions.RequestException as exc:
        logger.warning("HGNC API error for symbol '%s': %s", symbol, exc)
        return True, (
            f"HGNC API unreachable ({exc}) — symbol format accepted but not "
            "verified online. Proceeding with caution."
        )


# ===========================================================================
# Remote API validation — MGI (via MyGene.info)
# ===========================================================================

def validate_symbol_mgi(symbol: str) -> Tuple[bool, str]:
    """
    Query the MyGene.info API to confirm the symbol exists in the mouse
    (taxon 10090) gene database, which mirrors MGI annotations.

    The symbol passed in should already be normalised (title-case) by
    :func:`normalize_gene_symbol`.

    Parameters
    ----------
    symbol : str
        Title-case mouse gene symbol (e.g. "Cd3e").

    Returns
    -------
    (is_valid, message) : Tuple[bool, str]
        *is_valid* — True if the symbol matches a mouse gene record.
        *message*  — Human-readable status / error text.
    """
    params = {
        "q":       f"symbol:{symbol}",
        "species": "mouse",
        "fields":  "symbol,name,taxid",
        "size":    5,
    }
    try:
        resp = requests.get(MYGENE_API_URL, params=params, timeout=API_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("hits", [])
        # Filter hits to exact symbol match (case-insensitive) and correct taxon
        matches = [
            h for h in hits
            if h.get("symbol", "").lower() == symbol.lower()
            and h.get("taxid") == 10090
        ]
        if matches:
            return True, f"'{symbol}' is a recognised MGI/mouse gene symbol."
        else:
            return False, (
                f"'{symbol}' was not found as a mouse gene symbol in "
                "MyGene.info / MGI."
            )
    except requests.exceptions.Timeout:
        logger.warning("MyGene.info API timed out for symbol '%s'.", symbol)
        return True, (
            "MyGene.info API timed out — symbol format accepted but could "
            "not be verified online. Proceeding with caution."
        )
    except requests.exceptions.RequestException as exc:
        logger.warning("MyGene.info API error for symbol '%s': %s", symbol, exc)
        return True, (
            f"MyGene.info API unreachable ({exc}) — symbol format accepted "
            "but not verified online. Proceeding with caution."
        )


# ===========================================================================
# Unified validation entry point
# ===========================================================================

def validate_marker_submission(
    gene_symbol: str,
    gene_id: str,
    nomenclature_authority: str,
    skip_remote: bool = False,
) -> Tuple[str, bool, str]:
    """
    Full validation pipeline for a marker submission.

    Steps
    -----
    1. Normalise the gene symbol according to the organism's authority rules.
    2. Validate the gene ID format (NCBI or Ensembl).
    3. Optionally query the relevant remote API to confirm the symbol exists.

    Parameters
    ----------
    gene_symbol : str
        Raw symbol as entered by the user.
    gene_id : str
        Stable gene identifier (NCBI Gene ID or Ensembl Gene ID).
    nomenclature_authority : str
        Value from ``organisms.nomenclature_authority`` (e.g. 'HGNC', 'MGI').
    skip_remote : bool
        If True, skip the remote API verification step.  Useful during bulk
        imports or when running tests without network access.

    Returns
    -------
    (normalised_symbol, is_valid, message) : Tuple[str, bool, str]
        *normalised_symbol* — The normalised symbol (empty string on failure).
        *is_valid*          — Overall pass/fail flag.
        *message*           — Human-readable summary of all checks.
    """
    messages = []

    # --- Step 1: Normalise symbol -------------------------------------------
    try:
        normalised = normalize_gene_symbol(gene_symbol, nomenclature_authority)
        messages.append(
            f"✔ Symbol normalised to '{normalised}' "
            f"({nomenclature_authority} rules)."
        )
    except ValueError as exc:
        return "", False, f"✘ Symbol normalisation failed: {exc}"

    # --- Step 2: Validate gene ID format ------------------------------------
    if not validate_gene_id_format(gene_id):
        return (
            normalised,
            False,
            (
                f"✘ Gene ID '{gene_id}' is not a valid NCBI Gene ID (digits only) "
                "or Ensembl Gene ID (ENS[species]G + 11 digits).  "
                "A stable gene ID is required."
            ),
        )
    messages.append(f"✔ Gene ID '{gene_id}' has a valid format.")

    # --- Step 3: Remote API verification (optional) -------------------------
    if not skip_remote:
        authority = nomenclature_authority.upper()
        if authority == "HGNC":
            remote_ok, remote_msg = validate_symbol_hgnc(normalised)
        elif authority == "MGI":
            remote_ok, remote_msg = validate_symbol_mgi(normalised)
        else:
            # No remote verification available for this authority.
            remote_ok = True
            remote_msg = (
                f"Remote validation is not configured for authority "
                f"'{nomenclature_authority}'.  Symbol format accepted."
            )

        status_char = "✔" if remote_ok else "✘"
        messages.append(f"{status_char} Remote check: {remote_msg}")

        if not remote_ok:
            return normalised, False, "\n".join(messages)

    return normalised, True, "\n".join(messages)
