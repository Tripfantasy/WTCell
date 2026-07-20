"""
agent.py
========
Agentic literature confidence scoring for WTCell marker genes.

Architecture
------------
The agent queries a large language model (LLM) using **only** the gene symbol
and organism name — never the database cell-type annotation, tissue, or any
other stored metadata.  This is the critical design constraint: passing
metadata to the LLM would prime it to validate the existing annotation,
introducing confirmation bias and inflating scores.

Once the LLM returns the cell types it associates with the gene from published
literature, a separate similarity function compares those results against the
database annotation.  The final score therefore measures how well the database
entry is supported by independent literature evidence.

Environment variables
---------------------
OPENAI_API_KEY   — required; your OpenAI API key.
OPENAI_MODEL     — optional; model name (default: gpt-4o-mini).
API_TIMEOUT_SECONDS — optional; request timeout in seconds (default: 30).

Usage example
-------------
>>> from agent import run_literature_check
>>> score, summary = run_literature_check(
...     marker_id=1,
...     gene_symbol="CD3E",
...     organism_name="Human",
...     cell_type="T cell",
...     cell_type_aliases="T lymphocyte,T-cell,CD3+ cell",
... )
"""

import difflib
import json
import logging
import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_DEFAULT_MODEL = "gpt-4o-mini"
_AGENT_TIMEOUT = int(os.getenv("API_TIMEOUT_SECONDS", "30"))


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class LiteratureResult:
    """Structured output from a single literature search call."""

    # Cell types this gene is known to mark, per the LLM's literature knowledge.
    cell_types: List[str] = field(default_factory=list)

    # The LLM's self-reported confidence that the gene is a validated marker
    # (0.0 = no evidence, 1.0 = widely validated in multiple studies).
    confidence: float = 0.0

    # Human-readable summary of the evidence cited by the LLM.
    summary: str = ""

    # Raw JSON string returned by the model (stored for auditability).
    raw_response: str = ""


# ---------------------------------------------------------------------------
# LLM prompt
# ---------------------------------------------------------------------------

# IMPORTANT: The prompt includes ONLY the gene symbol and organism name.
# Cell type, tissue, platform, and all other database metadata are deliberately
# excluded to prevent the LLM from rubber-stamping the existing annotation.
_LITERATURE_PROMPT = """\
You are an expert in single-cell RNA sequencing (scRNA-seq) and cell biology \
with deep knowledge of published scientific literature.

Your task: based solely on peer-reviewed scientific literature, determine \
what cell types the gene {gene_symbol} ({organism}) is an established marker for.

Rules:
- Cite only findings from published research; do not speculate.
- Be conservative: only include cell types supported by strong, reproducible evidence.
- If this gene is not widely recognised as a cell-type marker, say so honestly.

Return your response as a JSON object with exactly these three fields:
- "cell_types": a list of cell type names (use standard names such as \
"T cell", "B cell", "Macrophage", "Hepatocyte"); return an empty list if none.
- "confidence": a float 0.0–1.0 representing how well-established this gene is \
as a marker (1.0 = validated across multiple independent studies, \
0.0 = no credible literature evidence).
- "summary": a concise 2–3 sentence summary of the key evidence.
"""


# ---------------------------------------------------------------------------
# OpenAI client helper
# ---------------------------------------------------------------------------

def _get_openai_client():
    """
    Build and return an ``openai.OpenAI`` client.

    Raises
    ------
    RuntimeError
        If the ``openai`` package is not installed or ``OPENAI_API_KEY`` is
        not set in the environment.
    """
    try:
        from openai import OpenAI  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "The 'openai' package is required for literature checks.  "
            "Run: pip install openai"
        ) from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set.  "
            "Add it to your .env file or Streamlit secrets to enable "
            "literature confidence scoring."
        )

    return OpenAI(api_key=api_key)


def openai_available() -> bool:
    """Return True if the OpenAI client can be constructed (key present)."""
    try:
        _get_openai_client()
        return True
    except RuntimeError:
        return False


