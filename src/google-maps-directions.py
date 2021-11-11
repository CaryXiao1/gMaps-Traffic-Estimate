"""
google-maps-directions.py

@author: Cary Xiao
@version: 25 October 2021

This file tests the Google Maps Distance Matrix API and the 
write / read file functionality that will be used in the main 
python file, gmaps-rush-hour
"""
import os
import requests
import datetime

# This function writes a specified string onto a new line of
# a specific file with name fileName. File must be in data folder.
def writeToFile(fileName, addLine):
    write_data = open("data\\" + fileName, "a")
    write_data.write("\n" + addLine)
    write_data.close()

# Locations - note: starting points directly correspond to 
# the same index of ending points

# note: use pipe (or |) to deliniate between multiple origins / destinations
# GPS coordinates for specified locations:
# 37.413611,-122.168969 - 94305 zip code centroid
# 37.424423,-122.164263 - soto house & stanford
# 33.345564,-87.480152 - 35406 zc centroid
# 37.434450,-122.161075 - center of Stanford Football Stadium


#STARTING_POINTS = ["Tuscaloosa",  "658 Escondido Rd, Stanford, CA 94305",      "New York City, New York"]
#ENDING_POINTS   = ["Santa Clara", "5421 Bluegrass Pkwy, Tuscaloosa, AL 35406", "Boston, Massachusetts"]
STARTING_POINTS = ["37.424423,-122.164263"]
ENDING_POINTS   = ["37.413611,-122.168969", "33.345564,-87.480152", "37.434450,-122.161075"]

# process points into starting string
allStartingPoints = ""
if (len(STARTING_POINTS) > 0):
    
    for i in range(len(STARTING_POINTS)):
        allStartingPoints += STARTING_POINTS[i] + '|'
    # removes last pipe
    allEndingPoints = allStartingPoints[0: len(allStartingPoints) - 1: 1]
print("Starting Points: " + allStartingPoints)

# process ending points into submitting string
allEndingPoints = ""
if (len(ENDING_POINTS) > 0):
    
    for i in range(len(ENDING_POINTS)):
        allEndingPoints += ENDING_POINTS[i] + '|'
    # removes last pipe
    allEndingPoints = allEndingPoints[0: len(allEndingPoints) - 1: 1]
print("Ending Points: " + allEndingPoints)
        

# grab API key from text file
os.chdir("C:\\Users\\caryx\\OneDrive - Stanford\\CS\\Work with Prof. Gerritsen")
API_FILE = open("ref\\google-api-key.txt", "r")
api_key = API_FILE.read()

# base url
url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&"

#get response
r = requests.get(url + "origins=" + allStartingPoints + "&destinations=" + allEndingPoints + "&key=" + api_key)
print(r.json())
time = r.json()["rows"][0]["elements"][0]["duration"]["text"]
seconds = r.json()["rows"][0]["elements"][0]["duration"]["value"]
distance = r.json()["rows"][0]["elements"][0]["distance"]["value"]

print("\nIt takes " + time + " or " + str(seconds) + " seconds to get to the destination.")
print("\nSelected route is " + str(distance) + " meters long.")

# write API data to file
# format of data in data folder: filename = origin_to_destination.txt, each line = time|distance (in meters)|time (in seconds)
fileName = "test-write.txt"
addLine = str(datetime.datetime.today()) + "|" + str(distance) + "|" + str(seconds)
writeToFile(fileName, addLine)

