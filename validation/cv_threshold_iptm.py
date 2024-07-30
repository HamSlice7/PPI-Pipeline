import get_iptm_LIS_LIA
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn import metrics
from matplotlib import pyplot as plt

#Setting the font size for subsequent graphs
plt.rcParams.update({'font.size': 15})

#Reading in the outputted results from the pipeline pertaining to the validation data
data = pd.read_csv("validation_custom_results.csv", index_col=0)

#Calling get_max_iptm function to get the complex with the best ipTM value from each complex in data
data_iptm = get_iptm_LIS_LIA.get_max_iptm(data, "ipTM")

#Set the parameters for cv and save to variable kf
kf = KFold(n_splits=5, shuffle=True, random_state=25)

#Extract the ipTM values from data_iptm and save to variable 'x'
x = data_iptm[["ipTM"]]
#Extract the Binary labels from data_ipTM and save to variable 'y'
y = data_iptm[["Binary_Label"]]

#Initiate empty lists that will hold scoring metrics for each iteration of cv
auc_scores = []
optimal_thresholds = []
test_accuracies = []
test_precisions = []
sensitivities = []
specificities = []
test_confusion_matrices = np.zeros((2,2))

#For each iteration of CV, perform a ROC-AUC analysis to find the optimal ipTM threshold and then use this optimal threshold on the testing set.
for training_index, test_index in kf.split(data_iptm):
    x_train, x_test = x.iloc[training_index], x.iloc[test_index]
    y_train, y_test = y.iloc[training_index], y.iloc[test_index]

    #ROC and AUC
    fpr,tpr,thresholds = metrics.roc_curve(y_train, x_train)
    auc = metrics.auc(fpr,tpr)
    auc_scores.append(auc)
    
    #Add current iterating ROC curve with AUC legend to plt
    plt.plot(fpr, tpr, label = f"AUC = {auc:.3f}")

    #calculate optimal threshold via Youden J statistic (Sensitivity + Specificity - 1)
    optimal_index = np.argmax(tpr - fpr)
    optimal_threshold = thresholds[optimal_index]
    optimal_thresholds.append(optimal_threshold)

    #Append the sensitivitiy and specificity at the optimal threhsold to the sensitivities and specificities list respectfully
    sensitivity = tpr[optimal_index]
    sensitivities.append(sensitivity)
    specificity = 1 - fpr[optimal_index]
    specificities.append(specificity)

    #predict value based on optimal threshold for the "test" set
    x_test_iptm = [iptm for iptm in x_test["ipTM"]]
    y_pred = []
    
    for iptm in x_test_iptm:
        if iptm >= optimal_threshold:
            y_pred.append(1)
        else:
            y_pred.append(0)
    
    #Calculate scoring metrics for the test set
    test_accuracy = metrics.accuracy_score(y_test, y_pred)
    test_accuracies.append(test_accuracy)
    test_precision = metrics.precision_score(y_test, y_pred)
    test_precisions.append(test_precision)
    test_confusion_matrix = metrics.confusion_matrix(y_test, y_pred)
    test_confusion_matrices += test_confusion_matrix
    

#Create labels for plt and display plt
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves for each iteration of CV')
plt.legend(loc='lower right')        
plt.show()

#Calculate the average and variance for the various scoring metrics from each iteraction of CV.
average_optimal_threshold = np.average(optimal_thresholds)
print(f"Average optimal threshold:{average_optimal_threshold}")

optimal_threshold_variance = np.var(optimal_thresholds)
print(f"Variance of average optimal threshold:{optimal_threshold_variance}")

average_auc = np.average(auc_scores)
print(f"Average AUC: {average_auc}")

variance_auc = np.var(auc_scores)
print(f"AUC variance: {variance_auc}")

average_test_accuracy = np.average(test_accuracies)
#print(f"Average test accuracies:{average_test_accuracy}")

average_test_precision = np.average(test_precisions)
#print(f"Average test precision: {average_test_precision}")

average_sensitivity = np.average(sensitivities)
print(f"Average sensitivity at optimal thresholds{average_sensitivity}")

average_sensitivity_variance = np.var(sensitivities)
print(f"Average sensitivity variance: {average_sensitivity_variance}")

average_specificity = np.average(specificities)
print(f"Average specificity at optimal thresholds {average_specificity}")

variance_average_specificity = np.var(specificities)
print(f"Average specificity variance: {variance_average_specificity}")


#Display the confusion matrix which represents the sum of predicted vs true label for each testing fold at each optimal threshold
cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix=test_confusion_matrices, display_labels=[0,1])
cm_display.plot()
plt.show()