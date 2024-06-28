import min_peptidase_inhibitor_distance
import active_site_sasa
import active_site_sasa_unbound_peptidase
from afm_scoring import afm_scoring
import os
import pandas as pd
import re
import sys
from statistics import mean


#Get a list of the complexes in the model_output directory
complex_names = os.listdir(f"{os.getcwd()}/model_output")

#Initialize a dictionary to hold the complex as a key and the closest distance of the active site and the inhibitor as the value
distances = {}

#Initialize a dictionary to hold the complex as a key and the SASA of a active site residue
sasa = {}

#Initialize a list to hold the SASA values of a active site resiude 
unbound_peptidase_sasa = []

#Initialize a dictionary to hold the complex as a key and the AFM scoring metrics as the value 
AFM_scoring_metric = {}

#get active site user input
active_site_resnum = int(sys.argv[1])

#Loop through each of the complexes in the model_output directory
for complex in complex_names:
    #Loop through each of the 5 complexes in the model_output directory
    for model_num in range(1,6):
        
        #Get the pdb file path of the iterating complex
        pdb_name = f"unrelaxed_model_{model_num}_multimer_v3_pred_0.pdb"
        pdb_file_path = os.path.join(f"{os.getcwd()}/model_output/{complex}", pdb_name)
        
        #Append the min distance of the inhibitor to the active site of the peptidase of the iterating complex to the distances dictionary
        distances[f"{complex}_{model_num}"] = min_peptidase_inhibitor_distance.min_distance(pdb_file_path, active_site_resnum)

        #Append the SASA of the residue of a active site of the peptidase for the current complex iteration to the sasa dictionary
        sasa[f"{complex}_{model_num}"] = active_site_sasa.calc_sasa(pdb_file_path, active_site_resnum)
        
        #Get the pkl file path of the iterating complex  
        pkl_name = f"result_model_{model_num}_multimer_v3_pred_0.pkl"
        pkl_file_path = os.path.join(f"{os.getcwd()}/model_output/{complex}", pkl_name)

        #Get AFM scoring metrics of the iterating complex and append to the AFM_scoring_metric dictionary
        AFM_scoring_metric[f"{complex}_{model_num}"] = afm_scoring(pdb_file_path, pkl_file_path, 12)

#Loop throught each model from unbound peptidase model prediction output.
for model_num in range(1,6):
    
    #Get PDB path of the iterating unbound peptidase complex (input fasta file was "bait.fasta")
    peptidase_AF_model_name = f"unrelaxed_model_{model_num}_pred_0.pdb"
    peptidase_AF_model_path = os.path.join(f"{os.getcwd()}/peptidase_model_output/bait/", peptidase_AF_model_name)

    #Append the SASA of a active site residue of the unbound peptidase to unbound_peptidase_sasa 
    unbound_peptidase_sasa.append(active_site_sasa_unbound_peptidase.calc_sasa(peptidase_AF_model_path, active_site_resnum))

#Getting the mean SASA of the active site of the unbound peptidase
mean_unbound_pepetidase_active_site_sasa = (round(mean(unbound_peptidase_sasa), 3))

#creating data frames from dictionaries
df_AFM_scoring_metric = pd.DataFrame.from_dict(AFM_scoring_metric, orient = "index")
df_sasa = pd.DataFrame.from_dict(sasa, orient = "index").rename(columns = {0:"SASA"})
df_distances = pd.DataFrame.from_dict(distances, orient = "index").rename(columns = {0:"Distances"})

#Concatenating the AFM_scoring_metric, sasa, and distances data frames 
df_final = pd.concat([df_AFM_scoring_metric, df_distances, df_sasa], axis = 1)

#appending difference in SASA at the active site between bound and unbound peptidase
df_final["Change in SASA"] = (df_final["SASA"] - mean_unbound_pepetidase_active_site_sasa)

#Get peptidase name
peptidase_complex = complex_names[0]
peptidase = re.search("^[^_]+", peptidase_complex).group()

#Save APD_results to a csv file
df_final.to_csv(f'{peptidase}_results.csv', index = True)

print(f'Saved results to {peptidase}_results.csv')
