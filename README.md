# WTCell 🧬

A centralized, multi-organism cell type annotation database for single-cell RNA sequencing (scRNA-seq) data.

WTCell allows researchers across different labs to **submit, standardize, and query marker genes** across various species while strictly enforcing proper gene nomenclature (HGNC for human, MGI for mouse, etc.).

---

## Features

| Feature | Details |
|---|---|
| **Decoupled schema** | Cell types (universal concepts) are stored separately from species-specific gene markers, preventing duplication |
| **Nomenclature enforcement** | Human genes → ALL UPPERCASE (HGNC); Mouse genes → Title Case (MGI) |
| **Stable gene IDs required** | Every submission must include an NCBI Gene ID or Ensembl Gene ID |
| **Remote API validation** | Optional live verification against HGNC REST API and MyGene.info |
| **Query dashboard** | Filter markers by organism, cell type, or tissue |
| **Submission form** | Structured UI with automated validation before writing to DB |
| **Multi-organism support** | Human, Mouse, Zebrafish, Rat, Fruit fly, Nematode (extensible) |

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
├── docker-compose.yml  # Full stack (PostgreSQL + Streamlit)
├── .env.example        # Environment variable template
└── tests/
    └── test_validation.py  # Unit tests for validation logic
```

### Database Schema

```
organisms          cell_types
─────────          ──────────
organism_id  PK    cell_type_id  PK
common_name        standardized_name
scientific_name    cell_ontology_id
ncbi_taxon_id      aliases
nomenclature_authority
       │                  │
       └──────────┬───────┘
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

## Quick Start (Docker — recommended)

```bash
# 1. Clone the repository
git clone https://github.com/Tripfantasy/WTCell.git
cd WTCell

# 2. Start the full stack (PostgreSQL + Streamlit)
docker-compose up --build

# 3. Open the app
open http://localhost:8501
```

The PostgreSQL database is automatically initialised with `schema.sql` on first start.

---

## Manual Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 14+

### 1 — Database

```bash
# Create database and user
psql -U postgres -c "CREATE USER wtcell_user WITH PASSWORD 'wtcell_pass';"
psql -U postgres -c "CREATE DATABASE wtcell OWNER wtcell_user;"

# Initialise schema and seed data
psql -U wtcell_user -d wtcell -f schema.sql
```

### 2 — Python environment

```bash
pip install -r requirements.txt
```

### 3 — Configuration

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4 — Run the app

```bash
streamlit run app.py
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests cover all gene symbol normalisation rules and gene ID format validation without requiring a database connection or network access.

---

## Gene Nomenclature Rules

| Organism | Authority | Symbol rule | Example |
|---|---|---|---|
| Human (*Homo sapiens*) | HGNC | ALL UPPERCASE | `CD3E`, `TP53` |
| Mouse (*Mus musculus*) | MGI | First letter uppercase | `Cd3e`, `Trp53` |
| Zebrafish (*Danio rerio*) | ZFIN | As entered | `tp53` |
| Rat (*Rattus norvegicus*) | RGD | As entered | `Tp53` |

### Gene ID Formats

| Format | Pattern | Example |
|---|---|---|
| NCBI Gene ID | Digits only | `916` |
| Ensembl Gene ID | `ENS[species]G` + 11 digits | `ENSG00000198851` |

---

## API Validation

When the **offline mode** checkbox is unchecked, the submission form performs live lookups:

- **HGNC symbols** → [HGNC REST API](https://www.genenames.org/tools/rest/) (`rest.genenames.org`)
- **MGI symbols** → [MyGene.info](https://mygene.info/) (mouse taxon 10090)

The API calls time out gracefully after 8 seconds — if the external service is unreachable the submission proceeds with a warning.

---

## Extending the Database

### Add a new organism

```sql
INSERT INTO organisms (common_name, scientific_name, ncbi_taxon_id, nomenclature_authority)
VALUES ('Chicken', 'Gallus gallus', 9031, 'ENTREZ');
```

### Add a new cell type

Use the **"Add a new cell type"** expander in the Submission Form, or insert directly:

```sql
INSERT INTO cell_types (standardized_name, cell_ontology_id, aliases)
VALUES ('Cardiomyocyte', 'CL:0000746', 'heart muscle cell');
```

---

## License

MIT
