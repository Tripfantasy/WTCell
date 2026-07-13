"""
app.py
======
WTCell — Streamlit front-end application.

Two main views (selected via the sidebar):
  1. Query Dashboard  — searchable, filterable table of all marker records.
  2. Submission Form  — structured form for adding new validated marker genes.

Run with:
    streamlit run app.py

Environment variables (see .env.example):
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
"""

import os
import re
import logging
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file (if present).
# In production deployments the variables should be injected by the host.
load_dotenv()

# Local modules
import db
import validation

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page-wide Streamlit configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="WTCell — Cell Type Marker Database",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ===========================================================================
# Cached data loaders — re-fetched at most once per Streamlit session so that
# reference data (organisms, cell types) doesn't hit the database on every
# widget interaction.
# ===========================================================================

@st.cache_data(ttl=300)   # cache for 5 minutes
def load_organisms() -> List[Dict]:
    """Load all organisms from the database."""
    return db.fetch_all_organisms()


@st.cache_data(ttl=300)
def load_cell_types() -> List[Dict]:
    """Load all cell types from the database."""
    return db.fetch_all_cell_types()


# ===========================================================================
# Helper: DB connectivity check
# ===========================================================================

def check_db_connection() -> bool:
    """
    Test the database connection and display a banner in the Streamlit UI.

    Returns True if connected, False otherwise.
    """
    if db.test_connection():
        return True
    st.error(
        "⚠️  **Cannot reach the database.**  "
        "Please check the connection settings in your `.env` file "
        "(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD) "
        "and ensure PostgreSQL is running."
    )
    return False


# ===========================================================================
# View 1 — Query Dashboard
# ===========================================================================

def render_query_dashboard() -> None:
    """
    Render the searchable marker query dashboard.

    Provides dropdown filters for organism and cell type, plus a free-text
    tissue search field.  Results are displayed in a sortable Pandas DataFrame.
    """
    st.header("🔍 Query Dashboard")
    st.markdown(
        "Search and filter the WTCell marker database.  "
        "Leave filters blank to show all records."
    )

    # --- Load reference data ------------------------------------------------
    organisms  = load_organisms()
    cell_types = load_cell_types()

    if not organisms:
        st.warning("No organisms found in the database.  Run `schema.sql` to seed data.")
        return

    # --- Filter controls (three columns) ------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        organism_options = {"(All organisms)": None} | {
            f"{o['common_name']} ({o['scientific_name']})": o["organism_id"]
            for o in organisms
        }
        selected_organism_label = st.selectbox(
            "🦠 Organism", list(organism_options.keys()), index=0
        )
        selected_organism_id: Optional[int] = organism_options[selected_organism_label]

    with col2:
        cell_type_options = {"(All cell types)": None} | {
            ct["standardized_name"]: ct["cell_type_id"] for ct in cell_types
        }
        selected_cell_type_label = st.selectbox(
            "🔬 Cell type", list(cell_type_options.keys()), index=0
        )
        selected_cell_type_id: Optional[int] = cell_type_options[selected_cell_type_label]

    with col3:
        tissue_query = st.text_input(
            "🫀 Tissue (free text or UBERON term)",
            placeholder="e.g. blood, UBERON:0002371",
        )

    # --- Execute query -------------------------------------------------------
    with st.spinner("Fetching markers …"):
        try:
            rows = db.fetch_markers(
                organism_id=selected_organism_id,
                cell_type_id=selected_cell_type_id,
                tissue_filter=tissue_query if tissue_query.strip() else None,
            )
        except Exception as exc:
            st.error(f"Database query failed: {exc}")
            logger.exception("fetch_markers error")
            return

    # --- Results table -------------------------------------------------------
    if not rows:
        st.info("No markers match the current filters.")
        return

    # Convert list-of-dicts to a DataFrame and rename columns for display.
    df = pd.DataFrame(rows)

    # Human-friendly column headers
    df = df.rename(
        columns={
            "marker_id":              "ID",
            "organism":               "Organism",
            "nomenclature_authority": "Authority",
            "cell_type":              "Cell Type",
            "cell_ontology_id":       "CL ID",
            "gene_symbol":            "Gene Symbol",
            "gene_id":                "Gene ID",
            "tissue":                 "Tissue",
            "platform":               "Platform",
            "submission_source":      "Source",
            "submitter_email":        "Submitted By",
            "date_submitted":         "Date",
        }
    )

    st.markdown(f"**{len(df)} marker(s) found.**")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn(width="small"),
            "Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
        },
    )

    # --- Download button -----------------------------------------------------
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download as CSV",
        data=csv,
        file_name="wtcell_markers.csv",
        mime="text/csv",
    )


# ===========================================================================
# View 2 — Submission Form
# ===========================================================================

