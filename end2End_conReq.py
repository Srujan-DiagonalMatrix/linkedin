##JI#!/usr/bin/env python

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
        global today_exec_list, user_data_list
        today_exec_list = []
        user_data_list = []

    @staticmethod
    def send_conn_req():
        """ Send Connection Request
        """
        global driver, exec_log

        End2EndConReq.init_logger()

        # Get Start Time
        exec_log["start_time"] = strftime("%d-%m-%Y %H:%M:%S", gmtime())
        print("Start Time = ", str(exec_log["start_time"]))

        for usr in range(config.total_li_user):
            driver = webdriver.Chrome(executable_path=config.chrome_driver_path)
            usr_name = eval("config.li_username_" + str(usr + 1))
            usr_pwd = eval("config.li_password_" + str(usr + 1))
            if not usr_name:
                continue
            print("Processing for User : ", usr_name)
            End2EndConReq.li_login(usr_name, usr_pwd)
            status = End2EndConReq.get_input_data(usr_name)
            if status:
                End2EndConReq.today_execution_contact()
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
    def get_input_data(usr):
        """ Get Input user data from CSV
        """
        global user_data_list
        csv_file = "I_O/" + usr + ".csv"

        try:
            with open(csv_file, 'r') as f:
                try:
                    reader = csv.reader(f, delimiter=';')
                    print(str(sys.argv[1]))
                except Exception as e:
                    reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    tmp_dict = {}
                    try:
                        tmp_dict.update( {"date" : row[0]} )
                        tmp_dict.update( {"li_url" : row[1]} )
                        tmp_dict.update( {"var_1" : row[2]} )
                        tmp_dict.update( {"var_2" : row[3]} )
                        tmp_dict.update( {"var_3" : row[4]} )
                        tmp_dict.update( {"var_4" : row[5]} )
                        tmp_dict.update( {"var_5" : row[6]} )
                        tmp_dict.update({"2nd_msg" : row[7]} )
                        tmp_dict.update({"3rd_msg" : row[8]} )

                        if len(tmp_dict["li_url"]):
                            user_data_list.append(tmp_dict)
                        else:
                            print("Line is blank...")
                    except Exception as e:
                        pass
            return True
        except Exception as e:
            return False

    @staticmethod
    def today_execution_contact():
        """ Get Mutual Contact Info
        """
        global today_exec_list, exec_log
        user_to_exec_today = 0
        today = str(strftime("%d-%m-%Y %H:%M:%S", gmtime()).split("-")[0])
        month = str(strftime("%d-%m-%Y %H:%M:%S", gmtime()).split("-")[1])

        for data in user_data_list:
            usr_set_day = str(data["date"]).split("-")[0]
            usr_set_month = str(data["date"]).split("-")[1]
            if (int(str(month)) == int(str(usr_set_month)) and
                int(str(today)) == int(str(usr_set_day))):
                print("User configure for today : ", data["li_url"])
                today_exec_list.append(data)
                user_to_exec_today += 1
            else:
                pass
        if not user_to_exec_today:
            print("No User Configured to execute today...")
        exec_log["total_input_user"] += user_to_exec_today

    @staticmethod
    def get_mutual_contact():
        """ Get Mutual Contacts
        """
        global exec_log
        for cnt in today_exec_list:
            try:
                print("Processing URL = {0}".format(cnt["li_url"]))
                driver.get(cnt["li_url"])
                time.sleep(5)
                End2EndConReq.total_results(cnt)
            except:
                exec_log["failure_cnt"] += 1
                print("ERROR: Invalid URL : ---------- " + cnt["li_url"])
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
            End2EndConReq.degree_of_connection(name_p, degree_p, cnt)
        else:
            print("Failed to Fetch Name and Degree of Connection...")
            exec_log["failure_cnt"] += 1

    @staticmethod
    def degree_of_connection(usr_name, degree, cnt):
        """ Get Degree of Connection and Mutual data
        """
        global exec_log

        if degree == "2nd":
            try:
                element = WebDriverWait(driver,50).until(
                    EC.presence_of_element_located((By.CLASS_NAME,"pv-highlight-entity__secondary-text"))
                )
                try:
                    time.sleep(5)
                    msg = driver.find_elements_by_css_selector(".pv-highlight-entity__secondary-text")
                    try:
                        mutual_msg = str(msg[0].text).replace(',',';').split("know")[1]
                    except Exception as e:
                        mutual_msg = str(msg[0].text).replace(',', ';')
                    End2EndConReq.send_req(usr_name, mutual_msg, degree, cnt)
                except Exception as e:
                    exec_log["failure_cnt"] += 1
            except Exception as e:
                exec_log["failure_cnt"] += 1

        if degree == "3rd":
            try:
                End2EndConReq.send_req(usr_name, None, degree, cnt)
            except Exception as e:
                exec_log["failure_cnt"] += 1

        if degree == "1st":
            print("User is 1st Degree so it already connected...")
            exec_log["failure_cnt"] += 1

    @staticmethod
    def send_req(name, mutual, degree, cnt):
        """ Send request with appropriate message
        """
        global exec_log

        if degree == "2nd":
            try:
                msg = cnt['2nd_msg']
                msg = msg.replace("<runtime_firstName>", str(str(name).split()[0]))
                msg = msg.replace("<runtime_commoncontacts_msg>", str(mutual))
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

                try:
                    print("\n\nconnecting to 2nd degree contact with msg = ", msg)
                    time.sleep(2)
                    driver.execute_script('document.getElementsByClassName("artdeco-button__text")[2].click();')
                    elm = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        "button.artdeco-button--3:nth-child(1)"))
                        )
                    elm.click()

                    time.sleep(2)
                    elm = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        "#custom-message"))
                    )
                    elm.send_keys(str(msg))

                    time.sleep(2)
                    elm = driver.find_elements_by_class_name("artdeco-button__text")
                    for el in elm:
                        if "Send invitation" in el.text:
                            el.click()
                            break
                    time.sleep(5)
                    # elm = WebDriverWait(driver, 50).until(
                    #    EC.presence_of_element_located((By.CSS_SELECTOR,
                    #                                    "button.artdeco-button:nth-child(2)"))
                    # )
                    # elm.click()
                    print("\nConnection request send successfully....\n")
                    exec_log["2nd_sent"] += 1
                except Exception as e:
                    # traceback.print_exc()
                    # print("\nConnection request already sent to contact = ", name)
                    # exec_log["failure_cnt"] += 1
                    pass
            except Exception as e:
                print(e)
                exec_log["failure_cnt"] += 1

        if degree == "3rd":
            try:
                msg = cnt['3rd_msg']
                msg = msg.replace("<runtime_firstName>", str(str(name).split()[0]))
                try:
                    print("\nconnecting to 3rd degree contact with msg = ", msg)
                    time.sleep(2)
                    name = driver.find_elements_by_class_name('artdeco-button__text')
                    for elm in name:
                        if "More" in elm.text:
                            elm.click()

                    # Click on connect button
                    time.sleep(2)
                    driver.find_element_by_xpath("//*[@type='connect-icon']").click()

                    time.sleep(2)
                    elm = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        "button.artdeco-button--3:nth-child(1)"))
                    )
                    elm.click()

                    time.sleep(2)
                    elm = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        "#custom-message"))
                    )
                    elm.send_keys(str(msg))

                    time.sleep(2)
                    elm = driver.find_elements_by_class_name("artdeco-button__text")
                    for el in elm:
                        if "Send invitation" in el.text:
                            el.click()
                            break
                    time.sleep(5)
                    # elm = WebDriverWait(driver, 50).until(
                    #     EC.presence_of_element_located((By.CSS_SELECTOR,
                    #                                     "button.artdeco-button:nth-child(2)"))
                    # )
                    # elm.click()
                    print("\nConnection request send successfully....")
                    exec_log['3rd_sent'] += 1
                except Exception as e:
                    # print("\nConnection request already sent to contact = ", name)
                    # exec_log["failure_cnt"] += 1
                    pass
            except Exception as e:
                print(e)
                exec_log["failure_cnt"] += 1


if __name__ == '__main__':

    # Initiate execution
    End2EndConReq.send_conn_req()

    # Dump info into log report
    logger_file.dump_log(exec_log)

