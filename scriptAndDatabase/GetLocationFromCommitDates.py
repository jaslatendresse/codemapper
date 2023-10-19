import requests
from string import Template
import pandas as pd
import multiprocessing
import random
import time
import pickle

#Not used for the moment but can be in the future
# from datetime import datetime
# from datetime import timedelta


# A simple function to use requests.post to make the API call.
def run_query(query, gh_token):

  # Data necessary to make a request to the API
  headers = {"Authorization": gh_token}

  request = requests.post('https://api.github.com/graphql', json={'query': query}, auth=('token', gh_token))

  # If the answer is good we return it, else we return the exception
  if request.status_code == 200:
      return request.json()
  else:
      if (request.status_code == 403):
        raise Exception("Blocked by Github API (code 403)")
      else :
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))   


# This function get the global ID of a user, we need this ID to find the commits on the repository, we cant just use the login
def getIdLogin(login, gh_token):

  # Template of query to get the ID
  getId = Template("""
  {
    repositoryOwner(login: "$login") {
      ... on User {
        id
      }
    }
  }
  """)

  # Adding the variable login to the Template of the query
  queryGetId = getId.substitute(login=login)

  resultQueryId = run_query(queryGetId, gh_token)

  id = resultQueryId["data"]["repositoryOwner"]["id"]
   
  return id


# This function returns the cursor to get the last commits
def getCursor(id, owner, package, gh_token):

  getCursor = Template("""
  {
    rateLimit {
      limit
      cost
      remaining
      resetAt
    }
    repository(owner : "$owner", name : "$name"){
      defaultBranchRef {
        target {
          ... on Commit {
            history(first : 100, author : {id  : "$idValue"}){
              pageInfo {
                endCursor
              } 
            }
          }
        }
      }
    }
  }
  """)
    
  cursorQuery = getCursor.substitute(owner=owner, name=package, idValue=id)
  
  resultQueryCursor = run_query(cursorQuery, gh_token)
  
  # Changing the values of the cursor to get the last page
  cursor = resultQueryCursor["data"]["repository"]["defaultBranchRef"]["target"]["history"]["pageInfo"]["endCursor"]
  cursor = cursor[:-2] + "100"

  return cursor


# This function return the UTC offset of the 100 last commits
def getTimeCommit(login, owner, package, gh_token):

  # Template of the query to get the time of the 100 commits
  getCommitDates = Template("""
  {    
    rateLimit {
      limit
      cost
      remaining
      resetAt
    }
    repository(owner : "$owner", name : "$name"){
      defaultBranchRef {
        target {
          ... on Commit {
            history(last : 100, before : "$cursor" author : {id  : "$idValue"}){     
              nodes{
                additions
                deletions
                changedFilesIfAvailable
                committer{
                  date
                }
              } 
              pageInfo {
                hasPreviousPage
                hasNextPage
                endCursor
              } 
            }
          }  
        }
      }
    }
  }
  """)

  # Getting the global ID of the user
  id = getIdLogin(login, gh_token)

  # Getting the cursor to get the latests commits
  cursor = getCursor(id, owner, package, gh_token)

  # Adding variables to the query Template
  queryGetCommitDates = getCommitDates.substitute(idValue=id, owner=owner, name=package, cursor=cursor)

  resultQueryDates = run_query(queryGetCommitDates, gh_token)

  # Remove the different "layers" on the data (layers come from the query)
  predata = resultQueryDates["data"]["repository"]["defaultBranchRef"]["target"]["history"]["nodes"]
  
  # The return array of all the offset
  offSetArray = []

  # We used to want the time of the commits, not only the offset but for the moment we wont use it
  # commitTimeArray = []

  # For each commit date we extract the UTC offset
  for commit in predata : 
    
    fullDate = commit["committer"]["date"]

    # the format of the date is : "2023-12-11T12:11:59+01:00"
    # We just want the offset so we remove the other part, this isnt the most efficient way to do it but we still want to have the option
    # to use the date in case for the future
    temp = fullDate.split("T")

    time = temp[1][0: 8] # this is the 12:11:59 part
    timezone = temp[1].replace(time, "") # Removing the 12:11:59 of the commit date

    # When there is no offset it is written with a "Z" (instead of for exemple -07:00)
    if (timezone == "Z"):
      offSetArray.append(0)
    else :
      offSetArray.append(int(timezone[0:3]))
    
  return offSetArray

