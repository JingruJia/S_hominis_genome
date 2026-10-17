source ~/miniconda3/bin/activate
conda activate dRep

# dRep --version
# dRep 3.6.2

dRep dereplicate /path/to/drep_output -g /path/to/genome_fna/*.fna -sa 0.999 -nc 0.30 -p 30 -comp 95 -con 5 -pa 0.95