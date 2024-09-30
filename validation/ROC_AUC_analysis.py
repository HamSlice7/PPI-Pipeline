import get_max
import get_mean
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn import metrics
from matplotlib import pyplot as plt

#Setting the font size for subsequent graphs
plt.rcParams.update({'font.size': 15})

#Reading in the outputted results from the pipeline pertaining to the validation data
data = pd.read_csv("custom_results_5_recycling.csv", index_col=0)

#Calling get_max_iptm function to get the complex with the best ipTM value from each complex in data
data_iptm = get_max.get_max(data, "ipTM")
data_LIS = get_max.get_max(data, "LIS")
data_LIA = get_max.get_max(data, "LIA")
data_mean = get_mean.get_mean(data)


def cross_validation_ROC(data: pd.DataFrame, metric: str):

    """
    Perform 5-fold cross validation to determine classification performance of a scoring metric derived from the output
    of AlphaFold-Multimer. 

    Parameters:
        - data (pd.DataFrame): A dataframe consisting of two columns, one for the chosen scoring metric for each complex and the 
         binary label indicating whether the complex is experimentally validated or not (1 or 0 respectively)
        - metric (str): To indicate which scoring metric is being used to classify the two classes of peptidase-inhibitor complexes

    Return:
        - The receiver operator curves (ROC) for each iteration of cross validation
        - The average true positive rate (TPR) across 5 interations of cross validation
        - The false positive rate (FPR) across 5 interations of cross validation
        - The average threshold across 5 iterations of cross validation via Youden's J statistic and the threhsold associated with
          the lowest non-zero FPR
        - The average area under the curve (AUC) across the 5 iterations of cross validation
        - A confusion matrix of the aggregation of the classification performance for the current iterating threshold across 5 iterations
          of 5 fold cross validation
    

    """


    #Set the parameters for cv and save to variable kf
    kf = KFold(n_splits=5, shuffle=True, random_state=25)

    #Extract the scroing values from data and save to variable 'x'
    x = data[[metric]]
    #Extract the Binary labels from data_ipTM and save to variable 'y'
    y = data[["Binary_Label"]]

    #Initiate empty lists that will hold scoring metrics for each iteration of cv
    auc_scores = []
    min_fpr_list = []
    min_fpr_tpr_list = []
    min_fpr_threshold_list = []
    optimal_thresholds = []
    yj_fpr_list = []
    test_accuracies = []
    test_precisions = []
    sensitivities = []
    specificities = []
    test_confusion_matrices = np.zeros((2,2))

    #For each iteration of CV, perform a ROC-AUC analysis to find the optimal ipTM threshold and then use this optimal threshold on the testing set.
    for training_index, test_index in kf.split(data_iptm):
        x_train, x_test = x.iloc[training_index], x.iloc[test_index]
        y_train, y_test = y.iloc[training_index], y.iloc[test_index]

        print(f"Training index: {len(training_index)}")
        print(f"Test index: {len(test_index)}")

        #ROC and AUC
        fpr,tpr,thresholds = metrics.roc_curve(y_train, x_train)
        auc = metrics.auc(fpr,tpr)
        auc_scores.append(auc)

        #print(f"fpr:{fpr}")
        #print(f"tpr{tpr}")
        #print(f"thresholds:{thresholds}")

        #finding the minumum non-zero fpr
        min_fpr = (min(n for n in fpr if n != 0))
        #appending the minumum non-zero fpr for the current iteration of cross validation
        min_fpr_list.append(min_fpr)

        #Get indices of all occurances of the minimum FPR
        min_fpr_indices = np.where(fpr == min_fpr)[0]
        #print(f"indices where fpr is equal to min_fpr:{min_fpr_indices}")

        #Selecting the min FPR indice that maximizes the TPR
        min_fpr_indices_best_tpr = min_fpr_indices[np.argmax(tpr[min_fpr_indices])]
        #print(f"FPR index that maximizes the TPR: {min_fpr_indices_best_tpr}")

        #finding the index assocaited with the non-zero fpr
        #min_fpr_index = list(fpr).index(min_fpr)
        #print(f"min_fpr_index{min_fpr_index}")

        #finding the best tpr rate associated with the minimum non-zero fpr
        min_fpr_tpr = tpr[min_fpr_indices_best_tpr]
        #print(f"Best TPR associated with the minimum non-zero FPR:{min_fpr_tpr}")

        #appending the tpr assocaited with the min fpr to min_fpr_tpr_list
        min_fpr_tpr_list.append(min_fpr_tpr)
        #finding the threshold associated with the minimum non-zero fpr
        min_fpr_threshold = thresholds[min_fpr_indices_best_tpr]
        #print(f"Finding the threshold associated with the minimum non-zero FPR that maxizmizes TPR: {min_fpr_threshold}")
        #appending the min fpr threshold to min_fpr_threshold_list
        min_fpr_threshold_list.append(min_fpr_threshold)
    
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
        yj_fpr = fpr[optimal_index]
        yj_fpr_list.append(yj_fpr)

        #predict value based on optimal threshold for the "test" set
        x_test_scoring_metric = [scoring_value for scoring_value in x_test[metric]]
        y_pred = []
    
        for scoring_value in x_test_scoring_metric:
            if scoring_value >= min_fpr_threshold:
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
    
    

    #print(f"Optimal thresholds for {metric} based on Youden's J statistic: {optimal_thresholds}")
    #print(f"Optimal threshold for {metric} based on minimizing FPR: {min_fpr_threshold_list}")
    
    #Create labels for plt and display plt
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curves for each iteration of CV for {metric}')
    plt.legend(loc='lower right')        
    plt.show()

   # print(f"FPR associated with smallest non-zero FPR:{min_fpr_list}")
   # print(f"FPR assocaited with Youden's J statistic:{yj_fpr_list}")
    #print(f"TPR associated with the smallest non-zero TPR:{min_fpr_tpr_list}")
    #print(f"TPR assocaited with Youden's J statistic: {sensitivities}")

    #Calculating the average optimal threshold that minimize FPR across the 5 iterations of CV
    print(f"Average threshold associated with the minimum fpr across the 5 iterations of CV:{round(np.average(min_fpr_threshold_list),3)} +/- {round(np.std(min_fpr_threshold_list),3)}")

    #Calculate the average optimal threshold based on Youden's J statistc across the 5 iterations of CV
    print(f"Average optimal threshold for {metric} based on Youden's J statistic :{round(np.average(optimal_thresholds),3)} +/- {round(np.std(optimal_thresholds),3)}")

    #Calculating the average FPR at the optimal threshold that minimizes FPR across the 5 iterations of CV
    print(f"Average FPR at the optimal threshold that minimizes FPR:{round(np.average(min_fpr_list),3)} +/- {round(np.std(min_fpr_list),3)}")

    #Calculating the average FPR at the optimal threshold based on Youden's J statistic across the 5 iterations of CV
    print(f"Average FPR at the optimal threshold based on Youden's J statistic: {round(np.average(yj_fpr_list),3)} +/- {round(np.std(yj_fpr_list),3)}")

    #Calculating the average TPR at the optimal threshold that minimizes FPR across the 5 iterations of CV
    print(f"Average TPR at the optimal threshold that minimizes FPR: {round(np.average(min_fpr_tpr_list),3)} +/- {round(np.std(min_fpr_tpr_list),3)}")

    #Calculating the average FPR at the optimal threhsold based on Youden's J statistic across the 5 interations of CV
    print(f"Average TPR at the optimal threshold based on Youden's J statistic:{round(np.average(sensitivities),3)} +/- {round(np.std(sensitivities),3)}")



    optimal_threshold_variance = np.var(optimal_thresholds)
    #print(f"Variance of average optimal threshold for {metric}:{optimal_threshold_variance}")

    
    print(f"Average AUC for {metric}: {round(np.average(auc_scores),3)} +/- {round(np.std(auc_scores),3)}")

    variance_auc = np.var(auc_scores)
    #print(f"AUC variance for {metric}: {variance_auc}")
  

    average_test_accuracy = np.average(test_accuracies)
    #print(f"Average test accuracies:{average_test_accuracy}")

    average_test_precision = np.average(test_precisions)
    #print(f"Average test precision: {average_test_precision}")

    average_sensitivity = np.average(sensitivities)
    #print(f"Average sensitivity at optimal thresholds for {metric}: {average_sensitivity}")

    average_sensitivity_variance = np.var(sensitivities)
    #print(f"Average sensitivity variance for {metric}: {average_sensitivity_variance}")

    average_specificity = np.average(specificities)
    #print(f"Average specificity at optimal thresholds for {metric}: {average_specificity}")

    variance_average_specificity = np.var(specificities)
    #print(f"Average specificity variance for {metric}: {variance_average_specificity}")


    #Display the confusion matrix which represents the sum of predicted vs true label for each testing fold at each optimal threshold
    cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix=test_confusion_matrices, display_labels=[0,1])
    cm_display.plot()
    plt.show()

#cross_validation_ROC(data_iptm, "ipTM") #Max ipTM
cross_validation_ROC(data_mean, "ipTM") #Mean ipTM
#cross_validation_ROC(data_LIS, "LIS") #Max LIS
#cross_validation_ROC(data_mean, "LIS") #Mean LIS
#cross_validation_ROC(data_LIA, "LIA") #Max LIA
#cross_validation_ROC(data_mean, "LIA") #Mean LIA
