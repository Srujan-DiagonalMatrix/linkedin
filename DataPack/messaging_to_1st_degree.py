#!/usr/bin/env python

################################################
#
# Get Contact info from URL and Send Connection
# request with appropriate message
#
#################################################

# Selenium Specific Modules
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Core Python Modules
import csv
import os
import sys
import time
from time import gmtime, strftime
import traceback

# Custom Modules
import config
import logger_file



if os.path.isfile("ConReqReport.txt"):
    os.remove("ConReqReport.txt")

# Macros
exec_log = {}
driver = None
user_data_list = []
today_exec_list = []
sales_user = False


class End2EndConReq:
    """ Send Conn Req into Linkedin Users
    """

    @staticmethod
    def init_logger():
        """ Initialize all the logger counter
        """
        global exec_log
        exec_log["start_time"] = 0
        exec_log["end_time"] = 0
        exec_log["total_input_user"] = 0
        exec_log["failure_cnt"] = 0
        exec_log["1st_sent"] = 0
        exec_log['2nd_sent'] = 0
        exec_log['3rd_sent'] = 0
        exec_log['total_sent'] = 0

    @staticmethod
    def clean_data_buffer():
        """ Clean object
        """
        global today_exec_list, user_data_list, sales_user
        today_exec_list = []
        user_data_list = []
        sales_user = False

    @staticmethod
    def send_message():
        """ Send Connection Request
        """
        global driver, exec_log, sales_user

        End2EndConReq.init_logger()

        # Get Start Time
        exec_log["start_time"] = strftime("%d-%m-%Y %H:%M:%S", gmtime())
        print("Start Time = ", str(exec_log["start_time"]))

        for usr in range(config.total_li_user):
            usr_name = eval("config.li_username_" + str(usr + 1))
            usr_pwd = eval("config.li_password_" + str(usr + 1))
            if not usr_name:
                continue
            status = End2EndConReq.get_input_data()
            print("Processing for User : ", usr_name)
            driver = webdriver.Chrome(executable_path=config.chrome_driver_path)
            End2EndConReq.li_login(usr_name, usr_pwd)
            if status:
                End2EndConReq.today_execution_contact(usr_name.lower())
                time.sleep(5)
                End2EndConReq.get_mutual_contact()
                driver.quit()
                End2EndConReq.clean_data_buffer()
            else:
                print("Skipping user {0} bcoz input data file not found...".format(usr_name))
                driver.quit()

        exec_log['total_sent'] = int(exec_log["1st_sent"]) + int(exec_log['2nd_sent']) + int(exec_log['3rd_sent'])
        # Get End Time
        exec_log["end_time"] = strftime("%d-%m-%Y %H:%M:%S", gmtime())
        print("End Time = ", str(exec_log["end_time"]))

    @staticmethod
    def li_login(usr, pwd):
        """ Login into Linkedin
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
    def get_input_data():
        """ Get Input user data from CSV
        """
        global user_data_list
        csv_file = config.input_file
        try:
            with open(csv_file, 'r') as f:
                try:
                    reader = csv.reader(f, delimiter = ';')
                except Exception as e:
                    reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    tmp_dict = {}
                    try:
                        tmp_dict.update( {"date" : row[0]} )
                        tmp_dict.update( {"usr" : row[1]} )
                        tmp_dict.update( {"url" : row[2]} )
                        tmp_dict.update( {"f_name" : row[3]} )
                        tmp_dict.update( {"var_1" : row[4]} )
                        tmp_dict.update( {"var_2" : row[5]} )
                        tmp_dict.update( {"var_3" : row[6]} )
                        tmp_dict.update( {"var_4" : row[7]} )
                        tmp_dict.update( {"var_5" : row[8]} )
                        tmp_dict.update( {"msg"   : row[9]} )
                        if len(tmp_dict["usr"]):
                            user_data_list.append(tmp_dict)
                        else:
                            print("Line is blank...")
                    except Exception as e:
                        pass
            print("Data loaded from CSV = ", user_data_list)
            return True
        except Exception as e:
            return False

    @staticmethod
    def today_execution_contact(usr):
        """ Get Mutual Contact Info
        """
        global today_exec_list, exec_log
        user_to_exec_today = 0
        today = str(strftime("%d/%m/%Y %H:%M:%S", gmtime()).split("/")[0])
        month = str(strftime("%d/%m/%Y %H:%M:%S", gmtime()).split("/")[1])

        for data in user_data_list:
            usr_set_day = str(data["date"]).split("/")[0]
            usr_set_month = str(data["date"]).split("/")[1]
            if (int(str(month)) == int(str(usr_set_month)) and
                int(str(today)) == int(str(usr_set_day))):
                if str(usr) == str(data["usr"].lower()):
                    print("User configure for today : ", data["url"])
                    today_exec_list.append(data)
                    user_to_exec_today += 1
                else:
                    pass
            else:
                pass
        if not user_to_exec_today:
            print("No User Configured to execute today...")
        exec_log["total_input_user"] += user_to_exec_today

    @staticmethod
    def get_mutual_contact():
        """ Get Mutual Contacts
        """
        global exec_log, today_exec_list
        for cnt in today_exec_list:
            try:
                print("Processing URL = {0}".format(cnt["url"]))
                driver.get(cnt["url"].replace(';', ','))
                time.sleep(5)
                if sales_user:
                    cnt["url"] = driver.current_url
                    continue
                End2EndConReq.total_results(cnt)
            except:
                exec_log["failure_cnt"] += 1
                print("ERROR: Invalid URL : ---------- " + cnt["url"])
                time.sleep(5)

    @staticmethod
    def total_results(cnt):
        # Get Person Name
        global exec_log
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
            End2EndConReq.send_msg(degree_p, cnt)
        else:
            print("Failed to Fetch Name and Degree of Connection...")
            exec_log["failure_cnt"] += 1

    @staticmethod
    def send_msg(degree, cnt):
        """ Send request with appropriate message
        """
        global exec_log

        if degree == "1st":
            try:
                msg = cnt['msg'].replace(';', ',')
                try:
                    msg = msg.replace("<fname>", str(cnt["f_name"]))
                except:
                    pass
                try:
                    msg = msg.replace("<var1>", str(cnt['var_1']))
                except:
                    pass
                try:
                    msg = msg.replace("<var2>", str(cnt['var_2']))
                except:
                    pass
                try:
                    msg = msg.replace("<var3>", str(cnt['var_3']))
                except:
                    pass
                try:
                    msg = msg.replace("<var4>", str(cnt['var_4']))
                except:
                    pass
                try:
                    msg = msg.replace("<var5>", str(cnt['var_5']))
                except:
                    pass
            except Exception as e:
                print("Failed to prepare connection message...")

            try:
                # Get MSG button Class Elements
                elms = driver.find_elements_by_class_name("artdeco-button__text")
                time.sleep(10)
                for elm in elms:
                    # If msg button found than cick on it
                    if str(elm.text) == "Message":
                        elm.click()
                        break
                time.sleep(10)
                txt_box = driver.find_element_by_css_selector(".msg-form__contenteditable")
                print("Sending Message = ", msg)
                txt_box.send_keys(str(msg))
                time.sleep(10)
                driver.find_element_by_xpath("//*[@type='submit']").click()
                time.sleep(10)
                print("Message Send successfully.......")
		time.sleep(10)
                exec_log['1st_sent'] += 1
            except Exception:
                print("Failed to send Message to User")
                exec_log["failure_cnt"] += 1

        if degree == "3rd":
            print("Connection is 3rd degree so no need to send message...")
            exec_log["failure_cnt"] += 1

        if degree == "2nd":
            print("Connection is 2nd degree so no need to send message...")
            exec_log["failure_cnt"] += 1


if __name__ == '__main__':

    # Initiate execution
    End2EndConReq.send_message()

    # Dump info into log report
    logger_file.dump_log(exec_log)
