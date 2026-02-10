import traceback

from selenium.webdriver.support.select import Select

from core.base_page import BasePage
from selenium.webdriver.common.by import By
from core.config import Config


class CozevaReasonForLoginPage(BasePage):

    REASON_FOR_LOGIN_URL = "/reasonForlogin"
    REASON_FOR_LOGIN = Config.REASON_FOR_LOGIN

    # Locators
    REASON_TEXTBOX = (By.ID, "reason_textbox")
    SUBMIT_BUTTON = (By.ID, "edit-submit")
    CUSTOMER_SELECTION_DROPDOWN = (By.ID, "select-customer")

    def __init__(self, driver):
        super().__init__(driver)

    def is_reason_page_opened(self):
        try:
            current_url = self.get_page_report()["CURRENT_URL"]
            return self.REASON_FOR_LOGIN_URL in current_url
        except Exception as e:
            print("Error checking if Reason for Login page is opened:", e)
            traceback.print_exc()
            return False

    def enter_reason(self):
        self.enter_text(self.REASON_TEXTBOX, self.REASON_FOR_LOGIN, 30)

    def click_submit(self):
        self.click_element(self.SUBMIT_BUTTON, 30)

    def select_customer(self, client_id):
        dropdown_element = Select(self.find_element(self.CUSTOMER_SELECTION_DROPDOWN))
        dropdown_element.select_by_value(str(client_id))

    def enter_reason_select_customer_and_submit(self, client_id):
        self.enter_reason()
        self.select_customer(client_id)
        self.click_submit()



