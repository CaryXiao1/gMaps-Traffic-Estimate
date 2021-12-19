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
import csv
import pandas as pd
from typing import Callable
import requests
import time
import datetime
from os.path import exists

######################################################
# Functions
######################################################

# This function writes a specified list onto the next row of
# a CSV file denoted by fileName within the folder data.
# If file doesn't exist, automatically creates one with specified
# header for data.
def writeToCSV(fileName, lineFields: list):
    if not(exists("data\\" + fileName)):
        # create file w/ header if it doesn't exist
        df = pd.DataFrame(list())
        df.to_csv("data\\" + fileName)
        write_data = open("data\\" + fileName, "a")
        writer = csv.writer(write_data)
        writer.writerow(["Time", "Distance", "Duration", "Duration in Traffic"])
        write_data.close()

    # create file to write line into
    write_data = open("data\\" + fileName, "a")
    writer = csv.writer(write_data)
    writer.writerow(lineFields)
    write_data.close()


# this helper function returns the string verson of all locations
# in locs (type list of strings) to be used by callAPI
def formatLocations(locs) -> str:
    formedLoc = ""
    if (type(locs) == list):
        for i in range(len(locs)):
            formedLoc += locs[i] + '|'
            # removes last pipe
        formedLoc = formedLoc[0: len(formedLoc) - 1: 1]
        return formedLoc
    elif (type(locs) == str):
        return locs


# This function makes an API Call to Google based off formatted origins and destinations.
# Returns the results from results.get(), generally dispayed as JSON.
def callAPI(originList: list, destinationList: list):
    # grab API key from text file
    API_FILE = open("ref\\.gitignore\\google-api-key.txt", "r")
    api_key = API_FILE.read()

    # convert originList and destinationList into link for call
    origins = formatLocations(originList)
    destinations = formatLocations(destinationList)

    # base url
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&"
    time.sleep(0.25)
    #get response
    return requests.get(url + "origins=" + origins + "&destinations=" + destinations + "&mode=driving" + "&departure_time=now" + "&key=" + api_key)


# Returns the list of all locations in a given text file denoted by filePath.
# Structure of data files: every other line (line 2, 4, 6, 8, etc.) holds GPS
# coordinates; lines 1, 3, 5, etc. describe what location that coordinate is for.
def getLocsFromFile(filePath: str, headers: bool):
    f = open(filePath, 'r')
    lines = f.readlines()
    if (len(lines) > 0 and not(headers)):
        lines.pop(0)
    result = lines[::2]
    for i in range(len(result)):
        result[i] = result[i][0: len(result[i]) - 1] # remove \n
    f.close()
    return result 
    

# given a specific text file denoted by 'filePath', automatically does API calls
# and records the results into an automatically-generated text file in the folder
# data\folder.
def recordRoad(filePath: str, folder: str):
    print("\nStarting calls on road with file: " + filePath)
    locs = getLocsFromFile(filePath, False)
    print("Locations found from file: " + str(locs))
    # Call API on very first and last loc
    if (len(locs) > 2):
        first = locs[0]
        last = locs[len(locs) - 1]
        for n in range(1):
            print("Calling API for first and last location: " + str(first) + " to " + str(last))
            r = callAPI(first, last)
            print(r.json())
            distance = None
            duration = None
            traffic = None
            try:
                distance = r.json()["rows"][0]["elements"][0]["distance"]["value"]
                duration = r.json()["rows"][0]["elements"][0]["duration"]["value"]
                traffic = r.json()["rows"][0]["elements"][0]["duration_in_traffic"]["value"]
                fileName = first + " to " + last + ".csv"
                addList = [datetime.datetime.today(), distance, duration, traffic]
                writeToCSV(folder + "\\" + fileName, addList)
            except IndexError:
                print("An error occured when calling the API on lines 115-116. Current r.json():")
                print(r.json())
            # switch to get time in other direction
            temp = first 
            first = last
            last = temp
        
    # getting API Calls going forward
    i = 0
    forward = locs
    while (len(forward) > 1):
        orig = forward[0]
        dest = forward[1]

        r = callAPI(orig, dest)
        # store data of call in file
        try:
            distance = r.json()["rows"][0]["elements"][0]["distance"]["value"]
            duration = r.json()["rows"][0]["elements"][0]["duration"]["value"]
            traffic = r.json()["rows"][0]["elements"][0]["duration_in_traffic"]["value"]
            fileName = orig + " to " + dest + ".csv"
            addList = [str(datetime.datetime.today()), distance, duration, traffic]
            writeToCSV(folder + "\\" + fileName, addList)
            print("Called API on Locations " + str(i) + " and " + str(i + 1) + ", added data: " + str(addList))
        except IndexError:
            print("An error occured when calling the API on lines 133-134. Current r.json():")
            print(r.json())
        forward = forward[1:]
        i += 1
    
    print("\nCalling API on locations going backward:")
    while (i > 1):
        orig = locs[i]
        dest = locs[i - 1]

        r = callAPI(orig, dest)
        # store data of call in file
        try:
            distance = r.json()["rows"][0]["elements"][0]["distance"]["value"]
            duration = r.json()["rows"][0]["elements"][0]["duration"]["value"]
            traffic = r.json()["rows"][0]["elements"][0]["duration_in_traffic"]["value"]
            fileName = orig + " to " + dest + ".csv"
            addList = [str(datetime.datetime.today()), distance, duration, traffic]
            writeToCSV(folder + "\\" + fileName, addList)
            print("Called API on Locations " + str(i) + " and " + str(i - 1) + ", added data: " + str(addList))
        except IndexError:
            print("An error occured when calling the API on lines 133-134. Current r.json():")
            print(r.json())
        i -= 1

