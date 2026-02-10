import traceback

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
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

    def click_element(self, target, timeout=10, desc=None):
        """
        target can be:
          - locator tuple: (By.X, "value")
          - WebElement
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(target)
            )
        except Exception:
            if desc:
                print(f"[click_element] Timed out waiting clickable: {desc}")

            # Fallback: resolve element if target is a locator
            if isinstance(target, WebElement):
                element = target
            else:
                element = self.driver.find_element(*target)

        try:
            element.click()
        except Exception:
            if desc:
                print(f"[click_element] Normal click failed, JS clicking: {desc}")
            self.driver.execute_script("arguments[0].click();", element)

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

    def is_element_visible(self, locator, timeout=10):
        # Check if an element is visible within the specified timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except:
            return False

    def is_element_interactable(self, locator, timeout=10):
        # Check if an element is clickable within the specified timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
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

    def ajax_preloader_wait(self):
        # wait for the ajax preloader to appear, load then dissapear, then wait for any drupal messages to disappear
        try:
            self.wait_helpers.wait_for_element_visible((By.CLASS_NAME, "ajax_preloader"), timeout=10)
            print("ajax_preloader visible")
        except TimeoutException:
            print("ajax_preloader did not appear, continuing without waiting for it to disappear")
            return


        self.wait_helpers.wait_for_element_invisible((By.CLASS_NAME, "ajax_preloader"), timeout=300)
        print("ajax_preloader invisible")
        self.wait_helpers.wait_for_element_invisible((By.CLASS_NAME, "drupal_message_text"), timeout=300)
        print("drupal_message_text invisible")

        if self.is_element_present((By.XPATH, "//*[@id='announcement_list']"), timeout=5):
            try:
                self.driver.find_element(By.XPATH, "//a[@OnClick='closeAnnouncements();']").click()
                print("Announcement closed")
            except Exception as e:
                print("Announcement not present")

    def scroll_to_view(self, target, timeout=10):
        if isinstance(target, WebElement):
            element = target
        else:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(target)
            )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            element
        )
        self.sleep_code(0.2)

    # def switch_back_to_CS(self):



class HeaderNavBar(BasePage):
    # Locators
    HEADER_BAR = (By.CLASS_NAME, "navbar-fixed")
    GLOBAL_SEARCH_BAR_INPUT = (By.ID, "globalsearch_input")
    NOTIFICATION_BELL = (By.ID, "notification_button")
    HELP_DROPDOWN = (By.XPATH, "//a[@data-target='help_menu_dropdown']")
    HELP_MENU_OPTION_ELEMENTS = (By.XPATH, "//ul[@id='help_menu_options']/li/a")

    USER_ICON = (By.XPATH, "//a[@data-target='user_menu_dropdown']")
    USER_DROPDOWN_ELEMENT = (By.ID, "user_menu_dropdown")
    USER_DROPDOWN_OPTION_ELEMENTS = (By.XPATH, "//ul[@id='user_menu_options']/li/a")

    SWITCH_BACK_TO_CS_BUTTON = (By.XPATH, "//a[contains(@href, '/masquerade') and contains(text(), 'Switch Back')]")
    SWITCH_BACK_TO_CS_BUTTON_NEXT_SCREEN = (By.XPATH, "//a[contains(@href, '/unmasquerade') and contains(text(), 'Switch back')]")



    def __init__(self, driver):
        super().__init__(driver)

    def click_user_dropdown_option(self, option_name):
        # check if user dropdown is open, if not click to open it
        if not self.is_element_interactable(self.USER_DROPDOWN_ELEMENT, timeout=2):
            self.click_element(self.USER_ICON, timeout=10)

        # click the option in the dropdown. Basically, using the option name, compare each element in user dropdown until you find the one that matches, then click it
        option_elements = self.find_elements(self.USER_DROPDOWN_OPTION_ELEMENTS, timeout=10)
        for option_element in option_elements:
            print("Comparing option:", option_element.text.strip().lower(), "to", option_name.strip().lower())
            if option_element.text.strip().lower() == option_name.strip().lower():
                option_element.click()
                self.ajax_preloader_wait()
                return

    def switch_back(self):
        # click the switch back button in the header nav bar, then wait for the next screen's switch back button to appear to confirm navigation
        self.click_element(self.SWITCH_BACK_TO_CS_BUTTON, timeout=10)
        self.wait_helpers.wait_for_element_visible(self.SWITCH_BACK_TO_CS_BUTTON_NEXT_SCREEN, timeout=30)
        self.click_element(self.SWITCH_BACK_TO_CS_BUTTON_NEXT_SCREEN, timeout=10)
        self.ajax_preloader_wait()
















