#!/bin/bash
source ./activate_pipeline_functions.sh

##check to see if alphapulldown container is in pwd, if not pull it

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


##create bait.txt and candidates.txt from inputted FASTA sequence

#create a flag for the bait fasta file and a flag for the candidates fasta file
while getopts 'a:b:c:' OPTION; do
	case "$OPTION" in
		a)
			peptidase_active_site="$OPTARG"
			;;

		b)
			bait_fasta_file="$OPTARG"
			;;

		c)
			candidates_fasta_file="$OPTARG"
			;;
	esac
done

#extract the name of the first sequence (peptidase bait)
grep '^>' "$bait_fasta_file" | sed 's/>/''/' > bait.txt

#extract the names of the reset of the sequences (inhibitor candidates)
grep '^>' "$candidates_fasta_file" | sed 's/>/''/' > candidates.txt

##create necessary directories
LOG_PATH="./log"
FEATURE_PATH="./feature_output"
MODEL_PATH="./model_output"
PEPTIDASE_MODEL_PATH="./peptidase_model_output"

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

#Making a peptidase model output directory if it does not exist in the current working directory
if [ -e "$PEPTIDASE_MODEL_PATH" ]; then
        echo "There is already a model directory"

else
        mkdir peptidase_model_output
        echo "Created $MODEL_PATH"

fi

#Count the number of lines in bait.txt
bait_count=$(grep -c "" ./bait.txt)

#count the number of lines in candidates.txt
candidates_count=$(grep -c "" ./candidates.txt)

count_features=$(( $bait_count + $candidates_count ))

count_model=$(($bait_count * $candidates_count))

PEPTIDASE_MODEL_CHECKPOINT=peptidase_model_prediction.txt
FEATURE_GENERATION_CHECKPOINT=feature_generation.txt
STURUCTURE_GENERATION_CHECKPOINT=complex_structural_predictions.txt
SCORING_GENERATION_CHECKPOINT=activate_scoring.txt

##Submit SLURM job scripts

if [ ! -f "$PEPTIDASE_MODEL_CHECKPOINT" ]; then
	#checks to see if a the peptidase-model job is already running
	if [ -z "$(squeue -n "peptidase-model" -h )" ]; then
		#Submit job to generate model for the peptidase
		peptidase_SLURM_output=$(sbatch --job-name=peptidase-model peptidase_model.sh "$bait_fasta_file")
		#Assign the peptidase SLURM job submission to a variable
		peptidase_model_SLURM_job_ID=$(echo $peptidase_SLURM_output | awk '{print $4}')
	else
		peptidase_model_SLURM_job_ID=$(squeue -n "peptidase-model" -h -o "%i")

	fi
else
	echo "Peptidase model generation completed"
	peptidase_model_SLURM_job_ID=""
fi

if [ ! -f "$FEATURE_GENERATION_CHECKPOINT" ]; then
	#Submit job to generate featueres for the peptidase and inhibitor candidates
	feature_generation_SLURM_output=$(sbatch --array=1-"$count_features" alphapulldown_feature_generation.sh "$bait_fasta_file" "$candidates_fasta_file")
	#assigning the feature_count job id to a variable
	feature_generation_job_ID=$(echo "$feature_generation_SLURM_output" | awk -v num_array="$count_features" '{print $4 "_[1-"num_array"]"}')
	#Submit job to generate predicted models for each of the complexes
	model_generation_SLURM_output=$(sbatch --array=1-"$count_model" --dependency=afterok:"$feature_generation_job_ID" alphapulldown_model_generation.sh)
	#assigning the model_count job id to a variable
	model_generation_job_ID=$(echo "$model_generation_SLURM_output" | awk -v num_array="$count_model" '{print $4 "_[1-"num_array"]"}')
	# Call function for complex_scoring
    if [ -n "$peptidase_model_SLURM_job_ID" ]; then
        sbatch --dependency=afterok:"$model_generation_job_ID":"$peptidase_model_SLURM_job_ID" activate_scoring.sh "$peptidase_active_site"
    else
        sbatch --dependency=afterok:"$model_generation_job_ID" activate_scoring.sh "$peptidase_active_site"
    fi

elif [ ! -f "$STURUCTURE_GENERATION_CHECKPOINT" ]; then
	#Submit job to generate predicted models for each of the complexes
	model_count=$(sbatch --array=1-"$count_model" alphapulldown_model_generation.sh)
	#assigning the model_count job id to a variable
	model_generation_job_ID=$(echo "$model_count" | awk -v num_array="$count_model" '{print $4 "_[1-"num_array"]"}')
	# Call function for complex_scoring
    if [ -n "$peptidase_model_SLURM_job_ID" ]; then
        sbatch --dependency=afterok:"$model_generation_job_ID":"$peptidase_model_SLURM_job_ID" activate_scoring.sh "$peptidase_active_site"
    else
        sbatch --dependency=afterok:"$model_generation_job_ID" activate_scoring.sh "$peptidase_active_site"
    fi

elif [ ! -f "$SCORING_GENERATION_CHECKPOINT" ]; then
	# Call function for complex_scoring
    if [ -n "$peptidase_model_SLURM_job_ID" ]; then
        sbatch --dependency=afterok:"$model_generation_job_ID":"$peptidase_model_SLURM_job_ID" activate_scoring.sh "$peptidase_active_site"
    else
        sbatch --dependency=afterok:"$model_generation_job_ID" activate_scoring.sh "$peptidase_active_site"
    fi

else
	echo "All steps complete"

fi
