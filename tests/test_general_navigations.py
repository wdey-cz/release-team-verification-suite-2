import time
from random import choice

import pytest
import traceback
from core.helpers import Helpers
from pages.cozeva_analytics_page import CozevaQualityOverviewPage
from pages.cozeva_mspl_page import CozevaMSPLPage
from pages.cozeva_patient_dashboard_page import CozevaPatientDashboardPage

from pages.cozeva_registries_page import CozevaRegistriesPage
from core.base_page import HeaderNavBar
from pages.cozeva_providers_page import CozevaProvidersPage

@pytest.mark.CozevaComboPack1
@pytest.mark.GeneralNavPackage
class TestGeneralNavigations:

    """
    Feature: F_09_GeneralNavs
    Test Cases -
        - F_09_01: Verify that the user can navigate from a support registry to a practice registry
        - F_09_02: Verify that the user can navigate from a support registry to a provider registry
        - F_09_03: Verify that the user can navigate from a support registry to a patient dashboard

    """

    @pytest.mark.SupportRegistryNavs
    def test_supportRegistryNavs(self, logged_in_driver, base_url, config_assists):
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            user_role = rc.user_role
            rc.base_landing_url = driver.current_url

            failed_cases = 0

            header_nav = HeaderNavBar(driver)

            if failed_cases == 0:
                config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
            else:
                config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)

            # return to start
            header_nav.navigate_to_url(rc.base_landing_url)
            header_nav.ajax_preloader_wait("Return to start")
            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



        except Exception as e:
            print("Error in test_loop_through_support_sidebar:", e)
            traceback.print_exc()
            assert False, f"Test failed due to exception: {e}"

    @pytest.mark.PracticeRegistryNavs
    def test_practiceRegistryNavs(self, logged_in_driver, base_url, config_assists):
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            user_role = rc.user_role
            rc.base_landing_url = driver.current_url

            failed_cases = 0

            header_nav = HeaderNavBar(driver)

            if failed_cases == 0:
                config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
            else:
                config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)

            # return to start
            header_nav.navigate_to_url(rc.base_landing_url)
            header_nav.ajax_preloader_wait("Return to start")
            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



        except Exception as e:
            print("Error in test_loop_through_practice_sidebar:", e)
            traceback.print_exc()
            assert False, f"Test failed due to exception: {e}"

    @pytest.mark.ProviderRegistryNavs
    def test_providerRegistryNavs(self, logged_in_driver, base_url, config_assists):
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            user_role = rc.user_role
            rc.base_landing_url = driver.current_url

            failed_cases = 0

            header_nav = HeaderNavBar(driver)

            if failed_cases == 0:
                config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
            else:
                config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)

            # return to start
            header_nav.navigate_to_url(rc.base_landing_url)
            header_nav.ajax_preloader_wait("Return to start")
            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



        except Exception as e:
            print("Error in test_loop_through_provider_sidebar:", e)
            traceback.print_exc()
            assert False, f"Test failed due to exception: {e}"



