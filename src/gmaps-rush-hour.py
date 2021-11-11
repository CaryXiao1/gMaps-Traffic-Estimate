"""
google-maps-directions.py

@author: Cary Xiao
@version: 24 October 2021

This file uses the google maps API to record data about commute times
on critical corridors (I-101, R-12, R-116) of Sonoma County. Automatically
places data in .txt files in the 'data' folder. 

Data records at 6 AM to 10 AM, with each point recorded 5 mins apart. 
Recorded data for each path = estimated time and calculated average speed.
"""
import os
import requests
import time
import datetime

######################################################
# Functions
######################################################

# This function writes a specified string onto a new line of
# a specific file with name fileName. File must be in data folder.
def writeToFile(fileName, addLine):
    write_data = open("data\\" + fileName, "a")
    write_data.write("\n" + addLine)
    write_data.close()

# this helper function returns the string version of all locations
# in locs (type list of strings) to be used by callAPI
def formatLocations(locs: list) -> str:
    formedLoc = ""
    for i in range(len(locs)):
        formedLoc += locs[i] + '|'
        # removes last pipe
    formedLoc = formedLoc[0: len(formedLoc) - 1: 1]
    return formedLoc

# This function makes an API Call to Google based off formatted origins and destinations.
def callAPI(originList: list, destinationList: list):
    # grab API key from text file
    os.chdir("C:\\Users\\caryx\\OneDrive - Stanford\\CS\\Work with Prof. Gerritsen")
    API_FILE = open("ref\\google-api-key.txt", "r")
    api_key = API_FILE.read()

    # convert originList and destinationList into link for call
    origins = formatLocations(originList)
    destinations = formatLocations(destinationList)

    # base url
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&"

    #get response
    r = requests.get(url + "origins=" + origins + "&destinations=" + destinations + "&key=" + api_key)
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

# This helper function for encode takes in a string (representing binary) 
# and inverts the 0s to 1s and 1s to 0s.
def flipBin(bin):
    result = ""
    if (len(bin) > 1):
        bin = bin[2: len(bin) - 2: 1]
        result += "0b"
    
    for char in bin:
        if (char == '0'):
            result += '1'
        elif (char == '1'):
            result += '0'
    return result


# This function converts a given GPS coordinate into the encoded version. Used
# to increase the number of destinatinos able to be called in the API call.
def encode(loc):
    print(loc)
    binLoc = bin(round(loc * 100000))
    print(binLoc)
    if (loc < 0):
        binLoc = flipBin(binLoc)
        print(binLoc)
        binLoc = int(binLoc, 2) + 1
        print(binLoc)
        binLoc = bin(binLoc)
        print(binLoc)
    
    print(binLoc)
    """
    binLoc << 1
    print(binLoc)
    if (loc < 0):
        binLoc = ~binLoc
    print(binLoc)
    [binLoc[i: i + 5]
      for i in range(0, len(binLoc), 5)
   ]
    print(binLoc)
    return binLoc"""

#####################################################
# Main Code
#####################################################
bin = encode(-179.9832104)
# Prevents code from running until between 6 to 10 AM
for i in range(0,365): # Stops script if it's still running after a year
    # sleep until 6AM and run for 4 hours (until 10 AM)
    start_time = 6
    run_time = 4
    t = datetime.datetime.today()
    future = datetime.datetime(t.year,t.month,t.day,start_time,0) + datetime.timedelta(minutes = 10)
    if t >= future:
        future += datetime.timedelta(days=1)
    print("\nScript started, sleeping until " + str(start_time) + ". Time to elapse: " + str(future-t))
    time.sleep((future-t).total_seconds())

    end_time = datetime.datetime.today() + datetime.timedelta(hours = run_time)

    # Code to run at 6 AM
    while (datetime.datetime.today() < end_time):
        mins_to_wait = 5; # number of mins to sleep until next API call / data gather
        starting_time = datetime.datetime.today()
        
        # grab points from file
        points = ["37.424423,-122.164263", "37.413611,-122.168969", "33.345564,-87.480152", "37.434450,-122.161075"]
        
        # create all pathways from points
        for i in range(len(points)):
            start_points = []
            end_points = []
            for n in range(len(points)):
                if (i == n):
                    start_points.append(points[n])
                else:
                    end_points.append(points[n])
            
            # TODO: do loop to go through all data points in JSON and independently store each data point in each file
            callAPI(start_points, end_points)
            ################
            # waits 2 seconds to prevent overloading GMaps with too many API calls
            time.sleep(2)

        # waits rest of time until 5 minutes have elapsed 
        repeat_time = starting_time + datetime.timedelta(minutes = mins_to_wait)
        print("\nAPI Call Round finished at " + str(datetime.datetime.today()) + ". Time to wait: " + str(repeat_time - datetime.datetime.today()))
        time.sleep((repeat_time-starting_time).total_seconds())