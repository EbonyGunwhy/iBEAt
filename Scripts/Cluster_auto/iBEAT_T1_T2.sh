#!/bin/bash
# Request 8 gigabytes of real memory (mem)
#####$ -l rmem=8GB
# Request 2  cores in an OpenMP environment
#$ -pe openmp 16
# Email notifications to j.s.periquito@sheffield.ac.uk
#$ -M j.s.periquito@sheffield.ac.uk
# Email notifications if the job aborts
#$ -m a
# Name the job
#$ -N iBEAT_T1T2
# Request 24 hours of time
#$ -l h_rt=24:00:00

module load apps/python/conda

# Set the OPENMP_NUM_THREADS environment variable to 2
# This is needed to ensure efficient core usage.

export OMP_NUM_THREADS=$NSLOTS

# it is assumed that the conda environment 'myscience' has already been created
conda activate myscience
python T1T2_alone_cluster.py
