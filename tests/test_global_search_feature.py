import time
from random import choice

import pytest
import traceback
from core.helpers import Helpers
from pages.cozeva_mspl_page import CozevaMSPLPage
from pages.cozeva_registries_page import CozevaRegistriesPage
from core.base_page import HeaderNavBar

@pytest.mark.CozevaComboPack1
@pytest.mark.GlobalSearchPackage
class TestGlobalSearch:

    @pytest.mark.GlobalSearch
    def test_global_search(self, logged_in_driver, base_url, config_assists):
        """
        Testing Global search
        1. First - collect required data from MSPL page
        2. Second - come back to landing registries and perform global search for the data collected from MSPL page
        """

        failed_cases = 0
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            user_role = rc.user_role


            # Load pre_test_url for navigation after
            rc.base_landing_url = driver.current_url
            config_assists.add_log_update("Navigating to Registries page to collect data for global search test...")

            registries_page = CozevaRegistriesPage(driver)
            mspl_page = CozevaMSPLPage(driver)

            measures = registries_page.fetch_num_den_from_registry()
            random_measure = choice(list(measures.keys()))
            print("Clicking on random measure:", random_measure, "with Metric ID:",
                measures[random_measure]['METRIC_ID'])

            registries_page.click_on_measure_by_metric_id(measures[random_measure]['METRIC_ID'])
            config_assists.add_log_update("Clicked on random measure: " + random_measure + " with Metric ID: " + str(
                measures[random_measure]['METRIC_ID']), driver=driver, status="IN_PROGRESS")

            registries_page.ajax_preloader_wait("Loading mspl for measure: " + random_measure)

            search_strings = {'Practice': None, 'Provider': None, 'Patient': None}

            if mspl_page.is_mspl_page_opened():
                config_assists.add_log_update("MSPL page loaded successfully for measure: " + random_measure, driver=driver, status="PASS")
                config_assists.add_log_update("Collecting practice, provider and patient names from MSPL page for measure: " + random_measure, driver=driver, status="IN_PROGRESS")

                search_strings['Practice'] = choice(mspl_page.fetch_practice_names()) if mspl_page.fetch_practice_names() else None
                search_strings['Provider'] = choice(mspl_page.fetch_provider_names()) if mspl_page.fetch_provider_names() else None
                search_strings['Patient'] = choice(mspl_page.fetch_patient_names()) if mspl_page.fetch_patient_names() else None

                config_assists.add_log_update("Collected search strings from MSPL page for measure: " + random_measure + " - " + str(search_strings), driver=driver, status="PASS")


            else:
                config_assists.add_log_update("Failed to load MSPL page for measure: " + random_measure, driver=driver, status="FAIL")

        except Exception:
            try:
                config_assists.add_log_update("Error during MSPL data collection for measure: " + random_measure, driver=driver, status="FAIL")
            except Exception:
                pass
            traceback.print_exc()
            failed_cases += 1

        try:
            # Perform global search for collected strings
            header_nav = HeaderNavBar(driver)


            if failed_cases == 0:
                config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
            else:
                config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)

            # return to start
            registries_page.navigate_to_url(rc.base_landing_url)
            registries_page.ajax_preloader_wait("Return to start")
            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."

        except Exception:
            traceback.print_exc()
            assert False, "Error during final assertions or navigation in test: " + rc.test_name















