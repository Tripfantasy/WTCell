"""
tests/test_agent.py
===================
Unit tests for the agent.py module.

These tests cover:
  - compute_similarity_score (pure logic, no network or LLM calls)
  - _normalize helper
  - _score_label helper
  - run_literature_check error path when OpenAI key is absent

No network access, OpenAI API key, or database connection is required.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import (
    LiteratureResult,
    compute_similarity_score,
    _score_label,
    _normalize,
)


# ===========================================================================
# _normalize
# ===========================================================================

class TestNormalize:
    def test_lowercases(self):
        assert _normalize("T Cell") == "t cell"

    def test_strips_whitespace(self):
        assert _normalize("  macrophage  ") == "macrophage"

    def test_collapses_internal_spaces(self):
        assert _normalize("natural  killer  cell") == "natural killer cell"

    def test_empty_string(self):
        assert _normalize("") == ""


# ===========================================================================
# compute_similarity_score
# ===========================================================================

class TestComputeSimilarityScore:
    """Tests for the post-hoc similarity scoring (no LLM calls)."""

    # --- Perfect matches -------------------------------------------------------

    def test_exact_match_returns_agent_confidence(self):
        result = LiteratureResult(cell_types=["T cell"], confidence=0.9)
        score = compute_similarity_score(result, "T cell")
        assert score == pytest.approx(0.9, abs=0.001)

    def test_exact_match_case_insensitive(self):
        result = LiteratureResult(cell_types=["t cell"], confidence=1.0)
        score = compute_similarity_score(result, "T cell")
        assert score == pytest.approx(1.0, abs=0.001)

    def test_exact_match_via_alias(self):
        result = LiteratureResult(cell_types=["T lymphocyte"], confidence=1.0)
        score = compute_similarity_score(result, "T cell", "T lymphocyte,CD3+ cell")
        assert score == pytest.approx(1.0, abs=0.001)

    # --- Substring matches -------------------------------------------------------

    def test_substring_match_lit_contains_db(self):
        # "CD4+ T cell" contains "T cell"
        result = LiteratureResult(cell_types=["CD4+ T cell"], confidence=1.0)
        score = compute_similarity_score(result, "T cell")
        assert score >= 0.80

    def test_substring_match_db_contains_lit(self):
        # "T cell" is inside "cytotoxic T cell" conceptually, but
        # here we test the literal containment direction.
        result = LiteratureResult(cell_types=["T cell"], confidence=1.0)
        score = compute_similarity_score(result, "CD8+ T cell")
        assert score >= 0.80

    # --- Fuzzy matches -----------------------------------------------------------

    def test_fuzzy_match_similar_names(self):
        # "Macrophage" vs "macrophages" — should fuzzy-match
        result = LiteratureResult(cell_types=["Macrophages"], confidence=0.8)
        score = compute_similarity_score(result, "Macrophage")
        assert score > 0.5

    # --- No match ----------------------------------------------------------------

    def test_no_match_returns_zero(self):
        result = LiteratureResult(cell_types=["Hepatocyte", "Neuron"], confidence=1.0)
        score = compute_similarity_score(result, "T cell")
        assert score == 0.0

    def test_empty_cell_types_returns_zero(self):
        result = LiteratureResult(cell_types=[], confidence=0.9)
        score = compute_similarity_score(result, "T cell")
        assert score == 0.0

    # --- Confidence scaling ------------------------------------------------------

    def test_low_confidence_scales_score_down(self):
        high = compute_similarity_score(
            LiteratureResult(cell_types=["T cell"], confidence=1.0), "T cell"
        )
        low = compute_similarity_score(
            LiteratureResult(cell_types=["T cell"], confidence=0.4), "T cell"
        )
        assert low < high
        assert low == pytest.approx(0.4, abs=0.001)

    def test_zero_confidence_returns_zero(self):
        result = LiteratureResult(cell_types=["T cell"], confidence=0.0)
        score = compute_similarity_score(result, "T cell")
        assert score == 0.0

    # --- Multiple literature cell types ------------------------------------------

    def test_best_of_multiple_cell_types(self):
        # One exact match among several — should pick the best.
        result = LiteratureResult(
            cell_types=["Hepatocyte", "T cell", "Fibroblast"],
            confidence=0.8,
        )
        score = compute_similarity_score(result, "T cell")
        assert score == pytest.approx(0.8, abs=0.001)

    # --- Score is clamped to [0, 1] ------------------------------------------------

    def test_score_does_not_exceed_one(self):
        result = LiteratureResult(cell_types=["T cell"], confidence=1.0)
        score = compute_similarity_score(result, "T cell")
        assert 0.0 <= score <= 1.0

    def test_score_rounded_to_three_decimals(self):
        result = LiteratureResult(cell_types=["T cell"], confidence=0.777)
        score = compute_similarity_score(result, "T cell")
        # Result should have at most 3 decimal places.
        assert score == round(score, 3)


# ===========================================================================
# _score_label
# ===========================================================================

class TestScoreLabel:
    def test_strong(self):
        assert "Strong" in _score_label(0.9)
        assert "🟢" in _score_label(0.9)

    def test_moderate(self):
        assert "Moderate" in _score_label(0.6)
        assert "🟡" in _score_label(0.6)

    def test_weak(self):
        assert "Weak" in _score_label(0.3)
        assert "🟠" in _score_label(0.3)

    def test_poor(self):
        assert "Little or no" in _score_label(0.1)
        assert "🔴" in _score_label(0.1)

    def test_zero(self):
        assert "🔴" in _score_label(0.0)

    def test_boundary_at_0_8(self):
        # Exactly 0.8 should be "Strong"
        assert "Strong" in _score_label(0.8)

    def test_boundary_below_0_8(self):
        # Just below 0.8 should be "Moderate"
        assert "Moderate" in _score_label(0.799)


# ===========================================================================
# run_literature_check — error path (no API key)
# ===========================================================================

class TestRunLiteratureCheckErrors:
    def test_raises_runtime_error_without_api_key(self, monkeypatch):
        """run_literature_check must raise RuntimeError when OPENAI_API_KEY absent."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        from agent import run_literature_check
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            run_literature_check(
                marker_id=1,
                gene_symbol="CD3E",
                organism_name="Human",
                cell_type="T cell",
            )
