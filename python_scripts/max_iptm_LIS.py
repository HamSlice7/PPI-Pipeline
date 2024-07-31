import pandas as pd
import sys
import re

csv_file = sys.argv[1]

df = pd.read_csv(csv_file)



def get_max(data: pd.DataFrame, metric: str()) -> pd.DataFrame:

    """
    Return a data frame of either the max ipTM value
    from each complex or the LIS+LIA value assocaited
    with the max ipTM of each complex

    Parameters:
        csv_file: path to a csv file with labels of 1 for a positive PPI and 0 for a negative PPI for each complex
        metric (str): Either "ipTM" to return a dataframe of the max ipTM value from each complex or
        "LIS_LIA" to return a data frame of the LIS and LIA value assocaited with each complex
        with the highest ipTM value
    Return:
        Max ipTM value from each complex or the LIS+LIA value assocaited
        with the max ipTM of each complex (pd.DataFrame)

    """

    df = data

    #add a column to group the complexes


    num_complexes = int(df.shape[0] / 5)

    complex_number = [i for i in range(num_complexes) for _ in range(5)]

    df["Complex_Number"] = complex_number

    if metric == "ipTM":

        df_iptm_max = df.groupby("Complex_Number")["ipTM"].max().reset_index()

        df_label = pd.merge(df_iptm_max, df, on=["Complex_Number", "ipTM"], how='left')

        df_label = df_label.drop_duplicates(subset="Complex_Number").reset_index(drop=True)

        df_max_iptm = df_label[["Complex_Number", "Protein 1", "Protein 2", "ipTM", "LIS", "LIA", "pTM", "AFM Confidence", "pLDDT", "Distances", "Change in SASA", "MSA_depth_peptidase", "MSA_depth_inhibitors"]]
        df_max_iptm.to_csv('iptm_max.csv', index=False)

    elif metric == "LIS":

        df_LIS_max = df.groupby("Complex_Number")["LIS"].max().reset_index()
        df_label = pd.merge(df_LIS_max, df, on=["Complex_Number", "LIS"], how='left')
        df_label = df_label.drop_duplicates(subset="Complex_Number").reset_index(drop=True)
        df_max_LIS = df_label[["Complex_Number", "Protein 1", "Protein 2", "ipTM", "LIS", "LIA", "pTM", "AFM Confidence", "pLDDT", "Distances", "Change in SASA", "MSA_depth_peptidase", "MSA_depth_inhibitors"]]
        df_max_LIS.to_csv('LIS_max.csv', index=False)

get_max(df, "ipTM")
get_max(df, "LIS")

