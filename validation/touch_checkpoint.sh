#!/bin/bash

#SBATCH --job-name=touch_checkpoint_files
#SBATCH --account=def-ahamilto
#SBATCH --time=0:05:00

CHECKPOINT=$1

touch "$(pwd)/$CHECKPOINT.txt"
