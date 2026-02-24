import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By

class CozevaPaymentToolPage(BasePage):

    # URLs
    PAYMENT_TOOL_BASE_URL = "/payment-tool"

    # Locators
    PAYMENT_TOOL_CYCLES = (By.XPATH, "//div[contains(@class, 'program-wrapper') and contains(@class, 'program-active')]")
    PAYMENT_NOT_ENABLED_MESSAGE = (By.XPATH, "//div[contains(@class, 'display-grid') and contains(@class, 'center-align') and contains(text(), 'You do not have any active or previously completed programs.')]")

    # PAYMENT_TOOL_CYCLES interior locators
    CYCLE_NAME = (By.XPATH, ".//div[contains(@class, 'quarter-wrapper')]/div[1]")
    PAYMENT_TOOL_CARDS = (By.XPATH, ".//div[contains(@class, 'program-state') and contains(@class, 'display-grid')]")



    def __init__(self, driver):
        super().__init__(driver)

    def go_to_payment_tool_page(self, base_url):
        try:
            self.navigate_to_url("https://www.cozeva.com/incentives/dashboard?session=YXBwX2lkPXJlZ2lzdHJpZXMmY3VzdElkPTQ0NTAmb3JnSWQ9NDQ1MCZwVWlkPTExNTM3OCZ2Z3BJZD00NDUwJnZwSWQ9NDQ1MA==")
        except Exception as e:
            print("Error navigating to Cozeva Payment Tool page:", e)
            traceback.print_exc()

    def is_payment_tool_page_open(self):
        # return the len of the cycles element list if payment tool is enabled. if 0, then not displayed, if 1 or more, then displayed
        if self.is_payment_tool_enabled():
            return len(self.find_elements(self.PAYMENT_TOOL_CYCLES, 10)) > 0
        else:
            return "Disabled"



    def is_payment_tool_enabled(self):
        # Check if the "not enabled" message is displayed. If it is, then payment tool is not enabled. If it is not, then it is enabled.
        return len(self.find_elements(self.PAYMENT_NOT_ENABLED_MESSAGE, 2)) == 0



    def fetch_payment_tool_cards_per_cycle(self):
        # Return a dict with cycle name as key, and list of card names as values
        cycles = self.find_elements(self.PAYMENT_TOOL_CYCLES, 10)
        cycle_card_dict = {}
        for cycle in cycles:
            try:
                cycle_name = self.find_element(self.CYCLE_NAME, 5, root=cycle).text
                cards = self.find_elements(self.PAYMENT_TOOL_CARDS, 5, root=cycle)
                cycle_card_dict[cycle_name] = len(cards)
            except Exception as e:
                print(f"Error fetching cards for cycle {cycle_name}: {e}")
                traceback.print_exc()
        return cycle_card_dict



