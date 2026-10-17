#!/usr/bin/env bash
CARD_JSON="/path/to/VFDB_db/VFDB_setB"
INPUT_DIR="/path/to/faa999"
OUTPUT_DIR="/path/to/vf_result"

mkdir -p "${OUTPUT_DIR}"

max_jobs=2

for faa in "${INPUT_DIR}"/*.faa; do
  sample_name=$(basename "$faa" .faa)

  (
    echo "Start $sample_name"
    blastp -query "$faa" \
      -db "${CARD_JSON}" \
      -out "${OUTPUT_DIR}/${sample_name}_vfdb.blast" \
      -evalue 1e-5 \
      -num_threads 2 \
      -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen stitle"
    echo "Done $sample_name"
  ) &

  while [[ $(jobs -r | wc -l) -ge $max_jobs ]]; do
    sleep 1
  done
done

wait

awk '{file=FILENAME; sub(/.*\//, "", file); sub(/_vfdb\.blast$/, "", file); print $0 "\t" file}' "${OUTPUT_DIR}"/*.blast > "${OUTPUT_DIR}/vf_result.blast"

echo -e "query_id\tsubject_id\tidentity\talignment_length\tmismatches\tgap_openings\tquery_start\tquery_end\tsubject_start\tsubject_end\tevalue\tbit_score\tquery_length\tsubject_title\tGCF_ID" | cat - "${OUTPUT_DIR}/vf_result.blast" > "${OUTPUT_DIR}/vf_result_with_header.blast"

cp "${OUTPUT_DIR}/vf_result_with_header.blast" "${OUTPUT_DIR}/vf_result_with_header.tsv"

awk -F'\t' 'NR==1 || ($11 < 1e-5 && $3 > 60 && ($8 - $7 + 1) / $13 >= 0.6)' "${OUTPUT_DIR}/vf_result_with_header.blast" > "${OUTPUT_DIR}/vf_filtered_6060.blast"

cp "${OUTPUT_DIR}/vf_filtered_6060.blast" "${OUTPUT_DIR}/vf_header_6060.tsv"