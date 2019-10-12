#!/usr/bin/env python

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import config
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from xlwt import Workbook

if os.path.isfile(config.csv_w_filepath):
    os.remove(config.csv_w_filepath)

driver = None
usr_name_list = []
usr_occ_list = []
usr_url_list = []


class connect():

    @staticmethod
    def get_followup(wb):
        """Get Recently Added contacts of input li_user
        """
        global driver
        for usr in range(config.total_li_user):
            driver = webdriver.Chrome(executable_path=config.chrome_driver_path)
            usr_name = eval("config.li_username_" + str(usr + 1))
            usr_pwd  = eval("config.li_password_" + str(usr + 1))
            if not usr_name:
                continue
            print("Getting Recent Connected Contacts for user = ", usr_name)
            connect.li_login(usr_name, usr_pwd)
            connect.open_connection()
            time.sleep(5)
            connect.get_recent_connected_connection(usr)
            time.sleep(5)
            connect.print_user_details(usr)
            connect.dump_data_in_xls(usr, usr_name, wb)
            driver.quit()
            connect.clean_data_buffer()

    @staticmethod
    def li_login(usr, pwd):
        """Login into Linkedin
        """
        driver.get("https://www.linkedin.com/uas/login")
        time.sleep(3)
        driver.maximize_window()
        time.sleep(2)
        driver.find_element_by_name('session_key').send_keys(usr)
        driver.find_element_by_name('session_password').send_keys(pwd)
        driver.find_element_by_name('session_password').send_keys(Keys.RETURN);
        time.sleep(5)

    @staticmethod
    def open_connection():
        """Open Connection tab of linkedin user
        """
        try:
            elm = WebDriverWait(driver,5).until(
                    EC.presence_of_element_located((By.XPATH,"//a[@href='/mynetwork/']"))
                )
        except Exception as err:
            print("My Network Tag Not Found over UI")

        # Click over My Network Button
        try:
            if elm:
                elm.click()
                time.sleep(5)
                elm = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "//a[@href='/mynetwork/invite-connect/connections/']"))
                )
                elm.click()
        except Exception as err:
            print("There is no connection Tag found inside My Network")

    @staticmethod
    def get_recent_connected_connection(usr):
        """Get Recently connected contacts detail
        """
        search_contact = True
        global usr_name_list, usr_occ_list, usr_url_list
        while search_contact:
            try:
                # Get Name
                names = driver.find_elements_by_css_selector("span.mn-connection-card__name.t-16.t-black.t-bold")

                for name in names:
                    if name.text not in usr_name_list:
                        usr_name_list.append(name.text)

                # Get Occupation
                occupations = driver.find_elements_by_css_selector \
                    ("span.mn-connection-card__occupation.t-14.t-black--light.t-normal")
                for occ in occupations:
                    if occ.text not in usr_occ_list:
                        usr_occ_list.append(occ.text)

            except Exception as err:
                print("Name and Occupation details are not found")

            # Get URL details for each user
            try:
                div = driver.find_elements_by_class_name('mn-connection-card__details')
                for elm in div:
                    link = elm.find_element_by_css_selector('a').get_attribute('href')
                    if link not in usr_url_list:
                        usr_url_list.append(link)
            except Exception as err:
                print("user URL's not found......")

            if int(len(usr_url_list)) >= int(eval("config.get_recent_count_" + str(usr + 1))):
                break
            else:
                driver.execute_script("window.scrollTo(0, window.scrollY + 800)")
                time.sleep(5)


    @staticmethod
    def print_user_details(usr):
        """Print User Details
        """
        try:
            cnt = eval("config.get_recent_count_" + str(usr + 1))
            for index in range(int(cnt)):
                try:
                    print("----   User Name --------  ", usr_name_list[index])
                    print("----   User Occupation --  ", usr_occ_list[index])
                    print("----   User Url ---------  ", usr_url_list[index])
                except:
                    pass
        except Exception as err:
            print("Unable to print user information.....")

    @staticmethod
    def dump_data_in_xls(index, usr, wb):
        """Dump data in XLS
        """
        try:
            # Write Heading

            sheet_name = str(usr)
            sheet = wb.add_sheet(sheet_name)
            sheet.write(0,0,"URL")
            sheet.write(0, 1, "Name")
            sheet.write(0, 2, "Company")

            cnt = eval("config.get_recent_count_" + str(index + 1))
            for index in range(int(cnt)):
                try:
                    sheet.write(index + 1, 0, usr_url_list[index])
                    sheet.write(index + 1, 1, usr_name_list[index])
                    sheet.write(index + 1, 2, usr_occ_list[index])
                except:
                    continue
            print("Data written into EXCEL sheet successfully....")
        except Exception as err:
            print("Failed to write data in Excel Sheet for user : ", sheet_name)

    @staticmethod
    def clean_data_buffer():
        """Clean all the data buffer to procced for new user
        """
        global usr_occ_list, usr_name_list, usr_url_list
        usr_name_list = []
        usr_occ_list = []
        usr_url_list = []


if __name__ == '__main__':
    # Create one Excel Sheet Instance
    wb = Workbook()
    connect.get_followup(wb)
    # Save Excel data
    wb.save(config.csv_w_filepath)