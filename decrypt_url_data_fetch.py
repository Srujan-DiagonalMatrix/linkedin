import time
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from config import li_username, li_password,chrome_driver_path
from config import csv_filepath, csv_w_filepath
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
linkedin_urls = []


class Connect:

    def __init__(self):
        with open(csv_filepath, 'r') as myFile:
            try:
                reader = csv.reader(myFile, delimiter=';', quoting=csv.QUOTE_NONE)
            except Exception as e:
                reader = csv.reader(myFile)
            header = next(reader)

            for row in reader:
                try:
                    linkedin_url = row[0]
                    if len(linkedin_url):
                        print(linkedin_url)
                        linkedin_urls.append(linkedin_url)
                    else:
                        print("Line is blank...")
                except Exception as e:
                    pass

    @staticmethod
    def search_results(url):
        try:
            li_url = "https://www.linkedin.com/sales/people/{}".format(url)
            driver.get(li_url)
            time.sleep(20)
        except:
            print('ERROR: Invalid URL : ---------- ' + li_url)
            print(driver.current_url)
            pass

    @staticmethod
    def get_contact_link():
        try:
            time.sleep(5)
            action_menu_selector = 'div[class="artdeco-dropdown artdeco-dropdown--placement-bottom artdeco-dropdown--justification-right ember-view"] > button'
            driver.find_element_by_css_selector(action_menu_selector).click()
            time.sleep(5)
            driver.find_element_by_css_selector('div[data-control-name="copy_linkedin"]').click()
            time.sleep(5)
            li_link = pyperclip.paste()
            print(li_link)
            return li_link
        except Exception as e:
            raise Exception("Problem in getting the Linkedin url for sales contact")

    @staticmethod
    def get_second_degree_contact():
        try:
            time.sleep(5)
            element = driver.find_element_by_css_selector('span[class="label-16dp block"]')
            print(element.text)
            if element.text == '2nd':
                time.sleep(5)
                connection_text = driver.find_element_by_css_selector('dd[class="t-12 t-black--light t-normal"]').text
                return connection_text.split("know")[1]
            else:
                return element.text
        except Exception as e:
            print("Problem in getting the degree of a contact")


if __name__ == '__main__':
    cn = Connect()
    for url in range(len(linkedin_urls)):
        cn.search_results(linkedin_urls[url])
        li_link = cn.get_contact_link()
        degree = cn.get_second_degree_contact()
        dict_data = {'Contact Url': li_link, 'Mutuals Contacts': degree}
        csv_data.append(dict_data)
    driver.quit()

    try:
        fields = ['Contact Url', 'Mutuals Contacts']
        with open(csv_w_filepath, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            for data in csv_data:
                try:
                    writer.writerow(data)
                except Exception:
                    data["Contact Url"] = data["Contact Url"].encode('utf-8')
                    writer.writerow(data)
    except IOError:
        print("I/O error")
