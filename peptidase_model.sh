#!/bin/bash
#SBATCH --job-name=peptidase_model_generation
#SBATCH --account=def-ahamilto
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=90G
#SBATCH --gpus-per-node=v100:1
#SBATCH --nodes=1
#SBATCH --error=job_o.err_af_peptidase
#SBATCH --output=job_o.output_af_peptidase


# Load modules dependencies.
module load StdEnv/2020 gcc/9.3.0 openmpi/4.0.3 cuda/11.4 cudnn/8.2.0 kalign/2.03 hmmer/3.2.1 openmm-alphafold/7.5.1 hh-suite/3.3.0 python/3.8


# Generate your virtual environment in $SLURM_TMPDIR.
virtualenv --no-download ${SLURM_TMPDIR}/env
source ${SLURM_TMPDIR}/env/bin/activate

# Install AlphaFold and its dependencies.
pip install --no-index --upgrade pip
pip install --no-index --requirement ~/alphafold-requirements.txt

#load in peptidase fasta file
peptidase_fasta_file=$1

# Edit with the proper arguments and run your commands.
run_alphafold.py \
   --fasta_paths=$(pwd)/"$peptidase_fasta_file" \
   --output_dir=$(pwd)/peptidase_model_output \
   --data_dir=/datashare/alphafold \
   --model_preset=monomer_casp14  \
   --bfd_database_path=/datashare/alphafold/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt \
   --mgnify_database_path=/datashare/alphafold/mgnify/mgy_clusters_2022_05.fa \
   --pdb70_database_path=/datashare/alphafold/pdb70/pdb70 \
   --template_mmcif_dir=/datashare/alphafold/pdb_mmcif/mmcif_files  \
   --obsolete_pdbs_path=/datashare/alphafold/pdb_mmcif/obsolete.dat \
   --uniref30_database_path=/datashare/alphafold/uniref30/UniRef30_2021_03 \
   --uniref90_database_path=/datashare/alphafold/uniref90/uniref90.fasta \
   --hhblits_binary_path=${EBROOTHHMINSUITE}/bin/hhblits \
   --hhsearch_binary_path=${EBROOTHHMINSUITE}/bin/hhsearch \
   --jackhmmer_binary_path=${EBROOTHMMER}/bin/jackhmmer \
   --kalign_binary_path=${EBROOTKALIGN}/bin/kalign \
   --max_template_date=2025-01-04 \
   --use_gpu_relax=True

