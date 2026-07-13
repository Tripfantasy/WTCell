# WTCell Submission Guide

**A step-by-step guide for bench scientists submitting marker gene data.**

This guide walks you through every field in the submission form, explains why each piece of information is needed, and highlights the most common mistakes to avoid.

---

## Table of Contents

- [Before You Start](#before-you-start)
- [Opening the Submission Form](#opening-the-submission-form)
- [Form Walkthrough](#form-walkthrough)
  - [Section 1 — Organism & Cell Type](#section-1--organism--cell-type)
  - [Section 2 — Gene Information](#section-2--gene-information)
  - [Section 3 — Experimental Context](#section-3--experimental-context)
  - [Section 4 — Provenance](#section-4--provenance)
  - [Section 5 — Validate & Submit](#section-5--validate--submit)
- [Adding a New Cell Type](#adding-a-new-cell-type)
- [Submitting Multiple Markers at Once](#submitting-multiple-markers-at-once)
- [After Submission](#after-submission)
- [Requesting a New Organism](#requesting-a-new-organism)

---

## Before You Start

Gather the following for each marker gene you want to submit:

- [ ] The **organism** (e.g., Human, Mouse, Zebrafish)
- [ ] The **cell type name** — you will pick from a dropdown; see [Adding a New Cell Type](#adding-a-new-cell-type) if yours is missing
- [ ] The **official gene symbol** (e.g., `CD3E` for human, `Cd3e` for mouse)
- [ ] Either an **NCBI Gene ID** (a plain number, e.g., `916`) *or* an **Ensembl ID** (starts with `ENSG` for human or `ENSMUSG` for mouse)
- [ ] The **tissue or organ** where this marker was identified (e.g., `peripheral blood`, `lung`)
- [ ] The **sequencing platform** used (e.g., `10x Chromium v3`, `Smart-seq2`)
- [ ] A **reference** — either `PMID:` followed by the PubMed ID (e.g., `PMID:31327801`), a DOI (e.g., `doi:10.1038/s41586-020-2277-x`), or an internal dataset identifier

If you are unsure about any field, see [GLOSSARY.md](GLOSSARY.md) for plain-language definitions.

---

## Opening the Submission Form

1. Navigate to the WTCell dashboard in your browser (default: **http://localhost:8501**).
2. In the left sidebar, click **📝 Submit Marker**.
3. The submission form will load on the main panel.

---

## Form Walkthrough

The form has five numbered sections. Work through them in order.

---

### Section 1 — Organism & Cell Type

**Organism dropdown**

Select the species your data comes from.

> Available: `Human (Homo sapiens)`, `Mouse (Mus musculus)`, `Zebrafish (Danio rerio)`, `Rat (Rattus norvegicus)`, `Fruit Fly (Drosophila melanogaster)`, `Nematode (Caenorhabditis elegans)`

After you select an organism, a caption below the cell type dropdown will tell you which gene naming rule applies. For example:
- *Human* → "Gene symbols will be converted to **ALL UPPERCASE**."
- *Mouse* → "Gene symbols will follow **Title Case** (e.g. Cd3e)."
- *Others* → "Gene symbols will be stored as entered."

**Why organism selection matters:** The gene naming rule is applied automatically based on your selection. Selecting the wrong organism will incorrectly format your gene symbol.

---

**Cell Type dropdown**

Select the cell type from the standardized list. The list is drawn from the [Cell Ontology (CL)](https://obofoundry.org/ontology/cl.html).

> Examples: `T cell`, `Natural killer cell`, `Alveolar macrophage`, `Hepatocyte`

**Tips:**
- Type part of the name to filter the list quickly.
- Pick the most specific term that matches your annotation.
- If your cell type is not listed, use the **➕ Add a new cell type** expander *before* filling in the rest of the form (see [Adding a New Cell Type](#adding-a-new-cell-type)).

---

### Section 2 — Gene Information

**Gene symbol** *(required)*

Type the official gene symbol for your marker.

> Human example: `CD3E`  
> Mouse example: `Cd3e`  
> Zebrafish example: `cd3e`

**Auto-correction:** After you select the organism, the form will automatically reformat your symbol:
- Human → ALL CAPS
- Mouse → First letter uppercase, rest lowercase (e.g. `Cd3e`)
- Others → stored exactly as typed

**How to look up the official symbol:**
- Human: [genenames.org](https://www.genenames.org/)
- Mouse: [informatics.jax.org](https://www.informatics.jax.org/)
- Zebrafish: [zfin.org](https://zfin.org/)

> ⚠️ **Common mistake:** Using a protein name (`CD45`) or an alias (`B220`) instead of the official gene symbol (`PTPRC` / `Ptprc`). The form cannot detect alias substitution automatically — you must use the approved symbol.

---

**Gene ID** *(required — NCBI or Ensembl)*

Provide *at least one* stable gene identifier.

| ID Type | Format | Where to Find |
|---|---|---|
| NCBI Gene ID | A plain number only, e.g., `916` | [ncbi.nlm.nih.gov/gene](https://www.ncbi.nlm.nih.gov/gene) |
| Ensembl Gene ID | `ENSG` + 11 digits (human); `ENSMUSG` + 11 digits (mouse) | [ensembl.org](https://www.ensembl.org) |

**Why it matters:** Gene symbols can change over time. A stable numeric or accession ID ensures the record always traces back to the correct gene.

**Quick lookup (NCBI):**
1. Go to [ncbi.nlm.nih.gov/gene](https://www.ncbi.nlm.nih.gov/gene)
2. Search for your gene name and select your organism
3. The Gene ID is the number shown at the top of the gene page

> ⚠️ **The form will reject submissions without a valid NCBI or Ensembl ID.** Do not include a version suffix on Ensembl IDs (e.g., `ENSG00000198851` is correct; `ENSG00000198851.2` is not).

---

**Skip remote API validation (offline mode)**

By default, the form queries HGNC and MyGene.info to verify your gene symbol exists in the official database. If you are working in an environment without internet access, check this box to skip those network requests and proceed with format-only validation.

---

### Section 3 — Experimental Context

**Tissue**

Enter the tissue or organ where you identified this marker. UBERON ontology terms are preferred but plain text is accepted.

> Examples: `peripheral blood`, `UBERON:0002106` (spleen), `lung`, `bone marrow`

**Tips:**
- Be as specific as possible (e.g., `alveolus of lung` vs. just `lung`) if your dataset supports it.
- For circulating cells without a fixed tissue location, use `peripheral blood`.

**Sequencing platform**

Enter the single-cell sequencing platform used.

> Examples: `10x Chromium v3`, `10x Chromium v2`, `Smart-seq2`, `Drop-seq`, `inDrop`

This field is optional but strongly recommended. Marker reliability can differ between platforms.

---

### Section 4 — Provenance

**Submission source**

Enter a reference for where this marker data comes from.

| Source type | Format | Example |
|---|---|---|
| Published paper | `PMID:` + PubMed ID | `PMID:31327801` |
| Preprint | `doi:` + DOI | `doi:10.1101/2020.03.10.986836` |
| Internal dataset | Your lab's dataset identifier | `Smith_Lab_PBMC_2024` |

If you are submitting unpublished data, use a consistent internal ID so entries from the same experiment can be grouped later.

**Submitter email** *(required)*

Enter your institutional email address (e.g., `researcher@institution.edu`). This is used to contact you if there is a question about your submission — it is not displayed publicly.

---

### Section 5 — Validate & Submit

**This is a two-step process.** You must validate before you can submit.

**Step 1 — Click 🔎 Validate gene symbol and ID**

This checks:
1. That the gene symbol is not empty
2. That the gene ID format is correct (numeric for NCBI, or `ENS[species]G` + 11 digits for Ensembl)
3. If online mode: that the gene symbol exists in the HGNC or MGI/MyGene.info database
4. That the submitter email is filled in

A green box confirms validation passed and shows the normalised gene symbol that will be stored. A red box describes what needs to be fixed.

**Step 2 — Click 💾 Submit to database**

This button is only active after validation passes. When you click it, the record is written to the database and you will see a success message with the assigned marker ID.

> ⚠️ **If you change any field after validating, click Validate again** before submitting — the Submit button will remain active from the previous validation but the data in the form will have changed.

---

## Adding a New Cell Type

If the cell type you need is not in the dropdown:

1. In the submission form, scroll to the **➕ Add a new cell type** expander (below the cell type dropdown) and click to expand it.
2. Fill in:
   - **New cell type name** *(required)* — the standardized name (e.g., `Alveolar type II cell`)
   - **Cell Ontology ID** *(optional but recommended)* — format `CL:XXXXXXX` (7 digits). Look it up at [ontobee.org/ontology/CL](http://www.ontobee.org/ontology/CL)
   - **Aliases** *(optional)* — comma-separated alternative names (e.g., `ATII cell,AT2 cell`)
3. Click **Register cell type**. The page will reload and the new cell type will appear in the dropdown.

> ⚠️ **Do not substitute a different cell type** to work around a missing entry — this creates inconsistent data that is hard to fix later.

---

## Submitting Multiple Markers at Once

If you have many markers to submit, prepare them offline using the provided template:

1. Download `examples/marker_submission_template.csv`
2. Fill in one row per marker (see the header row for column names and the example rows for correct formats)
3. On the submission form, click **Bulk Upload** and select your completed CSV
4. The form will validate each row and show a summary of any errors before writing to the database

> ⚠️ **Do not modify the column headers in the CSV template.** The bulk upload parser requires exact header names.
>
> For `submission_source`, use the `PMID:`, `doi:`, or internal-ID format shown in the template — bare numbers are not accepted.

---

## After Submission

- Successful submissions appear immediately in the **🔍 Query Dashboard**.
- You will see a confirmation message with the assigned marker ID, the stored gene symbol, and the cell type.
- If a duplicate is detected (same organism + cell type + gene symbol + tissue + platform already exists), you will see a warning message and the submission will not proceed — the existing record is sufficient.

---

## Requesting a New Organism

If the organism you need is not in the dropdown, contact the database administrator with:

- The common name of the species
- Its scientific (Latin) name
- Its NCBI Taxonomy ID (look it up at [ncbi.nlm.nih.gov/taxonomy](https://www.ncbi.nlm.nih.gov/taxonomy))
- The nomenclature authority for that species (if known)

New organisms are added via a single database entry and are typically available within 1–2 business days.
