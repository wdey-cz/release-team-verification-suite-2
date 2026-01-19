from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class WaitHelpers:
    def __init__(self, driver, default_timeout=10):
        # Initialize wait helpers.
        self.driver = driver
        self.default_timeout = default_timeout


    def wait_for_element_visible(self, locator,timeout=None):
        # Wait for an element to be visible.
        timeout = timeout or self.default_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
    def wait_for_element_invisible(self, locator, timeout=None):
        # Wait for an element to become invisible.
        timeout = timeout or self.default_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(locator)
        )
    def wait_for_element_clickable(self, locator, timeout=None):
        # Wait for an element to be clickable.
        timeout = timeout or self.default_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
    def wait_for_element_present(self, locator, timeout=None):
        # Wait for an element to be present in the DOM.
        timeout = timeout or self.default_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def wait_for_staleness_of(self, locator, timeout=None):
        # Wait for an element to become stale.
        timeout = timeout or self.default_timeout
        element = self.driver.find_element(*locator)
        return WebDriverWait(self.driver, timeout).until(
            EC.staleness_of(element)
        )