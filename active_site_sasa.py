from Bio import PDB
import freesasa
from freesasa import Structure, calc

def calc_sasa(pdb_file_path, residue):
   """
   Calculates the solvent accessibility surface area (SASA) of a active site residue for a peptidase-inhibitor complex
   
   Input: Path to a pdb file (string), residue number (int)
   Output: Solvent accessibility surface area (SASA) of residue (float)
   """

   #Parse through the PDB file
   parser = PDB.PDBParser(QUIET = True)
   structure = parser.get_structure("structure", pdb_file_path)

   #Calculate SASA of the complex
   result, sasa_classes = freesasa.calcBioPDB(structure)

   #Get the SASA of the active site residue
   sasa_active_site_residue = result.residueAreas()["B"][str(residue)].total

   return sasa_active_site_residue
