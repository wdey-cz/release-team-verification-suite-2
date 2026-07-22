import time
import traceback
import os
from random import choice

from core.driver_factory import WebDriverFactory
from pages.cozeva_login_page import CozevaLoginPage
from core.config import Config
from multiprocessing import Pool
from config.rtvsdb import RTVSDB

from pages.cozeva_mfa_page import CozevaMFAPage
from pages.cozeva_patient_dashboard_page import CozevaPatientDashboardPage
from pages.cozeva_reason_for_login_page import CozevaReasonForLoginPage
from core.base_page import HeaderNavBar
from pages.cozeva_users_page import CozevaUsersPage
from pages.cozeva_payment_tool_page import CozevaPaymentToolPage
from pages.cozeva_providers_page import CozevaProvidersPage
from pages.cozeva_analytics_page import AnalyticsLandingPage,AnalyticsWorksheetPage
from pages.cozeva_registries_page import CozevaRegistriesPage
from pages.cozeva_mspl_page import CozevaMSPLPage


def login_splash_test():
    print("Initializing WebDriver...")
    driver, profile = WebDriverFactory.get_driver(use_chrome_profile=True, download_directory=Config.RTVS_DOWNLOADS_DIR, lane_id='1')
    db = RTVSDB()
    user_role, user_name = "CS", "wdey.cs"
    #user_role, user_name = "Office Admin Practice Delegate", "AltaMed_Abigail"
    #user_role, user_name = "Provider", "altamed_kprice"
    try:
        login_page = CozevaLoginPage(driver)
        print("Navigating to login page...")
        login_page.go_to_login_page("https://www.cozeva.com")
        print("Performing login...")
        username = os.environ.get("CS2_RTVS_User")
        password = os.environ.get("CS2_RTVS_Password")
        if not username or not password:
            raise RuntimeError("CS2_RTVS_User / CS2_RTVS_Password environment variables are not set.")
        login_page.enter_credentials_and_login(username, password)
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
                users_page.masquerade_as_user(user_name, signature="Sarvada Srivastava",
                                          reason="Testing Masquerade functionality from RTVS2")

            except Exception as e:
                traceback.print_exc()
                print("Exception occurred while searching for user:", str(e))

            if users_page.is_eula_page_opened():
                print("EULA page detected after masquerade. Attempting to skip EULA...")
                users_page.skip_eula()

        # Sidebar options. collect all sidebar options, then loop through them, get back to base registries and repeat.
        start_url = header_nav.get_page_report()["CURRENT_URL"]

        #to test analytics worksheet
        # starting_page="https://www.cozeva.com/analytics/tab/a0e20053d20c690d51708b1a2354bf7135ba3c9b?session=YXBwX2lkPWFuYWx5dGljcyZjdXN0SWQ9MTUwMCZwYXllcklkPTE1MDAmb3JnSWQ9MTUwMCZ2Z3BJZD0xNTAwJnZwSWQ9MTUwMA%3D%3D&display_type=single_chart"
        # header_nav.navigate_to_url(starting_page)
        # analytics_page=AnalyticsWorksheetPage(driver)
        # analytics_page.get_selected_service_year()
        # time.sleep(5)
        # analytics_page.apply_filter()

        # to test analytics landing page
        url="https://www.cozeva.com/analytics?session=YXBwX2lkPWFuYWx5dGljcyZjdXN0SWQ9MTMwMCZwYXllcklkPTEzMDAmb3JnSWQ9MTMwMCZ2Z3BJZD0xMzAwJnZwSWQ9MTMwMA"
        header_nav.navigate_to_url(url)
        analytics_page = AnalyticsLandingPage(driver)
        if analytics_page.is_loading_over() :
            print("Analytics page loaded")
            recenlty_used_section_display_status=analytics_page.is_recently_used_displayed()
            print("Recently used section displayed:", recenlty_used_section_display_status)
            worksheets_found=analytics_page.get_number_of_worksheets()
            print("Worksheets found:", worksheets_found)



        #providers_list_page = CozevaProvidersPage(driver)
        # if providers_list_page.is_providers_page_open():
        #     print("Providers page is open. Fetching practice names...")
        #     practice_names = providers_list_page.fetch_practice_names()
        #     print("Practice names fetched:", practice_names)
        #     print("Now fetching provider names...")
        #     provider_names = providers_list_page.fetch_provider_names()
        #     print("Provider names fetched:", provider_names)
        #     url = header_nav.get_page_report()["CURRENT_URL"]
        #     r_practice = choice(practice_names)
        #     r_provider = choice(provider_names)
        #     print(f"Now clicking on random Practice {r_practice}")
        #     providers_list_page.click_practice_by_name(r_practice)
        #     header_nav.navigate_to_url(url)
        #     print(f"Now clicking on random Provider {r_provider}")
        #     providers_list_page.click_provider_by_name(r_provider)
        # else:
        #     print("Providers page did not open successfully. Current URL:", driver.current_url)
        registries_page = CozevaRegistriesPage(driver)
        """
        format of scores - 
        {
                'Measure_name 1': {'METRIC_ID': a, 'DOMAIN_NAME': b, 'NUMERATOR': d,'DENOMINATOR': e},
                'Measure_name 2': {'METRIC_ID': a, 'DOMAIN_NAME': b, 'NUMERATOR': d,'DENOMINATOR': e},
                ...
        }
        Need to pick a random metric ID from score list 
        """


        pat_dash = CozevaPatientDashboardPage(driver)
        pat_dash.navigate_to_url("https://www.cozeva.com/patient_detail/3ES838F?session=YXBwX2lkPXJlZ2lzdHJpZXMmcGF5ZXJJZD0xNTAwJmN1c3RJZD0xNTAwJnZncElkPTE1MDAmdnBJZD0xNTAwJnZnMElkPTE1MDAmb3JnSWQ9MTUwMCZwVWlkPTExNTM3OA%3D%3D&cozeva_id=3ES838F&patient_id=129614771&tab_type=CareOps&first_load=1")
        pat_dash.ajax_preloader_wait("Loading patient dashboard")
        #print(pat_dash.perform_pcp_checks())

        # Next demographic
        #print(pat_dash.fetch_gaps())
        #print(pat_dash.perform_pcp_checks())
        dropdown_names = pat_dash.fetch_history_dropdown_names()
        pat_dash.sleep_code(4)
        for dropdown in dropdown_names:
            print(f"Interacting with dropdown: {dropdown}")
            pat_dash.click_history_dropdown_option(dropdown)
            pat_dash.sleep_code(4)




















    except Exception as e:
        print(f"Error : {e}")
        traceback.print_exc()
    finally:
        driver.quit()
        WebDriverFactory.release_driver_from_profile(browser_name="chrome", profile_name=profile)

if __name__ == "__main__":
    login_splash_test()

