import time

import pytest
import traceback

from pages.cozeva_registries_page import CozevaRegistriesPage
from core.base_page import HeaderNavBar
from pages.cozeva_payment_tool_page import CozevaPaymentToolPage


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
            user_role = rc.user_role
            if user_role not in ["Cozeva Support","Customer Support", "Regional Support", "Limited Cozeva Support"]:
                config_assists.add_log_update(message="User role " + user_role + " is not in scope for this test.")
                pytest.skip(f"User role {user_role} is not in scope for this test.")


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
                print(f"Clicking on sidebar entry: {entry}")

                header_nav.click_sidebar_entry(entry)

                start_time = time.perf_counter()
                header_nav.ajax_preloader_wait("After Entry Click Sidebar")
                time_taken_loader = f"{time.perf_counter() - start_time:.2f}"
                print(
                    f"Finished waiting for page load after clicking sidebar entry: {entry}. Time taken: {time_taken_loader} seconds")

                current_url = header_nav.get_page_report()["CURRENT_URL"]

                if entry not in ["Registries","Reports", "Payment Tool", "Export Dashboard",]:
                    data_table_info = header_nav.fetch_datatable_info()
                    time_taken = f"{time.perf_counter() - start_time:.2f}"


                    # Add datatableinfo check
                    if data_table_info:
                        print(f"Successfully navigated to new page after clicking sidebar entry: {entry}")
                        config_assists.add_log_test_case(message="Click on sidebar entry: " + entry + " and verify page load",
                                                         status='PASSED',
                                                         driver=driver,
                                                         time_taken_ms=time_taken,
                                                         comment="Data table info found: " + str(data_table_info))

                    else:
                        failed_cases += 1
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            status='FAILED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Data table info not found after clicking sidebar entry: " + entry)

                elif entry == "Payment Tool":
                    # For Payment Tool, we can check for the presence of a unique element on the Payment
                    # Tool page to verify that the page has loaded correctly. If client does not have

                    payment_tool_page = CozevaPaymentToolPage(driver)
                    if payment_tool_page.is_payment_tool_page_open():
                        cart_dict = payment_tool_page.fetch_payment_tool_cards_per_cycle()
                        print(f"Successfully navigated to Payment Tool page. Fetched card info: {cart_dict}")
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            status='PASSED',
                            driver=driver,
                            comment="Payment Tool page opened and card info fetched: " + str(cart_dict))
                    elif payment_tool_page.is_payment_tool_page_open() == "Disabled":
                        print(f"Payment Tool is not enabled for this client. Sidebar entry: {entry} leads to page with 'not enabled' message.")
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            status='PASSED',
                            driver=driver,
                            comment="Payment Tool is not enabled for this client, but appropriate message is displayed.")
                    else:
                        failed_cases += 1
                        print(f"Failed to navigate to Payment Tool page after clicking sidebar entry: {entry}")
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            status='FAILED',
                            driver=driver,
                            comment="Payment Tool page did not open after clicking sidebar entry.")



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

    # @pytest.mark.PracticeSidebar
    # def test_practice_sidebar(self, logged_in_driver, base_url, config_assists):
    #     """
    #     Test Case: Navigate the different sidebar options in Cozeva after logging in.
    #     Steps:
    #     1. Log in to Cozeva using valid credentials.
    #     2. Collect sidebar elements.
    #     3. Loop through each sidebar element and navigate to the corresponding page.
    #     4. Verify that the correct page is displayed for each sidebar option.
    #     """
    #     try:
    #         driver = logged_in_driver
    #         profile = getattr(driver, "_rtvs_profile", None)
    #         rc = config_assists.get_run_configuration()
    #         failed_cases = 0
    #
    #         cozeva_registries_page = CozevaRegistriesPage(driver)
    #         cozeva_registries_page.registry_test_method()
    #
    #         config_assists.add_log_update(
    #             message=f"Navigated to {cozeva_registries_page.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases",
    #             driver=driver
    #         )
    #
    #         config_assists.add_log_heartbeat(
    #             message=f"Test case 1 : Clicking on sidebar option - Registries",
    #             status="STARTED",
    #             driver=driver
    #         )
    #
    #         config_assists.add_log_test_case(
    #             message=f"Test case 1a : Checking that sidebar option exists for Registries",
    #             status="PASSED",
    #             driver=driver
    #         )
    #
    #         config_assists.add_log_test_case(
    #             message=f"Test case 1b : Clicking on Sidebar Registries and verifying page load",
    #             status="PASSED",
    #             driver=driver
    #         )
    #
    #         config_assists.add_log_heartbeat(
    #             message=f"Test case 2 : Clicking on option - Supplemental Data List",
    #             status="STARTED",
    #             driver=driver
    #         )
    #
    #         config_assists.add_log_test_case(
    #             message=f"Test case 2a : Checking that sidebar option exists for Registries",
    #             status="PASSED",
    #             driver=driver
    #         )
    #
    #         config_assists.add_log_test_case(
    #             message=f"Test case 2b : Clicking on sidebar Supplemental Data list and verifying page load",
    #             status="PASSED",
    #             driver=driver
    #         )
    #
    #         config_assists.add_log_heartbeat(
    #             message=f"Test case 3 : Clicking on option - HCC data list",
    #             status="STARTED",
    #             driver=driver
    #         )
    #
    #         config_assists.add_log_test_case(
    #             message=f"Test case 3a : Checking that sidebar option exists for HCC Data List",
    #             status="PASSED",
    #             driver=driver
    #         )
    #         # failed_cases += 1
    #
    #         config_assists.add_log_test_case(
    #             message=f"Test case 3b : Clicking on sidebar HCC Data list and verifying page load",
    #             status="PASSED",
    #             driver=driver
    #         )
    #
    #         # failed_cases += 1
    #
    #         if failed_cases == 0:
    #             config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
    #         else:
    #             config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)
    #
    #         assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."
    #
    #         # test case 1 : Click on the registries sidebar and verify page load
    #         # test case 2 : Click on Supplemental Data list sidebar and verify page load
    #         # test case
    #
    #     except Exception as e:
    #         print("Error in test_loop_through_support_sidebar:", e)
    #         traceback.print_exc()
    #         assert False, f"Test failed due to exception: {e}"



