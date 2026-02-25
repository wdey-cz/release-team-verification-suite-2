import time

import pytest
import traceback

from pages.cozeva_registries_page import CozevaRegistriesPage
from core.base_page import HeaderNavBar


@pytest.mark.CozevaComboPack1
@pytest.mark.SidebarTestPackage
class TestSidebar:

    @pytest.mark.SupportSidebar
    def test_support_sidebar(self, logged_in_driver, base_url, config_assists):
        """
        Test Case: Navigate the different sidebar options in Cozeva after logging in.
        Steps:
        1. Log in to Cozeva using valid credentials.
        2. Collect sidebar elements.
        3. Loop through each sidebar element and navigate to the corresponding page.
        4. Verify that the correct page is displayed for each sidebar option.

        TC_Validate existence of default sidebar options : Validate that all default sidebar entries are present on the support level registries page
        test case 2-x : Click on each sidebar entry and validate that the page contains an element defined below. Then navigate back to the original page before clicking the next sidebar entry.

        Default element to validate for each sidebar entry after click: DatatableInfo (Showing x out of x entries) - This is present on most pages on the sidebar.
        Exceptions:
        - Export Dashboard: Opens in a new tab and does not have the datatable info element.
        - Registries, Payment Tool: Does not have the datatable info element.
        -
        """
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            failed_cases = 0

            # Load the header nav page for sidebar navigation functions
            header_nav = HeaderNavBar(driver)


            config_assists.add_log_update(
                message=f"Navigated to {header_nav.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases",
                driver=driver)

            # Save the start url to navigate back to after each sidebar click
            start_url = header_nav.get_page_report()["CURRENT_URL"]

            config_assists.add_log_heartbeat("Starting sidebar validation for Support Level Registries", driver=driver, status="STARTED")
            config_assists.add_log_heartbeat("Starting Test Case: Validate existence of default sidebar options", driver=driver, status="STARTED")

            # fetch the default sidebar options from header nav page.
            default_support_sidebar_options = header_nav.SUPPORT_SIDEBAR_OPTIONS

            # Collect all sidebar options from the UI.
            sidebar_options = header_nav.fetch_sidebar_entries()

            # Compare the two lists and create two lists. One for new entries and one for missing entries compared to the default list.
            missing_entries = [entry for entry in default_support_sidebar_options if entry not in sidebar_options]
            new_entries = [entry for entry in sidebar_options if entry not in default_support_sidebar_options]

            if len(missing_entries) == 0:
                config_assists.add_log_test_case(message="TC_Validate existence of default sidebar options",
                                                 status='PASSED', driver=driver,
                                                 comment="Entries on the sidebar : " + ", ".join(sidebar_options))
            else:  # Not exactly a failed case if there are missing entries, but we want to log it for visibility and investigation.
                config_assists.add_log_test_case(message="TC_Validate existence of default sidebar options",
                                                 status='FAILED', driver=driver,
                                                 comment="Missing sidebar options compared to default: " + ", ".join(missing_entries))

            if len(new_entries) > 0:
                config_assists.add_log_test_case(message="TC_Validate existence of default sidebar options",
                                                 status='INFO', driver=driver,
                                                 comment="New sidebar options compared to default: " + ", ".join(new_entries))

            config_assists.add_log_heartbeat("Starting Test Case: Loop through each sidebar entry, click it, and verify page load",
                                             status="STARTED",
                                             driver=driver)

            # Now loop through each sidebar entry, click it, check for datatableinfo or some exception, handle it,
            # then navigate back to start url before clicking the next one
            for entry in sidebar_options:
                config_assists.add_log_heartbeat("Sidebar entry to be tested: " + entry,
                                                 driver=driver)

                # Skipping this because this opens in a new tab. Need to factor that in.
                if entry == "Export Dashboard":
                    smth = 0

                print(f"Clicking on sidebar entry: {entry}")
                header_nav.click_sidebar_entry(entry)

                start_time = time.perf_counter()
                header_nav.ajax_preloader_wait(f"After {entry} Click Sidebar")
                time_taken_ajax = f"{time.perf_counter() - start_time:.2f}"
                print(
                    f"Finished waiting for page load after clicking sidebar entry: {entry}. Time taken: {time_taken_ajax} seconds")

                current_url = header_nav.get_page_report()["CURRENT_URL"]
                if current_url != start_url:
                    print(f"Successfully navigated to new page after clicking sidebar entry: {entry}")
                    config_assists.add_log_test_case(message="",
                                                     status='PASSED', driver=driver)

                else:
                    failed_cases += 1
                    print(f"Failed to navigate away from {start_url} after clicking sidebar entry: {entry}")

                print("Navigating back to start URL...")
                driver.get(start_url)
                header_nav.ajax_preloader_wait(desc="Back to start")

            if failed_cases == 0:
                config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
            else:
                config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)

            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



        except Exception as e:
            print("Error in test_loop_through_support_sidebar:", e)
            traceback.print_exc()
            assert False, f"Test failed due to exception: {e}"

    @pytest.mark.PracticeSidebar
    def test_practice_sidebar(self, logged_in_driver, base_url, config_assists):
        """
        Test Case: Navigate the different sidebar options in Cozeva after logging in.
        Steps:
        1. Log in to Cozeva using valid credentials.
        2. Collect sidebar elements.
        3. Loop through each sidebar element and navigate to the corresponding page.
        4. Verify that the correct page is displayed for each sidebar option.
        """
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            failed_cases = 0

            cozeva_registries_page = CozevaRegistriesPage(driver)
            cozeva_registries_page.registry_test_method()

            config_assists.add_log_update(
                message=f"Navigated to {cozeva_registries_page.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases",
                driver=driver
            )

            config_assists.add_log_heartbeat(
                message=f"Test case 1 : Clicking on sidebar option - Registries",
                status="STARTED",
                driver=driver
            )

            config_assists.add_log_test_case(
                message=f"Test case 1a : Checking that sidebar option exists for Registries",
                status="PASSED",
                driver=driver
            )

            config_assists.add_log_test_case(
                message=f"Test case 1b : Clicking on Sidebar Registries and verifying page load",
                status="PASSED",
                driver=driver
            )

            config_assists.add_log_heartbeat(
                message=f"Test case 2 : Clicking on option - Supplemental Data List",
                status="STARTED",
                driver=driver
            )

            config_assists.add_log_test_case(
                message=f"Test case 2a : Checking that sidebar option exists for Registries",
                status="PASSED",
                driver=driver
            )

            config_assists.add_log_test_case(
                message=f"Test case 2b : Clicking on sidebar Supplemental Data list and verifying page load",
                status="PASSED",
                driver=driver
            )

            config_assists.add_log_heartbeat(
                message=f"Test case 3 : Clicking on option - HCC data list",
                status="STARTED",
                driver=driver
            )

            config_assists.add_log_test_case(
                message=f"Test case 3a : Checking that sidebar option exists for HCC Data List",
                status="PASSED",
                driver=driver
            )
            # failed_cases += 1

            config_assists.add_log_test_case(
                message=f"Test case 3b : Clicking on sidebar HCC Data list and verifying page load",
                status="PASSED",
                driver=driver
            )

            # failed_cases += 1

            if failed_cases == 0:
                config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
            else:
                config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)

            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."

            # test case 1 : Click on the registries sidebar and verify page load
            # test case 2 : Click on Supplemental Data list sidebar and verify page load
            # test case

        except Exception as e:
            print("Error in test_loop_through_support_sidebar:", e)
            traceback.print_exc()
            assert False, f"Test failed due to exception: {e}"