# Like 'recordRoad' but finds estimated times between all zip
# code centroids.
# TODO: check to see if it works
def recordZipCodes(filePath: str, folder: str):
    print("\nStarting Calls on Zip Codes with file: " + filePath)
    locs = getLocsFromFile(filePath, False)
    headers = getLocsFromFile(filePath, True)
    print("Locations found from file: " + str(locs))
    print("Zip Code Headers found from file: " + str(headers))
    
    # loop through each Zip Code as origin for API Call
    for o_i in range(0, len(locs)): # o_i = origin index
        origin = locs[o_i]
        origin_h = headers[o_i]
        
        # get all destinations & destination headers, 10 at a time
        for d_i in range(0, len(locs), 10): # d_i = destination index
            remainder = len(locs) - d_i
            dests = None
            dests_h = None 
            if (remainder >= 10):
                dests = locs[d_i: 10 + d_i]
                dests_h = headers[d_i: 10 + d_i]
            else:
                dests = locs[d_i:]
                dests_h = headers[d_i:]

            print("Origin: " + str(origin) + ", " + "Destinations: " + str(dests))
            print("Origin Header: " + str(origin_h) + ", " + "Destination Headers: " + str(dests_h))
            # remove origin if it's in destinations list
            if origin in dests:
                remove_index = dests.index(origin)
                dests.pop(remove_index)
                dests_h.pop(remove_index)
                print("Removed Origin:" + str(origin) + " from destinations and destionation headers.")
            
            r = callAPI(origin, dests)

            # process results of API
            for n in range(len(dests)):
                try:
                    results = r.json()["rows"][0]["elements"][n]
                    duration = results["duration"]["value"]
                    distance = results["distance"]["value"]
                    traffic = results["duration_in_traffic"]["value"]
                    
                    fileName =  origin_h + " to " + dests_h[n] + ".csv"
                    addList = [str(datetime.datetime.today()), distance, duration, traffic]
                    writeToCSV(folder + "\\" + fileName, addList)

                except IndexError:
                    print("An error occured when calling the API on lines 225-227. Current r.json():")
                    print(r.json())



#####################################################
# Main Code
#####################################################

# cd to Repository
# os.chdir("C:\\Users\\caryx\\OneDrive - Stanford\\CS\\Repositories\\traffic-estimate")
os.chdir("C:\\Users\\gameb\\OneDrive - Stanford\\CS\\Repositories\\traffic-estimate")
print("\nScript Started.")
# loops call daily

for i in range(0,365): # Stops script if it's still running after a year
    # sleep until 6AM and run for 4 hours (until 10 AM)
    
    start_time = 6
    run_time = 4
    t = datetime.datetime.today()
    """
    future = datetime.datetime(t.year,t.month,t.day,start_time,0) + datetime.timedelta(minutes = 2)# + datetime.timedelta(seconds = 30)
    if t >= future:
        future += datetime.timedelta(days=1)
    print("Sleeping until " + str(start_time) + ". Time to elapse: " + str(future-t))
    time.sleep((future-t).total_seconds())
    """
    end_time = datetime.datetime.today() + datetime.timedelta(hours = run_time)
    # end_time = datetime.datetime.today() + datetime.timedelta(hours=4)

    # Code to run at 6 AM
    print("------------------------")
    while (datetime.datetime.today() < end_time):
        mins_to_wait = 10; # number of mins to sleep until next API call / data gather
        starting_time = datetime.datetime.today()
        # recordRoad("ref\\h-101.txt", "h-101")
        # recordRoad("ref\\h-12.txt", "h-12")
        # recordRoad("ref\\r-116.txt", "r-116")
        recordZipCodes("ref\\zip-code-centroids-update-2.txt", "zip-code-centroids")
        
        # waits rest of time until 5 minutes have elapsed 
        repeat_time = starting_time + datetime.timedelta(minutes = mins_to_wait)
        print("\nAPI Call Round finished at " + str(datetime.datetime.today()) + ". Time to wait: " + str(repeat_time - datetime.datetime.today()))
        time.sleep((repeat_time-starting_time).total_seconds())
    print("------------------------")
    print("API Calls finished for today.")