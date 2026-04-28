
from selenium.webdriver.common.by import By
from webdriver_manager.core import driver

from core.base_page import BasePage

class CozevaEFormSignOff(BasePage):
    CHART_SAVE_BUTTON=(By.XPATH,".//div[contains(@class,'btn-group')]//button[contains(text(),'Save')]")
    WARNING_CONTENT=(By.XPATH,".//*[@class='modal-content ']//div//div")
    WARNING_OK_BUTTON=(By.XPATH,"//div[contains(@class,'modal-footer')]//a[normalize-space()='Ok']")
    PAF_DETAILS=(By.XPATH,".//div[@class='_5vps relative_elem']//div//h3")


    def __init__(self,driver):
        super().__init__(driver)

    def warning_manage(self):
        #To read the warning and click ok button to proceed
        self.find_element(self.WARNING_CONTENT, 10)
        warning_text = self.get_text(self.WARNING_CONTENT)
        print("Warning appeared"+warning_text)
        self.driver.click_element(self.WARNING_OK_BUTTON)
        return warning_text

    def billing_provider_modal(self):
        #To manage billing provider modal
        self.find_element(self.PAF_DETAILS, 10)
        paf_detils_in_billing_provider_modal = self.get_text(self.PAF_DETAILS)
        print("PAF DETAILS: "+paf_detils_in_billing_provider_modal)
        




    def add_section(self,name,target):
        #this method will check the section avilability and pressent data count, then add new and check post count
        #name is a section name
        #target is table id
        #count is a locator to get attribute
        try:
            target_xpath=f".//span[@table_id='{target}']//span"
            elements = self.driver.find_elements(By.XPATH, target_xpath)
            count_xpath= f".//span[@table_id='{target}']//span[@class='count-indicator']"
            count=self.driver.find_element(By.XPATH, count_xpath)
            is_element_present = len(elements) > 0
            if is_element_present:
                present_Count=self.driver.get_element_attribute(count,'data-row-count')
                self.driver.find_element(By.XPATH,target_xpath,10)
                self.driver.click_element(By.XPATH,target_xpath)
                self.find_element(self.CHART_SAVE_BUTTON,10)
                self.click_element(self.CHART_SAVE_BUTTON)
                self.sleep_code(2)
                updated_Count = driver.get_element_attribute(count, 'data-row-count')
                diff=int(updated_Count)-int(present_Count)
                return diff
            else:
                print(f"{name} not present")
                return 0
        except Exception as e:
            print(f"{name} not present or error occurred: {e}")
            return 0



