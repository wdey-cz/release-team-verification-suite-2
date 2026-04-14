import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By
import time
from random import choice

import pytest
import traceback


class CozevaRegistriesPage(BasePage):


    REGISTRIES_BASE_URL = "/registries?"

    HCC_LOBS = ['Medicare']

    #Locators
    REGISTRIES_KEBAB = (By.XPATH, "//a[@data-target='datatable_filter_dropdown_metric_scorecard']")
    REGISTRIES_KEBAB_EXPORT_ALL = (By.XPATH, "//a[@id='qt-export-reg-all']")
    REGISTRIES_DEEPLINK = (By.ID, "reg-qwb-trigger")

    LOB_DROPDOWN_CONTAINER = (By.ID, 'reg-filters')

    REGISTRIES_LOB_DROPDOWN = (By.ID, 'qt-filter-label')
    LOB_DROPDOWN_MEASUREMENT_YEARS = (By.XPATH, "//ul[@id='filter-quarter']/li")
    DEFAULT_MEASUREMENT_YEAR = (By.XPATH, "//ul[@id='filter-quarter']/li[contains(@class, 'highlight')]")

    LOB_DROPDOWN_LOBS = (By.XPATH, "//ul[@id='filter-lob']/li")
    DEFAULT_LOB = (By.XPATH, "//ul[@id='filter-lob']/li[contains(@class, 'highlight')]")

    LOB_APPLY = (By.ID, 'reg-filter-apply')

    # Summary Bar Locators
    SUMMARY_BAR = (By.XPATH, "//div[contains(@class, 'registry_header_panel')]")
    SUMMARY_GAP_COUNT = (By.ID, 'reg-header-gapcount')
    SUMMARY_OVERALL_RATING = (By.ID, 'reg-header-overall-rating')
    SUMMARY_PATIENT_COUNT = (By.XPATH, "//div[contains(@class, 'registry_header_panel')]//div[contains(@class, 'header-card-name') and contains(text(), 'Patients')]/following-sibling::div")

    SUMMARY_OVERALL_RATING_TREND_CHART_LAUNCHER = (By.ID, 'rating_chart')
    SUMMARY_OVERALL_RATING_TREND_CHART_RATING_INSIDE = (By.CLASS_NAME, "cms_star_val")
    SUMMARY_OVERALL_RATING_TREND_CHART = (By.XPATH, "//div[@id='cmsChart']")
    SUMMARY_OVERALL_RATING_TREND_CHART_NODES = (By.TAG_NAME, "circle")
    SUMMARY_OVERALL_RATING_TREND_CHART_CLOSE = (By.XPATH, "//div[contains(@class, 'close-btn')]")

    SUMMARY_HCC_SCORE = (By.XPATH, "//div[contains(@class, 'registry_header_panel')]//div[contains(text(), 'HCC')]/following-sibling::div")

    CONTINUOUS_ENROLLMENT_CHECKBOX = (By.XPATH, "//input[@id='conti_enroll']")

    REGISTRY_MEASURES_WITH_DOMAIN_GROUPS = (By.XPATH, "//div[@id='registry_body']//ul//li")
    MEASURE_NAME = (By.XPATH, ".//span[contains(@class, 'met-name')]")
    MEASURE_NUM_DEN = (By.XPATH, ".//span[contains(@class, 'num-den')]")
    METRIC_ID = (By.XPATH, ".//div[contains(@class, 'qt-metric')]")
    METRIC_ABBR = (By.XPATH, ".//span[contains(@class, 'met-abbr')]")
    DOMAIN_NAME = (By.XPATH, ".//span[contains(@class, 'domain-name')]")
    GROUP_NAME = (By.XPATH, ".//div[contains(@class, 'group-name-wrapper')]")

    FILTER_PANEL_SLIDEOUT = (By.XPATH, "//a[@data-target='qt-reg-nav-filters']")
    FILTER_PANEL_FULL_ELEMENT = (By.XPATH, "//ul[@id='qt-reg-nav-filters']")
    FILTER_PANEL_INPUT = (By.XPATH, "//input[@id='qt-search-met']")
    FILTER_PANEL_APPLY = (By.XPATH, "//button[@id='qt-apply-search']")

    @staticmethod
    def measure_by_metric_id(metric_id):
        return (By.XPATH, f"//div[@data-metricid='{metric_id}']")



    def __init__(self, driver):
        super().__init__(driver)

    def is_registries_page_opened(self):
        # Check the url contains the expected path
        if self.REGISTRIES_BASE_URL not in self.driver.current_url:
            print(f"Current URL does not contain expected path. Current URL: {self.driver.current_url}")
            return False
        return True

    def download_export_all_registries(self):
        try:
            self.click_element(self.REGISTRIES_KEBAB)
            time.sleep(1)  # Wait for the dropdown to open
            self.click_element(self.REGISTRIES_KEBAB_EXPORT_ALL)
            print("Clicked Export All option.")
        except Exception as e:
            print("Error during Export All click:", str(e))
            traceback.print_exc()

    def click_on_deeplink(self):
        try:
            self.click_element(self.REGISTRIES_DEEPLINK)
            print("Clicked on registries deeplink.")
        except Exception as e:
            print("Error during clicking on registries deeplink:", str(e))
            traceback.print_exc()

    def open_lob_dropdown(self):
        # Check if the container is visible, if not click the dropdown to open it
        try:
            container = self.find_element(self.LOB_DROPDOWN_CONTAINER, timeout=5)
            if container and container.is_displayed():
                print("LOB dropdown container is already visible.")
                return True
            else:
                print("LOB dropdown container is not visible. Attempting to open it...")
                self.click_element(self.REGISTRIES_LOB_DROPDOWN)
                time.sleep(1)  # Wait for dropdown to open
                # Check again if the container is visible after clicking
                container = self.find_element(self.LOB_DROPDOWN_CONTAINER, timeout=5)
                if container and container.is_displayed():
                    print("LOB dropdown container is now visible after clicking.")
                    return True
                else:
                    print("Failed to make LOB dropdown container visible after clicking.")
                    return False
        except Exception as e:
            print("Error while trying to open LOB dropdown:", str(e))
            traceback.print_exc()
            return False

    def fetch_my_and_lob(self):
        LoBs = []
        MYs= []
        try:
            self.open_lob_dropdown()  # Wait for dropdown to open

            # Fetch Measurement Years
            my_elements = self.find_elements(self.LOB_DROPDOWN_MEASUREMENT_YEARS, timeout=10)
            for elem in my_elements:
                MYs.append(elem.text.strip())

            # Fetch Default Measurement Year
            default_my_element = self.find_element(self.DEFAULT_MEASUREMENT_YEAR, timeout=10)
            default_my = default_my_element.text.strip() if default_my_element else "None"


            # Fetch LOBs
            lob_elements = self.find_elements(self.LOB_DROPDOWN_LOBS, timeout=10)
            for elem in lob_elements:
                LoBs.append(elem.text.strip())

            # Fetch Default LOB
            default_lob_element = self.find_element(self.DEFAULT_LOB, timeout=10)
            default_lob = default_lob_element.text.strip() if default_lob_element else "None"

            my_lob_dict = {'MY' : MYs, 'LOB' : LoBs}
            my_lob_default = {'MY' : default_my, 'LOB' : default_lob}


            # print("Fetched Measurement Years:", MYs)
            # print("Default Measurement Year:", default_my)
            # print("Fetched LOBs:", LoBs)
            # print("Default LOB:", default_lob)

            return my_lob_dict, my_lob_default

        except Exception as e:
            print("Error while fetching MYs and LOBs:", str(e))
            traceback.print_exc()

    def switch_lob(self, lob_name):
        # Click the dropdown to open it, select the given lobname, click apply.
        try:
            self.open_lob_dropdown()  # Wait for dropdown to open

            # Fetch LOBs
            lob_elements = self.find_elements(self.LOB_DROPDOWN_LOBS, timeout=10)
            for elem in lob_elements:
                if elem.text.strip() == lob_name:
                    elem.click()
                    print(f"Selected LOB: {lob_name}")
                    break
            else:
                print(f"LOB '{lob_name}' not found in dropdown options.")
                return

            # Click Apply
            self.click_element(self.LOB_APPLY)
            print("Clicked Apply after selecting LOB.")
            self.ajax_preloader_wait("Waiting for page to reload after switching to LOB: " + lob_name)

        except Exception as e:
            print("Error while switching LOB:", str(e))
            traceback.print_exc()

    def switch_my(self, year):
        # Click the dropdown to open it, select the given year, click apply.
        try:
            self.open_lob_dropdown()  # Wait for dropdown to open

            # Fetch Measurement Years
            my_elements = self.find_elements(self.LOB_DROPDOWN_MEASUREMENT_YEARS, timeout=10)
            for elem in my_elements:
                if elem.text.strip() == year:
                    elem.click()
                    print(f"Selected Measurement Year: {year}")
                    break
            else:
                print(f"Measurement Year '{year}' not found in dropdown options.")
                return

            # Click Apply
            self.click_element(self.LOB_APPLY)
            print("Clicked Apply after selecting Measurement Year.")
            self.ajax_preloader_wait("Waiting for page to reload after switching to Measurement Year: " + year)

        except Exception as e:
            print("Error while switching Measurement Year:", str(e))
            traceback.print_exc()

    def fetch_summary_bar_info(self):
        # This function returns a tuple with the gap count, overall rating and patient count from the summary bar
        try:
            gap_count_element = self.find_element(self.SUMMARY_GAP_COUNT, timeout=10)
            gap_count = gap_count_element.text.strip() if gap_count_element else "None"

            overall_rating_element = self.find_element(self.SUMMARY_OVERALL_RATING, timeout=10)
            overall_rating = overall_rating_element.text.strip() if overall_rating_element else "None"

            patient_count_element = self.find_element(self.SUMMARY_PATIENT_COUNT, timeout=10)
            patient_count = patient_count_element.text.strip() if patient_count_element else "None"

            print(f"Fetched Summary Bar Info - Gap Count: {gap_count}, Overall Rating: {overall_rating}, Patient Count: {patient_count}")
            return gap_count, overall_rating, patient_count
        except Exception as e:
            print("Error while fetching summary bar info:", str(e))
            traceback.print_exc()
            return "None", "None", "None"

    def launch_overall_rating_trend_chart(self):
        if self.is_trend_chart_opened():
            print("Overall Rating Trend Chart is already opened.")
            return
        try:
            self.click_element(self.SUMMARY_OVERALL_RATING_TREND_CHART_LAUNCHER)
            print("Clicked on Overall Rating Trend Chart launcher.")
            # Wait for the chart to be visible
            self.wait_helpers.wait_for_element_visible(self.SUMMARY_OVERALL_RATING_TREND_CHART, timeout=5)
            print("Overall Rating Trend Chart is now visible.")
        except Exception as e:
            print("Error while launching Overall Rating Trend Chart:", str(e))
            traceback.print_exc()

    def close_overall_rating_trend_chart(self):
        # check if open, then close
        if not self.is_trend_chart_opened():
            print("Overall Rating Trend Chart is not opened, no need to close.")
            return
        try:
            self.click_element(self.SUMMARY_OVERALL_RATING_TREND_CHART_CLOSE)
            print("Clicked on Overall Rating Trend Chart close button.")
            # Wait for the chart to be invisible
            self.wait_helpers.wait_for_element_invisible(self.SUMMARY_OVERALL_RATING_TREND_CHART, timeout=5)
            print("Overall Rating Trend Chart is now closed.")
        except Exception as e:
            print("Error while closing Overall Rating Trend Chart:", str(e))
            traceback.print_exc()

    def is_trend_chart_opened(self):
        try:
            chart = self.find_element(self.SUMMARY_OVERALL_RATING_TREND_CHART, timeout=2)
            if chart and chart.is_displayed():
                print("Overall Rating Trend Chart is open and visible.")
                return True
            else:
                print("Overall Rating Trend Chart element found but not visible.")
                return False
        except Exception as e:
            return False

    def fetch_overall_rating_trend_chart_data(self):
        try:
            if not self.is_trend_chart_opened():
                print("Overall Rating Trend Chart is not opened. Opening...")
                self.launch_overall_rating_trend_chart()
            chart = self.find_element(self.SUMMARY_OVERALL_RATING_TREND_CHART, timeout=5)
            if not chart:
                print("Overall Rating Trend Chart element not found, cannot fetch data.")
                return False
            rating = self.find_element(self.SUMMARY_OVERALL_RATING_TREND_CHART_RATING_INSIDE)
            rating_value = rating.text.strip() if rating else "None"
            print(f"Fetched Overall Rating from Trend Chart: {rating_value}")
            nodes = self.find_elements(self.SUMMARY_OVERALL_RATING_TREND_CHART_NODES, root=chart)
            node_count = len(nodes) if nodes else 0
            print(f"Fetched Overall Rating Trend Chart data. Number of nodes found: {node_count}")
            self.close_overall_rating_trend_chart()
            return rating_value, node_count
        except Exception as e:
            print("Error while fetching Overall Rating Trend Chart data:", str(e))
            traceback.print_exc()
            self.close_overall_rating_trend_chart()
            return False

    def fetch_hcc_score(self):
        try:
            hcc_score_element = self.find_element(self.SUMMARY_HCC_SCORE, timeout=10)
            hcc_score = hcc_score_element.text.strip() if hcc_score_element else "None"
            print(f"Fetched HCC Score from Summary Bar: {hcc_score}")
            return hcc_score
        except Exception as e:
            print("Error while fetching HCC Score from Summary Bar:", str(e))
            traceback.print_exc()
            return "None"

    def toggle_continuous_enrollment_checkbox(self, status = True):
        try:
            checkbox = self.find_element(self.CONTINUOUS_ENROLLMENT_CHECKBOX, timeout=10)
            if checkbox:
                is_checked = checkbox.is_selected()
                if is_checked != status:
                    self.click_element(self.CONTINUOUS_ENROLLMENT_CHECKBOX, timeout=1)
                    print(f"Continuous Enrollment checkbox toggled to {'checked' if status else 'unchecked'}.")
                    self.ajax_preloader_wait("Waiting for page to reload after toggling Continuous Enrollment checkbox.")
                else:
                    print(f"Continuous Enrollment checkbox is already in the desired state: {'checked' if status else 'unchecked'}.")
            else:
                print("Continuous Enrollment checkbox element not found.")
        except Exception as e:
            print("Error while toggling Continuous Enrollment checkbox:", str(e))
            traceback.print_exc()

    def fetch_num_den_from_registry(self, lob = None):
        """
            function to Fetch current num_den scores. Format below.
            {
                'Measure_name 1': {'METRIC_ID': a, 'DOMAIN_NAME': b, 'NUMERATOR': d,'DENOMINATOR': e, 'ABBR': f},
                'Measure_name 2': {'METRIC_ID': a, 'DOMAIN_NAME': b, 'NUMERATOR': d,'DENOMINATOR': e. 'ABBR': f},
                ...
            }
        """
        measure_data = {}
        if lob is not None:
            self.switch_lob(lob)

        all_li_tags = self.find_elements(self.REGISTRY_MEASURES_WITH_DOMAIN_GROUPS, timeout=10)
        current_domain = "Noners"
        for index, li_element in enumerate(all_li_tags):
            # We need to check if the li tag is a domain or group header or a measure. If it's a header, we will store the domain name and assign it to the measures until we hit another header.

            try:
                domain_name_element = self.find_element(self.DOMAIN_NAME, root=li_element, timeout=2)
                domain = True

            except Exception as e:
                domain = False
            try:
                group_name_element = self.find_element(self.GROUP_NAME, root=li_element, timeout=2)
                group = True

            except Exception:
                group = False
            if group:
                current_domain = group_name_element.text.strip()

            if group or domain:
                continue

            try:
                measure_name_element = self.find_element(self.MEASURE_NAME, root=li_element, timeout=2)
                metric_id_element = self.find_element(self.METRIC_ID, root=li_element, timeout=2)
                num_den_element = self.find_element(self.MEASURE_NUM_DEN, root=li_element, timeout=2)
                measure_abbr_element = self.find_element(self.METRIC_ABBR, root=li_element, timeout=2)

                if measure_name_element and metric_id_element and num_den_element and measure_abbr_element:
                    measure_name = measure_name_element.text.strip()
                    metric_id = metric_id_element.get_attribute("data-metricid").strip()
                    num_den_text = num_den_element.text.strip()

                    if '/' in num_den_text:
                        numerator, denominator = num_den_text.split('/')
                        numerator = numerator.strip()
                        denominator = denominator.strip()
                    else:
                        numerator = "None"
                        denominator = "None"

                    measure_abbr_text = measure_abbr_element.text.strip().replace('·', "")

                    #print(f"Fetched data for measure '{measure_name}' - Metric ID: {metric_id}, Domain: {current_domain if 'current_domain' in locals() else 'None'}, Numerator: {numerator}, Denominator: {denominator}")

                    measure_data[measure_name] = {
                        'METRIC_ID': metric_id,
                        'DOMAIN_NAME': current_domain,
                        'NUMERATOR': numerator,
                        'DENOMINATOR': denominator,
                        'ABBR': measure_abbr_text
                    }
            except Exception as e:
                print(f"Error while processing li element at index {index}:", str(e))
                # traceback.print_exc()

        # print(f"Fetched num/den data for measures under LOB '{lob}':", measure_data)
        return measure_data

    def fetch_measure_details(self, metric_id):
        # This function will find the measure with the given metric id and fetch details from the element. It will return the details as a dictionary.
        details = {}
        try:
            measure_element = self.find_element((self.measure_by_metric_id(metric_id)), timeout=10)
            if measure_element:
                measure_name_element = self.find_element(self.MEASURE_NAME, root=measure_element, timeout=2)
                # domain_name_element = self.find_element(self.DOMAIN_NAME, root=measure_element, timeout=2)
                num_den_element = self.find_element(self.MEASURE_NUM_DEN, root=measure_element, timeout=2)

                measure_name = measure_name_element.text.strip() if measure_name_element else "None"
                # domain_name = domain_name_element.text.strip() if domain_name_element else "None"
                num_den_text = num_den_element.text.strip() if num_den_element else "None"

                if '/' in num_den_text:
                    numerator, denominator = num_den_text.split('/')
                    numerator = numerator.strip()
                    denominator = denominator.strip()
                else:
                    numerator = "None"
                    denominator = "None"

                details = {
                    'MEASURE_NAME': measure_name,
                    'NUMERATOR': numerator,
                    'DENOMINATOR': denominator
                }
                print(f"Fetched details for measure with Metric ID '{metric_id}':", details)

        except Exception as e:
            print(f"Error while fetching details for measure with Metric ID '{metric_id}':", str(e))
            traceback.print_exc()

        return details

    def is_filter_panel_opened(self):
        try:
            panel = self.find_element(self.FILTER_PANEL_FULL_ELEMENT, timeout=2)
            if panel and panel.is_displayed():
                print("Filter panel is open and visible.")
                return True
            else:
                print("Filter panel element found but not visible.")
                return False
        except Exception as e:
            return False

    def open_filter_panel(self):
        if self.is_filter_panel_opened():
            print("Filter panel is already opened.")
            return
        try:
            self.click_element(self.FILTER_PANEL_SLIDEOUT)
            print("Clicked on Filter Panel slideout launcher.")
            # Wait for the panel to be visible
            self.wait_helpers.wait_for_element_visible(self.FILTER_PANEL_FULL_ELEMENT, timeout=5)
            print("Filter panel is now visible.")
        except Exception as e:
            print("Error while opening filter panel:", str(e))
            traceback.print_exc()

    def filter_by_measure_abbr(self, abbr):
        try:
            self.open_filter_panel()
            input_field = self.find_element(self.FILTER_PANEL_INPUT, timeout=5)
            if input_field:
                input_field.clear()
                input_field.send_keys(abbr)
                print(f"Entered '{abbr}' into filter panel input field.")
                self.click_element(self.FILTER_PANEL_APPLY)
                print("Clicked Apply on filter panel.")
                self.ajax_preloader_wait("Waiting for page to reload after applying measure abbreviation filter: " + abbr)
            else:
                print("Filter panel input field not found.")
        except Exception as e:
            print("Error while filtering by measure abbreviation:", str(e))
            traceback.print_exc()
















