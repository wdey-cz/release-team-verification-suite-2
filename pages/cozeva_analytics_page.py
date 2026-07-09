import base64
import re
import traceback

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core import helpers
from core.base_page import BasePage
from selenium.webdriver.common.by import By
import time
from random import choice

import pytest
import traceback

from core.helpers import Helpers


class AnalyticsLandingPage(BasePage):


    RECENTLY_USED_SECTION=(By.XPATH, '//div[text()="Recently Used"]')
    RECENTLY_USED_CARDS=(By.XPATH, '//div[text()="Recently Used"]//parent::li//child::div[contains(@class,"horizontal_list_renderer") and @id="items"]//child::div[@class="sm_card card hoverable "]')
    RECENTLY_USED_SCROLLER=(By.XPATH,'//div[text()="Recently Used"]//parent::li//child::i')
    WORKSHEETS=(By.XPATH, "//tr[@class='sm_list_row']//child::td[1]")

    def __init__(self, driver):
        super().__init__(driver)

    def open_analytics_page(self,driver,base_url, customer_id):
        customer_list_url = []
        sm_customer_id = customer_id
        session_var = 'app_id=analytics&custId=' + str(sm_customer_id) + '&payerId=' + str(
            sm_customer_id) + '&orgId=' + str(sm_customer_id)
        encoded_string = base64.b64encode(session_var.encode('utf-8'))
        customer_list_url.append(encoded_string)
        for idx, val in enumerate(customer_list_url):
            driver.get(base_url+"/analytics/?session=" + val.decode('utf-8'))

    def is_loading_over(self):
        # Wait for the loader to disappear
        try:
            self.ajax_preloader_wait("Waiting for Analytics to load")
            return True
        except Exception as e:
            print("Error while waiting for analytics loader to disappear:", str(e))
            traceback.print_exc()
            return False

    def is_recently_used_displayed(self):
        result = {
            "section_visible": False,
            "cards_found": 0,
            "cards_visible": 0,
            "scrollers_found": 0,
            "scrollers_visible": 0,
            "status": False
        }

        try:
            # Step 1: Section visibility
            result["section_visible"] = self.is_element_visible(self.RECENTLY_USED_SECTION)

            # Step 2: Cards info
            cards = self.driver.find_elements(*self.RECENTLY_USED_CARDS)
            result["cards_found"] = len(cards)
            result["cards_visible"] = sum(1 for card in cards if card.is_displayed())

            # Step 3: Scroller info
            scrollers = self.driver.find_elements(*self.RECENTLY_USED_SCROLLER)
            result["scrollers_found"] = len(scrollers)
            result["scrollers_visible"] = sum(1 for scroller in scrollers if scroller.is_displayed())

            # Final status logic
            if result["section_visible"] and result["cards_visible"] > 0:
                result["status"] = True

            return result

        except Exception as e:
            print("Error in is_recently_used_displayed:", str(e))
            traceback.print_exc()
            return result

    def get_number_of_worksheets(self):
        try:
            elements = self.driver.find_elements(*self.WORKSHEETS)
            return len(elements)
        except Exception as e:
            print("Error while fetching number of worksheets:", str(e))
            traceback.print_exc()
            return -1

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

