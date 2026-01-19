import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By


class WikiHomePage(BasePage):

    SEARCH_BAR = (By.ID, "searchInput")
    SUGGESTION_DROPDOWN = (By.CLASS_NAME, "suggestions-dropdown")
    SUGGESTIONS = (By.CLASS_NAME, "suggestion-link")
    SUGGESTION_TEXT = (By.CLASS_NAME, "suggestion-highlight")

    def __init__(self, driver):
        super().__init__(driver)

    def click_search_bar(self):
        self.click_element(self.SEARCH_BAR, 30)

    def search(self, text):
        self.enter_text(self.SEARCH_BAR, text, 30)

    def go_to_homepage(self):
        try:
            self.navigate_to_url("https://www.wikipedia.org/")
        except Exception as e:
            print("Error navigating to homepage:", e)
            traceback.print_exc()

    def get_suggestions(self):
        self.wait_helpers.wait_for_element_visible(self.SUGGESTION_DROPDOWN, 30)
        suggestions_elements = self.find_elements(self.SUGGESTIONS, 30)
        suggestions = [elem.text for elem in suggestions_elements]
        return suggestions




