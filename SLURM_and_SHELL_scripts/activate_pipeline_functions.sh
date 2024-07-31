#!/bin/bash

##SLURM submission functions
function peptidase_model_prediction {
	#Submit job to generate model for the peptidase
	peptidase_SLURM_output=$(sbatch --job-name=peptidase-model SLURM_and_SHELL_scripts/peptidase_model.sh "$bait_fasta_file")
	#Assign the peptidase SLURM job submission to a variable
	peptidase_model_SLURM_job_ID=$(echo $peptidase_SLURM_output | awk '{print $4}')
	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$peptidase_model_SLURM_job_ID" SLURM_and_SHELL_scripts/touch.sh "peptidase_model"
	echo "Submitted peptidase model prediction"
}

function complex_feature_generation {
    #Submit job to generate features for the peptidase and each of the inhibitors
	feature_generation_SLURM_output=$(sbatch --array=1-"$count_features" SLURM_and_SHELL_scripts/alphapulldown_feature_generation.sh "$bait_fasta_file" "$candidates_fasta_file")
	#assigning the feature_count job id to a variable
	feature_generation_job_ID=$(echo "$feature_generation_SLURM_output" | awk -v num_array="$count_features" '{print $4 "_[1-"num_array"]"}')
	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$feature_generation_job_ID" SLURM_and_SHELL_scripts/touch.sh "feature_generation"
	echo "Submitted complex feature generation"

}

function complex_model_generation_dependency {
	#Submit job to generate predicted models for each of the complexes
	model_generation_SLURM_output=$(sbatch --array=1-"$count_model" --dependency=afterok:"$feature_generation_job_ID" SLURM_and_SHELL_scripts/alphapulldown_model_generation.sh)
	#assigning the model_count job id to a variable
	model_generation_job_ID=$(echo "$model_generation_SLURM_output" | awk -v num_array="$count_model" '{print $4 "_[1-"num_array"]"}')
	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$model_generation_job_ID" SLURM_and_SHELL_scripts/touch.sh "model_generation"
	echo "Submitted complex model generation"
}

function complex_scoring_peptidase_dependency {
	scoring_SLURM_output=$(sbatch --dependency=afterok:"$model_generation_job_ID":"$peptidase_model_SLURM_job_ID" SLURM_and_SHELL_scripts/activate_scoring.sh "$peptidase_active_site")
	scoring_job_ID=$(echo "$scoring_SLURM_output" | awk '{print $4}')
	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$scoring_job_ID" SLURM_and_SHELL_scripts/touch.sh "complex_scoring"
	echo "Submitted scoring"

}

function complex_scoring_model_dependency {
	scoring_SLURM_output=$(sbatch --dependency=afterok:"$model_generation_job_ID" SLURM_and_SHELL_scripts/activate_scoring.sh "$peptidase_active_site")
	scoring_job_ID=$(echo "$scoring_SLURM_output" | awk '{pring $4}' )
	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$scoring_job_ID" SLURM_and_SHELL_scripts/touch.sh "complex_scoring"
	echo "Submitted scoring (model dependency)"
}

function complex_model_generation {
	#Submit job to generate predicted models for each of the complexes
	model_generation_SLURM_output=$(sbatch --array=1-"$count_model" SLURM_and_SHELL_scripts/alphapulldown_model_generation.sh)
	#assigning the model_count job id to a variable
	model_generation_job_ID=$(echo "$model_generation_SLURM_output" | awk -v num_array="$count_model" '{print $4 "_[1-"num_array"]"}')
	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$model_generation_job_ID" SLURM_and_SHELL_scripts/touch.sh "model_generation"
	echo "Submitted model generation"
}

function complex_scoring_peptidase_no_dependency {
	scoring_SLURM_output=$(sbatch SLURM_and_SHELL_scripts/activate_scoring.sh "$peptidase_active_site")
	scoring_job_ID=$(echo "$scoring_SLURM_output" | awk '{print $4}')
	echo "$scoring_job_ID"
	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$scoring_job_ID" SLURM_and_SHELL_scripts/touch.sh "complex_scoring"
	echo "Submitted scoring (no dependency)"
}

