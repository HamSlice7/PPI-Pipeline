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

##Submit SLURM job scripts

#Submit job for peptidase structure prediction if not complete
if [ ! -f peptidase_model_prediction.txt ]; then
	#call function for peptidase_model prediction
	peptidase_model_prediction
else
	echo "Peptidase model generation completed"

if [ ! -f feature_generation.txt ]; then
	#Call function for complex_feature_generation
	complex_feature_generation
	#Call function for complex_model_generation
	complex_model_generation
	#Call function for complex_scoring
	complex_scoring "$peptidase_active_site"
else
	echo "Complex feature generation completed"

if [ ! -f complex_structural_predictions.txt ] then;
	#Call function for complex_model_generation
	complex_model_generation
	#Call function for complex_scoring
	complex_scoring "$peptidase_active_site"
else
	echo "Complex model generation completed"

if [ ! -f activate_scoring.txt ] then;
	#Call function for complex_scoring
	complex_scoring "$peptidase_active_site"
else
	echo "Scoring completed"
