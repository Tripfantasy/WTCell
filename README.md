# WTCell

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
- [For Developers / Local Setup](#for-developers--local-setup)
- [Further Reading](#further-reading)

---

## Who is this for?

WTCell is built for **bench scientists** performing single-cell RNA sequencing (scRNA-seq) experiments who want to:

- Record and share the marker genes they use to annotate cell types
- Ensure their gene names match the official standard (HGNC for human, MGI for mouse)
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
   docker-compose up -d
   ```
4. Open your browser and go to **http://localhost:8501**
5. You will see the WTCell dashboard. Use the sidebar to switch between **Query** and **Submit** views.

---

## What Can I Do?

| Task | Where to go |
|---|---|
| Search for markers by cell type, tissue, or organism | **Query Dashboard** tab |
| Submit new marker genes from your experiment | **Submission Form** tab |
| Download a template CSV to prepare your entries offline | `examples/marker_submission_template.csv` |
| Look up what a term means (e.g. "Cell Ontology ID") | [GLOSSARY.md](GLOSSARY.md) |
| Troubleshoot a submission error or gene naming issue | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Understand the full submission process step by step | [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md) |

---

## Submitting Marker Data

The Submission Form guides you through each field. The most important things to know:

1. **Select your organism first** — this determines how gene symbols must be formatted.
2. **Gene symbols are auto-corrected** — the form will automatically apply the correct capitalization for your organism (see [Gene Nomenclature Rules](#gene-nomenclature-rules)).
3. **A stable gene ID is required** — you must provide either an NCBI Gene ID or an Ensembl ID alongside the gene symbol. This prevents duplicate entries with different symbol spellings.
4. **Cell type names come from a dropdown** — choose from the standardized list. If your cell type is missing, contact the database administrator to have it added.

For a detailed walkthrough with screenshots and examples, see [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md).

---

## Querying the Database

From the **Query Dashboard**:

- Use the **Organism** dropdown to filter by human, mouse, or other species.
- Use the **Tissue** filter to narrow results to a specific tissue or organ.
- Use the **Cell Type** search box to find all markers associated with a cell type.
- Results appear as a table you can sort and export.

---

## Gene Nomenclature Rules

Getting gene names right is the most common source of errors. WTCell enforces the following rules automatically:

| Organism | Rule | Example |
|---|---|---|
| **Human** | All uppercase (HGNC standard) | `CD3E`, `PTPRC`, `EPCAM` |
| **Mouse** | First letter uppercase, rest lowercase (MGI standard) | `Cd3e`, `Ptprc`, `Epcam` |

The form will reformat your input automatically, but it is good practice to use the correct format from the start. See [GLOSSARY.md](GLOSSARY.md) for links to the HGNC and MGI databases.

---

## For Developers / Local Setup

Full setup instructions, environment variables, and the database schema are documented in the following files generated alongside this application:

| File | Purpose |
|---|---|
| `schema.sql` | PostgreSQL table definitions, keys, and constraints |
| `validation.py` | Gene symbol normalization and ID validation logic |
| `db.py` | Database connection helpers and query/insert functions |
| `app.py` | Streamlit application entry point |
| `requirements.txt` | Python dependencies |
| `.env.example` | Required environment variables |
| `docker-compose.yml` | One-command local PostgreSQL deployment |

---

## Further Reading

- [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md) — Step-by-step guide for bench scientists submitting marker data
- [GLOSSARY.md](GLOSSARY.md) — Plain-language definitions of all technical terms
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common errors, discrepancy resolution, and FAQ
- [HGNC Gene Nomenclature](https://www.genenames.org/) — Official human gene symbol lookup
- [MGI Gene Nomenclature](https://www.informatics.jax.org/) — Official mouse gene symbol lookup
- [Cell Ontology (CL)](https://obofoundry.org/ontology/cl.html) — Standardized cell type terms
- [Uberon Anatomy Ontology](https://uberon.github.io/) — Standardized tissue/organ terms

