import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

#Initiating the font sizes for the subsequent plt plots
plt.rcParams.update({'font.size': 15})

#Reading in the the results for the validation data.
data = pd.read_csv("validation_custom_results.csv")

#Extracting the ipTM values and the binary label values as 'data_iptm'
data_iptm = data[["ipTM", "Binary_Label"]]

#Extracting the LIS values and the binary label values as 'data_LIS'
data_LIS = data[["LIS", "Binary_Label"]]

#Extracting the LIA values and the bianry label values as 'data_LIA'
data_LIA = data[["LIA", "Binary_Label"]]

# Initiating a box plot with binary labels on the x axis and ipTM values on the y axis.
sns.boxplot(x='Binary_Label', y='ipTM', data=data_iptm)

# Add labels and title
plt.xlabel('Binary Label')
plt.ylabel('ipTM')
plt.title('Distribution of ipTM for validation data set')

#Display the plot
plt.show()

# Initiating a box plot with binary labels on the x axis and LIS values on the y axis.
sns.boxplot(x='Binary_Label', y='LIS', data=data_LIS)

# Add labels and title
plt.xlabel('Binary Label')
plt.ylabel('LIS')
plt.title('Distribution of LIS for validation data set')

#Display the plot
plt.show()

# Initiating a box plot with binary labels on the x axis and LIA values on the y axis.
sns.boxplot(x='Binary_Label', y='LIA', data=data_LIA)

# Add labels and title
plt.xlabel('Binary Label')
plt.ylabel('LIA')
plt.title('Distribution of LIS for validation data set')

#Display the plot
plt.show()