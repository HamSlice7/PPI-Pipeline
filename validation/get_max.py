import pandas as pd
import sys

#data = sys.argv[1]
#df = pd.read_csv(data)

def get_max(data: pd.DataFrame, metric: str) -> pd.DataFrame: 

    """
    Return a data frame of either the max ipTM, max LIS, or max LIA value from each complex
    
    Parameters:
        -data (pd.DataFrame): path to a csv file with labels of 1 for a positive PPI and 0 for a negative PPI for each complex
        -metric (str): "ipTM" to return a dataframe of the max ipTM value from each complex, "LIA" 
        to return a data frame of the LIA value assocaited with each complex or "LIS" to return a data frame of the
        LIS value associated with each complex.  
    
    Return:
        Max ipTM, LIS, or LIA value from each complex (pd.DataFrame)
    
    """

    df = data

    #add a column to group the complexes

    num_complexes = int(df.shape[0] / 5)

    #For the number of complexes loop through range(5) but return the current iterating number of complex for each iteration of range(5)
    complex_number = [i for i in range(num_complexes) for _ in range(5)]

    df["Complex_Number"] = complex_number

    if metric == "ipTM":
        df_iptm_max = df.groupby("Complex_Number")["ipTM"].max().reset_index()

        df_merge_iptm = pd.merge(df_iptm_max, df, on=["Complex_Number", "ipTM"], how='left')

        df_merge_iptm = df_merge_iptm.drop_duplicates(subset="Complex_Number").reset_index(drop=True)

        df_iptm = df_merge_iptm[["ipTM", "Binary_Label"]]
        return df_iptm
    
    elif metric == "LIS":
        df_lis_max = df.groupby("Complex_Number")["LIS"].max().reset_index()

        df_merge_lis = pd.merge(df_lis_max, df, on=["Complex_Number", "LIS"], how='left')

        df_merge_lis = df_merge_lis.drop_duplicates(subset="Complex_Number").reset_index(drop=True)

        df_lis = df_merge_lis[["LIS", "Binary_Label"]]
        
        return df_lis
    
    else:
        df_lia_max = df.groupby("Complex_Number")["LIA"].max().reset_index()

        df_merge_lia = pd.merge(df_lia_max, df, on=["Complex_Number", "LIA"], how='left')

        df_merge_lia = df_merge_lia.drop_duplicates(subset="Complex_Number").reset_index(drop=True)

        df_lia = df_merge_lia[["LIA", "Binary_Label"]]
        
        return df_lia

    

#get_max(df, "ipTM").to_csv("max_ipTM.csv", index=False)
#get_max(df, "LIS").to_csv("max_LIS.csv", index=False)
#get_max(df, "LIA").to_csv("max_LIA.csv", index=False)
