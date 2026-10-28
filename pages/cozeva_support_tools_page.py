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

class CozevaSupportToolsPage(BasePage):

    # LOCATORS
    SUPPORT_TOOLS_HEADING = (By.CLASS_NAME, "header")

    # Functions
    def __init__(self, driver):
        super().__init__(driver)

    def is_support_tools_page_opened(self):
        try:
            self.is_element_present(self.SUPPORT_TOOLS_HEADING, timeout=10)
            return True
        except Exception as e:
            print("Support Tools page not opened:", str(e))
            return False