import os
from dataclasses import dataclass
from config.rtvsdb import RTVSDB
from core.config import Config

@dataclass
class RunConfiguration:
    run_id: str | None = None
    env: str | None = None
    category: str | None = None
    test_package: str | None = None
    test_name: str | None = None
    browser: str | None = None
    started_at: str | None = None
    timestamp: str | None = None
    ended_at: str | None = None
    unique_id: str | None = None
    prefix: str = "RTVS"
    multiprocessing: bool = False
    threads: int = 1
    client_id: int | None = None
    other_info: dict | None = None

class ConfigAssists:

    BROWSER = Config.get_browser()
    ENV = Config.get_test_env()

    def __init__(self):
        self.db = RTVSDB()
        self.run_config: RunConfiguration | None = None
        self.set_run_configuration(RunConfiguration())

    def create_first_time_setup(self):
        # Create the chrome_profiles table if it doesn't exist
        self.db.create_chrome_profile_info_table()
        # Initialize the table with default profiles
        self.db.initialize_chrome_profiles(profile_count=5)
        self.db.create_customer_tables()
        self.db.load_customer_json_into_db()
        self.db.create_test_activity_table()

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
                self.run_config.browser or "BROWSER",
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

    def fetch_first_inactive_profile(self, browser_name='chrome'):
        # Fetch and return inactive profiles
        if browser_name.lower() == 'chrome':
            rows = self.db.get_inactive_chrome_profiles()
            if not rows:
                return None
            inactive_profile = rows[0][1]
            self.set_profile_active(inactive_profile, browser_name)
            return inactive_profile
        return None

    # Customer table interactors
    def get_role_dict_for_customer_id(self, customer_id: int) -> dict:
        # Get role dictionary for a given customer ID
        return self.db.get_role_dict_for_customer_id(customer_id)

    def update_username_for_role(self, customer_id: int, role: str, new_username: str):
        # Update username for a specific role under a customer ID
        self.db.update_username_for_role(customer_id, role, new_username)

    # Test activity log interactors and run_id stuff




