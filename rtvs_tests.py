import time
import traceback
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
        # pat_dash.navigate_to_url("https://www.cozeva.com/registries/219?session=YXBwX2lkPXJlZ2lzdHJpZXMmY3VzdElkPTE1MDAmcGF5ZXJJZD0xNTAwJm9yZ0lkPTE1MDAmdmdwSWQ9MTUwMCZ2cElkPTE1MDA&orgId=1500&plan_type=ALL&quarter=2026-12-31&payerId=1500&perf_stats_enabled=1&utl=0&is_cost=0&dashboard_metric_category=0&cont_discont_flag=0&table_id=metric-support-prov-ls#qt-sp-prov-ls")
        # pat_dash.ajax_preloader_wait("loading mspl")

        mspl = CozevaMSPLPage(driver)

        measures = registries_page.fetch_num_den_from_registry()
        random_measure = choice(list(measures.keys()))
        print("Clicking on random measure:", random_measure, "with Metric ID:",
              measures[random_measure]['METRIC_ID'])

        registries_page.click_on_measure_by_metric_id(measures[random_measure]['METRIC_ID'])


        registries_page.ajax_preloader_wait("Loading mspl for measure: " + random_measure)
        #print(pat_dash.perform_pcp_checks())

        # Next demographic
        #print(pat_dash.fetch_gaps())
        #print(pat_dash.perform_pcp_checks())
        # dropdown_names = pat_dash.fetch_history_dropdown_names()
        # pat_dash.sleep_code(4)
        # for dropdown in dropdown_names:
        #     print(f"Interacting with dropdown: {dropdown}")
        #     pat_dash.click_history_dropdown_option(dropdown)
        #     pat_dash.sleep_code(4)

        # print(pat_dash.fetch_coverage_info())
        search_strings = {'Practice': None, 'Provider': None, 'Patient': None}
        if mspl.is_mspl_page_opened():


            search_strings['Practice'] = choice(
                mspl.fetch_practice_names()) if mspl.fetch_practice_names() else None
            search_strings['Provider'] = choice(
                mspl.fetch_provider_names()) if mspl.fetch_provider_names() else None
            search_strings['Patient'] = choice(
                mspl.fetch_patient_names()) if mspl.fetch_patient_names() else None

            print("SEARCHING STRINGS COLLECTED FROM MSPL PAGE:", search_strings)

            header_nav.enter_global_search_value(search_strings['Practice'], 'Practice')
            collection_header_visible = header_nav.submit_global_search()
            header_nav.click_global_search_result("Practice", "Altamed")

            header_nav.switch_tab(1)
            header_nav.sleep_code(5)
            header_nav.switch_tab_and_close_current(0)
            header_nav.navigate_to_url(start_url)

            header_nav.enter_global_search_value(search_strings['Provider'], 'Provider')
            collection_header_visible = header_nav.submit_global_search()
            header_nav.click_global_search_result("Provider", "Altamed")

            header_nav.switch_tab(1)
            header_nav.sleep_code(5)
            header_nav.switch_tab_and_close_current(0)
            header_nav.navigate_to_url(start_url)

            header_nav.enter_global_search_value(search_strings['Patient'], 'Patient')
            collection_header_visible = header_nav.submit_global_search()
            header_nav.click_global_search_result("Patient", "Altamed")

            header_nav.switch_tab(1)
            header_nav.sleep_code(5)
            header_nav.switch_tab_and_close_current(0)
            header_nav.navigate_to_url(start_url)



        pat_dash.sleep_code(50)
























    except Exception as e:
        print(f"Error : {e}")
        traceback.print_exc()
    finally:
        driver.quit()
        WebDriverFactory.release_driver_from_profile(browser_name="chrome", profile_name=profile)

if __name__ == "__main__":
    login_splash_test()

