import json
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException 
from selenium.common.exceptions import ElementClickInterceptedException

JSESSIONID = "REPLACE ME"
SECONDS_BETWEEN_CHECKS = 10
grades_url = ""

# Set up Chrome options (optional)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection as a bot
chrome_options.add_argument("--no-sandbox")  # Useful for some environments
chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent shared memory issues
chrome_options.add_argument("--remote-debugging-port=9222")

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

def nav(element_list, name, max_attempts = -1):
    attempts = 0
    while True:
        try:
            curr_element = driver
            for element in element_list:
                curr_element = curr_element.find_element(element[0], element[1])
            time.sleep(0.5)
            curr_element.click()
            print(f"\033[92mClicked {name}\033[0m")
            return True
        except (NoSuchElementException,ElementClickInterceptedException):
            print(f"\033[93mCould not find {name}, retrying...\033[0m")
            attempts += 1
            if attempts == max_attempts:
                return False
            time.sleep(0.5)

def get_grades_table():
    global grades_url
    while True:
        try:
            element = driver.find_element(By.CSS_SELECTOR, '[data-testid="table"]')
            tbody_element = element.find_element(By.CSS_SELECTOR, 'tbody')
            entries = tbody_element.find_elements(By.XPATH, './*')

            res = {}
            for entry in entries:
                entry_data = []
                for child in entry.find_elements(By.XPATH, './*'):
                    entry_data.append(child.text)
                if len(entry_data) <= 1:
                    raise ValueError("oof")
                res[entry_data[0]] = entry_data[4]

            print("\033[92mFound grades table\033[0m")
            grades_url = driver.current_url

            return res
        except (NoSuchElementException, ValueError): 
            print("\033[93mCould not find grades table, retrying...\033[0m")
            time.sleep(0.5)

def get_grades(academic_period="2024-25 Winter Session (UBC-V)", retries_before_JSESSIONID_expiry=10):

    driver.get("https://wd10.myworkday.com/")

    driver.add_cookie({"name": "JSESSIONID", "value": JSESSIONID})
    global grades_url
    if len(grades_url) > 0:
        driver.get(grades_url)
        return get_grades_table()
        
    driver.implicitly_wait(0.5)
    driver.get("https://wd10.myworkday.com/ubc/d/home.htmld")

    if nav([
        (By.CSS_SELECTOR, '[data-uxi-element-id="pex-view-all-apps"]')
    ], "view all apps", max_attempts=retries_before_JSESSIONID_expiry) == False:
        print("\033[91mJSESSIONID likely expired, please get a new one\033[0m")
        driver.quit()
        sys.exit()

    nav([
        (By.CSS_SELECTOR, '[aria-label="Academics"][itemtype="app"]')
        ], "academics page")
    
    nav([
        (By.CSS_SELECTOR, '[class="WDVQ"][role="listitem"][aria-setsize="3"][aria-posinset="3"]')
        ], "view my grades page")
    
    nav([
        (By.XPATH, '//*[contains(text(), "Academic Period")]'),
        (By.XPATH, '..'),
        (By.XPATH, '..'),
        (By.CSS_SELECTOR, '[data-automation-id="decorationWrapper"]'),
        ], "academic period selector")
    
    nav([
        (By.CSS_SELECTOR, f'[data-automation-label="{academic_period}"]')
        ], "academic period")
 
    nav([
        (By.CSS_SELECTOR, '[data-automation-activebutton="true"][data-uxi-actionbutton-action="bpf-submit"][title="OK"]')
        ], "OK button")

    return get_grades_table()

# with open("config.json", "r") as f:
#     jssid = json.load(f)["JSESSIONID"]

prev_grades = {}
for i in range(5):
    new_grades = get_grades()
    found_new = False
    for course in new_grades.keys():
        if new_grades[course] == "":
            continue
        if course not in prev_grades.keys():
            print(f"\033[92mNew course: {course} with grade {new_grades[course]}\033[0m")
            found_new = True
        elif prev_grades[course] == "":
            print(f"\033[92mNew course grade: {course} with grade {new_grades[course]}\033[0m")
            found_new = True
        elif prev_grades[course] != new_grades[course]:
            print(f"\033[92mCourse grade updated: {course} with grade {new_grades[course]}\033[0m")
            found_new = True
    prev_grades = new_grades
    if not found_new:
        print("\033[93mNo new grades found this time\033[0m")
    time.sleep(SECONDS_BETWEEN_CHECKS)