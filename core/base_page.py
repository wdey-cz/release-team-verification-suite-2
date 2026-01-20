from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from core.wait_helpers import WaitHelpers


class BasePage:
    GET_ANCHOR_TAGS_LOCATOR = (By.TAG_NAME, "a")
    GET_STRONG_TAGS_LOCATOR = (By.TAG_NAME, "strong")
    GET_LI_TAGS_LOCATOR = (By.TAG_NAME, "li")
    GET_TD_TAGS_LOCATOR = (By.TAG_NAME, "td")
    GET_TR_TAGS_LOCATOR = (By.TAG_NAME, "tr")

    def __init__(self, driver):
        self.driver = driver
        self.wait_helpers = WaitHelpers(driver)

    def find_element(self, locator, timeout=10, root=None):
        """
        If root is None: find on page (driver).
        If root is a WebElement: find inside that element.
        """
        if root is None:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
        return root.find_element(*locator)

    def find_elements(self, locator, timeout=10, root=None):
        """
        If root is None: find on page (driver).
        If root is a WebElement: find inside that element.
        """
        if root is None:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        return root.find_elements(*locator)

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

    def get_element_attribute(self, locator, attribute, timeout=10):
        # Get a specific attribute value from an element
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        return element.get_attribute(attribute)

    def is_element_present(self, locator, timeout=10):
        # Check if an element is present within the specified timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except:
            return False

    def navigate_to_url(self, url):
        # Navigate to a specified URL
        self.driver.get(url)

    @staticmethod
    def sleep_code(sleep_time):
        # Pause execution for a specified number of seconds
        time.sleep(sleep_time)

    def get_current_url(self):
        # Return the current URL of the page
        return self.driver.current_url


    def get_page_report(self):
        # Generate a list of important things on the page for reporting purposes
        report = {'CURRENT_URL': self.driver.current_url, 'CURRENT_TITLE': self.driver.title}  # [Current URL, Page Title]
        return report



