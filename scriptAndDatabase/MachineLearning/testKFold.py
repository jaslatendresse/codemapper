import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
# evaluate a logistic regression model using k-fold cross-validation
from numpy import median
from sklearn.tree import DecisionTreeClassifier
from sklearn import model_selection
import matplotlib.pyplot as plt
import numpy as np
from ast import literal_eval
from sklearn.preprocessing import label_binarize
from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score, roc_auc_score

df = pd.read_csv("../userDB/UserDataBase.csv",on_bad_lines="skip",  encoding='latin-1')
df = df[["login","locationFromUser","locationFromCommitOffset","locationFromName"]]

# Getting the length of the dataframe before doing anything so we can check values removed
totalLength = len(df.index) 


# Removing data with missing target values
df = df.replace("no data", None)
df = df[df["locationFromUser"] != "['Lost in preprocessing', 'no data']"]
df = df[df["locationFromUser"] != "['no data', 'no data']"]
df = df.dropna(subset=["locationFromUser"])
df = df.dropna(subset=["locationFromCommitOffset"])
df = df.dropna(subset=["locationFromName"])


# Display stats on the dataset
postLength = len(df.index)
stats = df.isna().sum()
print("Total length :", postLength, "(out of ",totalLength,")")
print("Missing values : ")
print(stats)


# Getting the values for the input data and the target data
LabelData = df[["locationFromUser"]].to_numpy()
UTCOffsetData = df[["locationFromCommitOffset"]].to_numpy()
NameData = df[["locationFromName"]].to_numpy()


# This function is used to transform an array that is stored as a string
def strToNumpyArray(string): # Input looks like : "[1, 1, 3, 2, 2]" as a string
    string = string[1 : -1] # Removing the "[]" from the array

    splittedString = string.split(", ")
    returnArray = []
    for value in splittedString : 
        returnArray.append(int(value))

    return returnArray


# This function return an average of what used to be a list of UTC offset
# This list has been transformed to a matrix so we can just use an average
def averageMatrix(array):
    index = 0
    nbValues = 0
    sum = 0
    for value in array:
        sum += value*(index - 12) # The array goes for UTC from -12 to +12. We just convert the index - 12 to get the UTC
        nbValues += value
        index += 1

    if (nbValues > 0): # Doing that because if array is empty, nbValues == 0 and we cant devide by 0
        return (sum/nbValues)
    else :
        return None
    

# This function retuns the median of what used to be a list of UTC offset
def medianMatrix(array):
    length = sum(array)
    count = 0

    for index in range(len(array)) :
        count += array[index]

        if (count > length/2):
            return index - 12 # -12 because the UTC offset array starts for the -12 UTC offset


# Getting the values for the data (from the csv file)
UTCOffsetInputData = []
NameInputData = []
outputData = []
timezoneData = []


# Creating target array and getting the timezone for the country
print("Adding labels to dataset")
for i in LabelData : # i variable looks like this : '["France", 2]' as a string
    temp = i[0]

    temp = temp[1:-1] # Removing the "[]""
    splitedTemp = temp.split(",")

    timezone = splitedTemp[-1]
    country = temp.replace(timezone, "")[1:-2] # we remove the first element and last because the variable is "'France'," as a string

    outputData.append(country)
    timezoneData.append(timezone)


# Creating the input array

# First, we transform the 100 offset array into a distribution matrix of thoses values
print("Adding UTC Offset to dataset")
for i in UTCOffsetData : 
    if (i[0] == None):
        tempArray = []
    else : 
        tempArray = strToNumpyArray(i[0])

    temp2Array = []
    # Transforming the [0, 0, 1, 1, 2, 3] into [2, 2, 1, 1] that represent the amount of times a variable appears (0 is present 2 times so 2 at the index 0)
    # The values can go from -12 to 14 so at index 0 we have the amount of times there is -12; at index 1 is the amount of times -11 is present and so on
    for j in range (-12, 14): 
        count = tempArray.count(j)
        temp2Array.append(count)

    UTCOffsetInputData.append(temp2Array)

# Getting the database of the Country name probability, we need it to create the input values for the names
tempDf = pd.read_csv("../database/PopulationCountry.csv")
CountryName = tempDf["Country"].to_numpy()
CountryPopulation = tempDf["Population"].to_numpy()

