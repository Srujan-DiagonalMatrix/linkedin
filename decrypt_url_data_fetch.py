import time
import argparse
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from config import li_username, li_password,chrome_driver_path
from config import csv_filepath, csv_w_filepath
import csv
import os

csv_data = []
linkedin_urls = []


class Connect:

    def __init__(self):
        self.driver = None
        self.read_input_csv()

    def setup_driver(self):
        self.driver = webdriver.Chrome(executable_path=chrome_driver_path)
        self.driver.get("https://www.linkedin.com/uas/login")
        time.sleep(5)
        self.driver.maximize_window()
        time.sleep(2)
        self.driver.find_element_by_name('session_key').send_keys(li_username)
        self.driver.find_element_by_name('session_password').send_keys(li_password)
        self.driver.find_element_by_name('session_password').send_keys(Keys.RETURN)
        time.sleep(5)

    def __del__(self):
        if self.driver:
            self.driver.close()

    def search_results(self, url):
        try:
            self.driver.get(url)
            time.sleep(15)
        except Exception as e:
            print('ERROR: Invalid URL : ---------- ' + url)
            print(self.driver.current_url)
            pass

    def get_contact_link(self, url):
        try:
            time.sleep(5)
            action_menu_selector = 'div[class="artdeco-dropdown artdeco-dropdown--placement-bottom artdeco-dropdown--justification-right ember-view"] > button'
            self.driver.find_element_by_css_selector(action_menu_selector).click()
            time.sleep(7)
            self.driver.find_element_by_css_selector('div[data-control-name="copy_linkedin"]').click()
            time.sleep(6)
            li_link = pyperclip.paste()
            print(li_link)
            return li_link
        except Exception as e:
            return f"Problem in getting the Linkedin url for ::{url}"

    def get_second_degree_contact(self, url):
        try:
            time.sleep(5)
            element = self.driver.find_element_by_css_selector('span[class="label-16dp block"]')
            print(element.text)
            try:
                common_text = self.driver.find_element_by_css_selector('div.incommon-entity > dl > dd').text
                entity = self.driver.find_element_by_css_selector('div.incommon-entity > dl > dt').text
                if 'groups' in entity:
                    return common_text.split("in the")[1].strip()
                elif 'connections' in entity:
                    return common_text.split("know")[1].strip()
            except Exception as e:
                pass
            try:
                element1 = self.driver.find_element_by_css_selector('li[class="incommon profile-highlight-card relative overflow-hidden inline-block mr4"] > p')
                print(f"{element1.text} for {url}")
                return element.text.strip()
            except Exception as e:
                return element.text.strip()
        except Exception as e:
            return f"Problem in getting the degree for::{url}"

    def get_connections(self, url):
        try:
            element = self.driver.find_element_by_css_selector("div[class='profile-topcard__connections-data type-total inline t-14 t-black--light mr5']")
            return element.text.split(" ")[0].strip()
        except Exception as e:
            return f"Problem in finding the connections for::{url}"

    @staticmethod
    def read_input_csv():
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
    def read_output_csv():
        output_list = []
        with open(csv_w_filepath, 'r') as myFile:
            try:
                reader = csv.reader(myFile, delimiter=',', quoting=csv.QUOTE_NONE)
            except Exception as e:
                reader = csv.reader(myFile)
            header = next(reader)
            for row in reader:
                try:
                    if len(row) >= 1:
                        output_dict = {'Contact Url': row[0], 'Mutuals Contacts': row[1], 'Connections': row[2]}
                        output_list.append(output_dict)
                    else:
                        print("Line is blank...")
                except Exception as e:
                    pass
        assert len(output_list), "No data found in output_contacts.csv"
        return output_list

    @staticmethod
    def write_output_csv(csv_data_list):
        try:
            fields = ['Contact Url', 'Mutuals Contacts', 'Connections']
            with open(csv_w_filepath, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                for data in csv_data_list:
                    try:
                        writer.writerow(data)
                    except Exception as e:
                        data["Contact Url"] = data["Contact Url"].encode('utf-8')
                        writer.writerow(data)
        except IOError:
            print("I/O error")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Gather command line arguments'
    )
    parser.add_argument(
        '-u', '--url', action="store_true", help='Fetch Linkedin url only'
    )
    parser.add_argument(
        '-d',
        '--degree',
        action="store_true",
        help="Fetch mutual contacts/groups",
    )
    parser.add_argument(
        '-c',
        '--connections',
        action="store_true",
        help='Fetch number of connections',
    )
    args = parser.parse_args()
    url = args.url
    degree = args.degree
    connections = args.connections

    cn = Connect()
    if url and degree and connections:
        cn.setup_driver()
        if os.path.isfile(csv_w_filepath):
            os.remove(csv_w_filepath)
        for url in range(len(linkedin_urls)):
            cn.search_results(linkedin_urls[url])
            li_link = cn.get_contact_link(linkedin_urls[url])
            degree = cn.get_second_degree_contact(linkedin_urls[url])
            connections = cn.get_connections(linkedin_urls[url])
            dict_data = {'Contact Url': li_link, 'Mutuals Contacts': degree, 'Connections': connections}
            csv_data.append(dict_data)
        cn.write_output_csv(csv_data)

    elif url and not degree and not connections:
        cn.setup_driver()
        if os.path.isfile(csv_w_filepath):
            os.remove(csv_w_filepath)
        for url in range(len(linkedin_urls)):
            cn.search_results(linkedin_urls[url])
            li_link = cn.get_contact_link(linkedin_urls[url])
            dict_data = {'Contact Url': li_link, 'Mutuals Contacts': None, 'Connections': None}
            csv_data.append(dict_data)
        cn.write_output_csv(csv_data)

    elif degree and not url and not connections:
        if not os.path.isfile(csv_w_filepath):
            assert False, "No output file found to append mutual contacts/groups"
        url_data = cn.read_output_csv()
        cn.setup_driver()
        for url in range(len(linkedin_urls)):
            cn.search_results(linkedin_urls[url])
            li_link = url_data[url]['Contact Url']
            degree = cn.get_second_degree_contact(linkedin_urls[url])
            connections = url_data[url]['Connections']
            dict_data = {'Contact Url': li_link, 'Mutuals Contacts': degree, 'Connections': connections}
            csv_data.append(dict_data)
        cn.write_output_csv(csv_data)

    elif connections and not url and not degree:
        if not os.path.isfile(csv_w_filepath):
            assert False, "No output file found to append mutual contacts/groups"
        url_data = cn.read_output_csv()
        cn.setup_driver()
        for url in range(len(linkedin_urls)):
            cn.search_results(linkedin_urls[url])
            li_link = url_data[url]['Contact Url']
            degree = url_data[url]['Mutuals Contacts']
            connections = cn.get_connections(linkedin_urls[url])
            dict_data = {'Contact Url': li_link, 'Mutuals Contacts': degree, 'Connections': connections}
            csv_data.append(dict_data)
        cn.write_output_csv(csv_data)

    else:
        print("Please enter the valid combination of command line arguments")
