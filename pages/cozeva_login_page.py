"""
Login Page Test Cases
1. test_login_page_loads: Verify that the Cozeva login page loads successfully.
2. test_login_page_elements: Verify that all necessary elements are present on the login page.
3. test_invalid_login: Verify that an invalid login attempt shows the correct error message.
4. test_valid_login: Verify that a valid login attempt redirects to the dashboard page.
5. test_forgot_password_link: Verify that the "Forgot Password" link navigates to the correct page.
6. test_stay_signed_in_checkbox: Verify that the "Stay Signed In" checkbox functions correctly.

Cozeva Login Page Functions
1. go_to_login_page: Navigate to the Cozeva login page.
2. enter_username: Enter the username into the username field.
3. enter_password: Enter the password into the password field.
4. click_login_button: Click the login button to attempt login.
5. get_error_message: Retrieve the error message displayed after a failed login attempt.
6. click_forgot_password_link: Click the "Forgot Password" link.
7. toggle_stay_signed_in: Toggle the "Stay Signed In" checkbox.
8. is_stay_signed_in_checked: Check if the "Stay Signed In" checkbox is selected.
9. is_main_logo_displayed: Verify if the main logo is displayed on the login page.
10. is_username_field_displayed: Verify if the username input field is displayed.
11. is_password_field_displayed: Verify if the password input field is displayed.
12. is_login_button_displayed: Verify if the login button is displayed.
13. is_forgot_password_link_displayed: Verify if the "Forgot Password" link is displayed.
14. is_stay_signed_in_checkbox_displayed: Verify if the "Stay Signed In" checkbox is displayed.
15. is_banner_displayed: Verify if the banner is displayed on the login page.
16. get_banner_text: Retrieve the text displayed in the banner on the login page.
17. is_footer_developer_link_present: Check if the developer link is present in the footer.
18. is_footer_privacy_policy_link_present: Check if the privacy policy link is present in the footer.
19. is_footer_messaging_guidelines_link_present: Check if the terms of service link is present in the footer.
20. is_footer_copyright_text_present: Check if the copyright text is present in the footer.
21. is_footer_contact_us_link_present: Check if the contact us link is present in the footer.
22. is_footer_follow_us_link_present: Check if the follow us link is present in the footer.
"""
import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By


class CozevaLoginPage(BasePage):

    LOGIN_BASE_URL = "/user/login"
    LOGOUT_BASE_URL = "/user/logout"

    def __init__(self, driver):
        super().__init__(driver)

    def go_to_login_page(self, base_url):
        try:
            self.navigate_to_url(base_url + self.LOGIN_BASE_URL)
        except Exception as e:
            print("Error navigating to Cozeva login page:", e)
            traceback.print_exc()

