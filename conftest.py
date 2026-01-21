"""
Pytest configuration file (conftest.py).
Contains fixtures and hooks for the test suite.
"""
from datetime import datetime

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

    driver._rtvs_profile = profile
    yield driver




    # Teardown: Take screenshot on failure and quit driver

    driver.quit()
    WebDriverFactory.release_driver_from_profile(browser_name=browser, profile_name=profile)


@pytest.fixture(scope="session")
def config_assists():
    """
    Fixture to provide ConfigAssists instance.

    Returns:
        ConfigAssists instance
    """
    ca = ConfigAssists()
    ca.create_first_time_setup()
    yield ca
    ca.db.close()

@pytest.fixture(scope="session", autouse=True)
def init_session_state(config_assists):
    """
    Session-level fixture to initialize session state.
    Runs once before all tests.
    """
    # Create necessary directories
    Config.setup_directories()
    print("Test Environment Setup Complete")
    # start run config creation
    rc = config_assists.get_run_configuration()
    # here read back from the db, but get runid somehow
    rc.env = Config.get_test_env()
    rc.browser = Config.get_browser()
    rc.started_at = datetime.now().strftime("%Y%m%d_%H%M%S")

@pytest.fixture(autouse=True)
def populate_run_config_for_test(request, config_assists):
    item = request.node
    rc = config_assists.get_run_configuration()

    rc.test_name = item.name
    rc.test_package = ""
    rc.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    config_assists.set_unique_id()
    """
    Fields - run_id:
        - prefix : RTVS
        - category : REG or DATA
        - env : PROD, CERT, STAGE, NOENV
        - test_case_package : ComboPack1, ComboPack2, DefaultRegressionPack, AnalyticsPack, PatientDashboardPack, SidebarPack AWV, PracticeProviderCompare
        - timestamp : YYYYMMDD_HHMMSS
        - unique id : random 4 digit number
        - optional suffix : any additional info
        Example1: RTVS-REG-PROD-ComboPack1-20231015_142530-1234-SuffixInfo
        Example2: RTVS-REG-STAGE-AnalyticsPack-20231101_101015-5678-AnotherSuffix
        Example3: RTVS-DATA-NOENV-PracticeProviderCompare-20231205_090000-9012-StressTest
    """
    config_assists.create_run_id()

    yield






# @pytest.fixture(scope="session",autouse=True)
# def assign_test_package(request, config_assists):
#     """
#     Session-level fixture to assign test packages based on markers.
#     Runs once before all tests.
#     """
#     item = request.node
#     rc = config_assists.get_run_configuration()
#     rc.env = Config.get_test_env()
#     rc.browser = Config.get_browser()
#     rc.category =



# @pytest.fixture(scope="session", autouse=True)
# def setup_test_environment():
#     """
#     Session-level fixture to set up the test environment.
#     Runs once before all tests.
#     """
#     # Create necessary directories
#     Config.setup_directories()
#     config_assists = ConfigAssists()
#     config_assists.create_first_time_setup()
#     print("\n=== Test Environment Setup Complete ===")


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
        driver = item.funcargs.get("sessiondriver") or None
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


