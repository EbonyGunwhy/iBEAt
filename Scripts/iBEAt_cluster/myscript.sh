#!/bin/bash
# Request 16 g
#SBATCH --mem=32G
# Request 4 cores
#SBATCH --cpus-per-task=16
#SBATCH --time=167:45:00
# Email notifications to me@somedomain.com
#SBATCH --mail-user=j.s.periquito@sheffield.ac.uk
# Email notifications if the job fails
#SBATCH --mail-type=FAIL
# Rename the job's name
#SBATCH --comment=iBEAT
#SBATCH --array=3
unset SLURM_CPU_BIND

export SLURM_EXPORT_ENV=ALL
module load Anaconda3/2019.07

# We assume that the conda environment 'myexperiment' has already been created
source activate myscience
srun python main_cluster.py --num 9

