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
@pytest.mark.PatientDashboardTestPackage
class TestPatientDashboard:

    @pytest.mark.PatientDashboard
    def test_patient_dashboard(self, logged_in_driver, base_url, config_assists):
        """
        Feature - F_04_PatientDashboard
        Test Cases -
            - F_04_01 : Validate Demographic information display for member
            - F_04_02 : Validate measures and gaps displayed on dashboard
            - F_04_03 : Validate pencil icon is visible for some measures
            - F_04_04 : Validate PCP name and attribution
            - F_04_05 : Validate patient history dropdown navigations
            - F_04_06 : Validate care team
            - F_04_07 : Validate patient active insurance cards
            - F_04_08 : Validate Preferred pharmacy

        There are a lot of ways to navigate to a patient dashboard, but for the sake of simplicity,
        we will navigagte to the patient dashboard via the registries page. We will select a random measure,
        then depending on the role, we will select a patient.

        Cozeva Support, Customer Support, Limited Cozeva Support will reach the support MSPL > Patients tab > Select random patient > click
        practice delegates, regional support will reach either the support mspl or the practice mspl, and they will have to go to the patients tab
        providers, provider delegates will use the provider registries, the patient list is default on there.


        """
        try:
            driver = logged_in_driver
            profile = getattr(driver, "_rtvs_profile", None)
            rc = config_assists.get_run_configuration()
            user_role = rc.user_role
            failed_cases = 0

            # Load pre_test_url for navigation after
            rc.base_landing_url = driver.current_url

            config_assists.add_log_update("Navigating to Registries page to select patient for Patient Dashboard testing", driver=driver,
                                         status="IN_PROGRESS")

            registries_page = CozevaRegistriesPage(driver)
            mspl_page = CozevaMSPLPage(driver)
            patient_dashboard_page = CozevaPatientDashboardPage(driver)


            if registries_page.is_registries_page_opened():

                my_lob_dict, default_dict = registries_page.fetch_my_and_lob()
                measures = registries_page.fetch_num_den_from_registry(default_dict['LOB'])
                random_measure = choice(list(measures.keys()))
                print("Clicking on random measure:", random_measure, "with Metric ID:",
                      measures[random_measure]['METRIC_ID'])
                registries_page.click_on_measure_by_metric_id(measures[random_measure]['METRIC_ID'])
                config_assists.add_log_update("Clicked on random measure: " + random_measure + " with Metric ID: " + str(measures[random_measure]['METRIC_ID']), driver=driver, status="IN_PROGRESS")
                registries_page.ajax_preloader_wait("Loading mspl for measure: " + random_measure)
                # mspl page is here, create mspl page object.

            if mspl_page.is_mspl_page_opened():
                mspl_page.click_on_random_patient()
                config_assists.add_log_update("Clicked on random patient from the patients tab in mspl page", driver=driver, status="IN_PROGRESS")
                mspl_page.switch_tab(1)
                mspl_page.ajax_preloader_wait("Loading patient dashboard after clicking on random patient in mspl page")

            # patient dashboard is here,
            if patient_dashboard_page.is_patient_dashboard_opened():
                config_assists.add_log_update("Patient dashboard opened successfully", driver=driver, status="PASSED")
                config_assists.add_log_heartbeat("Starting Regression on F_04_PatientDashboard", driver=driver,
                                                     status="STARTED")
                rc.test_page_url = driver.current_url
            else:
                config_assists.add_log_update("Failed to open patient dashboard after clicking on random patient in mspl page", driver=driver, status="FAILED")
                pytest.fail("Failed to open patient dashboard after clicking on random patient in mspl page")


            # F_04_01 : Validate Demographic information display for member
            config_assists.add_log_heartbeat("Starting test case F_04_01: Validate Demographic information display for member",
                                             driver=driver,
                                             status="STARTED")

            #demograpic info is returned by the func fetch_demographic_info looks like return 'Passed', demographic_info
            demographic_status, demographic_info = patient_dashboard_page.fetch_demographic_info()

            if demographic_status == "Passed":
                config_assists.add_log_test_case(
                    message= "Validate Demographic information display for member",
                    test_case_id="F_04_01",
                    status='PASSED',
                    driver=driver,
                    time_taken_ms=0,
                    comment = "Demographic information fetched successfully: "
                                + "\n CZ-ID: "+ str(demographic_info['cozeva_id'])
                                + "\n Name: " + str(demographic_info['name'])
                                + "\n DoB: " + str(demographic_info['dob'])
                                + "\n Gender: " + str(demographic_info['gender'])
                                + "\n Age: " + str(demographic_info['age']))
            else:
                config_assists.add_log_test_case(
                    message= "Validate Demographic information display for member",
                    test_case_id="F_04_01",
                    status='FAILED',
                    driver=driver,
                    time_taken_ms=0,
                    comment = "Failed to fetch some/all demographic information: "
                              + "\n CZ-ID: " + str(demographic_info['cozeva_id'])
                              + "\n Name: " + str(demographic_info['name'])
                              + "\n DoB: " + str(demographic_info['dob'])
                              + "\n Gender: " + str(demographic_info['gender'])
                              + "\n Age: " + str(demographic_info['age']))
                failed_cases += 1

            config_assists.add_log_heartbeat("finished test case F_04_01: Validate Demographic information display for member",)
            patient_dashboard_page.navigate_to_url(rc.test_page_url)
            patient_dashboard_page.ajax_preloader_wait("Reloading patient dashboard for next test case")

            # F_04_02 : Validate measures and gaps displayed on dashboard
            config_assists.add_log_heartbeat("Starting test case F_04_02: Validate measures and gaps displayed on dashboard",
                                             driver=driver,
                                             status="STARTED")

            # Record the gap count first
            gap_count = patient_dashboard_page.fetch_gaps()

            # Now we will fetch all quality + hcc measures, count red dots.
            quality_measures, hcc_measures = patient_dashboard_page.fetch_quality_measures(), patient_dashboard_page.fetch_hcc_measures()

            # quality_measures is a list of dicts. The "gap_status" key in each needs to be added if its "red_dot"
            red_dot_count_quality = sum(1 for measure in quality_measures if measure['gap_status'] == 'red_dot')

            # Do same for hcc measures
            red_dot_count_hcc = sum(1 for measure in hcc_measures if measure['gap_status'] == 'red_dot')

            # Add and compare - Make it a test case
            total_red_dots = red_dot_count_quality + red_dot_count_hcc

            if total_red_dots == gap_count:
                config_assists.add_log_test_case(
                    message= "Validate measures and gaps displayed on dashboard",
                    test_case_id="F_04_02",
                    status='PASSED',
                    driver=driver,
                    time_taken_ms=0,
                    comment = "Gap count matches red dot count: "
                                + "\n Gap Count: "+ str(gap_count)
                                + "\n Red Dot Count (Quality Measures): " + str(red_dot_count_quality)
                                + "\n Red Dot Count (HCC Measures): " + str(red_dot_count_hcc))
            else:
                config_assists.add_log_test_case(
                    message= "Validate measures and gaps displayed on dashboard",
                    test_case_id="F_04_02",
                    status='FAILED',
                    driver=driver,
                    time_taken_ms=0,
                    comment = "Gap count does NOT match red dot count: "
                              + "\n Gap Count: " + str(gap_count)
                              + "\n Red Dot Count (Quality Measures): " + str(red_dot_count_quality)
                              + "\n Red Dot Count (HCC Measures): " + str(red_dot_count_hcc))
                failed_cases += 1

            # reset
            config_assists.add_log_heartbeat("finished test case F_04_02: Validate measures and gaps displayed on dashboard",)
            patient_dashboard_page.navigate_to_url(rc.test_page_url)
            patient_dashboard_page.ajax_preloader_wait("Reloading patient dashboard for next test case")

            # F_04_03 : Validate pencil icon is visible for some measures
            config_assists.add_log_heartbeat("Starting test case F_04_03: Validate pencil icon is visible for some measures",
                                             driver=driver,
                                             status="STARTED")

            quality_measures, hcc_measures = patient_dashboard_page.fetch_quality_measures(), patient_dashboard_page.fetch_hcc_measures()

            # here we will count the number of times a key's value is "pencil_icon_present" = True.
            pencil_icon_count_quality = sum(1 for measure in quality_measures if measure['pencil_icon_present'] == True)
            pencil_icon_count_hcc = sum(1 for measure in hcc_measures if measure['pencil_icon_present'] == True)

            # we will have two test cases here. One for quality measures, one for hcc measures. We just want to validate that at least 1 pencil icon is present in either category, we dont know beforehand which measures will have pencil icons.

            if pencil_icon_count_quality > 0 or pencil_icon_count_hcc > 0:
                config_assists.add_log_test_case(
                    message= "Validate pencil icon is visible for some measures",
                    test_case_id="F_04_03",
                    status='PASSED',
                    driver=driver,
                    time_taken_ms=0,
                    comment = "Pencil icon is present for some measures: "
                                + "\n Pencil Icon Count (Quality Measures): " + str(pencil_icon_count_quality)
                                + "\n Pencil Icon Count (HCC Measures): " + str(pencil_icon_count_hcc))
            else:
                config_assists.add_log_test_case(
                    message= "Validate pencil icon is visible for some measures",
                    test_case_id="F_04_03",
                    status='FAILED',
                    driver=driver,
                    time_taken_ms=0,
                    comment = "Pencil icon is NOT present for any measures: "
                              + "\n Pencil Icon Count (Quality Measures): " + str(pencil_icon_count_quality)
                              + "\n Pencil Icon Count (HCC Measures): " + str(pencil_icon_count_hcc))
                failed_cases += 1

            #reset
            config_assists.add_log_heartbeat("finished test case F_04_03: Validate pencil icon is visible for some measures",)
            patient_dashboard_page.navigate_to_url(rc.test_page_url)
            patient_dashboard_page.ajax_preloader_wait("Reloading patient dashboard for next test case")


            # F_04_04 : Validate PCP name and attribution
            config_assists.add_log_heartbeat("Starting test case F_04_04: Validate PCP name and attribution",
                                             driver=driver,
                                             status="STARTED")

            pcp_attribution_data = patient_dashboard_page.perform_pcp_checks()

            """
            Data looks like this. We wil print the data in the test case comment for now, but ideally we would want to validate the data against some expected values. The expected values can be set in the test data based on the patient we select, or we can just validate that the data is present and in the correct format. For now, we will just log the data and mark the test case as passed if the data is present.
            {'pcp_name': 'ALL-INCLUSIVE COMMUNITY HEALTH CENTER-BU, ALL-INCLUSIVE COMMUNITY HEALTH CENTER ( 1093019051 )', 'pcp_hover': 'AltaMed IPA, HOLLYWOOD, ALL-INCLUSIVE COMMUNITY HEALTH CENTER', 'pcp_name_check': ('Passed', 'PCP Name is Present: ALL-INCLUSIVE COMMUNITY HEALTH CENTER-BU, ALL-INCLUSIVE COMMUNITY HEALTH CENTER ( 1093019051 )'), 'pcp_attribution_check': ('Passed', 'PCP Attribution on hover is present: AltaMed IPA, HOLLYWOOD, ALL-INCLUSIVE COMMUNITY HEALTH CENTER'), 'success': True, 'error': None}

            """

            if pcp_attribution_data['success'] == True:
                config_assists.add_log_test_case(
                    message= "Validate PCP name and attribution",
                    test_case_id="F_04_04",
                    status='PASSED',
                    driver=driver,
                    time_taken_ms=0,
                    comment = "PCP Name and Attribution are present: "
                                + "\n PCP Name: " + str(pcp_attribution_data['pcp_name'])
                                + "\n PCP Hover: " + str(pcp_attribution_data['pcp_hover'])
                                + "\n PCP Name Check: " + str(pcp_attribution_data['pcp_name_check'])
                                + "\n PCP Attribution Check: " + str(pcp_attribution_data['pcp_attribution_check']))
            else:
                config_assists.add_log_test_case(
                    message= "Validate PCP name and attribution",
                    test_case_id="F_04_04",
                    status='FAILED',
                    driver=driver,
                    time_taken_ms=0,
                    comment = "PCP Name and Attribution check failed: "
                              + "\n PCP Name: " + str(pcp_attribution_data['pcp_name'])
                              + "\n PCP Hover: " + str(pcp_attribution_data['pcp_hover'])
                              + "\n PCP Name Check: " + str(pcp_attribution_data['pcp_name_check'])
                              + "\n PCP Attribution Check: " + str(pcp_attribution_data['pcp_attribution_check'])
                              + "\n Error: " + str(pcp_attribution_data['error']))
                failed_cases += 1

            # reset
            config_assists.add_log_heartbeat("finished test case F_04_04: Validate PCP name and attribution",)
            patient_dashboard_page.navigate_to_url(rc.test_page_url)
            patient_dashboard_page.ajax_preloader_wait("Reloading patient dashboard for next test case")

            # F_04_05 : Validate patient history dropdown navigations
            config_assists.add_log_heartbeat("Starting test case F_04_05: Validate patient history dropdown navigations",
                                             driver=driver,
                                             status="STARTED")

            history_content = patient_dashboard_page.fetch_history_dropdown_names()
            for dropdown_option in history_content:
                patient_dashboard_page.click_history_dropdown_option(dropdown_option)
                patient_dashboard_page.ajax_preloader_wait("Loading patient history dropdown content for: " + dropdown_option)
                data_tableinfo = patient_dashboard_page.fetch_datatable_info()
                if data_tableinfo != None:
                    config_assists.add_log_test_case(
                        message= "Validate patient history dropdown navigations - " + dropdown_option,
                        test_case_id="F_04_05",
                        status='PASSED',
                        driver=driver,
                        time_taken_ms=0,
                        comment = "Data table info fetched successfully for dropdown option: " + dropdown_option
                                  + "\n Data Table Info: " + str(data_tableinfo))
                else:
                    config_assists.add_log_test_case(
                        message= "Validate patient history dropdown navigations - " + dropdown_option,
                        test_case_id="F_04_05",
                        status='FAILED',
                        driver=driver,
                        time_taken_ms=0,
                        comment = "Failed to fetch data table info for dropdown option: " + dropdown_option)
                    failed_cases += 1

            # reset
            config_assists.add_log_heartbeat("finished test case F_04_05: Validate patient history dropdown navigations",)
            patient_dashboard_page.navigate_to_url(rc.test_page_url)
            patient_dashboard_page.ajax_preloader_wait("Reloading patient dashboard for next test case")

            # F_04_06 : Validate care team



            if failed_cases == 0:
                config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
            else:
                config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)

            # return to start
            patient_dashboard_page.navigate_to_url(rc.base_landing_url)
            patient_dashboard_page.ajax_preloader_wait("Return to start")
            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



























        except Exception as e:
            traceback.print_exc()
            config_assists.add_log_update("An error occurred during the patient dashboard test setup: " + str(e), driver=driver, status="FAILED")
            assert False, "Test failed due to an exception: " + str(e)