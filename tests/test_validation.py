"""
tests/test_validation.py
========================
Unit tests for the validation.py module.

These tests exercise:
  - Gene symbol normalisation (HGNC uppercase / MGI title-case / other)
  - Gene ID format validation (NCBI and Ensembl patterns)
  - The full validate_marker_submission pipeline (offline / skip_remote=True)

No network access or database connection is required.
Run with:
    pytest tests/test_validation.py -v
"""

import pytest
import sys
import os

# Ensure the project root is on the path regardless of how pytest is invoked.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validation import (
    normalize_gene_symbol,
    validate_gene_id_format,
    validate_marker_submission,
)


# ===========================================================================
# normalize_gene_symbol
# ===========================================================================

class TestNormalizeGeneSymbol:
    """Tests for gene symbol normalisation rules."""

    # ---- HGNC (human) — all uppercase ----------------------------------------

    def test_hgnc_lowercase_to_upper(self):
        assert normalize_gene_symbol("cd3e", "HGNC") == "CD3E"

    def test_hgnc_already_upper(self):
        assert normalize_gene_symbol("TP53", "HGNC") == "TP53"

    def test_hgnc_mixed_case(self):
        assert normalize_gene_symbol("Cd3E", "HGNC") == "CD3E"

    def test_hgnc_strips_whitespace(self):
        assert normalize_gene_symbol("  GAPDH  ", "HGNC") == "GAPDH"

    def test_hgnc_hyphenated_symbol(self):
        # Hyphenated human gene symbols should remain uppercased
        assert normalize_gene_symbol("hla-a", "HGNC") == "HLA-A"

    # ---- MGI (mouse) — first letter upper, rest lower ------------------------

    def test_mgi_all_lower_to_titlecase(self):
        assert normalize_gene_symbol("cd3e", "MGI") == "Cd3e"

    def test_mgi_all_upper_to_titlecase(self):
        assert normalize_gene_symbol("CD3E", "MGI") == "Cd3e"

    def test_mgi_already_correct(self):
        assert normalize_gene_symbol("Trp53", "MGI") == "Trp53"

    def test_mgi_strips_whitespace(self):
        assert normalize_gene_symbol("  Gapdh  ", "MGI") == "Gapdh"

    def test_mgi_single_char(self):
        assert normalize_gene_symbol("a", "MGI") == "A"

    # ---- Other authorities — return as-is (stripped) -------------------------

    def test_zfin_unchanged(self):
        assert normalize_gene_symbol("tp53", "ZFIN") == "tp53"

    def test_rgd_unchanged(self):
        assert normalize_gene_symbol("Tp53", "RGD") == "Tp53"

    def test_unknown_authority_unchanged(self):
        assert normalize_gene_symbol("BRCA1", "UNKNOWN") == "BRCA1"

    # ---- Error cases ---------------------------------------------------------

    def test_empty_symbol_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            normalize_gene_symbol("", "HGNC")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            normalize_gene_symbol("   ", "MGI")


# ===========================================================================
# validate_gene_id_format
# ===========================================================================

class TestValidateGeneIdFormat:
    """Tests for stable gene identifier format validation."""

    # ---- Valid NCBI Gene IDs (pure digits) -----------------------------------

    def test_ncbi_single_digit(self):
        assert validate_gene_id_format("1") is True

    def test_ncbi_typical_id(self):
        assert validate_gene_id_format("916") is True      # human CD3E

    def test_ncbi_long_id(self):
        assert validate_gene_id_format("100008586") is True

    # ---- Valid Ensembl Gene IDs ----------------------------------------------

    def test_ensembl_human(self):
        # Human ENSG format (15 chars after ENS)
        assert validate_gene_id_format("ENSG00000198851") is True

    def test_ensembl_mouse(self):
        assert validate_gene_id_format("ENSMUSG00000000001") is True

    def test_ensembl_zebrafish(self):
        assert validate_gene_id_format("ENSDARG00000000001") is True

    def test_ensembl_fly(self):
        assert validate_gene_id_format("ENSFLYG00000000001") is True

    def test_ensembl_min_species_code_empty(self):
        # ENS + G + 11 digits (no species code) is valid per regex
        assert validate_gene_id_format("ENSG00000000000") is True

    # ---- Invalid inputs ------------------------------------------------------

    def test_empty_string(self):
        assert validate_gene_id_format("") is False

    def test_alpha_only(self):
        assert validate_gene_id_format("ABCDE") is False

    def test_ensembl_wrong_digit_count(self):
        # Only 10 digits — should fail
        assert validate_gene_id_format("ENSG0000019885") is False

    def test_ensembl_lowercase(self):
        # Lowercase 'ensg' — should fail (our regex is case-sensitive)
        assert validate_gene_id_format("ensg00000198851") is False

    def test_ensembl_with_version(self):
        # Versioned IDs (ENSG00000198851.2) are NOT accepted
        assert validate_gene_id_format("ENSG00000198851.2") is False

    def test_float_string(self):
        assert validate_gene_id_format("9.16") is False

    def test_whitespace_leading(self):
        # validate_gene_id_format strips leading/trailing whitespace, so
        # " 916" is treated as "916" and considered valid.
        assert validate_gene_id_format(" 916") is True

    def test_whitespace_trailing(self):
        assert validate_gene_id_format("916 ") is True

    def test_whitespace_both_sides(self):
        assert validate_gene_id_format("  916  ") is True


