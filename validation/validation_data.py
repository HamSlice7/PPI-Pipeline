import pandas as pd
import random

seed = 25

df_validation = pd.read_csv("df_validation.csv")

n_samples_per_family = 5

df_validation_group = df_validation.groupby('Peptidase Family')


#Sample 5 rows from each of the peptidase families
df_validation_sampled = df_validation_group.apply(lambda x: x.sample(n = n_samples_per_family, random_state = seed)).reset_index(drop=True)

#Merge df_validation and df_validation_sampled and add in an extra column to indicate from which data frame the row is from. Will indicate which rows are only in df_validation (unsampled)
df_all = df_validation.merge(df_validation_sampled, on=['Peptidase', 'Peptidase Family', 'Inhibitor', 'Inhibitor Family'], how='left', indicator='True') 

#Isolate the rows that are not found in the sampled data frame.
df_validation_positive = df_all[df_all['True'] == 'left_only']

df_validation_positive = df_validation_positive.drop('True', axis=1)


inhibitor_families = df_validation_sampled['Inhibitor Family'].unique()

random_pairs = []

inhibitors_negative_set = []
count = 0
# Generate a new dataframe with randomized peptidase-inhibitor pairs that are not from the same family
while count < 20:
    peptidase = df_validation_sampled['Peptidase'][count]
    peptidase_family = df_validation_sampled['Peptidase Family'][count]
    inhibitor_family = random.choice([fam for fam in inhibitor_families if fam != peptidase_family])
    inhibitor = df_validation_sampled[df_validation_sampled['Inhibitor Family'] == inhibitor_family]['Inhibitor'].sample(n=1).values[0]
    new_pair = ({'Peptidase': peptidase, 'Peptidase Family': peptidase_family, 'Inhibitor': inhibitor, 'Inhibitor Family': inhibitor_family})
    if new_pair not in random_pairs:
        random_pairs.append(new_pair)
        count += 1
    else:
        pass
            
df_validation_negative = pd.DataFrame(random_pairs)

df_validation_final = pd.concat([df_validation_positive, df_validation_negative], ignore_index=True, axis=0)

df_validation_final.to_csv("df_validation_final.csv")

