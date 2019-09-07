import time
import csv
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from config import li_username, li_password,chrome_driver_path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import csv_filepath


driver = webdriver.Chrome(executable_path=chrome_driver_path)
driver.get("https://www.linkedin.com/uas/login")
time.sleep(3)
driver.maximize_window()
time.sleep(2)
driver.find_element_by_name('session_key').send_keys(li_username)
driver.find_element_by_name('session_password').send_keys(li_password)
driver.find_element_by_name('session_password').send_keys(Keys.RETURN);
time.sleep(5)


class Connect():

    def __init__(self):
        self.csv_data = []

    def read_csv(self, ):

        with open(csv_filepath, 'r') as f:
            try:
                reader = csv.reader(f, delimiter=',')
            except Exception as e:
                reader = csv.reader(f)

            header = next(reader)
            for row in reader:
                raw_data_buf = {}
                l_url = row[0]
                if l_url:
                    raw_data_buf.update({"l_url": row[0],
                                         "contact_name" : row[1],
                                         "var1" : row[2],
                                         "var2" : row[3],
                                         "var3" : row[4],
                                         "var4" : row[5],
                                         "var5" : row[6],
                                         "msg"  : row[7]
                                         })
                    self.csv_data.append(raw_data_buf)
                else:
                    print('# ' + row[0] + ' ' + row[1] + "'s linkedin is blank")
        print("CSV DATA = ", self.csv_data)

    def send_req(self):
        for index in range(len(self.csv_data)):
            self.search_results(index, self.csv_data[index]['l_url'])
            time.sleep(30)

    def search_results(self, index, url):
        # Get Person Name
        try:
            driver.get(url)
            time.sleep(15)
            name = driver.find_elements_by_css_selector('li.inline.t-24.t-black.t-normal.break-words')
            print("\nName of person = ", str(name[0].text))
            if not (str(name[0].text)):
                print("\nNo Result Found...")
        except Exception as e:
            print("\nInvalid URL...")

        # Get Person degree
        try:
            degree = driver.find_elements_by_css_selector('span.dist-value')
            print("\nDegree of connection = ", str(degree[0].text))
            self.send_msg(index, degree[0].text, name[0].text)
        except Exception as e:
            print(e)

    def send_msg(self, index, degree, usr_name):

        if degree == "1st":
            try:
                # Prepare Message
                self.csv_data[index]["msg"] = self.csv_data[index]["msg"].replace('<fname>', self.csv_data[index]["contact_name"])
                self.csv_data[index]["msg"] = self.csv_data[index]["msg"].replace('<var1>',self.csv_data[index]["var1"])
                self.csv_data[index]["msg"] = self.csv_data[index]["msg"].replace('<var2>',self.csv_data[index]["var2"])
                self.csv_data[index]["msg"] = self.csv_data[index]["msg"].replace('<var3>',self.csv_data[index]["var3"])
                self.csv_data[index]["msg"] = self.csv_data[index]["msg"].replace('<var4>',self.csv_data[index]["var4"])
                self.csv_data[index]["msg"] = self.csv_data[index]["msg"].replace('<var5>',self.csv_data[index]["var5"]).replace(';' , ',')

                # Get MSG button Class Elements
                elms = driver.find_elements_by_class_name("artdeco-button__text")
                time.sleep(20)
                for elm in elms:
                    # If msg button found than cick on it
                    if str(elm.text) == "Message":
                        elm.click()
                        break
                time.sleep(20)
                txt_box = driver.find_element_by_css_selector(".msg-form__contenteditable")
                print("Sending Message = ", self.csv_data[index]["msg"])
                txt_box.send_keys(str(self.csv_data[index]["msg"]))
                time.sleep(20)
                driver.find_element_by_xpath("//*[@type='submit']").click()
                print("Message Send successfully.......")
            except Exception:
                print("Failed to send Message to User = ", usr_name)
        elif degree == "2nd":
            print("Connection is second degree so no need to send message...")
        elif degree == "3rd":
            print("Connection is third degree so no need to send message...")


if __name__ == '__main__':
    cn_obj = Connect()
    cn_obj.read_csv()
    cn_obj.send_req()
    driver.quit()