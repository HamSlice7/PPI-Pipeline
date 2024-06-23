import min_peptidase_inhibitor_distance
import active_site_sasa
import active_site_sasa_unbound_peptidase
import AFM_scoring
import os
import pandas as pd
import re
import sys
from statistics import mean


#Get a list of the complexes in the model_output directory
complex_names = os.listdir(f"{os.getcwd()}/model_output")

distances = {}

sasa = {}

unbound_peptidase_sasa = []

AFM_scoring_metric = {}

#get active site user input
active_site_resnum = int(sys.argv[1])

#Loop through each of the complexes in the model_output directory
for complex in complex_names:
    #Loop through each of the 5 complexes in the model_output directory
    for model_num in range(1,6):
        pdb_name = f"unrelaxed_model_{model_num}_multimer_v3_pred_0.pdb"
        pdb_file_path = os.path.join(f"{os.getcwd()}/model_output/{complex}", pdb_name)
        distances[f"{complex}_{model_num}"] = min_peptidase_inhibitor_distance.min_distance(pdb_file_path, active_site_resnum)
        sasa[f"{complex}_{model_num}"] = active_site_sasa.calc_sasa(pdb_file_path, active_site_resnum)

        pkl_name = f"result_model_{model_num}_multimer_v3_pred_0.pkl"
        pkl_file_path = os.path.join(f"{os.getcwd()}/model_output/{complex}", pkl_name)
        AFM_scoring_metric[f"{complex}_{model_num}"] = AFM_scoring.AFM_scoring(pdb_file_path, pkl_file_path, 12)

#Loop throught each model from unbound peptidase model prediction output (assuming bait.fasta is the name of the input fasta)
for model_num in range(1,6):
    peptidase_AF_model_name = f"unrelaxed_model_{model_num}_pred_0.pdb"
    #assuming input fasta file was "bait.fasta"
    peptidase_AF_model_path = os.path.join(f"{os.getcwd()}/peptidase_model_output/bait/", peptidase_AF_model_name)
    unbound_peptidase_sasa.append(active_site_sasa_unbound_peptidase.calc_sasa(peptidase_AF_model_path, active_site_resnum))

#Getting the mean SASA of the active site of the unbound peptidase
mean_unbound_pepetidase_active_site_sasa = (round(mean(unbound_peptidase_sasa), 3))

#creating data frames from dictionaries
df_AFM_scoring_metric = pd.DataFrame.from_dict(AFM_scoring_metric, orient = "index")
df_sasa = pd.DataFrame.from_dict(sasa, orient = "index").rename(columns = {0:"SASA"})
df_distances = pd.DataFrame.from_dict(distances, orient = "index").rename(columns = {0:"Distances"})

#creating the final data frame
df_final = pd.concat([df_AFM_scoring_metric, df_distances, df_sasa], axis = 1)

#appending difference in SASA at the active site between bound and unbound peptidase
df_final["Change in SASA"] = (df_final["SASA"] - mean_unbound_pepetidase_active_site_sasa)

print(df_final)

#Get peptidase name
peptidase_complex = complex_names[0]
peptidase = re.search("^[^_]+", peptidase_complex).group()

#Save APD_results to a csv file
df_final.to_csv(f'{peptidase}_results.csv', index = True)

print(f'Saved results to {peptidase}_results.csv')
