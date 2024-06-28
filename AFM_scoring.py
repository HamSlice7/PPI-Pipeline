from typing import Any
import os
from Bio import PDB
import pickle
import numpy as np
import reverse_and_scale_pae_matrix

parser = PDB.PDBParser(QUIET = True)

def afm_scoring(pdb_file_path: str, pkl_file_path: str, pae_cutoff: int, peptidase_name: str, inhibitor_name: str) -> dict[str, Any]:
    """
    Calculate the AFM scoring metrics for the complex

    Parameters:
        pdb_file_path: path to the complex pdb file (str)
        pkl_file_path: path to the complex pkl file (str)
        pae_cutoff: the PAE cutoff value (int)
        peptidase_name: the name of the peptidase (str)
        inhibitor_name: the name of the inhibitor (str)
    
    Returns:
        A dictionary containing the AFM scoring metrics for the complex (dict)
    """

    structure = parser.get_structure("complex", pdb_file_path)

    #Get the length of the peptidase
    for model in structure:
        for chain in model:
            if chain.get_id() == "B":
                peptidase_length = sum(1 for residue in chain.get_residues())

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
    scaled_pae = reverse_and_scale_pae_matrix.reverse_and_scale_pae_matrix(pae, pae_cutoff)

    #Calculating the LIS
    LIS_1 = scaled_pae[:peptidase_length, peptidase_length:][thresholded_pae[:peptidase_length, peptidase_length:] == 1] #Selecting PAE values below pae_threshold in the bottom left quadrant of PAE
    average_LIS_1 = np.mean(LIS_1) if np.size(LIS_1) > 0 else 0 #Taking the average of the selected scaled LIS values

    LIS_2 = scaled_pae[peptidase_length:, :peptidase_length][thresholded_pae[peptidase_length:, :peptidase_length] == 1] #Selecting PAE values below pae_threshold in the top right quadrant of the PAE
    average_LIS_2 = np.mean(LIS_2) if np.size(LIS_2) > 0 else 0 #Taking the average of the selected scaled LIS values

    average_LIS_score = (average_LIS_1 + average_LIS_2) / 2

    model_scores = {
        'Protein 1' : peptidase_name,
        'Protein 2' : inhibitor_name,
        'LIS' : round(average_LIS_score, 3),
        'LIA' : LIA_sum,
        'ipTM' : round(float(ipTM), 3),
        'pTM' : round(float(pTM), 3),
        'AFM Confidence' : round(float(AFM_confidence), 3),
        'pLDDT' : round(plddt,3),
        'PDB file path' : os.path.basename(pdb_file_path),
        'PKL file path' : os.path.basename(pkl_file_path)
    }

    return model_scores
