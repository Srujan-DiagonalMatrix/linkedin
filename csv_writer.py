import csv
from config import csv_w_filepath
#from url_helper import url_checker
import sys

# field names
fields = ['Contact', '2nd degree contact', '3rd degree contact', 'Mutuals', 'Multiple results', 'Degree']

# name of csv file
filename = csv_w_filepath

# writing to csv file
with open(filename, 'w') as csvfile:
    # creating a csv writer object
    csvwriter = csv.writer(csvfile)
    
    # writing the fields
    csvwriter.writerow(fields)
    
    # writing the data rows
    #csvwriter.writerows(rows)

def write_single_row(single_row):
    print("write_single_row call")
    # writing to csv file
    with open(filename, 'a') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        #csvwriter.writerows(single_row)
        csvwriter.writerow(single_row)


