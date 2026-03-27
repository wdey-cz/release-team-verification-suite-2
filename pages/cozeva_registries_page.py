import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By
import time
from random import choice

import pytest
import traceback


class CozevaRegistriesPage(BasePage):


    REGISTRIES_BASE_URL = "/registries?"

    #Locators
    REGISTRIES_KEBAB = (By.XPATH, "//a[@data-target='datatable_filter_dropdown_metric_scorecard']")
    REGISTRIES_KEBAB_EXPORT_ALL = (By.XPATH, "//a[@id='qt-export-reg-all']")
    REGISTRIES_DEEPLINK = (By.ID, "reg-qwb-trigger")

    LOB_DROPDOWN_CONTAINER = (By.ID, 'reg-filters')

    REGISTRIES_LOB_DROPDOWN = (By.ID, 'qt-filter-label')
    LOB_DROPDOWN_MEASUREMENT_YEARS = (By.XPATH, "//ul[@id='filter-quarter']/li")
    DEFAULT_MEASUREMENT_YEAR = (By.XPATH, "//ul[@id='filter-quarter']/li[contains(@class, 'highlight')]")

    LOB_DROPDOWN_LOBS = (By.XPATH, "//ul[@id='filter-lob']/li")
    DEFAULT_LOB = (By.XPATH, "//ul[@id='filter-lob']/li[contains(@class, 'highlight')]")

    LOB_APPLY = (By.ID, 'reg-filter-apply')

    # Summary Bar Locators
    SUMMARY_BAR = (By.XPATH, "//div[contains(@class, 'registry_header_panel')]")
    SUMMARY_GAP_COUNT = (By.ID, 'reg-header-gapcount')
    SUMMARY_OVERALL_RATING = (By.ID, 'reg-header-overall-rating')
    SUMMARY_PATIENT_COUNT = (By.XPATH, "//div[contains(@class, 'registry_header_panel')]//div[contains(@class, 'header-card-name') and contains(text(), 'Patients')]/following-sibling::div")

    SUMMARY_OVERALL_RATING_CHART = "xx"








    def __init__(self, driver):
        super().__init__(driver)

    def is_registries_page_opened(self):
        # Check the url contains the expected path
        if self.REGISTRIES_BASE_URL not in self.driver.current_url:
            print(f"Current URL does not contain expected path. Current URL: {self.driver.current_url}")
            return False
        return True

    def download_export_all_registries(self):
        try:
            self.click_element(self.REGISTRIES_KEBAB)
            time.sleep(1)  # Wait for the dropdown to open
            self.click_element(self.REGISTRIES_KEBAB_EXPORT_ALL)
            print("Clicked Export All option.")
        except Exception as e:
            print("Error during Export All click:", str(e))
            traceback.print_exc()

    def click_on_deeplink(self):
        try:
            self.click_element(self.REGISTRIES_DEEPLINK)
            print("Clicked on registries deeplink.")
        except Exception as e:
            print("Error during clicking on registries deeplink:", str(e))
            traceback.print_exc()

    def open_lob_dropdown(self):
        # Check if the container is visible, if not click the dropdown to open it
        try:
            container = self.find_element(self.LOB_DROPDOWN_CONTAINER, timeout=5)
            if container and container.is_displayed():
                print("LOB dropdown container is already visible.")
                return True
            else:
                print("LOB dropdown container is not visible. Attempting to open it...")
                self.click_element(self.REGISTRIES_LOB_DROPDOWN)
                time.sleep(1)  # Wait for dropdown to open
                # Check again if the container is visible after clicking
                container = self.find_element(self.LOB_DROPDOWN_CONTAINER, timeout=5)
                if container and container.is_displayed():
                    print("LOB dropdown container is now visible after clicking.")
                    return True
                else:
                    print("Failed to make LOB dropdown container visible after clicking.")
                    return False
        except Exception as e:
            print("Error while trying to open LOB dropdown:", str(e))
            traceback.print_exc()
            return False

    def fetch_my_and_lob(self):
        LoBs = []
        MYs= []
        try:
            self.open_lob_dropdown()  # Wait for dropdown to open

            # Fetch Measurement Years
            my_elements = self.find_elements(self.LOB_DROPDOWN_MEASUREMENT_YEARS, timeout=10)
            for elem in my_elements:
                MYs.append(elem.text.strip())

            # Fetch Default Measurement Year
            default_my_element = self.find_element(self.DEFAULT_MEASUREMENT_YEAR, timeout=10)
            default_my = default_my_element.text.strip() if default_my_element else "None"


            # Fetch LOBs
            lob_elements = self.find_elements(self.LOB_DROPDOWN_LOBS, timeout=10)
            for elem in lob_elements:
                LoBs.append(elem.text.strip())

            # Fetch Default LOB
            default_lob_element = self.find_element(self.DEFAULT_LOB, timeout=10)
            default_lob = default_lob_element.text.strip() if default_lob_element else "None"

            my_lob_dict = {'MY' : MYs, 'LOB' : LoBs}
            my_lob_default = {'MY' : default_my, 'LOB' : default_lob}


            # print("Fetched Measurement Years:", MYs)
            # print("Default Measurement Year:", default_my)
            # print("Fetched LOBs:", LoBs)
            # print("Default LOB:", default_lob)

            return my_lob_dict, my_lob_default

        except Exception as e:
            print("Error while fetching MYs and LOBs:", str(e))
            traceback.print_exc()

    def switch_lob(self, lob_name):
        # Click the dropdown to open it, select the given lobname, click apply.
        try:
            self.open_lob_dropdown()  # Wait for dropdown to open

            # Fetch LOBs
            lob_elements = self.find_elements(self.LOB_DROPDOWN_LOBS, timeout=10)
            for elem in lob_elements:
                if elem.text.strip() == lob_name:
                    elem.click()
                    print(f"Selected LOB: {lob_name}")
                    break
            else:
                print(f"LOB '{lob_name}' not found in dropdown options.")
                return

            # Click Apply
            self.click_element(self.LOB_APPLY)
            print("Clicked Apply after selecting LOB.")
            self.ajax_preloader_wait("Waiting for page to reload after switching to LOB: " + lob_name)

        except Exception as e:
            print("Error while switching LOB:", str(e))
            traceback.print_exc()

    def switch_my(self, year):
        # Click the dropdown to open it, select the given year, click apply.
        try:
            self.open_lob_dropdown()  # Wait for dropdown to open

            # Fetch Measurement Years
            my_elements = self.find_elements(self.LOB_DROPDOWN_MEASUREMENT_YEARS, timeout=10)
            for elem in my_elements:
                if elem.text.strip() == year:
                    elem.click()
                    print(f"Selected Measurement Year: {year}")
                    break
            else:
                print(f"Measurement Year '{year}' not found in dropdown options.")
                return

            # Click Apply
            self.click_element(self.LOB_APPLY)
            print("Clicked Apply after selecting Measurement Year.")
            self.ajax_preloader_wait("Waiting for page to reload after switching to Measurement Year: " + year)

        except Exception as e:
            print("Error while switching Measurement Year:", str(e))
            traceback.print_exc()

    def fetch_summary_bar_info(self):
        # This function returns a tuple with the gap count, overall rating and patient count from the summary bar
        try:
            gap_count_element = self.find_element(self.SUMMARY_GAP_COUNT, timeout=10)
            overall_rating_element = self.find_element(self.SUMMARY_OVERALL_RATING, timeout=10)
            patient_count_element = self.find_element(self.SUMMARY_PATIENT_COUNT, timeout=10)
            gap_count = gap_count_element.text.strip() if gap_count_element else "None"
            overall_rating = overall_rating_element.text.strip() if overall_rating_element else "None"
            patient_count = patient_count_element.text.strip() if patient_count_element else "None"
            print(f"Fetched Summary Bar Info - Gap Count: {gap_count}, Overall Rating: {overall_rating}, Patient Count: {patient_count}")
            return gap_count, overall_rating, patient_count
        except Exception as e:
            print("Error while fetching summary bar info:", str(e))
            traceback.print_exc()
            return "None", "None", "None"




