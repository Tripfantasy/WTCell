# WTCell Submission Guide

**A step-by-step guide for bench scientists submitting marker gene data.**

This guide walks you through every field in the submission form, explains why each piece of information is needed, and highlights the most common mistakes to avoid.

---

## Table of Contents

- [Before You Start](#before-you-start)
- [Opening the Submission Form](#opening-the-submission-form)
- [Field-by-Field Walkthrough](#field-by-field-walkthrough)
  - [1. Organism](#1-organism)
  - [2. Cell Type](#2-cell-type)
  - [3. Gene Symbol](#3-gene-symbol)
  - [4. Gene ID (NCBI or Ensembl)](#4-gene-id-ncbi-or-ensembl)
  - [5. Tissue / Anatomical Context](#5-tissue--anatomical-context)
  - [6. Sequencing Platform](#6-sequencing-platform)
  - [7. Submission Source](#7-submission-source)
  - [8. Submitter Email](#8-submitter-email)
- [Submitting Multiple Markers at Once](#submitting-multiple-markers-at-once)
- [After Submission](#after-submission)
- [Requesting a New Cell Type or Organism](#requesting-a-new-cell-type-or-organism)

---

## Before You Start

Gather the following for each marker gene you want to submit:

- [ ] The **organism** (e.g., human, mouse)
- [ ] The **cell type name** (you will pick from a dropdown — see [Requesting a New Cell Type](#requesting-a-new-cell-type-or-organism) if yours is missing)
- [ ] The **official gene symbol** (e.g., `CD3E` for human, `Cd3e` for mouse)
- [ ] Either an **NCBI Gene ID** (a number, e.g., `916`) *or* an **Ensembl ID** (starts with `ENSG` for human or `ENSMUSG` for mouse)
- [ ] The **tissue or organ** where this marker was identified (e.g., `peripheral blood`, `lung`)
- [ ] The **sequencing platform** used (e.g., `10x Chromium v3`, `Smart-seq2`)
- [ ] A **reference** — either a PubMed ID (PMID) or your internal dataset identifier

If you are unsure about any field, see [GLOSSARY.md](GLOSSARY.md) for plain-language definitions.

---

## Opening the Submission Form

1. Navigate to the WTCell dashboard in your browser (default: **http://localhost:8501**).
2. In the left sidebar, click **"Submit Marker"**.
3. The submission form will load on the main panel.

---

## Field-by-Field Walkthrough

### 1. Organism

**What to do:** Select your organism from the dropdown menu.

> Example: `Human (Homo sapiens)` or `Mouse (Mus musculus)`

**Why it matters:** The organism you select determines the gene naming rules applied to your entry. Human genes use all-uppercase symbols (HGNC standard); mouse genes use title-case symbols (MGI standard). The form enforces this automatically — but selecting the wrong organism will incorrectly reformat your gene symbol.

---

### 2. Cell Type

**What to do:** Select the cell type from the dropdown menu. The list is drawn from the [Cell Ontology (CL)](https://obofoundry.org/ontology/cl.html), so names are standardized.

> Examples: `T cell`, `natural killer cell`, `alveolar macrophage`, `goblet cell`

**Tips:**
- Type part of the name in the search box to filter the list quickly.
- If you annotated a subtype (e.g., "CD8+ effector T cell"), look for the most specific matching term.
- If your cell type is not listed, **do not use a free-text workaround** — contact the database administrator to add it (see [Requesting a New Cell Type](#requesting-a-new-cell-type-or-organism)).

---

### 3. Gene Symbol

**What to do:** Type the official gene symbol.

> Human example: `CD3E`  
> Mouse example: `Cd3e`

**Auto-correction:** After you select the organism, the form will automatically reformat your symbol to match the correct convention:
- Human → converts to ALL CAPS
- Mouse → converts to Title Case (first letter uppercase, rest lowercase)

**How to look up the official symbol:**
- Human: Search [genenames.org](https://www.genenames.org/)
- Mouse: Search [informatics.jax.org](https://www.informatics.jax.org/)

> ⚠️ **Common mistake:** Submitting `cd3e` (all lowercase) or `CD3E` for a mouse gene. The form will correct the case, but verify you have the right gene.

---

### 4. Gene ID (NCBI or Ensembl)

**What to do:** Provide *at least one* stable gene identifier. You can enter both.

| ID Type | Format | Where to Find |
|---|---|---|
| NCBI Gene ID | A number only, e.g., `916` | [ncbi.nlm.nih.gov/gene](https://www.ncbi.nlm.nih.gov/gene) — search by gene name |
| Ensembl ID | Starts with `ENSG` (human) or `ENSMUSG` (mouse) | [ensembl.org](https://www.ensembl.org) — search by gene name |

**Why it matters:** Gene symbols can be ambiguous or change over time. A stable numeric or accession ID ensures entries can always be traced back to the correct gene, even if the symbol is later updated.

> ⚠️ **The form will reject submissions without a valid NCBI or Ensembl ID.**

**Quick lookup steps (NCBI):**
1. Go to [ncbi.nlm.nih.gov/gene](https://www.ncbi.nlm.nih.gov/gene)
2. Search for your gene name and select your organism
3. The Gene ID is the number in the top-left of the gene page

---

### 5. Tissue / Anatomical Context

**What to do:** Select or type the tissue or organ where you identified this marker. Terms are drawn from the [Uberon anatomy ontology](https://uberon.github.io/).

> Examples: `peripheral blood`, `bone marrow`, `lung`, `large intestine`, `liver`

**Tips:**
- Be as specific as possible (e.g., `alveolus of lung` rather than just `lung`) if your dataset allows it.
- For circulating cells without a fixed tissue, use `blood` or `peripheral blood`.

---

### 6. Sequencing Platform

**What to do:** Select the single-cell sequencing platform used to generate the data.

> Examples: `10x Chromium v3`, `10x Chromium v2`, `Smart-seq2`, `Drop-seq`, `inDrop`

**Why it matters:** Marker gene sensitivity and specificity can differ between platforms, so this context helps users interpret results correctly.

---

### 7. Submission Source

**What to do:** Enter a reference for where this marker data comes from. Acceptable formats:

| Source type | What to enter | Example |
|---|---|---|
| Published paper | PubMed ID (PMID) — numbers only | `32214231` |
| Preprint | DOI or bioRxiv ID | `10.1101/2020.03.10.986836` |
| Internal dataset | Your lab's dataset identifier | `Smith_Lab_PBMC_2024` |

If you are submitting unpublished data, use a consistent internal ID so entries from the same experiment can be grouped.

---

### 8. Submitter Email

**What to do:** Enter your institutional email address.

This is used to contact you if there is a question about your submission or if a discrepancy is detected against an existing entry. It is not displayed publicly.

---

## Submitting Multiple Markers at Once

If you have many markers to submit, you can prepare them offline using the provided template:

1. Download `examples/marker_submission_template.csv`
2. Fill in one row per marker (see the header row for column names and the example rows for guidance)
3. On the submission form, click **"Bulk Upload"** and select your completed CSV file
4. The form will validate each row and show a summary of any errors before writing to the database

> ⚠️ **Do not modify the column headers in the CSV template.** The bulk upload parser requires exact header names.

---

## After Submission

- Successful submissions appear immediately in the **Query Dashboard**.
- You will receive a confirmation with the assigned marker ID(s) on screen.
- If a duplicate entry is detected (same gene + organism + cell type + tissue already exists), you will be shown the existing entry and asked to confirm before a second copy is added.

---

## Requesting a New Cell Type or Organism

If the cell type or organism you need is not in the dropdown:

1. **Do not** submit with a free-text substitute — this creates inconsistent data.
2. Contact the database administrator (email listed on the dashboard homepage) with:
   - The cell type name you need
   - The matching Cell Ontology ID (look it up at [ontobee.org](http://www.ontobee.org/ontology/CL)) if possible
   - Or the organism's NCBI Taxonomy ID (look it up at [ncbi.nlm.nih.gov/taxonomy](https://www.ncbi.nlm.nih.gov/taxonomy))
3. New entries are typically added within 1–2 business days.
