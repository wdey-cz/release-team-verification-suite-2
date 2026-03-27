import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By
import time
from random import choice

import pytest
import traceback

class AnalyticsBasePage(BasePage):

    ANALYTICS_BASE_URL = "/analytics"

    # Basic Locators
    ANALYTICS_LOADER = (By.CLASS_NAME,'sm_download_cssload_loader')


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

class CozevaQualityOverviewPage(AnalyticsBasePage):

    #Locators
    QUALITY_OVERVIEW_TITLE = (By.XPATH, "//div[contains(@class, 'sm_panel_heading') and contains(@class, 'text-darken-2')]")

    def __init__(self, driver):
        super().__init__(driver)

    def is_quality_overview_page_opened(self):
        # check that the quality overview page has opened by looking for the title element
        try:
            if self.is_loading_over():
                title_element = self.wait_helpers.wait_for_element_visible(self.QUALITY_OVERVIEW_TITLE, timeout=10)
                if title_element and "Quality Overview" in title_element.text:
                    return "OPEN"
                else:
                    print("Quality Overview title element found but text did not match. Found text: " + (title_element.text if title_element else "None"))
                    return "NOT_OPEN"
            else:
                print("Loading did not complete successfully, cannot verify Quality Overview page.")
                return "LOADING_ISSUE"
        except Exception as e:
            print("Error while checking if Quality Overview page is opened:", str(e))
            traceback.print_exc()
            return False



