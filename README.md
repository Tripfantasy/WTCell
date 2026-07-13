# WTCell 🧬

**A centralized, multi-organism database for standardized scRNA-seq cell type markers.**

WTCell allows research groups to collaboratively submit, standardize, and query marker genes across species — enforcing consistent gene nomenclature to eliminate discrepancies between labs.

---

## Table of Contents

- [Who is this for?](#who-is-this-for)
- [Quick Start](#quick-start)
- [What Can I Do?](#what-can-i-do)
- [Submitting Marker Data](#submitting-marker-data)
- [Querying the Database](#querying-the-database)
- [Gene Nomenclature Rules](#gene-nomenclature-rules)
- [Supported Organisms](#supported-organisms)
- [Architecture](#architecture)
- [For Developers / Local Setup](#for-developers--local-setup)
- [Running Tests](#running-tests)
- [Further Reading](#further-reading)

---

## Who is this for?

WTCell is built for **bench scientists** performing single-cell RNA sequencing (scRNA-seq) experiments who want to:

- Record and share the marker genes they use to annotate cell types
- Ensure their gene names match the official standard (HGNC for human, MGI for mouse, etc.)
- Look up what markers other labs in the department are using for a given cell type or tissue
- Resolve disagreements between labs about gene symbol formatting

No programming experience is required to use the submission form or search dashboard.

---

## Quick Start

> **Prerequisites:** Docker Desktop must be installed on your computer. Ask your IT/bioinformatics support contact if you need help installing it.

1. Clone or download this repository.
2. Copy `.env.example` to `.env` and fill in a database password of your choice.
3. From a terminal in the project folder, run:
   ```bash
   docker-compose up --build
   ```
4. Open your browser and go to **http://localhost:8501**
5. You will see the WTCell dashboard. Use the sidebar to switch between **🔍 Query Dashboard** and **📝 Submit Marker** views.

> **First run only:** `--build` compiles the app container image. Subsequent starts can use `docker-compose up` without `--build`.

---

## What Can I Do?

| Task | Where to go |
|---|---|
| Search for markers by cell type, tissue, or organism | **🔍 Query Dashboard** tab |
| Submit new marker genes from your experiment | **📝 Submit Marker** tab |
| Add a new cell type (not in the dropdown) | **📝 Submit Marker → ➕ Add a new cell type** expander |
| Download a template CSV to prepare entries offline | `examples/marker_submission_template.csv` |
| Look up what a term means (e.g. "Cell Ontology ID") | [GLOSSARY.md](GLOSSARY.md) |
| Troubleshoot a submission error or gene naming issue | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Understand the full submission process step by step | [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md) |

---

## Submitting Marker Data

The Submission Form is divided into five sections:

1. **Organism & Cell Type** — select from standardized dropdowns
2. **Gene Information** — enter the gene symbol and a stable gene ID; the symbol is auto-corrected to the right capitalization for your organism
3. **Experimental Context** — tissue and sequencing platform
4. **Provenance** — source reference (PubMed ID, DOI, or internal dataset ID) and your email
5. **Validate & Submit** — click **🔎 Validate** first, then **💾 Submit to database** once validation passes

> The two-step flow is intentional: validation checks your gene symbol and ID against official databases *before* writing anything to the database. This catches typos and mismatched organisms early.

For a detailed walkthrough of every field, see [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md).

---

## Querying the Database

From the **🔍 Query Dashboard**:

- Use the **Organism** dropdown to filter by any supported species.
- Use the **Cell Type** dropdown to narrow results to a specific cell type.
- Use the **Tissue** free-text box to search by tissue name or UBERON term.
- Results appear as a sortable table. Leave all filters blank to show all records.

---

## Gene Nomenclature Rules

Getting gene names right is the most common source of errors. WTCell enforces the following rules automatically:

| Organism | Authority | Symbol rule | Example |
|---|---|---|---|
| Human (*Homo sapiens*) | HGNC | ALL UPPERCASE | `CD3E`, `TP53` |
| Mouse (*Mus musculus*) | MGI | First letter uppercase only | `Cd3e`, `Trp53` |
| Zebrafish (*Danio rerio*) | ZFIN | Stored as entered | `tp53` |
| Rat (*Rattus norvegicus*) | RGD | Stored as entered | `Tp53` |
| Fruit Fly (*Drosophila melanogaster*) | FlyBase | Stored as entered | `p53` |
| Nematode (*C. elegans*) | WormBase | Stored as entered | `cep-1` |

The form auto-corrects Human and Mouse capitalization. For all other organisms, symbols are stored exactly as you type them. See [GLOSSARY.md](GLOSSARY.md) for links to each nomenclature authority.

---

## Supported Organisms

WTCell ships with six organisms pre-loaded. Additional organisms can be added by the database administrator using a single SQL statement — contact them or see the schema comments in `schema.sql`.

---

## Architecture

```
WTCell/
├── schema.sql          # PostgreSQL schema + seed data
├── db.py               # Database connection & query helpers
├── validation.py       # Gene symbol normalisation & ID validation
├── app.py              # Streamlit UI (Query Dashboard + Submission Form)
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container image for the Streamlit app
├── docker-compose.yml  # Full stack: PostgreSQL 16 + Streamlit
├── .env.example        # Environment variable template
├── tests/
│   └── test_validation.py  # Unit tests (no DB or network required)
├── SUBMISSION_GUIDE.md # Step-by-step guide for bench scientists
├── GLOSSARY.md         # Plain-language definitions of all terms
├── TROUBLESHOOTING.md  # FAQ and discrepancy resolution guide
└── examples/
    └── marker_submission_template.csv  # Bulk upload template
```

**Database schema (simplified):**

```
organisms              cell_types
─────────              ──────────
organism_id  PK        cell_type_id  PK
common_name            standardized_name
scientific_name        cell_ontology_id
ncbi_taxon_id          aliases
nomenclature_authority
      │                       │
      └────────────┬──────────┘
                   │
               markers
               ───────
               marker_id  PK
               organism_id   FK → organisms
               cell_type_id  FK → cell_types
               gene_symbol
               gene_id        (NCBI or Ensembl)
               tissue
               platform
               submission_source
               submitter_email
               date_submitted
```

---

## For Developers / Local Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 14+

### Steps

```bash
# 1. Create the database
psql -U postgres -c "CREATE USER wtcell_user WITH PASSWORD 'your_password';"
psql -U postgres -c "CREATE DATABASE wtcell OWNER wtcell_user;"
psql -U wtcell_user -d wtcell -f schema.sql

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — at minimum set DB_PASSWORD

# 4. Run the app
streamlit run app.py
```

All database configuration is driven by environment variables (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`). There is no hard-coded password. If `DB_PASSWORD` is unset the application will warn and fail to connect.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests cover all gene symbol normalization rules and gene ID format validation. No database connection or network access is required.

---

## Further Reading

- [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md) — Step-by-step guide for bench scientists submitting marker data
- [GLOSSARY.md](GLOSSARY.md) — Plain-language definitions of all technical terms
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common errors, discrepancy resolution, and FAQ
- [HGNC Gene Nomenclature](https://www.genenames.org/) — Official human gene symbol lookup
- [MGI Gene Nomenclature](https://www.informatics.jax.org/) — Official mouse gene symbol lookup
- [Cell Ontology (CL)](https://obofoundry.org/ontology/cl.html) — Standardized cell type terms
- [Uberon Anatomy Ontology](https://uberon.github.io/) — Standardized tissue/organ terms
