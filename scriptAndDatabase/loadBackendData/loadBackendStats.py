import pandas as pd
import numpy as np
from ast import literal_eval


def strToNumpyArray(string): # Input looks like : "[1, 1, 3, 2, 2]" as a string
    string = string[1 : -1] # Removing the "[]" from the array

    splittedString = string.split(", ")
    returnArray = []
    for value in splittedString : 
        returnArray.append(int(value))

    return returnArray

def average(x, total):
    return (x.sum()/total*100)


def loadGlobalStats():
    countryRegionDf = pd.read_csv("../database/countryToRegion.csv", delimiter=";")

    df = pd.read_csv("../userDB/DecisionDatabase.csv" , encoding="utf-8")

    arrayCountry = countryRegionDf["country"].values
    arrayContribution = []
    total = 0

    for i in range (len(arrayCountry)):
        arrayContribution.append(0)

    for index, row in df.iterrows():

        countryList = literal_eval(row["countryList"])
        contributionList = literal_eval(row["contributionsList"])
        subTotal = sum(contributionList)

        for i in range(len(countryList)):
            try : 
                if (countryList[i] == "Unknown"):
                    continue

                arrayContribution[np.where(arrayCountry == countryList[i])[0][0]] += contributionList[i]/subTotal
                total += contributionList[i]
            except Exception as e: 
                print(index, "/", len(df.index)," : Error with location : ", countryList[i])
                print(e)


    countryRegionDf.insert(len(countryRegionDf.columns), "contributions", arrayContribution)
    countryRegionDf = countryRegionDf.groupby("region")["contributions"].apply(average, len(df.index))
    countryRegionDf = countryRegionDf.sort_values(ascending=False)
    print(countryRegionDf)
    countryRegionDf.to_csv("backendStats.csv")


loadGlobalStats()