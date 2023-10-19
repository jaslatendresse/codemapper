import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt


import random
import pickle
from ast import literal_eval



# # Opening the file 
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

# We get some statistics about the input values that we have and the output values
count = 0
temp3Array = []

# We then check if the input values are valid. Do to so we look a the difference between the supposed offset of the world region to the median of the array
FinalInputDataset = []
FinalOutputDataset = []

for index in range (len(UTCOffsetInputData)):
    try : 
        if (index % 1000 == 0):
            print(index)
        # average = averageMatrix(UTCOffsetInputData[index])
        median = medianMatrix(UTCOffsetInputData[index])
        # print(index," : ",inputData[index]," : ",outputData[index],"(timezone expected : ",timezoneData[index],", average : ",average,")")
        # try : 
        temp3Array.append(abs(int(timezoneData[index]) - median))

        # and np.count_nonzero(namesEncoded[index] == 1) == 2
        if (abs(int(timezoneData[index]) - median) < 2 ):
            count += 1
            # FinalInputDataset.append(np.concatenate((UTCOffsetInputData[index], NameInputData[index])))
            tempFinal = np.concatenate((UTCOffsetInputData[index], NameInputData[index]))
            # print(tempFinal)
            FinalInputDataset.append(tempFinal)
            # FinalInputDataset.append(UTCOffsetInputData[index])
            FinalOutputDataset.append(outputData[index])

    except :
        print(index, " : found error input")
        print(UTCOffsetInputData[index], " : ", timezoneData[index])


# Display the amount of valid inputs and some stats on them
print("size input : ", np.array(FinalInputDataset).itemsize*np.array(FinalInputDataset).size)
print("size output : ", np.array(FinalOutputDataset).itemsize*np.array(FinalOutputDataset).size)
print("Valid input : ", count)

# Temporary addition, just to show the difference between the supposed utc offset and the average of the utc offset
plt.hist(temp3Array, bins=15, range=(0, 15))
plt.show()


# Displaying distribution of the final dataset
unique = np.unique(FinalOutputDataset, return_counts=True)
print("Final dataset : ",count," users; ",len(unique[0])," classes ")
for i in range (len(unique[0])):
    
    percentage = float(unique[1][i]/len(FinalOutputDataset)*100)
    print(unique[0][i], " : ", unique[1][i], " (",percentage,"%)")


# Creating training dataset without the oversampling
x_train = []
y_train = []
x_test = []
y_test = []

# Choosing randomly between train and test to mix the data
for i in range (len(FinalInputDataset)):
    rand = random.random()
    if rand < 0.2 : 
        x_test.append(FinalInputDataset[i])
        y_test.append(FinalOutputDataset[i])
    else :
        x_train.append(FinalInputDataset[i])
        y_train.append(FinalOutputDataset[i])


# Creating a random forest and using cross validation to check to f1 score, then fitting the model
print("Creating random forest classifier")
clf1 = RandomForestClassifier(criterion= 'gini', max_depth= 50)

clf1.fit(x_train, y_train)
y_predict = clf1.predict(x_test)

y_predict_proba  = clf1.predict_proba(x_test)

accuracy = accuracy_score(y_predict, y_test)

print("Accuracy : ")
print(accuracy)

RegionDf = pd.read_csv("../database/countryToRegion.csv", delimiter=";")

# Displaying some stats on the distribution of correct prediction related to the confidence score
print("Doing stats on results (",len(y_predict_proba),"values)")
classes = clf1.classes_

graphGood = []
graphBad = []
graphUnknown = []
step = []

for j in range(40, 70):
    goodPrecidtion = []
    badPrediction = []
    countUnknown = 0
    countGoodPrediction = 0
    countBadPrediction = 0
    countRegion = 0
    threshold = j/100
    for index in range (len(y_predict_proba)) :

        outputExpected = y_test[index]
        indexOutputExpected = np.where(classes == outputExpected)

        row = y_predict_proba[index]
        maxRow = max(row)
        indexMaxRow = np.where(row == maxRow)

        if (len(indexMaxRow[0]) < 2 and indexOutputExpected == indexMaxRow[0][0]):
            if (maxRow >= threshold):
                countGoodPrediction += 1
            else : 
                countUnknown += 1
            goodPrecidtion.append(maxRow)
        else :
            if (maxRow >= threshold):
                countBadPrediction += 1
            else : 
                countUnknown += 1
            badPrediction.append(maxRow)

        if (RegionDf.loc[RegionDf["country"] == outputExpected, "region"].values == RegionDf.loc[RegionDf["country"] == classes[indexMaxRow[0][0]], "region"].values):
            countRegion += 1


    print("With threshold of ",threshold," : ")
    print("Unknown : ", countUnknown/len(y_predict_proba)*100)
    print("Good : ", countGoodPrediction/len(y_predict_proba)*100)
    print("Bad : ", countBadPrediction/len(y_predict_proba)*100)

    step.append(j/100)
    graphGood.append(countGoodPrediction/len(y_predict_proba)*100)
    graphBad.append(countBadPrediction/len(y_predict_proba)*100)
    graphUnknown.append(countUnknown/len(y_predict_proba)*100)


plt.plot(step, graphGood, label="Correct predictions")
plt.plot(step, graphBad, label="Wrong predictions")
#x-axis label
plt.xlabel('Accuracy')
#y-axis label
plt.ylabel('Percentage of predictions')
#plt.plot(step, graphUnknown, label="ratioUnknown")
plt.legend()
plt.show()

# # Saving the model in a file
filename = "modelSaved"
pickle.dump(clf1, open(filename, "wb"))