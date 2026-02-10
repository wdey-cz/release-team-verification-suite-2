import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

class CozevaMFAPage(BasePage):

    MFA_PAGE_URL = "/twostepAuthSettings"
    # locators
    MFA_CODE_INPUT = (By.ID, "edit-twostep-code")
    MFA_VERIFY_BUTTON = (By.ID, "edit-twostep")
    MFA_RESEND_BUTTON = (By.ID, "edit-twostep-resend-code")

    def __init__(self, driver):
        super().__init__(driver)

    def is_mfa_page_opened(self):
        try:
            current_url = self.get_page_report()["CURRENT_URL"]
            return self.MFA_PAGE_URL in current_url
        except Exception as e:
            print("Error checking if MFA page is opened:", e)
            traceback.print_exc()
            return False

    def wait_for_user_mfa_and_navigation(self, timeout: int = 180, next_page_locator=None):
        """
        Wait until user enters MFA and clicks Verify, and navigation begins.
        Optionally wait for a locator on the next page.
        """
        print("Please enter the 6-digit MFA code in the browser, then click Verify.")

        start_url = self.driver.current_url

        # Grab a "sentinel" element from the MFA page.
        # If the page navigates, this element often becomes stale.
        verify_btn = self.find_element(self.MFA_VERIFY_BUTTON, timeout=10)

        def _navigation_started(driver):
            # 1) URL changed away from MFA page
            try:
                cur = driver.current_url
                if (cur != start_url) and (self.MFA_PAGE_URL not in cur):
                    return True
            except Exception:
                pass

            # 2) MFA page element went stale (hard navigation)
            try:
                _ = verify_btn.is_enabled()
            except StaleElementReferenceException:
                return True

            return False

        try:
            WebDriverWait(self.driver, timeout, poll_frequency=0.25).until(_navigation_started)
        except TimeoutException:
            # Useful debug when user didn't click verify or MFA failed and stayed on same page
            raise TimeoutException(
                f"MFA did not complete within {timeout}s. "
                f"Still on URL: {self.driver.current_url}"
            )

        # If you know something that must exist on the next page, wait for it
        if next_page_locator is not None:
            self.wait_helpers.wait_for_element_present(next_page_locator, timeout=30)

        # Optional: wait for DOM ready if you do full page loads (safe even if SPA)
        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass

        self.sleep_code(5)  # Allow any post-login redirects or modals to appear

        return True




