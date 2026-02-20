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

    PRELOADER = (By.CLASS_NAME, "ajax_preloader")
    DRUPAL_MSG = (By.CLASS_NAME, "drupal_message_text")




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

    def ajax_preloader_wait(self, desc="", appear_timeout=3, disappear_timeout=300):
        t0 = time.perf_counter()
        seen = False

        print(f"[ajax] start {desc}", flush=True)

        try:
            WebDriverWait(self.driver, appear_timeout).until(
                EC.visibility_of_element_located(self.PRELOADER)
            )
            seen = True
            print(f"[ajax] preloader appeared in {time.perf_counter() - t0:.2f}s {desc}", flush=True)
        except TimeoutException:
            # Not necessarily an error, it can be fast or delayed
            print(f"[ajax] preloader not seen within {appear_timeout}s {desc}", flush=True)

        if seen:
            WebDriverWait(self.driver, disappear_timeout).until(
                EC.invisibility_of_element_located(self.PRELOADER)
            )
            print(f"[ajax] preloader gone in {time.perf_counter() - t0:.2f}s {desc}", flush=True)

        # This is safe even if it never existed
        WebDriverWait(self.driver, disappear_timeout).until(
            EC.invisibility_of_element_located(self.DRUPAL_MSG)
        )
        print(f"[ajax] drupal message gone in {time.perf_counter() - t0:.2f}s {desc}", flush=True)

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

    # Sidebar locators
    SIDEBAR_MENU_KEBAB = (By.XPATH, "//a[contains(@class, 'sidenav-trigger')]")
    SIDEBAR_SLIDEOUT_ELEMENT = (By.ID, "sidenav_slide_out")

    SIDEBAR_ENTRIES = (By.XPATH, "//li[contains(@class, 'sidebar-menu-item')]/a")

    SUPPORT_SIDEBAR_OPTIONS = ["Registries", "Reports", "Supplemental Data", "HCC Chart List",
                               "AVW Chart List", "AWV Summary", "Exclusion List", "Pending List",
                               "Batches", "Providers", "All Providers", "Imported Charts", "Hospital Activity",
                               "Contact Log", "Sticket Log", "Export Dashboard", "Shared Forms", "Payment Tool"]

    PRACTICE_SIDEBAR_OPTIONS = []
    PROVIDER_SIDEBAR_OPTIONS = []




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

    def open_sidebar(self):
        # check if the sidebar is already open by checking if the slideout element is visible, if not click the kebab menu to open it
        if not self.is_element_visible(self.SIDEBAR_SLIDEOUT_ELEMENT, timeout=5):
            self.click_element(self.SIDEBAR_MENU_KEBAB, timeout=10)
            self.wait_helpers.wait_for_element_visible(self.SIDEBAR_SLIDEOUT_ELEMENT, timeout=10)

    def fetch_sidebar_entries(self):
        # fetch the sidebar entries and return them as a list of strings
        self.open_sidebar()
        entry_elements = self.find_elements(self.SIDEBAR_ENTRIES, timeout=10)
        entries = [elem.text.strip() for elem in entry_elements]
        return entries

    def click_sidebar_entry(self, entry_name):
        # click the sidebar entry that matches the entry name
        self.open_sidebar()
        entry_elements = self.find_elements(self.SIDEBAR_ENTRIES, timeout=10)
        for entry_element in entry_elements:
            #print("Comparing sidebar entry:", entry_element.text.strip().lower(), "to", entry_name.strip().lower())
            if entry_element.text.strip().lower() == entry_name.strip().lower():
                entry_element.click()
                self.ajax_preloader_wait()
                return


















