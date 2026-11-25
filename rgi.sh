#!/usr/bin/env bash
source ~/miniconda3/bin/activate
conda activate rgi

# rgi main --version
# 6.0.5

CARD_JSON="/path/to/CARD_db/card.json"
INPUT_DIR="/path/to/prokka_faa"
OUTPUT_DIR="/path/to/rgi_result"

rgi main \
        --input_sequence "$input" \
        --output_file "$OUTPUT_DIR/$sample" \
        --input_type protein \
        --local \
        --clean \
        --include_nudge \
        --num_threads "$THREADS" \
        --evalue 1e-5