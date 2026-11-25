source ~/miniconda3/bin/activate
conda activate gubbins

# gubbins --version
# 3.4.3

run_gubbins.py \
  --prefix S_hominis_filter \
  --threads 30 \
  --filter-percentage 35 \
  --iterations 5 \
  /path/to/gubbins/02_alignment/S_hominis.aln \
  > /path/to/gubbins/logs/gubbins_filter.log \
  2>&1
