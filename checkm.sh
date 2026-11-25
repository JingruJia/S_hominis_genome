source ~/miniconda3/bin/activate
conda activate /data/work/conda_envs/checkm

# checkm
# 1.2.5

checkm lineage_wf -t 32 -x fna \
    /path/to/genome_fna \
    /path/to/checkm/