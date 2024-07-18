import AFM_scoring
import num_unique_msa
import os
import pandas as pd
import re
import sys
from statistics import mean


#Get a list of the complexes in the model_output directory
complex_names = os.listdir(f"{os.getcwd()}/model_output")

AFM_scoring_metric = {}

#Loop through each of the complexes in the model_output directory
for complex in complex_names:
    #Loop through each of the 5 complexes in the model_output directory
    for model_num in range(1,6):
        pdb_name = f"unrelaxed_model_{model_num}_multimer_v3_pred_0.pdb"
        pdb_file_path = os.path.join(f"{os.getcwd()}/model_output/{complex}", pdb_name)

        #Getting the names for the peptidase and inhibitor from the current iterating complex
        peptidase_inhibitor_name = complex.split("_and_")
        peptidase_name = peptidase_inhibitor_name[0]
        inhibitor_name = peptidase_inhibitor_name[1]

        pkl_name = f"result_model_{model_num}_multimer_v3_pred_0.pkl"
        pkl_file_path = os.path.join(f"{os.getcwd()}/model_output/{complex}", pkl_name)
        AFM_scoring_metric[f"{complex}_{model_num}"] = AFM_scoring.AFM_scoring(pdb_file_path, pkl_file_path, 12, peptidase_name, inhibitor_name)


#creating data frames from dictionaries
df_AFM_scoring_metric = pd.DataFrame.from_dict(AFM_scoring_metric, orient = "index")

#creating the final data frame
df_final = df_AFM_scoring_metric

protein_pairs_file = "validation_protein_pairs.txt"

with open (protein_pairs_file, "r") as f:
    proteins = [line.strip().split(";") for line in f]
    proteins = [item for list in proteins for item in list]

print(proteins)

msa_depth = {}

for protein in proteins:
    msa_file_path = f"{os.getcwd()}/feature_output/{protein}"
    msa_depth[protein] = num_unique_msa.num_unique_msa(msa_file_path)


#creating new columns for the msa depth of the peptidase and inhibitor and mapping values from msa_depth dictionary
df_final["MSA_depth_peptidase"] = df_final["Protein 1"].map(msa_depth)

df_final["MSA_depth_inhibitors"] = df_final["Protein 2"].map(msa_depth)

print(df_final)

#Save APD_results to a csv file
df_final.to_csv(f'custom_results.csv', index = True)

print(f'Saved results to custom_results.csv')
