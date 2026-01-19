"""
Configuration management for the test suite.
"""

import os
from pathlib import Path


class Config:
    """Configuration class for test suite settings."""

    # Base URL for the application
    BASE_URL = os.getenv("BASE_URL", "https://www.cozeva.com")

    # Browser settings
    BROWSER = os.getenv("BROWSER", "chrome")
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

    # Timeout settings (in seconds)
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "10"))
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "0"))

    # Test credentials (should be set via environment variables)
    TEST_USERNAME = os.getenv("TEST_USERNAME", "")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "")

    # Screenshot settings
    SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
    SCREENSHOTS_DIR = os.getenv("SCREENSHOTS_DIR", "screenshots")

    # Reporting settings
    REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")

    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def get_base_url(cls):
        """Get the base URL for the application."""
        return cls.BASE_URL

    @classmethod
    def get_browser(cls):
        """Get the browser to use for tests."""
        return cls.BROWSER

    @classmethod
    def is_headless(cls):
        """Check if browser should run in headless mode."""
        return cls.HEADLESS

    @classmethod
    def get_timeout(cls):
        """Get the default timeout value."""
        return cls.DEFAULT_TIMEOUT

    @classmethod
    def get_credentials(cls):
        """
        Get test credentials.

        Returns:
            Tuple of (username, password)
        """
        return (cls.TEST_USERNAME, cls.TEST_PASSWORD)

    @classmethod
    def get_screenshots_dir(cls):
        """Get the screenshots directory path."""
        return cls.SCREENSHOTS_DIR

    @classmethod
    def get_reports_dir(cls):
        """Get the reports directory path."""
        return cls.REPORTS_DIR

    @classmethod
    def setup_directories(cls):
        """Create necessary directories if they don't exist."""
        Path(cls.SCREENSHOTS_DIR).mkdir(parents=True, exist_ok=True)
        Path(cls.REPORTS_DIR).mkdir(parents=True, exist_ok=True)
