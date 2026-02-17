import time
import traceback

from core.driver_factory import WebDriverFactory
from pages.cozeva_login_page import CozevaLoginPage
from core.config import Config
from multiprocessing import Pool

from pages.cozeva_mfa_page import CozevaMFAPage
from pages.cozeva_reason_for_login_page import CozevaReasonForLoginPage
from core.base_page import HeaderNavBar
from pages.cozeva_users_page import CozevaUsersPage


def login_splash_test():
    print("Initializing WebDriver...")
    driver, profile = WebDriverFactory.get_driver(use_chrome_profile=True)
    user_role, user_name = "CS", "wdey.cs"
    #user_role, user_name = "CU", "AltaMed_AlUtria"
    try:
        login_page = CozevaLoginPage(driver)
        print("Navigating to login page...")
        login_page.go_to_login_page("https://www.cozeva.com")
        print("Performing login...")
        login_page.enter_credentials_and_login("xxx", "xxx")
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

        # Sidebar options. collect all sidebar options, then loop through them, get back to base registries and repeat.
        start_url = header_nav.get_page_report()["CURRENT_URL"]

        sidebar_entries = header_nav.fetch_sidebar_entries()

        # Now loop through each sidebar entry, click it, verify page load, then navigate back to start url before clicking the next one
        for entry in sidebar_entries:
            if entry == "Payment Tool" or entry == "Export Dashboard":
                continue
            print(f"Clicking on sidebar entry: {entry}")
            header_nav.click_sidebar_entry(entry)
            start_time = time.perf_counter()
            header_nav.ajax_preloader_wait("After Entry Click Sidebar")
            print(f"Finished waiting for page load after clicking sidebar entry: {entry}. Time taken: {time.perf_counter() - start_time:.2f} seconds")


            current_url = header_nav.get_page_report()["CURRENT_URL"]
            if current_url != start_url:
                print(f"Successfully navigated to new page after clicking sidebar entry: {entry}")
            else:
                print(f"Failed to navigate away from {start_url} after clicking sidebar entry: {entry}")

            print("Navigating back to start URL...")
            driver.get(start_url)
            header_nav.ajax_preloader_wait(desc="Back to start")




    except Exception as e:
        print(f"Error : {e}")
        traceback.print_exc()
    finally:
        driver.quit()
        WebDriverFactory.release_driver_from_profile(browser_name="chrome", profile_name=profile)

if __name__ == "__main__":
    login_splash_test()

