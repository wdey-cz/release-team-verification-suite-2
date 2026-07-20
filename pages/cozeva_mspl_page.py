import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By
import time
from random import choice

import pytest
import traceback

class CozevaMSPLPage(BasePage):

    MSPL_TITLE = (By.XPATH, "//div[contains(@class, 'metric_specific_patient_list_title')]")

    # Locators for support and practice mspl
    TAB_BAR_SUPPORT_PRACTICE = (By.XPATH, "//ul[@id='qt-mt-support-ls']")
    TAB_BAR_PRACTICES = (By.XPATH, "//ul[@id='qt-mt-support-ls']//a[contains(text(), 'Practices')]")
    PRACTICE_TABLE = (By.XPATH, "//table[@id='metric-support-prac-ls']/tbody")
    TAB_BAR_PROVIDERS = (By.XPATH, "//ul[@id='qt-mt-support-ls']//a[contains(text(), 'Providers')]")
    PROVIDER_TABLE = (By.XPATH, "//table[@id='metric-support-prov-ls']/tbody")
    TAB_BAR_PATIENTS = (By.XPATH, "//ul[@id='qt-mt-support-ls']//a[contains(text(), 'Patients')]")
    PATIENTS_TABLE = (By.XPATH, "//table[@id='metric-support-pat-ls']/tbody")
    TAB_BAR_PERFORMANCE_STATISTICS = (By.XPATH,
                                      "//ul[@id='qt-mt-support-ls']//a[contains(text(), 'Performance Statistics')]")

    # locators for provider mspl
    TAB_BAR_PROVIDER = (By.XPATH, "//ul[@class='tabs']")
    TAB_PATIENTS_PROVMSPL = (By.XPATH, "//ul[@class='tabs']//a[contains(text(), 'Patients')]")
    PATIENTS_TABLE_PROVMSPL = (By.XPATH, "//table[@id='quality_registry_list']/tbody")
    TAB_PERFORMANCE_STATISTICS_PROVMSPL = (By.XPATH, "//ul[@class='tabs']//a[contains(text(), 'Performance Statistics')]")
    TAB_NETWORK_COMPARISON_PROVMSPL = (By.XPATH, "//ul[@class='tabs']//a[contains(text(), 'Network Comparison')]")




    def __init__(self, driver):
        super().__init__(driver)

    def is_mspl_page_opened(self):
        try:
            return self.is_element_visible(self.MSPL_TITLE)
        except Exception as e:
            print("Error in checking if MSPL page is opened:", str(e))
            traceback.print_exc()
            return False

    def fetch_mspl_type(self):
        '''
        Determine the type of MSPL page based on the presence of specific elements
        If its a Support MSPL, it will have the support/practice tab bar and the practices, providers, patients, performance statistics tabs.
        If its a Practice MSPL, it will have the support/practice tab bar, providers, patients, performance statistics tabs.
        If its a provider MSPL, it will have the provider tab bar with patients, performance statistics and network comparison tabs.
        check and return the type of mspl page accordingly, if its unable to determine, return unknown.
        '''

        try:
            if self.is_element_visible(self.TAB_BAR_SUPPORT_PRACTICE, timeout=5):
                if self.is_element_visible(self.TAB_BAR_PRACTICES, timeout=5):
                    return "Support MSPL"
                else:
                    return "Practice MSPL"
            elif self.is_element_visible(self.TAB_BAR_PROVIDER, timeout=5):
                return "Provider MSPL"
            else:
                return "Unknown MSPL Type"
        except Exception as e:
            print("Error in determining MSPL type:", str(e))
            traceback.print_exc()
            return "Unknown MSPL Type"

    def click_on_random_patient(self):
        # Fetch the mspl type, then switch case based on that, then click on a random patient from the patients table
        mspl_type = self.fetch_mspl_type()
        print("MSPL Type detected:", mspl_type)
        try:
            if mspl_type in ["Support MSPL", "Practice MSPL"]:
                self.click_element(self.TAB_BAR_PATIENTS)
                self.ajax_preloader_wait("Clicked on Patients tab in " + mspl_type)
                patients_table = self.find_element(self.PATIENTS_TABLE, 10)
                patient_rows = self.find_elements(self.GET_TR_TAGS_LOCATOR, root=patients_table)
                if not patient_rows:
                    print("No patients found in the table.")
                    return
                random_patient_row = choice(patient_rows)
                patient_name = self.find_element(self.GET_ANCHOR_TAGS_LOCATOR, root=random_patient_row)
                self.click_element(patient_name)
                print("Clicked on a random patient in " + mspl_type)
            elif mspl_type == "Provider MSPL":
                self.click_element(self.TAB_PATIENTS_PROVMSPL)
                self.ajax_preloader_wait("Clicked on Patients tab in Provider MSPL")
                patients_table = self.find_element(self.PATIENTS_TABLE_PROVMSPL, 10)
                patient_rows = self.find_elements(self.GET_TR_TAGS_LOCATOR, root=patients_table)
                if not patient_rows:
                    print("No patients found in the provider MSPL table.")
                    return
                random_patient_row = choice(patient_rows)
                patient_name = self.find_element(self.GET_ANCHOR_TAGS_LOCATOR, root=random_patient_row)
                self.click_element(patient_name)
                print("Clicked on a random patient in Provider MSPL")
            else:
                print("Unknown MSPL type, cannot click on patient.")

        except Exception as e:
            print("Error in clicking on random patient:", str(e))
            traceback.print_exc()

    def fetch_practice_names(self):
        if self.is_mspl_page_opened():
            mspl_type = self.fetch_mspl_type()
            print("MSPL Type detected:", mspl_type)
            try:
                if mspl_type in ["Support MSPL"]:
                    self.click_element(self.TAB_BAR_PRACTICES)
                    self.ajax_preloader_wait("Clicked on Practices tab in " + mspl_type)
                    practices_table = self.find_element(self.PRACTICE_TABLE, 10)
                    practice_rows = self.find_elements(self.GET_TR_TAGS_LOCATOR, root=practices_table)
                    practice_names = []
                    for row in practice_rows:
                        try:
                            name_element = self.find_elements(self.GET_ANCHOR_TAGS_LOCATOR, root=row)[1]
                            practice_names.append(name_element.text)
                        except Exception as e:
                            print("Error fetching practice name from row:", e)
                            traceback.print_exc()
                    return practice_names
                else:
                    print("MSPL type is not Support MSPL, cannot fetch practice names.")
                    return []
            except Exception as e:
                print("Error in fetching practice names:", str(e))
                traceback.print_exc()
                return []
        return []

    def fetch_provider_names(self):
        if self.is_mspl_page_opened():
            mspl_type = self.fetch_mspl_type()
            print("MSPL Type detected:", mspl_type)
            try:
                if mspl_type in ["Support MSPL", "Practice MSPL"]:
                    self.click_element(self.TAB_BAR_PROVIDERS)
                    self.ajax_preloader_wait("Clicked on Providers tab in " + mspl_type)
                    providers_table = self.find_element(self.PROVIDER_TABLE, 10)
                    provider_rows = self.find_elements(self.GET_TR_TAGS_LOCATOR, root=providers_table)
                    provider_names = []
                    for row in provider_rows:
                        try:
                            name_element = self.find_elements(self.GET_ANCHOR_TAGS_LOCATOR, root=row)[2]
                            provider_names.append(name_element.text)
                        except Exception as e:
                            print("Error fetching provider name from row:", e)
                            traceback.print_exc()
                    return provider_names
                else:
                    print("MSPL type is not Support or Practice MSPL, cannot fetch provider names.")
                    return []
            except Exception as e:
                print("Error in fetching provider names:", str(e))
                traceback.print_exc()
                return []
        return []

    def fetch_patient_names(self):
        if self.is_mspl_page_opened():
            mspl_type = self.fetch_mspl_type()
            print("MSPL Type detected:", mspl_type)
            try:
                if mspl_type in ["Support MSPL", "Practice MSPL"]:
                    self.click_element(self.TAB_BAR_PATIENTS)
                    self.ajax_preloader_wait("Clicked on Patients tab in " + mspl_type)
                    patients_table = self.find_element(self.PATIENTS_TABLE, 10)
                    patient_rows = self.find_elements(self.GET_TR_TAGS_LOCATOR, root=patients_table)
                    patient_names = []
                    for row in patient_rows:
                        try:
                            name_element = self.find_element(self.GET_ANCHOR_TAGS_LOCATOR, root=row)
                            patient_names.append(name_element.text)
                        except Exception as e:
                            print("Error fetching patient name from row:", e)
                            traceback.print_exc()
                    return patient_names
                elif mspl_type == "Provider MSPL":
                    self.click_element(self.TAB_PATIENTS_PROVMSPL)
                    self.ajax_preloader_wait("Clicked on Patients tab in Provider MSPL")
                    patients_table = self.find_element(self.PATIENTS_TABLE_PROVMSPL, 10)
                    patient_rows = self.find_elements(self.GET_TR_TAGS_LOCATOR, root=patients_table)
                    patient_names = []
                    for row in patient_rows:
                        try:
                            name_element = self.find_element(self.GET_ANCHOR_TAGS_LOCATOR, root=row)
                            patient_names.append(name_element.text)
                        except Exception as e:
                            print("Error fetching patient name from row in Provider MSPL:", e)
                            traceback.print_exc()
                    return patient_names
                else:
                    print("Unknown MSPL type, cannot fetch patient names.")
                    return []
            except Exception as e:
                print("Error in fetching patient names:", str(e))
                traceback.print_exc()
                return []
        return []


    def fetch_global_search_data(self):
        mspl_type = self.fetch_mspl_type()
        print("MSPL Type detected:", mspl_type)
        try:
            # Can try to fetch all 3 data (Prac, prov, pat)
            if mspl_type in ["Support MSPL"]:
                x=0

        except Exception as e:
            print("Error in fetching global search data:", str(e))
            traceback.print_exc()





