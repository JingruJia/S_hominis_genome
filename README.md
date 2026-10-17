# The population genomic structure and functional diversity of *Staphylococcus hominins*

## Overview

This repository contains the scripts and parameter settings used for the population genomic analysis of human skin-associated *Staphylococcus hominis*. The workflow covers genome collection, quality control, dereplication, annotation, phylogenomics, pan-genome analysis, functional annotation, and screening of virulence- and resistance-associated genes.

## Dataset

A total of 446 publicly available *S. hominis* genomes were retrieved from NCBI. Filtering for human host and skin-associated isolation sources retained 114 genomes. CheckM quality control retained 111 genomes, and dRep dereplication produced a final dataset of 71 non-redundant genomes.

## Software

- CheckM v1.2.5
- dRep v3.6.2
- Prokka v1.14.6
- Panaroo v1.8.0
- Gubbins v3.4.3
- IQ-TREE v3.1.4
- FastANI v1.34
- eggNOG-mapper
- Resistance Gene Identifier and CARD
- Virulence Factor Database
- R v4.6.0

The version information of the relevant tools used in the analysis is recorded in the repository environment configuration.

## Workflow

### 1. Genome collection and source filtering

Genomes and metadata were downloaded from NCBI. Only genomes derived from human hosts and annotated as skin or skin-associated sources were retained.

### 2. Genome quality control

Genome quality was assessed using CheckM. Genomes were retained when completeness was at least 95% and contamination did not exceed 5%.

### 3. Genome dereplication

dRep was used to remove near-identical genomes at a 99.9% ANI threshold. This threshold was used for dereplication and not for taxonomic delimitation.

### 4. Genome annotation

The non-redundant genomes were annotated using Prokka with default settings. The resulting annotations were used in subsequent pan-genome and functional analyses.

### 5. Phylogenomic and ANI analyses

Putative recombination regions in the core-genome alignment were identified and masked using Gubbins. A maximum-likelihood phylogeny was reconstructed using IQ-TREE with ModelFinder, 1,000 ultrafast bootstrap replicates and 1,000 SH-aLRT replicates. Pairwise ANI values were calculated using FastANI. The conventional 95% ANI threshold was used only as a reference for species-level relatedness.

### 6. Pan-genome analysis

The pan-genome was constructed using Panaroo. Genes were classified as core, soft-core, shell or cloud according to their frequencies across genomes. Heap’s law and the rate of new-gene discovery were fitted to evaluate pan-genome openness.

### 7. Functional annotation

Gene functions were annotated using eggNOG and grouped into COG categories. 

### 8. Virulence-associated gene screening

The genomes were screened against the VFDB core dataset. The resulting presence/absence profiles describe the predicted distribution of virulence-associated genes.

### 9. Resistome screening

Resistance-associated genes were identified using RGI and CARD. The analysis describes the presence and distribution of predicted resistance-associated genes.

### 10. Statistical analysis and visualization

Statistical analyses and figure generation were performed in R. The scripts are organized in the repository, and shared paths, thread numbers and database locations are defined in the configuration files.

## Repository contents

The repository contains:

- analysis scripts arranged in execution order;
- environment dependencies and software versions;
- parameter and database configurations;
- genome accession and sample metadata;
- intermediate and final analysis results;
- source data and scripts for main and supplementary figures.

Large result files, supplementary tables and supplementary figures are provided in the corresponding repository directories or with the article supplementary materials.

## Reproducibility

The complete workflow can be reproduced by configuring the software environment and running the numbered scripts sequentially. Software versions, database releases, key parameters, execution order and output descriptions are retained in the repository to support reproducibility of the core analyses.
