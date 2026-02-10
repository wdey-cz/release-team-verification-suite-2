import os
from dataclasses import dataclass
from typing import Any
import shutil
import subprocess
from pathlib import Path

import sys

from config.rtvsdb import RTVSDB
from core.config import Config


@dataclass
class RunConfiguration:
    prefix: str = "RTVS"
    run_id: str | None = None
    env: str | None = None
    category: str | None = None
    test_package: str | None = None
    test_package_desc: str | None = None
    unique_id: str | None = None
    multiprocessing: bool = False
    threads: int = 1
    started_at: str | None = None

    ended_at: str | None = None

    timestamp: str | None = None

    browsers: str | None = None
    browser: str | None = None
    browser_profile: str | None = None
    test_name: str | None = None
    clients: str | None = None
    client_id: int | None = None
    user_roles: str | None = None
    user_role: str | None = None
    user_name: str | None = None
    pid: str | None = None
    worker: str | None = None
    workbook_title: str | None = None
    other_info: dict | None = None
    base_landing_url: str | None = None



class ConfigAssists:

    BROWSER = Config.get_browser()
    ENV = Config.get_test_env()

    def __init__(self):
        self.db = RTVSDB()
        self.run_config: RunConfiguration | None = None
        self.set_run_configuration(RunConfiguration())

    def create_first_time_setup(self):
        self.install_requirements()
        # Create the chrome_profiles table if it doesn't exist
        self.db.create_chrome_profile_info_table()
        # Initialize the table with default profiles
        self.db.initialize_chrome_profiles(profile_count=10)
        self.db.create_customer_tables()
        self.db.load_customer_json_into_db()
        self.db.create_run_and_log_tables()
        self.db.load_test_packages_from_dict()
        self.db.create_tester_info_table()



    def install_requirements(self) -> list[str]:
        prefix = self._pick_external_python_for_setup()
        req = self._bundled_requirements_path()

        # make sure pip exists
        try:
            subprocess.run(prefix + ["-m", "pip", "--version"], check=True, capture_output=True, text=True)
        except Exception:
            subprocess.run(prefix + ["-m", "ensurepip", "--upgrade"], check=True)

        # install deps (try normal, then --user fallback)
        try:
            subprocess.run(prefix + ["-m", "pip", "install", "-r", str(req)], check=True)
        except subprocess.CalledProcessError:
            subprocess.run(prefix + ["-m", "pip", "install", "--user", "-r", str(req)], check=True)

        # quick sanity check
        subprocess.run(prefix + ["-c", "import pytest; import selenium; import PySide6"], check=True)

        return prefix

    @staticmethod
    def _pick_external_python_for_setup() -> list[str]:
        py = os.getenv("RTVS_PYTHON")
        if py and Path(py).exists():
            return [py]

        py_launcher = shutil.which("py")
        if py_launcher:
            return [py_launcher, "-3"]

        py_on_path = shutil.which("python")
        if py_on_path:
            return [py_on_path]

        raise RuntimeError("Python not found. Install Python or set RTVS_PYTHON.")

    @staticmethod
    def _bundled_requirements_path() -> Path:
        # PyInstaller onefile extracts to sys._MEIPASS
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
            p = base / "requirements.txt"
            if p.exists():
                return p

        # dev fallbacks
        for p in [
            Path.cwd() / "requirements.txt",
            Path(__file__).resolve().parent.parent / "requirements.txt",
        ]:
            if p.exists():
                return p

        raise RuntimeError("requirements.txt not found.")



    # Run onfiguration interactors
    def set_run_configuration(self, run_config: RunConfiguration):
        # Set the current run configuration
        self.run_config = run_config

    def get_run_configuration(self):
        # Get the current run configuration
        return self.run_config

    def set_env(self, env: str):
        if self.run_config:
            self.run_config.env = env
    def set_category(self, category: str):
        if self.run_config:
            self.run_config.category = category
    def set_test_package(self, test_package: str):
        if self.run_config:
            self.run_config.test_package = test_package
    def set_test_name(self, test_name: str):
        if self.run_config:
            self.run_config.test_name = test_name
    def set_browser(self, browser: str):
        if self.run_config:
            self.run_config.browser = browser
    def set_client_id(self, client_id: int):
        if self.run_config:
            self.run_config.client_id = client_id
    def set_timestamp(self, timestamp: str):
        if self.run_config:
            self.run_config.timestamp = timestamp
    def set_unique_id(self):
        if self.run_config:
            import uuid
            self.run_config.unique_id = str(uuid.uuid4())
    def set_prefix(self, prefix: str):
        if self.run_config:
            self.run_config.prefix = prefix
    def set_multiprocessing(self, multiprocessing: bool):
        if self.run_config:
            self.run_config.multiprocessing = multiprocessing
    def set_threads(self, threads: int):
        if self.run_config:
            self.run_config.threads = threads

    def create_run_id(self):
        if self.run_config:
            parts = [
                self.run_config.prefix,
                self.run_config.category or "CAT",
                self.run_config.env or "ENV",
                self.run_config.test_package or "PKG",
                self.run_config.started_at or "TIME",
                self.run_config.unique_id or "UID"
            ]
            self.run_config.run_id = "_".join(parts)
            return self.run_config.run_id
        return None


    # Chrome profile interactors
    def display_profiles(self, browser_name='chrome'):
        # Display current chrome profiles
        if browser_name.lower() == 'chrome':
            self.db.display_chrome_profiles()

    def update_profile_mfa_time(self, profile_name, browser_name='chrome'):
        # Update the MFA time for a given profile
        if browser_name.lower() == 'chrome':
            print(f"Updating MFA time for profile {profile_name}.")
            self.db.edit_chrome_profile_table(change_type='UPDATE_MFA_TIME', profile_name=profile_name)

    def set_profile_active(self, profile_name, browser_name='chrome'):
        # Set a given profile as active
        if browser_name.lower() == 'chrome':
            print(f"Setting profile {profile_name} as active.")
            self.db.edit_chrome_profile_table(change_type='SET_ACTIVE_PROFILE', profile_name=profile_name)

    def set_profile_inactive(self, profile_name, browser_name='chrome'):
        # Set a given profile as inactive
        if browser_name.lower() == 'chrome':
            print(f"Setting profile {profile_name} as inactive.")
            self.db.edit_chrome_profile_table(change_type='SET_INACTIVE_PROFILE', profile_name=profile_name)

    # def fetch_first_inactive_profile(self, browser_name='chrome'):
    #     # Fetch and return inactive profiles
    #     if browser_name.lower() == 'chrome':
    #         rows = self.db.get_inactive_chrome_profiles()
    #         if not rows:
    #             return None
    #         inactive_profile = rows[0][1]
    #         self.set_profile_active(inactive_profile, browser_name)
    #         return inactive_profile
    #     return None

    def fetch_first_inactive_profile(self, browser_name: str = "chrome", run_id: str | None = None):
        if browser_name.lower() != "chrome":
            return None

        tag = run_id or "no_run_id"
        claimed_by = f"{tag}|pid={os.getpid()}"

        return self.db.claim_first_inactive_chrome_profile(claimed_by=claimed_by)

    # Customer table interactors
    def get_role_dict_for_customer_id(self, customer_id: int) -> dict:
        # Get role dictionary for a given customer ID
        return self.db.get_role_dict_for_customer_id(customer_id)

    def update_username_for_role(self, customer_id: int, role: str, new_username: str):
        # Update username for a specific role under a customer ID
        self.db.update_username_for_role(customer_id, role, new_username)

    # Test_log interactors and run_id stuff

    def set_test_context(
            self,
            *,
            test_name: str | None = None,
            test_package: str | None = None,
            client_id: int | None = None,
            user_role: str | None = None,
            user_name: str | None = None,
            browser: str | None = None,
            browser_profile: str | None = None,
    ) -> None:
        rc = self._require_rc()

        if test_name is not None:
            rc.test_name = test_name
        if test_package is not None:
            rc.test_package = test_package
        if client_id is not None:
            rc.client_id = client_id
        if user_role is not None:
            rc.user_role = user_role
        if user_name is not None:
            rc.user_name = user_name
        if browser is not None:
            rc.browser = browser
        if browser_profile is not None:
            rc.browser_profile = browser_profile


    def _require_rc(self) -> RunConfiguration:
        if not self.run_config:
            raise RuntimeError("RunConfiguration is not initialized on ConfigAssists.")
        if not self.run_config.run_id:
            raise RuntimeError("run_id is missing. Create/load run_id once per session.")
        return self.run_config

    def _safe_current_url(self, driver) -> str | None:
        if driver is None:
            return None
        try:
            return driver.current_url
        except Exception:
            return None

    def _get_worker(self) -> str:
        return os.getenv("PYTEST_XDIST_WORKER", "local")

    def _get_pid(self) -> int:
        try:
            return int(os.getpid())
        except Exception:
            return -1

    def _log(self, *, type_: str, message: str, status: str = "Info", driver=None, current_url: str | None = None, test_name: str | None = None, extra: dict[str, Any] | None = None, mark_fail: bool = False) -> None:
        rc = self._require_rc()

        # Allow caller override, else use driver, else None
        url = current_url if current_url is not None else self._safe_current_url(driver)

        # Pick test name: explicit > rc.test_name
        tn = test_name or rc.test_name

        # Worker/pid defaults if not already set
        worker = rc.worker or self._get_worker()
        pid = rc.pid if isinstance(rc.pid, int) else self._get_pid()

        # Browser/profile defaults
        browser = rc.browser
        profile = rc.browser_profile
        if driver is not None and hasattr(driver, "_rtvs_profile"):
            profile = profile or getattr(driver, "_rtvs_profile", None)

        # Optional: merge extras into other_info just for debugging
        if extra:
            rc.other_info = rc.other_info or {}
            rc.other_info.update(extra)

        self.db.insert_test_log(
            run_id=rc.run_id,
            type_=type_,
            status=status,
            message=message,
            browser=browser,
            test_package=rc.test_package,
            test_name=tn,
            client_id=rc.client_id,
            user_role=rc.user_role,
            user_name=rc.user_name,
            pid=pid,
            worker=worker,
            current_url=url,
        )

        if mark_fail:
            self.db.mark_test_failure(rc.run_id, message=message)

    # test facing helpers
    def add_log_start(self, message: str = "Test started", *, driver=None, status: str = "Info") -> None:
        self._log(type_="start", message=message, status=status, driver=driver)

    def add_log_test_case(self, message: str, *, driver=None, status: str = "Info") -> None:
        self._log(type_="test_case", message=message, status=status, driver=driver)

    def add_log_update(self, message: str, *, driver=None, status: str = "Success",
                     current_url: str | None = None) -> None:
        self._log(type_="update", message=message, status=status, driver=driver, current_url=current_url)

    def add_log_end(self, message: str = "Test finished", *, driver=None, status: str = "Success") -> None:
        self._log(type_="end", message=message, status=status, driver=driver)

    def add_log_skip(self, message: str, *, driver=None, status: str = "Skipped") -> None:
        self._log(type_="force_skip", message=message, status=status, driver=driver)

    def add_log_error(self, message: str, *, driver=None, status: str = "Error") -> None:
        self._log(type_="error", message=message, status=status, driver=driver, mark_fail=True)

    def add_log_heartbeat(self, message: str = "heartbeat", *, status="Info", driver=None) -> None:
        self._log(type_="heartbeat", message=message, status=status, driver=driver)







