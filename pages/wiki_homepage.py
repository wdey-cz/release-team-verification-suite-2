import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By


class WikiHomePage(BasePage):

    SEARCH_BAR = (By.ID, "searchInput")
    SUGGESTION_DROPDOWN = (By.CLASS_NAME, "suggestions-dropdown")
    SUGGESTIONS = (By.CLASS_NAME, "suggestion-link")
    SUGGESTION_TEXT = (By.CLASS_NAME, "suggestion-highlight")
    LANGUAGES_ELEMENT = (By.XPATH, "//nav[contains(@class, 'central-featured')]")
    TOP_LANGUAGES = (By.XPATH, "//div[contains(@class, 'central-featured-lang')]")  # returns a list of all top language divs
    WIKI_LOGO = (By.XPATH, "//img[@alt='Wikipedia']")


    def __init__(self, driver):
        super().__init__(driver)

    def click_search_bar(self):
        self.click_element(self.SEARCH_BAR, 30)

    def clear_search_bar(self):
        search_bar_element = self.find_element(self.SEARCH_BAR, 30)
        search_bar_element.clear()

    def search(self, text):
        self.click_search_bar()
        self.clear_search_bar()
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

    def get_suggestions_from_search_term(self, search_term):
        # Check if there is already a search term in the bar, if its the same as the new one, skip entering it again
        current_search_text = self.get_element_attribute(self.SEARCH_BAR, "value", 5)
        print("Current search bar text:", current_search_text)
        if current_search_text != search_term:
            print("Adding search term to search bar:", search_term)
            self.search(search_term)

        return self.get_suggestions()


    def suggestion_dropdown_exists(self):
        return self.is_element_present(self.SUGGESTION_DROPDOWN, 5)

    def click_suggestion(self, index):
        # Verify if Suggestion Dropdown is visible. If its not, validate that there is text in the search bar and click the search bar again
        if not self.suggestion_dropdown_exists():
            search_bar_text = self.get_element_attribute(self.SEARCH_BAR, "value", 5)
            if search_bar_text:
                self.click_search_bar()
            else:
                raise Exception("Suggestion dropdown not visible and search bar is empty.")

        # Now fetch the suggestions again
        suggestions_elements = self.find_elements(self.SUGGESTIONS, 30)
        if index < 0 or index >= len(suggestions_elements):
            raise IndexError("Suggestion index out of range.")
        self.click_element(suggestions_elements[index], 10)

    def languages_element_exists(self):
        return self.is_element_present(self.LANGUAGES_ELEMENT, 5)

    def wiki_logo_exists(self):
        return self.is_element_present(self.WIKI_LOGO, 5)

    # returns a str list of the top languages on the homepage
    def get_top_languages_list(self):
        # check that language element exists
        if not self.languages_element_exists():
            raise Exception("Languages element not found on the homepage.")

        language_elements = self.find_elements(self.TOP_LANGUAGES, 10)
        language_list = []

        for elem in language_elements:
            language_header = self.find_element(self.GET_STRONG_TAGS_LOCATOR, 10, root=elem)
            language_list.append(language_header.text)

        return language_list

    def click_language_by_name(self, language_name):
        # check that language element exists
        if not self.languages_element_exists():
            raise Exception("Languages element not found on the homepage.")

        language_elements = self.find_elements(self.TOP_LANGUAGES, 10)

        for elem in language_elements:
            language_header = self.find_element(self.GET_STRONG_TAGS_LOCATOR, 10, root=elem)
            if language_header.text.lower() == language_name.lower():
                elem.click()
                return

        raise Exception(f"Language '{language_name}' not found on the homepage.")











