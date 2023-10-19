import pandas as pd
import re


# We open the database and sort by population (biggest population first) so when we find 2 cities/country with the same name we favor the biggest one
file = pd.read_csv("database/geonames-all-cities-with-a-population-1000.csv", on_bad_lines="skip", delimiter=";")

# We remove all the data that we wont use and order it from the biggest population to the lowest
# We do that in case we first 2 cities with the same name
file = file[["Name","ASCII Name", "Country Code", "Country name EN", "Population", "Timezone"]]
file = file.sort_values(by=["Population"], ascending=False)


# This function allows us to find a match between the location entered by the user and a real location
# We first split the location and try each "sub value" from the split (usually people enter the location from the most precise to the most unprecise ex : Montréal, Quebec, Canada)
# If none of thoses "sub value" works we take the first one (most likely the city name) and we try combination without the first element, without the last etc.. untill we find a match
# We need to be carefull to not destroy the location name to much because we could find a match that isnt relevent
# For exemple : location = "San Francisco Bay Area/CA/USA"
# We cant try all the words in "San Fransisco Bay Area" because "San" in  a city in Mexico
def findMatch(location): 

    clean_location = re.split(',|:|/', location)

    for subLocation in clean_location :
        subLocation = subLocation.strip() 
        # print("Trying sublocation : " + subLocation.title())
        if (subLocation.upper() in file.values):
            return(subLocation.upper())
        elif (subLocation.title() in file.values):
            # print("Returning sublocation : " + subLocation.title())
            return (subLocation.title())
        # else :
            # print("Not sublocation : " + subLocation)

    splitLocation = clean_location[0].split(" ")

    if (len(splitLocation) == 1):
        # print("Lost in preprocessing ------------------------------") #This print is for debug purposes
        return "Lost in preprocessing"
    else :
        withoutLastElement = " ".join(splitLocation[:-1])
        # print("Trying without last : " + withoutLastElement)

        withLastReturn = findMatch(withoutLastElement)

        if (withLastReturn == "Lost in preprocessing"):

            withoutFirstElement = " ".join(splitLocation[1:])
            # print("Trying without first : " + withoutFirstElement)

            return (findMatch(withoutFirstElement))
        else :

            return(withLastReturn)


# After finding a country we want to have the corresponding UTC offset 
def findTimezone(timezone):

    file = pd.read_csv("database/timezones.csv")

    if (timezone in file.values):
        filtered_df = file[file["timezone"] == timezone]
        return int((filtered_df["offset"].iloc[0])/3600) # The offset in the database is in second, we prefer to save it in second
    else :
        return ("no data")


# This function trys to find a country and a UTC offset for a location entered by a user. 
def findCountry(location):

    if (location == "No Data" or type(location) != str):
        return ["no data", "no data"]

    match = findMatch(location)
    
    # Check if the match is a country
    if (match in file["Country name EN"].values):
        filtered_df = file[file["Country name EN"] == match]

        timezoneArea = filtered_df["Timezone"].iloc[0]
        timezone = findTimezone(timezoneArea)

        return [match, timezone]
    
    if (match in file["Country Code"].values):
        filtered_df = file[file["Country Code"] == match]
        country = filtered_df["Country name EN"].iloc[0]

        timezoneArea = filtered_df["Timezone"].iloc[0]
        timezone = findTimezone(timezoneArea)

        return [country, timezone]
    

    elif (match in file["ASCII Name"].values):
        filtered_df = file[file["ASCII Name"] == match]
        country = filtered_df["Country name EN"].iloc[0]

        timezoneArea = filtered_df["Timezone"].iloc[0]
        timezone = findTimezone(timezoneArea)

        return [country, timezone]
    

    elif (match in file["Name"].values) : 
        filtered_df = file[file["Name"] == match]
        country = filtered_df["Country name EN"].iloc[0]

        timezoneArea = filtered_df["Timezone"].iloc[0]
        timezone = findTimezone(timezoneArea)

        return [country, timezone]
    
    # If we are not able to find a location we suppose our alogrithm isnt good enough
    # Some user enter random words but we cant make de difference between random words and the mistake from our algorithm ( random words arent that frequent anyway)
    else : 
        return ["no data", "no data"]


# Return a world region corresponding to the country
def getRegion(country) : 
    file1 = pd.read_csv("database/countryToRegion.csv", on_bad_lines="skip", delimiter=";", encoding="latin-1")

    if (country in file1.values):
        filtered_df = file1[file1["country"] == country]
        region = filtered_df["region"].iloc[0]
        return region

    else :
        return "no data"


# This function get a location and the UTC offset for the said location
def getLocationFromUser() :
    
    #Open database that we are gonna use
    df = pd.read_csv('tempData/GithubAPIData.csv')

    # Fill the empty location with No data
    df = df.fillna("no data")

    locationArray = df[["location"]].to_numpy()

    matchArray = []
    timezoneArray = []

    for item in locationArray : 
        tempArray = findCountry(item[0])
        
        # Save the data to the corresponding type of data
        matchArray.append(tempArray[0])
        timezoneArray.append(tempArray[1])

    # We return an other array to match a country to a region
    regionArray = []

    for country in matchArray:
        regionArray.append(getRegion(country))


    # Adding the data to the dataframe
    subDf = df[["login", "contributions", "location"]]
    subDf.insert(len(subDf.columns), "country", matchArray)
    # subDf.insert(len(subDf.columns), "timezone", timezoneArray)

    # Displaying stats from the data used
    print(subDf)
    print("out of ", len(matchArray) ,"-> No data : ", matchArray.count("no data") ,"; Lost in preprocessing : ", matchArray.count("Lost in preprocessing"))

    # Saving the temporary data used form debug purposes
    subDf.to_csv("tempData/GetLocationFromUserData.csv")

    #  Adding data to the final dataframe
    Finaldf = pd.read_csv("database/FinalData.csv")
    # Finaldf.insert(len(Finaldf.columns), "LocationFromUser", matchArray)
    Finaldf.insert(len(Finaldf.columns), "regionFromUser", regionArray)
    Finaldf.to_csv("database/FinalData.csv")


# Start the main function
if __name__ == "__main__" : 
    getLocationFromUser()


# value = findMatch("Edinburgh, Scotland")
# print(value)

#     country = findCountry("Cyprus")
#     print(country)