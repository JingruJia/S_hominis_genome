#!/usr/bin/env bash
source ~/miniconda3/bin/activate
conda activate blastp

# blastp --version
# 2.12.0

CARD_JSON="/path/to/VFDB_db/VFDB_setB"
INPUT_DIR="/path/to/faa999"
OUTPUT_DIR="/path/to/vf_result"

blastp -query "$faa" \
      -db "${CARD_JSON}" \
      -out "${OUTPUT_DIR}/${sample_name}_vfdb.blast" \
      -evalue 1e-5 \
      -num_threads 2 \
      -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen stitle"
    echo "Done $sample_name"