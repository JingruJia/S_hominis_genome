source ~/miniconda3/bin/activate
conda activate panaroo

# panaroo --version
# panaroo 1.8.0

panaroo \
  -i /path/to/gff/*.gff \
  -o /path/to/panaroo \
  --clean-mode strict \
  -a core \
  --aligner mafft \
  --core_threshold 0.95 \
  -t 30