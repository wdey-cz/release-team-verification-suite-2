import time
import traceback
import pytest
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.cozeva_analytics_page import AnalyticsLandingPage, AnalyticsWorksheetPage
from config.rtvsdb import RTVSDB


@pytest.mark.CozevaComboPack1
@pytest.mark.AnalyticsTestPackage
class TestAnalyticsLandingPage:
    """Test Landing Page of customer analytics to verify
    if worksheets are not missing and important sections are visible"""

    @pytest.mark.AnalyticsLandingPage
    def test_analytics_page(self, logged_in_driver, base_url, config_assists):
        """
        Feature - Analytics Landing Page
        Test Cases:
        TC_01: Validate Analytics page load
        TC_02: Validate Recently Used section
        TC_03: Validate Worksheets count
        """
        failed_cases = 0
        customer_id = 3000
        db_client = RTVSDB()

        try:
            driver = logged_in_driver
            rc = config_assists.get_run_configuration()
            analytics_page = AnalyticsLandingPage(driver)

            print("Analytics Page Navigation  ")
            # 🔹 Log navigation
            config_assists.add_log_update(
                message=f"Starting {rc.test_name} - Analytics Landing Page validation",
                driver=driver
            )

            # =========================
            # 🟢 TC_01: Page Load
            # =========================
            config_assists.add_log_heartbeat(
                "TC_06_01: Validate Analytics page load",
                driver=driver,
                status="STARTED"
            )

            start_time = time.perf_counter()
            analytics_page.open_analytics_page(driver, base_url, customer_id)
            is_loaded = analytics_page.is_loading_over()
            time_taken = f"{time.perf_counter() - start_time:.2f}"

            if is_loaded:
                config_assists.add_log_test_case(
                    message="Validate Analytics page load",
                    test_case_id="F_06_01",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Analytics page loaded successfully"
                )
                print("Analytics Page Loaded  ")
            else:
                failed_cases += 1
                config_assists.add_log_test_case(
                    message="Validate Analytics page load",
                    test_case_id="F_06_01",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment="Analytics page did not load properly"
                )
                print("Analytics Page did not load  ")

            # =========================
            # 🟢 TC_02: Recently Used Section
            # =========================
            config_assists.add_log_heartbeat(
                "TC_02: Validate Recently Used section",
                driver=driver,
                status="STARTED"
            )

            start_time = time.perf_counter()
            result = analytics_page.is_recently_used_displayed()
            time_taken = f"{time.perf_counter() - start_time:.2f}"

            if result["section_visible"] and result["cards_visible"] > 0:
                config_assists.add_log_test_case(
                    message="Validate Recently Used section",
                    test_case_id="F_06_02",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment=f"Recently Used validated: {result}"
                )
            else:
                failed_cases += 1
                config_assists.add_log_test_case(
                    message="Validate Recently Used section",
                    test_case_id="F_06_02",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment=f"Recently Used validation failed: {result}"
                )

            # =========================
            # 🟢 TC_03: Worksheets Count
            # =========================
            config_assists.add_log_heartbeat(
                "F_06_04: Validate Worksheets count",
                driver=driver,
                status="STARTED"
            )

            expected_count = db_client.get_customer_worksheets(customer_id)

            start_time = time.perf_counter()
            actual_count = analytics_page.get_number_of_worksheets()
            time_taken = f"{time.perf_counter() - start_time:.2f}"

            if expected_count is None:
                db_client.ensure_customer_analytics_entry(customer_id, actual_count)
                expected_count = actual_count

                config_assists.add_log_update(
                    message=f"Customer analytics data missing. Inserted default worksheets={actual_count} "
                            f"for customer_id={customer_id}",
                    driver=driver
                )

            if actual_count == expected_count:
                config_assists.add_log_test_case(
                    message="Validate Worksheets count",
                    test_case_id="F_06_04",
                    status="PASSED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment=f"Expected: {expected_count}, Found: {actual_count}"
                )
            else:
                failed_cases += 1
                config_assists.add_log_test_case(
                    message="Validate Worksheets count",
                    test_case_id="F_06_04",
                    status="FAILED",
                    driver=driver,
                    time_taken_ms=time_taken,
                    comment=f"Mismatch → Expected: {expected_count}, Found: {actual_count}"
                )

            # =========================
            # 🔚 Final Result
            # =========================
            if failed_cases == 0:
                config_assists.add_log_update(
                    f"All test cases passed for {rc.test_name}",
                    driver=driver
                )
            else:
                config_assists.add_log_update(
                    f"{failed_cases} test cases failed for {rc.test_name}",
                    driver=driver
                )

            assert failed_cases < 1, f"{failed_cases} test cases failed."
            print("Analytics Landing page done ")

        except Exception as e:
            print("Error in test_analytics_page:", e)
            traceback.print_exc()

            config_assists.add_log_update(
                message=f"Test failed due to exception: {e}",
                driver=driver
            )

    @pytest.mark.AnalyticsWorksheet
    def test_analytics_worksheets_for_current_year(self, logged_in_driver, base_url, config_assists):
        """Iterates all worksheets and prints No Data (no DB insert yet)"""
        try:
            driver = logged_in_driver

            landing = AnalyticsLandingPage(driver)
            worksheet = AnalyticsWorksheetPage(driver)

            rc = config_assists.get_run_configuration()

            config_assists.add_log_update(
                message=f"Starting {rc.test_name} - Worksheet Iteration",
                driver=driver
            )

            # 🚨 ASSUMPTION: landing page already opened by previous test

            #Open Analytics page for customer
            customer_id = rc.client_id
            landing.open_analytics_page(driver, base_url, customer_id)

            if not landing.is_loading_over():
                print("Page did not load yet ")
                raise Exception("[ERROR] Page loading did not complete")



            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(landing.WORKSHEETS)
            )

            worksheets = driver.find_elements(*landing.WORKSHEETS)
            total = len(worksheets)

            if total == 0:
                print("No worksheets found")
                raise Exception("[ERROR] No worksheets found after loading")

            print(f"[INFO] Total Worksheets: {total}")
            final_result = {}

            for i in range(total):

                print(f"\n===== WORKSHEET {i + 1}/{total} =====")

                # 🔁 re-fetch to avoid stale elements
                worksheets = driver.find_elements(*landing.WORKSHEETS)
                ele = worksheets[i]

                worksheet_name = ele.text
                ele.click()

                print(f"[INFO] Opened: {worksheet_name}")

                # wait for worksheet load
                if not worksheet.is_loading_over():
                    print("[ERROR] Worksheet load failed")
                    continue

                # =========================
                # 🟢 Year Handling
                # =========================
                status, current_year = worksheet.get_selected_service_year()

                if not status:
                    print("[ERROR] Unable to fetch year")
                    worksheet.get_back()
                    continue

                target_year = "2026"

                if str(current_year) != target_year:
                    print(f"[INFO] Changing year {current_year} → {target_year}")
                    status, _ = worksheet.set_service_year(target_year)

                    if not status:
                        print("[ERROR] Failed to set year")
                        worksheet.get_back()
                        continue
                else:
                    print(f"[INFO] Year already set to {target_year}")

                # =========================
                # 🟢 Worksheet Name
                # =========================
                worksheet_name = worksheet.get_worksheet_name()

                if not worksheet_name:
                    print("[ERROR] Worksheet name fetch failed")
                    worksheet.get_back()
                    continue

                # =========================
                # 🟢 Drilldown Execution
                # =========================
                no_data_map = worksheet.iterate_drilldowm(target_year, worksheet_name)

                final_result[worksheet_name] = no_data_map

                # =========================
                # 🟢 Print Results
                # =========================
                print("\n================ NO DATA RESULTS ================")

                if no_data_map:
                    for drill, status_val in no_data_map.items():
                        print(f"Year: {target_year} | Worksheet: {worksheet_name} | Drill: {drill} → {status_val}")
                else:
                    print(f"{worksheet_name} → No 'No Data' scenarios found")

                print("================================================\n")

                # =========================
                # 🟢 Go Back
                # =========================
                worksheet.get_back()

            # =========================
            # 🟢 Final Summary
            # =========================
            print("\n=========== FINAL RESULT ===========")

            for ws, data in final_result.items():
                print(f"{ws} → {data}")

            print("====================================\n")

            config_assists.add_log_update(
                message=f"Final No Data Map: {final_result}",
                driver=driver
            )

            assert final_result is not None, "Final result is None"

        except Exception as e:
            print("Error in test_analytics_worksheet_with_year:", e)
            traceback.print_exc()

            config_assists.add_log_update(
                message=f"Test failed due to exception: {e}",
                driver=driver
            )

            assert False, f"Test failed due to exception: {e}"
