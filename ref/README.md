# Reference Files for traffic-data

This file outlines the structure and extra notes on the structure of each ref file.

# File Structure

Each file stores GPS coordinates of zip code centroids or the start, large intersections, and end in order from one edge of a specified road section to another. Each position takes up two lines in the text file, with the actual GPS coordinates located on every even line and a description of what that code represents on every odd line.

# Zip Code Centroids

The file 'zip-code-centroids-update-2.txt' contains all zip codes with > 7,000 trips from the data from https://github.com/jz486350/ENERGY-312-SONOMA/blob/main/nodes.csv.
