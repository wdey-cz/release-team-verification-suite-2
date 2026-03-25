import time
import traceback
from random import choice

from core.driver_factory import WebDriverFactory
from pages.cozeva_login_page import CozevaLoginPage
from core.config import Config
from multiprocessing import Pool
from config.rtvsdb import RTVSDB

from pages.cozeva_mfa_page import CozevaMFAPage
from pages.cozeva_reason_for_login_page import CozevaReasonForLoginPage
from core.base_page import HeaderNavBar
from pages.cozeva_users_page import CozevaUsersPage
from pages.cozeva_payment_tool_page import CozevaPaymentToolPage
from pages.cozeva_providers_page import CozevaProvidersPage
from pages.cozeva_registries_page import CozevaRegistriesPage


def login_splash_test():
    print("Initializing WebDriver...")
    driver, profile = WebDriverFactory.get_driver(use_chrome_profile=True, download_directory=Config.RTVS_DOWNLOADS_DIR, lane_id='1')
    db = RTVSDB()
    user_role, user_name = "CS", "wdey.cs"
    #user_role, user_name = "CU", "AltaMed_AlUtria"
    try:
        login_page = CozevaLoginPage(driver)
        print("Navigating to login page...")
        login_page.go_to_login_page("https://www.cozeva.com")
        print("Performing login...")
        creds = db.fetch_tester_credentials()
        login_page.enter_credentials_and_login(creds[0], creds[1])
        print("Login Complete. Waiting for 5 seconds...")
        login_page.sleep_code(5)

        # check if we were sent to the MFA page
        mfa_page = CozevaMFAPage(driver)
        if mfa_page.is_mfa_page_opened():
            mfa_page.wait_for_user_mfa_and_navigation(timeout=180)

        reason_page = CozevaReasonForLoginPage(driver)
        if reason_page.is_reason_page_opened():
            reason_page.enter_reason_select_customer_and_submit(client_id="1500")
            reason_page.ajax_preloader_wait()

        print("We should be logged in now. Current URL:", driver.current_url)

        # Now lets code Masqurade after login is user_role is not Cozeva Support
        header_nav = HeaderNavBar(driver)
        if user_role != "CS":
            print("Starting Masquerade process...")
            header_nav.click_user_dropdown_option("Users")
            print("Masquerade started... Reached users page")
            print("Now Switching POM to users page to continue Masquerade")
            # Here you would continue with the Masquerade process using the UsersPage POM
            print("Selected user to masquerade:", user_name)
            mfa_page.sleep_code(3)

            users_page = CozevaUsersPage(driver)
            try:
                users_page.filter_search_field(user_name)
                print("Done filtering for user. Now attempting to masquerade as user:", user_name)
                users_page.masquerade_as_user(user_name, signature="Writtwik Dey",
                                          reason="Testing Masquerade functionality from RTVS2")

            except Exception as e:
                traceback.print_exc()
                print("Exception occurred while searching for user:", str(e))

            if users_page.is_eula_page_opened():
                print("EULA page detected after masquerade. Attempting to skip EULA...")
                users_page.skip_eula()

        # Sidebar options. collect all sidebar options, then loop through them, get back to base registries and repeat.
        start_url = header_nav.get_page_report()["CURRENT_URL"]

        registries_page = CozevaRegistriesPage(driver)
        registries_page.is_registries_page_opened()
        if registries_page.is_registries_page_opened():
            my_lob_dict, default_dict = registries_page.fetch_my_and_lob()

        else:
            print("Registries page did not open successfully. Current URL:", driver.current_url)

        for lob in my_lob_dict['LOB']:
            registries_page.switch_lob(lob)
            registries_page.sleep_code(5)

    except Exception as e:
        print(f"Error : {e}")
        traceback.print_exc()
    finally:
        driver.quit()
        WebDriverFactory.release_driver_from_profile(browser_name="chrome", profile_name=profile)

if __name__ == "__main__":
    login_splash_test()