# ---------------------------------------------------------------------------
# Literature query
# ---------------------------------------------------------------------------

def query_gene_literature(
    gene_symbol: str,
    organism_name: str,
    model: Optional[str] = None,
) -> LiteratureResult:
    """
    Ask the LLM what cell types *gene_symbol* marks, based on literature.

    **No database metadata is included in the prompt.**  Only the gene symbol
    and organism name are sent to the model so that the result is independent
    of the existing database annotation.

    Parameters
    ----------
    gene_symbol : str
        The gene symbol to query (e.g. "CD3E").
    organism_name : str
        Human-readable species name (e.g. "Human", "Mouse").
    model : str, optional
        OpenAI model name.  Defaults to the ``OPENAI_MODEL`` env var or
        ``gpt-4o-mini``.

    Returns
    -------
    LiteratureResult
        Parsed and validated response from the model.

    Raises
    ------
    RuntimeError
        If the OpenAI client cannot be created (missing key / package).
    ValueError
        If the model returns a response that cannot be parsed as valid JSON.
    """
    if model is None:
        model = os.getenv("OPENAI_MODEL", _DEFAULT_MODEL)

    client = _get_openai_client()
    prompt = _LITERATURE_PROMPT.format(
        gene_symbol=gene_symbol.strip(),
        organism=organism_name.strip(),
    )

    logger.info(
        "Literature query: gene=%s organism=%s model=%s",
        gene_symbol,
        organism_name,
        model,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,        # low temperature → more deterministic, less confabulation
        response_format={"type": "json_object"},
        timeout=_AGENT_TIMEOUT,
    )

    raw = response.choices[0].message.content or ""

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Model returned non-JSON content for gene '{gene_symbol}': {raw!r}"
        ) from exc

    cell_types = data.get("cell_types", [])
    if not isinstance(cell_types, list):
        cell_types = []

    try:
        confidence = float(data.get("confidence", 0.0))
        confidence = max(0.0, min(1.0, confidence))   # clamp to [0, 1]
    except (TypeError, ValueError):
        confidence = 0.0

    return LiteratureResult(
        cell_types=[str(ct).strip() for ct in cell_types if str(ct).strip()],
        confidence=confidence,
        summary=str(data.get("summary", "")).strip(),
        raw_response=raw,
    )


# ---------------------------------------------------------------------------
# Similarity scoring
# ---------------------------------------------------------------------------

def _normalize(name: str) -> str:
    """Lowercase, strip, and collapse internal whitespace."""
    return " ".join(name.lower().split())


def compute_similarity_score(
    literature_result: LiteratureResult,
    db_cell_type: str,
    db_aliases: Optional[str] = None,
) -> float:
    """
    Compare literature agent results against the *database* annotation.

    This function is called **after** the agent has already returned its
    findings.  The cell-type annotation is therefore used only for scoring,
    never as part of the agent's input, preserving the bias-free design.

    The match quality is calculated as follows:
    - Exact match (after normalisation) → 1.0
    - Substring containment (one name inside the other) → 0.85
    - Fuzzy similarity ≥ 0.80 → scaled to [0.75, 0.85)
    - No match → 0.0

    The final score is ``match_quality × agent_confidence``, so an uncertain
    agent finding produces a proportionally lower score.

    Parameters
    ----------
    literature_result : LiteratureResult
        Output from :func:`query_gene_literature`.
    db_cell_type : str
        The cell type name stored in the database (the annotation to validate).
    db_aliases : str, optional
        Comma-separated synonyms for the cell type (e.g. "T-cell,CD3+ cell").

    Returns
    -------
    float
        Score in [0.0, 1.0], rounded to three decimal places.
        Returns 0.0 if the literature result contains no cell types.
    """
    if not literature_result.cell_types:
        return 0.0

    # Build the full set of acceptable names from the database annotation.
    db_names = {_normalize(db_cell_type)}
    if db_aliases:
        for alias in db_aliases.split(","):
            stripped = _normalize(alias)
            if stripped:
                db_names.add(stripped)

    best_match = 0.0

    for lit_ct in literature_result.cell_types:
        lit_norm = _normalize(lit_ct)
        for db_name in db_names:
            # Exact match
            if lit_norm == db_name:
                best_match = 1.0
                break
            # Substring containment (e.g. "CD4+ T cell" vs "T cell")
            if db_name in lit_norm or lit_norm in db_name:
                best_match = max(best_match, 0.85)
                continue
            # Fuzzy similarity
            ratio = difflib.SequenceMatcher(None, lit_norm, db_name).ratio()
            if ratio >= 0.80:
                # Scale fuzzy matches into (0.75, 0.85) to rank below substring
                scaled = 0.75 + (ratio - 0.80) * 0.5
                best_match = max(best_match, scaled)

        if best_match >= 1.0:
            break

    # Multiply by the agent's self-reported confidence.
    score = best_match * literature_result.confidence
    return round(score, 3)


