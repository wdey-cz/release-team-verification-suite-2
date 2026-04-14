"""
Helper utility functions for common operations in tests.
"""

import time
import os
from datetime import datetime
from core.config import Config


class Helpers:
    """Collection of utility helper functions."""

    @staticmethod
    def take_screenshot(driver, name="screenshot"):
        """
        Take a screenshot and save it to screenshots directory.

        Args:
            driver: WebDriver instance
            name: Name for the screenshot file

        Returns:
            Path to the saved screenshot
        """
        # Create screenshots directory if it doesn't exist
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)

        # Take screenshot
        driver.save_screenshot(filepath)
        print(f"Screenshot saved: {filepath}")

        return filepath

    @staticmethod
    def wait(seconds):
        """
        Wait for a specific number of seconds.

        Args:
            seconds: Number of seconds to wait
        """
        time.sleep(seconds)

    @staticmethod
    def generate_unique_email(prefix="test"):
        """
        Generate a unique email address using timestamp.

        Args:
            prefix: Prefix for the email address

        Returns:
            Unique email address
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}_{timestamp}@example.com"

    @staticmethod
    def generate_unique_username(prefix="user"):
        """
        Generate a unique username using timestamp.

        Args:
            prefix: Prefix for the username

        Returns:
            Unique username
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}_{timestamp}"

    @staticmethod
    def scroll_to_bottom(driver):
        """
        Scroll to the bottom of the page.

        Args:
            driver: WebDriver instance
        """
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    @staticmethod
    def scroll_to_top(driver):
        """
        Scroll to the top of the page.

        Args:
            driver: WebDriver instance
        """
        driver.execute_script("window.scrollTo(0, 0);")

    @staticmethod
    def switch_to_new_window(driver):
        """
        Switch to the most recently opened window/tab.

        Args:
            driver: WebDriver instance
        """
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])

    @staticmethod
    def close_current_window_and_switch_back(driver):
        """
        Close current window and switch to the previous one.

        Args:
            driver: WebDriver instance
        """
        driver.close()
        windows = driver.window_handles
        driver.switch_to.window(windows[0])

    @staticmethod
    def get_element_attribute(element, attribute):
        """
        Get an attribute value from an element.

        Args:
            element: WebElement
            attribute: Attribute name

        Returns:
            Attribute value
        """
        return element.get_attribute(attribute)

    @staticmethod
    def highlight_element(driver, element):
        """
        Highlight an element by adding a border (useful for debugging).

        Args:
            driver: WebDriver instance
            element: WebElement to highlight
        """
        original_style = element.get_attribute("style")
        driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            element,
            "border: 2px solid red; border-style: dashed;"
        )
        time.sleep(0.5)
        driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            element,
            original_style
        )

    @staticmethod
    def fetch_downloaded_file(lane_id=None):
        """
        Fetch the most recently downloaded file from the downloads directory.

        Returns:
            Path to the most recently downloaded file
        """
        download_directory = Config.RTVS_DOWNLOADS_DIR / (lane_id or "")
        files = os.listdir(download_directory)
        paths = [os.path.join(download_directory, f) for f in files]
        latest_file = max(paths, key=os.path.getctime)
        return latest_file

    @staticmethod
    def does_file_have_data(file_path):
        """
        Check if a file has data (is not empty).

        Args:
            file_path: Path to the file
        Returns:
            True if file has data, False if empty
        """
        return os.path.getsize(file_path) > 0

    @staticmethod
    def delete_file(file_path):
        """
        Delete a file from the filesystem.

        Args:
            file_path: Path to the file to delete
        """
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        else:
            print(f"File not found, cannot delete: {file_path}")

if __name__ == "__main__":
    # Example usage of helper functions
    helper = Helpers()

