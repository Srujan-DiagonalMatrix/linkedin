import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from links import linkedin_urls
from config import li_username, li_password,chrome_driver_path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import csv_w_filepath
import csv
import os

driver = webdriver.Chrome(executable_path=chrome_driver_path)

if os.path.isfile(csv_w_filepath):
    os.remove(csv_w_filepath)

driver.get("https://www.linkedin.com/uas/login")
time.sleep(5)
driver.maximize_window()
time.sleep(2)
driver.find_element_by_name('session_key').send_keys(li_username)
driver.find_element_by_name('session_password').send_keys(li_password)
driver.find_element_by_name('session_password').send_keys(Keys.RETURN);
time.sleep(5)
csv_data = []
user_name = None
src_url = None


class connect():

    def search_results(self, url):
        global src_url

        try:
            driver.get(url)
            src_url = driver.current_url
            connect.total_results()
        except:
            print('ERROR: Invalid URL : ---------- ' + url)
            time.sleep(2)
            pass

    @staticmethod
    def total_results():
        # Get Person Name
        try:
            name = driver.find_elements_by_css_selector('li.inline.t-24.t-black.t-normal.break-words')
            print("Name of person = ", str(name[0].text))
            name_p = str(name[0].text).replace(',', '')
        except Exception as e:
            name_p = None

        # Get Person degree
        try:
            degree = driver.find_elements_by_css_selector('span.dist-value')
            print("Degree of connection = ", str(degree[0].text))
            degree_p = str(degree[0].text)
        except Exception as e:
            degree_p = None

        if name_p and degree_p:
            connect.degree_of_connection(name_p, degree_p)
        else:
            connect.total_connections(name=None, mutual=None, degree=None)

    @staticmethod
    def degree_of_connection(usr_name, degree):
        if degree == "2nd":
            try:
                element = WebDriverWait(driver,50).until(
                    EC.presence_of_element_located((By.CLASS_NAME,"pv-highlight-entity__secondary-text"))
                )
                try:
                    time.sleep(5)
                    msg = driver.find_elements_by_css_selector(".pv-highlight-entity__secondary-text")
                    mutual_msg = str(msg[0].text).replace(',',';')
                    connect.total_connections(usr_name, mutual_msg, degree)
                except Exception as e:
                    connect.total_connections(name=usr_name, mutual=None, degree=degree)
            except Exception as e:
                connect.total_connections(name=usr_name, mutual=None, degree=degree)

        if degree == "3rd":
            try:
                connect.total_connections(name=usr_name, mutual=None, degree=degree)
            except:
                pass

        if degree == "1st":
            try:
                connect.total_connections(name=usr_name, mutual=None, degree=degree)
            except:
                pass

    @staticmethod
    def total_connections(name, mutual, degree):
        global csv_data

        try:
            dict_data = {"Name": str(name), "Mutual contacts": mutual,
                         "Degree": str(degree), "Contact Url": src_url
                        }
            csv_data.append(dict_data)
        except Exception as e:
            pass


if __name__ == '__main__':
    for url in linkedin_urls:
        cn = connect()
        cn.search_results(url)
    driver.quit()
    try:
        fields = ['Name', 'Mutual contacts', 'Degree', 'Contact Url']
        with open(csv_w_filepath, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            for data in csv_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")

