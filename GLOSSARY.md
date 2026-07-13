# WTCell Glossary

**Plain-language definitions of technical terms used in WTCell.**

You do not need to understand all of these terms to use the database — the submission form guides you through every field. This glossary is here if you want to understand *why* a term or format is required.

---

## A

### Alias (cell type)
An alternative name for a cell type. For example, "NK cell" is an alias for "natural killer cell". WTCell stores aliases so searches using informal names still return results.

---

## C

### Cell Ontology (CL)
A standardized vocabulary of cell type names maintained by the [OBO Foundry](https://obofoundry.org/ontology/cl.html). Using Cell Ontology terms ensures that "T cell" entered by one lab means exactly the same thing as "T cell" entered by another, and enables cross-database compatibility.

**Cell Ontology ID format:** `CL:XXXXXXX` (seven digits)  
**Example:** T cell = `CL:0000084`  
**Look it up:** [ontobee.org/ontology/CL](http://www.ontobee.org/ontology/CL)

---

## E

### Ensembl ID
A stable, unique identifier assigned to each gene by the [Ensembl genome browser](https://www.ensembl.org). Unlike gene symbols, Ensembl IDs never change — even if the official symbol is updated.

| Organism | Format | Example |
|---|---|---|
| Human | Starts with `ENSG` followed by 11 digits | `ENSG00000198851` |
| Mouse | Starts with `ENSMUSG` followed by 11 digits | `ENSMUSG00000032530` |

**Look it up:** Search [ensembl.org](https://www.ensembl.org) by gene name and organism.

---

## G

### Gene Symbol
A short, standardized abbreviation for a gene. Gene symbols are assigned and maintained by official nomenclature authorities (HGNC for human, MGI for mouse). They are case-sensitive — `CD3E` (human) and `Cd3e` (mouse) are the same gene in different organisms.

### Gene ID (NCBI)
A stable, unique integer identifier assigned to each gene by the [NCBI Gene database](https://www.ncbi.nlm.nih.gov/gene). Like Ensembl IDs, NCBI Gene IDs do not change over time.

**Format:** A plain number (no prefix)  
**Example:** Human CD3E = `916`  
**Look it up:** [ncbi.nlm.nih.gov/gene](https://www.ncbi.nlm.nih.gov/gene) — search gene name, filter by organism.

---

## H

### HGNC (HUGO Gene Nomenclature Committee)
The international authority responsible for approving and maintaining standardized names and symbols for human genes. HGNC requires that human gene symbols be written in **all uppercase** letters (e.g., `EPCAM`, `PTPRC`).

**Website:** [genenames.org](https://www.genenames.org/)  
**Use it to:** Verify the correct spelling and capitalization of a human gene symbol.

---

## M

### Marker Gene
A gene whose expression level reliably distinguishes one cell type from another in single-cell RNA sequencing data. For example, `CD3E` is expressed in T cells but not in B cells.

### MGI (Mouse Genome Informatics)
The authoritative database for mouse genetics, maintained by The Jackson Laboratory. MGI requires that mouse gene symbols follow **title-case** capitalization: first letter uppercase, remaining letters lowercase (e.g., `Epcam`, `Ptprc`, `Cd3e`).

**Website:** [informatics.jax.org](https://www.informatics.jax.org/)  
**Use it to:** Verify the correct spelling and capitalization of a mouse gene symbol.

---

## N

### NCBI Taxonomy ID
A unique number assigned to every species by the National Center for Biotechnology Information (NCBI). Used to unambiguously identify an organism.

**Examples:**
- Human (*Homo sapiens*): `9606`
- Mouse (*Mus musculus*): `10090`

**Look it up:** [ncbi.nlm.nih.gov/taxonomy](https://www.ncbi.nlm.nih.gov/taxonomy)

### Nomenclature Authority
The organization responsible for maintaining official gene names for a species. The two most relevant for WTCell users are HGNC (human) and MGI (mouse).

---

## O

### Organism
The species from which the marker data was derived. WTCell currently supports human and mouse, with additional organisms available on request.

---

## P

### PMID (PubMed ID)
A unique number assigned to each publication indexed in the [PubMed](https://pubmed.ncbi.nlm.nih.gov/) database. Used in WTCell as a reference for published marker data.

**Format:** A plain number (no prefix)  
**Example:** `32214231`  
**Find it:** Search for your paper at [pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov) — the PMID is shown below the article title.

---

## S

### scRNA-seq (Single-Cell RNA Sequencing)
A laboratory technique that measures gene expression in individual cells, allowing researchers to identify distinct cell types within a mixed population (e.g., a tissue biopsy or blood sample).

### Sequencing Platform
The specific technology and protocol used to perform scRNA-seq. Different platforms have different sensitivity levels and gene detection rates, which can affect which markers are most informative.

**Common platforms:**
- `10x Chromium v3` / `10x Chromium v2` — droplet-based, high cell throughput
- `Smart-seq2` — plate-based, higher sensitivity per cell
- `Drop-seq` — droplet-based
- `inDrop` — droplet-based

---

## T

### Tissue / Anatomical Context
The organ or tissue type from which cells were collected. WTCell uses terms from the [Uberon anatomy ontology](#uberon) to keep tissue names consistent across submissions.

---

## U

### Uberon
An anatomy ontology that provides standardized names for tissues, organs, and anatomical structures across species. Using Uberon terms ensures that "lung" entered by one lab is comparable with "lung" entered by another, and that cross-species comparisons are possible.

**Website:** [uberon.github.io](https://uberon.github.io/)  
**Look it up:** [ontobee.org/ontology/UBERON](http://www.ontobee.org/ontology/UBERON)

**Common Uberon tissue terms used in WTCell:**

| Common name | Uberon term |
|---|---|
| Blood / peripheral blood | `peripheral blood` |
| Bone marrow | `bone marrow` |
| Lymph node | `lymph node` |
| Spleen | `spleen` |
| Lung | `lung` |
| Liver | `liver` |
| Colon / large intestine | `large intestine` |
| Small intestine | `small intestine` |
| Skin | `skin of body` |
| Brain | `brain` |
| Kidney | `kidney` |
