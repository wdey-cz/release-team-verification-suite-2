import base64
import traceback

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
    WORKSHEETS=(By.XPATH, "//tr[@class='sm_list_row']")

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


class AnalyticsWorksheetPage(BasePage):
    PAGE_TITLE = [
        (By.XPATH, "//h1[contains(text(),'Analytics')]"),
    ]
    ANALYTICS_LOADER = (By.CLASS_NAME, 'sm_download_cssload_loader')
    APPLY_FILTER = (By.XPATH, '//a[text()="Apply"]')
    SELECTED_YEAR_VALUE = [
        (By.XPATH, '//select[@name="year"]//following::span[@class="multiselect-selected-text"][1]'),
        (By.XPATH, '//select[@name="selection"]//following::span[@class="multiselect-selected-text"][1]')
    ]
    YEAR_FILTER = [
        (By.XPATH, '//select[@name="year"]//following::button[1]'),
    ]
    DRILLDOWN_ELEMENTS=(By.XPATH,'//div[@class="breadcrumb_dropdown"]//child::a')
    SELECT_ALL_ID = (By.ID,'sm_select_all')
    OVERVIEW=(By.XPATH,'overview_xpath = //div[@class="breadcrumb_dropdown"]//child::a[1]')
    WORKSHEET_TITLE=(By.XPATH,"//div[@data-once='faq-link']")
    BACK_BUTTON= (By.XPATH,'//i[text()=\"arrow_back\"]')
    ANALYTICS_LANDING_LOADER=(By.CLASS_NAME,'sm_download_cssload_loader_wrap')
    FILTER_EXPAND_ICON=(By.XPATH,'')

    def __init__(self, driver):
        super().__init__(driver)
        # Stores the WebElement for service year once located
        self.service_year: WebElement | None = None
        self.drilldown_elements: list[WebElement] | None = None

    def get_worksheet_name(self):
        try:
            if not self.is_loading_over():
                print("[INFO] Page not ready, loader still present")
                return None
            worksheet_name=self.driver.find_element(*self.WORKSHEET_TITLE).text
            return worksheet_name
        except Exception as e:
            print("[ERROR] find_service_year:", str(e))
            traceback.print_exc()
            return [0, None]

    def is_loading_over(self):
        # Wait for the loader to disappear
        try:
            self.wait_helpers.wait_for_element_invisible(self.ANALYTICS_LOADER, timeout=120)
            return True
        except Exception as e:
            print("Error while waiting for analytics loader to disappear:", str(e))
            traceback.print_exc()
            return False

    def find_element_with_retry(self, locators, timeout=10):
        """
        Try multiple locators and return the first successful element.
        Logs which locator worked.
        """
        last_exception = None

        for index, locator in enumerate(locators):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                print(f"[SUCCESS] Locator #{index+1} worked: {locator}")
                return element

            except Exception as e:
                print(f"[RETRY] Locator #{index+1} failed: {locator}")
                last_exception = e

        print("[FAILED] All locators failed.")
        traceback.print_exc()
        raise last_exception

    def get_text_with_retry(self, locators, timeout=10):
        """
        Helper method to fetch text from an element using fallback locators.
        Internally uses retry logic defined in BasePage.
        """
        element = self.find_element_with_retry(locators, timeout)
        return element.text.strip()

    def get_selected_service_year(self):
        """
        Finds the currently selected service year from the UI.

        Returns:
        [1, value] → if element is found and value extracted
        [0, None] → if element not found or page not ready
        """

        try:
            # Ensure page loading is complete before interacting
            if not self.is_loading_over():
                print("[INFO] Page not ready, loader still present")
                return [0, None]

            # Locate the element using fallback locators and store reference
            self.service_year = self.find_element_with_retry(
                self.SELECTED_YEAR_VALUE
            )

            # Extract text from the stored WebElement
            value = self.service_year.text.strip()

            # Success log
            print(f"[SUCCESS] Service year found: {value}")

            return [1, value]

        except Exception as e:
            print("[ERROR] find_service_year:", str(e))
            traceback.print_exc()
            return [0, None]

    def apply_filter(self):
        """
        Click Apply using helpers.action_click (no retry)
        """
        try:
            # Wait until element is clickable
            apply_filter = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.APPLY_FILTER)
            )

            # Use helper click
            Helpers.action_click(self.driver, apply_filter)

            # Wait for loader
            if not self.is_loading_over():
                return False

            print("[SUCCESS] Applied filter")
            return True

        except Exception as e:
            print("[ERROR] apply_filter:", str(e))
            traceback.print_exc()
            return False

    def set_service_year(self, year):
        """
        Sets the service year using dropdown values with fuzzy matching.

        Strategy:
        1. Open dropdown
        2. Extract all available options
        3. Match using partial/normalized comparison
        4. Select best match
        5. Apply filter and validate
        """
        try:
            if not self.is_loading_over():
                print("[INFO] Page not ready, loader still present")
                return [0, None]

            print(f"[INFO] Attempting to set service year: {year}")

            # Step 1: Open dropdown
            dropdown_btn = self.find_element_with_retry(self.YEAR_FILTER)
            Helpers.action_click(self.driver, dropdown_btn)
            print("[INFO] Dropdown opened")

            # Step 2: Capture all dropdown options
            options_locator = (By.XPATH, "//label[contains(@class,'radio')]")

            options = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(options_locator)
            )

            print(f"[INFO] Total dropdown options found: {len(options)}")

            extracted_values = []
            matched_element = None

            # Step 3: Extract + Match
            for idx, opt in enumerate(options):
                text = opt.text.strip()
                extracted_values.append(text)

                print(f"[DEBUG] Option {idx + 1}: '{text}'")

                # Normalize comparison (handles "2023", "CY 2023", "Year: 2023", etc.)
                if str(year) in text:
                    matched_element = opt
                    print(f"[MATCH] Found matching option: '{text}'")
                    break

            print(f"[INFO] All extracted values: {extracted_values}")

            # Step 4: Fallback (if no match found)
            if not matched_element:
                print("[WARN] No exact match found. Applying fallback strategy...")

                # Try numeric extraction match
                for opt in options:
                    text = opt.text.strip()
                    digits = ''.join(filter(str.isdigit, text))

                    if digits == str(year):
                        matched_element = opt
                        print(f"[MATCH-FALLBACK] Matched via digits: '{text}'")
                        break

            # Step 5: If still not found → fail safely
            if not matched_element:
                print(f"[ERROR] No matching year found for: {year}")
                return [0, None]

            # Scroll + Click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", matched_element)
            Helpers.action_click(self.driver, matched_element)

            print(f"[INFO] Selected year option successfully")

            # Step 6: Apply filter
            if not self.apply_filter():
                print("[ERROR] Apply filter failed")
                return [0, None]

            # Step 7: Validate selection
            status, selected_year = self.get_selected_service_year()

            if status and str(year) in str(selected_year):
                print(f"[SUCCESS] Service year set correctly: Expected={year}, Got={selected_year}")
                return [1, year]
            else:
                print(f"[ERROR] Validation failed: Expected={year}, Got={selected_year}")
                return [0, None]

        except Exception as e:
            print("[ERROR] set_service_year:", str(e))
            traceback.print_exc()
            return [0, None]
    # def show_filter(self):


    def iterate_drilldowm(self, year, val):
        """
        Updated Behavior:
        1. If overview has no data → return
        2. Before first drill → select all
        3. If DATA → stay and go deeper (next drill)
        4. If NO DATA → record → go back → select all → skip
        5. Continue till end

        Returns:
            dict → {drill_name: "no_data"}
        """

        no_data_drills = {}

        try:
            # Step 1: Ensure page ready
            if not self.is_loading_over():
                print("[INFO] Page not ready")
                return {}

            # Step 2: Overview check
            if self.check_exists_byclass( "nodata"):
                print(f"[NO DATA - OVERVIEW] {year}, {val}")
                no_data_drills["overview"] = "no_data"
                return no_data_drills

            total = len(self.driver.find_elements(*self.DRILLDOWN_ELEMENTS))

            # Initial reset before starting
            select_all = self.driver.find_element(*self.SELECT_ALL_ID)
            Helpers.action_click(self.driver, select_all)

            if not self.is_loading_over():
                return {}

            j = 1
            while j <= total:

                # Click drill j
                drill_xpath = f"(//div[@class='breadcrumb_dropdown']//child::a)[{j}]"
                ele = self.driver.find_element(By.XPATH, drill_xpath)

                Helpers.action_click(self.driver, ele)

                drill_name = ele.get_attribute("drill_down_name")
                print(f"[INFO] Drill {j}: {drill_name}")

                if not self.is_loading_over():
                    return {}

                # 🔴 NO DATA → backtrack
                if self.check_exists_byclass( "nodata"):
                    print(f"[NO DATA] {year}, {val}, {drill_name}")
                    no_data_drills[drill_name] = "no_data"

                    # Go back one level
                    overview = self.driver.find_element(By.XPATH, self.overview_xpath)
                    Helpers.action_click(self.driver, overview)

                    if not self.is_loading_over():
                        return {}

                    # Reset state
                    select_all = self.driver.find_element(*self.SELECT_ALL_ID)
                    Helpers.action_click(self.driver, select_all)

                    if not self.is_loading_over():
                        return {}

                    # Skip → next drill
                    j += 1
                    continue

                # 🟢 DATA → DO NOT GO BACK
                else:
                    print(f"[DATA]  {year}, {val}, {drill_name} ::: Data Found")
                    Helpers.action_click(self.driver, select_all)
                    # Stay in current level and move forward
                    j += 1

            return no_data_drills

        except Exception as e:
            print("[ERROR] iterate_drilldowm:", str(e))
            traceback.print_exc()
            return {}

    def get_back(self):
        try:
            back_button=self.driver.find_element(*self.BACK_BUTTON)
            Helpers.action_click(self.driver, back_button)
            WebDriverWait(self.driver, 200).until(EC.invisibility_of_element_located(self.ANALYTICS_LANDING_LOADER))
        except Exception as e:
            print("[ERROR] Error in navigating back from worksheet ", str(e))
            traceback.print_exc()

    # def does_lob_filter_exists(self):

    # def change_lob_filter(self,index):
    #
    # def iterate_with_lob(self):

    #TODO 1. Handle collapse cases of Filters 2. Iterates drilldowns













