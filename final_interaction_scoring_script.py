#! usr/bin/env python3

"""
Scoring script for the output of AlphaPulldown By Jacob Hambly.

References:
- https://github.com/KosinskiLab/AlphaPulldown
- https://github.com/flyark/AFM-LIS
- https://github.com/mittinatten/freesasa
- https://github.com/biopython/biopython

"""

#Import necessary modules
import os
import json
import pickle
import numpy as np
import pandas as pd
import re
from Bio import PDB
import freesasa
from freesasa import Structure, calc
import sys

#Get user input
active_site_resnum = int(sys.argv[1])

def scores_from_APD(pae_cutoff = 12, active_site_residue = active_site_resnum):
	"""
	Acquire scores from the outputted pickle (.pkl) file associated with each model complex
	Scores:
	- ipTM
	- pTM
	- AFM confidence score (0.8ipTM * 0.2pTM)
	- pLDDT
	- Localized interaction score (LIS)
	- Localized interaction area (LIA)
	"""

	#Initiating a dictionary to hold the AA lengths of the peptidase and inhibitor for each predicted complex
	chain_lengths = {}


	#Initiating a list to hold the scores for each of the complexes
	model_scores = []

	#Loop through each of the complexes in the model_output directory
	for complex in complex_names:
	#Loop through each of the 5 complexes in the model_output directory
		for model_num in range(1,6):
			pdb_name = f"unrelaxed_model_{model_num}_multimer_v3_pred_0.pdb"
			pdb_file_path = os.path.join(f"{os.getcwd()}/model_output/{complex}", pdb_name)


			#Parse through each PDB file
			parser = PDB.PDBParser(QUIET = True)
			structure = parser.get_structure("structure", pdb_file_path)

			#Get the length of the peptidase
			for model in structure:
				for chain in model:
					chain_id = chain.get_id()
					chain_length = sum(1 for resiude in chain.get_residues()) #iterates through each residue in a chain and replaces all residues with 1 and then sums all then 1's
					chain_lengths[chain_id] = chain_length
					peptidase_length = chain_lengths.get("B")

			##Calculate the distance of the active site to the closest inhibitor residue

			#Get the active site residue as an object from the peptidase
			active_site_residue = structure[0]['B'][active_site_resnum]
			#Get the coordinates of the alpha carbon of the active site residue
			active_site_alpha = active_site_residue["CA"].get_coord()

			#Save the inhibitor as an object
			inhibitor = structure[0]['C']

			#Initialize a list to hold all the distances
			distances = []

			#Iterate through residues in the inhibitor and calculate distance to the active site of the residue
			for residue in inhibitor:
				residue_alpha = residue["CA"].get_coord()
				distances.append(np.linalg.norm(active_site_alpha - residue_alpha))

			#select the minimum distance to the active site
			min_distance_to_active_site = min(distances)

			##Calculate the SASA of the active site residue

			#Calculate the SASA of the complex
			result, sasa_classes = freesasa.calcBioPDB(structure)

			#Get the SASA of the active site residue
			sasa_active_site_residue = result.residueAreas()["B"][str(active_site_resnum)].total

			#Getting the path for pickle file corresponding to the current iterating complex
			pkl_name = f"result_model_{model_num}_multimer_v3_pred_0.pkl"
			pkl_file_path = os.path.join(f"{os.getcwd()}/model_output/{complex}", pkl_name)

			#open and read pickle file and extract ipTM, pTM, AFM confidence score, PAE and mean pLDDT
			p = pickle.load(open(pkl_file_path, 'rb'))
			ipTM = p.get("iptm")
			pTM = p.get("ptm")
			AFM_confidence = ((0.8*ipTM) + (0.2*pTM))
			pae = p.get("predicted_aligned_error")
			plddt = np.mean(p.get("plddt"))


			#creating new PAE matrix where values less than pae_cutoff = 1 and values greater than pae_cutoff = 0
			thresholded_pae = np.where(pae < pae_cutoff, 1, 0)


			#Calculating the LIA
			LIA_1 = np.count_nonzero(thresholded_pae[:peptidase_length, peptidase_length:]) #Bottom left quadrant of PAE matrix
			LIA_2 = np.count_nonzero(thresholded_pae[peptidase_length:, :peptidase_length]) #Top right quadrant of PAE matrix
			LIA_sum = (LIA_1 + LIA_2)

			#Reverse scaling the PAE matrix
			scaled_pae = reverse_and_scale_pae_matrix(pae, pae_cutoff)

			#Calculating the LIS
			LIS_1 = scaled_pae[:peptidase_length, peptidase_length:][thresholded_pae[:peptidase_length, peptidase_length:] == 1] #Selecting PAE values bellow pae_threshold in the bottom left quadrant of PAE
			average_LIS_1 = np.mean(LIS_1) if np.size(LIS_1) > 0 else 0 #Taking the average of the selected PAE values

			LIS_2 = scaled_pae[peptidase_length:, :peptidase_length][thresholded_pae[peptidase_length:, :peptidase_length] == 1] #Selecting PAE values bellow pae_threshold in the top right quadrant of the PAE matrix
			average_LIS_2 = np.mean(LIS_2) if np.size(LIS_2) > 0 else 0 #Taking the average of the selected PAE values


			average_LIS_score = (average_LIS_1 + average_LIS_2)/2

			#Append data to the model_scores list as a panda series
			model_scores.append(pd.Series({
				'Complex':complex,
				'Protein_1': 'B',
				'Protein_2': 'C',
				'LIS': round(average_LIS_score, 3),
				'LIA': LIA_sum,
				'ipTM': round(float(ipTM),3),
				'Inhibitor minimum distance to active site' : min_distance_to_active_site,
				'SASA of the active site residue' : sasa_active_site_residue,
				'Confidence': round(float(AFM_confidence),3),
				'pTM': round(float(pTM),3),
				'pLDDT': round(plddt, 2),
				'Model': model_num,
				'Saved Folder': os.path.dirname(pdb_file_path),
				'pdb': os.path.basename(pdb_file_path),
				'pkl': os.path.basename(pkl_file_path),
			}))

		result_df = pd.concat(model_scores, axis=1).T
	return result_df

def reverse_and_scale_pae_matrix(pae_matrix, pae_cutoff):
        """
        Scale PAE matrix such that 0 becomes 1, pae_cutoff becomes 0, and values greater than pae_cutoff are also 0.
        Args:
        - PAE matrix (numpy matrix)
        - pae_cutoff (float)

        Returns:
        - Transformed PAE matrix (numpy matrix)
        """

        #Reverse scale the PAE matrix values where PAE values of 0 equal 1, PAE values equal to the cutoff equal 0 and any value above the PAE cutoff is less than 0
        scaled_matrix = (pae_cutoff - pae_matrix) / pae_cutoff

        #Use np.clip() to limit the values in the matrix, i.e. if a value is below 0 then it becomes 0.
        scaled_matrix = np.clip(scaled_matrix, 0, None)

        return scaled_matrix



#Get a list of the complexes in the model_output directory
complex_names = os.listdir(f"{os.getcwd()}/model_output")

#Get peptidase name
peptidase_complex = complex_names[0]
peptidase = re.search("^[^_]+", peptidase_complex).group()

#Call the scores_from_APD() function and save the output to the APD_results variable
APD_results = scores_from_APD()

#Save APD_results to a csv file
APD_results.to_csv(f'{peptidase}_results.csv', index = False)

print(f'Saved results to {peptidase}_results.csv')
