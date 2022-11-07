#!/bin/bash
# Request 8 gigabytes of real memory (mem)
#####$ -l rmem=2GB
# Request 16  cores in an OpenMP environment
#$ -pe openmp 16
# Email notifications to j.s.periquito@sheffield.ac.uk
#$ -M j.s.periquito@sheffield.ac.uk
# Email notifications if the job aborts
#$ -m a
# Name the job
#$ -N iBEAt_Leeds_01_to_02
# Request 95 hours of time
#$ -l h_rt=95:58:00
#$ -t 1-2

module load apps/python/conda

# Set the OPENMP_NUM_THREADS environment variable to 2
# This is needed to ensure efficient core usage.

export OMP_NUM_THREADS=$NSLOTS

# it is assumed that the conda environment 'myscience' has already been created
conda activate myscience
python main_cluster.py --num $SGE_TASK_ID
