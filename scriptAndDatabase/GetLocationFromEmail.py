import pandas as pd
import numpy as np


def findLocationFromDomain(domain):
    file = pd.read_csv("database/geonames-all-cities-with-a-population-1000.csv", on_bad_lines="skip", delimiter=";")

    # We remove all the data that we wont use and order it from the biggest population to the lowest
    # We do that in case we first 2 cities with the same name
    file = file[["Country Code", "Country name EN", "Population"]]
    file = file.sort_values(by=["Population"], ascending=False)

    file = file[file["Country Code"] == domain.upper()]

    # print("Checking domain : " + domain)
    # print("Found ", len(file.index), "matche(s)")
    if (file.empty):
        return "no data"
    
    else : 
        return file["Country name EN"].iloc[0]



# Get the email and return the email country of the email domain
def getEmailLocation(email):

    if (type(email) != str):
        # print("no email found, skippping")
        return "no data" 
    
    SplitedEmail = email.split(".")
    temp = findLocationFromDomain(SplitedEmail[-1])
    return(temp)



def matchEmailAlldata():

    file = pd.read_csv("DataMining/dataMined.csv", delimiter=",", on_bad_lines="skip",  encoding='latin-1')

    emails = file[["email"]].to_numpy()

    returnArray = []
    totalLength = len(emails)
    index = 0

    for email in emails:
        index += 1
        print(index, "/", totalLength)

        email = email[0] # Using the "to_numpy()" method we get an array of single arrays, we need to remove the useless layer of "[]"
        
        if (index > 100):
            break
        

        temp = getEmailLocation(email)
        print(temp)
        returnArray.append(temp)

    print(returnArray)


if __name__ == "__main__" : 
    matchEmailAlldata()