# ---------------------------------------------------------------------------
# High-level entry point
# ---------------------------------------------------------------------------

def run_literature_check(
    marker_id: int,
    gene_symbol: str,
    organism_name: str,
    cell_type: str,
    cell_type_aliases: Optional[str] = None,
) -> Tuple[float, str]:
    """
    Run a complete literature confidence check for a single marker entry.

    The agent is queried with **only** the gene symbol and organism.  The
    cell_type and aliases are used exclusively in the post-hoc similarity
    computation, ensuring the LLM cannot validate the annotation by having
    seen it first.

    Parameters
    ----------
    marker_id : int
        Database marker ID — used for logging only.
    gene_symbol : str
        Gene symbol (e.g. "CD3E").  **This and organism_name are the only
        values sent to the LLM.**
    organism_name : str
        Human-readable organism name (e.g. "Human").
    cell_type : str
        The database cell-type annotation to validate (used after LLM call).
    cell_type_aliases : str, optional
        Comma-separated aliases for the cell type (used after LLM call).

    Returns
    -------
    (score, summary) : Tuple[float, str]
        *score*   — similarity score in [0.0, 1.0].
        *summary* — markdown-formatted narrative for display in the UI.

    Raises
    ------
    RuntimeError
        If the OpenAI client cannot be created.
    ValueError
        If the model response cannot be parsed.
    """
    logger.info(
        "Literature check: marker_id=%d gene=%s organism=%s",
        marker_id,
        gene_symbol,
        organism_name,
    )

    # --- Step 1: query LLM with gene + organism only (no metadata) ----------
    result = query_gene_literature(gene_symbol, organism_name)

    # --- Step 2: compare against database annotation (post-hoc) -------------
    score = compute_similarity_score(result, cell_type, cell_type_aliases)

    # --- Step 3: build human-readable summary --------------------------------
    if result.cell_types:
        lit_types_str = ", ".join(f"**{ct}**" for ct in result.cell_types)
    else:
        lit_types_str = "_None identified_"

    score_label = _score_label(score)

    summary = (
        f"### Literature Confidence Check: {gene_symbol} ({organism_name})\n\n"
        f"**Evidence summary:**  \n{result.summary}\n\n"
        f"**Cell types identified in literature** _(gene queried without database context)_:  \n"
        f"{lit_types_str}\n\n"
        f"**Agent literature confidence:** {result.confidence:.0%}\n\n"
        f"**Annotation match score:** {score:.0%} — {score_label}  \n"
        f"_(How well the literature-identified cell types overlap with the "
        f"database annotation, computed after the literature search)_"
    )

    logger.info(
        "Literature check complete: marker_id=%d score=%.3f",
        marker_id,
        score,
    )
    return score, summary


def _score_label(score: float) -> str:
    """Return a human-readable quality label for a score value."""
    if score >= 0.8:
        return "🟢 Strong literature support"
    if score >= 0.5:
        return "🟡 Moderate literature support"
    if score >= 0.2:
        return "🟠 Weak literature support"
    return "🔴 Little or no literature support"
