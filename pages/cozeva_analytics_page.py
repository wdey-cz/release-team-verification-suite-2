import traceback

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core import helpers
from core.base_page import BasePage
from selenium.webdriver.common.by import By
import time
from random import choice

import pytest
import traceback

from core.helpers import Helpers


class AnalyticsLandingPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)

    def is_loading_over(self):
        # Wait for the loader to disappear
        try:
            self.wait_helpers.wait_for_element_invisible(self.ANALYTICS_LOADER, timeout=30)
            return True
        except Exception as e:
            print("Error while waiting for analytics loader to disappear:", str(e))
            traceback.print_exc()
            return False

    # def get_number_of_worksheets(self):


class AnalyticsWorksheetPage(BasePage):
    PAGE_TITLE = [
        (By.XPATH, "//h1[contains(text(),'Analytics')]"),
    ]
    ANALYTICS_LOADER = (By.CLASS_NAME, 'sm_download_cssload_loader')
    APPLY_FILTER = (By.XPATH, '//a[text()="Apply"]')
    SELECTED_YEAR_VALUE = [
        (By.XPATH, '//select[@name="year"]//following::span[@class="multiselect-selected-text"][1]')
    ]
    YEAR_FILTER = [
        (By.XPATH, '//select[@name="year"]//following::button[1]'),
    ]

    def __init__(self, driver):
        super().__init__(driver)
        # Stores the WebElement for service year once located
        self.service_year: WebElement | None = None
        self.drilldown_elements: list[WebElement] | None = None

    def is_loading_over(self):
        # Wait for the loader to disappear
        try:
            self.wait_helpers.wait_for_element_invisible(self.ANALYTICS_LOADER, timeout=30)
            return True
        except Exception as e:
            print("Error while waiting for analytics loader to disappear:", str(e))
            traceback.print_exc()
            return False

    def find_element_with_retry(self, locators, timeout=10):
        """
        Try multiple locators and return the first successful element.
        Logs which locator worked.
        """
        last_exception = None

        for index, locator in enumerate(locators):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                print(f"[SUCCESS] Locator #{index+1} worked: {locator}")
                return element

            except Exception as e:
                print(f"[RETRY] Locator #{index+1} failed: {locator}")
                last_exception = e

        print("[FAILED] All locators failed.")
        traceback.print_exc()
        raise last_exception

    def get_text_with_retry(self, locators, timeout=10):
        """
        Helper method to fetch text from an element using fallback locators.
        Internally uses retry logic defined in BasePage.
        """
        element = self.find_element_with_retry(locators, timeout)
        return element.text.strip()

    def get_selected_service_year(self):
        """
        Finds the currently selected service year from the UI.

        Returns:
        [1, value] → if element is found and value extracted
        [0, None] → if element not found or page not ready
        """

        try:
            # Ensure page loading is complete before interacting
            if not self.is_loading_over():
                print("[INFO] Page not ready, loader still present")
                return [0, None]

            # Locate the element using fallback locators and store reference
            self.service_year = self.find_element_with_retry(
                self.SELECTED_YEAR_VALUE
            )

            # Extract text from the stored WebElement
            value = self.service_year.text.strip()

            # Success log
            print(f"[SUCCESS] Service year found: {value}")

            return [1, value]

        except Exception as e:
            print("[ERROR] find_service_year:", str(e))
            traceback.print_exc()
            return [0, None]

    def apply_filter(self):
        """
        Click Apply using helpers.action_click (no retry)
        """
        try:
            # Wait until element is clickable
            apply_filter = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.APPLY_FILTER)
            )

            # Use helper click
            Helpers.action_click(self.driver, apply_filter)

            # Wait for loader
            if not self.is_loading_over():
                return False

            print("[SUCCESS] Applied filter")
            return True

        except Exception as e:
            print("[ERROR] apply_filter:", str(e))
            traceback.print_exc()
            return False

    #def set_service_year(self,year):
        #Check if service year is present

        #set service year
        #click on apply
        #wait for page load













