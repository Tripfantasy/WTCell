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

**What it means:** The gene symbol you entered either doesn't exist in the official nomenclature database for your selected organism, or the capitalization does not match after auto-correction.

**Steps to resolve:**
1. Double-check the organism selection — are you sure you're submitting human (not mouse) data?
2. Look up the correct official symbol:
   - Human: [genenames.org](https://www.genenames.org/)
   - Mouse: [informatics.jax.org](https://www.informatics.jax.org/)
3. Watch for common mistakes:
   - Using a gene *alias* instead of the *approved symbol* (e.g., `OKT3` instead of `CD3E`)
   - Using a protein name instead of a gene name (e.g., `CD45` instead of `PTPRC`)
   - Including a hyphen or number suffix that shouldn't be there (e.g., `CD3-E` instead of `CD3E`)

---

### Invalid or missing Gene ID

**Error message:** *"A valid NCBI Gene ID or Ensembl ID is required"*

**What it means:** The submission form requires at least one stable gene identifier so the entry can always be traced to the correct gene.

**How to find the ID:**

*NCBI Gene ID (quickest):*
1. Go to [ncbi.nlm.nih.gov/gene](https://www.ncbi.nlm.nih.gov/gene)
2. Search `CD3E[Gene Name] AND human[Organism]` (or mouse)
3. Click the correct result — the Gene ID is the number shown at the top left (e.g., `916`)

*Ensembl ID:*
1. Go to [ensembl.org](https://www.ensembl.org)
2. Search the gene name and select your species
3. The Ensembl ID (e.g., `ENSG00000198851`) appears on the gene page

> **Tip:** If you have the gene symbol and NCBI Gene ID, you do not also need the Ensembl ID — one stable ID is sufficient.

---

### Cell type not found in dropdown

**What it means:** The cell type you need hasn't been added to the database yet.

**What to do:**
1. Try searching with alternative terms (e.g., "NK cell" instead of "natural killer cell", or vice versa).
2. If it's genuinely missing, contact the database administrator (see [Contact & Escalation](#contact--escalation)) with:
   - The cell type name you need
   - The Cell Ontology ID if you can find it at [ontobee.org/ontology/CL](http://www.ontobee.org/ontology/CL)
3. **Do not substitute a different cell type** to work around this — it will corrupt the data.

---

### Duplicate entry detected

**What it means:** A submission with the same gene symbol, organism, cell type, and tissue already exists in the database.

**Options:**
- **If the existing entry is correct:** No action needed — the data is already recorded.
- **If your entry adds new information** (e.g., a different reference or platform): Confirm the submission; both entries will be kept with their respective sources.
- **If you believe the existing entry is wrong:** Do not submit a duplicate to "overwrite" it. Contact the database administrator to review and correct the original entry.

---

### Bulk upload CSV errors

**Error message:** *"Column headers do not match template"* or *"Row N: [specific error]"*

**Common causes and fixes:**

| Problem | Fix |
|---|---|
| Column headers were renamed or reordered | Re-download `examples/marker_submission_template.csv` and re-enter your data without changing headers |
| Extra columns were added | Remove any columns not in the original template |
| Cells contain line breaks or unusual characters | Check for copy-paste issues from Excel — save as plain CSV (UTF-8) before uploading |
| Gene ID column is empty | Every row must have at least one gene ID (NCBI or Ensembl) |
| Organism name doesn't match | Use the exact organism name from the dropdown (e.g., `Human` not `Homo sapiens` or `human`) |

---

## Gene Naming Discrepancies

### My lab uses a different name/spelling than what the form accepts

This is one of the most common issues. Labs often use informal gene names, protein names, or legacy symbols that differ from the current official symbol.

**Resolution steps:**
1. Look up your gene by searching the alias in HGNC or MGI:
   - HGNC alias search: [genenames.org/tools/search](https://www.genenames.org/tools/search/) — use "Previous symbol" or "Alias symbol" filters
   - MGI alias search: [informatics.jax.org/marker](https://www.informatics.jax.org/marker) — enter your name in the search box
2. The database will return the current approved symbol.
3. Use the approved symbol for your submission. If you want the alias preserved for searchability, you can note it in a comment field.

**Example:**
- Your lab calls it `B220` → official approved symbol is `PTPRC` (human) / `Ptprc` (mouse)
- Your lab calls it `CD45` → same gene: `PTPRC` / `Ptprc`

---

### The same gene has different entries from different labs

**Example:** Lab A submitted `CD3E` for human T cells; Lab B submitted `CD3` (an alias).

**What happens:** Both entries are stored, but the query dashboard will surface them separately if the symbols differ.

**Resolution:**
1. Identify which symbol is the current HGNC/MGI approved symbol using the databases above.
2. Contact the database administrator to merge or correct the non-standard entry.
3. Going forward, both labs should use the approved symbol — WTCell auto-corrects capitalization but cannot correct wrong symbols automatically.

---

### A gene symbol was updated in HGNC/MGI after we submitted

Gene symbols occasionally change. When this happens, previously submitted entries may have an outdated symbol, but the NCBI Gene ID or Ensembl ID will still be correct.

**What to do:**
1. Contact the database administrator with the old symbol, new symbol, and the relevant Gene ID.
2. The administrator can update all affected entries in bulk.
3. The stable Gene ID field is exactly why it's required — it makes bulk corrections like this possible.

---

## Query / Search Issues

### My search returns no results

**Try these steps:**

1. **Check the organism filter** — make sure it is set to the organism you expect (or "All organisms").
2. **Try a partial search** — type just part of the cell type name in case of slight wording differences.
3. **Check the gene symbol format** — search is case-insensitive, but spelling must be correct (e.g., `CD3E` not `CD3-E`).
4. **Check the tissue filter** — if a tissue filter is active, results will only show markers from that tissue.
5. **The data may not have been submitted yet** — if you believe it should be there, contact the lab that would have submitted it.

---

### I see the same gene listed multiple times

This is expected behavior if:
- The same gene was found in the same cell type from multiple tissues (e.g., lung macrophages and splenic macrophages)
- Multiple labs independently submitted the same marker with different reference PMIDs
- The gene was identified on different sequencing platforms

Multiple entries for the same gene + cell type combination are allowed when the context (tissue, platform, or source) differs. If you see apparent duplicates with identical metadata, report them to the database administrator.

---

## Access & Setup Problems

### The dashboard won't load

1. Confirm Docker is running (check Docker Desktop or `docker ps` in a terminal).
2. Check that the containers are up: in a terminal, run `docker-compose ps` in the project folder. Both the `db` and `app` services should show `Up`.
3. Try a hard refresh in your browser (Ctrl+Shift+R / Cmd+Shift+R).
4. If the app container shows an error, run `docker-compose logs app` to see the error message and share it with your bioinformatics support contact.

---

### I can't connect to the database

1. Make sure you have a `.env` file in the project root (copied from `.env.example` with a password filled in).
2. Confirm the `db` container is running (`docker-compose ps`).
3. If you changed the password in `.env` after the database was first created, you may need to reset the volume: run `docker-compose down -v` then `docker-compose up -d` (⚠️ this deletes all data — only do this on a fresh install).

---

## Contact & Escalation

For issues not resolved by this guide:

| Issue | Who to contact |
|---|---|
| Cannot find a cell type or organism in the dropdown | Database administrator |
| Suspected duplicate or incorrect entries | Database administrator |
| Gene symbol update needed across many records | Database administrator |
| Application errors, cannot access dashboard | Bioinformatics support / IT |
| Questions about gene nomenclature | HGNC helpdesk: [hgnc@genenames.org](mailto:hgnc@genenames.org) |

> The database administrator's email address is displayed on the WTCell dashboard homepage.