# class AnalyticsWorksheetPage(BasePage):
#
#
#
#     def get_worksheet_name(self):
#         try:
#             if not self.is_loading_over():
#                 print("[INFO] Page not ready, loader still present")
#                 return None
#             worksheet_name=self.driver.find_element(*self.WORKSHEET_TITLE).text
#             return worksheet_name
#         except Exception as e:
#             print("[ERROR] find_service_year:", str(e))
#             traceback.print_exc()
#             return [0, None]
#
#     def is_loading_over(self):
#         # Wait for the loader to disappear
#         try:
#             self.wait_helpers.wait_for_element_invisible(self.ANALYTICS_LOADER, timeout=120)
#             return True
#         except Exception as e:
#             print("Error while waiting for analytics loader to disappear:", str(e))
#             traceback.print_exc()
#             return False
#
#     def find_element_with_retry(self, locators, timeout=10):
#         """
#         Try multiple locators and return the first successful element.
#         Logs which locator worked.
#         """
#         last_exception = None
#
#         for index, locator in enumerate(locators):
#             try:
#                 element = WebDriverWait(self.driver, timeout).until(
#                     EC.presence_of_element_located(locator)
#                 )
#                 print(f"[SUCCESS] Locator #{index+1} worked: {locator}")
#                 return element
#
#             except Exception as e:
#                 print(f"[RETRY] Locator #{index+1} failed: {locator}")
#                 last_exception = e
#
#         print("[FAILED] All locators failed.")
#         traceback.print_exc()
#         raise last_exception
#
#     def get_text_with_retry(self, locators, timeout=10):
#         """
#         Helper method to fetch text from an element using fallback locators.
#         Internally uses retry logic defined in BasePage.
#         """
#         element = self.find_element_with_retry(locators, timeout)
#         return element.text.strip()
#
#     def get_selected_service_year(self):
#         """
#         Finds the currently selected service year from the UI.
#
#         Returns:
#         [1, value] → if element is found and value extracted
#         [0, None] → if element not found or page not ready
#         """
#
#         try:
#             # Ensure page loading is complete before interacting
#             if not self.is_loading_over():
#                 print("[INFO] Page not ready, loader still present")
#                 return [0, None]
#
#             # Locate the element using fallback locators and store reference
#             self.service_year = self.find_element_with_retry(
#                 self.SELECTED_YEAR_VALUE
#             )
#
#             # Extract text from the stored WebElement
#             value = self.service_year.text.strip()
#
#             # Success log
#             print(f"[SUCCESS] Service year found: {value}")
#
#             return [1, value]
#
#         except Exception as e:
#             print("[ERROR] find_service_year:", str(e))
#             traceback.print_exc()
#             return [0, None]
#
#     def apply_filter(self):
#         """
#         Click Apply using helpers.action_click (no retry)
#         """
#         try:
#             # Wait until element is clickable
#             apply_filter = WebDriverWait(self.driver, 10).until(
#                 EC.element_to_be_clickable(self.APPLY_FILTER)
#             )
#
#             # Use helper click
#             Helpers.action_click(self.driver, apply_filter)
#
#             # Wait for loader
#             if not self.is_loading_over():
#                 return False
#
#             print("[SUCCESS] Applied filter")
#             return True
#
#         except Exception as e:
#             print("[ERROR] apply_filter:", str(e))
#             traceback.print_exc()
#             return False
#
#     def set_service_year(self, year):
#         """
#         Sets the service year using dropdown values with fuzzy matching.
#
#         Strategy:
#         1. Open dropdown
#         2. Extract all available options
#         3. Match using partial/normalized comparison
#         4. Select best match
#         5. Apply filter and validate
#         """
#         try:
#             if not self.is_loading_over():
#                 print("[INFO] Page not ready, loader still present")
#                 return [0, None]
#
#             print(f"[INFO] Attempting to set service year: {year}")
#
#             # Step 1: Open dropdown
#             dropdown_btn = self.find_element_with_retry(self.YEAR_FILTER)
#             Helpers.action_click(self.driver, dropdown_btn)
#             print("[INFO] Dropdown opened")
#
#             # Step 2: Capture all dropdown options
#             options_locator = (By.XPATH, "//label[contains(@class,'radio')]")
#
#             options = WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_all_elements_located(options_locator)
#             )
#
#             print(f"[INFO] Total dropdown options found: {len(options)}")
#
#             extracted_values = []
#             matched_element = None
#
#             # Step 3: Extract + Match
#             for idx, opt in enumerate(options):
#                 text = opt.text.strip()
#                 extracted_values.append(text)
#
#                 print(f"[DEBUG] Option {idx + 1}: '{text}'")
#
#                 # Normalize comparison (handles "2023", "CY 2023", "Year: 2023", etc.)
#                 if str(year) in text:
#                     matched_element = opt
#                     print(f"[MATCH] Found matching option: '{text}'")
#                     break
#
#             print(f"[INFO] All extracted values: {extracted_values}")
#
#             # Step 4: Fallback (if no match found)
#             if not matched_element:
#                 print("[WARN] No exact match found. Applying fallback strategy...")
#
#                 # Try numeric extraction match
#                 for opt in options:
#                     text = opt.text.strip()
#                     digits = ''.join(filter(str.isdigit, text))
#
#                     if digits == str(year):
#                         matched_element = opt
#                         print(f"[MATCH-FALLBACK] Matched via digits: '{text}'")
#                         break
#
#             # Step 5: If still not found → fail safely
#             if not matched_element:
#                 print(f"[ERROR] No matching year found for: {year}")
#                 return [0, None]
#
#             # Scroll + Click
#             self.driver.execute_script("arguments[0].scrollIntoView(true);", matched_element)
#             Helpers.action_click(self.driver, matched_element)
#
#             print(f"[INFO] Selected year option successfully")
#
#             # Step 6: Apply filter
#             if not self.apply_filter():
#                 print("[ERROR] Apply filter failed")
#                 return [0, None]
#
#             # Step 7: Validate selection
#             status, selected_year = self.get_selected_service_year()
#
#             if status and str(year) in str(selected_year):
#                 print(f"[SUCCESS] Service year set correctly: Expected={year}, Got={selected_year}")
#                 return [1, year]
#             else:
#                 print(f"[ERROR] Validation failed: Expected={year}, Got={selected_year}")
#                 return [0, None]
#
#         except Exception as e:
#             print("[ERROR] set_service_year:", str(e))
#             traceback.print_exc()
#             return [0, None]
#     # def show_filter(self):
#
#
#     def iterate_drilldowm(self, year, val):
#         """
#         Updated Behavior:
#         1. If overview has no data → return
#         2. Before first drill → select all
#         3. If DATA → stay and go deeper (next drill)
#         4. If NO DATA → record → go back → select all → skip
#         5. Continue till end
#
#         Returns:
#             dict → {drill_name: "no_data"}
#         """
#
#         no_data_drills = {}
#
#         try:
#             # Step 1: Ensure page ready
#             if not self.is_loading_over():
#                 print("[INFO] Page not ready")
#                 return {}
#
#             # Step 2: Overview check
#             if self.check_exists_byclass( "nodata"):
#                 print(f"[NO DATA - OVERVIEW] {year}, {val}")
#                 no_data_drills["overview"] = "no_data"
#                 return no_data_drills
#
#             total = len(self.driver.find_elements(*self.DRILLDOWN_ELEMENTS))
#
#             # Initial reset before starting
#             select_all = self.driver.find_element(*self.SELECT_ALL_ID)
#             Helpers.action_click(self.driver, select_all)
#
#             if not self.is_loading_over():
#                 return {}
#
#             j = 1
#             while j <= total:
#
#                 # Click drill j
#                 drill_xpath = f"(//div[@class='breadcrumb_dropdown']//child::a)[{j}]"
#                 ele = self.driver.find_element(By.XPATH, drill_xpath)
#
#                 Helpers.action_click(self.driver, ele)
#
#                 drill_name = ele.get_attribute("drill_down_name")
#                 print(f"[INFO] Drill {j}: {drill_name}")
#
#                 if not self.is_loading_over():
#                     return {}
#
#                 # 🔴 NO DATA → backtrack
#                 if self.check_exists_byclass( "nodata"):
#                     print(f"[NO DATA] {year}, {val}, {drill_name}")
#                     no_data_drills[drill_name] = "no_data"
#
#                     # Go back one level
#                     overview = self.driver.find_element(By.XPATH, self.overview_xpath)
#                     Helpers.action_click(self.driver, overview)
#
#                     if not self.is_loading_over():
#                         return {}
#
#                     # Reset state
#                     select_all = self.driver.find_element(*self.SELECT_ALL_ID)
#                     Helpers.action_click(self.driver, select_all)
#
#                     if not self.is_loading_over():
#                         return {}
#
#                     # Skip → next drill
#                     j += 1
#                     continue
#
#                 # 🟢 DATA → DO NOT GO BACK
#                 else:
#                     print(f"[DATA]  {year}, {val}, {drill_name} ::: Data Found")
#                     Helpers.action_click(self.driver, select_all)
#                     # Stay in current level and move forward
#                     j += 1
#
#             return no_data_drills
#
#         except Exception as e:
#             print("[ERROR] iterate_drilldowm:", str(e))
#             traceback.print_exc()
#             return {}
#
#     def get_back(self):
#         try:
#             back_button=self.driver.find_element(*self.BACK_BUTTON)
#             Helpers.action_click(self.driver, back_button)
#             WebDriverWait(self.driver, 200).until(EC.invisibility_of_element_located(self.ANALYTICS_LANDING_LOADER))
#         except Exception as e:
#             print("[ERROR] Error in navigating back from worksheet ", str(e))
#             traceback.print_exc()
#
#     # def does_lob_filter_exists(self):
#
#     # def change_lob_filter(self,index):
#     #
#     # def iterate_with_lob(self):
#

