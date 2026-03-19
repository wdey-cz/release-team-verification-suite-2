import traceback

from selenium.common import TimeoutException

from core.base_page import BasePage
from selenium.webdriver.common.by import By

class CozevaProvidersPage(BasePage):

    # URLs
    PROVIDERS_BASE_URL = "/providers"

    # Locators
    PROVIDER_PAGE_TITLE = (By.XPATH, "//div[contains(@class, 'metric_specific_patient_list_title') and contains(text(), 'Providers')]")

    # Practice stuff
    PRACTICE_LIST_TAB = (By.XPATH, "//li[contains(@class, 'tab')]/a[contains(text(), 'Practices')]")
    PRACTICE_LIST = (By.XPATH, "//table[@id='metric-support-prac-ls']/tbody")


    # Provider Stuff
    PROVIDER_LIST_TAB = (By.XPATH, "//li[contains(@class, 'tab')]/a[contains(text(), 'Providers')]")
    PROVIDER_LIST = (By.XPATH, "//table[@id='metric-support-prov-ls']/tbody")


    def __init__(self, driver):
        super().__init__(driver)

    def is_providers_page_open(self):
        try:
            return self.is_element_visible(self.PROVIDER_PAGE_TITLE, 10)
        except TimeoutException as e:
            print("Providers page title not found:", e)
            traceback.print_exc()
            return False

    def open_practices_tab(self):
        try:
            self.click_element(self.PRACTICE_LIST_TAB, 10)
        except TimeoutException as e:
            print("Practice List tab not found:", e)
            traceback.print_exc()

    def open_providers_tab(self):
        try:
            self.click_element(self.PROVIDER_LIST_TAB, 10)
        except TimeoutException as e:
            print("Provider List tab not found:", e)
            traceback.print_exc()

    def fetch_practice_names(self):
        # Return the list of practice names from the practice list table
        try:
            self.open_practices_tab()
            self.ajax_preloader_wait("Clicked Practice Tab")
            practice_table = self.find_element(self.PRACTICE_LIST, 10)
            practice_rows = self.find_elements(self.GET_TR_TAGS_LOCATOR, root=practice_table)
            practice_names = []
            for row in practice_rows:
                try:
                    practice_name = self.find_element(self.GET_ANCHOR_TAGS_LOCATOR, root=row).text
                    practice_names.append(practice_name)
                except Exception as e:
                    print("Error fetching practice name from row:", e)
                    traceback.print_exc()
            return practice_names
        except:
            print("Error fetching practice names:")
            traceback.print_exc()
            return []

    def fetch_provider_names(self):
        try:
            try:
                self.open_providers_tab()
            except Exception as e:
                print("Error opening provider tab:", e)
            self.ajax_preloader_wait("Clicked Provider Tab")
            providers_table = self.find_element(self.PROVIDER_LIST, 10)
            # Get all rows in the table body
            provider_rows = self.find_elements(self.GET_TR_TAGS_LOCATOR, root=providers_table)
            provider_names = []
            for row in provider_rows:
                try:

                    provider_name = self.find_elements(self.GET_ANCHOR_TAGS_LOCATOR, root=row)[1].text
                    provider_names.append(provider_name)

                except Exception as e:
                    print("Error fetching provider name from row:", e)
                    traceback.print_exc()

            return provider_names
        except:
            print("Error fetching provider names:")
            traceback.print_exc()
            return []

    def click_provider_by_name(self, provider_name):
        try:
            self.open_providers_tab()
            self.ajax_preloader_wait("Clicked Provider Tab")
            providers_table = self.find_element(self.PROVIDER_LIST, 10)
            provider_rows = self.find_elements(self.GET_TR_TAGS_LOCATOR, root=providers_table)
            for row in provider_rows:
                try:
                    name_element = self.find_elements(self.GET_ANCHOR_TAGS_LOCATOR, root=row)[1]
                    if name_element.text == provider_name:
                        name_element.click()
                        self.ajax_preloader_wait(f"Clicked provider: {provider_name}")
                        return True
                except Exception as e:
                    print(f"Error clicking provider {provider_name} in row:", e)
                    traceback.print_exc()
            print(f"Provider with name {provider_name} not found.")
            return False
        except Exception as e:
            print(f"Error in click_provider_by_name for {provider_name}:", e)
            traceback.print_exc()
            return False

    def click_practice_by_name(self, practice_name):
        try:
            self.open_practices_tab()
            self.ajax_preloader_wait("Clicked Practice Tab")
            practice_table = self.find_element(self.PRACTICE_LIST, 10)
            practice_rows = self.find_elements(self.GET_TR_TAGS_LOCATOR, root=practice_table)
            for row in practice_rows:
                try:
                    name_element = self.find_element(self.GET_ANCHOR_TAGS_LOCATOR, root=row)
                    if name_element.text == practice_name:
                        name_element.click()
                        self.ajax_preloader_wait(f"Clicked practice: {practice_name}")
                        return True
                except Exception as e:
                    print(f"Error clicking practice {practice_name} in row:", e)
                    traceback.print_exc()
            print(f"Practice with name {practice_name} not found.")
            return False
        except Exception as e:
            print(f"Error in click_practice_by_name for {practice_name}:", e)
            traceback.print_exc()
            return False






