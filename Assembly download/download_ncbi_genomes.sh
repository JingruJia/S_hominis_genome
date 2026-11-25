#!/bin/bash

target_dir="/path/to/genome_fna_gz"
input_file="/path/to/genome_accession_list.txt"

log_file="$target_dir/download_fna.log"

mkdir -p "$target_dir"
cd "$target_dir" || exit 1

echo "Starting genome DNA sequence downloads (genomic.fna.gz) - $(date)" > "$log_file"

base_url="https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF"

success_count=0
fail_count=0

while IFS=$'\t' read -r accession asm_id || [[ -n "$accession" ]]; do
    accession=$(echo "$accession" | tr -d '\r' | xargs)
    asm_id=$(echo "$asm_id" | tr -d '\r' | xargs)

    [[ -z "$accession" || -z "$asm_id" ]] && continue

    echo "Processing: $accession ($asm_id)"
    echo "----------------------------------------" >> "$log_file"
    echo "Processing: $accession ($asm_id)" >> "$log_file"

    acc_num=$(echo "$accession" | sed 's/GCF_//' | sed 's/\.[0-9]*$//')
    if [[ ${#acc_num} -lt 9 ]]; then
        echo "  Skipping: Invalid accession format $accession" >> "$log_file"
        ((fail_count++))
        continue
    fi

    p1=${acc_num:0:3}
    p2=${acc_num:3:3}
    p3=${acc_num:6:3}
    folder_name="${accession}_${asm_id}"

    dir_url="${base_url}/${p1}/${p2}/${p3}/${folder_name}/"

    echo "  Probing directory: $dir_url" >> "$log_file"

    tmp_html=$(mktemp)
    if ! wget -q -T 20 -O "$tmp_html" "$dir_url" 2>/dev/null; then
        echo "  [FAILED] Cannot access directory" >> "$log_file"
        echo "    [FAILED] $accession"
        ((fail_count++))
        rm -f "$tmp_html"
        continue
    fi

    real_file=$(grep -oE "href=\"[^\"]*genomic\.fna\.gz\"" "$tmp_html" | sed 's/href="//;s/"//' | head -n 1)

    rm -f "$tmp_html"

    if [[ -z "$real_file" ]]; then
        echo "  [FAILED] No *genomic.fna.gz file found in directory" >> "$log_file"
        echo "    [FAILED] $accession (file missing)"
        ((fail_count++))
        continue
    fi

    echo "  [FOUND] Actual filename: $real_file" >> "$log_file"

    download_url="${dir_url}${real_file}"

    local_save_name="${accession}_genomic.fna.gz"

    echo "  Downloading: $download_url" >> "$log_file"
    echo "  Saving as: $local_save_name" >> "$log_file"

    if wget -T 60 -t 2 "$download_url" -O "$target_dir/$local_save_name" 2>> "$log_file"; then
        echo "    [SUCCESS] Saved as $local_save_name"
        echo "    [SUCCESS] $local_save_name" >> "$log_file"
        ((success_count++))
    else
        echo "    [FAILED] Download interrupted or failed"
        echo "    [FAILED] Failed to download $real_file" >> "$log_file"
        rm -f "$target_dir/$local_save_name"
        ((fail_count++))
    fi

done < "$input_file"

echo ""
echo "=========================================="
echo "DNA sequence downloads completed!"
echo "Succeeded: $success_count"
echo "Failed: $fail_count"
echo "Save path: $target_dir"
echo "=========================================="
echo "Summary: Succeeded=$success_count, Failed=$fail_count, Finished=$(date)" >> "$log_file"