def render_submission_form() -> None:
    """
    Render the structured marker-gene submission form.

    Workflow:
    1. Researcher selects an organism and cell type from standardised dropdowns.
    2. Researcher enters the gene symbol and a stable gene ID.
    3. On clicking **Validate**, the application:
       a. Normalises the symbol according to the organism's nomenclature rules.
       b. Validates the gene ID format.
       c. (Optionally) queries the HGNC / MGI / MyGene.info API.
    4. If all checks pass, **Submit to database** becomes available.
    """
    st.header("📝 Submit Marker Gene")
    st.markdown(
        "Add a new experimentally validated or literature-supported marker gene "
        "to the WTCell database.  All fields marked **\\*** are required."
    )

    # --- Load reference data ------------------------------------------------
    organisms  = load_organisms()
    cell_types = load_cell_types()

    if not organisms or not cell_types:
        st.warning("Reference data missing.  Run `schema.sql` to seed organisms and cell types.")
        return

    # ---- Organism & cell type selectors ------------------------------------
    st.subheader("1 · Biological context")

    col_org, col_ct = st.columns(2)

    with col_org:
        organism_labels = [
            f"{o['common_name']} ({o['scientific_name']})" for o in organisms
        ]
        org_index = st.selectbox(
            "Organism *", range(len(organism_labels)),
            format_func=lambda i: organism_labels[i],
        )
        selected_organism: Dict = organisms[org_index]

    with col_ct:
        cell_type_labels = [ct["standardized_name"] for ct in cell_types]
        ct_index = st.selectbox(
            "Cell type *", range(len(cell_type_labels)),
            format_func=lambda i: cell_type_labels[i],
        )
        selected_cell_type: Dict = cell_types[ct_index]

    # Show which nomenclature authority will be applied
    authority = selected_organism["nomenclature_authority"]
    st.caption(
        f"ℹ️  Nomenclature authority for **{selected_organism['common_name']}**: "
        f"**{authority}**.  "
        + (
            "Gene symbols will be converted to **ALL UPPERCASE**."
            if authority == "HGNC"
            else "Gene symbols will follow **Title Case** (e.g. Cd3e)."
            if authority == "MGI"
            else "Gene symbols will be stored as entered."
        )
    )

    st.divider()

    # ---- Gene information --------------------------------------------------
    st.subheader("2 · Gene information")

    col_sym, col_gid = st.columns(2)

    with col_sym:
        raw_symbol = st.text_input(
            "Gene symbol *",
            placeholder="e.g. CD3E (human) or Cd3e (mouse)",
            help=(
                "Enter the gene symbol.  It will be automatically normalised "
                "to the correct case for the selected organism."
            ),
        )

    with col_gid:
        gene_id_input = st.text_input(
            "Gene ID * (NCBI or Ensembl)",
            placeholder="e.g. 916  or  ENSG00000198851",
            help=(
                "A stable, permanent gene identifier is required.  "
                "NCBI Gene IDs are plain integers.  "
                "Ensembl IDs follow the pattern ENS[species]G + 11 digits."
            ),
        )

    # Remote API validation toggle (useful to disable in offline environments)
    skip_remote = st.checkbox(
        "Skip remote API validation (offline mode)",
        value=False,
        help=(
            "When checked, only the format of the symbol and ID are checked "
            "(no network requests to HGNC / MyGene.info)."
        ),
    )

    st.divider()

    # ---- Experimental context ----------------------------------------------
    st.subheader("3 · Experimental context")

    col_tissue, col_platform = st.columns(2)

    with col_tissue:
        tissue_input = st.text_input(
            "Tissue",
            placeholder="e.g. UBERON:0002106 (spleen) or 'peripheral blood'",
            help="UBERON ontology term preferred, but free text is accepted.",
        )

    with col_platform:
        platform_input = st.text_input(
            "Sequencing platform",
            placeholder="e.g. 10x Chromium v3, Smart-seq2",
        )

    st.divider()

    # ---- Provenance --------------------------------------------------------
    st.subheader("4 · Provenance")

    col_source, col_email = st.columns(2)

    with col_source:
        source_input = st.text_input(
            "Submission source",
            placeholder="e.g. PMID:31327801, doi:10.1038/…, LAB_DATASET_001",
            help="PubMed ID, DOI, or internal dataset identifier.",
        )

    with col_email:
        email_input = st.text_input(
            "Submitter email *",
            placeholder="researcher@institution.edu",
        )

    st.divider()

    # ---- Optionally add a new cell type ------------------------------------
    with st.expander("➕  Add a new cell type (if not listed above)"):
        st.markdown(
            "If the target cell type does not appear in the dropdown, "
            "register it here first.  The page will reload with the new entry."
        )
        new_ct_name = st.text_input("New cell type name *")
        new_ct_cl   = st.text_input(
            "Cell Ontology ID", placeholder="CL:XXXXXXX"
        )
        new_ct_aliases = st.text_input(
            "Aliases (comma-separated)", placeholder="T lymphocyte,T-cell"
        )
        if st.button("Register cell type"):
            if not new_ct_name.strip():
                st.error("Cell type name is required.")
            else:
                # Validate CL ID format if provided
                if new_ct_cl.strip() and not re.match(r"^CL:[0-9]{7}$", new_ct_cl.strip()):
                    st.error("Cell Ontology ID must be in the format CL:XXXXXXX (7 digits).")
                else:
                    try:
                        new_id = db.insert_cell_type(
                            new_ct_name, new_ct_cl or None, new_ct_aliases or None
                        )
                        st.success(
                            f"✅ Cell type '{new_ct_name}' registered "
                            f"(cell_type_id = {new_id}).  "
                            "Refresh the page to see it in the dropdown."
                        )
                        # Invalidate the cell types cache
                        load_cell_types.clear()
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Failed to register cell type: {exc}")

    st.divider()

    # ---- Validate button ---------------------------------------------------
    st.subheader("5 · Validate and submit")

    # Store validation state across button clicks using session state
    if "validation_passed" not in st.session_state:
        st.session_state["validation_passed"] = False
    if "normalised_symbol" not in st.session_state:
        st.session_state["normalised_symbol"] = ""

    if st.button("🔎 Validate gene symbol and ID", type="secondary"):
        # Reset validation state
        st.session_state["validation_passed"] = False
        st.session_state["normalised_symbol"] = ""

        # Check required fields
        missing = []
        if not raw_symbol.strip():
            missing.append("Gene symbol")
        if not gene_id_input.strip():
            missing.append("Gene ID")
        if not email_input.strip():
            missing.append("Submitter email")
        if missing:
            st.error(f"Please fill in the required field(s): {', '.join(missing)}.")
        else:
            # Run full validation pipeline
            with st.spinner("Validating …"):
                normalised, is_valid, message = validation.validate_marker_submission(
                    gene_symbol=raw_symbol,
                    gene_id=gene_id_input,
                    nomenclature_authority=authority,
                    skip_remote=skip_remote,
                )

            # Display validation results in an expandable box
            with st.expander("Validation details", expanded=True):
                if is_valid:
                    st.success(message)
                else:
                    st.error(message)

            if is_valid:
                st.session_state["validation_passed"] = True
                st.session_state["normalised_symbol"] = normalised

    # ---- Submit button (only active after successful validation) -----------
    submit_disabled = not st.session_state["validation_passed"]
    if st.session_state["validation_passed"]:
        st.info(
            f"✅ Validation passed.  Normalised symbol: "
            f"**{st.session_state['normalised_symbol']}**"
        )

    if st.button(
        "💾 Submit to database",
        type="primary",
        disabled=submit_disabled,
    ):
        # Final email format check (belt-and-braces; the DB also checks)
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email_input.strip(), re.IGNORECASE):
            st.error("Please enter a valid email address.")
        else:
            try:
                new_marker_id = db.insert_marker(
                    organism_id=selected_organism["organism_id"],
                    cell_type_id=selected_cell_type["cell_type_id"],
                    gene_symbol=st.session_state["normalised_symbol"],
                    gene_id=gene_id_input.strip(),
                    tissue=tissue_input.strip() or None,
                    platform=platform_input.strip() or None,
                    submission_source=source_input.strip() or None,
                    submitter_email=email_input.strip(),
                )
                st.success(
                    f"🎉 Marker successfully submitted!  "
                    f"Record ID: **{new_marker_id}**  |  "
                    f"Gene: **{st.session_state['normalised_symbol']}**  |  "
                    f"Cell type: **{selected_cell_type['standardized_name']}**"
                )
                # Reset validation state after a successful submission
                st.session_state["validation_passed"] = False
                st.session_state["normalised_symbol"] = ""
            except Exception as exc:
                err_str = str(exc)
                if "unique constraint" in err_str.lower() or "duplicate" in err_str.lower():
                    st.error(
                        "⚠️  This marker already exists in the database "
                        "(same organism, cell type, gene symbol, tissue, and platform)."
                    )
                else:
                    st.error(f"Submission failed: {exc}")
                    logger.exception("insert_marker error")


