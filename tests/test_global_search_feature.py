import time
from random import choice

import pytest
import traceback
from core.helpers import Helpers
from pages.cozeva_mspl_page import CozevaMSPLPage
from pages.cozeva_registries_page import CozevaRegistriesPage
from core.base_page import HeaderNavBar
from pages.cozeva_patient_dashboard_page import CozevaPatientDashboardPage


@pytest.mark.CozevaComboPack1
@pytest.mark.GlobalSearchPackage
class TestGlobalSearch:

    @pytest.mark.GlobalSearch
    def test_global_search(self, logged_in_driver, base_url, config_assists):
        """
        Testing Global search
        F_03_01: Validate collection header for practice search
        F_03_02: Practice Registry Loading after global search
        F_03_03: Validate collection header for provider search
        F_03_04: Provider Registry Loading after global search
        F_03_05: Validate collection header for patient search
        F_03_06: Patient Dashboard Loading after global search
        """

        failed_cases = 0
        search_strings = {'Practice': None, 'Provider': None, 'Patient': None}
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

                # before we pick random, we will removie entries that are less than 3 characters long, as they are not valid for global search.
                practice_names = [name for name in mspl_page.fetch_practice_names() if len(name) >= 3] if mspl_page.fetch_practice_names() else []
                provider_names = [name for name in mspl_page.fetch_provider_names() if len(name) >= 3] if mspl_page.fetch_provider_names() else []
                patient_names = [name for name in mspl_page.fetch_patient_names() if len(name) >= 3] if mspl_page.fetch_patient_names() else []

                search_strings['Practice'] = choice(mspl_page.fetch_practice_names()) if mspl_page.fetch_practice_names() else None
                search_strings['Provider'] = choice(mspl_page.fetch_provider_names()) if mspl_page.fetch_provider_names() else None
                search_strings['Patient'] = choice(mspl_page.fetch_patient_names()) if mspl_page.fetch_patient_names() else None


                config_assists.add_log_update("Collected search strings from MSPL page for measure: " + random_measure + " - " + str(search_strings), driver=driver, status="PASS")
                registries_page.navigate_to_url(rc.base_landing_url)
                registries_page.ajax_preloader_wait("Returning to registries page after collecting search strings for measure: " + random_measure)

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

            # Perform Global search for Practice F_03_01/F_03_02
            if search_strings['Practice']:
                config_assists.add_log_update("Performing global search for Practice: " + search_strings['Practice'], driver=driver, status="IN_PROGRESS")
                config_assists.add_log_heartbeat("starting test case F_03_01: Validate collection header for practice search")
                header_nav.enter_global_search_value(search_strings['Practice'], 'Practice')
                start_time = time.perf_counter()
                collection_header_visible = header_nav.submit_global_search()
                time_taken = f"{time.perf_counter() - start_time:.2f}"
                header_nav.ajax_preloader_wait("Global search for Practice: " + search_strings['Practice'])

                if collection_header_visible:
                    config_assists.add_log_test_case(
                        message=f"Global search for Practice: {search_strings['Practice']} - Collection header is visible.",
                        test_case_id="F_03_01",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Practice: " + search_strings['Practice'],
                    )
                else:
                    config_assists.add_log_test_case(
                        message=f"Global search for Practice: {search_strings['Practice']} - Collection header is visible.",
                        test_case_id="F_03_01",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Practice: " + search_strings['Practice'],
                    )
                    failed_cases += 1

                config_assists.add_log_heartbeat("Finished test case F_03_01: Validate collection header for practice search")

                config_assists.add_log_heartbeat("starting test case F_03_02: Practice Registry Loading after global search")

                # now we will click on the practice result and validate.
                client_name = config_assists.db.get_customer_name_from_id(rc.client_id)
                header_nav.click_global_search_result("Practice", client_name)

                # Switch to the new tab opened after clicking on the practice result
                start_time = time.perf_counter()
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Global search for Practice: " + search_strings['Practice'])
                time_taken = f"{time.perf_counter() - start_time:.2f}"

                load_post_click = registries_page.is_registries_page_opened()

                if load_post_click:
                    config_assists.add_log_test_case(
                        message=f"Global search for Practice: {search_strings['Practice']} - Navigated to practice page successfully.",
                        test_case_id="F_03_02",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Practice: " + search_strings['Practice'],
                    )
                else:
                    config_assists.add_log_test_case(
                        message=f"Global search for Practice: {search_strings['Practice']} - Navigated to practice page successfully.",
                        test_case_id="F_03_02",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Practice: " + search_strings['Practice'],
                    )
                    failed_cases += 1

                header_nav.switch_tab_and_close_current(0)  # Switch back to the original tab and close the new one

                #reset
                config_assists.add_log_heartbeat("finished test case F_03_02: Practice Registry Loading after global search")
                header_nav.navigate_to_url(rc.base_landing_url)
                header_nav.ajax_preloader_wait("returning to registries page after practice search test case")
                config_assists.add_log_heartbeat("Reloading registries page after practice search test case")

            # Test case F_03_03 and F_03_04 for Provider search
            if search_strings['Provider']:
                config_assists.add_log_update("Performing global search for Provider: " + search_strings['Provider'], driver=driver, status="IN_PROGRESS")
                config_assists.add_log_heartbeat("starting test case F_03_03: Validate collection header for provider search")
                header_nav.enter_global_search_value(search_strings['Provider'], 'Provider')
                start_time = time.perf_counter()
                collection_header_visible = header_nav.submit_global_search()
                time_taken = f"{time.perf_counter() - start_time:.2f}"
                header_nav.ajax_preloader_wait("Global search for Provider: " + search_strings['Provider'])

                if collection_header_visible:
                    config_assists.add_log_test_case(
                        message=f"Global search for Provider: {search_strings['Provider']} - Collection header is visible.",
                        test_case_id="F_03_03",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Provider: " + search_strings['Provider'],
                    )
                else:
                    config_assists.add_log_test_case(
                        message=f"Global search for Provider: {search_strings['Provider']} - Collection header is visible.",
                        test_case_id="F_03_03",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Provider: " + search_strings['Provider'],
                    )
                    failed_cases += 1

                config_assists.add_log_heartbeat("finished test case F_03_03: Provider collection header is visible")

                config_assists.add_log_heartbeat("starting test case F_03_04: Provider Registry Loading after global search")
                # now we will click on the provider result and validate.
                client_name = config_assists.db.get_customer_name_from_id(rc.client_id)
                header_nav.click_global_search_result("Provider", client_name)

                # Switch to the new tab opened after clicking on the provider result
                start_time = time.perf_counter()
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Global search for Provider: " + search_strings['Provider'])
                time_taken = f"{time.perf_counter() - start_time:.2f}"

                load_post_click = registries_page.is_registries_page_opened()

                if load_post_click:
                    config_assists.add_log_test_case(
                        message=f"Global search for Provider: {search_strings['Provider']} - Navigated to provider page successfully.",
                        test_case_id="F_03_04",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Provider: " + search_strings['Provider'],
                    )
                else:
                    config_assists.add_log_test_case(
                        message=f"Global search for Provider: {search_strings['Provider']} - Navigated to provider page successfully.",
                        test_case_id="F_03_04",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Provider: " + search_strings['Provider'],
                    )
                    failed_cases += 1

                header_nav.switch_tab_and_close_current(0)  # Switch back to the original tab and close the new one
                #reset
                config_assists.add_log_heartbeat("finished test case F_03_04: Provider Registry Loading after global search")
                header_nav.navigate_to_url(rc.base_landing_url)
                header_nav.ajax_preloader_wait("returning to registries page after provider search test case")
                config_assists.add_log_heartbeat("Reloading registries page after provider search test case")

            # Test case F_03_05 and F_03_06 for Patient search
            if search_strings['Patient']:
                config_assists.add_log_update("Performing global search for Patient: " + search_strings['Patient'], driver=driver, status="IN_PROGRESS")
                config_assists.add_log_heartbeat("starting test case F_03_05: Validate collection header for patient search")
                header_nav.enter_global_search_value(search_strings['Patient'], 'Patient')
                start_time = time.perf_counter()
                collection_header_visible = header_nav.submit_global_search()
                time_taken = f"{time.perf_counter() - start_time:.2f}"
                header_nav.ajax_preloader_wait("Global search for Patient: " + search_strings['Patient'])

                if collection_header_visible:
                    config_assists.add_log_test_case(
                        message=f"Global search for Patient: {search_strings['Patient']} - Collection header is visible.",
                        test_case_id="F_03_05",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Patient: " + search_strings['Patient'],
                    )
                else:
                    config_assists.add_log_test_case(
                        message=f"Global search for Patient: {search_strings['Patient']} - Collection header is visible.",
                        test_case_id="F_03_05",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Patient: " + search_strings['Patient'],
                    )
                    failed_cases += 1

                config_assists.add_log_heartbeat("finished test case F_03_05: Patient collection header is visible")

                config_assists.add_log_heartbeat("starting test case F_03_06: Patient Dashboard Loading after global search")
                # now we will click on the patient result and validate.
                client_name = config_assists.db.get_customer_name_from_id(rc.client_id)
                header_nav.click_global_search_result("Patient", client_name)

                # Switch to the new tab opened after clicking on the patient result
                start_time = time.perf_counter()
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Global search for Patient: " + search_strings['Patient'])
                time_taken = f"{time.perf_counter() - start_time:.2f}"
                
                pat_dash = CozevaPatientDashboardPage(driver)
                success_pat_dashboard = pat_dash.is_patient_dashboard_opened()

                if success_pat_dashboard:
                    config_assists.add_log_test_case(
                        message=f"Global search for Patient: {search_strings['Patient']} - Navigated to patient page successfully.",
                        test_case_id="F_03_06",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Patient: " + search_strings['Patient'],
                    )
                else:
                    config_assists.add_log_test_case(
                        message=f"Global search for Patient: {search_strings['Patient']} - Navigated to patient page successfully.",
                        test_case_id="F_03_06",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Global search for Patient: " + search_strings['Patient'],
                    )
                    failed_cases += 1

                header_nav.switch_tab_and_close_current(0)  # Switch back to the original tab and close the new one
                # reset
                config_assists.add_log_heartbeat("finished test case F_03_06: Patient Dashboard Loading after global search")
                header_nav.navigate_to_url(rc.base_landing_url)
                header_nav.ajax_preloader_wait("returning to registries page after patient search test case")



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















