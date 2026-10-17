source ~/miniconda3/bin/activate
conda activate fastANI

# fastANI --version
# fastANI 1.34

fastANI --ql /path/to/fastani/list.txt \
        --rl /path/to/fastani/list.txt \
        --output /path/to/fastani/ani/FASTANI_matrix \
        --threads 30 \
        --matrix