#!/bin/bash

#Count the number of lines in bait.txt
bait_count=$(grep -c "" ./bait.txt)

#count the number of lines in candidates.txt
candidates_count=$(grep -c "" ./candidates.txt)

count_features=$(( $bait_count + $candidates_count ))

##SLURM submission functions
function peptidase_model_prediction {
	#generate model for the peptidase
	peptidase_SLURM_output=$(sbatch peptidase_model.sh "$bait_fasta_file")

	#assign the peptidase SLURM job submission to a variable
	peptidase_model_SLURM_job_ID=$(echo $peptidase_SLURM_output | awk '{print $4}')
}

function complex_feature_generation {
	feature_count=$(sbatch --array=1-"$count_features" alphapulldown_feature_generation.sh "$bait_fasta_file" "$candidates_fasta_file")
	echo "Feature generation jobs submitted to SLURM"

	#assigning the feature_count job id to a variable
	feature_generation_job_ID=$(echo "$feature_count" | awk -v num_array="$count_features" '{print $4 "_[1-"num_array"]"}')
	echo "Submitting peptidase model prediction to SLURM"
}

function complex_model_generation {
	count_model=$(($bait_count * $candidates_count))
	model_count=$(sbatch --array=1-"$count_model" --dependency=afterok:"$feature_generation_job_ID" alphapulldown_model_generation.sh)
	echo "Model generation jobs submitted to SLURM"
	model_generation_job_ID=$(echo "$model_count" | awk -v num_array="$count_model" '{print $4 "_[1-"num_array"]"}')
}

function complex_scoring {
	sbatch --dependency=afterok:"$model_generation_job_ID":"$peptidase_model_SLURM_job_ID" activate_scoring.sh $1
	echo "Scoring script submitted to SLURM"
}