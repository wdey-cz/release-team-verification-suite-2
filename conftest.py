"""
Pytest configuration file (conftest.py).
Contains fixtures and hooks for the test suite.
"""
import os
from datetime import datetime

import pytest
from selenium.common.exceptions import InvalidSessionIdException

from core.driver_factory import WebDriverFactory
from core.config import Config
from core.helpers import Helpers

from config.config_assists import ConfigAssists

from pages.cozeva_reason_for_login_page import CozevaReasonForLoginPage
from pages.cozeva_login_page import CozevaLoginPage
from pages.cozeva_users_page import CozevaUsersPage
from pages.cozeva_mfa_page import CozevaMFAPage
from core.base_page import HeaderNavBar


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
    # ca.create_first_time_setup()
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


@pytest.fixture(scope="session")
def logged_in_driver(session_driver, config_assists):
    """
    Fixture to provide a logged-in WebDriver instance.

    Args:
        session_driver: WebDriver instance from session_driver fixture
        config_assists: ConfigAssists instance
    """
    # get the run config
    rc = config_assists.get_run_configuration()
    user_role, user_name = rc.user_role, rc.user_name

    # get the db
    db = config_assists.db

    login_page = CozevaLoginPage(session_driver)
    print("Navigating to login page...")
    login_page.go_to_login_page("https://www.cozeva.com")
    print("Performing login...")
    creds = db.fetch_tester_credentials()
    login_page.enter_credentials_and_login(*creds)
    print("Login Complete. Waiting for 5 seconds...")
    login_page.sleep_code(5)

    # check if we were sent to the MFA page
    mfa_page = CozevaMFAPage(session_driver)
    if mfa_page.is_mfa_page_opened():
        mfa_page.wait_for_user_mfa_and_navigation(timeout=180)

    reason_page = CozevaReasonForLoginPage(session_driver)
    if reason_page.is_reason_page_opened():
        reason_page.enter_reason_select_customer_and_submit(client_id=rc.client_id)
        reason_page.ajax_preloader_wait()

    print("We should be logged in now. Current URL:", session_driver.current_url)

    if user_role != "Cozeva Support":
        header_nav = HeaderNavBar(session_driver)
        print("Starting Masquerade process...")
        header_nav.click_user_dropdown_option("Users")
        print("Masquerade started... Reached users page")
        print("Now Switching POM to users page to continue Masquerade")
        # Here you would continue with the Masquerade process using the UsersPage POM
        print("Selected user to masquerade:", user_name)

        users_page = CozevaUsersPage(session_driver)
        try:
            users_page.filter_search_field(user_name)
            print("Done filtering for user. Now attempting to masquerade as user:", user_name)
            users_page.masquerade_as_user(user_name, signature=db.fetch_tester_signature(),
                                          reason=db.fetch_tester_reason())
        except Exception as e:
            print("Exception occurred while searching for user:", str(e))

        print("Masquerade complete. Current URL:", session_driver.current_url)

    rc.base_landing_url = session_driver.current_url
    print("Logged in driver setup complete.")

    yield session_driver

    if user_role != "Cozeva Support":
        header_nav = HeaderNavBar(session_driver)
        header_nav.switch_back()

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
    ca = item.funcargs.get("config_assists") or None
    if ca:
        driver = item.funcargs.get("session_driver") or None
        rc = ca.get_run_configuration()
        if driver:
            driver.get(rc.base_landing_url)


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


