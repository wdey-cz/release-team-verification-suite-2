import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By

class CozevaUsersPage(BasePage):

    USERS_URL = "/users_list"

    # Locators
    FILTER_SLIDEOUT = (By.XPATH, "//a[contains(@class, 'datatable_filter_dropdown')]")
    FILTER_ELEMENT = (By.XPATH, "//div[contains(@class, 'dt_sidenav_filter ')]")
    FILTER_SEARCH_ELEMENT = (By.XPATH, "//input[@title = 'Search' and @type = 'text']")

    FILTER_APPLY_BUTTON = (By.XPATH, "//a[contains(@class, 'datatable_apply') and contains(@class, 'green-text')]")
    USERS_TABLE = (By.ID, "people_list")
    USERS_TABLE_ENTRIES = (By.CSS_SELECTOR, "#people_list tbody tr")
    USER_ENTRY_USERNAME = (By.XPATH, ".//td[contains(@class, 'username')]")
    USER_ENTRY_FNAME = (By.XPATH, ".//td[contains(@class, 'first_name')]")
    USER_ENTRY_LNAME = (By.XPATH, ".//td[contains(@class, 'last_name ')]")
    USER_ENTRY_ROLE = (By.XPATH, ".//td[contains(@class, 'role_name')]")
    USER_ENTRY_CHECKBOX = (By.XPATH, ".//input[contains(@class, 'selector')]")
    KEBAB_MENU = (By.XPATH, "//a[contains(@class, 'datatable_filter_options') and contains(@data-target, 'datatable_filter_dropdown_people_list_table')]")
    MASQUERADE_OPTION = (By.XPATH, "//a[contains(@id, 'masquerade_user')]")

    # Masqurade page mini interators
    MASQUERADE_PAGE_USERNAME_ELEMENT = (By.ID, "edit-masquerade-user-field")
    MASQUERADE_PAGE_REASON = (By.ID, "edit-masquerade-reason-field")
    MASQUERADE_PAGE_SUBMIT_BUTTON = (By.ID, "edit-submit")
    MASQUERADE_PAGE_SIGNATURE = (By.ID, "edit-drsign")



    def __init__(self, driver):
        super().__init__(driver)

    def filter_search_field(self, filter_text):
        # check if filter slideout is open, if not click to open it
        if not self.is_element_interactable(self.FILTER_ELEMENT, timeout=2):
            self.click_element(self.FILTER_SLIDEOUT, timeout=10)

        # enter text into filter search field
        # self.scroll_to_view(self.FILTER_SEARCH_ELEMENT)
        self.enter_text(self.FILTER_SEARCH_ELEMENT, filter_text, timeout=10)

        # click apply button
        # self.scroll_to_view(self.FILTER_APPLY_BUTTON)
        self.click_element(self.FILTER_APPLY_BUTTON, timeout=10, desc="Click Apply button after entering filter text")

        self.ajax_preloader_wait()

    def masquerade_as_user(self, username, reason="Testing", signature="NONE"):
        # match username to entry in users table, click the checkbox to select that user, click the kebab menu, then click the masquerade option
        # wait for users table to load, if it doesn't load return None

        if not self.is_element_present(self.USERS_TABLE, timeout=10):
            print("Users table did not load")
            return None

        user_entries = self.get_user_table_entries()
        print("Number of user entries found:", len(user_entries))

        for entry in user_entries:
            user_info = self.get_user_info_from_entry(entry)
            if user_info['username'].lower() == username.lower():
                self.select_user_entry_checkbox(entry)
                self.click_element(self.KEBAB_MENU, timeout=10)
                self.click_element(self.MASQUERADE_OPTION, timeout=10)
                self.ajax_preloader_wait()

                if self.is_masquerade_page_opened():
                    self.check_masquerade_username_field(username)
                    self.enter_reason_for_masquerade(reason)
                    self.enter_signature_for_masquerade(signature)
                    self.submit_masquerade()


                return True

            return False

        return None

    def get_user_table_entries(self):
        # returns a list of web elements for each entry in the users table
        return self.find_elements(self.USERS_TABLE_ENTRIES, timeout=10)

    def get_user_info_from_entry(self, entry_element):
        # given a web element for an entry in the users table, return a dictionary with the user's info (username, first name, last name, role)
        user_info = {'username': self.find_element(self.USER_ENTRY_USERNAME, root=entry_element).text.strip(),
                     'first_name': self.find_element(self.USER_ENTRY_FNAME, root=entry_element).text.strip(),
                     'last_name': self.find_element(self.USER_ENTRY_LNAME, root=entry_element).text.strip(),
                     'role': self.find_element(self.USER_ENTRY_ROLE, root=entry_element).text.strip()}
        print("Extracted user info from entry:", user_info)
        return user_info

    def select_user_entry_checkbox(self, entry_element):
        # given a web element for an entry in the users table, click the checkbox to select that user
        checkbox_element = self.find_element(self.USER_ENTRY_CHECKBOX, root=entry_element)
        if not checkbox_element.is_selected():
            self.click_element(checkbox_element, timeout=2, desc="Click checkbox to select user entry for masquerading")

    def is_masquerade_page_opened(self):
        try:
            current_url = self.get_page_report()["CURRENT_URL"]
            return "/masquerade" in current_url
        except Exception as e:
            print("Error checking if Masquerade page is opened:", e)
            traceback.print_exc()
            return False

    def check_masquerade_username_field(self, expected_username):
        try:
            username_element = self.find_element(self.MASQUERADE_PAGE_USERNAME_ELEMENT, timeout=10)
            actual_username = username_element.get_attribute("value").strip()
            print(f"Masquerade page username field value: '{actual_username}' (expected: '{expected_username}')")
            return actual_username.lower() == expected_username.lower()
        except Exception as e:
            print("Error checking masquerade username field:", e)
            traceback.print_exc()
            return False

    def enter_reason_for_masquerade(self, reason_text):
        self.enter_text(self.MASQUERADE_PAGE_REASON, reason_text, timeout=10)

    def enter_signature_for_masquerade(self, signature_text):
        self.enter_text(self.MASQUERADE_PAGE_SIGNATURE, signature_text, timeout=10)

    def submit_masquerade(self):
        self.click_element(self.MASQUERADE_PAGE_SUBMIT_BUTTON, timeout=10, desc="Click submit button on masquerade page")
        self.ajax_preloader_wait()







