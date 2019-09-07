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
cur_url = None
src_url = None


class connect():

    def search_results(self, url):
        global cur_url, src_url

        try:
            url = url.replace(',', '%2C')
        except:
            pass
        try:
            url = url.replace('&', '%26')
        except:
            pass

        try:
            linkedin_url = "https://www.linkedin.com/search/results/index/?keywords={0}&origin=GLOBAL_SEARCH_HEADER".format(url)
            driver.get(linkedin_url)
            src_url = driver.current_url
            total_search_results = driver.find_elements_by_class_name("actor-name")
            print('Total search result = ', len(total_search_results))
            if len(total_search_results) > 1:
                cur_url = None
                connect.total_connections(name=url, connections=None, degree=None, name_list=None)
            elif len(total_search_results) == 0:
                cur_url = None
                connect.total_connections(name=url, connections=0, degree=None, name_list=None)
            else:
                connect.total_results(len(total_search_results))
        except:
            print('ERROR: Invalid URL : ---------- ' + url)
            time.sleep(10)
            print(driver.current_url)
            pass

    @staticmethod
    def total_results(results):
        global cur_url
        if results == 0:
            count = 1
            while(count):
                try:
                    time.sleep(10)
                    url = driver.current_url
                    total_search_results = driver.find_elements_by_class_name("actor-name")
                    print("Total search results ", len(total_search_results))
                    if len(total_search_results) > 0:
                        count = 0
                        connect.total_results(len(total_search_results))
                    else:
                        count = 1
                except:
                    time.sleep(10)
                    url = driver.current_url
                    total_search_results = driver.find_elements_by_class_name("actor-name")
                    print("Total search results")
                    print(len(total_search_results))
                    connect.total_results(len(total_search_results))

        if results == 1:
            try:
                driver.execute_script('document.getElementsByClassName("name actor-name")[0].click();')
                time.sleep(5)
                cur_url = driver.current_url
            except Exception as e:
                print(e)
                driver.execute_script('document.getElementsByClassName("name actor-name")[0].click();')

            # Get Person Name
            try:
                name = driver.find_elements_by_css_selector('li.inline.t-24.t-black.t-normal.break-words')
                print("Name of person = ", str(name[0].text))
            except Exception as e:
                print("Refreshing.....")
                driver.find_element_by_name("s").sendKeys(Keys.F5)
                name = driver.find_elements_by_css_selector('li.inline.t-24.t-black.t-normal.break-words')
                print("Name of person = ", str(name[0].text))

            # Get Person degree
            try:
                degree = driver.find_elements_by_css_selector('span.dist-value')
                print("Degree of connection = ", str(degree[0].text))
                connect.degree_of_connection(degree[0].text, name[0].text)
            except Exception as e:
                print(e)

    @staticmethod
    def degree_of_connection(degree, usr_name):
        global cur_url
        if degree == "2nd":
            try:
                element = WebDriverWait(driver,50).until(
                    EC.presence_of_element_located((By.CLASS_NAME,"pv-highlight-entity__secondary-text"))
                )
                try:
                    time.sleep(5)
                    msg = driver.find_elements_by_css_selector(".pv-highlight-entity__secondary-text")
                    mutual_msg = str(msg[0].text).replace(',',';')

                    # print('Getting mutual connections...')
                    # elm = WebDriverWait(driver, 50).until(
                    #     EC.presence_of_element_located((By.CLASS_NAME, "pv-highlight-entity__primary-text"))
                    # )
                    # elm.click()
                    # time.sleep(3)
                    # elm = driver.find_elements_by_class_name("pv-highlight-entity__secondary-text t-14 t-black--light
                    # t-normal")
                    # elm = driver.find_elements_by_class_name("actor-name")
                    # print('total mutual connections = ', int(len(elm)))
                    # name_list = []
                    # for name in range( len(elm)):
                    #     print("connection data = ", elm[name].text)
                    #     name_list.append(str(elm[name].text))
                    connect.total_connections(usr_name, 0, degree, mutual_msg)
                except Exception as e:
                    pass
            except Exception as e:
                print(e)

        if degree == "3rd" or len(degree.strip()) == 0:
            try:
                cur_url = driver.current_url
                connect.total_connections(name=usr_name, connections=None, degree=degree, name_list=None)
            except:
                pass

    @staticmethod
    def total_connections(name, connections, degree, name_list):
        global csv_data
        name_list_str = None
        mul_results = None
        if name:
            name = name.replace(',','')

        if name_list:
            name_list_str = str(name_list.split("know ")[1])

        if (name_list == None) and (degree != "3rd") and (connections != 0):
            mul_results = "YES"

        try:
            dict_data = {"Contact": str(name), "2nd degree contact": None, "3rd degree contact": None,
                         "Mutuals": name_list_str, "Multiple results" : mul_results, "Degree": str(degree),
                         "Contact Url" : str(cur_url), "Source Url" : src_url
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
        fields = ['Contact', '2nd degree contact', '3rd degree contact', 'Mutuals', 'Multiple results', 'Degree', "Contact Url", "Source Url"]
        with open(csv_w_filepath, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            for data in csv_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")

