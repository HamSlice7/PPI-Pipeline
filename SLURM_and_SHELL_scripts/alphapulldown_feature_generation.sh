#!/bin/bash

#SBATCH --job-name=feature_generation
#SBATCH --account=def-ahamilto
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=24
#SBATCH --mem=125G
#SBATCH --error=log/alphapulldown_model_feature_generation_%A_%a_err
#SBATCH --output=log/alphapulldown_model_feature_generation_%A_%a_out

date

bait_fasta_file=$1

cat $(pwd)/"$bait_fasta_file"

echo "Bait FASTA file loaded"

candidates_fasta_file=$2

cat $(pwd)/"$candidates_fasta_file"

echo "Candidates FASTA file loaded"

#load in apptainer
module load apptainer/1.2.4

echo "apptainer loaded"

echo "beginning feature generation"

echo $(pwd)


#test command

echo "testing container"

apptainer exec -C -B /datashare/alphafold -B $(pwd) -B $SLURM_TMPDIR:/tmp $(pwd)/alphapulldown_0.30.7.sif create_individual_features.py \
  --helpfull

echo "testing sucessfull"

#execute create_individual_features.py command within the alphapulldown container
apptainer exec -C -B /datashare/alphafold -B $(pwd) -B $SLURM_TMPDIR:/tmp $(pwd)/alphapulldown_0.30.7.sif create_individual_features.py \
  --fasta_paths=$(pwd)/"$bait_fasta_file",$(pwd)/"$candidates_fasta_file" \
  --data_dir=/datashare/alphafold \
  --save_msa_files=True \
  --output_dir=$(pwd)/feature_output \
  --use_precomputed_msas=False \
  --max_template_date=2025-01-04 \
  --skip_existing=False \
  --seq_index=$SLURM_ARRAY_TASK_ID

echo "finished feature generation"


date