# ===========================================================================
# Sidebar navigation
# ===========================================================================

def render_sidebar() -> str:
    """
    Render the sidebar navigation and return the selected page name.

    Returns
    -------
    str
        One of: 'Query Dashboard', 'Submit Marker'.
    """
    with st.sidebar:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/"
            "Cell_membrane_detailed_diagram_en.svg/320px-"
            "Cell_membrane_detailed_diagram_en.svg.png",
            use_container_width=True,
        )
        st.title("🧬 WTCell")
        st.markdown(
            "**Centralized multi-organism**  \n"
            "cell type annotation database  \n"
            "for scRNA-seq marker genes."
        )
        st.divider()

        page = st.radio(
            "Navigate",
            ["🔍 Query Dashboard", "📝 Submit Marker"],
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("#### Database status")
        if db.test_connection():
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")

        st.divider()
        st.caption(
            "WTCell · scRNA-seq marker database  \n"
            "[GitHub](https://github.com/Tripfantasy/WTCell)"
        )

    return page


# ===========================================================================
# Main entry point
# ===========================================================================

def main() -> None:
    """Application entry point — renders sidebar and routes to the active page."""
    page = render_sidebar()

    # Gate all views behind a connection check so users get a clear error
    # message rather than a cryptic psycopg2 traceback.
    if not check_db_connection():
        return

    if page == "🔍 Query Dashboard":
        render_query_dashboard()
    elif page == "📝 Submit Marker":
        render_submission_form()


if __name__ == "__main__":
    main()
