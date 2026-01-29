"""
Pytest configuration file (conftest.py).
Contains fixtures and hooks for the test suite.
"""
import os
from datetime import datetime

import pytest
from selenium.common import InvalidSessionIdException

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
def session_driver(request):
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
def init_session_state(pytestconfig, config_assists):
    """
    Session-level fixture to initialize session state.
    Runs once before all tests.
    This function will add values to the RunConfiguration Dataclass in config_assists as self.run_config from DB.
    """
    # Create necessary directories
    Config.setup_directories()
    print("Test Environment Setup Complete")
    # start run config creation, this is the dataclass within config_assists
    rc = config_assists.get_run_configuration()

    # here read back from the db, but get runid - Pass it via pytest argument
    run_id = pytestconfig.getoption("--rtvs-run-id")
    if run_id:
        row = config_assists.db.get_test_run_row(run_id)
        if not row:
            raise RuntimeError(f"run_id not found in DB: {run_id}")

        rc.run_id = row["run_id"]
        rc.category = row["category"]
        rc.env = row["env"]
        rc.test_package = row["test_package"]
        rc.test_package_desc = row["test_package_desc"]
        rc.unique_id = row["unique_id"]
        rc.started_at = row["started_at"]
        rc.multiprocessing = bool(row["multiprocessing"])
        rc.threads = int(row["threads"])
        rc.browser = Config.get_browser()
    else:
        # fallback for ad-hoc runs without controller
        rc.env = Config.get_test_env()
        rc.browser = Config.get_browser()
        rc.browsers = rc.browser
        rc.started_at = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_assists.set_unique_id()
        rc.category = rc.category or "REG"
        rc.test_package = rc.test_package or "UNCATEGORIZED"
        config_assists.create_run_id()
        config_assists.db.insert_test_run(rc)

        # Per-process args
    cid = pytestconfig.getoption("--client-id")
    rc.client_id = int(cid) if cid else None
    rc.user_role = pytestconfig.getoption("--user-role") or None
    rc.user_name = pytestconfig.getoption("--user-name") or None
    rc.worker = os.getenv("PYTEST_XDIST_WORKER", "local")
    rc.pid = os.getpid()

    print("\n[RTVS] Loaded run_config from DB:")
    print(f"  run_id={rc.run_id}")
    print(f"  package={rc.test_package}")
    print(f"  client_id={rc.client_id} role={rc.user_role} user={rc.user_name}")
    print(f"  browser={rc.browser} worker={rc.worker} pid={rc.pid}")
    # create the run row

@pytest.fixture(autouse=True)
def auto_log_test_lifecycle(request, config_assists, session_driver):

    rc = config_assists.get_run_configuration()
    rc.test_name = request.node.name
    rc.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Start log
    config_assists.add_log_start(message=f"START {rc.test_name}", driver=session_driver)

    yield

    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        config_assists.add_log_error(message=f"FAIL {rc.test_name}", driver=session_driver)
    elif rep_call and rep_call.skipped:
        config_assists.add_log_skip(message=f"SKIP {rc.test_name}", driver=session_driver)
    else:
        config_assists.add_log_end(message=f"END {rc.test_name}", driver=session_driver)


@pytest.fixture(autouse=True)
def populate_run_config_for_test(request, config_assists):
    config_assists.set_test_context(test_name=request.node.name)



    yield    # Teardown if needed

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
        driver = item.funcargs.get("session_driver") or None
        if driver:
            try:
                Helpers.take_screenshot(driver, f"failed_{item.name}")
            except InvalidSessionIdException as e:
                print(f"Could not take screenshot, invalid session: {e}")


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
    config.addinivalue_line("markers", "no_teardown: skip RTVS teardown hook logic")


def pytest_addoption(parser):
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
    parser.addoption("--rtvs-run-id", action="store", default="")
    parser.addoption("--client-id", action="store", default="")
    parser.addoption("--user-role", action="store", default="")
    parser.addoption("--user-name", action="store", default="")


@pytest.fixture
def base_url():
    """
    Fixture to provide the base URL.

    Returns:
        Base URL string
    """
    return Config.get_base_url()


