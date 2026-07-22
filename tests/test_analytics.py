import datetime
import time
import traceback
import pytest
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.cozeva_analytics_page import AnalyticsLandingPage, AnalyticsWorksheetPage
from config.rtvsdb import RTVSDB
from core.helpers import Helpers as helpers


@pytest.mark.CozevaComboPack1
@pytest.mark.AnalyticsTestPackage
class TestAnalytics:
    """Test Landing Page of customer analytics to verify
    if worksheets are not missing and important sections are visible"""

    @pytest.mark.AnalyticsLandingPage
    def test_analytics_page(self, logged_in_driver, base_url, config_assists):

        failed_cases = 0
        worksheet_names = []
        actual_count = None
        expected_count = None

        db_client = RTVSDB()

        driver = logged_in_driver
        rc = config_assists.get_run_configuration()
        analytics_page = AnalyticsLandingPage(driver)
        customer_id = rc.client_id

        try:

            # ============================================================
            # TC : F_06_01 — Validate Analytics Page Load
            # ============================================================
            config_assists.add_log_start(
                message="F_06_01: Validate Analytics page load",
                driver=driver
            )

            start_time = time.perf_counter()

            analytics_page.open_analytics_page(driver, base_url, customer_id)

            is_loaded = analytics_page.is_loading_over()

            time_taken = f"{time.perf_counter() - start_time:.2f}"

            config_assists.add_log_heartbeat(
                message=f"Page load status : {'Loaded' if is_loaded else 'Did not load'} | Time : {time_taken}s | Customer ID : {customer_id}",
                driver=driver,
                status="Info"
            )

            if is_loaded:
                config_assists.add_log_test_case(
                    message="Validate Analytics page load",
                    test_case_id="F_06_01",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment=f"Analytics page loaded in {time_taken}s for Customer ID : {customer_id}"
                )
            else:
                failed_cases += 1
                config_assists.add_log_test_case(
                    message="Validate Analytics page load",
                    test_case_id="F_06_01",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment=f"Page did not load after {time_taken}s for Customer ID : {customer_id}"
                )
                config_assists.add_log_failed(
                    message=f"F_06_01: Page load timed out for Customer ID : {customer_id}",
                    driver=driver
                )

            config_assists.add_log_end(
                message="F_06_01: Validate Analytics page load",
                driver=driver,
                status="Success" if is_loaded else "Failed"
            )

            # ============================================================
            # TC : F_06_02 — Validate Recently Used Section
            # ============================================================
            config_assists.add_log_start(
                message="F_06_02: Validate Recently Used section",
                driver=driver
            )

            start_time = time.perf_counter()

            result = analytics_page.is_recently_used_displayed()

            time_taken = f"{time.perf_counter() - start_time:.2f}"

            tc_02_passed = result["section_visible"] and result["cards_visible"] > 0

            config_assists.add_log_heartbeat(
                message=f"Section visible : {result['section_visible']} | Cards found : {result['cards_visible']} | Time : {time_taken}s",
                driver=driver,
                status="Info"
            )

            if tc_02_passed:
                config_assists.add_log_test_case(
                    message="Validate Recently Used section",
                    test_case_id="F_06_02",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment=f"Section visible with {result['cards_visible']} card(s) displayed"
                )
            else:
                failed_cases += 1
                config_assists.add_log_test_case(
                    message="Validate Recently Used section",
                    test_case_id="F_06_02",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment=f"Section visible : {result['section_visible']} | Cards visible : {result['cards_visible']}"
                )
                config_assists.add_log_failed(
                    message=f"F_06_02: Recently Used section missing or no cards — section={result['section_visible']}, cards={result['cards_visible']}",
                    driver=driver
                )

            config_assists.add_log_end(
                message="F_06_02: Validate Recently Used section",
                driver=driver,
                status="Success" if tc_02_passed else "Failed"
            )

            # ============================================================
            # TC : F_06_04 — Validate Worksheet Count
            # ============================================================
            config_assists.add_log_start(
                message="F_06_04: Validate Worksheets count",
                driver=driver
            )

            expected_count = db_client.get_customer_worksheets(customer_id)

            start_time = time.perf_counter()

            actual_count = analytics_page.get_number_of_worksheets()

            time_taken = f"{time.perf_counter() - start_time:.2f}"

            if expected_count is None:
                db_client.ensure_customer_analytics_entry(customer_id, actual_count)
                expected_count = actual_count
                config_assists.add_log_heartbeat(
                    message=f"No prior baseline found — seeded expected count as {actual_count} for Customer ID : {customer_id}",
                    driver=driver,
                    status="Info"
                )
            else:
                config_assists.add_log_heartbeat(
                    message=f"Expected : {expected_count} | Actual : {actual_count} | Time : {time_taken}s",
                    driver=driver,
                    status="Info"
                )

            tc_04_passed = actual_count == expected_count

            if tc_04_passed:
                config_assists.add_log_test_case(
                    message="Validate Worksheets count",
                    test_case_id="F_06_04",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment=f"Worksheet count matched : {actual_count}"
                )
            else:
                failed_cases += 1
                config_assists.add_log_test_case(
                    message="Validate Worksheets count",
                    test_case_id="F_06_04",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment=f"Expected {expected_count} worksheets but found {actual_count}"
                )
                config_assists.add_log_failed(
                    message=f"F_06_04: Count mismatch — expected={expected_count}, actual={actual_count}",
                    driver=driver
                )

            config_assists.add_log_end(
                message="F_06_04: Validate Worksheets count",
                driver=driver,
                status="Success" if tc_04_passed else "Failed"
            )

            # ============================================================
            # TC : F_06_05 — Capture Worksheet Names
            # ============================================================
            config_assists.add_log_start(
                message="F_06_05: Capture Worksheet Names",
                driver=driver
            )

            start_time = time.perf_counter()

            worksheet_names = analytics_page.fetch_all_worksheet_names()

            time_taken = f"{time.perf_counter() - start_time:.2f}"

            config_assists.add_log_heartbeat(
                message=f"{len(worksheet_names)} worksheet(s) captured in {time_taken}s : {', '.join(worksheet_names)}",
                driver=driver,
                status="Info"
            )

            config_assists.add_log_test_case(
                message="Capture Worksheet Names",
                test_case_id="F_06_05",
                status="PASSED",
                driver=driver,
                time_taken_ms=time_taken,
                comment=f"{len(worksheet_names)} worksheet(s) found : {', '.join(worksheet_names)}"
            )

            config_assists.add_log_end(
                message="F_06_05: Capture Worksheet Names",
                driver=driver,
                status="Success"
            )

            assert failed_cases < 1, f"{failed_cases} test case(s) failed."

        except Exception as e:

            config_assists.add_log_error(
                message=f"Unhandled exception — {type(e).__name__} : {e}",
                driver=driver
            )
            config_assists.add_log_end(
                message=f"{rc.test_name} : Aborted due to exception",
                driver=driver,
                status="Failed"
            )

            traceback.print_exc()
            assert False, f"Test failed due to exception: {e}"

    def fetch_all_worksheet_names(self) -> list[str]:
        """
        Required by F_06_05

        Example:

        [
            "Quality Metrics",
            "Risk Metrics",
            "Cost Metrics"
        ]
        """
        print("[AnalyticsLandingPage] fetch_all_worksheet_names()")

        try:

            worksheets = self.driver.find_elements(
                *self.WORKSHEETS
            )

            return [
                worksheet.text.strip()
                for worksheet in worksheets
                if worksheet.text.strip()
            ]

        except Exception as e:

            print(
                "Error while fetching worksheet names:",
                str(e)
            )

            traceback.print_exc()

            return []

    def _dismiss_alert_if_present(self, driver):
        """Safely dismiss any open browser alert."""
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.dismiss()
            return alert_text
        except Exception:
            return None

    def _dismiss_alert_if_present(self, driver):
        """Safely dismiss any open browser alert."""
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.dismiss()
            return alert_text
        except Exception:
            return None

    def test_analytics_worksheets_for_current_year(
            self,
            logged_in_driver,
            base_url,
            config_assists):

        driver = logged_in_driver

        landing = AnalyticsLandingPage(driver)
        worksheet = AnalyticsWorksheetPage(driver)

        rc = config_assists.get_run_configuration()
        customer_id = rc.client_id
        final_result = {}
        not_processed=[]
        # ============================================================
        # Pre-requisite : Open Analytics Page
        # ============================================================
        landing.open_analytics_page(driver, base_url, customer_id)
        landing.is_loading_over()

        assert landing.is_loading_over(), \
            "Analytics page failed to load"

        worksheets = driver.find_elements(*landing.WORKSHEETS)
        total = len(worksheets)

        try:
            # worksheet selection part
            i = 0
            while i <total:
                # open worksheet
                try:
                    worksheets = driver.find_elements(*landing.WORKSHEETS)
                    worksheet_element = worksheets[i]
                    worksheet_name = worksheet_element.text.strip()
                    if worksheet_element is None:
                        raise Exception(f"Could not locate worksheet element at index {i}")
                    helpers.action_click(driver, worksheet_element)
                except Exception:
                    if worksheet_element is None:
                        worksheet_name = f"Worksheet_{i + 1}"
                    config_assists.add_log_error(
                        message=f"Could not open worksheet element at index {i} {worksheet_name}",
                        driver=driver
                    )
                    i += 1
                    continue

                worksheet_result = {
                    "year": None,
                    "drilldowns": [],
                    "has_lob_filter": False,
                    "lobs": []
                }

                no_data_list = []
                tc_passed = True
                skip_get_back = False

                # --------------------------------------------------------
                # Worksheet TC : Start
                # --------------------------------------------------------
                config_assists.add_log_start(
                    message=f"Validate {worksheet_name}",
                    driver=driver
                )

                try:
                    assert worksheet.is_loading_over(), \
                        f"Worksheet load failed : {worksheet_name}"

                    # ==========================================
                    # YEAR
                    # ==========================================
                    print(f"{worksheet_name} loaded")
                    if worksheet.does_year_filter_exist():
                        worksheet = AnalyticsWorksheetPage(driver)

                        status, result = worksheet.set_service_year("2026")

                        if status == 1:
                            worksheet_result["year"] = result  # result = "2026"
                            config_assists.add_log_heartbeat(
                                message=f"Year Filter | Set to {result}",
                                driver=driver,
                                status="Info"
                            )
                        elif status == 0 and result == "Already selected":
                            config_assists.add_log_heartbeat(
                                message=f"Year Filter | Already selected 2026",
                                driver=driver,
                                status="Info"
                            )
                        else:
                            config_assists.add_log_error(
                                message=f"Year Filter | Failed to set year",
                                driver=driver,
                                status="Error"
                            )
                    else:
                        worksheet_result["year"] = None
                        config_assists.add_log_heartbeat(
                            message=f"Year Filter | Not present on this worksheet",
                            driver=driver,
                            status="Info"
                        )

                    # ==========================================
                    # DRILLDOWNS
                    # ==========================================
                    has_drilldowns = worksheet.does_drilldown_exist()

                    if has_drilldowns:
                        try:
                            drilldown_names = worksheet.fetch_drilldown_names()
                            worksheet_result["drilldowns"] = drilldown_names
                            config_assists.add_log_heartbeat(
                                message=f"Drilldown | Discovered : {drilldown_names}",
                                driver=driver,
                                status="Info"
                            )
                        except Exception as e:
                            # Alert may have appeared during drilldown discovery
                            alert_text = self._dismiss_alert_if_present(driver)
                            raise Exception(f"Drilldown discovery failed | Alert: {alert_text} | Error: {e}")
                    else:
                        config_assists.add_log_heartbeat(
                            message=f"Drilldown | No drilldowns present on this worksheet",
                            driver=driver,
                            status="Info"
                        )

                    # ==========================================
                    # LOB ITERATION
                    # ==========================================
                    has_lob_filter = worksheet.does_lob_filter_exist()
                    worksheet_result["has_lob_filter"] = has_lob_filter

                    if has_lob_filter:
                        lob_values = worksheet.fetch_lob_values()
                        worksheet_result["lobs"] = lob_values
                        config_assists.add_log_heartbeat(
                            message=f"LOB | {len(lob_values)} value(s) found : {lob_values}",
                            driver=driver,
                            status="Info"
                        )

                        for lob in lob_values:
                            try:
                                worksheet.set_lob(lob)  # Alert can appear here
                            except Exception as e:
                                alert_text = self._dismiss_alert_if_present(driver)
                                raise Exception(f"set_lob({lob}) failed | Alert: {alert_text} | Error: {e}")

                            try:
                                if has_drilldowns:
                                    no_data_drilldowns = worksheet.execute_all_drilldowns()  # Alert here too

                                    for drilldown in no_data_drilldowns:
                                        no_data_list.append((
                                            worksheet_name,
                                            worksheet_result["year"],
                                            drilldown,
                                            lob
                                        ))
                            except Exception as e:
                                alert_text = self._dismiss_alert_if_present(driver)
                                raise Exception(
                                    f"execute_all_drilldowns() for LOB {lob} failed | Alert: {alert_text} | Error: {e}")
                    else:
                        config_assists.add_log_heartbeat(
                            message=f"LOB | No LOB filter present on this worksheet",
                            driver=driver,
                            status="Info"
                        )
                        if has_drilldowns:
                            try:
                                no_data_drilldowns = worksheet.execute_all_drilldowns()

                                for drilldown in no_data_drilldowns:
                                    no_data_list.append((
                                        worksheet_name,
                                        worksheet_result["year"],
                                        drilldown,
                                        ""
                                    ))
                            except Exception as e:
                                alert_text = self._dismiss_alert_if_present(driver)
                                raise Exception(f"execute_all_drilldowns() failed | Alert: {alert_text} | Error: {e}")
                        else:
                            try:
                                is_overview_no_data = worksheet.is_no_data_present()
                                if is_overview_no_data:
                                    no_data_list.append((
                                        worksheet_name,
                                        worksheet_result["year"],
                                        "OVERVIEW",
                                        ""
                                    ))
                            except Exception as e:
                                alert_text = self._dismiss_alert_if_present(driver)
                                raise Exception(f"is_no_data_present() check failed | Alert: {alert_text} | Error: {e}")

                    # ==========================================
                    # LOG & RESULT
                    # ==========================================
                    if no_data_list:
                        config_assists.add_log_error(
                            message=f"No data entries: {no_data_list}",
                            driver=driver
                        )
                        tc_passed = False

                    final_result[f"{i}_{worksheet_name}"] = worksheet_result

                    config_assists.add_log_test_case(
                        message=f"Validate {worksheet_name}",
                        test_case_id=f"WS_{i + 1:02}",
                        status="PASSED" if tc_passed else "FAILED",
                        driver=driver,
                        comment=f"No-data count: {len(no_data_list)}"
                    )

                    if not tc_passed:
                        config_assists.add_log_failed(
                            message=f"Validate {worksheet_name}",
                            driver=driver
                        )

                except Exception as ws_error:
                    # Catches all exceptions including those with alerts already dismissed
                    error_text = str(ws_error)
                    safe_error = (
                        error_text
                        .replace("\n", " ")
                        .replace("\r", " ")
                        .replace("<", "[")
                        .replace(">", "]")
                    )[:150]

                    # Double-check in case alert is still there
                    remaining_alert = self._dismiss_alert_if_present(driver)

                    config_assists.add_log_error(
                        message=f"Validate {worksheet_name} | {safe_error}"
                                + (f" | Remaining alert: '{remaining_alert}'" if remaining_alert else ""),
                        driver=driver
                    )

                    config_assists.add_log_skip(
                        message=f"Validate {worksheet_name} | Skipped due to error",
                        driver=driver
                    )

                    config_assists.add_log_test_case(
                        message=f"Validate {worksheet_name}",
                        test_case_id=f"WS_{i + 1:02}",
                        status="FAILED",
                        driver=driver,
                        comment="Error during execution"
                    )

                    tc_passed = False
                    skip_get_back = True
                    not_processed.append(f"{i}_{worksheet_name}")
                    landing.open_analytics_page(driver, base_url, customer_id)
                    landing.is_loading_over()

                    if not landing.is_loading_over():
                        config_assists.add_log_error(
                            message=f"Reload failed after error",
                            driver=driver
                        )

                finally:

                    if not skip_get_back:
                        try:
                            if not worksheet.get_back():
                                config_assists.add_log_error(
                                    message=f"get_back returned False | Forcing reload",
                                    driver=driver
                                )
                                landing.open_analytics_page(driver, base_url, customer_id)
                                landing.is_loading_over()
                        except Exception as gb_error:
                            config_assists.add_log_error(
                                message=f"get_back failed | {gb_error} | Forcing reload",
                                driver=driver
                            )
                            try:
                                landing.open_analytics_page(driver, base_url, customer_id)
                                landing.is_loading_over()
                            except Exception:
                                pass

                    config_assists.add_log_end(
                        message=f"Validate {worksheet_name}",
                        driver=driver,
                        status="Success" if tc_passed else "Failed"
                    )

                i += 1

            # ============================================================
            # Final Summary + Overall End
            # ============================================================
            # For debug purpose
            # config_assists.add_log_update(
            #     message=f"Analytics Worksheet Summary : {final_result}",
            #     driver=driver
            # )

            # Add unprocessed

            config_assists.add_log_end(
                message=f"{rc.test_name} - All worksheets processed",
                driver=driver,
                status="Success"
            )

            # Add unprocessed worksheets
            if len(final_result) == total :
                config_assists.add_log_heartbeat(
                    message=f"All worksheets processed successfully ",driver=driver )
            else:
                config_assists.add_log_heartbeat(message=f"Unprocessed worksheets due to execution error {not_processed} ",driver=driver)

        except Exception as e:

            traceback.print_exc()

            config_assists.add_log_error(
                message=f"Test aborted due to exception : {e}",
                driver=driver
            )
            config_assists.add_log_end(
                message=f"{rc.test_name} ended with an unhandled exception",
                driver=driver,
                status="Failed"
            )

            assert False, f"Test failed due to exception : {e}"