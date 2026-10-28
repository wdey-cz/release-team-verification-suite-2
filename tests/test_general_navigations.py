import time
from random import choice

import pytest
import traceback
from core.helpers import Helpers
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
    -- Support Registry Navigation Test Cases
        - F_09_01: Verify that the user can navigate from a support registry to a practice registry
        -- Click a random metric, Switch to the practices tab, click on a random practice, and verify that the user is navigated to the practice dashboard
        - F_09_02: Verify that the user can navigate from a support registry to a provider registry
        -- Click a random metric, Switch to the providers tab, click on a random provider, and verify that the user is navigated to the provider dashboard
        - F_09_03: Verify that the user can navigate from a support registry to a patient dashboard
        -- Click a random metric, Switch to the patients tab, click on a random patient, and verify that the user is navigated to the patient dashboard
        - F_09_04: Verify that the user can navigate from a support registry to a performance stats page
        - F_09_05: Verify that the user can change Lobs on the support registry page
    -- Practice Registry Navigation Test Cases
        - F_09_06: Verify that the user can navigate from a practice registry to a provider registry
        -- Click a random metric, Switch to the providers tab, click on a random provider, and verify that the user is navigated to the provider dashboard
        - F_09_07: Verify that the user can navigate from a practice registry to a patient dashboard
        -- Click a random metric, Switch to the patients tab, click on a random patient, and verify that the user is navigated to the patient dashboard
        - F_09_08: Verify that the user can navigate from a practice registry to a performance stats page
        - F_09_09: Verify that the user can change Lobs on the practice registry page
    -- Provider Registry Navigation Test Cases
        - F_09_10: Verify that the user can navigate from a provider registry to a patient dashboard
        -- Click a random metric, Switch to the patients tab, click on a random patient, and verify that the user is navigated to the patient dashboard
        - F_09_11: Verify that the user can navigate from a provider registry to a performance stats page
        - F_09_12: Verify that the user can change Lobs on the provider registry page
    """

    @pytest.mark.SupportRegistryNavs
    def test_supportRegistryNavs(self, logged_in_driver, base_url, config_assists):
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            user_role = rc.user_role
            rc.base_landing_url = driver.current_url

            if user_role not in ["Cozeva Support", "Customer Support", "Regional Support", "Limited Cozeva Support"]:
                config_assists.add_log_update(message="User role " + user_role + " is not in scope for this test.")
                pytest.skip(f"User role {user_role} is not in scope for this test.")

            failed_cases = 0

            # Load the header nav page for sidebar navigation functions
            header_nav = HeaderNavBar(driver)
            registries_page = CozevaRegistriesPage(driver)
            mspl_page = CozevaMSPLPage(driver)

            config_assists.add_log_update(
                message=f"Navigated to {header_nav.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases",
                driver=driver)

            # Save the start url to navigate back to after each sidebar click
            start_url = header_nav.get_page_report()["CURRENT_URL"]
            rc.test_page_url = start_url


            # Begin case writing for support registry navigation test cases
            config_assists.add_log_heartbeat("Starting Cases for Support Registry Navigation Test Cases", driver=driver)
            config_assists.add_log_heartbeat("Starting test case F_09_01: Verify that the user can navigate from a support registry to a practice registry",)

            # Test Case F_09_01: Verify that the user can navigate from a support registry to a practice registry.
            # Click a random metric, Switch to the practices tab, click on a random practice, and verify that the user is navigated to the practice dashboard.

            config_assists.add_log_heartbeat(
                "Starting test case F_09_01: Verify that the user can navigate from a support registry to a practice registry",
                driver=driver, )

            # wrote a random metric page object
            random_metric_id, random_measure = registries_page.click_on_random_metric()

            config_assists.add_log_update(
                "Randomly selected measure: " + random_measure + " with metric ID: " + random_metric_id + " for test case F_09_01",
                driver=driver, )

            # Arrived at support level mspl page, Now fetch pratice names.
            practice_names = mspl_page.fetch_practice_names()

            # click a random selected practice
            if practice_names:
                random_practice = choice(practice_names)
                print(f"Randomly selected practice: {random_practice}")
                config_assists.add_log_update("Randomly selected practice: " + random_practice + " for test case F_09_01", driver=driver, )
                mspl_page.click_on_practice_by_name(random_practice)
                start_time = time.perf_counter()
                mspl_page.ajax_preloader_wait("Clicked random practice: " + random_practice)
                time_taken = f"{time.perf_counter() - start_time:.2f}"

                # Verify that the user is navigated to the practice dashboard
                load_status = registries_page.is_registries_page_fully_opened()
                practice_context_name = header_nav.fetch_context_name()
                # write test case, Compare the practice_context_name with the random_practice name, if they match, then we are on the practice dashboard.
                if practice_context_name == random_practice and load_status:
                    print(f"Successfully navigated to the practice dashboard for {random_practice}.")
                    config_assists.add_log_update(
                        "Successfully navigated to the practice dashboard for " + random_practice + " for test case F_09_01",
                        driver=driver, )

                    config_assists.add_log_test_case(
                        message="Verify that the user can navigate from a support registry to a practice registry.",
                        test_case_id="F_09_01",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Clicked a random metric, switched to the practices tab, clicked on a random practice, and verified that the user is navigated to the practice dashboard.",)
                elif not load_status:
                    print(f"Failed to navigate to the practice dashboard for {random_practice}. Current context: {practice_context_name}")
                    config_assists.add_log_update(
                        "Failed to navigate to the practice dashboard for " + random_practice + " for test case F_09_01",
                        driver=driver, )

                    config_assists.add_log_test_case(
                        message="Verify that the user can navigate from a support registry to a practice registry.",
                        test_case_id="F_09_01",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Clicked a random metric, switched to the practices tab, clicked on a random practice, and failed to verify that the user is navigated to the practice dashboard.",)
                    failed_cases += 1

            else:
                print("No practices found to test navigation.")
                config_assists.add_log_update("No practices found to test navigation for test case F_09_01", driver=driver, )
                failed_cases += 1


            # reset
            config_assists.add_log_heartbeat("finished test case F_09_01: Verify that the user can navigate from a support registry to a practice registry", driver=driver, )
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")

            # Test Case F_09_02: Verify that the user can navigate from a support registry to a provider registry.
            # Click a random metric, Switch to the providers tab, click on a random provider, and verify that the user is navigated to the provider dashboard.
            config_assists.add_log_heartbeat("Starting test case F_09_02: Verify that the user can navigate from a support registry to a provider registry", driver=driver, )

            # wrote a random metric page object
            random_metric_id, random_measure = registries_page.click_on_random_metric()

            config_assists.add_log_update(
                "Randomly selected measure: " + random_measure + " with metric ID: " + random_metric_id + " for test case F_09_02",
                driver=driver, )
            config_assists.add_log_update("Randomly selected measure: " + random_measure + " with metric ID: " + random_metric_id + " for test case F_09_02", driver=driver, )



            # Arrived at support level mspl page, Now fetch provider names.
            provider_names = mspl_page.fetch_provider_names()

            # click a random selected provider
            if provider_names:
                random_provider = choice(provider_names)
                print(f"Randomly selected provider: {random_provider}")
                config_assists.add_log_update("Randomly selected provider: " + random_provider + " for test case F_09_02", driver=driver, )
                mspl_page.click_on_provider_by_name(random_provider)
                start_time = time.perf_counter()
                mspl_page.ajax_preloader_wait("Clicked random provider: " + random_provider)
                time_taken = f"{time.perf_counter() - start_time:.2f}"

                # Verify that the user is navigated to the provider dashboard
                load_status = registries_page.is_registries_page_fully_opened()
                provider_context_name = header_nav.fetch_context_name()
                print("Attempting to compare "+provider_context_name+ " with "+random_provider)
                if provider_context_name == random_provider and load_status:
                    print(f"Successfully navigated to the provider dashboard for {random_provider}.")
                    config_assists.add_log_update("Successfully navigated to the provider dashboard for " + random_provider + " for test case F_09_02", driver=driver, )

                    config_assists.add_log_test_case(
                        message="Verify that the user can navigate from a support registry to a provider registry.",
                        test_case_id="F_09_02",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Clicked a random metric, switched to the providers tab, clicked on a random provider, and verified that the user is navigated to the provider dashboard.",)
                elif not load_status:
                    print(f"Failed to navigate to the provider dashboard for {random_provider}. Current context: {provider_context_name}")
                    config_assists.add_log_update("Failed to navigate to the provider dashboard for " + random_provider + " for test case F_09_02", driver=driver, )

                    config_assists.add_log_test_case(
                        message="Verify that the user can navigate from a support registry to a provider registry.",
                        test_case_id="F_09_02",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Clicked a random metric, switched to the providers tab, clicked on a random provider, and failed to verify that the user is navigated to the provider dashboard.",)
                    failed_cases += 1
                elif load_status and provider_context_name != random_provider:
                    print(f"Failed to navigate to the provider dashboard for {random_provider}. Current context: {provider_context_name}")
                    config_assists.add_log_update("Failed to navigate to the provider dashboard for " + random_provider + " for test case F_09_02", driver=driver, )

                    config_assists.add_log_test_case(
                        message="Verify that the user can navigate from a support registry to a provider registry.",
                        test_case_id="F_09_02",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Clicked a random metric, switched to the providers tab, clicked on a random provider, and failed to verify that the user is navigated to the provider dashboard.",)
                    failed_cases += 1
            else:
                print("No providers found to test navigation.")
                config_assists.add_log_update("No providers found to test navigation for test case F_09_02", driver=driver, )
                failed_cases += 1

            # reset
            config_assists.add_log_heartbeat("finished test case F_09_02: Verify that the user can navigate from a support registry to a provider registry", driver=driver, )
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")

            # Test Case F_09_03: Verify that the user can navigate from a support registry to a patient dashboard.
            # Click a random metric, Switch to the patients tab, click on a random patient, and verify that the user is navigated to the patient dashboard.
            config_assists.add_log_heartbeat("Starting test case F_09_03: Verify that the user can navigate from a support registry to a patient dashboard", driver=driver, )

            # Click a random metric, Switch to the patients tab, click on a random patient, and verify that the user is navigated to the patient dashboard.
            random_metric_id, random_measure = registries_page.click_on_random_metric()

            config_assists.add_log_update(
                "Randomly selected measure: " + random_measure + " with metric ID: " + random_metric_id + " for test case F_09_03",
                driver=driver, )

            # Arrived at support level mspl page, Now click on random patient
            mspl_page.click_on_random_patient()
            start_time = time.perf_counter()
            mspl_page.switch_tab(1)
            mspl_page.ajax_preloader_wait("Clicked random patient")
            time_taken = time.perf_counter() - start_time

            # Verify that the user is navigated to the patient dashboard
            patient_dashboard_page = CozevaPatientDashboardPage(driver)
            load_status = patient_dashboard_page.is_patient_dashboard_opened()
            if load_status:
                print("Successfully navigated to the patient dashboard.")
                config_assists.add_log_update("Successfully navigated to the patient dashboard for test case F_09_03", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a support registry to a patient dashboard.",
                    test_case_id="F_09_03",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, switched to the patients tab, clicked on a random patient, and verified that the user is navigated to the patient dashboard.",)
            else:
                print("Failed to navigate to the patient dashboard.")
                config_assists.add_log_update("Failed to navigate to the patient dashboard for test case F_09_03", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a support registry to a patient dashboard.",
                    test_case_id="F_09_03",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, switched to the patients tab, clicked on a random patient, and failed to verify that the user is navigated to the patient dashboard.",)
                failed_cases += 1
            # reset
            config_assists.add_log_heartbeat("finished test case F_09_03: Verify that the user can navigate from a support registry to a patient dashboard", driver=driver, )
            mspl_page.switch_tab_and_close_current()
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")

            # Test Case F_09_04: Verify that the user can navigate from a support registry to a performance stats page.
            config_assists.add_log_heartbeat("Starting test case F_09_04: Verify that the user can navigate from a support registry to a performance stats page", driver=driver, )

            # Click a random metric, and verify that the user is navigated to the performance stats page.
            random_metric_id, random_measure = registries_page.click_on_random_metric()

            config_assists.add_log_update(
                "Randomly selected measure: " + random_measure + " with metric ID: " + random_metric_id + " for test case F_09_04",
                driver=driver, )

            # click on performance stats button
            mspl_page.click_on_performance_statistics_tab()
            load_status = mspl_page.is_performance_statistics_ribbon_visible()

            if load_status:
                print("Successfully navigated to the performance stats page.")
                config_assists.add_log_update("Successfully navigated to the performance stats page for test case F_09_04", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a support registry to a performance stats page.",
                    test_case_id="F_09_04",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, and verified that the user is navigated to the performance stats page.",)
            else:
                print("Failed to navigate to the performance stats page.")
                config_assists.add_log_update("Failed to navigate to the performance stats page for test case F_09_04", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a support registry to a performance stats page.",
                    test_case_id="F_09_04",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, and failed to verify that the user is navigated to the performance stats page.",)
                failed_cases += 1

            # reset
            config_assists.add_log_heartbeat("finished test case F_09_04: Verify that the user can navigate from a support registry to a performance stats page", driver=driver, )
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")

            # Test Case F_09_05: Verify that the user can change Lobs on the support registry page.
            config_assists.add_log_heartbeat("Starting test case F_09_05: Verify that the user can change Lobs on the support registry page", driver=driver, )
            # Change Lobs on the support registry page and verify that the user is able to change Lobs on the support registry page.
            # To test this, we will cycle between the lobs on the default MY, and for each, validate that the registries displays atleast one metric for the selected lob.

            MY_LOB_TUPLE = registries_page.fetch_my_and_lob()

            # RETURN FORMAT : Returns a tuple containing two dictionaries:
            # 1. my_lob_dict: {'MY': [list of MYs], 'LOB': [list of LoBs]}
            # 2. my_lob_default: {'MY': default MY, 'LOB': default LOB}

            LoB_list = MY_LOB_TUPLE[0]['LOB']

            # Begin lob loop
            for lob in LoB_list:
                registries_page.switch_lob(lob)

                measure_count = len(registries_page.fetch_num_den_from_registry())

                if measure_count > 0 and registries_page.is_registries_page_fully_opened():
                    print(f"Successfully changed LOB to {lob} and found {measure_count} measures.")
                    config_assists.add_log_update("Successfully changed LOB to " + lob + " and found " + str(measure_count) + " measures for test case F_09_05", driver=driver, )

                    config_assists.add_log_test_case(
                        message="Verify that the user can change Lobs on the support registry page.",
                        test_case_id="F_09_05",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Changed Lob to " +lob+" the support registry page and verified that the user is able to change Lobs on the support registry page.",)
                else:
                    print(f"Failed to change LOB to {lob} or found no measures.")
                    config_assists.add_log_update("Failed to change LOB to " + lob + " or found no measures for test case F_09_05", driver=driver, )

                    config_assists.add_log_test_case(
                        message="Verify that the user can change Lobs on the support registry page.",
                        test_case_id="F_09_05",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Changed Lob to " +lob+" the support registry page and failed to verify that the user is able to change Lobs on the support registry page.",)
                    failed_cases += 1

            # reset
            config_assists.add_log_heartbeat("finished test case F_09_05: Verify that the user can change Lobs on the support registry page", driver=driver, )
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")



            if failed_cases == 0:
                config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
            else:
                config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)

            # return to start
            header_nav.navigate_to_url(rc.base_landing_url)
            header_nav.ajax_preloader_wait("Return to start")
            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



        except Exception as e:
            print("Error in "+rc.test_name, e)
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

            if user_role not in ["Cozeva Support", "Customer Support", "Regional Support", "Limited Cozeva Support", "Office Admin Practice Delegate"]:
                config_assists.add_log_update(message="User role " + user_role + " is not in scope for this test.")
                pytest.skip(f"User role {user_role} is not in scope for this test.")

            failed_cases = 0

            header_nav = HeaderNavBar(driver)
            registries_page = CozevaRegistriesPage(driver)
            mspl_page = CozevaMSPLPage(driver)

            # Navigate to a random practice registry before starting.
            config_assists.add_log_update("Navigating to a random practice registry before starting test cases for practice registry navigation.", driver=driver)
            registries_page.click_on_random_metric()

            practice_names = mspl_page.fetch_practice_names()
            random_practice = choice(practice_names)
            print(f"Randomly selected practice: {random_practice}")
            config_assists.add_log_update("Randomly selected practice: " + random_practice + " for practice registry navigation test cases", driver=driver)
            mspl_page.click_on_practice_by_name(random_practice)
            start_time = time.perf_counter()
            mspl_page.ajax_preloader_wait("Clicked random practice: " + random_practice)
            time_taken = f"{time.perf_counter() - start_time:.2f}"

            if registries_page.is_registries_page_fully_opened():
                print(f"Successfully navigated to the practice registry for {random_practice}.")
                config_assists.add_log_update("Successfully navigated to the practice registry for " + random_practice + " for practice registry navigation test cases", driver=driver)

            start_url = header_nav.get_page_report()["CURRENT_URL"]
            rc.test_page_url = start_url

            # Test Case F_09_06: Verify that the user can navigate from a practice registry to a provider registry.
            # Click a random metric, Switch to the providers tab, click on a random provider, and verify that the user is navigated to the provider dashboard.
            config_assists.add_log_heartbeat("Starting test case F_09_06: Verify that the user can navigate from a practice registry to a provider registry", driver=driver, )

            # Random metric.
            random_metric_id, random_measure = registries_page.click_on_random_metric()
            config_assists.add_log_update("Randomly selected measure: " + random_measure + " with metric ID: " + random_metric_id + " for test case F_09_06", driver=driver, )

            # Click on random provider
            provider_names = mspl_page.fetch_provider_names()
            if provider_names:
                random_provider = choice(provider_names)
                print(f"Randomly selected provider: {random_provider}")
                config_assists.add_log_update("Randomly selected provider: " + random_provider + " for test case F_09_06", driver=driver, )
                mspl_page.click_on_provider_by_name(random_provider)
                start_time = time.perf_counter()
                mspl_page.ajax_preloader_wait("Clicked random provider: " + random_provider)
                time_taken = f"{time.perf_counter() - start_time:.2f}"

                # Verify that the user is navigated to the provider dashboard
                load_status = registries_page.is_registries_page_fully_opened()
                provider_context_name = header_nav.fetch_context_name()
                if provider_context_name == random_provider and load_status:
                    print(f"Successfully navigated to the provider dashboard for {random_provider}.")
                    config_assists.add_log_update("Successfully navigated to the provider dashboard for " + random_provider + " for test case F_09_06", driver=driver, )

                    config_assists.add_log_test_case(
                        message="Verify that the user can navigate from a practice registry to a provider registry.",
                        test_case_id="F_09_06",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Clicked a random metric, switched to the providers tab, clicked on a random provider, and verified that the user is navigated to the provider dashboard.",)
                elif not load_status:
                    print(f"Failed to navigate to the provider dashboard for {random_provider}. Current context: {provider_context_name}")
                    config_assists.add_log_update("Failed to navigate to the provider dashboard for " + random_provider + " for test case F_09_06", driver=driver, )

                    config_assists.add_log_test_case(
                        message="Verify that the user can navigate from a practice registry to a provider registry.",
                        test_case_id="F_09_06",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Clicked a random metric, switched to the providers tab, clicked on a random provider, and failed to verify that the user is navigated to the provider dashboard.",)
                    failed_cases += 1
            else:
                print("No providers found to test navigation.")
                config_assists.add_log_update("No providers found to test navigation for test case F_09_06", driver=driver, )
                failed_cases += 1

            # reset
            config_assists.add_log_heartbeat("finished test case F_09_06: Verify that the user can navigate from a practice registry to a provider registry", driver=driver, )
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")

            # Test Case F_09_07: Verify that the user can navigate from a practice registry to a patient dashboard.
            # Click a random metric, Switch to the patients tab, click on a random patient, and verify that the user is navigated to the patient dashboard.
            config_assists.add_log_heartbeat("Starting test case F_09_07: Verify that the user can navigate from a practice registry to a patient dashboard", driver=driver, )

            # Click a random metric, Switch to the patients tab, click on a random patient, and verify that the user is navigated to the patient dashboard.
            random_metric_id, random_measure = registries_page.click_on_random_metric()
            config_assists.add_log_update("Randomly selected measure: " + random_measure + " with metric ID: " + random_metric_id + " for test case F_09_07", driver=driver, )
            start_time = time.perf_counter()
            mspl_page.click_on_random_patient()
            mspl_page.switch_tab(1)
            time_taken = time.perf_counter() - start_time
            # Verify that the user is navigated to the patient dashboard
            patient_dashboard_page = CozevaPatientDashboardPage(driver)
            load_status = patient_dashboard_page.is_patient_dashboard_opened()
            if load_status:
                print("Successfully navigated to the patient dashboard.")
                config_assists.add_log_update("Successfully navigated to the patient dashboard for test case F_09_07", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a practice registry to a patient dashboard.",
                    test_case_id="F_09_07",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, switched to the patients tab, clicked on a random patient, and verified that the user is navigated to the patient dashboard.",)
            else:
                print("Failed to navigate to the patient dashboard.")
                config_assists.add_log_update("Failed to navigate to the patient dashboard for test case F_09_07", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a practice registry to a patient dashboard.",
                    test_case_id="F_09_07",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, switched to the patients tab, clicked on a random patient, and failed to verify that the user is navigated to the patient dashboard.",)
                failed_cases += 1

            # reset
            config_assists.add_log_heartbeat("finished test case F_09_07: Verify that the user can navigate from a practice registry to a patient dashboard", driver=driver, )
            header_nav.switch_tab_and_close_current()
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")

            # Test Case F_09_08: Verify that the user can navigate from a practice registry to a performance stats page.
            config_assists.add_log_heartbeat("Starting test case F_09_08: Verify that the user can navigate from a practice registry to a performance stats page", driver=driver, )
            # Click a random metric, and verify that the user is navigated to the performance stats page.
            random_metric_id, random_measure = registries_page.click_on_random_metric()
            config_assists.add_log_update("Randomly selected measure: " + random_measure + " with metric ID: " + random_metric_id + " for test case F_09_08", driver=driver, )
            # click on performance stats button
            mspl_page.click_on_performance_statistics_tab()
            load_status = mspl_page.is_performance_statistics_ribbon_visible()

            if load_status:
                print("Successfully navigated to the performance stats page.")
                config_assists.add_log_update("Successfully navigated to the performance stats page for test case F_09_08", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a practice registry to a performance stats page.",
                    test_case_id="F_09_08",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, and verified that the user is navigated to the performance stats page.",)
            else:
                print("Failed to navigate to the performance stats page.")
                config_assists.add_log_update("Failed to navigate to the performance stats page for test case F_09_08", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a practice registry to a performance stats page.",
                    test_case_id="F_09_08",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, and failed to verify that the user is navigated to the performance stats page.",)
                failed_cases += 1

            # reset
            config_assists.add_log_heartbeat("finished test case F_09_08: Verify that the user can navigate from a practice registry to a performance stats page", driver=driver, )
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")

            # Test Case F_09_09: Verify that the user can change Lobs on the practice registry page.
            config_assists.add_log_heartbeat("Starting test case F_09_09: Verify that the user can change Lobs on the practice registry page", driver=driver, )
            # Change Lobs on the practice registry page and verify that the user is able to change Lobs on the practice registry page.
            # To test this, we will cycle between the lobs on the default MY, and for each, validate that the registries displays atleast one metric for the selected lob.

            LoB_list = registries_page.fetch_my_and_lob()[0]['LOB']

            # Begin lob loop
            for lob in LoB_list:
                registries_page.switch_lob(lob)
                measure_count = len(registries_page.fetch_num_den_from_registry())
                if measure_count > 0 and registries_page.is_registries_page_fully_opened():
                    print(f"Successfully changed LOB to {lob} and found {measure_count} measures.")
                    config_assists.add_log_update("Successfully changed LOB to " + lob + " and found " + str(measure_count) + " measures for test case F_09_09", driver=driver, )
                    config_assists.add_log_test_case(
                        message="Verify that the user can change Lobs on the practice registry page.",
                        test_case_id="F_09_09",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Changed Lob to " +lob+" the practice registry page and verified that the user is able to change Lobs on the practice registry page.",)
                else:
                    print(f"Failed to change LOB to {lob} or found no measures.")
                    config_assists.add_log_update("Failed to change LOB to " + lob + " or found no measures for test case F_09_09", driver=driver, )
                    config_assists.add_log_test_case(
                        message="Verify that the user can change Lobs on the practice registry page.",
                        test_case_id="F_09_09",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Changed Lob to " +lob+" the practice registry page and failed to verify that the user is able to change Lobs on the practice registry page.",)
                    failed_cases += 1

            # Reset
            config_assists.add_log_heartbeat("finished test case F_09_09: Verify that the user can change Lobs on the practice registry page", driver=driver, )
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")



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

            if user_role not in ["Cozeva Support", "Customer Support", "Regional Support", "Limited Cozeva Support",
                                 "Office Admin Practice Delegate", "Office Admin Provider Delegate", "Provider"]:
                config_assists.add_log_update(message="User role " + user_role + " is not in scope for this test.")
                pytest.skip(f"User role {user_role} is not in scope for this test.")

            failed_cases = 0

            header_nav = HeaderNavBar(driver)
            registries_page = CozevaRegistriesPage(driver)
            mspl_page = CozevaMSPLPage(driver)

            # Navigate to a random provider registry before starting.
            config_assists.add_log_update("Navigating to a random provider registry before starting test cases for provider registry navigation.", driver=driver)
            registries_page.click_on_random_metric()

            provider_names = mspl_page.fetch_provider_names()
            random_provider = choice(provider_names)
            print(f"Randomly selected provider: {random_provider}")
            config_assists.add_log_update("Randomly selected provider: " + random_provider + " for provider registry navigation test cases", driver=driver)
            mspl_page.click_on_provider_by_name(random_provider)
            start_time = time.perf_counter()
            mspl_page.ajax_preloader_wait("Clicked random provider: " + random_provider)
            time_taken = f"{time.perf_counter() - start_time:.2f}"

            if registries_page.is_registries_page_fully_opened():
                print(f"Successfully navigated to the provider registry for {random_provider}.")
                config_assists.add_log_update("Successfully navigated to the provider registry for " + random_provider + " for provider registry navigation test cases", driver=driver)

            start_url = header_nav.get_page_report()["CURRENT_URL"]
            rc.test_page_url = start_url
            # Test Case F_09_10: Verify that the user can navigate from a provider registry to a patient dashboard.
            # Click a random metric, Switch to the patients tab, click on a random patient, and verify that the user is navigated to the patient dashboard.
            config_assists.add_log_heartbeat("Starting test case F_09_10: Verify that the user can navigate from a provider registry to a patient dashboard", driver=driver, )
            # Click a random metric, Switch to the patients tab, click on a random patient, and verify that the user is navigated to the patient dashboard.
            random_metric_id, random_measure = registries_page.click_on_random_metric()
            config_assists.add_log_update("Randomly selected measure: " + random_measure + " with metric ID: " + random_metric_id + " for test case F_09_10", driver=driver, )
            start_time = time.perf_counter()
            mspl_page.click_on_random_patient()
            mspl_page.switch_tab(1)
            time_taken = time.perf_counter() - start_time
            # Verify that the user is navigated to the patient dashboard
            patient_dashboard_page = CozevaPatientDashboardPage(driver)
            load_status = patient_dashboard_page.is_patient_dashboard_opened()
            if load_status:
                print("Successfully navigated to the patient dashboard.")
                config_assists.add_log_update("Successfully navigated to the patient dashboard for test case F_09_10", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a provider registry to a patient dashboard.",
                    test_case_id="F_09_10",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, switched to the patients tab, clicked on a random patient, and verified that the user is navigated to the patient dashboard.",)
            else:
                print("Failed to navigate to the patient dashboard.")
                config_assists.add_log_update("Failed to navigate to the patient dashboard for test case F_09_10", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a provider registry to a patient dashboard.",
                    test_case_id="F_09_10",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, switched to the patients tab, clicked on a random patient, and failed to verify that the user is navigated to the patient dashboard.",)
                failed_cases += 1

            # reset
            config_assists.add_log_heartbeat("finished test case F_09_10: Verify that the user can navigate from a provider registry to a patient dashboard", driver=driver, )
            header_nav.switch_tab_and_close_current()
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")

            # Test Case F_09_11: Verify that the user can navigate from a provider registry to a performance stats page.
            config_assists.add_log_heartbeat("Starting test case F_09_11: Verify that the user can navigate from a provider registry to a performance stats page", driver=driver, )
            # Click a random metric, and verify that the user is navigated to the performance stats page.
            random_metric_id, random_measure = registries_page.click_on_random_metric()
            config_assists.add_log_update("Randomly selected measure: " + random_measure + " with metric ID: " + random_metric_id + " for test case F_09_11", driver=driver, )
            # click on performance stats button
            mspl_page.click_on_performance_statistics_tab()
            load_status = mspl_page.is_performance_statistics_ribbon_visible()

            if load_status:
                print("Successfully navigated to the performance stats page.")
                config_assists.add_log_update("Successfully navigated to the performance stats page for test case F_09_11", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a provider registry to a performance stats page.",
                    test_case_id="F_09_11",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, and verified that the user is navigated to the performance stats page.",)
            else:
                print("Failed to navigate to the performance stats page.")
                config_assists.add_log_update("Failed to navigate to the performance stats page for test case F_09_11", driver=driver, )

                config_assists.add_log_test_case(
                    message="Verify that the user can navigate from a provider registry to a performance stats page.",
                    test_case_id="F_09_11",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Clicked a random metric, and failed to verify that the user is navigated to the performance stats page.",)
                failed_cases += 1

            # reset
            config_assists.add_log_heartbeat("finished test case F_09_11: Verify that the user can navigate from a provider registry to a performance stats page", driver=driver, )
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")

            # Test Case F_09_12: Verify that the user can change Lobs on the provider registry page.
            config_assists.add_log_heartbeat("Starting test case F_09_12: Verify that the user can change Lobs on the provider registry page", driver=driver, )
            # Change Lobs on the provider registry page and verify that the user is able to change Lobs on the provider registry page.
            # To test this, we will cycle between the lobs on the default MY, and for each, validate that the registries displays atleast one metric for the selected lob.
            MY_LOB_TUPLE = registries_page.fetch_my_and_lob()
            LoB_list = MY_LOB_TUPLE[0]['LOB']

            # Begin lob loop
            for lob in LoB_list:
                registries_page.switch_lob(lob)
                measure_count = len(registries_page.fetch_num_den_from_registry())
                if measure_count > 0 and registries_page.is_registries_page_fully_opened():
                    print(f"Successfully changed LOB to {lob} and found {measure_count} measures.")
                    config_assists.add_log_update("Successfully changed LOB to " + lob + " and found " + str(measure_count) + " measures for test case F_09_12", driver=driver, )
                    config_assists.add_log_test_case(
                        message="Verify that the user can change Lobs on the provider registry page.",
                        test_case_id="F_09_12",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Changed Lob to " +lob+" the provider registry page and verified that the user is able to change Lobs on the provider registry page.",)
                else:
                    print(f"Failed to change LOB to {lob} or found no measures.")
                    config_assists.add_log_update("Failed to change LOB to " + lob + " or found no measures for test case F_09_12", driver=driver, )
                    config_assists.add_log_test_case(
                        message="Verify that the user can change Lobs on the provider registry page.",
                        test_case_id="F_09_12",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms=time_taken,
                        comment="Changed Lob to " +lob+" the provider registry page and failed to verify that the user is able to change Lobs on the provider registry page.",)
                    failed_cases += 1

            # Reset
            config_assists.add_log_heartbeat("finished test case F_09_12: Verify that the user can change Lobs on the provider registry page", driver=driver, )
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")


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



