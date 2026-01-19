"""
Pytest configuration file (conftest.py).
Contains fixtures and hooks for the test suite.
"""

import pytest
from core.driver_factory import WebDriverFactory
from core.config import Config
from core.helpers import Helpers

from config.config_assists import ConfigAssists


@pytest.fixture(scope="function")
def functiondriver(request):
    """
    Fixture to initialize and quit WebDriver for each test.

    Args:
        request: Pytest request object

    Yields:
        WebDriver instance
    """
    # Setup: Create WebDriver
    browser = Config.get_browser()
    headless = Config.is_headless()
    driver, profile = WebDriverFactory.get_driver(browser_name=browser, headless=headless, use_chrome_profile=False)

    # Set timeouts
    driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
    if Config.IMPLICIT_WAIT > 0:
        driver.implicitly_wait(Config.IMPLICIT_WAIT)

    # Yield driver to the test
    yield driver

    # Teardown: Take screenshot on failure and quit driver


    driver.quit()




@pytest.fixture(scope="session")
def sessiondriver(request):
    """
    Fixture to initialize and quit WebDriver for each test.

    Args:
        request: Pytest request object

    Yields:
        WebDriver instance
    """
    # Setup: Create WebDriver
    browser = Config.get_browser()
    headless = Config.is_headless()
    driver, profile = WebDriverFactory.get_driver(browser_name=browser, headless=headless, use_chrome_profile=True)

    # Set timeouts
    driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
    if Config.IMPLICIT_WAIT > 0:
        driver.implicitly_wait(Config.IMPLICIT_WAIT)

    # Yield driver and profile to the test
    yield driver, profile

    # Teardown: Take screenshot on failure and quit driver

    driver.quit()
    WebDriverFactory.release_driver_from_profile(browser_name=browser, profile_name=profile)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Session-level fixture to set up the test environment.
    Runs once before all tests.
    """
    # Create necessary directories
    Config.setup_directories()
    config_assists = ConfigAssists()
    config_assists.create_first_time_setup()
    print("\n=== Test Environment Setup Complete ===")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to make test results available to fixtures.

    This allows fixtures to access test pass/fail status.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_runtest_teardown(item, nextitem):
    """
    Runs after each test. If the test failed, take screenshot using the driver fixture.
    """
    rep_call = getattr(item, "rep_call", None)
    if rep_call and rep_call.failed and Config.SCREENSHOT_ON_FAILURE:
        # only if the test used the driver fixture
        driver, profile = item.funcargs.get("sessiondriver") or (None, None)
        if driver:
            Helpers.take_screenshot(driver, f"failed_{item.name}")


def pytest_configure(config):
    """
    Configure pytest with custom markers and settings.

    Args:
        config: Pytest config object
    """
    # Register custom markers
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as a regression test"
    )
    config.addinivalue_line(
        "markers", "login: tests related to login functionality"
    )
    config.addinivalue_line(
        "markers", "dashboard: tests related to dashboard functionality"
    )
    config.addinivalue_line(
        "markers", "registries: tests related to registries functionality"
    )


@pytest.fixture
def base_url():
    """
    Fixture to provide the base URL.

    Returns:
        Base URL string
    """
    return Config.get_base_url()


@pytest.fixture
def config_assists():
    """
    Fixture to provide ConfigAssists instance.

    Returns:
        ConfigAssists instance
    """
    return ConfigAssists()
