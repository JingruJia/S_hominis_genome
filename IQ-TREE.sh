source ~/miniconda3/bin/activate
conda activate iqtree

# iqtree --version
# iqtree 3.1.4

iqtree \
    -s /path/to/panaroo/core_gene_alignment_filtered.aln \
    -m MFP \
    -B 1000 \
    -alrt 1000 \
    -T AUTO \
    --prefix /path/to/panaroo/preliminary_tree/S_hominis_core