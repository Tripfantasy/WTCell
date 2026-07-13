# WTCell Troubleshooting & FAQ

**Answers to common problems when submitting data or querying the WTCell database.**

---

## Table of Contents

- [Submission Errors](#submission-errors)
  - [Gene symbol validation failed](#gene-symbol-validation-failed)
  - [Invalid or missing Gene ID](#invalid-or-missing-gene-id)
  - [Cell type not found in dropdown](#cell-type-not-found-in-dropdown)
  - [Duplicate entry detected](#duplicate-entry-detected)
  - [Bulk upload CSV errors](#bulk-upload-csv-errors)
  - [Remote API validation times out or fails](#remote-api-validation-times-out-or-fails)
- [Gene Naming Discrepancies](#gene-naming-discrepancies)
  - [My lab uses a different name/spelling than what the form accepts](#my-lab-uses-a-different-namespelling-than-what-the-form-accepts)
  - [The same gene has different entries from different labs](#the-same-gene-has-different-entries-from-different-labs)
  - [A gene symbol was updated in HGNC/MGI after we submitted](#a-gene-symbol-was-updated-in-hgncmgi-after-we-submitted)
- [Query / Search Issues](#query--search-issues)
  - [My search returns no results](#my-search-returns-no-results)
  - [I see the same gene listed multiple times](#i-see-the-same-gene-listed-multiple-times)
- [Access & Setup Problems](#access--setup-problems)
  - [The dashboard won't load](#the-dashboard-wont-load)
  - [I can't connect to the database](#i-cant-connect-to-the-database)
- [Contact & Escalation](#contact--escalation)

---

## Submission Errors

### Gene symbol validation failed

**Error message:** *"Gene symbol does not match HGNC/MGI records"* or *"Symbol format invalid for selected organism"*

**What it means:** The gene symbol you entered either doesn't exist in the official nomenclature database for your selected organism, or it could not be verified (e.g., a network timeout).

**Steps to resolve:**

1. **Check the organism selection** — are you sure you are submitting human (not mouse) data? Selecting the wrong organism will reformat the symbol incorrectly and may cause it to fail validation.

2. **Look up the correct official symbol:**
   - Human: [genenames.org](https://www.genenames.org/)
   - Mouse: [informatics.jax.org](https://www.informatics.jax.org/)
   - Zebrafish: [zfin.org](https://zfin.org/)

3. **Watch for common mistakes:**
   - Using a gene *alias* instead of the *approved symbol* (e.g., `OKT3` instead of `CD3E`, or `B220` instead of `PTPRC`)
   - Using a protein name instead of a gene name (e.g., `CD45` instead of `PTPRC`)
   - Including a hyphen or suffix that shouldn't be there (e.g., `CD3-E` instead of `CD3E`)

4. **Network issue?** If validation fails because the HGNC or MyGene.info server is unreachable, check the **Skip remote API validation (offline mode)** box and re-validate. Format-only checks will still run. See [GLOSSARY.md — Offline Mode](GLOSSARY.md#offline-mode) for details.

---

### Invalid or missing Gene ID

**Error message:** *"A valid NCBI Gene ID or Ensembl ID is required"*

**What it means:** The submission form requires at least one stable gene identifier.

**Accepted formats:**
- NCBI Gene ID: a plain number, e.g., `916`
- Ensembl Gene ID: `ENSG` + 11 digits (human), `ENSMUSG` + 11 digits (mouse), etc. No version suffix (`.2`).

**How to find the ID:**

*NCBI Gene ID:*
1. Go to [ncbi.nlm.nih.gov/gene](https://www.ncbi.nlm.nih.gov/gene)
2. Search `CD3E[Gene Name] AND human[Organism]`
3. Click the correct result — the Gene ID is the number shown at the top left (e.g., `916`)

*Ensembl ID:*
1. Go to [ensembl.org](https://www.ensembl.org)
2. Search the gene name and select your species
3. The Ensembl ID (e.g., `ENSG00000198851`) is shown on the gene page

> **Tip:** If you have the NCBI Gene ID, you do not also need the Ensembl ID — one stable ID is sufficient.

---

### Cell type not found in dropdown

**What it means:** The cell type you need hasn't been added to the database yet.

**What to do:**
1. Try alternative terms (e.g., "NK cell" → search "natural killer"; "ATII cell" → search "alveolar").
2. If it is genuinely missing, use the **➕ Add a new cell type** expander in the submission form to add it yourself. You will need the cell type name and, ideally, the Cell Ontology ID from [ontobee.org/ontology/CL](http://www.ontobee.org/ontology/CL).
3. **Do not substitute a different cell type** to work around this — it corrupts the data.

---

### Duplicate entry detected

**Error message:** *"This marker already exists in the database (same organism, cell type, gene symbol, tissue, and platform)."*

**What it means:** An entry with exactly the same combination of organism + cell type + gene symbol + tissue + sequencing platform already exists. Adding an identical record would create unhelpful duplicates.

**Options:**
- **If the existing entry is correct:** No action needed — the data is already recorded.
- **If your entry adds new information** (e.g., a different tissue, different platform, or different publication reference): change one of those fields so it is distinct, and resubmit.
- **If you believe the existing entry is wrong:** Contact the database administrator (see [Contact & Escalation](#contact--escalation)) to review and correct the original entry. Do not submit a duplicate to "overwrite" it.

---

### Bulk upload CSV errors

**Error message:** *"Column headers do not match template"* or *"Row N: [specific error]"*

**Common causes and fixes:**

| Problem | Fix |
|---|---|
| Column headers were renamed or reordered | Re-download `examples/marker_submission_template.csv` and re-enter your data without changing headers |
| Extra columns were added | Remove any columns not in the original template |
| Cells contain line breaks or unusual characters | Save from Excel as plain CSV (UTF-8) before uploading |
| `gene_id` column is empty | Every row must have at least one gene ID (NCBI or Ensembl) |
| `submission_source` is a bare PMID number | Use the `PMID:NNNNN` format (e.g., `PMID:31327801`) |
| Organism name doesn't match | Use the exact organism name from the dropdown (e.g., `Human` not `Homo sapiens`) |

---

### Remote API validation times out or fails

**Symptom:** Validation is slow or fails with a network-related error even though your gene symbol looks correct.

**Quick fix:** Check the **Skip remote API validation (offline mode)** checkbox in Section 2 of the form, then click **Validate** again. The form will check only the format of your symbol and ID — no network requests will be made. If format validation passes you can proceed to submit.

> This is safe to use when you are confident in the symbol because you have already looked it up in HGNC or MGI directly.

---

## Gene Naming Discrepancies

### My lab uses a different name/spelling than what the form accepts

Labs often use informal names, protein names, or legacy symbols that differ from the current official symbol.

**Resolution steps:**

1. Look up your gene by alias in HGNC or MGI:
   - HGNC: [genenames.org/tools/search](https://www.genenames.org/tools/search/) — use the "Previous symbol" or "Alias symbol" filters
   - MGI: [informatics.jax.org/marker](https://www.informatics.jax.org/marker) — enter your name in the search box
2. The database will return the current approved symbol.
3. Use the approved symbol when submitting.

**Common examples of alias → approved symbol:**

| What your lab may call it | Official approved symbol |
|---|---|
| `B220`, `CD45` | `PTPRC` (human) / `Ptprc` (mouse) |
| `OKT3` | `CD3E` / `Cd3e` |
| `Ly6G/Ly6C` | `Ly6g` / `Ly6c1` (mouse) |
| `F4/80` | `Adgre1` (mouse) |

---

### The same gene has different entries from different labs

**Example:** Lab A submitted `CD3E` for human T cells; Lab B submitted `CD3epsilon` (an alias).

**What happens:** Both entries exist in the database but are not linked, so queries for one will not surface the other.

**Resolution:**
1. Identify which symbol is the current HGNC/MGI approved symbol.
2. Contact the database administrator to merge or correct the non-standard entry.
3. Going forward, both labs should use the approved symbol. WTCell auto-corrects capitalization but cannot detect alias substitution automatically.

---

### A gene symbol was updated in HGNC/MGI after we submitted

Gene symbols occasionally change. When this happens, previously submitted entries may carry an outdated symbol — but the NCBI Gene ID or Ensembl ID will still be correct.

**What to do:**
1. Contact the database administrator with:
   - The old symbol
   - The new approved symbol
   - The relevant Gene ID (to confirm which gene is affected)
2. The administrator can update all affected entries in bulk using the stable ID.

This is exactly why a permanent gene ID is required at submission time.

---

## Query / Search Issues

### My search returns no results

**Try these steps:**

1. **Check the organism filter** — make sure it is set to the expected organism or "(All organisms)".
2. **Check the cell type filter** — if a specific cell type is selected, try "(All cell types)".
3. **Clear the tissue text box** — a tissue filter that doesn't match any record will return zero results.
4. **Try a partial or alternate name** — type just `T cell` if a full name like `CD4+ T cell` returns nothing.
5. **The data may not have been submitted yet** — if you expect it to be there, check with the lab that should have submitted it.

---

### I see the same gene listed multiple times

This is expected when:
- The same gene was found in the same cell type from multiple tissues (e.g., lung macrophages vs. splenic macrophages)
- Multiple labs independently submitted the same marker from different publications or datasets
- The gene was identified on different sequencing platforms

Multiple records with the same gene + cell type are allowed when tissue, platform, or source differs. If you see apparent duplicates with identical metadata, report them to the database administrator.

---

## Access & Setup Problems

### The dashboard won't load

1. **Confirm Docker is running** — check Docker Desktop or run `docker ps` in a terminal.
2. **Check container status** — in the project folder, run:
   ```bash
   docker-compose ps
   ```
   Both `wtcell_db` and `wtcell_app` should show `Up`. If `wtcell_app` shows `Exit` or an error, run:
   ```bash
   docker-compose logs app
   ```
   and share the output with your bioinformatics support contact.
3. **Hard refresh the browser** — press `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac).
4. **Restart the stack:**
   ```bash
   docker-compose down
   docker-compose up --build
   ```

---

### I can't connect to the database

The dashboard sidebar shows **❌ Disconnected** instead of **✅ Connected**.

**Check these in order:**

1. Confirm a `.env` file exists in the project root and contains a value for `DB_PASSWORD`.
2. Confirm the `wtcell_db` container is running (`docker-compose ps`).
3. If you changed `DB_PASSWORD` in `.env` after the first start, the existing database volume still has the old password. To reset (⚠️ **this deletes all data** — only do this on a fresh install):
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```
4. If the problem persists, run `docker-compose logs db` and share the output with your bioinformatics support contact.

---

## Contact & Escalation

For issues not resolved by this guide:

| Issue | Who to contact |
|---|---|
| Cell type or organism missing from dropdown | Database administrator |
| Suspected duplicate or incorrect entries | Database administrator |
| Gene symbol update needed across many records | Database administrator |
| Application errors or cannot access dashboard | Bioinformatics support / IT |
| Questions about human gene nomenclature | HGNC helpdesk: [hgnc@genenames.org](mailto:hgnc@genenames.org) |
| Questions about mouse gene nomenclature | MGI helpdesk at [informatics.jax.org/contact](https://www.informatics.jax.org/contact) |

> The database administrator's contact details are displayed in the WTCell dashboard sidebar.
