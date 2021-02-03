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
            li_url = url
            driver.get(li_url)
            time.sleep(15)
        except Exception as e:
            print('ERROR: Invalid URL : ---------- ' + li_url)
            print(driver.current_url)
            pass

    @staticmethod
    def get_contact_link(url):
        try:
            time.sleep(5)
            action_menu_selector = 'div[class="artdeco-dropdown artdeco-dropdown--placement-bottom artdeco-dropdown--justification-right ember-view"] > button'
            driver.find_element_by_css_selector(action_menu_selector).click()
            time.sleep(7)
            driver.find_element_by_css_selector('div[data-control-name="copy_linkedin"]').click()
            time.sleep(6)
            li_link = pyperclip.paste()
            print(li_link)
            return li_link
        except Exception as e:
            return f"Problem in getting the Linkedin url for ::{url}"

    @staticmethod
    def get_second_degree_contact(url):
        try:
            time.sleep(5)
            element = driver.find_element_by_css_selector('span[class="label-16dp block"]')
            print(element.text)
            try:
                common_text = driver.find_element_by_css_selector('div.incommon-entity > dl > dd').text
                entity = driver.find_element_by_css_selector('div.incommon-entity > dl > dt').text
                if 'groups' in entity:
                    return common_text.split("in the")[1].strip()
                elif 'connections' in entity:
                    return common_text.split("know")[1].strip()
            except Exception as e:
                pass
            try:
                element1 = driver.find_element_by_css_selector('li[class="incommon profile-highlight-card relative overflow-hidden inline-block mr4"] > p')
                print(f"{element1.text} for {url}")
                return element.text.strip()
            except Exception as e:
                pass
        except Exception as e:
            return f"Problem in getting the degree for::{url}"

    @staticmethod
    def get_connections(url):
        try:
            element = driver.find_element_by_css_selector("div[class='profile-topcard__connections-data type-total inline t-14 t-black--light mr5']")
            return element.text.split(" ")[0].strip()
        except Exception as e:
            return f"Problem in finding the connections for::{url}"


if __name__ == '__main__':
    cn = Connect()
    for url in range(len(linkedin_urls)):
        cn.search_results(linkedin_urls[url])
        li_link = cn.get_contact_link(linkedin_urls[url])
        degree = cn.get_second_degree_contact(linkedin_urls[url])
        connections = cn.get_connections(linkedin_urls[url])
        dict_data = {'Contact Url': li_link, 'Mutuals Contacts': degree, 'Connections': connections}
        csv_data.append(dict_data)
    driver.quit()

    try:
        fields = ['Contact Url', 'Mutuals Contacts', 'Connections']
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
