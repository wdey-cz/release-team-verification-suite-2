'''
EXAMPLE

from core.base_page import BasePage
from selenium.webdriver.common.by import By
import pytest
import traceback

class CozevaChartReviewPage(BasePage):

    # LOCATORS
    SUPPLEMENTAL_DATA_HEADING = (By.CLASS_NAME, "table_header")

    # Functions
    def __init__(self, driver):
        super().__init__(driver)

    def is_chart_review_page_opened(self):
        try:
            self.is_element_present(self.SUPPLEMENTAL_DATA_HEADING, timeout=10)
            return True
        except Exception as e:
            print("Chart Review page not opened:", str(e))
            return False

'''

from core.base_page import BasePage
from selenium.webdriver.common.by import By
import pytest
import traceback

class CozevaConfigToolsPage(BasePage):

    # LOCATORS
    CONFIG_TOOLS_HEADING = (By.CLASS_NAME, "sm_heading_title")

    # Functions
    def __init__(self, driver):
        super().__init__(driver)

    def is_config_tools_page_opened(self):
        try:
            self.is_element_present(self.CONFIG_TOOLS_HEADING, timeout=10)
            return True
        except Exception as e:
            print("Config Tools page not opened:", str(e))
            return False





