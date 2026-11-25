source ~/miniconda3/bin/activate
conda activate poppunk

# poppunk --version
# 2.7.8

poppunk \
  --create-db \
  --r-files /path/to/poppunk/input/S_hominis_rfiles.txt \
  --output /path/to/poppunk/database/S_hominis \
  --k-step 4 \
  --threads 8 \
  > /path/to/poppunk/log/create_db.log \
  2>&1

poppunk \
  --fit-model lineage \
  --ref-db /path/to/poppunk/database/S_hominis \
  --output /path/to/poppunk/lineage/S_hominis_lineages \
  --ranks 1,2,3 \
  --threads 1 \
  > /path/to/poppunk/log/lineage.log \
  2>&1