# Then we add the name probability per country, for country without probability we return 0
# We transform the [["France", 0.2], ["Canada", 0.1]] into [0, 0, 0, 0.2, 0, 0.1] (0 for each country without probability)
print("Adding names proba to dataset")
for i in NameData : 
    temp = i[0]
    if (isinstance(temp, float) or temp == "[]"):
        temp = "[['', 0]]"

    temp2 = literal_eval(temp) # We transform a list that is stored as string to a list element
    transpose = np.transpose(temp2) # We change the matrix with country associated with propa to a list of country and list of proba

    returnArray = []
    
    for j in range(len(CountryName)):
        if CountryName[j] in transpose[0]:
            # print("Indiv : ", (float(transpose[1][np.where(transpose[0] == CountryName[j])][0]) * CountryPopulation[j]/100)/sumProba)
            returnArray.append((float(transpose[1][np.where(transpose[0] == CountryName[j])][0])))
        else :
            returnArray.append(0)

    NameInputData.append(returnArray)


# Free some memory because next this is really heavy memory speaking
del df
# del otherTempDf

# We get some statistics about the input values that we have and the output values
count = 0
temp3Array = []

# We then check if the input values are valid. Do to so we look a the difference between the supposed offset of the world region to the median of the array
FinalInputDataset = []
FinalOutputDataset = []

for index in range (len(UTCOffsetInputData)):
    # if (index > 100):
    #     exit()
    try : 
        if (index % 1000 == 0):
            print(index)
        median = medianMatrix(UTCOffsetInputData[index])
        temp3Array.append(abs(int(timezoneData[index]) - median))
        tempFinal = []

        if (abs(int(timezoneData[index]) - median) < 2 ):
            count += 1
            tempFinal = np.concatenate((UTCOffsetInputData[index], NameInputData[index]))
            FinalInputDataset.append(tempFinal)
            FinalOutputDataset.append(outputData[index])

    except :
        print(index, " : found error input")
        print(UTCOffsetInputData[index], " : ", timezoneData[index])

# Display the amount of valid inputs and some stats on them
print("size input : ", np.array(FinalInputDataset).itemsize*np.array(FinalInputDataset).size)
print("size output : ", np.array(FinalOutputDataset).itemsize*np.array(FinalOutputDataset).size)
print("Valid input : ", count)

unique = np.unique(FinalOutputDataset, return_counts=True)
lowCountry = []
print("Final dataset : ",count," users; ",len(unique[0])," classes ")
for i in range (len(unique[0])):
    
    percentage = float(unique[1][i]/len(FinalOutputDataset)*100)
    print(unique[0][i], " : ", unique[1][i], " (",percentage,"%)")
    if (unique[1][i] < 5):
        lowCountry.append(unique[0][i])

print(lowCountry)
print(len(lowCountry))

i = 0
for j in range (len(FinalInputDataset)):

    if (FinalOutputDataset[i] in lowCountry):
        del FinalInputDataset[i]
        del FinalOutputDataset[i]
        i -= 1
    i += 1


unique1 = np.unique(FinalOutputDataset, return_counts=True)

print("After removing low class : Input Length = ", len(FinalInputDataset), "; nb class = ", len(unique1[0]))

X = FinalInputDataset
Y = []
for output in FinalOutputDataset : 
    Y.append(np.where(unique1[0] == output)[0][0])
binaryLabelClass = label_binarize(FinalOutputDataset, classes=unique1[0])


models = []
models.append(('LR', LogisticRegression()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('DT', DecisionTreeClassifier()))
models.append(('RF', RandomForestClassifier()))
models.append(('SVM', SVC(kernel='linear')))


results = []
names = []
totalOut = ""


def print_results(name, measure, mean):
    msg = "%s-%s: %s " % (name, measure, mean)
    print(msg)
    global totalOut 
    totalOut = totalOut + msg + "\n"

for name, model in models:
    kfold = model_selection.StratifiedKFold(n_splits=5, shuffle=True)

    precision_results = model_selection.cross_val_score(model, X, Y, cv=kfold,scoring=make_scorer(precision_score, average="weighted", zero_division=0))
    print_results(name, "Precision", precision_results.mean())


    recall_results = model_selection.cross_val_score(model, X, Y, cv=kfold, scoring=make_scorer(recall_score, average="weighted", zero_division=0))
    print_results(name, "Recall", recall_results.mean())

    cv_results = model_selection.cross_val_score(model, X, Y, cv=kfold, scoring=make_scorer(f1_score, average="weighted", zero_division=0))
    print_results(name, "F1", cv_results.mean())
    
    AUC_results = model_selection.cross_val_score(model, X, Y, cv=kfold, scoring='roc_auc_ovr')
    print_results(name, "AUC", AUC_results.mean())

    results.append(cv_results)
    names.append(name)
    totalOut = totalOut + "==================================\n"

    print("==================================")

print(totalOut)

fig = plt.figure()
fig.suptitle('Algorithm Comparison')
ax = fig.add_subplot(111)
plt.boxplot(results)
ax.set_xticklabels(names)
plt.show()