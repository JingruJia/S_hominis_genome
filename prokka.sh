source ~/miniconda3/bin/activate
conda activate prokka

# prokka --version
# 1.14.6

prokka "/path/to/genome_fna/${base}.fna" \
    --outdir "/path/to/prokka/${base}_prokka" \
    --cpus 3 \
    --compliant