"""
Configuration management for the test suite.
"""

import os
import sys
from pathlib import Path


def _is_frozen_exe() -> bool:
    # True when running from a PyInstaller build
    return bool(getattr(sys, "frozen", False))


def _default_user_data_dir(app_name: str = "RTVS2") -> Path:
    """
    Cross-platform-ish, no extra deps:
    - Windows: %LOCALAPPDATA%\\RTVS2
    - macOS: ~/Library/Application Support/RTVS2
    - Linux: ~/.local/share/RTVS2
    """
    if os.name == "nt":
        base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / app_name

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / app_name

    # linux and others
    xdg = os.getenv("XDG_DATA_HOME")
    return Path(xdg) / app_name if xdg else (Path.home() / ".local" / "share" / app_name)


def _runtime_assets_dir(dev_project_root: Path) -> Path:
    """
    Assets location:
    - Dev: <project_root>/assets
    - PyInstaller onefile/onedir: <sys._MEIPASS>/assets
    """
    if _is_frozen_exe() and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "assets"
    return dev_project_root / "assets"


class Config:
    """Configuration class for test suite settings."""

    # Base URL for the application
    BASE_URL = os.getenv("BASE_URL", "https://www.cozeva.com")

    # Project root in dev mode (core/config.py is inside core)
    RTVS_PROJECT_ROOT = Path(__file__).resolve().parent.parent

    # Read-only packaged assets
    RTVS_ASSETS_DIR = _runtime_assets_dir(RTVS_PROJECT_ROOT)

    # Writable app data root (override if you want)
    RTVS_DATA_DIR = Path(os.getenv("RTVS_DATA_DIR", str(_default_user_data_dir("RTVS2"))))
    RTVS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Customers JSON
    # If you pass an absolute path in env, it will use that.
    # Otherwise it will look inside assets.
    RTVS_CUSTOMERS_JSON = os.getenv("RTVS_CUSTOMERS_JSON", "customers1.json")

    @classmethod
    def get_customers_json_path(cls) -> Path:
        p = Path(cls.RTVS_CUSTOMERS_JSON)
        return p if p.is_absolute() else (cls.RTVS_ASSETS_DIR / p)

    # DB path (IMPORTANT: writable and persistent)
    RTVS_DEFAULT_DB_PATH = Path(os.getenv("RTVS_DB_PATH", str(RTVS_DATA_DIR / "rtvs_database.db")))

    # Browser settings
    BROWSER = os.getenv("BROWSER", "chrome")
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

    # ENV settings
    TEST_ENV = os.getenv("TEST_ENV", "PROD")

    # Timeout settings (in seconds)
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "10"))
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "0"))

    # Test credentials
    TEST_USERNAME = os.getenv("TEST_USERNAME", "")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "")
    REASON_FOR_LOGIN = os.getenv("REASON_FOR_LOGIN", "RM 17811")

    # Output directories (make them live under RTVS_DATA_DIR by default)
    SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
    SCREENSHOTS_DIR = Path(os.getenv("SCREENSHOTS_DIR", str(RTVS_DATA_DIR / "screenshots")))
    REPORTS_DIR = Path(os.getenv("REPORTS_DIR", str(RTVS_DATA_DIR / "reports")))

    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def get_base_url(cls):
        return cls.BASE_URL

    @classmethod
    def get_browser(cls):
        return cls.BROWSER

    @classmethod
    def get_test_env(cls):
        return cls.TEST_ENV

    @classmethod
    def is_headless(cls):
        return cls.HEADLESS

    @classmethod
    def get_timeout(cls):
        return cls.DEFAULT_TIMEOUT

    @classmethod
    def get_credentials(cls):
        return (cls.TEST_USERNAME, cls.TEST_PASSWORD)

    @classmethod
    def get_screenshots_dir(cls) -> Path:
        return cls.SCREENSHOTS_DIR

    @classmethod
    def get_reports_dir(cls) -> Path:
        return cls.REPORTS_DIR

    @classmethod
    def setup_directories(cls):
        cls.RTVS_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
