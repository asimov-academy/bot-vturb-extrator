import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


class Browser:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.options = Options()
        if self.headless:
            self.options.add_argument("--headless")

    def open(self):
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        self.driver.maximize_window()
        return self.driver

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def wait_for_element(self, xpath, timeout=10):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
        except TimeoutException:
            return None

    def double_click(self, element):
        ActionChains(self.driver).double_click(element).perform()
    
    def find_element_by_xpath(self, element):
        return self.driver.find_element(By.XPATH, element)

    def find_elements_by_xpath(self, element) -> list:
        return self.driver.find_elements(By.XPATH, element)
    
    def visit(self, url):
        self.driver.get(url)

    def wait(self, seconds):
        time.sleep(seconds)