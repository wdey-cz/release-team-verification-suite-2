"""
WebDriver manager for creating and configuring WebDriver instances.
"""
import os
from config.config_assists import ConfigAssists as ConfigAssists

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class WebDriverFactory:
    """Factory class for creating WebDriver instances."""
    
    @staticmethod
    def get_driver(browser_name="chrome", headless=False, use_chrome_profile=False, **kwargs):
        """
        Create and return a WebDriver instance.
        
        Args:
            browser_name: Name of the browser (chrome, firefox, edge)
            headless: Run browser in headless mode
            use_chrome_profile: Use existing Chrome profile (only for Chrome)
            **kwargs: Additional arguments for browser options
            
        Returns:
            WebDriver instance
            
        Raises:
            ValueError: If browser_name is not supported

        Example Call:
            driver = WebDriverFactory.get_driver(browser_name="chrome", headless=True, arguments=["--incognito"])
        """
        browser_name = browser_name.lower()
        
        if browser_name == "chrome":
            return WebDriverFactory._get_chrome_driver(headless, use_chrome_profile, **kwargs)
        elif browser_name == "firefox":
            return WebDriverFactory._get_firefox_driver(headless, **kwargs)
        elif browser_name == "edge":
            return WebDriverFactory._get_edge_driver(headless, **kwargs)
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")

    @staticmethod
    def release_driver_from_profile(browser_name="chrome", profile_name=None):
        """
        Release the browser profile after use.

        Args:
            browser_name: Name of the browser (chrome, firefox, edge)
            profile_name: Name of the profile to release

        Example Call:
            WebDriverFactory.release_driver_from_profile(browser_name="chrome", profile_name="Profile 1")
        """
        browser_name = browser_name.lower()

        if browser_name == "chrome" and profile_name:
            ConfigAssists().set_profile_inactive(profile_name, browser_name)
            print(f"Released Chrome profile: {profile_name}")
        else:
            print(f"No action taken for browser: {browser_name} with profile: {profile_name}")
    
    @staticmethod
    def _get_chrome_driver(headless=False, use_chrome_profile=False, **kwargs):
        """
        Create Chrome WebDriver instance.
        
        Args:
            headless: Run browser in headless mode
            **kwargs: Additional Chrome options
            
        Returns:
            Chrome WebDriver instance
        """
        options = ChromeOptions()
        profile_name = None
        
        if headless:
            options.add_argument("--headless")
        
        # Common Chrome arguments
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # resolve Chrome profile usage
        if use_chrome_profile:
            profile_name = ConfigAssists().fetch_first_inactive_profile(browser_name='chrome')
            if profile_name:
                user_data_dir = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", profile_name)
                # chrome_profile_path = "user-data-dir=C:\\Users\\"+pc_username+"\\AppData\\Local\\Google\\Chrome\\User Data\\"+free_chrome_profile
                print(f"Using Chrome profile: {profile_name} located at {user_data_dir}")
                options.add_argument(f"--user-data-dir={user_data_dir}")



        
        # Add custom arguments if provided
        if "arguments" in kwargs:
            for arg in kwargs["arguments"]:
                options.add_argument(arg)
        
        # Add experimental options if provided
        if "experimental_options" in kwargs:
            for key, value in kwargs["experimental_options"].items():
                options.add_experimental_option(key, value)
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        
        return driver, profile_name
    
    @staticmethod
    def _get_firefox_driver(headless=False, **kwargs):
        """
        Create Firefox WebDriver instance.
        
        Args:
            headless: Run browser in headless mode
            **kwargs: Additional Firefox options
            
        Returns:
            Firefox WebDriver instance
        """
        options = FirefoxOptions()
        
        if headless:
            options.add_argument("--headless")
        
        # Add custom arguments if provided
        if "arguments" in kwargs:
            for arg in kwargs["arguments"]:
                options.add_argument(arg)
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        driver.maximize_window()
        
        return driver
    
    @staticmethod
    def _get_edge_driver(headless=False, **kwargs):
        """
        Create Edge WebDriver instance.
        
        Args:
            headless: Run browser in headless mode
            **kwargs: Additional Edge options
            
        Returns:
            Edge WebDriver instance
        """
        options = EdgeOptions()
        
        if headless:
            options.add_argument("--headless")
        
        # Common Edge arguments
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # Add custom arguments if provided
        if "arguments" in kwargs:
            for arg in kwargs["arguments"]:
                options.add_argument(arg)
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        driver.maximize_window()
        
        return driver
