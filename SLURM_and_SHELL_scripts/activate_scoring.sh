#!/bin/bash

#SBATCH --job-name=scoring_activation
#SBATCH --account=def-ahamilto
#SBATCH --time=1:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --error=log/alphapulldown_scoring_metrics_%A_%a_err
#SBATCH --output=log/alphapulldown_scoring_metrics_%A_%a_out


#activate python virtual environment
source ~/AF_LIS_ENV/bin/activate

#Load necessary modules
module load StdEnv/2020 python/3.10.2

active_site=$1

#run main_scoring.py
python $(pwd)/python_scripts/main_scoring.py "$active_site"

