# WTCell Glossary

**Plain-language definitions of technical terms used in WTCell.**

You do not need to understand all of these terms to use the database — the submission form guides you through every field. This glossary is here if you want to understand *why* a term or format is required.

---

## A

### Alias (cell type)
An alternative name for a cell type. For example, "NK cell" is an alias for "Natural killer cell". WTCell stores aliases so searches using informal names still return results.

### API Validation (Online Mode)
When the **Skip remote API validation** checkbox is *unchecked* (the default), WTCell contacts external databases to verify your gene symbol:
- **Human (HGNC)** → checks the [HGNC REST API](https://www.genenames.org/tools/rest/) (`rest.genenames.org`)
- **Mouse (MGI)** → checks [MyGene.info](https://mygene.info/) (mouse taxon 10090)

These checks time out after 8 seconds and fail gracefully — if the external service is unreachable, the submission proceeds with a warning. If you are working without internet access, enable **Offline Mode** (see below).

---

## C

### Cell Ontology (CL)
A standardized vocabulary of cell type names maintained by the [OBO Foundry](https://obofoundry.org/ontology/cl.html). Using Cell Ontology terms ensures that "T cell" entered by one lab means exactly the same thing as "T cell" entered by another, enabling cross-database and cross-lab compatibility.

**Cell Ontology ID format:** `CL:XXXXXXX` (seven digits)  
**Example:** T cell = `CL:0000084`  
**Look it up:** [ontobee.org/ontology/CL](http://www.ontobee.org/ontology/CL)

---

## E

### Ensembl ID
A stable, unique identifier assigned to each gene by the [Ensembl genome browser](https://www.ensembl.org). Unlike gene symbols, Ensembl IDs never change — even if the official symbol is later updated.

| Organism | Format | Example |
|---|---|---|
| Human | `ENSG` + 11 digits | `ENSG00000198851` |
| Mouse | `ENSMUSG` + 11 digits | `ENSMUSG00000032530` |
| Zebrafish | `ENSDARG` + 11 digits | `ENSDARG00000002769` |

> ⚠️ Do not include a version suffix (e.g., `.2`). WTCell requires the bare accession only.

**Look it up:** Search [ensembl.org](https://www.ensembl.org) by gene name and organism.

---

## F

### FlyBase
The nomenclature authority for *Drosophila melanogaster* (Fruit Fly) genes. WTCell stores Fruit Fly gene symbols exactly as entered — no automatic reformatting is applied.

**Website:** [flybase.org](https://flybase.org/)

---

## G

### Gene ID (NCBI)
A stable, unique integer identifier assigned to each gene by the [NCBI Gene database](https://www.ncbi.nlm.nih.gov/gene). NCBI Gene IDs do not change over time, even if the gene symbol is updated.

**Format:** A plain number (no prefix)  
**Example:** Human CD3E = `916`  
**Look it up:** [ncbi.nlm.nih.gov/gene](https://www.ncbi.nlm.nih.gov/gene) — search by gene name, filter by organism.

### Gene Symbol
A short, standardized abbreviation for a gene. Gene symbols are assigned and maintained by official nomenclature authorities. They are case-sensitive for some organisms:
- Human `CD3E` and mouse `Cd3e` refer to the same biological gene in different species.
- Entering the wrong case for human or mouse will be auto-corrected, but entering the wrong organism will produce an incorrect result.

---

## H

### HGNC (HUGO Gene Nomenclature Committee)
The international authority responsible for approving and maintaining standardized names and symbols for **human** genes. HGNC requires that human gene symbols be written in **all uppercase** letters (e.g., `EPCAM`, `PTPRC`, `CD3E`).

**Website:** [genenames.org](https://www.genenames.org/)  
**Use it to:** Verify the correct spelling and capitalization of a human gene symbol, or look up the approved symbol for a gene you know by an alias.

---

## M

### Marker Gene
A gene whose expression level reliably distinguishes one cell type from another in single-cell RNA sequencing data. For example, `CD3E` is expressed in T cells but not in B cells.

### MGI (Mouse Genome Informatics)
The authoritative database for mouse genetics, maintained by The Jackson Laboratory. MGI requires that mouse gene symbols follow **title-case** capitalization: first letter uppercase, remaining letters lowercase (e.g., `Cd3e`, `Trp53`, `Ptprc`).

**Website:** [informatics.jax.org](https://www.informatics.jax.org/)  
**Use it to:** Verify the correct spelling and capitalization of a mouse gene symbol.

---

## N

### NCBI Taxonomy ID
A unique number assigned to every species by the National Center for Biotechnology Information (NCBI). Used to unambiguously identify an organism.

**Examples:**
- Human (*Homo sapiens*): `9606`
- Mouse (*Mus musculus*): `10090`
- Zebrafish (*Danio rerio*): `7955`
- Rat (*Rattus norvegicus*): `10116`
- Fruit Fly (*Drosophila melanogaster*): `7227`
- Nematode (*C. elegans*): `6239`

**Look it up:** [ncbi.nlm.nih.gov/taxonomy](https://www.ncbi.nlm.nih.gov/taxonomy)

### Nomenclature Authority
The organization responsible for maintaining official gene names for a species.

| Organism | Authority | Website |
|---|---|---|
| Human | HGNC | [genenames.org](https://www.genenames.org/) |
| Mouse | MGI | [informatics.jax.org](https://www.informatics.jax.org/) |
| Zebrafish | ZFIN | [zfin.org](https://zfin.org/) |
| Rat | RGD | [rgd.mcw.edu](https://rgd.mcw.edu/) |
| Fruit Fly | FlyBase | [flybase.org](https://flybase.org/) |
| Nematode | WormBase | [wormbase.org](https://wormbase.org/) |

---

## O

### Offline Mode
When the **Skip remote API validation** checkbox is checked in the submission form, WTCell skips the live HGNC and MyGene.info lookups and validates only the format of your gene symbol and ID. Use this when working without internet access. The gene symbol will still be auto-corrected to the right case, but its existence in the official database will not be confirmed.

### Organism
The species from which the marker data was derived. WTCell pre-loads six organisms: Human, Mouse, Zebrafish, Rat, Fruit Fly, and Nematode. Additional organisms can be added by the database administrator.

---

## P

### PMID (PubMed ID)
A unique number assigned to each publication indexed in [PubMed](https://pubmed.ncbi.nlm.nih.gov/). Used in WTCell as a reference for published marker data.

**Format in WTCell:** Use the `PMID:` prefix, e.g., `PMID:31327801`  
**Find it:** Search for your paper at [pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov) — the PMID is shown below the article title.

---

## R

### RGD (Rat Genome Database)
The nomenclature authority for *Rattus norvegicus* (Rat) genes. WTCell stores Rat gene symbols exactly as entered.

**Website:** [rgd.mcw.edu](https://rgd.mcw.edu/)

---

## S

### scRNA-seq (Single-Cell RNA Sequencing)
A laboratory technique that measures gene expression in individual cells, allowing researchers to identify distinct cell types within a mixed population (e.g., a tissue biopsy or blood sample).

### Sequencing Platform
The specific technology and protocol used to perform scRNA-seq. Different platforms have different sensitivity and gene detection rates, which can affect which markers are most informative.

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
An anatomy ontology that provides standardized names for tissues, organs, and anatomical structures across species. Using Uberon terms enables cross-species and cross-lab comparisons.

**Website:** [uberon.github.io](https://uberon.github.io/)  
**Look it up:** [ontobee.org/ontology/UBERON](http://www.ontobee.org/ontology/UBERON)

**Common Uberon tissue terms used in WTCell:**

| Common name | Uberon term / free text |
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

---

## W

### WormBase
The nomenclature authority for *Caenorhabditis elegans* (Nematode) genes. WTCell stores Nematode gene symbols exactly as entered.

**Website:** [wormbase.org](https://wormbase.org/)

---

## Z

### ZFIN (Zebrafish Information Network)
The nomenclature authority for *Danio rerio* (Zebrafish) genes. WTCell stores Zebrafish gene symbols exactly as entered — no automatic reformatting is applied.

**Website:** [zfin.org](https://zfin.org/)
