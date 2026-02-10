import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By

class CozevaRegistriesPage(BasePage):

    REGISTRIES_URL = "/registries?"

    # Locators
    REGISTRIES_TABLE = (By.ID, "registries-table")
    REGISTRY_ROWS = (By.CSS_SELECTOR, "#registries-table tbody tr")

    def __init__(self, driver):
        super().__init__(driver)

    def get_registry_table_entries(self):
        return

    def registry_test_method(self):
        try:
            # Placeholder for actual implementation
            print(self.REGISTRIES_URL)
            print("jchvbvjswbvwuobswvnclwsdbsjdSDVFDFHARGRTJRFENFQBDGBETNHYTW")
            pass
        except Exception as e:
            print("Error in registry_test_method:", e)
            traceback.print_exc()
