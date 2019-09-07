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
time.sleep(5)
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
                                         "mutual_contacts" : row[1],
                                         "name" : row[2],
                                         "second_degree" : row[3],
                                         "third_degree" : row[4]}
                                        )
                    self.csv_data.append(raw_data_buf)
                else:
                    print('# ' + row[0] + ' ' + row[2] + "'s linkedin is blank")
        print("CSV DATA = ", self.csv_data)

    def send_req(self):
        for index in range(len(self.csv_data)):
            self.search_results(index, self.csv_data[index]['l_url'])
            time.sleep(10)

    def search_results(self, index, url):
        # Get Person Name
        try:
            driver.get(url)
            time.sleep(5)
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
            self.degree_of_connection(index, degree[0].text, name[0].text)
        except Exception as e:
            print(e)

    def degree_of_connection(self, index, degree, usr_name):

        if degree == "1st":
            print("\n\nAlready connected with contacts", usr_name)

        if degree == "2nd":
            try:
                self.csv_data[index]["second_degree"] = self.csv_data[index]["second_degree"].replace(';', ',')
                self.csv_data[index]["mutual_contacts"] = self.csv_data[index]["mutual_contacts"].replace(';', ',')
                cnt_msg = self.csv_data[index]["second_degree"].replace("<FirstName>",
                                                                        self.csv_data[index]["name"]).replace("<Mutual contacts>",
                                                                                            self.csv_data[index]["mutual_contacts"])
                try:
                    print("\n\nconnecting to 2nd degree contact with msg = ", cnt_msg)
                    time.sleep(20)
                    driver.execute_script('document.getElementsByClassName("artdeco-button__text")[2].click();')
                    
                    time.sleep(20)
 
                    elm = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        "button.artdeco-button--3:nth-child(1)"))
                    )
                    elm.click()
                    
                    time.sleep(20)
                    elm = WebDriverWait(driver, 50).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        "#custom-message"))
                    )
                    elm.send_keys(str(cnt_msg))

                    time.sleep(20)
                    elm = WebDriverWait(driver, 50).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        "button.artdeco-button:nth-child(2)"))
                    )
                    elm.click()
                    print("\n\nConnection request send successfully....\n")
                except Exception as e:
                    print("\n\nConnection request already sent to contact = ", usr_name)
            except Exception as e:
                print(e)

        if degree == "3rd":
            try:
                self.csv_data[index]["third_degree"] = self.csv_data[index]["third_degree"].replace(';', ',')
                cnt_msg = self.csv_data[index]["third_degree"].replace("<FirstName>",
                                                                       self.csv_data[index]["name"])
                try:
                    print("\n\nconnecting to 3rd degree contact with msg = ", cnt_msg)
                    time.sleep(20)
                    name = driver.find_elements_by_class_name('artdeco-button__text')
                    for elm in name:
                        if "More" in elm.text:
                            elm.click()

                    # Click on connect btton
                    time.sleep(20)
                    driver.find_element_by_xpath("//*[@type='connect-icon']").click()

                    # driver.execute_script('document.getElementsByClassName
                    # ("display-flex t-normal pv-s-profile-actions__label")[2].click();')

                    time.sleep(20)
                    elm = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR,
                                                            "button.artdeco-button--3:nth-child(1)"))
                        )
                    elm.click()

                    time.sleep(20)
                    elm = WebDriverWait(driver, 50).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                            "#custom-message"))
                        )
                    elm.send_keys(str(cnt_msg))
                    
                    time.sleep(20)
                    elm = WebDriverWait(driver, 50).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR,
                                                            "button.artdeco-button:nth-child(2)"))
                            )
                    time.sleep(20)
                    elm.click()
                    print("\n\nConnection request send successfully....")
                except Exception as e:
                    print("\n\nConnection request already sent to contact = ", usr_name)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    cn_obj = Connect()
    cn_obj.read_csv()
    cn_obj.send_req()
    driver.quit()