# ===========================================================================
# validate_marker_submission (offline / skip_remote=True)
# ===========================================================================

class TestValidateMarkerSubmission:
    """Integration tests for the full validation pipeline (no network calls)."""

    # ---- Happy paths ---------------------------------------------------------

    def test_human_valid(self):
        normalised, ok, msg = validate_marker_submission(
            gene_symbol="cd3e",
            gene_id="916",
            nomenclature_authority="HGNC",
            skip_remote=True,
        )
        assert ok is True
        assert normalised == "CD3E"
        assert "CD3E" in msg

    def test_mouse_valid_ncbi(self):
        normalised, ok, msg = validate_marker_submission(
            gene_symbol="CD3E",
            gene_id="12501",
            nomenclature_authority="MGI",
            skip_remote=True,
        )
        assert ok is True
        assert normalised == "Cd3e"

    def test_human_ensembl_id(self):
        normalised, ok, msg = validate_marker_submission(
            gene_symbol="TP53",
            gene_id="ENSG00000141510",
            nomenclature_authority="HGNC",
            skip_remote=True,
        )
        assert ok is True
        assert normalised == "TP53"

    def test_mouse_ensembl_id(self):
        normalised, ok, msg = validate_marker_submission(
            gene_symbol="Trp53",
            gene_id="ENSMUSG00000059552",
            nomenclature_authority="MGI",
            skip_remote=True,
        )
        assert ok is True
        assert normalised == "Trp53"

    def test_unknown_authority_valid(self):
        normalised, ok, msg = validate_marker_submission(
            gene_symbol="tp53",
            gene_id="30590",
            nomenclature_authority="ZFIN",
            skip_remote=True,
        )
        assert ok is True
        assert normalised == "tp53"   # unchanged for non-HGNC/MGI

    # ---- Failure cases -------------------------------------------------------

    def test_empty_symbol_fails(self):
        normalised, ok, msg = validate_marker_submission(
            gene_symbol="",
            gene_id="916",
            nomenclature_authority="HGNC",
            skip_remote=True,
        )
        assert ok is False
        assert normalised == ""

    def test_invalid_gene_id_alpha(self):
        normalised, ok, msg = validate_marker_submission(
            gene_symbol="CD3E",
            gene_id="NOT_AN_ID",
            nomenclature_authority="HGNC",
            skip_remote=True,
        )
        assert ok is False
        assert "NOT_AN_ID" in msg

    def test_invalid_gene_id_empty(self):
        normalised, ok, msg = validate_marker_submission(
            gene_symbol="CD3E",
            gene_id="",
            nomenclature_authority="HGNC",
            skip_remote=True,
        )
        assert ok is False

    def test_ensembl_wrong_digit_count_fails(self):
        normalised, ok, msg = validate_marker_submission(
            gene_symbol="TP53",
            gene_id="ENSG0000014151",   # 10 digits — too short
            nomenclature_authority="HGNC",
            skip_remote=True,
        )
        assert ok is False

    # ---- Normalisation side-effects visible in message ----------------------

    def test_message_contains_normalised_symbol(self):
        _, _, msg = validate_marker_submission(
            gene_symbol="brca1",
            gene_id="672",
            nomenclature_authority="HGNC",
            skip_remote=True,
        )
        assert "BRCA1" in msg

    def test_message_contains_authority(self):
        _, _, msg = validate_marker_submission(
            gene_symbol="brca1",
            gene_id="672",
            nomenclature_authority="HGNC",
            skip_remote=True,
        )
        assert "HGNC" in msg
