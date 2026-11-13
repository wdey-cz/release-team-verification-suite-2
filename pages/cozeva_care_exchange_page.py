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

class CozevaCareExchangePage(BasePage):

    # LOCATORS
    CARE_EXCHANGE_HEADING = (By.CLASS_NAME, "table_header")

    # Functions
    def __init__(self, driver):
        super().__init__(driver)

    def is_care_exchange_page_opened(self):
        try:
            self.is_element_present(self.CARE_EXCHANGE_HEADING, timeout=10)
            return True
        except Exception as e:
            print("Care Exchange page not opened:", str(e))
            return False