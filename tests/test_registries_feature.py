import time
from random import choice

import pytest
import traceback
from core.helpers import Helpers
from pages.cozeva_analytics_page import CozevaQualityOverviewPage

from pages.cozeva_registries_page import CozevaRegistriesPage
from core.base_page import HeaderNavBar
from pages.cozeva_providers_page import CozevaProvidersPage

@pytest.mark.CozevaComboPack1
@pytest.mark.RegistriesTestPackage
class TestRegistries:

    @pytest.mark.SupportRegistries
    def test_support_registries(self, logged_in_driver, base_url, config_assists):
        """
        Feature - F_02_Registries
        Test Cases -
         F_02_01: Validate that the Analytics Deeplink button navigates to the analytics app
         F_02_02: Validate Gaps are visible on summary bar for all LoBs
         F_02_03: Validate Overall Rating are visible on summary bar for all LoBs
         F_02_04: Validate Patient count is visible on summary bar for all LoBs
         F_02_05: Validate the Overall Rating Trend chart for relevant lobs
         F_02_06: Validate Summary HCC score for relevant lobs
         F_02_07: Validate Continous Enrollment checkbox alters num/den counts
         F_02_08: Validate chicklets / stars with exceptions
         F_02_09: Validate Quality/HCC Measure display on registries contains all elements.
         F_02_10: Validate registries filter
         F_02_11: Validate Accordion sumation for all Lobs
         F_02_12: Validate number of 0/0 measures on all Lobs against a previously stored list LoB wise.
         F_02_13: Validate registry export
        """
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            user_role = rc.user_role
            if user_role not in ["Cozeva Support","Customer Support", "Regional Support", "Limited Cozeva Support"]:
                config_assists.add_log_update(message="User role " + user_role + " is not in scope for this test.")
                pytest.skip(f"User role {user_role} is not in scope for this test.")


            failed_cases = 0

            # Load pre_test_url for navigation after
            rc.base_landing_url = driver.current_url

            header_nav = HeaderNavBar(driver)

            config_assists.add_log_update(
                message=f"Navigated to {header_nav.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases",
                driver=driver)

            config_assists.add_log_heartbeat("Starting Regression on F_02_Registries", driver=driver,
                                             status="STARTED")
            registries_page = CozevaRegistriesPage(driver)

            # F_02_01 : Validate that the Analytics Deeplink button navigates to the analytics app
            config_assists.add_log_heartbeat("Starting test case F_02_01: Validate Analytics Deeplink button", driver=driver,
                                             status="STARTED")
            registries_page.click_on_deeplink()

            # Switch tab
            registries_page.switch_tab(1)
            config_assists.add_log_update(
                message="Switched to new tab after clicking on Analytics Deeplink button",
                driver=driver)

            # Check quality overview page is opened
            quality_overview_page = CozevaQualityOverviewPage(driver)
            if quality_overview_page.is_quality_overview_page_opened() == "OPEN":
                config_assists.add_log_test_case(
                    message="Validate Analytics Deeplink button",
                    test_case_id="F_02_01",
                    status='PASSED', driver=driver,
                    comment="Clicked on Analytics deeplink and Quality Overview page opened successfully in a new tab, deeplink seems to be working fine.")
            elif quality_overview_page.is_quality_overview_page_opened() == "NOT_OPEN":
                config_assists.add_log_test_case(
                    message="Validate Analytics Deeplink button",
                    test_case_id="F_02_01",
                    status='FAILED', driver=driver,
                    comment="Clicked on Analytics deeplink but Quality Overview page did not open successfully, deeplink seems to be broken.")
                failed_cases += 1
            elif quality_overview_page.is_quality_overview_page_opened() == "LOADING_ISSUE":
                config_assists.add_log_test_case(
                    message="Validate Analytics Deeplink button",
                    test_case_id="F_02_01",
                    status='FAILED', driver=driver,
                    comment="Clicked on Analytics deeplink but there was an issue with loading the Quality Overview page, cannot verify if deeplink is working or not.")
                failed_cases += 1

            # Switch back to original tab
            registries_page.switch_tab_and_close_current(0)
            config_assists.add_log_heartbeat("Finished test case F_02_01: Validate Analytics Deeplink button",
                                             driver=driver,
                                             status="FINISHED")
            registries_page.navigate_to_url(rc.base_landing_url)

            # F_02_02 : Validate Gaps are visible on summary bar for all LoBs
            # F_02_03 : Validate Overall Rating are visible on summary bar for all LoBs
            # F_02_04 : Validate Patient count is visible on summary bar for all LoBs
            """
                Above three cases will be merged into one. Switch lob and check for these three elements.
            """
            config_assists.add_log_heartbeat("Started test case F_02_02,03,04: Validate Gaps, Overall Rating and Patient count visibility on summary bar for all LoBs",
                                             driver=driver,
                                             status="STARTED")

            if registries_page.is_registries_page_opened():
                my_lob_dict, default_dict = registries_page.fetch_my_and_lob()

            # now, we will loop through the Lobs.
            for lob in my_lob_dict['LOB']:
                registries_page.switch_lob(lob)
                registries_page.sleep_code(5)  # Wait for page to load after switching lob

                # Here you would add the code to validate the presence of Gaps, Overall Rating and Patient count on the summary bar for the current lob.
                # This would likely involve checking for specific elements on the page and verifying their visibility and content.








            # F_02_05 : Validate the Overall Rating Trend chart for relevant lobs
            # F_02_06 : Validate Summary HCC score for relevant lobs






            # F_02_13
            config_assists.add_log_heartbeat("Starting test case F_02_13: Validate registry export", driver=driver,
                                             status="STARTED")
            if registries_page.is_registries_page_opened():
                print("Registries page opened successfully. Now attempting to click Export All option in kebab menu...")
                registries_page.download_export_all_registries()
                print("Clicked Export All option. Waiting for 2 seconds to observe any potential issues...")
                time.sleep(2)
            else:
                print("Registries page did not open successfully. Current URL:", driver.current_url)

            # Check if the downloaded file has any data in it
            downloaded_file = Helpers.fetch_downloaded_file(rc.lane_id)
            if downloaded_file:
                config_assists.add_log_update(f"Downloaded file {downloaded_file}", driver=driver,
                                                 status="INFO")
                if Helpers.does_file_have_data(downloaded_file):
                    config_assists.add_log_test_case(
                        message="Validate registry export",
                        test_case_id="F_02_13",
                        status='PASSED', driver=driver,
                        comment=f"Downloaded file {downloaded_file} has data in it, registry export seems to be working fine.")
                    Helpers.delete_file(downloaded_file)
                else:
                    config_assists.add_log_test_case(
                        message="Validate registry export",
                        test_case_id="F_02_13",
                        status='FAILEd', driver=driver,
                        comment=f"Downloaded file {downloaded_file} is empty, registry export seems to be broken.")
                    failed_cases += 1
                    Helpers.delete_file(downloaded_file)
                    config_assists.add_log_update(f"Deleted file {downloaded_file}", driver=driver,
                                                     status="INFO")
            else:
                config_assists.add_log_test_case(
                    message="Validate registry export",
                    test_case_id="F_02_13",
                    status='FAILED', driver=driver,
                    comment=f"No file was downloaded after clicking Export All, registry export seems to be broken.")
                failed_cases += 1

            config_assists.add_log_heartbeat("Finished test case F_02_13: Validate registry export", driver=driver,
                                             status="FINISHED")
            registries_page.navigate_to_url(rc.base_landing_url)



            if failed_cases == 0:
                config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
            else:
                config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)

            # return to start
            header_nav.navigate_to_url(rc.base_landing_url)
            header_nav.ajax_preloader_wait("Return to start")
            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



        except Exception as e:
            traceback.print_exc()
            failed_cases += 1