### We used to try to find the time (12:11:59) from the user and convert it to UTC time so we would have an idea from where his commits are but it's not the most reliable way
### We still keep the function in case we might need it in the future
  #     if (timezone == "Z") :
  #       finalTime = time
  #       offSetArray.append(0)
  #     else : 
  #       offSetArray.append(int(timezone[0 : 3]))
  #       if (timezone[0] == "-"):
  #           tempTime = datetime.strptime(time, "%H:%M:%S") - timedelta(hours = int(timezone[1: 3])) 
            
  #       elif(timezone[0] == "+"):
  #           tempTime = datetime.strptime(time, "%H:%M:%S") + timedelta(hours = int(timezone[1: 3])) 
  #       else :
  #           print("problem with the difference time")
  #           print(fullDate)

  #       finalTime = tempTime.strftime("%H:%M:%S")
  #     # print(finalTime)

  #     commitTimeArray.append(finalTime)

  # returnArray = [commitTimeArray, offSetArray]


# This function predict a location
# The way we predict if handmade and is probably gonna change 
# FUNCTION NOT USED ANYMORE
def predictLocation(timeUTC):
  load_model = pickle.load(open("modelSaved", "rb"))

  reshapedData = []
  for j in range (-12, 12): 
    count = timeUTC.count(j)
    reshapedData.append(count)

  # print(reshapedData)  

  y_predict = load_model.predict([reshapedData])

  return y_predict[0]


# This function return the average offset, most frequent offset, frequency of this offset and a prediction based on thoses data
def getLocationData(Array, gh_token) :   
  login = Array[0]   
  owner = Array[1]   
  package = Array[2]  

  # Some users we are not able to do some querys, to avoid crashing the script we just print the name of the user and move on
  try : 
    timeUTC = getTimeCommit(login, owner, package, gh_token)

    # prediction = predictLocation(timeUTC)
    prediction = "removed for the moment"

    returnArray = [prediction, timeUTC]
    return returnArray

  except Exception as e: 
    print("problem with user : " + login)
    print(e)

    return ["no data", "no data"]
  

# This function allows us to get data from all the users, it then adds all the temporary data (average, most frequent offset etc..) to a csv file for debug purposes
# FUNCTION NOT USED ANYMORE
def allDataBase(gh_token):

  # Reads the data 
  df = pd.read_csv('tempData/GithubAPIData.csv')

  # For each use we create a process, reach request takes around 2 sec so we have to multiprocess
  nbCommiters = len(df.index)
  print("Number of users to process : ", nbCommiters)

  # Data used for the processes
  subDf = df[["login", "owner", "package"]].to_numpy()


# # TEMP CHANGE BECAUSE API LIMIT SO CANT MULTIPROCESS, JUST TEMP CHANGE (removed)
#   # Creating the multiprocess pool and running it
#   pool = multiprocessing.Pool(processes=5)
#   output = pool.map(getLocationData, subDf)
#   print("After multi")

  # We add each time of data to a separate array that we are gonna input in different csv files
  PredictionArray = []
  allUTCoffset = []

  # Getting stats from the data processed
  noDataCount = 0

  index = 0
  # for values in output : 
  
  for user in subDf :
    print("On user : ", (index +  1), "/", nbCommiters)
    index = index + 1 

    # rand = random.random()
    # time.sleep(rand)
    # print("Sleep of ", rand)

    values = getLocationData(user, gh_token)

    # Adding the data to the different arrays
    PredictionArray.append(values[0])
    allUTCoffset.append(values[1])

    # Getting stats 
    if (values[0] == "no data"):
       noDataCount = noDataCount + 1

    # if (values[3] == "Data too uneven"):
    #    unevenDataCount = unevenDataCount + 1


  return allUTCoffset 


# MAIN of the script, it allows us to have multiprocessing to make it faster
if __name__ == "__main__" : 
  allDataBase()



# # Test function
# offset = getTimeCommit("Yikun", "apache", "spark")
# print(offset)