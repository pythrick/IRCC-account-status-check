import json
import logging
import time
from pathlib import Path

from selenium import webdriver
from send_status import send_telegram
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import os

os.environ["DISPLAY"] = ":99"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / 'config.json') as config_file:
    data = json.load(config_file)

chrome_options = Options()

# Next 2 lines prevent selenium detection as a bot
chrome_options.add_argument("--disable-blink-features")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# TODO: Сделать запуск в headless режиме
# chrome_options.headless = True
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('disable-gpu')

service = Service(ChromeDriverManager().install())


def checkprofile():
    driver = webdriver.Chrome(service=service, options=chrome_options)
    url = "https://onlineservices-servicesenligne-cic.fjgc-gccf.gc.ca/mycic/gccf?lang=eng&idp=gckey&svc=/mycic/start"

    def buttonclick():
        driver.find_element(By.CLASS_NAME, 'btn.btn-primary').click()
        time.sleep(3)

    # driver.minimize_window()
    driver.get(url)

    username = driver.find_element(By.ID, 'token1')
    login = data["login"]
    username.send_keys(login)

    password_input = driver.find_element(By.ID, 'token2')
    password = data["password"]
    password_input.send_keys(password)
    time.sleep(3)

    buttonclick()
    if len(driver.find_elements(By.CLASS_NAME, 'btn.btn-default.cancel')) > 0:
        driver.find_element(By.CLASS_NAME, 'btn.btn-default.cancel').click()
    buttonclick()
    buttonclick()

    answer = driver.find_element(By.ID, 'answer')

    questions = data['questions_and_answers']

    for key, value in questions.items():
        if key in driver.page_source:
            answer.send_keys(value)
            buttonclick()

    result = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[1]/div/table/tbody/tr[1]/td[5]').text

    if result == 'Submitted':
        logger.info('Current status: Nothing new, try again later.')
    else:
        driver.get_screenshot_as_file("screenshot.png")
        logger.info('Current status: Update!')
        send_telegram('Ghost update! Check profile ASAP')

    driver.quit()


if __name__ == '__main__':
    checkprofile()
