import traceback

from core.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException
import time
from random import choice

import pytest
import traceback

class CozevaPatientDashboardPage(BasePage):

    # Locators
    COZEVA_ID = (By.XPATH, "//span[@data-tooltip='Cozeva Id (Click to Copy)']")
    NAME = (By.XPATH, "//div[contains(@id, 'patient_header_compact')]")
    GENDER = (By.XPATH, "//span[contains(@class, 'gender')]")
    DOB = (By.XPATH, "//span[contains(@class, 'dob')]")
    AGE = (By.XPATH, "//span[contains(@class, 'age ')]")

    PATIENT_NAME_HEADER = (By.XPATH, "//a[contains(@data-target, 'patient_header_dropdown_compact')]")
    PATIENT_INFORMATION = (By.XPATH, "//a[contains(@class, 'contacts_n_eligibility_new_tab')]")
    PATIENT_HISTORY_DROPDOWN = (By.XPATH, "//li[@id='history']")
    PATIENT_HISTORY_DROPDOWN_OPTIONS = (By.XPATH, "//li[@id='history']//ul[@class='patient_submenu']//li/a")

    PATIENT_INFORMATION_CARE_TEAM = (By.XPATH,
                                     "//span[contains(@data-once, 'pointer_link_trigger') and contains(text(), 'Care Team')]")
    PATIENT_INFORMATION_CARE_TEAM_CONTENTS = (By.XPATH, "//div[@id='visits' and contains(@class, 'section scrollspy clearfix')]//div[contains(@class, 'mlm')]//span[contains(@class, 'care_team_doc')]")

    PATIENT_INFORMATION_COVERAGE = (By.XPATH, "//span[contains(@data-once, 'pointer_link_trigger') and contains(text(), 'Coverage')]")
    PATIENT_INFORMATION_COVERAGE_CARDS = (By.XPATH, "//div[@id='payment_section' and contains(@class, 'section scrollspy clearfix')]//div[contains(@class, 'card_wrapper')]")


    # PCP and Attribution Locators
    MORE_INFO_HEADER = (By.CLASS_NAME, "more_info_header")
    PCP_NAME = (By.XPATH, "//span[@id='pcp_name']")
    PCP_NAME_BY_ID = (By.ID, "pcp_name")

    #GAP_COUNT = (By.XPATH, "//div[contains(@class, 'child secondelem')]")
    GAP_COUNT = (By.XPATH, "//div[contains(concat(' ', normalize-space(@class), ' '), ' right_border ') and contains(concat(' ', normalize-space(@class), ' '), ' child ') and contains(@data-tooltip, 'Total gap count')]")

    #HCC measures table locator
    HCC_MEASURES = (By.XPATH, "//div[@id='table_4']")
    HCC_ROW = (By.XPATH, ".//div[contains(@class, 'hcc_row ')]")

    # HCC_ROW element
    HCC_GAP_RED_DOT = (By.XPATH, ".//div[contains(@class, 'red_dot ')]")
    HCC_GAP_NO_DOT = (By.XPATH, ".//div[contains(@class, 'no_dot ')]")
    HCC_GAP_HOLLOW_DOT = (By.XPATH, ".//div[contains(@class, 'hollow_dot ')]")
    HCC_DX_DESCRIPTION = (By.XPATH, ".//div[contains(@class, 'dx_description ')]")
    HCC_PENCIL_ICON = (By.XPATH, ".//div[contains(@class, 'pencil_icon ')]")
    HCC_PENCIL_ICON_DROP_OPTIONS = (By.XPATH, ".//ul/li/a") # this will have to be a find elements and then loop list get text.

    # Quality measures table locators
    QUALITY_MEASURES = (By.XPATH, "//div[@id='table_1']")
    QUALITY_ROW = (By.XPATH, ".//div[contains(@class, 'row-group row')]")
    QUALITY_RED_DOT = (By.XPATH, ".//div[contains(@class, 'non_compliant red_dot')]")
    QUALITY_DESCRIPTION = (By.XPATH, ".//span[@class='faq_field']")
    QUALITY_PENCIL_ICON = (By.XPATH, ".//a[@data-tooltip='Add Supplemental Data']")
    QUALITY_MARK_AS_PENDING = (By.XPATH, ".//div[@data-tooltip='Mark as Pending']")




    def __init__(self, driver):
        super().__init__(driver)

    def is_patient_dashboard_opened(self):
        try:
            return self.is_element_visible(self.NAME)
        except Exception as e:
            print("Error in checking if Patient Dashboard page is opened:", str(e))
            traceback.print_exc()
            return False

    # PCP and Attribution relatedmethods
    def click_more_info_header(self, timeout=2):
        """Click the more info header if it's clickable."""
        try:
            time.sleep(1)
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(self.MORE_INFO_HEADER)
            )
            self.click_element(self.MORE_INFO_HEADER)
            print("More info header clicked successfully.")
            return True
        except TimeoutException:
            return False
        except Exception as e:
            print(f"Error clicking more info header: {str(e)}")
            traceback.print_exc()
            return False

    def get_pcp_name(self):
        """Get the PCP name text."""
        try:
            return self.get_text(self.PCP_NAME)
        except Exception as e:
            print(f"Error getting PCP name: {str(e)}")
            traceback.print_exc()
            return None

    def get_pcp_hover_tooltip(self):
        """Get the PCP hover tooltip (data-tooltip attribute)."""
        try:
            return self.get_element_attribute(self.PCP_NAME_BY_ID, "data-tooltip")
        except Exception as e:
            print(f"Error getting PCP hover tooltip: {str(e)}")
            traceback.print_exc()
            return None

    def check_pcp_name(self, pcp_name):
        """
        Check PCP name and return status with message.
        Returns: tuple (status, message)
            status: 'Passed' or 'Failed'
            message: description of the result
        """
        if pcp_name == '-':
            return ('Failed', "PCP Name is Blank")
        elif pcp_name == "N/A":
            return ('Failed', "PCP Name is NA")
        elif pcp_name == "NO PCP":
            return ('Passed', "PCP Name is No PCP")
        elif pcp_name:
            return ('Passed', f"PCP Name is Present: {pcp_name}")
        else:
            return ('Failed', "PCP Name is not present/Not interactable")

    def check_pcp_attribution_on_hover(self, pcp_hover, pcp_name):
        """
        Check PCP attribution on hover and return status with message.
        Returns: tuple (status, message)
            status: 'Passed' or 'Failed'
            message: description of the result
        """
        # Check if it's NO PCP case with N/A attribution
        if (pcp_hover == "N/A, N/A, No Practice" or
            pcp_hover == "N/A, N/A, N/A" or
            ("N/A" in pcp_hover and pcp_name == "NO PCP")):
            return ('Passed', "No region panel attribution since its no PCP")

        # Check for missing region/panel attribution
        elif pcp_hover == "N/A, N/A, No Practice" or pcp_hover == "N/A, N/A, No PRACTICE":
            return ('Failed', "PCP does not have Region/Panel Attribution")

        # Check for no attribution at all
        elif pcp_hover == "N/A, N/A, N/A":
            return ('Failed', "PCP does not have any attribution")

        # Attribution is present
        elif pcp_hover:
            return ('Passed', f"PCP Attribution on hover is present: {pcp_hover}")

        else:
            return ('Failed', "PCP hover tooltip is not present")

    def perform_pcp_checks(self):
        """
        Perform all PCP related checks and return results.
        Returns: dict with keys:
            - 'pcp_name': the PCP name value
            - 'pcp_hover': the PCP hover tooltip value
            - 'pcp_name_check': tuple (status, message) for PCP name check
            - 'pcp_attribution_check': tuple (status, message) for attribution check
            - 'success': boolean indicating if all checks were successful
            - 'error': error message if any exception occurred
        """
        result = {
            'pcp_name': None,
            'pcp_hover': None,
            'pcp_name_check': None,
            'pcp_attribution_check': None,
            'success': False,
            'error': None
        }

        try:
            # Click more info header if available
            self.click_more_info_header()

            # Get PCP name
            pcp_name = self.get_pcp_name()
            result['pcp_name'] = pcp_name

            # Get PCP hover tooltip
            pcp_hover = self.get_pcp_hover_tooltip()
            result['pcp_hover'] = pcp_hover

            # Perform PCP name check
            if pcp_name is not None:
                result['pcp_name_check'] = self.check_pcp_name(pcp_name)
                print(f"PCP Name Check: {result['pcp_name_check'][1]}")
            else:
                result['pcp_name_check'] = ('Failed', "PCP Name is not present/Not interactable")
                print("PCP Name is not present/Not interactable")

            # Perform PCP attribution check
            if pcp_hover is not None and pcp_name is not None:
                result['pcp_attribution_check'] = self.check_pcp_attribution_on_hover(pcp_hover, pcp_name)
                print(f"PCP Attribution Check: {result['pcp_attribution_check'][1]}")
            else:
                result['pcp_attribution_check'] = ('Failed', "PCP hover tooltip is not present")
                print("PCP hover tooltip is not present")

            result['success'] = True

        except Exception as e:
            print(f"Error performing PCP checks: {str(e)}")
            traceback.print_exc()
            result['error'] = str(e)
            result['pcp_name_check'] = ('Failed', "PCP Name is not present/Not interactable")
            result['pcp_attribution_check'] = ('Failed', "PCP hover check failed due to error")

        return result

    # Demographic info related methods
    def fetch_demographic_info(self):
        """
        Fetch demographic information such as Cozeva ID, Name, dob, age, and gender. return a tuple -  dictionary with the demographic info, PASSED or FAILED status based on whats visible.
        """
        try:
            demographic_info = {}
            demographic_info['cozeva_id'] = self.get_text(self.COZEVA_ID).replace("·", "").strip()
            demographic_info['name'] = self.get_text(self.NAME).replace("·", "").strip()
            demographic_info['gender'] = self.get_text(self.GENDER).replace("·", "").strip()
            demographic_info['dob'] = self.get_text(self.DOB).replace("·", "").strip()
            demographic_info['age'] = self.get_text(self.AGE).replace("·", "").strip()

            # Check if all demographic info is present
            if all(demographic_info.values()):
                print("Demographic info fetched successfully:", demographic_info)
                return 'Passed', demographic_info
            else:
                print("Some demographic info is missing:", demographic_info)
                return 'Failed', demographic_info,
        except Exception as e:
            print(f"Error fetching demographic info: {str(e)}")
            traceback.print_exc()
            return 'Failed', demographic_info

    # Gaps and measures related methods
    def fetch_gaps(self):
        """
        Fetch the gaps count from the dashboard. return gap count.
        """
        try:
            gap_count_text = self.get_text(self.GAP_COUNT).strip()
            gap_count = int(gap_count_text)  # Convert to integer
            print(f"Gap count fetched successfully: {gap_count}")
            return gap_count
        except Exception as e:
            print(f"Error fetching gap count: {str(e)}")
            traceback.print_exc()
            return None

    def fetch_hcc_measures(self):
        """
        Fetch the HCC measures from the dashboard.
        We will return a list of dictionaries with the measure description, gap status (red dot, no dot, hollow dot) and pencil icon options if present.
        use find_elements and find element for anything that needs root element. Get text and click dont support root=
        """
        try:
            measures = []
            hcc_table = self.find_element(self.HCC_MEASURES)
            hcc_rows = self.find_elements(self.HCC_ROW, root=hcc_table)
            for row in hcc_rows:
                measure_info = {}
                options = []
                measure_info['description'] = self.find_element(self.HCC_DX_DESCRIPTION, root=row).text.strip()
                if self.is_element_visible(self.HCC_GAP_RED_DOT, root=row, timeout=2):
                    measure_info['gap_status'] = 'red_dot'
                elif self.is_element_visible(self.HCC_GAP_NO_DOT, root=row, timeout=2):
                    measure_info['gap_status'] = 'no_dot'
                elif self.is_element_visible(self.HCC_GAP_HOLLOW_DOT, root=row, timeout=2):
                    measure_info['gap_status'] = 'hollow_dot'
                else:
                    measure_info['gap_status'] = 'unknown'
                measure_info['pencil_icon_present'] = self.is_element_visible(self.HCC_PENCIL_ICON, root=row)
                if measure_info['pencil_icon_present']:
                    pencil_element = self.find_element(self.HCC_PENCIL_ICON, root=row)
                    self.scroll_to_view(pencil_element)
                    self.click_element(pencil_element)
                    options = self.find_elements(self.HCC_PENCIL_ICON_DROP_OPTIONS, root=pencil_element)
                    measure_info['pencil_icon_options'] = [option.text.strip() for option in options]
                    # self.click_element(self.find_element(self.HCC_PENCIL_ICON, root=row))

                measures.append(measure_info)
            print("HCC measures fetched successfully:", measures)
            return measures
        except Exception as e:
            print(f"Error fetching HCC measures: {str(e)}")
            traceback.print_exc()
            return []

    def fetch_quality_measures(self):
        """
        Fetch the quality measures from the dashboard.
        We will return a list of dictionaries with the measure description, gap status (red dot or no dot), map present, pencil icon present.
        use find_elements and find element for anything that needs root element. Get text and click dont support root.
        """
        try:
            measures = []
            quality_table = self.find_element(self.QUALITY_MEASURES)
            quality_rows = self.find_elements(self.QUALITY_ROW, root=quality_table)
            for row in quality_rows:
                measure_info = {}
                measure_info['description'] = self.find_element(self.QUALITY_DESCRIPTION, root=row).text.strip()
                print("Fetching quality measure:", measure_info['description'])
                if self.is_element_visible(self.QUALITY_RED_DOT, root=row, timeout=2):
                    measure_info['gap_status'] = 'red_dot'
                else:
                    measure_info['gap_status'] = 'no_dot'
                measure_info['pencil_icon_present'] = self.is_element_visible(self.QUALITY_PENCIL_ICON, root=row, timeout=1)
                print(f"Pencil icon present: {measure_info['pencil_icon_present']} for measure: {measure_info['description']}")
                measure_info['mark_as_pending_present'] = self.is_element_visible(self.QUALITY_MARK_AS_PENDING, root=row, timeout=1)
                print(f"Mark as pending option present: {measure_info['mark_as_pending_present']} for measure: {measure_info['description']}")
                measures.append(measure_info)
            print("Quality measures fetched successfully:", measures)
            return measures
        except Exception as e:
            print(f"Error fetching Quality measures: {str(e)}")
            traceback.print_exc()
            return []

    def fetch_history_dropdown_names(self):
        """
        Fetch the names of the dropdown options under history from the patient header dropdown. the PATIENT_HISTORY_DROPDOWN only shows options when its hovered over.
        So we might need to use a robot or smthing to hover and then fetch the options. return list of dropdown option names.
        """
        try:
            dropdown_names = []
            self.click_element(self.PATIENT_NAME_HEADER)
            self.hover_over_element(self.PATIENT_HISTORY_DROPDOWN)
            time.sleep(1)  # Wait for the dropdown to appear
            options = self.find_elements(self.PATIENT_HISTORY_DROPDOWN_OPTIONS)
            dropdown_names = [option.text.strip() for option in options]
            print("History dropdown option names fetched successfully:", dropdown_names)
            self.click_element(self.PATIENT_NAME_HEADER)
            return dropdown_names
        except Exception as e:
            print(f"Error fetching history dropdown option names: {str(e)}")
            traceback.print_exc()
            return []

    def click_history_dropdown_option(self, option_name):
        """
        Click a specific option from the history dropdown based on the option name provided.
        """
        try:
            self.click_element(self.PATIENT_NAME_HEADER)
            self.hover_over_element(self.PATIENT_HISTORY_DROPDOWN)
            time.sleep(1)  # Wait for the dropdown to appear
            options = self.find_elements(self.PATIENT_HISTORY_DROPDOWN_OPTIONS)
            for option in options:
                if option.text.strip() == option_name:
                    self.click_element(option)
                    print(f"Clicked on history dropdown option: {option_name}")
                    return True
            print(f"Option '{option_name}' not found in history dropdown.")
            return False
        except Exception as e:
            print(f"Error clicking history dropdown option '{option_name}': {str(e)}")
            traceback.print_exc()
            return False

    def fetch_care_team_info(self):
        """
        Fetch the care team information from the patient information section. return list of care team members.
        """
        try:
            care_team_info = []
            self.click_element(self.PATIENT_NAME_HEADER)
            self.click_element(self.PATIENT_INFORMATION)
            self.ajax_preloader_wait("Loading patient information section")
            if self.is_element_visible(self.PATIENT_INFORMATION_CARE_TEAM, timeout=5):
                self.click_element(self.PATIENT_INFORMATION_CARE_TEAM)
                time.sleep(1)  # Wait for care team content to load
                care_team_elements = self.find_elements(self.PATIENT_INFORMATION_CARE_TEAM_CONTENTS)
                care_team_info = [member.text.strip() for member in care_team_elements]
                print("Care team information fetched successfully:", care_team_info)
                return care_team_info
            else:
                print("Care Team section not found in patient information.")
                return []
        except Exception as e:
            print(f"Error fetching care team information: {str(e)}")
            traceback.print_exc()
            return []

    def fetch_coverage_info(self):
        """
        Fetch the coverage information from the patient information section. return list of coverage cards info.
        """
        try:
            coverage_info = []
            self.click_element(self.PATIENT_NAME_HEADER)
            self.click_element(self.PATIENT_INFORMATION)
            self.ajax_preloader_wait("Loading patient information section")
            if self.is_element_visible(self.PATIENT_INFORMATION_COVERAGE, timeout=5):
                self.click_element(self.PATIENT_INFORMATION_COVERAGE)
                time.sleep(1)  # Wait for coverage content to load
                coverage_elements = self.find_elements(self.PATIENT_INFORMATION_COVERAGE_CARDS)
                coverage_info = [card.text.strip() for card in coverage_elements]
                print("Coverage information fetched successfully:", coverage_info)
                return coverage_info
            else:
                print("Coverage section not found in patient information.")
                return []
        except Exception as e:
            print(f"Error fetching coverage information: {str(e)}")
            traceback.print_exc()
            return []









