# Bulk follow  LinkedIn users

The LinkedIn script `follow_li.py` will send a invitation for each user passed in csv file.

1) Place your .csv file in this repo's root directory. 

2) Install Linux: `sudo apt-get install python-pip`. 

3) Install Python dependencies: Navigate to root directory of repo and in terminal type `pip install -r requirements.txt`

4) Install `chromedriver`. Mac OS: `brew install chromedriver`. Linux: http://stackoverflow.com/a/24364290

5) Execute scripts: 
About decrypt_url_data_fetch.py::
decrypt_url_data_fetch.py fetches data for sales person linked url, mutual groups/contact or degree and his number of connections.

How to run the decrypt_url_data_fetch.py?

Command to fetch all the data at once:
python decrypt_url_data_fetch.py -u -d -c

-u stands for Sales person linked url. True if present
-d stands for mutual groups/contact or degree
-c stands for number of Connections

However, there some constraint while fetching this data in different ways or at different times which are mentioned below:
* You can either fetch all the data or just Sales person linked url at once.
Command to run> python decrypt_url_data_fetch.py -u -d -c
               or
Command to run> python decrypt_url_data_fetch.py -u
In above cases output_contacts.csv will always be re-created.

* You can fetch mutual groups/contact or degree of a sales person provided that the direct linked url is already present in the output_contacts.csv. But make sure that your input file i.e contacts.csv does not change or remains intact from the last run.
Command to run> python decrypt_url_data_fetch.py -d
In this case, the existing output_contacts.csv will be just modified for new column 'Mutual Contacts'

* You ca fetch number of contacts for a sales person provided that direct linked url is already present in the output_contacts.csv. But make sure that your input file i.e contacts.csv remains intact from the last run.
Command to run> python decrypt_url_data_fetch.py -c
In this case, the existing output_contacts.csv will be just modified for new column 'Connections'


**LinkedIn** 
  * In the terminal type `python follow_li.py` or `python3 follow_li.py`

_Some people's LinkedIn handles may be missing, contain typos or have already been followed. Feedback will be provided in the terminal when running the script._

