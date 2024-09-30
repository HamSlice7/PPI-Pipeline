import pandas as pd
import sys

#data = sys.argv[1]
#df = pd.read_csv(data)

def get_mean(data: pd.DataFrame) -> pd.DataFrame:

    """
    Return a data frame of the mean values for ipTM, LIS, LIA, pTM, AF Confidience (0.8*ipTM + 0.2*pTM)
    and pLDDT

    Parameters:
        - csv_file (pd.DataFrame): path to a csv file with labels of 1 for a positive PPI and 0 for a negative PPI for each complex

    Return:
        - Mean ipTM, LIS, LIA, pTM, AF Confidience (0.8*ipTM + 0.2*pTM)
          and pLDDT values from each complex.

    """

    #assign the pipeline output data to the variable 'df'
    df = data

    #Create a list of the metrics that will be used for averages
    metric_columns = ["LIS", "LIA", "ipTM", "pTM", "AFM Confidence", "pLDDT", "MSA_depth_peptidase", "MSA_depth_inhibitors", "Binary_Label"]

    #Group the pipeline data by "Protein 1" and "Protein 2" and then take the means of the groups based on the specified columns in the "metric_columns" list
    df_complex_mean = df.groupby(["Protein 1", "Protein 2"])[metric_columns].mean().reset_index()

    df_complex_mean.to_csv("validation_1_recycle_mean.csv", index=False)

    return df_complex_mean

#get_mean(df)

        


