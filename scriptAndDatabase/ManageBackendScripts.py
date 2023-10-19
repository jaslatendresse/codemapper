import sys

sys.path.append('')

import pandas as pd
import numpy as np
import time
import multiprocessing
import random
import pickle
from ast import literal_eval
from csv import writer
import json

from GenerateDataFromGithubAPI import getData
from GetLocationFromCommitDates import getTimeCommit
from GetLocationFromUser import findCountry
from GetLocationFromName import findCountryProba
from GetLocationFromEmail import getEmailLocation

gh_token = json.load(open("../config.json", "r"))["GH_TOKEN"]

# This function is used to transform an array that is stored as a string
def strToNumpyArray(string): # Input looks like : "[1, 1, 3, 2, 2]" as a string
    string = string[1 : -1] # Removing the "[]" from the array

    splittedString = string.split(", ")
    returnArray = []
    for value in splittedString : 
        returnArray.append(int(value))

    return returnArray


# This function retuns the median of what used to be a list of UTC offset
def medianMatrix(array):
    length = sum(array)
    count = 0

    for index in range(len(array)) :
        count += array[index]

        if (count > length/2):
            return index - 12 # -12 because the UTC offset array starts for the -12 UTC offset


# This function is used to shape location from a user. We processed this information and now it is stored as ["COUNTRY", TIMEZONE]. 
# Depending the way the database is handled this variable can be used as a string of a list.
def shapeLocationFromUser(array):
    if (type(array) == list):
        return array[0], array[1]
    
    temp = array[1:-1] # Removing the "[]""
    splitedTemp = temp.split(",")

    timezone = splitedTemp[-1]
    country = temp.replace(timezone, "")[1:-2] # we remove the first element and last because the variable is "'France'," as a string

    return country, timezone


# This function is used to transform the list of commit offset to a matrix (like a One Hot Encoding)
def shapeLocationFromCommitOffset(array):
    if (array == "no data"):
        array = []
    elif (type(array) == str):
        array = strToNumpyArray(array)

    temp2Array = []
    # Transforming the [0, 0, 1, 1, 2, 3] into [2, 2, 1, 1] that represent the amount of times a variable appears (0 is present 2 times so 2 at the index 0)
    # The values can go from -12 to 14 so at index 0 we have the amount of times there is -12; at index 1 is the amount of times -11 is present and so on
    for j in range (-12, 14): 
        count = array.count(j)
        temp2Array.append(count)

    return temp2Array


# This function is a One Hot Encoding for all the country proba. We return a matrix that represent all the country possibles with their adequat probability. 
def shapeLocationFromNameProba(array):

    tempDf = pd.read_csv("database/PopulationCountry.csv", encoding='latin-1')
    CountryName = tempDf["Country"].to_numpy()

    if (type(array) == float or array == "[]" or array == "no data" or array == []):
        array = [["", 0]]

    elif (type(array) != list):
        array = literal_eval(array)

    transpose = np.transpose(array) # We change the matrix with country associated with propa to a list of country and list of proba

    returnArray = []
    for j in range(len(CountryName)):
        if CountryName[j] in transpose[0]:
            returnArray.append((float(transpose[1][np.where(transpose[0] == CountryName[j])][0])))
        else :
            returnArray.append(0)

    return returnArray



def processUser(tempData):
    time.sleep(random.random())
    gh_token = gh_token

    owner = tempData[0]
    package = tempData[1]
    login = tempData[2]
    location = tempData[3]
    name = tempData[4]
    email = tempData[5]

    good = 0
    while (good != 1):
        try : 
            processedCommitOffset = getTimeCommit(login, owner, package, gh_token)
            good = 1
        except Exception as e:
            print("ERROR getting users commit dates : ", login)
            processedCommitOffset = "no data"

            if (e == "Blocked by Github API (code 403)"):
                print("GitHub token exhausted : ", gh_token)
            else : 
                print(e)
                good = 1
                print("ignoring user")


    processedLocation = findCountry(location)
    processedName = findCountryProba(name)
    processedEmail = getEmailLocation(email)

    # Save last update of the informations
    t = time.localtime()
    current_time = time.strftime("%DT%H:%M:%S", t)

    row = [login,name,email,location,processedLocation,processedCommitOffset,processedName,processedEmail,current_time]
    # print(row)
    return row



