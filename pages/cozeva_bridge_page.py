from core.base_page import BasePage
from selenium.webdriver.common.by import By
import pytest
import traceback

class CozevaBridgePage(BasePage):

    # LOCATORS
    BRIDGE_APP_HEADING = (By.ID, "bridge_app_heading")

    # Functions
    def __init__(self, driver):
        super().__init__(driver)

    def is_bridge_page_opened(self):
        try:
            self.is_element_present(self.BRIDGE_APP_HEADING, timeout=10)
            return True
        except Exception as e:
            print("Bridge page not opened:", str(e))
            return False