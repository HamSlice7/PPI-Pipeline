# PPI-Pipeline

activate_alphapulldown.sh is used to activate the feature generation and model prediction scripts for the peptidase-inhibitor complexes as well as the model generation of the unbound peptidase (alphapulldown_feature_generation.sh, alphapulldown_model_generation.sh, peptidase_model.sh)

main_scoring.py is used to calculate the scoring metrics for each of the peptidase-inhibitor complexes and to save the results in a csv file. Functions for main_scoring.py are written in afm_scoring.py, active_site_sasa.py, active_site_sasa_unbound_peptidase.py, min_peptidase_inhibitor_distance.py, and reverse_and_scale_pae_matrix.py. 

bait.fasta and candidates.fasta are example input fasta files and 1DJ_results.csv is an example of an output from the pipeline.
