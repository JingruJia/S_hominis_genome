roary -p 16 -e -n -v -f /path/to/roary_output /path/to/prokka_gff/*.gff
fasttree -nt /path/to/roary_output/core_gene_alignment.aln > /path/to/roary_output/core_gene_alignment.nwk