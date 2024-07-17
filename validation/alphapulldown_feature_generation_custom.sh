#!/bin/bash

#SBATCH --job-name=feature_generation
#SBATCH --account=def-ahamilto
#SBATCH --time=6:00:00
#SBATCH --cpus-per-task=24
#SBATCH --mem=125G
#SBATCH --error=log/alphapulldown_feature_generation_%A_%a_err
#SBATCH --output=log/alphapulldown_feature_generation_%A_%a_out

date

#load in apptainer
module load apptainer/1.2.4

#execute create_individual_features.py command within the alphapulldown container
apptainer exec -C -B /datashare/alphafold -B $(pwd) -B $SLURM_TMPDIR:/tmp $(pwd)/alphapulldown_0.30.7.sif create_individual_features.py \
  --fasta_paths=$(pwd)/validation_protein_sequences.fasta \
  --data_dir=/datashare/alphafold \
  --save_msa_files=True \
  --output_dir=$(pwd)/feature_output \
  --use_precomputed_msas=False \
  --max_template_date=2025-01-04 \
  --skip_existing=False \
  --seq_index=$SLURM_ARRAY_TASK_ID

echo "finished feature generation"


date