#     #TODO 1. Handle collapse cases of Filters 2. Iterates drilldowns

class AnalyticsWorksheetPage(BasePage):

    def __init__(self,driver):
        super().__init__(driver)
        self.analytics_loader_locator = [
            (By.CLASS_NAME, 'sm_download_cssload_loader')
        ]

        self.apply_filter_locator = [
            (By.XPATH, '//a[text()="Apply"]')
        ]

        self.selected_year_value = [
            (By.XPATH, '//select[@name="year"]//following::span[@class="multiselect-selected-text"][1]'),
            (By.XPATH, '//select[@name="selection"]//following::span[@class="multiselect-selected-text"][1]')
        ]

        self.year_filter_locator = [
            (By.XPATH, '//select[@name="year"]//following::button[1]')
        ]

        self.drilldown_elements_locator = [
            (By.XPATH, '//div[@class="breadcrumb_dropdown"]//child::a')
        ]
        self.options_locator=[
            (By.XPATH, "//label[contains(@class,'radio')]")
        ]
        self.select_all_locator = [
            (By.ID, 'sm_select_all')
        ]

        self.overview_locator = [
            (By.XPATH, '//div[@class="breadcrumb_dropdown"]//child::a[1]')
        ]

        self.worksheet_title_locator = [
            (By.XPATH, "//div[@data-once='faq-link']")
        ]

        self.back_button_locator = [
            (By.XPATH, '//i[text()=\"arrow_back\"]')
        ]

        self.analytics_landing_loader_locator = [
            (By.CLASS_NAME, 'sm_download_cssload_loader_wrap')
        ]

    def find_element_with_retry(self, locators, timeout=10):
        """
        Try all locators in the list and return the first successful element.

        Args:
            locators: List of tuples containing (By, selector_value)
            timeout: Wait timeout in seconds (default: 10)

        Returns:
            WebElement: The first element found using any of the locators

        Raises:
            Exception: If none of the locators successfully find an element
        """
        last_exception = None

        for index, locator in enumerate(locators):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                print(f"✓ [SUCCESS] Locator #{index + 1} worked: {locator}")
                return element

            except (TimeoutException, NoSuchElementException) as e:
                print(f"✗ [RETRY] Locator #{index + 1} failed: {locator}")
                print(f"   Error: {type(e).__name__}")
                last_exception = e

        # All locators failed
        print(f"\n❌ [FAILED] All {len(locators)} locators failed.")
        traceback.print_exc()
        raise last_exception

    def get_text_with_retry(self, locators, timeout=10):
        """
        Helper method to fetch text from an element using fallback locators.
        Internally uses retry logic.

        Args:
            locators: List of tuples containing (By, selector_value)
            timeout: Wait timeout in seconds (default: 10)

        Returns:
            str: The stripped text content of the element

        Raises:
            Exception: If no locator successfully finds an element
        """
        element = self.find_element_with_retry(locators, timeout)
        return element.text.strip()

    def get_attribute_with_retry(self, locators, attribute_name, timeout=10):
        """
        Helper method to fetch an attribute from an element using fallback locators.

        Args:
            locators: List of tuples containing (By, selector_value)
            attribute_name: The attribute to fetch (e.g., 'href', 'value', 'class')
            timeout: Wait timeout in seconds (default: 10)

        Returns:
            str: The attribute value

        Raises:
            Exception: If no locator successfully finds an element
        """
        element = self.find_element_with_retry(locators, timeout)
        return element.get_attribute(attribute_name)

    def is_loading_over(self) -> bool:
        """
        Used after opening worksheet
        Used after filter changes
        Used after drilldown clicks
        """
        try:
            self.ajax_preloader_wait("Waiting for Analytics to load")
            print("[AnalyticsWorksheetPage] is_loading_over()")
            return True
        except Exception as e:
            print("Error while waiting for analytics loader to disappear:", str(e))
            traceback.print_exc()
            return False

    def element_exists_with_retry(self, locators, timeout=5) -> bool:
        """
        Check if an element exists by trying all locators in the list.
        Returns True if any locator finds the element, False if none work.
        Does NOT raise an exception.

        Args:
            locators: List of tuples containing (By, selector_value)
            timeout: Wait timeout in seconds (default: 5)

        Returns:
            bool: True if element exists, False otherwise
        """
        for index, locator in enumerate(locators):
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                print(f"✓ [FOUND] Locator #{index + 1} exists: {locator}")
                return True

            except (TimeoutException, NoSuchElementException):
                print(f"✗ [NOT FOUND] Locator #{index + 1} failed: {locator}")
                continue

        print(f"✗ [NOT FOUND] All {len(locators)} locators do not exist.")
        return False

    def does_year_filter_exist(self) -> bool:
        """
        Check if the year filter exists on the page.
        Tries all locators in service_year_filter_locator list.

        Called before get_selected_service_year()

        Returns:
            bool: True if year filter exists, False otherwise
        """
        print("[AnalyticsWorksheetPage] does_year_filter_exist()")
        return self.element_exists_with_retry(self.year_filter_locator, timeout=5)

    def get_selected_service_year(self) -> tuple[int, str | None]:
        """
        Get the currently selected service year from the year filter.
        Extracts the FIRST year number (4 consecutive digits) from the selected text.

        Examples:
            - "2026" → (1, "2026")
            - "2026-2027" → (1, "2026")
            - "Year: 2026-2027" → (1, "2026")
            - "2025" → (1, "2025")
            - "No year found" → (0, None)

        Uses retry logic to try all locators in selected_year_value list.

        Returns:
            tuple[int, str | None]:
                - (1, "YYYY") if year successfully extracted (e.g., (1, "2026"))
                - (0, None) if year extraction fails
        """
        print("[AnalyticsWorksheetPage] get_selected_service_year()")

        try:
            # Use retry logic to get text from selected_year_value locators
            selected_year_text = self.get_text_with_retry(
                self.selected_year_value,
                timeout=10
            )

            print(f"✓ [SUCCESS] Selected year text retrieved: '{selected_year_text}'")

            # Extract the FIRST year number (4 consecutive digits)
            year_match = re.search(r'\d{4}', selected_year_text)

            if year_match:
                first_year = year_match.group()
                print(f"✓ [SUCCESS] Year extracted: {first_year}")
                return 1, first_year
            else:
                print(f"✗ [FAILED] No year number found in: '{selected_year_text}'")
                return 0, None

        except Exception as e:
            print(f"✗ [FAILED] Could not get selected year: {type(e).__name__}")
            print(f"   Error details: {str(e)}")
            return 0, None

    def set_service_year(self, year: str) -> tuple[int, str | None]:
        """
        Set the service year filter to the specified year.

        Uses retry logic for all element locations and interactions.
        Validates that the year was successfully set before returning.

        Args:
            year (str): The year to set (e.g., "2026")

        Returns:
            tuple[int, str | None]:
                - (1, "2026") if year successfully set
                - (0, "Already selected") if year is already selected
                - (0, None) if operation fails

        Raises:
            Exception: If page has not loaded or year cannot be found in options
        """
        print(f"[AnalyticsWorksheetPage] set_service_year({year})")

        try:
            # Step 1: Check if page has loaded
            if not self.does_year_filter_exist():
                raise Exception("Page has not loaded yet - Year filter not found")

            print(f"✓ Page loaded - Year filter exists")

            # Step 2: Get currently selected year
            status, selected_year = self.get_selected_service_year()

            if status == 1 and selected_year == year:
                print(f"✓ Year {year} is already selected")
                return 0, "Already selected"

            print(f"✓ Current year: {selected_year}, Target year: {year}")

            # Step 3: Open the year filter dropdown
            print(f"→ Opening year filter dropdown...")
            year_filter_element = self.find_element_with_retry(
                self.year_filter_locator,
                timeout=10
            )
            Helpers.action_click(self.driver, year_filter_element)
            print(f"✓ Year filter dropdown opened")

            # Step 4: Wait for dropdown options to appear
            time.sleep(1)  # Brief wait for dropdown to render

            # Step 5: Find all year options in dropdown
            print(f"→ Looking for year '{year}' in dropdown options...")
            year_options = self.find_element_with_retry(
                self.options_locator,
                timeout=10
            )

            # Step 6: Find the LATEST option containing the year
            # Get all options and filter by those containing the target year
            matched_elements = []

            try:
                # Retry to get all option elements
                all_options = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(self.options_locator)
                )

                for option in all_options:
                    option_text = option.text.strip()
                    if year in option_text:
                        matched_elements.append(option)
                        print(f"  - Found option containing '{year}': {option_text}")

            except Exception as e:
                print(f"✗ [FAILED] Could not retrieve options: {type(e).__name__}")
                raise Exception(f"Failed to retrieve year options: {str(e)}")

            if not matched_elements:
                print(f"✗ [FAILED] Year '{year}' not found in any dropdown options")
                raise Exception(f"Year '{year}' not found in dropdown options")

            # Step 7: Select the LATEST (last) matched element
            matched_element = matched_elements[-1]
            matched_element_text = matched_element.text.strip()
            print(f"✓ Selected option (latest): {matched_element_text}")

            # Step 8: Scroll into view
            print(f"→ Scrolling option into view...")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", matched_element)
            time.sleep(0.5)  # Brief wait for scroll

            # Step 9: Click the option
            print(f"→ Clicking on year option...")
            Helpers.action_click(self.driver, matched_element)
            print(f"✓ Year option clicked")

            # Step 10: Wait for dropdown to close and value to update
            time.sleep(1)

            # Step 11: Validate that the year was successfully set
            print(f"→ Validating year selection...")
            validation_status, validated_year = self.get_selected_service_year()

            if validation_status == 1 and validated_year == year:
                print(f"✓ [SUCCESS] Year '{year}' successfully set and validated")
                return 1, year
            else:
                print(f"✗ [FAILED] Year validation failed. Selected: {validated_year}, Expected: {year}")
                return 0, None

        except Exception as e:
            print(f"✗ [EXCEPTION] set_service_year failed: {type(e).__name__}")
            print(f"   Error: {str(e)}")
            traceback.print_exc()
            return 0, None

    def does_drilldown_exist(self) -> bool:
        """
        Determines whether drilldowns exist.
        """
        print("[AnalyticsWorksheetPage] does_drilldown_exist()")
        return False

    def execute_all_drilldowns(self) -> dict:
        """
        Expected Return:

        {
            "Provider": "DATA",
            "Practice": "NO_DATA"
        }

        OR

        {}
        """
        print("[AnalyticsWorksheetPage] execute_all_drilldowns()")
        return {}

    def does_lob_filter_exist(self) -> bool:
        """
        Determines whether LOB filter exists.
        """
        print("[AnalyticsWorksheetPage] does_lob_filter_exist()")
        return False

    def fetch_lob_values(self) -> list[str]:
        """
        Expected Return:

        [
            "Commercial",
            "Medicare",
            "Medicaid"
        ]
        """
        print("[AnalyticsWorksheetPage] fetch_lob_values()")
        return []

    def set_lob(
            self,
            lob_name: str
    ) -> bool:
        """
        Returns:
            True
            False
        """
        print(f"[AnalyticsWorksheetPage] set_lob({lob_name})")
        return False

    def get_back(self) -> bool:
        """Return to worksheet landing page."""
        print("[AnalyticsWorksheetPage] get_back()")

        try:
            # Step 1: Check if page is ready
            if not self.is_loading_over():
                print("[AnalyticsWorksheetPage] get_back() | Page not ready")
                return False

            print("✓ Page is ready for navigation")

            # Step 2: Find back button with retry logic
            print("→ Finding back button...")
            back_button = self.find_element_with_retry(
                self.back_button_locator,
                timeout=10
            )
            print("✓ Back button found")

            # Step 3: Click back button
            print("→ Clicking back button...")
            Helpers.action_click(self.driver, back_button)
            print("✓ Back button clicked")

            # Step 4: Wait for landing page to load
            print("→ Waiting for Analytics landing page...")
            self.ajax_preloader_wait("Waiting for Analytics landing to load")
            print("✓ Landing page loaded")

            print("[AnalyticsWorksheetPage] get_back() | SUCCESS")
            return True

        except Exception as e:
            print(f"[AnalyticsWorksheetPage] get_back() | ERROR: {type(e).__name__}")
            print(f"   Details: {str(e)}")
            traceback.print_exc()
            return False

    def fetch_drilldown_names(self):
        """Return list of drilldown names WITHOUT executing them."""
        # Implementation depends on your page selectors
        pass


    def is_no_data_present(self):
        """Check if worksheet overview displays no-data message."""
        # Returns True/False
        pass