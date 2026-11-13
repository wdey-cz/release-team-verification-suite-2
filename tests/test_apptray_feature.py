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
from pages.cozeva_analytics_page import AnalyticsLandingPage
from pages.cozeva_bridge_page import CozevaBridgePage
from pages.cozeva_care_exchange_page import CozevaCareExchangePage
from pages.cozeva_case_management_page import CozevaCaseManagementPage
from pages.cozeva_chart_review_page import CozevaChartReviewPage
from pages.cozeva_config_tools_page import CozevaConfigToolsPage
from pages.cozeva_connect_page import CozevaConnectPage
from pages.cozeva_hedis_hybrid_page import CozevaHedisHybridPage
from pages.cozeva_query_automation_page import CozevaQueryAutomationPage
from pages.cozeva_secure_messaging_page import CozevaSecureMessagingPage
from pages.cozeva_support_tools_page import CozevaSupportToolsPage
from pages.cozeva_time_capsule_page import CozevaTimeCapsulePage


@pytest.mark.CozevaComboPack1
@pytest.mark.ApptrayTestPackage
class TestGeneralNavigations:

    """
    Feature: F_10_AppTray
    Test Cases - Apptray Options
    -- F_10_01 - Verify the apptray drowdown is available and displays options.
    -- F_10_02 - Verify the apptray options are clickable and navigate to the correct pages.
    """
    def test_apptray_options(self, logged_in_driver, base_url, config_assists):
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            user_role = rc.user_role
            rc.base_landing_url = driver.current_url
            failed_cases = 0

            # Load the header nav page for sidebar navigation functions
            header_nav = HeaderNavBar(driver)
            registries_page = CozevaRegistriesPage(driver)

            config_assists.add_log_update(
                message=f"Navigated to {header_nav.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases",
                driver=driver)

            # Save the start url to navigate back to after each sidebar click
            start_url = header_nav.get_page_report()["CURRENT_URL"]
            rc.test_page_url = start_url

            # Begin the test cases
            # Test Case F_10_01 : Verify the apptray dropdown is available and displays options.
            config_assists.add_log_update("Starting test case F_10_01: Verify the apptray dropdown is available and displays options.", driver=driver)
            apptray_visible, available_apptray_options = header_nav.open_apptray_dropdown()
            header_nav.ajax_preloader_wait("Clicking apptray dropdown")

            if apptray_visible:
                config_assists.add_log_test_case(
                    message="Verify the apptray dropdown is available and displays options.",
                    test_case_id="F_10_01",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Options visible on the apptray: "+str(available_apptray_options))
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray dropdown is available and displays options.",
                    test_case_id="F_10_01",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Apptray dropdown not visible or options not displayed.")
                failed_cases += 1

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_01: Verify the apptray dropdown is available and displays options.",
                driver=driver, )
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test case")

            # Test Case F_10_02 : Verify the apptray options are clickable and navigate to the correct pages.
            config_assists.add_log_update("Starting test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.", driver=driver)

            # OPTION : Analytics
            config_assists.add_log_update("Testing apptray option: Analytics", driver=driver)
            href_available = header_nav.click_apptray_analytics()
            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Analytics")

                analytics_page = AnalyticsLandingPage(driver)
                load_status = analytics_page.is_analytics_landing_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Analytics' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_01",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Analytics landing page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Analytics' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_01",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Analytics landing page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Analytics' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_01",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Analytics option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver, )
            if href_available:
                header_nav.switch_tab_and_close_current(0)
            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : Bridge
            config_assists.add_log_update("Testing apptray option: Bridge", driver=driver)
            href_available = header_nav.click_apptray_bridge()

            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Bridge")

                bridge_page = CozevaBridgePage(driver)
                load_status = bridge_page.is_bridge_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Bridge' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_02",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Bridge page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Bridge' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_02",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Bridge page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Bridge' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_02",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Bridge option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver,
            )
            if href_available:
                header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : Care Exchange
            config_assists.add_log_update("Testing apptray option: Care Exchange", driver=driver)
            href_available = header_nav.click_apptray_care_exchange()

            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Care Exchange")

                care_exchange_page = CozevaCareExchangePage(driver)
                load_status = care_exchange_page.is_care_exchange_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Care Exchange' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_03",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Care Exchange page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Care Exchange' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_03",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Care Exchange page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Care Exchange' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_03",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Care Exchange option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver,
            )
            if href_available:
                header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : Case Management
            config_assists.add_log_update("Testing apptray option: Case Management", driver=driver)
            href_available = header_nav.click_apptray_case_management()

            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Case Management")

                case_management_page = CozevaCaseManagementPage(driver)
                load_status = case_management_page.is_case_management_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Case Management' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_04",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Case Management page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Case Management' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_04",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Case Management page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Case Management' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_04",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Case Management option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver,
            )
            if href_available:
                header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : Chart Review
            config_assists.add_log_update("Testing apptray option: Chart Review", driver=driver)
            href_available = header_nav.click_apptray_chart_review()

            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Chart Review")

                chart_review_page = CozevaChartReviewPage(driver)
                load_status = chart_review_page.is_chart_review_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Chart Review' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_05",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Chart Review page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Chart Review' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_05",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Chart Review page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Chart Review' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_05",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Chart Review option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver,
            )
            if href_available:
                header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : Config Tools
            config_assists.add_log_update("Testing apptray option: Config Tools", driver=driver)
            href_available = header_nav.click_apptray_config_tools()

            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Config Tools")

                config_tools_page = CozevaConfigToolsPage(driver)
                load_status = config_tools_page.is_config_tools_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Config Tools' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_06",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Config Tools page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Config Tools' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_06",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Config Tools page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Config Tools' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_06",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Config Tools option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver,
            )
            if href_available:
                header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : Cozeva Connect
            config_assists.add_log_update("Testing apptray option: Cozeva Connect", driver=driver)
            href_available = header_nav.click_apptray_cozeva_connect()

            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Cozeva Connect")

                cozeva_connect_page = CozevaConnectPage(driver)
                load_status = cozeva_connect_page.is_cozeva_connect_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Cozeva Connect' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_07",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Cozeva Connect page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Cozeva Connect' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_07",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Cozeva Connect page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Cozeva Connect' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_07",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Cozeva Connect option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigates to the correct pages.",
                driver=driver,
            )
            if href_available:
                header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : HEDIS Hybrid
            config_assists.add_log_update("Testing apptray option: HEDIS Hybrid", driver=driver)
            href_available = header_nav.click_apptray_hedis_hybrid()

            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: HEDIS Hybrid")

                hedis_hydrid_page = CozevaHedisHybridPage(driver)
                load_status = hedis_hydrid_page.is_hedis_hybrid_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'HEDIS Hybrid' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_08",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="HEDIS Hybrid page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'HEDIS Hybrid' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_08",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="HEDIS Hybrid page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'HEDIS Hybrid' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_08",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="HEDIS Hybrid option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver,
            )
            if href_available:
                header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : Query Automation
            config_assists.add_log_update("Testing apptray option: Query Automation", driver=driver)
            href_available = header_nav.click_apptray_query_automation()

            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Query Automation")

                query_automation_page = CozevaQueryAutomationPage(driver)
                load_status = query_automation_page.is_query_automation_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Query Automation' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_09",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Query Automation page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Query Automation' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_09",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Query Automation page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Query Automation' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_09",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Query Automation option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver,
            )
            if href_available:
                header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : Registries
            # Additional flag for registries href cz we are using the apptray from registries itself, so a new tab wont open.
            # Write a function to fetch number of current tabs, and if its 1 tab after the click, then set a flag and dont swap tabs
            config_assists.add_log_update("Testing apptray option: Registries", driver=driver)
            href_available = header_nav.click_apptray_registries()
            header_nav.sleep_code(1) # wait for the page to load after click

            tab_count = len(driver.window_handles)

            if href_available:
                if tab_count > 1:
                    header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Registries")

                registries_page = CozevaRegistriesPage(driver)
                load_status = registries_page.is_registries_page_fully_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Registries' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_10",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Registries page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Registries' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_10",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Registries page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Registries' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_10",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Registries option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver,
            )
            if href_available:
                if tab_count > 1:
                    header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : Secure Messaging
            config_assists.add_log_update("Testing apptray option: Secure Messaging", driver=driver)
            href_available = header_nav.click_apptray_secure_messaging()

            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Secure Messaging")

                secure_messaging_page = CozevaSecureMessagingPage(driver)
                load_status = secure_messaging_page.is_secure_messaging_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Secure Messaging' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_11",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Secure Messaging page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Secure Messaging' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_11",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Secure Messaging page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Secure Messaging' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_11",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Secure Messaging option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver,
            )
            if href_available:
                header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : Support Tools
            config_assists.add_log_update("Testing apptray option: Support Tools", driver=driver)
            href_available = header_nav.click_apptray_support_tools()

            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Support Tools")

                support_tools_page = CozevaSupportToolsPage(driver)
                load_status = support_tools_page.is_support_tools_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Support Tools' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_12",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Support Tools page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Support Tools' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_12",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Support Tools page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Support Tools' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_12",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Support Tools option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver,
            )
            if href_available:
                header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")

            # OPTION : Time Capsule
            config_assists.add_log_update("Testing apptray option: Time Capsule", driver=driver)
            href_available = header_nav.click_apptray_time_capsule()

            if href_available:
                header_nav.switch_tab(1)
                header_nav.ajax_preloader_wait("Clicking apptray option: Time Capsule")

                time_capsule_page = CozevaTimeCapsulePage(driver)
                load_status = time_capsule_page.is_time_capsule_page_opened()

                if load_status:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Time Capsule' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_13",
                        status="PASSED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Time Capsule page loaded successfully.")
                else:
                    config_assists.add_log_test_case(
                        message="Verify the apptray option 'Time Capsule' is clickable and navigates to the correct page.",
                        test_case_id="F_10_02_13",
                        status="FAILED",
                        driver=driver,
                        time_taken_ms="",
                        comment="Time Capsule page did not load successfully.")
                    failed_cases += 1
            else:
                config_assists.add_log_test_case(
                    message="Verify the apptray option 'Time Capsule' is clickable and navigates to the correct page.",
                    test_case_id="F_10_02_13",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms="",
                    comment="Time Capsule option not available or LOCKED in apptray.")

            # reset
            config_assists.add_log_heartbeat(
                "finished test case F_10_02: Verify the apptray options are clickable and navigate to the correct pages.",
                driver=driver,
            )
            if href_available:
                header_nav.switch_tab_and_close_current(0)

            header_nav.navigate_to_url(rc.test_page_url)
            header_nav.ajax_preloader_wait("Reloading the page to reset for next test option")


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
