import time
from random import choice

import pytest
import traceback

from pages.cozeva_registries_page import CozevaRegistriesPage
from core.base_page import HeaderNavBar
from pages.cozeva_payment_tool_page import CozevaPaymentToolPage
from pages.cozeva_providers_page import CozevaProvidersPage


@pytest.mark.CozevaComboPack1
@pytest.mark.SidebarTestPackage
class TestSidebar:

    @pytest.mark.SupportSidebar
    def test_support_sidebar(self, logged_in_driver, base_url, config_assists):
        """
        Feature - F_01_Sidebar
        Test Cases -
         F_01_01: Validate the visible sidebar options against a default list.
         F_01_02: Validate each sidebar option is able to navigate to the relevant page.
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
            rc.base_landing_url = driver.current_url

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
                config_assists.add_log_test_case(message="Validate the visible sidebar options against a default list. ",
                                                 test_case_id = "F_01_01",
                                                 status='PASSED', driver=driver,
                                                 comment="Entries on the sidebar : " + ", ".join(sidebar_options))
            else:  # Not exactly a failed case if there are missing entries, but we want to log it for visibility and investigation.
                config_assists.add_log_test_case(message="TC_Validate existence of default sidebar options",
                                                 test_case_id="F_01_01",
                                                 status='FAILED', driver=driver,
                                                 comment="Missing sidebar options compared to default: " + ", ".join(missing_entries))

            if len(new_entries) > 0:
                config_assists.add_log_test_case(message="TC_Validate existence of default sidebar options",
                                                 test_case_id="F_01_01",
                                                 status='INFO', driver=driver,
                                                 comment="New sidebar options compared to default: " + ", ".join(new_entries))

            config_assists.add_log_heartbeat("Starting Test Case: Loop through each sidebar entry, click it, and verify page load",
                                             status="STARTED",
                                             driver=driver)

            # Now loop through each sidebar entry, click it, check for datatableinfo or some exception, handle it,
            # then navigate back to start url before clicking the next one

            for entry in sidebar_options:
                # To check a specific entry for testing,
                # if entry not in ["Payment Tool", "Export Dashboard"]:
                #     continue
                config_assists.add_log_heartbeat("Sidebar entry to be tested: " + entry,
                                                 driver=driver)
                print(f"Clicking on sidebar entry: {entry}")
                header_nav.click_sidebar_entry(entry)

                # time Calculation for page load after click
                start_time = time.perf_counter()
                header_nav.ajax_preloader_wait("After Entry Click Sidebar")
                time_taken_loader = f"{time.perf_counter() - start_time:.2f}"
                print(
                    f"Finished waiting for page load after clicking sidebar entry: {entry}. Time taken: {time_taken_loader} seconds")

                current_url = header_nav.get_page_report()["CURRENT_URL"]

                # These Sidebar pages all have datatables
                if entry not in ["Registries","Reports", "Payment Tool"]:
                    if entry == "Export Dashboard":
                        header_nav.switch_tab(1)

                    data_table_info = header_nav.fetch_datatable_info()
                    time_taken = f"{time.perf_counter() - start_time:.2f}"


                    # Add datatableinfo check
                    if data_table_info:
                        print(f"Successfully navigated to new page after clicking sidebar entry: {entry}")
                        config_assists.add_log_test_case(message="Click on sidebar entry: " + entry + " and verify page load",
                                                         test_case_id="F_01_02",
                                                         status='PASSED',
                                                         driver=driver,
                                                         time_taken_ms=time_taken,
                                                         comment="Data table info found: " + str(data_table_info))

                    else:
                        failed_cases += 1
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_02",
                            status='FAILED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Data table info not found after clicking sidebar entry: " + entry)
                    if entry == "Export Dashboard":
                        header_nav.switch_tab_and_close_current(0)

                elif entry == "Payment Tool":
                    # For Payment Tool, we can check for the presence of a unique element on the Payment
                    # Tool page to verify that the page has loaded correctly. If client does not have

                    payment_tool_page = CozevaPaymentToolPage(driver)
                    if payment_tool_page.is_payment_tool_page_open() != "Disabled":
                        cart_dict = payment_tool_page.fetch_payment_tool_cards_per_cycle()
                        time_taken = f"{time.perf_counter() - start_time:.2f}"
                        print(f"Successfully navigated to Payment Tool page. Fetched card info: {cart_dict}")
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_02",
                            status='PASSED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Payment Tool page opened and card info fetched: " + str(cart_dict))
                    elif payment_tool_page.is_payment_tool_page_open() == "Disabled":
                        print(f"Payment Tool is not enabled for this client. Sidebar entry: {entry} leads to page with 'not enabled' message.")
                        time_taken = f"{time.perf_counter() - start_time:.2f}"
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_02",
                            status='PASSED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Payment Tool is not enabled for this client, but appropriate message is displayed.")
                    else:
                        failed_cases += 1
                        print(f"Failed to navigate to Payment Tool page after clicking sidebar entry: {entry}")
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_02",
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

            # return to start
            header_nav.navigate_to_url(rc.base_landing_url)
            header_nav.ajax_preloader_wait("Return to start")
            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



        except Exception as e:
            print("Error in test_loop_through_support_sidebar:", e)
            traceback.print_exc()
            assert False, f"Test failed due to exception: {e}"

    @pytest.mark.PracticeSidebar
    def test_practice_sidebar(self, logged_in_driver, base_url, config_assists):
        """
        Feature - F_01_Sidebar
        Test Cases -
         F_01_03: Validate the visible sidebar options against a default list.
         F_01_04: Validate each sidebar option is able to navigate to the relevant page.
        """
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            user_role = rc.user_role
            if user_role not in ["Cozeva Support", "Customer Support", "Regional Support", "Limited Cozeva Support", "Office Admin Practice Delegate"]:
                config_assists.add_log_update(message="User role " + user_role + " is not in scope for this test.")
                pytest.skip(f"User role {user_role} is not in scope for this test.")

            failed_cases = 0

            # We go back to the Base_landing url after the test function is complete/errored
            rc.base_landing_url = driver.current_url

            # Load the header nav page for sidebar navigation functions
            header_nav = HeaderNavBar(driver)

            # First, We need to navigate to a random practice sidebar if the user role is not Office Admin Practice Delegate. Starting page is landing registries
            if user_role != "Office Admin Practice Delegate":
                config_assists.add_log_update(
                    message=f"{user_role} role detected, navigating to Providers list page to click on a practice and access practice sidebar.",
                    driver=driver)
                header_nav.click_sidebar_entry("Providers")
                header_nav.ajax_preloader_wait("Navigate to Providers page")

                # now load the providers page object
                providers_list_page = CozevaProvidersPage(driver)
                practice_list = providers_list_page.fetch_practice_names()
                if len(practice_list) == 0:
                    print("No practices found for this client. Cannot continue with Practice sidebar tests.")
                    config_assists.add_log_update(message="No practices found for this client. Cannot continue with Practice sidebar tests.", driver=driver)
                    pytest.skip("No practices found for this client. Cannot continue with Practice sidebar tests.")
                elif len(practice_list) != 0:
                    print(f"Fetched practice list: {practice_list}.")
                    r_practice = choice(practice_list)
                    providers_list_page.click_practice_by_name(r_practice)
                    header_nav.ajax_preloader_wait(f"Navigate to practice {r_practice} page")
                    print(f"Successfully navigated to practice page for practice: {r_practice}.")
                    config_assists.add_log_update(
                        message="Navigated to practice page for practice: " + r_practice,
                        driver=driver)

            # For practice delegate, we will already be on a practice sidebar after login, but we can add some logs to indicate that.
            elif user_role == "Office Admin Practice Delegate":
                config_assists.add_log_update(
                    message=f"{user_role} role detected, already on practice sidebar after login.",
                    driver=driver)



            config_assists.add_log_update(
                message=f"Navigated to {header_nav.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases",
                driver=driver)

            # Save the start url to navigate back to after each sidebar click
            start_url = header_nav.get_page_report()["CURRENT_URL"]

            config_assists.add_log_heartbeat("Starting sidebar validation for Practice Level Registries", driver=driver,
                                             status="STARTED")
            config_assists.add_log_heartbeat("Starting Test Case: Validate existence of default sidebar options",
                                             driver=driver, status="STARTED")

            # fetch the default sidebar options from header nav page.
            default_practice_sidebar_options = header_nav.PRACTICE_SIDEBAR_OPTIONS

            # Collect all sidebar options from the UI.
            sidebar_options = header_nav.fetch_sidebar_entries()

            # Compare the two lists and create two lists. One for new entries and one for missing entries compared to the default list.
            missing_entries = [entry for entry in default_practice_sidebar_options if entry not in sidebar_options]
            new_entries = [entry for entry in sidebar_options if entry not in default_practice_sidebar_options]

            if len(missing_entries) == 0:
                config_assists.add_log_test_case(message="TC_Validate existence of default sidebar options",
                                                 test_case_id="F_01_03",
                                                 status='PASSED', driver=driver,
                                                 comment="Entries on the sidebar : " + ", ".join(sidebar_options))
            else:  # Not exactly a failed case if there are missing entries, but we want to log it for visibility and investigation.
                config_assists.add_log_test_case(message="TC_Validate existence of default sidebar options",
                                                 test_case_id="F_01_03",
                                                 status='FAILED', driver=driver,
                                                 comment="Missing sidebar options compared to default: " + ", ".join(
                                                     missing_entries))

            if len(new_entries) > 0:
                config_assists.add_log_test_case(message="TC_Validate existence of default sidebar options",
                                                 test_case_id="F_01_03",
                                                 status='INFO', driver=driver,
                                                 comment="New sidebar options compared to default: " + ", ".join(
                                                     new_entries))

            config_assists.add_log_heartbeat(
                "Starting Test Case: Loop through each sidebar entry, click it, and verify page load",
                status="STARTED",
                driver=driver)

            # Now loop through each sidebar entry, click it, check for datatableinfo or some exception, handle it,
            # then navigate back to start url before clicking the next one

            for entry in sidebar_options:
                # To check a specific entry for testing,
                # if entry not in ["Payment Tool", "Export Dashboard"]:
                #     continue
                config_assists.add_log_heartbeat("Sidebar entry to be tested: " + entry,
                                                 driver=driver)
                print(f"Clicking on sidebar entry: {entry}")
                header_nav.click_sidebar_entry(entry)

                # time Calculation for page load after click
                start_time = time.perf_counter()
                header_nav.ajax_preloader_wait("After Entry Click Sidebar")
                time_taken_loader = f"{time.perf_counter() - start_time:.2f}"
                print(
                    f"Finished waiting for page load after clicking sidebar entry: {entry}. Time taken: {time_taken_loader} seconds")

                current_url = header_nav.get_page_report()["CURRENT_URL"]

                # These Sidebar pages all have datatables
                if entry not in ["Registries", "Reports", "Payment Tool"]:
                    if entry == "Export Dashboard":
                        header_nav.switch_tab(1)
                    data_table_info = header_nav.fetch_datatable_info()
                    time_taken = f"{time.perf_counter() - start_time:.2f}"

                    # Add datatableinfo check
                    if data_table_info:
                        print(f"Successfully navigated to new page after clicking sidebar entry: {entry}")
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_04",
                            status='PASSED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Data table info found: " + str(data_table_info))

                    else:
                        failed_cases += 1
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_04",
                            status='FAILED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Data table info not found after clicking sidebar entry: " + entry)
                    if entry == "Export Dashboard":
                        header_nav.switch_tab_and_close_current(0)

                elif entry == "Payment Tool":
                    # For Payment Tool, we can check for the presence of a unique element on the Payment
                    # Tool page to verify that the page has loaded correctly. If client does not have

                    payment_tool_page = CozevaPaymentToolPage(driver)
                    if payment_tool_page.is_payment_tool_page_open() != "Disabled":
                        cart_dict = payment_tool_page.fetch_payment_tool_cards_per_cycle()
                        time_taken = f"{time.perf_counter() - start_time:.2f}"
                        print(f"Successfully navigated to Payment Tool page. Fetched card info: {cart_dict}")
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_04",
                            status='PASSED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Payment Tool page opened and card info fetched: " + str(cart_dict))
                    elif payment_tool_page.is_payment_tool_page_open() == "Disabled":
                        print(
                            f"Payment Tool is not enabled for this client. Sidebar entry: {entry} leads to page with 'not enabled' message.")
                        time_taken = f"{time.perf_counter() - start_time:.2f}"
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_04",
                            status='PASSED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Payment Tool is not enabled for this client, but appropriate message is displayed.")
                    else:
                        failed_cases += 1
                        print(f"Failed to navigate to Payment Tool page after clicking sidebar entry: {entry}")
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_04",
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

            # return to start
            header_nav.navigate_to_url(rc.base_landing_url)
            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



        except Exception as e:
            print("Error in test_practice_sidebar:", e)
            traceback.print_exc()
            assert False, f"Test failed due to exception: {e}"

    @pytest.mark.ProviderSidebar
    def test_provider_sidebar(self, logged_in_driver, base_url, config_assists):
        """
        Feature - F_01_Sidebar
        Test Cases -
         F_01_05: Validate the visible sidebar options against a default list.
         F_01_06: Validate each sidebar option is able to navigate to the relevant page.
        """
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            user_role = rc.user_role
            if user_role not in ["Cozeva Support", "Customer Support", "Regional Support", "Limited Cozeva Support",
                                 "Office Admin Practice Delegate", "Office Admin Provider Delegate", "Provider"]:
                config_assists.add_log_update(message="User role " + user_role + " is not in scope for this test.")
                pytest.skip(f"User role {user_role} is not in scope for this test.")

            # Counter for number of failed cases. Assert this = 0 at the end of the test.
            failed_cases = 0

            # We go back to the pre-test url after the test function is complete/errored
            rc.base_landing_url = driver.current_url

            # Load the header nav page for sidebar navigation functions
            header_nav = HeaderNavBar(driver)

            '''
            First, We need to navigate to a random Provider sidebar. 
            Providers and provider delegate users start on the provider registry page, so no need to navigate to providers page for those roles.
            For Practice Delegate roles, we will have to navigate to the provider list and click one, Tab switching not required. 
            '''
            if user_role != "Office Admin Provider Delegate" or user_role != "Provider":
                config_assists.add_log_update(
                    message=f"{user_role} role detected, navigating to Providers list page to click on a provider and access provider sidebar.",
                    driver=driver)
                header_nav.click_sidebar_entry("Providers")
                header_nav.ajax_preloader_wait("Navigate to Providers page")

                # now load the providers page object
                providers_list_page = CozevaProvidersPage(driver)
                provider_list = providers_list_page.fetch_provider_names()
                if len(provider_list) == 0:
                    print("No providers found for this client. Cannot continue with provider sidebar tests.")
                    config_assists.add_log_update(
                        message="No providers found for this client. Cannot continue with provider sidebar tests.",
                        driver=driver)
                    pytest.skip("No providers found for this client. Cannot continue with provider sidebar tests.")
                elif len(provider_list) != 0:
                    print(f"Fetched provider list: {provider_list}.")
                    r_provider = choice(provider_list)
                    providers_list_page.click_provider_by_name(r_provider)
                    header_nav.ajax_preloader_wait(f"Navigate to provider {r_provider} page")
                    print(f"Successfully navigated to provider page for provider: {r_provider}.")
                    config_assists.add_log_update(
                        message="Navigated to provider page for provider: " + r_provider,
                        driver=driver)

            elif user_role == "Office Admin Provider Delegate" or user_role == "Provider":
                config_assists.add_log_update(
                    message=f"{user_role} role detected, already on provider sidebar after login.",
                    driver=driver)




            config_assists.add_log_update(
                message=f"Navigated to {header_nav.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases",
                driver=driver)

            # Save the start url to navigate back to after each sidebar click
            start_url = header_nav.get_page_report()["CURRENT_URL"]

            config_assists.add_log_heartbeat("Starting sidebar validation for Provider Level Registries", driver=driver,
                                             status="STARTED")
            config_assists.add_log_heartbeat("Starting Test Case: Validate existence of default sidebar options",
                                             driver=driver, status="STARTED")

            # fetch the default sidebar options from header nav page.
            default_provider_sidebar_options = header_nav.PROVIDER_SIDEBAR_OPTIONS

            # Collect all sidebar options from the UI.
            sidebar_options = header_nav.fetch_sidebar_entries()

            # Compare the two lists and create two lists. One for new entries and one for missing entries compared to the default list.
            missing_entries = [entry for entry in default_provider_sidebar_options if entry not in sidebar_options]
            new_entries = [entry for entry in sidebar_options if entry not in default_provider_sidebar_options]

            if len(missing_entries) == 0:
                config_assists.add_log_test_case(message="TC_Validate existence of default sidebar options",
                                                 test_case_id="F_01_05",
                                                 status='PASSED', driver=driver,
                                                 comment="Entries on the sidebar : " + ", ".join(sidebar_options))
            else:  # Not exactly a failed case if there are missing entries, but we want to log it for visibility and investigation.
                config_assists.add_log_test_case(message="TC_Validate existence of default sidebar options",
                                                 test_case_id="F_01_05",
                                                 status='FAILED', driver=driver,
                                                 comment="Missing sidebar options compared to default: " + ", ".join(
                                                     missing_entries))

            if len(new_entries) > 0:
                config_assists.add_log_test_case(message="TC_Validate existence of default sidebar options",
                                                 test_case_id="F_01_05",
                                                 status='INFO', driver=driver,
                                                 comment="New sidebar options compared to default: " + ", ".join(
                                                     new_entries))

            config_assists.add_log_heartbeat(
                "Starting Test Case: Loop through each sidebar entry, click it, and verify page load",
                status="STARTED",
                driver=driver)

            # Now loop through each sidebar entry, click it, check for datatableinfo or some exception, handle it,
            # then navigate back to start url before clicking the next one

            for entry in sidebar_options:
                # To check a specific entry for testing,
                # if entry not in ["Payment Tool", "Export Dashboard"]:
                #     continue
                config_assists.add_log_heartbeat("Sidebar entry to be tested: " + entry,
                                                 driver=driver)
                print(f"Clicking on sidebar entry: {entry}")
                header_nav.click_sidebar_entry(entry)

                # time Calculation for page load after click
                start_time = time.perf_counter()
                header_nav.ajax_preloader_wait("After Entry Click Sidebar")
                time_taken_loader = f"{time.perf_counter() - start_time:.2f}"
                print(
                    f"Finished waiting for page load after clicking sidebar entry: {entry}. Time taken: {time_taken_loader} seconds")

                current_url = header_nav.get_page_report()["CURRENT_URL"]

                # These Sidebar pages all have datatables
                if entry not in ["Registries", "Reports", "Payment Tool", "Home"]:
                    if entry == "Export Dashboard":
                        header_nav.switch_tab(1)
                    data_table_info = header_nav.fetch_datatable_info()
                    time_taken = f"{time.perf_counter() - start_time:.2f}"

                    # Add datatableinfo check
                    if data_table_info:
                        print(f"Successfully navigated to new page after clicking sidebar entry: {entry}")
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_06",
                            status='PASSED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Data table info found: " + str(data_table_info))

                    else:
                        failed_cases += 1
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_06",
                            status='FAILED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Data table info not found after clicking sidebar entry: " + entry)
                    if entry == "Export Dashboard":
                        header_nav.switch_tab_and_close_current(0)

                elif entry == "Payment Tool":
                    # For Payment Tool, we can check for the presence of a unique element on the Payment
                    # Tool page to verify that the page has loaded correctly. If client does not have

                    payment_tool_page = CozevaPaymentToolPage(driver)
                    if payment_tool_page.is_payment_tool_page_open() != "Disabled":
                        cart_dict = payment_tool_page.fetch_payment_tool_cards_per_cycle()
                        time_taken = f"{time.perf_counter() - start_time:.2f}"
                        print(f"Successfully navigated to Payment Tool page. Fetched card info: {cart_dict}")
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_06",
                            status='PASSED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Payment Tool page opened and card info fetched: " + str(cart_dict))
                    elif payment_tool_page.is_payment_tool_page_open() == "Disabled":
                        print(
                            f"Payment Tool is not enabled for this client. Sidebar entry: {entry} leads to page with 'not enabled' message.")
                        time_taken = f"{time.perf_counter() - start_time:.2f}"
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_06",
                            status='PASSED',
                            driver=driver,
                            time_taken_ms=time_taken,
                            comment="Payment Tool is not enabled for this client, but appropriate message is displayed.")
                    else:
                        failed_cases += 1
                        print(f"Failed to navigate to Payment Tool page after clicking sidebar entry: {entry}")
                        config_assists.add_log_test_case(
                            message="Click on sidebar entry: " + entry + " and verify page load",
                            test_case_id="F_01_06",
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

            # return to start
            header_nav.navigate_to_url(rc.base_landing_url)
            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



        except Exception as e:
            print("Error in test_provider_sidebar:", e)
            traceback.print_exc()
            assert False, f"Test failed due to exception: {e}"





