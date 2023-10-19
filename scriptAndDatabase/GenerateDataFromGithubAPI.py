from github import Github
from github import GithubException
import requests
import pandas as pd
import multiprocessing
import sys
import time
import random

from ManageGitTokens import getToken
from ManageGitTokens import changeToken


# This function display stats on the data generated (amount of location missing, email etc..)
def displayStats(df):

    noEmail = df[df['email'].isnull()]
    noLocation = df[df['location'].isnull()]

    print("no location : ", len(noLocation.index))
    print("no email : ", len(noEmail.index))


# This function is used to get informations on a user (email, contributions, location etc..)
def getUserData(contributor):

    time.sleep(random.random())
    gh_token = getToken()
    login = contributor['login']
    contributions = contributor['contributions']

 
    g = Github(gh_token)
    
    # Sometimes a request doesnt works and to avoid crashing the program we just print the user that causes the problem and move to the next one
    good = 0
    while (good != 1):
        try:
            user = g.get_user(login)
            location = user.location
            email = user.email
            name = user.name
            company = user.company
            twitter_username = user.twitter_username
            bio = user.bio

            good = 1
            if (contributions > 10):
                return [login, name, twitter_username, bio, company, email, contributions, location]
            else :
                return "not enough contributions"

        except GithubException as e:
            print("Error with user " + login)
            print(e)
            if (e.status == 403):
                print("toke didnt worked here : ", gh_token)
                gh_token = changeToken(gh_token)
                g = Github(gh_token)
            else :
                return "error with user"


# This function return the list off the biggest contributors to a repository
def getContributorsList(owner, package):

    gh_token = getToken()
    # Amount of contributors we want (can't go over 100 because of Github limit)
    total = 100

    url = "https://api.github.com/repos/" + owner+ "/"+ package+ "/contributors?per_page=" + str(total)

    # Get list of the biggest contributors
    # print("Getting contributors list")

    good = 0
    while (good != 1):

        response = requests.get(url, auth=('token', gh_token))
        response_json = response.json()

        if (response.status_code == 200):
            response_json = response.json()
            return response_json
        elif(response.status_code == 403) : 
            print("Token didnt worked list : ", gh_token)
            gh_token = changeToken(gh_token)
        else : 
            print("Error with the request to get contributors lists, code : ", response.status_code)
            return ("Error")
            




# This function generates all the data, we first get the list of the first 50 contributors and for each we get informations available on github
def getData(owner, package):
    
    # Get the list of contributors, sometimes it gets blocked because of Github API request limit

    response_json = getContributorsList(owner, package)

    # If the response if "Error" we stop and return the error
    if (response_json == "Error"):
        print("Error with contributor list")
        return (pd.DataFrame())
    

    # Creating the dataframe that's gonna hold the values
    df = pd.DataFrame(columns=["owner", "package", "login", "name", "twitter_username", "bio", "company", "email", "contributions", "location"]
)
   
    # Creating the multiprocessing process do reduce time
    pool = multiprocessing.Pool(processes=10)
    output = pool.map(getUserData, response_json)

    # We add the data to the dataframe
    index = 0
    for row in output : 
        if (row != "not enough contributions" and row!= "error with user"):
            row = [owner, package] + row
            # print(row)
            df.loc[index] = row
            index = index + 1

    # Display the dataframe the user for debug/code review
    print(df)

    # # Adding data that are gonna be used by other scripts
    # df.to_csv("tempData/GithubAPIData.csv")

    # # Adding the important informations to the final dataset
    # FinalDf = df[["login","contributions", "location"]]
    # FinalDf.to_csv("database/FinalData.csv")

    # Displaying stats on the data generated
    print ("total contributors found : ", len(df.index))
    # displayStats(df)

    return df


# Main function, we need to add that to be able to enable multiprocessing
if __name__ == "__main__" : 
    # owner = sys.argv[1]
    # package = sys.argv[2]



    repo = sys.argv[1]
    splitedRepoName = repo.split("/")

    getData("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", splitedRepoName[0], splitedRepoName[1])