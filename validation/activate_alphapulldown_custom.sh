#!/bin/bash

#Define variables
CONTAINER_NAME="alphapulldown_0.30.7.sif"
CONTAINER_PATH="./$CONTAINER_NAME"
DOCKER_IMAGE="docker://gallardoalba/alphapulldown:0.30.7"

#Check if the container image exists in the current working directory
if [ -e "$CONTAINER_PATH" ]; then
	echo "Container image $CONTAINER_NAME aleardy exists."
else
	echo "Container image $CONTAINER_NAME does not exist. Pulling from $DOCKER_IMAGE..."

	#Load Apptainer module
	module load apptainer/1.2.4
	#Pull the Docker image using Apptainer
	apptainer pull "$DOCKER_IMAGE"
	#Check if the pull was successful
	if [ -e "$CONTAINER_PATH" ]; then
		echo "Successfully pulled $CONTAINER_NAME."
	else
		echo "Failed to pull $CONTAINER_NAME."
		exit 1
	fi
fi

##create necessary directories
LOG_PATH="./log"
FEATURE_PATH="./feature_output"
MODEL_PATH="./model_output"

#Making a log directory if it does not exist in the current working directory
if [ -e "$LOG_PATH" ]; then
	echo "There is already a log directory"

else
	mkdir log
	echo "Created $LOG_PATH"

fi

#Making a feature output directory if it does not exist in the current working directory
if [ -e "$FEATURE_PATH" ]; then
        echo "There is already a feature output directory"

else
	mkdir feature_output
	echo "Created $FEATURE_PATH"
fi

#Making a model output directory if it does not exist in the current working directory
if [ -e "$MODEL_PATH" ]; then
        echo "There is already a model directory"

else
	mkdir model_output
	echo "Created $MODEL_PATH"

fi


#Count the number of proteins
feature_array_count=$(grep -c '>' validation_protein_sequences.fasta)

#Count the number of protein pairs
model_array_count=$(grep -c "" validation_protein_pairs.txt)

#Setting varibales for the checkpoint files
FEATURE_GENERATION_CHECKPOINT="feature_generation.txt"
STURUCTURE_GENERATION_CHECKPOINT="model_generation.txt"
SCORING_GENERATION_CHECKPOINT="complex_scoring.txt"


if [ ! -f "$FEATURE_GENERATION_CHECKPOINT" ]; then

	#Submit job to generate the features for the proteins
	feature_generation=$(sbatch --array=1-"$feature_array_count" alphapulldown_feature_generation_custom.sh)

	#Capture the feature generation job ID
	feature_generation_job_ID=$(echo "$feature_generation" | awk -v num_array="$feature_array_count" '{print $4 "_[1-"num_array"]"}')

	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$feature_generation_job_ID" touch_checkpoint.sh "feature_generation"

	#Submit job to generate the predicted model complex for each of the protein pairs
	model_generation=$(sbatch --array=1-"$model_array_count" --dependency=afterok:"$feature_generation_job_ID" alphapulldown_model_generation_custom.sh)

	#Capture the model generation job ID
	model_generation_job_ID=$(echo "$model_generation" | awk -v num_array="$model_array_count" '{print $4 "_[1-"num_array"]"}')

	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$model_generation_job_ID" touch_checkpoint.sh "model_generation"

	#Submit job to generate scoring metrics for each of the predicted models
	scoring_generation=$(sbatch --dependency=afterok:"$model_generation_job_ID" activate_scoring_custom.sh)

	#Capture the scoring job ID
	scoring_job_ID=$(echo "$scoring_generation" | awk '{print $4}')

	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$scoring_job_ID" touch_checkpoint.sh "complex_scoring"

	echo "Running step 1,2,and 3"

elif [ ! -f "$STURUCTURE_GENERATION_CHECKPOINT" ]; then

	#Submit job to generate the predicted model complex for each of the protein pairs
	model_generation=$(sbatch --array=1-"$model_array_count" alphapulldown_model_generation_custom.sh)

	#Capture the model generation job ID
	model_generation_job_ID=$(echo "$model_generation" | awk -v num_array="$model_array_count" '{print $4 "_[1-"num_array"]"}')

	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$model_generation_job_ID" touch_checkpoint.sh "model_generation"

	#Capture the model generation job ID
	scoring_generation=$(sbatch --dependency=afterok:"$model_generation_job_ID" activate_scoring_custom.sh)

	#Capture the scoring job ID
	scoring_job_ID=$(echo "$scoring_generation" | awk '{print $4}')

	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$scoring_job_ID" touch_checkpoint.sh "complex_scoring"

	echo "Running step 2, and 3"

elif [ ! -f "$SCORING_GENERATION_CHECKPOINT" ]; then

	#Submit job to generate scoring metrics for each of the predicted models
	scoring_generation=$(sbatch activate_scoring_custom.sh)

	#Capture the scoring job ID
	scoring_job_ID=$(echo "$scoring_generation" | awk '{print $4}')

	#Submit a job to create a checkpoint file only when job completes succesfully
	sbatch --dependency=afterok:"$scoring_job_ID" touch_checkpoint.sh "complex_scoring"

	echo "Running step 3"

else
	echo "All steps already completed!"

fi
