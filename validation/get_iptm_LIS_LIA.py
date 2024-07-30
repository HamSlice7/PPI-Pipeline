import pandas as pd

def get_max_iptm(data: pd.DataFrame, metric: str) -> pd.DataFrame: 

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

    df_iptm_max = df.groupby("Complex_Number")["ipTM"].max().reset_index()

    df_label = pd.merge(df_iptm_max, df, on=["Complex_Number", "ipTM"], how='left')

    df_label = df_label.drop_duplicates(subset="Complex_Number").reset_index(drop=True)

    if metric == "ipTM":
        df_iptm = df_label[["ipTM", "Binary_Label"]]
        return df_iptm
    
    if metric == "LIS_LIA":
        df_LIS_LIA = df_label[["LIS", "LIA", "Binary_Label"]]
        return df_LIS_LIA
  
def get_average_iptm(data: pd.DataFrame, metric: str) -> pd.DataFrame:
    """
    Return a data frame of either the average ipTM value 
    from each complex or the average LIS+LIA value.
    
    Parameters:
        csv_file: path to a csv file with labels of 1 for a positive PPI and 0 for a negative PPI for each complex
        metric (str): Either "ipTM" to return a dataframe of the average ipTM value from each complex or 
        "LIS_LIA" to return a data frame of the average LIS and LIA.
    
    Return:
        Average ipTM value from each complex or the average LIS+LIA value 
        of each complex (pd.DataFrame)
    
    """

    df = data

    #add a column to group the complexes

    num_complexes = int(df.shape[0] / 5)

    complex_number = [i for i in range(num_complexes) for _ in range(5)]

    df["Complex_Number"] = complex_number

    df_iptm_average = df.groupby("Complex_Number")["ipTM"].mean().reset_index
    print(df_iptm_average)

    df_label = pd.merge(df_iptm_average, df, on=["Complex_Number", "ipTM"], how='left')

    df_label = df_label.drop_duplicates(subset="Complex_Number").reset_index(drop=True)

    if metric == "ipTM":
        df_iptm = df_label[["ipTM", "Binary_Label"]]
        return df_iptm
    
    if metric == "LIS_LIA":
        df_LIS_LIA = df_label[["LIS", "LIA", "Binary_Label"]]
        return df_LIS_LIA
    