def main(owner, package):
    
    print("---- (1/4) Getting contributors list and informatons -----")

    usersDf = getData(owner, package)

    # If after the entire loop there is still no user, we quit
    if (usersDf.empty):
        print("Couldnt get contributor list, quitting")
        return


    # Checking if the users we got for this packages are allready in our database
    userDatabase = pd.read_csv("userDB/UserDataBase.csv", delimiter=",", on_bad_lines="skip", encoding="utf-8")

    # Get users already processed
    users = userDatabase[["login"]].to_numpy()
    ArrayUserDB = []
    for user in users:
        ArrayUserDB.append(user[0])
        
    # Get the user from the package
    users = usersDf[["login"]].to_numpy()  
    ArrayUserDf = []
    for user in users:
        ArrayUserDf.append(user[0])
    
    # We select all the users from this package already in the database (already processed)
    userInDatabase = userDatabase[userDatabase["login"].isin(ArrayUserDf)]

    # Removing the rows with an user already preprocessed
    userNotInDatabase = usersDf[~usersDf["login"].isin(ArrayUserDB)]

    print("New users to process : ", len(userNotInDatabase))

    tempData = userNotInDatabase[["owner", "package", "login", "location", "name",  "email"]].values

    print("---- (2/4) Processing new users informations -------------")

    # Using multiprocessing to speed-up the requests
    pool = multiprocessing.Pool(processes=10)
    returnDatabase = pool.map(processUser, tempData)


    returnDatabaseDf = pd.DataFrame(returnDatabase, columns=["login","name","email","location","locationFromUser","locationFromCommitOffset","locationFromName","locationFromEmail","timeLastUpdate"])

    # Save the new users processed in the database
    if (len(returnDatabaseDf.index) > 0):

        for index in range (len(returnDatabase)):
            with open("userDB/UserDatabase.csv", 'a', newline="",  encoding="utf-8") as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(returnDatabase[index])


    packageData = pd.concat([userInDatabase, returnDatabaseDf, usersDf])
    packageData = packageData.groupby(by="login", as_index=False).first()

    packageData = packageData[["login", "contributions", "locationFromUser", "locationFromCommitOffset", "locationFromName", "locationFromEmail"]]

    load_model = pickle.load(open("MachineLearning/modelSaved", "rb"))
    classes = load_model.classes_

    print("---- (3/4) Running decision algorithm --------------------")  
    decisionLocation = []
    for index, row in packageData.iterrows(): 

        userLocation, timezone = shapeLocationFromUser(row["locationFromUser"])
        commitOffsetInput = shapeLocationFromCommitOffset(row["locationFromCommitOffset"])
        NameProbaInput = shapeLocationFromNameProba(row["locationFromName"])

        inputModel = np.concatenate([commitOffsetInput, NameProbaInput])

        try : 
            # Really ugly way to do it :(, need to change for the future 
            if (timezone != "no data" and userLocation != "Lost in preprocessing" and userLocation != "no data" and medianMatrix(commitOffsetInput) != None and abs(int(timezone) - medianMatrix(commitOffsetInput)) <= 2):
                decision = userLocation
                # print("going for user location : ",decision)
            else : 
                raise Exception
        except :
            # print("Using ML model")
            y_predict = load_model.predict_proba([inputModel])
            if (max(y_predict[0]) >= 0.5):
                indexMax = np.where(y_predict[0] == max(y_predict[0]))

                decision = classes[indexMax[0][0]]
                # print("Confident enough, going for ML prediction : ", decision)
            else :
                # print("Not confident enough (",max(y_predict[0]),"), Unknown location")
                decision = "Unknown"
        
        decisionLocation.append(decision)


    packageData.insert(len(packageData.columns), "decision", decisionLocation)    
    packageData = packageData[["login", "contributions", "decision"]]
    packageData = packageData.groupby("decision")["contributions"].sum()
    packageData = packageData.sort_values(ascending=False)
    print(packageData)

    # print(packageData)
    print("---- (4/4) Saving data in database -----------------------")

    packageData.to_csv("userDB/dataForFrontend.csv")
    countryList = packageData.index.values.tolist()
    countryContributions = packageData.values.tolist()
    save = owner + "/" + package , countryList , countryContributions, time.strftime("%DT%H:%M:%S", time.localtime())

    with open("userDB/DecisionDatabase.csv", 'a', newline="",  encoding="utf-8") as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(save)

if __name__ == "__main__" : 

    ## THIS PART IS FOR THE WEBSITE, DEALING WITH 1 PACKAGE AT A TIME
    empty = pd.DataFrame(list())
    empty.to_csv("userDB/dataForFrontend.csv")
    file = open("userDB/tempPackage.txt", "r")
    package = file.read()

    splittedPackage = package.split("/")

    df = pd.read_csv("userDB/DecisionDatabase.csv", delimiter=",")

    storedDecision = df[df["repo"] == package]
    print(storedDecision)
    if (len(storedDecision.index) > 0):
        print("package allready processed")
        processedRepo = storedDecision.iloc[0]
        temp = literal_eval(processedRepo["countryList"])
        data = {"decision" : literal_eval(processedRepo["countryList"]),
                "contributions" : literal_eval(processedRepo["contributionsList"])}
        decision = pd.DataFrame(data=data)
        print(decision)
        decision.to_csv("userDB/dataForFrontend.csv", index=False)
        exit()


    print("New package to process")
    owner = splittedPackage[0]
    package = splittedPackage[1]

    try : 
        main(owner, package)
    except Exception as e:
        print("Error with package name")
        print(e)
        exit()
