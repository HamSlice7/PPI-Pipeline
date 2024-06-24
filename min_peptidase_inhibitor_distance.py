from Bio import PDB
import numpy as np

parser = PDB.PDBParser(QUIET = True)

def min_distance(pdb_file, active_site_residue_num):
    """
    Finds the minimum distance between the alpha carbon of a active site residue and a alpha carbon of the inhibitor
    
    Input: PDB file for a peptidase-inhibitor complex (string), a residue number for the active site (int)
    Output: The minimum distance between the alpha carbon of the active site residue and a alpha carbon of the inhibitor (float)
    """
    
    #create a structure object from pdb_file
    structure = parser.get_structure("complex", pdb_file)

    #get the active site residue on the peptidase from inputted residue number
    active_site_residue = structure[0]["B"][active_site_residue_num]

    #Get the coordinates of the alpha carbon of the active site residue
    active_site_alpha = active_site_residue["CA"].get_coord()

    #Save the inhibitor as an object
    inhibitor = structure[0]["C"]

    #Initialize a list to hold all the distances between the alpha carbons of active site residue and inhibitor residues
    distances = []

    #Iterate through residues of the inhibitor and calculate eucladian distance of alpha carbon to alpha carbon of active site residue
    for residue in inhibitor:
        residue_alpha = residue["CA"].get_coord()
        distances.append(np.linalg.norm(active_site_alpha - residue_alpha))

    min_distance_to_active_site = min(distances)

    return min_distance_to_active_site
