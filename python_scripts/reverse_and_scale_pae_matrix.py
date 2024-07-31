import numpy as np

def reverse_and_scale_pae_matrix(pae_matrix, pae_cutoff):
    """
    Scale PAE matrix such that 0 becomes 1, pae_cutoff becomes 0, and values greater than pae_cutoff are also 0.
    Input: PAE matrix (numpy matrix), pae_cutoff (float)
    Output: Transformed PAE matrix (numpy matrix)
    """

    #Reverse scale the PAE matrix values where PAE values of 0 equal 1, PAE values equal to the cutoff equal 0 and any value above the PAE cutoff is less than 0
    scaled_pae = (pae_cutoff - pae_matrix) / pae_cutoff

    #Use np.clip() to limit the values in the matrix, i.e. if a value is below 0 then it becomes 0
    scaled_pae = np.clip(scaled_pae, 0, None)

    return scaled_pae
