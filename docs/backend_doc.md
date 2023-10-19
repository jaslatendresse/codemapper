# Backend Documentation

Here, we describe how every script in the backend functions and how every file is used by the backend to display the information in the frontend. 

### scriptAndDatabase/database/

* `countryToRegion.csv` - 
Contains matches of every country to a world region. Thoses world regions come from a [World of Code paper](https://dl.acm.org/doi/pdf/10.1145/3524842.3528471) and help visualize data on the world scale. Link: https://zenodo.org/record/6390355

* `dataForFrontend.csv` - 
Holds the data that is going to be displayed to the front-end. 

* `FinalData.csv` - 
Receives the data from every script that get informations about a user. It is then to find the contributor location.

* `geonames-all-cities-with-a-population-1000.csv` - 
Database that matches every city with a country. Data sourced from [OpenDataSoft](https://public.opendatasoft.com/explore/dataset/geonames-all-cities-with-a-population-1000/table/?disjunctive.cou_name_en&sort=name)

* `nameProbaInCountry.csv` - 
Associates a name with a country based on the likelihood that an individual with this name originates from that country. Data from World of Code.
Link: https://zenodo.org/record/6390355

* `timezones.csv` - 
Matches between timezones and UTC offsets.
Link : https://github.com/bproctor/timezones/blob/master/timezones.csv


### scriptAndDatabase/DataMining/

* `dataMined.csv` - 
Database with unique users and their public information. Built with MiningScript.py.

* `listRepo.csv` - 
Database with every repository on GitHub with more that 100 commits and 20 contributors, generated with [SEART GitHub Search Engine](https://seart-ghs.si.usi.ch/).


### scriptAndDatabase/MachineLearning

* `RandomForestAlgo.py` - 

Builds a machine learning model to predict a contributor location without the GitHub profile location.

* `TrainingDataSet.csv` - 

Database with data from /DataMining/dataMined.csv but preprocessed. We anonymized the user login for privacy.


### scriptAndDatabase/

* `getData.php` - 

Return data to the frontend for each country the corresponding world region.

* `GenerateDataFromGithubAPI.py` - 

Returns a list of GitHub contributors and information about them from a specific repository.

* `GetLocationFromCommitDates.py` - 

For each contributor, get the UTC offset from their last 100 commits.

* `GetLocationFromEmail.py` - 

For each contributor, get the domain email and return the country this email is associated to.

* `GetLocationFromName.py` - 

For each contributor, get the name and return the probability this name is associated to a country.

* `GetLocationFromUser.py`

For each contributor, process the location information and return a country with the expected UTC offset.

* `MiningScript.py`

For every repository in `DataMining/listRepo.csv`, get the contributor informations and store them in `DataMining/dataMined.csv`.

