#A set of simple functions to read in csv file as nested tuple
#Or export nested tuple to CSV (for Python 3+)

import csv

#simple function to read in csv files
def ReadCSV(loc):
    tup = []
    with open(loc) as f:
        z = csv.reader(f)
        for row in z:
            tup.append(tuple(row))
    return tup
#First row will be header
#So can do 
#data = ReadCSV(????CSVLocation?????)
#colnames = data.pop(0)	

#General function to export nested tuples to csv
def ExpCSV(loc,head,data):
    with open(loc, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(head)
        for line in data:
            writer.writerow(line)