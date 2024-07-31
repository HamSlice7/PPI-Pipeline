#!/bin/bash

#SBATCH --job-name=model_generation
#SBATCH --account=def-ahamilto
#SBATCH --time=12:00:00
#SBATCH --gres=gpu:1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=64000M
#SBATCH --error=log/APD_model_generation_%A_%a_err
#SBATCH --output=log/APD_model_generation_%A_%a_out

date

#load dependencies
module load cuda/11.1

echo 'cuda loaded'

nvidia-smi

#load in apptainer
module load apptainer/1.2.4


echo 'starting structural prediction'

#execute run_multimer_jobs.py command within the alphapulldown container
apptainer exec -C -B /datashare/alphafold -B $(pwd) -B $SLURM_TMPDIR:/tmp --nv ./alphapulldown_0.30.7.sif run_multimer_jobs.py --mode=pulldown \
  --num_cycle=1 \
  --num_predictions_per_model=1 \
  --output_path=$(pwd)/model_output \
  --data_dir=/datashare/alphafold \
  --protein_lists=$(pwd)/bait.txt,$(pwd)/candidates.txt  \
  --monomer_objects_dir=$(pwd)/feature_output \
  --job_index=$SLURM_ARRAY_TASK_ID

echo 'Finished complex structural predictions'


date
