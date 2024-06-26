#!/bin/bash

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

##Submit script to create MSA features in an array based off the sum of the number of rown in bait.txt and candidate.txt

#Count the number of jobs corresponding to the number of sequences:
bait_count=`grep -c "" ./bait.txt` #count lines even if the last one has no end of line

candidates_count=`grep -c "" ./candidates.txt` #count lines even if the last one has no end of line

count_features=$(( $bait_count + $candidates_count ))

echo "There are $count_features to be completed for feature generation"

#generate features for proteins in baits.txt and candidates.txt
echo "Submitting feature generation jobs to SLURM"

feature_count=$(sbatch --array=1-"$count_features" alphapulldown_feature_generation.sh "$bait_fasta_file" "$candidates_fasta_file")

echo "Feature generation jobs submitted to SLURM"

#assigning the feature_count job id to a variable
feature_generation_job_ID=$(echo "$feature_count" | awk -v num_array="$count_features" '{print $4 "_[1-"num_array"]"}')

echo "Submitting peptidase model prediction to SLURM"

#generate model for the peptidase
sbatch peptidase_model.sh "$bait_fasta_file"

echo "Peptidase AlphaFold model prediction submitted to SLURM"

##Once all the msa features are created, submit the script that generates the models in pulldown mode
count_model=$(($bait_count * $candidates_count))

echo "There are $count_model jobs to be completed for model generation"

echo "Submitting model generation jobs to SLURM"

model_count=$(sbatch --array=1-"$count_model" --dependency=afterok:"$feature_generation_job_ID" alphapulldown_model_generation.sh)

echo "Model generation jobs submitted to SLURM"

model_generation_job_ID=$(echo "$model_count" | awk -v num_array="$count_model" '{print $4 "_[1-"num_array"]"}')

#run scoring script after model generation is complete
sbatch --dependency=afterok:"$model_generation_job_ID" activate_scoring.sh "$peptidase_active_site"

echo "Scoring script submitted to SLURM"
