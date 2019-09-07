import csv
from config import csv_filepath
#from url_helper import url_checker
import sys

linkedin_urls = []
source_urls   = []

with open(csv_filepath,'r') as f:
    try:
        reader = csv.reader(f,delimiter=';')
        print(str(sys.argv[1]))
    except Exception as e:
        reader = csv.reader(f)

    header = next(reader)

    for row in reader:
        try:
            linkedin_url = row[0]
            source_url = row[1]
            if len(linkedin_url):
                print(linkedin_url)
                linkedin_urls.append(linkedin_url)
                source_urls.append(source_url)
            else:
                print("Line is blank...")
        except Exception as e:
            pass