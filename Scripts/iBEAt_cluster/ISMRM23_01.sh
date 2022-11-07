#!/bin/bash
# Request 8 gigabytes of real memory (mem)
#####$ -l rmem=2GB
# Request 8  cores in an OpenMP environment
#$ -pe openmp 8
# Email notifications to j.s.periquito@sheffield.ac.uk
#$ -M j.s.periquito@sheffield.ac.uk
# Email notifications if the job aborts
#$ -m a
# Name the job
#$ -N ISMRM_Exeter_06_to_26
# Request 95 hours of time
#$ -l h_rt=24:00:00
#$ -t 6-26

module load apps/python/conda

# Set the OPENMP_NUM_THREADS environment variable to 2
# This is needed to ensure efficient core usage.

export OMP_NUM_THREADS=$NSLOTS

# it is assumed that the conda environment 'myscience' has already been created
conda activate myscience
python main_cluster_ISMRM23_01.py --num $SGE_TASK_ID
