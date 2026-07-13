-- =============================================================================
-- WTCell: Centralized Multi-Organism Cell Type Annotation Database
-- Schema Initialization Script
-- =============================================================================
-- This script creates the full relational schema for WTCell.
-- It decouples the biological concept of a cell type (universal) from the
-- species-specific gene nomenclature, preventing data duplication and
-- nomenclature discrepancies across organisms.
--
-- Usage:
--   psql -U <user> -d <database> -f schema.sql
-- =============================================================================

-- Drop tables in reverse dependency order to allow clean re-initialization.
DROP TABLE IF EXISTS markers   CASCADE;
DROP TABLE IF EXISTS cell_types CASCADE;
DROP TABLE IF EXISTS organisms  CASCADE;

-- =============================================================================
-- Table: organisms
-- Tracks each species tracked in the database, including its nomenclature
-- authority so that downstream validation logic knows which rules to apply.
-- =============================================================================
CREATE TABLE organisms (
    -- Surrogate primary key — auto-incrementing integer.
    organism_id          SERIAL      PRIMARY KEY,

    -- Human-readable common name (e.g. "Human", "Mouse").
    common_name          VARCHAR(100) NOT NULL,

    -- Full Linnaean scientific name (e.g. "Homo sapiens").
    -- Must be unique to prevent duplicate organism records.
    scientific_name      VARCHAR(200) NOT NULL UNIQUE,

    -- NCBI Taxonomy database identifier (https://www.ncbi.nlm.nih.gov/taxonomy).
    -- Used for programmatic lookups and cross-referencing external databases.
    ncbi_taxon_id        INTEGER     NOT NULL UNIQUE,

    -- The primary gene nomenclature authority for this organism.
    -- Examples: 'HGNC' (human), 'MGI' (mouse), 'ZFIN' (zebrafish), 'FlyBase' (fly).
    -- This field drives the validation rules applied during marker submission.
    nomenclature_authority VARCHAR(50) NOT NULL
);

COMMENT ON TABLE organisms IS
    'Master list of organisms tracked by WTCell. Each organism record anchors '
    'the nomenclature authority used for gene symbol validation.';

-- =============================================================================
-- Table: cell_types
-- Captures the universal, species-agnostic biological concept of a cell type.
-- Decoupling cell type identity from species-specific genes is the core design
-- principle that prevents data duplication and cross-species naming conflicts.
-- =============================================================================
CREATE TABLE cell_types (
    -- Surrogate primary key.
    cell_type_id        SERIAL      PRIMARY KEY,

    -- The canonical, standardized name for this cell type (e.g. "T cell").
    -- Must be unique; used as the primary human-readable identifier.
    standardized_name   VARCHAR(200) NOT NULL UNIQUE,

    -- Cell Ontology (CL) accession identifier (https://obofoundry.org/ontology/cl.html).
    -- Format: CL:XXXXXXX (seven digits).  May be NULL if not yet mapped.
    cell_ontology_id    VARCHAR(20)  CHECK (
                            cell_ontology_id IS NULL
                            OR cell_ontology_id ~ '^CL:[0-9]{7}$'
                        ),

    -- Comma-separated list of alternative names / synonyms for this cell type
    -- (e.g. "T lymphocyte,T-cell,CD3+ cell").  Stored as free text to keep the
    -- schema simple; full-text search can be applied at query time.
    aliases             TEXT
);

COMMENT ON TABLE cell_types IS
    'Species-independent master list of cell types, keyed to the Cell Ontology. '
    'One record here represents the biological concept shared across all organisms.';

-- =============================================================================
-- Table: markers
-- The core repository table.  Each row records a single gene that has been
-- experimentally validated (or literature-supported) as a marker for a given
-- cell type in a given organism, under specific experimental conditions.
-- =============================================================================
CREATE TABLE markers (
    -- Surrogate primary key.
    marker_id           SERIAL      PRIMARY KEY,

    -- FK → organisms.organism_id.
    -- ON DELETE CASCADE: removing an organism also removes all its markers.
    organism_id         INTEGER     NOT NULL
                            REFERENCES organisms(organism_id) ON DELETE CASCADE,

    -- FK → cell_types.cell_type_id.
    -- ON DELETE CASCADE: removing a cell type definition removes its marker records.
    cell_type_id        INTEGER     NOT NULL
                            REFERENCES cell_types(cell_type_id) ON DELETE CASCADE,

    -- Official gene symbol as enforced by the organism's nomenclature authority.
    -- For human (HGNC): ALL UPPERCASE (e.g. "CD3E").
    -- For mouse (MGI):  First-letter-uppercase only (e.g. "Cd3e").
    gene_symbol         VARCHAR(100) NOT NULL,

    -- Stable, permanent gene identifier.  Either:
    --   • NCBI Gene ID  — numeric string (e.g. "916")
    --   • Ensembl Gene ID — format ENSG00000000000 or ENSMUSG00000000000
    -- A permanent ID is REQUIRED to maintain a reliable source of truth even
    -- if the gene symbol is later updated by the nomenclature authority.
    gene_id             VARCHAR(50)  NOT NULL
                            CHECK (
                                gene_id ~ '^\d+$'                   -- NCBI Gene ID (numeric)
                                OR gene_id ~ '^ENS[A-Z]*G\d{11}$'  -- Ensembl Gene ID
                            ),

    -- Tissue / anatomical context described using UBERON ontology terms.
    -- Format example: "UBERON:0002106" (spleen).  Free text is also accepted.
    tissue              VARCHAR(200),

    -- Sequencing platform used to generate the data (e.g. "10x Chromium v3",
    -- "Smart-seq2", "Drop-seq").
    platform            VARCHAR(200),

    -- Source reference: a PubMed ID (PMID), DOI, or internal dataset identifier
    -- (e.g. "PMID:31327801", "doi:10.1038/s41586-020-2277-x", "LAB_DATASET_001").
    submission_source   VARCHAR(200),

    -- Email address of the researcher who submitted this marker record.
    -- Used for provenance tracking and follow-up queries.
    submitter_email     VARCHAR(254) NOT NULL
                            CHECK (submitter_email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),

    -- Date the record was written to the database.
    -- Defaults to the current date; can be overridden for bulk imports.
    date_submitted      DATE        NOT NULL DEFAULT CURRENT_DATE,

    -- Prevent exact duplicate submissions (same gene in the same organism /
    -- cell-type / tissue / platform combination).
    UNIQUE (organism_id, cell_type_id, gene_symbol, tissue, platform)
);

COMMENT ON TABLE markers IS
    'Species-specific gene marker records.  Each row links a validated gene '
    'symbol (and its stable ID) to a universal cell type for a particular '
    'organism, tissue context, and experimental platform.';

-- =============================================================================
-- Indexes — improve filter performance on the most common query patterns.
-- =============================================================================

-- Filtering markers by organism (very common in the query dashboard).
CREATE INDEX idx_markers_organism  ON markers(organism_id);

-- Filtering markers by cell type.
CREATE INDEX idx_markers_cell_type ON markers(cell_type_id);

-- Searching markers by gene symbol (partial match via ILIKE is also useful).
CREATE INDEX idx_markers_gene_symbol ON markers(gene_symbol);

-- Searching by tissue context.
CREATE INDEX idx_markers_tissue ON markers(tissue);

-- =============================================================================
-- Seed Data — common organisms and a handful of canonical cell types so that
-- the application is immediately useful after initialization.
-- =============================================================================

-- Organisms ----------------------------------------------------------------
INSERT INTO organisms (common_name, scientific_name, ncbi_taxon_id, nomenclature_authority)
VALUES
    ('Human',     'Homo sapiens',          9606,  'HGNC'),
    ('Mouse',     'Mus musculus',          10090, 'MGI'),
    ('Zebrafish', 'Danio rerio',           7955,  'ZFIN'),
    ('Rat',       'Rattus norvegicus',     10116, 'RGD'),
    ('Fruit fly', 'Drosophila melanogaster', 7227, 'FlyBase'),
    ('Nematode',  'Caenorhabditis elegans', 6239, 'WormBase');

-- Cell Types ---------------------------------------------------------------
INSERT INTO cell_types (standardized_name, cell_ontology_id, aliases)
VALUES
    ('T cell',               'CL:0000084', 'T lymphocyte,T-cell,CD3+ cell'),
    ('B cell',               'CL:0000236', 'B lymphocyte,B-cell,CD19+ cell'),
    ('Natural killer cell',  'CL:0000623', 'NK cell'),
    ('Macrophage',           'CL:0000235', 'tissue macrophage'),
    ('Dendritic cell',       'CL:0000451', 'DC'),
    ('Monocyte',             'CL:0000576', NULL),
    ('Neutrophil',           'CL:0000775', NULL),
    ('Erythrocyte',          'CL:0000232', 'red blood cell,RBC'),
    ('Platelet',             'CL:0000233', 'thrombocyte'),
    ('Hepatocyte',           'CL:0000182', 'liver parenchymal cell'),
    ('Neuron',               'CL:0000540', 'nerve cell'),
    ('Astrocyte',            'CL:0000127', NULL),
    ('Oligodendrocyte',      'CL:0000128', NULL),
    ('Endothelial cell',     'CL:0000115', NULL),
    ('Fibroblast',           'CL:0000057', NULL),
    ('Epithelial cell',      'CL:0000066', NULL),
    ('Stem cell',            'CL:0000034', 'progenitor cell'),
    ('Plasma cell',          'CL:0000786', 'antibody-secreting cell'),
    ('Mast cell',            'CL:0000097', NULL),
    ('Eosinophil',           'CL:0000771', NULL);

-- =============================================================================
-- End of schema.sql
-- =============================================================================
