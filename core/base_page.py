from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from core.wait_helpers import WaitHelpers


class BasePage:

    def __init__(self, driver):
        self.driver = driver
        self.wait_helpers = WaitHelpers(driver)

    def find_element(self, locator, timeout=10):
        # Find an element with explicit wait, return WebElement if found
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def find_elements(self, locator, timeout=10):
        # Find multiple elements with explicit wait, return list of WebElements
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        return self.driver.find_elements(*locator)

    def click_element(self, locator, timeout=10):
        # Click an element after waiting for it to be clickable
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        element.click()

    def enter_text(self, locator, text, timeout=10):
        # Enter text into an input field after waiting for it to be visible
        element = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        print("Entering text:", text)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator, timeout=10):
        # Get text from an element after waiting for it to be visible
        element = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        return element.text

    def navigate_to_url(self, url):
        # Navigate to a specified URL
        self.driver.get(url)
    @staticmethod
    def sleep_code(sleep_time):
        # Pause execution for a specified number of seconds
        time.sleep(sleep_time)



