import time
import traceback
import os

from core.driver_factory import WebDriverFactory
from core.config import Config
from config.rtvsdb import RTVSDB
from config.config_assists import ConfigAssists

from pages.cozeva_mfa_page import CozevaMFAPage
from pages.cozeva_login_page import CozevaLoginPage
from pages.cozeva_reason_for_login_page import CozevaReasonForLoginPage

def CONFIGURE_MFA(profile):
    """
    Configure MFA settings for the application.
    This function can be expanded to include specific MFA configuration steps.
    """
    driver = None
    try:
        print("Initializing WebDriver...")
        driver, profile = WebDriverFactory.get_driver(use_chrome_profile=True,
                                                      download_directory=Config.RTVS_DOWNLOADS_DIR, selected_chrome_profile=profile, lane_id='1')
        db = RTVSDB()
        login_page = CozevaLoginPage(driver)
        print("Navigating to login page...")
        login_page.go_to_login_page("https://www.cozeva.com")
        driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
        driver.delete_all_cookies()
        login_page.sleep_code(2)
        print("Performing login...")
        username = os.environ.get("CS2_RTVS_User")
        password = os.environ.get("CS2_RTVS_Password")
        if not username or not password:
            raise RuntimeError("CS2_RTVS_User / CS2_RTVS_Password environment variables are not set.")
        login_page.enter_credentials_and_login(username, password)
        print("Login Complete. Waiting for 5 seconds...")
        login_page.sleep_code(5)

        # check if we were sent to the MFA page
        is_mfa_page_opened = False
        mfa_page = CozevaMFAPage(driver)
        if mfa_page.is_mfa_page_opened():
            is_mfa_page_opened = True
            mfa_page.wait_for_user_mfa_and_navigation(timeout=180)
            db.edit_chrome_profile_table(change_type='UPDATE_MFA_TIME', profile_name=profile)


        reason_page = CozevaReasonForLoginPage(driver)
        if reason_page.is_reason_page_opened():
            reason_page.enter_reason_select_customer_and_submit(client_id="1500")
            reason_page.ajax_preloader_wait()


        print("We should be logged in now. Current URL:", driver.current_url)

    except Exception as e:
        print("Error during MFA configuration:", e)
        traceback.print_exc()

    finally:
        if driver is not None:
            driver.quit()
