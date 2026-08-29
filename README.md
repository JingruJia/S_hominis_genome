
```markdown
# Genome analysis scripts and output files

This repository provides the scripts and selected output files used for comparative genomic analysis in this study.

## dRep

`dRep/dRep.sh` was used to dereplicate genome assemblies and define representative genomes based on genome quality and average nucleotide identity thresholds. The `dRep/` directory contains the resulting clustering tables, genome quality summaries, and visualization files.

## Roary

`Roary.sh` was used for pan-genome analysis of annotated genomes. The `Roary/` directory includes gene presence/absence matrices, core genome alignment files, accessory genome tables, and pan-genome summary statistics.

## FastANI

`FastANI.sh` was used to calculate pairwise average nucleotide identity among genomes and generate an ANI matrix for genome-level comparison.

## VFDB

`VF.sh` was used to identify putative virulence factor genes by protein-level similarity searches against the VFDB database, followed by filtering based on sequence identity, coverage, and e-value.

## RGI

`RGI.sh` was used to annotate antimicrobial resistance genes with RGI and the CARD database. High-confidence hits classified as Perfect or Strict were retained for downstream analysis.
```
