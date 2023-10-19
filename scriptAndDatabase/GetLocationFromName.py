import pandas as pd
from csv import writer


# This function return a matrix or country probability for a specific name
def getSubNameProba(subName):

    file = pd.read_csv("database/nameProbaInCountry.csv")

    file = file.loc[(file["Name"] == subName.title())]

    # print("Found ", len(file.index), " matche(s) for " + subName)
    if (len(file.index) > 0):

        # print(file)
        file = file[["Country", "Probability"]]
        # print(file)
        return (file)
    
    else : 
        return pd.DataFrame({"Country" : [], "Probability" : []})


# This function multiply the probability of a country by it's population
def timesCountryPopulation(row):

    file = pd.read_csv("database/PopulationCountry.csv", delimiter=",")

    countryPop = file.loc[file["Country"] == row[0], "Population"].values

    row[1] = row[1]*int(countryPop[0])
    return row


# This function returns a country probability for a name, we decompose the name into subnames and get the probability for each subname
# After that we combine the country proba for each subname and multiply each country proba by this country population
def findCountryProba(fullName):

    # If input is not a name we return an error
    if (type(fullName) != str):
        # print("Nan name, return no data")
        return "no data"
    
    # We decompose each name into subnames (ex : "jean marc" -> "jean", "marc")
    splitedName = fullName.split(" ")

    # proba matrix for the entire name
    fullNameProba = pd.DataFrame({"Country" : [], "Probability" : []})

    # We process each subname and and concatenate each proba matrix
    for index in range (len(splitedName)):
        subNameProba = getSubNameProba(splitedName[index])
        fullNameProba = pd.concat([fullNameProba, subNameProba], ignore_index=True)

    # Sum the country proba for each country
    fullNameProba = fullNameProba.groupby("Country").aggregate({"Country":"first", "Probability":"sum"})
    
    # Multiply each country proba by this country population
    # print(fullNameProba)
    fullNameProba = fullNameProba.apply(timesCountryPopulation, axis=1)
    # Sort the proba from biggest to lowest
    fullNameProba = fullNameProba.sort_values(by="Probability", ascending=False)
    
    # print(fullNameProba)

    return fullNameProba.values.tolist()


## Function used to process all names in a database, not used anymore
def findNameAllData():

    file = pd.read_csv("DataMining/dataMined.csv")
    # file = pd.read_csv("tempData/GithubAPIData.csv")

    names = file[["name"]].to_numpy()
    country = file[["location"]].to_numpy()

    totalLength = len(names)

    probaCountry = []
    index = 0

    for name in names:
        name = name[0]
        if (index %10 == 0):
            print(index,"/", totalLength)
        index += 1

        if (index <= 52126):
            continue

        # print("Search for : " + name)
        # print("name : ")
        try : 
            listCountry = findCountryProba(name)


            ### TEMP ADDITION, NEED TO REDO THE NAME PROBABILITIES
            # Add the row to the training dataset
            newRow = [index, name, listCountry]
            with open("tempData/DataNameProbability.csv", 'a', newline="") as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(newRow)

            f_object.close()
        except Exception as e:
            print("Error with user")
            print(name)
            print(e)

        # probaCountry.append(listCountry)

    # print(names)
    # print(probaCountry)

    # file.insert(len(file.columns), "LocationFromName", probaCountry)

    # file.to_csv("DataMining/dataMinedWithCountryAndName.csv")

if __name__ == "__main__" : 
    # findNameAllData()
    test = findCountryProba("Jeremy Shao")
    print(test)

    # test2 = findCountryProba("Thomas")
    # print(test2)
