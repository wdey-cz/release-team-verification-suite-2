import time
from random import choice

import pytest
import traceback
from core.helpers import Helpers
from pages.cozeva_analytics_page import CozevaQualityOverviewPage

from pages.cozeva_registries_page import CozevaRegistriesPage
from core.base_page import HeaderNavBar
from pages.cozeva_providers_page import CozevaProvidersPage

@pytest.mark.CozevaComboPack1
@pytest.mark.RegistriesTestPackage
class TestRegistries:

    @pytest.mark.SupportRegistries
    def test_support_registries(self, logged_in_driver, base_url, config_assists):
        """
        Feature - F_02_Registries
        Test Cases -
         F_02_01: Validate that the Analytics Deeplink button navigates to the analytics app
         F_02_02: Validate Gaps are visible on summary bar for all LoBs
         F_02_03: Validate Overall Rating are visible on summary bar for all LoBs
         F_02_04: Validate Patient count is visible on summary bar for all LoBs
         F_02_05: Validate the Overall Rating Trend chart for relevant lobs
         F_02_06: Validate Summary HCC score for relevant lobs
         F_02_07: Validate Continous Enrollment checkbox alters num/den counts
         F_02_08: Validate chicklets / stars with exceptions
         F_02_09: Validate Quality/HCC Measure display on registries contains all elements.
         F_02_10: Validate registries filter
         F_02_11: Validate Accordion summation for all Lobs
         F_02_12: Validate number of 0/0 measures on all Lobs against a previously stored list LoB wise.
         F_02_13: Validate registry export
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

            # Load pre_test_url for navigation after
            rc.base_landing_url = driver.current_url

            header_nav = HeaderNavBar(driver)

            config_assists.add_log_update(
                message=f"Navigated to {header_nav.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases",
                driver=driver)

            config_assists.add_log_heartbeat("Starting Regression on F_02_Registries", driver=driver,
                                             status="STARTED")
            registries_page = CozevaRegistriesPage(driver)

            # F_02_01 : Validate that the Analytics Deeplink button navigates to the analytics app
            config_assists.add_log_heartbeat("Starting test case F_02_01: Validate Analytics Deeplink button", driver=driver,
                                             status="STARTED")
            registries_page.click_on_deeplink()

            # Switch tab
            registries_page.switch_tab(1)
            config_assists.add_log_update(
                message="Switched to new tab after clicking on Analytics Deeplink button",
                driver=driver)

            # Check quality overview page is opened
            quality_overview_page = CozevaQualityOverviewPage(driver)
            if quality_overview_page.is_quality_overview_page_opened() == "OPEN":
                config_assists.add_log_test_case(
                    message="Validate Analytics Deeplink button",
                    test_case_id="F_02_01",
                    status='PASSED', driver=driver,
                    comment="Clicked on Analytics deeplink and Quality Overview page opened successfully in a new tab, deeplink seems to be working fine.")
            elif quality_overview_page.is_quality_overview_page_opened() == "NOT_OPEN":
                config_assists.add_log_test_case(
                    message="Validate Analytics Deeplink button",
                    test_case_id="F_02_01",
                    status='FAILED', driver=driver,
                    comment="Clicked on Analytics deeplink but Quality Overview page did not open successfully, deeplink seems to be broken.")
                failed_cases += 1
            elif quality_overview_page.is_quality_overview_page_opened() == "LOADING_ISSUE":
                config_assists.add_log_test_case(
                    message="Validate Analytics Deeplink button",
                    test_case_id="F_02_01",
                    status='FAILED', driver=driver,
                    comment="Clicked on Analytics deeplink but there was an issue with loading the Quality Overview page, cannot verify if deeplink is working or not.")
                failed_cases += 1

            # Switch back to original tab
            registries_page.switch_tab_and_close_current(0)
            config_assists.add_log_heartbeat("Finished test case F_02_01: Validate Analytics Deeplink button",
                                             driver=driver,
                                             status="FINISHED")
            registries_page.navigate_to_url(rc.base_landing_url)

            # F_02_02 : Validate Gaps are visible on summary bar for all LoBs
            # F_02_03 : Validate Overall Rating are visible on summary bar for all LoBs
            # F_02_04 : Validate Patient count is visible on summary bar for all LoBs
            """
                Above three cases will be merged into one. Switch lob and check for these three elements.
            """
            config_assists.add_log_heartbeat("Started test case F_02_02,03,04: Validate Gaps, Overall Rating and Patient count visibility on summary bar for all LoBs",
                                             driver=driver,
                                             status="STARTED")

            my_lob_dict, default_dict = {'MY' : [], 'LOB' : []}, {'MY' : [], 'LOB' : []}
            if registries_page.is_registries_page_opened():
                my_lob_dict, default_dict = registries_page.fetch_my_and_lob()

            # now, we will loop through the Lobs.
            for lob in my_lob_dict['LOB']:
                registries_page.switch_lob(lob)
                registries_page.sleep_code(2)  # Wait for page to load after switching lob

                config_assists.add_log_heartbeat("Switched to " + lob + " Lob for test case F_02_02,03,04: Validate Gaps, Overall Rating and Patient count visibility on summary bar for all LoBs",)

                # Here you would add the code to validate the presence of Gaps, Overall Rating and Patient count on the summary bar for the current lob.
                # This would likely involve checking for specific elements on the page and verifying their visibility and content.
                gap_count, overall_rating, patient_count = registries_page.fetch_summary_bar_info()

                # Gap count validation
                if gap_count != "None":
                    config_assists.add_log_test_case(
                        message=f"Validate Gap Count visibility on summary bar for {lob} LOB",
                        test_case_id="F_02_02",
                        status='PASSED', driver=driver,
                        comment=f"Gap Count is visible on summary bar for {lob} LOB with value: {gap_count}.")
                else:
                    config_assists.add_log_test_case(
                        message=f"Validate Gap Count visibility on summary bar for {lob} LOB",
                        test_case_id="F_02_02",
                        status='FAILED', driver=driver,
                        comment=f"Gap Count is not visible on summary bar for {lob} LOB, it seems to be broken.")
                    failed_cases += 1

                # Overall Rating validation
                if overall_rating != "None":
                    config_assists.add_log_test_case(
                        message=f"Validate Overall Rating visibility on summary bar for {lob} LOB",
                        test_case_id="F_02_03",
                        status='PASSED', driver=driver,
                        comment=f"Overall Rating is visible on summary bar for {lob} LOB with value: {overall_rating}.")
                else:
                    config_assists.add_log_test_case(
                        message=f"Validate Overall Rating visibility on summary bar for {lob} LOB",
                        test_case_id="F_02_03",
                        status='FAILED', driver=driver,
                        comment=f"Overall Rating is not visible on summary bar for {lob} LOB, it seems to be broken.")
                    failed_cases += 1

                # Patient Count validation
                if patient_count != "None":
                    config_assists.add_log_test_case(
                        message=f"Validate Patient Count visibility on summary bar for {lob} LOB",
                        test_case_id="F_02_04",
                        status='PASSED', driver=driver,
                        comment=f"Patient Count is visible on summary bar for {lob} LOB with value: {patient_count}.")
                else:
                    config_assists.add_log_test_case(
                        message=f"Validate Patient Count visibility on summary bar for {lob} LOB",
                        test_case_id="F_02_04",
                        status='FAILED', driver=driver,
                        comment=f"Patient Count is not visible on summary bar for {lob} LOB, it seems to be broken.")
                    failed_cases += 1

            # Finish test case and navigate back to base URL
            config_assists.add_log_heartbeat("Finished test case F_02_02,03,04: Validate Gaps, Overall Rating and Patient count visibility on summary bar for all LoBs",
                                             driver=driver,
                                             status="FINISHED")
            registries_page.navigate_to_url(rc.base_landing_url)



            # F_02_05 : Validate the Overall Rating Trend chart for relevant lobs
            '''
            Overall Rating trend chart is currently only present for specific lobs defined by a list.
            We will fetch all lobs, then loop through the common ones. 
            Currenty, Only Medicare Lob.
            '''

            config_assists.add_log_heartbeat("Starting test case F_02_05: Validate the Overall Rating Trend chart for relevant lobs", driver=driver,status="STARTED")

            my_lob_dict, default_dict = {'MY': [], 'LOB': []}, {'MY': [], 'LOB': []}
            if registries_page.is_registries_page_opened():
                my_lob_dict, default_dict = registries_page.fetch_my_and_lob()

            if "Medicare" in my_lob_dict['LOB']:
                registries_page.switch_lob("Medicare")
                registries_page.sleep_code(2)  # Wait for page to load after switching lob
                config_assists.add_log_update("Switched to Medicare Lob for test case F_02_05: Validate the Overall Rating Trend chart for relevant lobs", driver=driver)

                # one to check that the chart is visible and and one to check if it has data in it.
                registries_page.launch_overall_rating_trend_chart()
                if registries_page.is_trend_chart_opened():
                    config_assists.add_log_test_case(
                        message=f"Validate Overall Rating Trend chart launch for Medicare LOB",
                        test_case_id="F_02_05",
                        status='PASSED', driver=driver,
                        comment=f"Overall Rating Trend chart launched successfully for Medicare LOB.")

                else:
                    config_assists.add_log_test_case(
                        message=f"Validate Overall Rating Trend chart launch for Medicare LOB",
                        test_case_id="F_02_05",
                        status='FAILED', driver=driver,
                        comment=f"Overall Rating Trend chart did not launch for Medicare LOB, it seems to be broken.")
                    failed_cases += 1


                chart_overall_rating, chart_nodes = registries_page.fetch_overall_rating_trend_chart_data()
                registries_rating = registries_page.fetch_summary_bar_info()[1]  # Fetching overall rating from summary bar for comparison

                if chart_overall_rating == registries_rating and chart_nodes > 0:
                    config_assists.add_log_test_case(
                        message=f"Validate Overall Rating Trend chart data for Medicare LOB",
                        test_case_id="F_02_05",
                        status='PASSED', driver=driver,
                        comment=f"Overall Rating Trend chart data seems to be correct for Medicare LOB with Overall Rating: {chart_overall_rating} and Nodes count: {chart_nodes}.")
                else:
                    config_assists.add_log_test_case(
                        message=f"Validate Overall Rating Trend chart data for Medicare LOB",
                        test_case_id="F_02_05",
                        status='FAILED', driver=driver,
                        comment=f"Overall Rating Trend chart data seems to be incorrect for Medicare LOB. Chart Overall Rating: {chart_overall_rating}, Summary Bar Overall Rating: {registries_rating} and Nodes count: {chart_nodes}.")
                    failed_cases += 1

            else:
                config_assists.add_log_update("Medicare Lob is not present, skipping test case F_02_05: Validate the Overall Rating Trend chart for relevant lobs", driver=driver,)

            config_assists.add_log_heartbeat("Finished test case F_02_05: Validate the Overall Rating Trend chart for relevant lobs", driver=driver,status="FINISHED")
            registries_page.navigate_to_url(rc.base_landing_url)

            # F_02_06 : Validate Summary HCC score for relevant lobs
            '''
            Similar to Overall Rating Trend chart, Summary HCC score is also only present for some lobs. 
            We will fetch all lobs, then loop through the common ones. 
            '''
            config_assists.add_log_heartbeat("Starting test case F_02_06: Validate Summary HCC score for relevant lobs", driver=driver,
                                             status="STARTED")
            my_lob_dict, default_dict, hcc_lobs = {'MY': [], 'LOB': []}, {'MY': [], 'LOB': []}, []
            if registries_page.is_registries_page_opened():
                my_lob_dict, default_dict = registries_page.fetch_my_and_lob()
                hcc_lobs = registries_page.HCC_LOBS

            # make a list of commons between hcc_lobs and my_lob_dict['LOB']
            common_hcc_lobs = list(set(hcc_lobs) & set(my_lob_dict['LOB']))
            for lob in common_hcc_lobs:
                registries_page.switch_lob(lob)
                registries_page.sleep_code(2)  # Wait for page to load after switching lob
                config_assists.add_log_update("Switched to " + lob + " Lob for test case F_02_06: Validate Summary HCC score for relevant lobs",)

                hcc_score = registries_page.fetch_hcc_score()
                if hcc_score != "None":
                    config_assists.add_log_test_case(
                        message=f"Validate Summary HCC score visibility on summary bar for {lob} LOB",
                        test_case_id="F_02_06",
                        status='PASSED', driver=driver,
                        comment=f"Summary HCC score is visible on summary bar for {lob} LOB with value: {hcc_score}.")
                else:
                    config_assists.add_log_test_case(
                        message=f"Validate Summary HCC score visibility on summary bar for {lob} LOB",
                        test_case_id="F_02_06",
                        status='FAILED', driver=driver,
                        comment=f"Summary HCC score is not visible on summary bar for {lob} LOB, it seems to be broken.")
                    failed_cases += 1

            config_assists.add_log_heartbeat("Finished test case F_02_06: Validate Summary HCC score for relevant lobs", driver=driver,)
            registries_page.navigate_to_url(rc.base_landing_url)

            # F_02_07 : Validate Continous Enrollment checkbox alters num/den counts
            ''' 
            For this case, we will check on the Default Lob. We will fetch the num/den counts with checkbox unchecked, then check the checkbox and fetch the counts again.
            We will validate that the counts have changed after checking the checkbox.
            '''
            config_assists.add_log_heartbeat("Starting test case F_02_07: Validate Continous Enrollment checkbox alters num/den counts", driver=driver,
                                             status="STARTED")
            if registries_page.is_registries_page_opened():
                my_lob_dict, default_dict = registries_page.fetch_my_and_lob()
                if default_dict['LOB']:
                    default_lob = default_dict['LOB'][0]
                    registries_page.switch_lob(default_lob)
                    registries_page.sleep_code(2)  # Wait for page to load after switching lob
                    config_assists.add_log_update("Switched to default Lob: " + default_lob + " for test case F_02_07: Validate Continous Enrollment checkbox alters num/den counts", driver=driver)

                    old_scores = registries_page.fetch_num_den_from_registry("Medicare")
                    registries_page.toggle_continuous_enrollment_checkbox(True)
                    new_scores = registries_page.fetch_num_den_from_registry()

                    # Now we will compare the old and new scores and count how many measures have changed in numerator and denominator.
                    changed_scores = {}
                    for measure_name, measure_data in new_scores.items():
                        if measure_name in old_scores:
                            old_measure_data = old_scores[measure_name]
                            if measure_data['NUMERATOR'] != old_measure_data['NUMERATOR'] or measure_data[
                                'DENOMINATOR'] != old_measure_data['DENOMINATOR']:
                                changed_scores[measure_name] = {
                                    'OLD_NUMERATOR': old_measure_data['NUMERATOR'],
                                    'NEW_NUMERATOR': measure_data['NUMERATOR'],
                                    'OLD_DENOMINATOR': old_measure_data['DENOMINATOR'],
                                    'NEW_DENOMINATOR': measure_data['DENOMINATOR']
                                }
                    print(
                        f"Total measures with changed scores after toggling continuous enrollment: {len(changed_scores)}")


                    if len(changed_scores) > 0:
                        config_assists.add_log_test_case(
                            message=f"Validate Continous Enrollment checkbox alters num/den counts for {default_lob} LOB",
                            test_case_id="F_02_07",
                            status='PASSED', driver=driver,
                            comment=f"Continuous Enrollment checkbox alters num/den counts for {default_lob} LOB, total measures with changed scores: {len(changed_scores)}.")
                    else:
                        config_assists.add_log_test_case(
                            message=f"Validate Continous Enrollment checkbox alters num/den counts for {default_lob} LOB",
                            test_case_id="F_02_07",
                            status='FAILED', driver=driver,
                            comment=f"Continuous Enrollment checkbox does not alter num/den counts for {default_lob} LOB, it seems to be broken.")
                        failed_cases += 1

                    config_assists.add_log_heartbeat("Finished test case F_02_07: Validate Continous Enrollment checkbox alters num/den counts", driver=driver,)
                    registries_page.navigate_to_url(rc.base_landing_url)


                else:
                    config_assists.add_log_update("No default Lob found, skipping test case F_02_07: Validate Continous Enrollment checkbox alters num/den counts", driver=driver,)

            # F_02_08 : Validate chicklets / stars with exceptions
            config_assists.add_log_heartbeat("Starting test case F_02_08: Validate chicklets / stars with exceptions", driver=driver,)
            """
            To Validate this test case, we will validate chicklets/stars on the registries. (DO THIS LATER!!)
            """
            config_assists.add_log_heartbeat("Finished test case F_02_08: Validate chicklets / stars with exceptions", driver=driver,)
            registries_page.navigate_to_url(rc.base_landing_url)

            # F_02_09 : Validate Quality/HCC Measure display on registries contains all elements.
            """
            Here, we will look for a random metric, and then validate its values are visible on the UI.
            """
            config_assists.add_log_heartbeat("Starting test case F_02_09: Validate Quality/HCC Measure display on registries contains all elements", driver=driver,)
            scores = registries_page.fetch_num_den_from_registry()
            random_measure = choice(list(scores.keys()))
            random_metric_id = scores[random_measure]['METRIC_ID']
            print(f"Randomly selected measure: {random_measure} with metric ID: {random_metric_id}")
            config_assists.add_log_update("Randomly selected measure: " + random_measure + " with metric ID: " + random_metric_id + " for test case F_02_09: Validate Quality/HCC Measure display on registries contains all elements", driver=driver,)


            details = registries_page.fetch_measure_details(random_metric_id)
            # Example Format {'MEASURE_NAME': 'Medication Review', 'NUMERATOR': '2,625', 'DENOMINATOR': '5,090'}

            if details and details['NUMERATOR'] != "None" and details['DENOMINATOR'] != "None":
                config_assists.add_log_test_case(
                    message=f"Validate Quality/HCC Measure display on registries contains all elements for {random_measure}",
                    test_case_id="F_02_09",
                    status='PASSED', driver=driver,
                    comment=f"Quality/HCC Measure details are displayed correctly for {random_measure} with Numerator: {details['NUMERATOR']} and Denominator: {details['DENOMINATOR']}.")
            else:
                config_assists.add_log_test_case(
                    message=f"Validate Quality/HCC Measure display on registries contains all elements for {random_measure}",
                    test_case_id="F_02_09",
                    status='FAILED', driver=driver,
                    comment=f"Quality/HCC Measure details are not displayed correctly for {random_measure}, it seems to be broken.")
                failed_cases += 1

            config_assists.add_log_heartbeat("Finished test case F_02_09: Validate Quality/HCC Measure display on registries contains all elements", driver=driver,)
            registries_page.navigate_to_url(rc.base_landing_url)

            # F_02_10 : Validate registries filter
            config_assists.add_log_heartbeat("Starting test case F_02_10: Validate registries filter", driver=driver,)
            """
            To validate this test case, we will apply a filter on the registries page and then check if the results are
            consistent with the applied filter. For example, if we apply a filter for a specific measure, we should only see that measure in the results.
            """
            if registries_page.is_registries_page_opened():
                my_lob_dict, default_dict = registries_page.fetch_my_and_lob()
                scores = registries_page.fetch_num_den_from_registry(lob=default_dict['LOB'])
                random_measure = choice(list(scores.keys()))
                print(f"Randomly selected measure: {random_measure} for filter validation")
                config_assists.add_log_update("Randomly selected measure: " + random_measure + " for filter validation", driver=driver,)
                abbr = scores[random_measure]['ABBR']
                registries_page.filter_by_measure_abbr(abbr)
                filtered_measures = registries_page.fetch_num_den_from_registry()

                # Now we check that the randomly selected measure is present in the filtered results and that the numerator and denominator match
                if random_measure in filtered_measures:
                    print(f"Measure {random_measure} is present in the filtered results.")
                    if (filtered_measures[random_measure]['NUMERATOR'] == scores[random_measure]['NUMERATOR'] and
                            filtered_measures[random_measure]['DENOMINATOR'] == scores[random_measure]['DENOMINATOR']):
                        print("Numerator and Denominator values match for the filtered measure.")
                        config_assists.add_log_test_case(
                            message=f"Validate registries filter for {random_measure}",
                            test_case_id="F_02_10",
                            status='PASSED', driver=driver,
                            comment=f"Registries filter seems to be working fine for {random_measure}, Numerator and Denominator values match for the filtered measure."
                        )
                    else:
                        print("Numerator and Denominator values do NOT match for the filtered measure.")
                        config_assists.add_log_test_case(
                            message=f"Validate registries filter for {random_measure}",
                            test_case_id="F_02_10",
                            status='FAILED', driver=driver,
                            comment=f"Registries filter seems to be broken for {random_measure}, Numerator and Denominator values do NOT match for the filtered measure."
                        )
                        failed_cases += 1
                else:
                    print(f"Measure {random_measure} is NOT present in the filtered results.")
                    config_assists.add_log_test_case(
                        message=f"Validate registries filter for {random_measure}",
                        test_case_id="F_02_10",
                        status='FAILED', driver=driver,
                        comment=f"Registries filter seems to be broken for {random_measure}, measure is NOT present in the filtered results."
                    )
                    failed_cases += 1

            config_assists.add_log_heartbeat("Finished test case F_02_10: Validate registries filter", driver=driver,)
            registries_page.navigate_to_url(rc.base_landing_url)

            # F_02_11 : Validate Accordion summation for all Lobs
            '''
            For this test case, we will expand all accordions on the registries page and then validate that the summation of the numerator and denominator values in the expanded accordions matches the numerator
            '''
            config_assists.add_log_heartbeat("Starting test case F_02_11: Validate Accordion summation for all Lobs", driver=driver,)

            config_assists.add_log_heartbeat("Finished test case F_02_11: Validate Accordion summation for all Lobs", driver=driver,)
            registries_page.navigate_to_url(rc.base_landing_url)

            # F_02_13
            config_assists.add_log_heartbeat("Starting test case F_02_13: Validate registry export", driver=driver,
                                             status="STARTED")
            if registries_page.is_registries_page_opened():
                print("Registries page opened successfully. Now attempting to click Export All option in kebab menu...")
                registries_page.download_export_all_registries()
                print("Clicked Export All option. Waiting for 2 seconds to observe any potential issues...")
                time.sleep(2)
            else:
                print("Registries page did not open successfully. Current URL:", driver.current_url)

            # Check if the downloaded file has any data in it
            downloaded_file = Helpers.fetch_downloaded_file(rc.lane_id)
            if downloaded_file:
                config_assists.add_log_update(f"Downloaded file {downloaded_file}", driver=driver,
                                                 status="INFO")
                if Helpers.does_file_have_data(downloaded_file):
                    config_assists.add_log_test_case(
                        message="Validate registry export",
                        test_case_id="F_02_13",
                        status='PASSED', driver=driver,
                        comment=f"Downloaded file {downloaded_file} has data in it, registry export seems to be working fine.")
                    Helpers.delete_file(downloaded_file)
                else:
                    config_assists.add_log_test_case(
                        message="Validate registry export",
                        test_case_id="F_02_13",
                        status='FAILEd', driver=driver,
                        comment=f"Downloaded file {downloaded_file} is empty, registry export seems to be broken.")
                    failed_cases += 1
                    Helpers.delete_file(downloaded_file)
                    config_assists.add_log_update(f"Deleted file {downloaded_file}", driver=driver,
                                                     status="INFO")
            else:
                config_assists.add_log_test_case(
                    message="Validate registry export",
                    test_case_id="F_02_13",
                    status='FAILED', driver=driver,
                    comment=f"No file was downloaded after clicking Export All, registry export seems to be broken.")
                failed_cases += 1

            config_assists.add_log_heartbeat("Finished test case F_02_13: Validate registry export", driver=driver,
                                             status="FINISHED")
            registries_page.navigate_to_url(rc.base_landing_url)



            if failed_cases == 0:
                config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
            else:
                config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)

            # return to start
            header_nav.navigate_to_url(rc.base_landing_url)
            header_nav.ajax_preloader_wait("Return to start")
            assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



        except Exception as e:
            traceback.print_exc()
            failed_cases += 1




