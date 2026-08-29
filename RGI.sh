#!/usr/bin/env bash

CARD_JSON="/path/to/CARD_db/card.json"
INPUT_DIR="/path/to/prokka_faa"
OUTPUT_DIR="/path/to/rgi_result"
THREADS=8

mkdir -p "$OUTPUT_DIR"
rgi load --card_json "$CARD_JSON" --local

for input in "$INPUT_DIR"/*.faa; do
    sample=$(basename "$input" .faa)
    rgi main \
        --input_sequence "$input" \
        --output_file "$OUTPUT_DIR/$sample" \
        --input_type protein \
        --local \
        --clean \
        --include_nudge \
        --num_threads "$THREADS" \
        --evalue 1e-5
done

awk -F'\t' 'FNR==1 && NR==1 {print; next} FNR>1 && ($0 ~ /\tPerfect\t/ || $0 ~ /\tStrict\t/) {print}' \
    "$OUTPUT_DIR"/*.txt > "$OUTPUT_DIR/All_Perfect_Strict_Results.txt"
