import sqlite3
import json
import os
import time
from pathlib import Path
from core.config import Config

'''
This module is collection of all DB based informaton required for the functioning of RTVS.
Functions :

'''


def find_assets_dir() -> Path:
    """
    Finds the nearest 'assets' directory by searching upward from:
      1) current working directory
      2) this file's directory
    Also supports overriding via env var RTVS_ROOT.
    """
    # Optional override
    env_root = os.getenv("RTVS_ROOT")
    if env_root:
        p = Path(env_root).expanduser().resolve() / "assets"
        if p.is_dir():
            return p

    candidates = [
        Path.cwd().resolve(),
        Path(__file__).resolve().parent,
    ]

    for start in candidates:
        for p in [start] + list(start.parents):
            assets = p / "assets"
            if assets.is_dir():
                return assets

    # Fallback: create assets next to this file's parent (safe default)
    fallback = Path(__file__).resolve().parent / "assets"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


class RTVSDB:

    #Class Attributes
    PROJECT_ROOT = Config.RTVS_PROJECT_ROOT
    ASSETS_DIR = Config.RTVS_ASSETS_DIR
    DEFAULT_DB_PATH = Config.RTVS_DEFAULT_DB_PATH
    #


    def __init__(self, db_path: str | Path | None = None):

        # self.assets_dir = find_assets_dir()
        # db_path = self.assets_dir / "rtvs_database.db"
        # db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(db_path).resolve() if db_path else self.DEFAULT_DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.db_path), timeout=5, check_same_thread=True)
        self.cursor = self.connection.cursor()
        self.connection.execute('PRAGMA foreign_keys = ON;')
        self.connection.execute("PRAGMA journal_mode=WAL;")
        self.connection.execute("PRAGMA synchronous = NORMAL;")
        self.connection.execute("PRAGMA busy_timeout = 30000;")

        # Initialize tables
        self.create_chrome_profile_info_table()
        self.create_customer_tables()
        self.create_run_and_log_tables()
        self.create_test_package_table()

        # Commit any initial changes
        self.connection.commit()

    @property
    def _db_path(self) -> Path:
        return self.db_path

    def check_if_table_exists(self, table_name):
        """Check if a table exists in the database."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name=?;
        """, (table_name,))
        return cursor.fetchone() is not None

    def create_table(self, table_name, columns):
        """Create a table with the specified columns."""
        columns_with_types = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types});
            """)

    def run_query(self, query, params=()):
        """Run a custom query with optional parameters."""
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.connection.close()

    # DB functions for the master test package table
    def create_test_package_table(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_packages (
              id                    INTEGER PRIMARY KEY AUTOINCREMENT,
              test_package_name     TEXT NOT NULL UNIQUE,
              test_package_category TEXT NOT NULL,
              test_package_desc     TEXT NOT NULL,
              available_to          TEXT NOT NULL,
              updated_at            TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)

    def fetch_regression_test_packages(self):
        """Fetch all test packages categorized as 'REG'."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT test_package_name, test_package_desc 
            FROM test_packages 
            WHERE test_package_category = 'REG';
        """)
        return [tp[0] for tp in cursor.fetchall()]



    def fetch_data_integrity_test_packages(self):
        """Fetch all test packages categorized as 'DATA_INTEGRITY'."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT test_package_name, test_package_desc 
            FROM test_packages 
            WHERE test_package_category = 'DATA';
        """)
        return [tp[0] for tp in cursor.fetchall()]

    def fetch_test_package_description(self, name: str) -> str | None:
        """Fetch the description of a test package by name."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT test_package_desc 
            FROM test_packages 
            WHERE test_package_name = ?;
        """, (name,))
        row = cursor.fetchone()
        return row[0] if row else None


    def insert_test_package(self, name: str, category: str, desc: str, available_to: str):
        """Insert a new test package into the database.
        args:
            name: Name of the test package
            category: Category of the test package (e.g., 'REG', 'DATA')
            desc: Description of the test package
            available_to: Who the test package is available to (e.g., 'ALL', 'CS', 'RS', 'LCS', 'CU', 'OAPD', 'ALL_VIEW')
        """
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO test_packages (test_package_name, test_package_category, test_package_desc, available_to)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(test_package_name) DO UPDATE SET
                  test_package_category=excluded.test_package_category,
                  test_package_desc=excluded.test_package_desc,
                  available_to=excluded.available_to,
                  updated_at=CURRENT_TIMESTAMP;
            """, (name, category, desc, available_to))


    # DB Functions for Chrome Profile Info Table
    def create_chrome_profile_info_table(self):
        """Create the Chrome profile table if it doesn't exist."""
        default_timestamp = '2020-01-01 00:00:00'
        columns = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'profile_name': 'TEXT NOT NULL UNIQUE',
            'currently_running': 'TEXT',
            'is_active': 'BOOLEAN NOT NULL DEFAULT 0',
            'last_mfa_time': f"TEXT NOT NULL DEFAULT '{default_timestamp}'",
        }
        self.create_table('chrome_profiles', columns)

    def initialize_chrome_profiles(self, profile_count: int = 5, name_prefix: str = "ChromeTestProfile"):
        """
        Initialize chrome_profiles with default profiles (idempotent).
        Creates rows: ChromeTestProfile1...N with profile_path NULL and is_active 0.
        """
        if profile_count <= 0:
            return

        profiles = [(f"{name_prefix}{i}", "Not running, MFA Expired", 0) for i in range(1, profile_count + 1)]

        with self.connection:
            cursor = self.connection.cursor()
            cursor.executemany(
                """
                INSERT INTO chrome_profiles (profile_name, currently_running, is_active)
                VALUES (?, ?, ?)
                ON CONFLICT(profile_name) DO NOTHING;
                """,
                profiles,
            )

    def display_chrome_profiles(self):
        """Display the Chrome profiles in the database."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM chrome_profiles;")
        profiles = cursor.fetchall()
        for profile in profiles:
            print(profile)

    def edit_chrome_profile_table(self, change_type='UPDATE_MFA_TIME', profile_name=None, timestamp='CURRENT_TIMESTAMP'):
        """Edit the Chrome profile table based on the change type.
        Args:
            change_type: Type of change to make ('UPDATE_MFA_TIME', 'SET_ACTIVE_PROFILE', 'SET_INACTIVE_PROFILE')
            profile_name: Name of the profile to update
            timestamp: Timestamp to set for MFA time (default is CURRENT_TIMESTAMP)
        usage:
            db.edit_chrome_profile_table(change_type='UPDATE_MFA_TIME', profile_name=profile_name, timestamp='2020-01-01 0:00:00')

        """
        if change_type == 'UPDATE_MFA_TIME' and profile_name:
            print(f"Updating MFA time for profile {profile_name} to {timestamp}.")
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("""
                    UPDATE chrome_profiles
                    SET last_mfa_time = {}
                    WHERE profile_name = '{}';
                """.format(timestamp, profile_name))
        if change_type == 'SET_ACTIVE_PROFILE' and profile_name:
            # this will look for profile name and set its only its is active to 1.
            # print(f"Setting profile {profile_name} as active.")
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("""
                    UPDATE chrome_profiles
                    SET is_active = 1
                    WHERE profile_name = ?;
                """, (profile_name,))
        if change_type == 'SET_INACTIVE_PROFILE' and profile_name:
            # this will look for profile name and set its only its is active to 0.
            # print(f"Setting profile {profile_name} as inactive.")
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("""
                    UPDATE chrome_profiles
                    SET is_active = 0
                    WHERE profile_name = ?;
                """, (profile_name,))

    def get_inactive_chrome_profiles(self):
        """Fetch and return all inactive Chrome profiles."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT c.id,c.profile_name, c.is_active FROM chrome_profiles c WHERE is_active = 0;
        """)
        return cursor.fetchall()

    # DB Functions for the Customer table
    def create_customer_tables(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
              customer_id   INTEGER PRIMARY KEY,
              customer_name TEXT NOT NULL,
              updated_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_accounts (
              customer_id INTEGER NOT NULL,
              role        TEXT NOT NULL,
              username    TEXT NOT NULL,
              updated_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (customer_id, role),
              FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            );
            """)

            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customer_accounts_customer
            ON customer_accounts(customer_id);
            """)

    def load_customer_json_into_db(self, json_path="customers1.json"):
        with open(os.path.join(self.ASSETS_DIR, json_path), "r", encoding="utf-8") as f:
            doc = json.load(f)

        customers = doc.get("customers", [])
        if not isinstance(customers, list):
            raise ValueError("JSON format error: 'customers' must be a list")

        with self.connection:  # one transaction
            cursor = self.connection.cursor()
            for c in customers:
                customer_id = int(c["id"])
                customer_name = str(c["name"]).strip()
                accounts = c.get("accounts", [])

                # 1) Upsert customer (portable)
                cursor.execute(
                    """
                    UPDATE customers
                    SET customer_name = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE customer_id = ?;
                    """,
                    (customer_name, customer_id)
                )

                if cursor.rowcount == 0:
                    cursor.execute(
                        """
                        INSERT INTO customers (customer_id, customer_name, updated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP);
                        """,
                        (customer_id, customer_name)
                    )

                # 2) Overwrite roles for this customer_id
                cursor.execute(
                    "DELETE FROM customer_accounts WHERE customer_id = ?;",
                    (customer_id,)
                )

                # 3) Insert accounts
                rows = []
                for a in accounts:
                    role = str(a["role"]).strip()
                    username = str(a["username"]).strip()
                    rows.append((customer_id, role, username))

                if rows:
                    cursor.executemany(
                        """
                        INSERT INTO customer_accounts (customer_id, role, username, updated_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP);
                        """,
                        rows
                    )

    def get_role_dict_for_customer_id(self, customer_id):
        """Get all roles for a given customer ID."""
        query = ("""
                SELECT c.customer_id, c.customer_name, a.role, a.username
                FROM customers c
                JOIN customer_accounts a ON a.customer_id = c.customer_id
                WHERE c.customer_id = ?;
            """, (customer_id,))  # example customer_id = 1
        cursor = self.connection.cursor()
        cursor.execute(*query)
        rows = cursor.fetchall()
        role_dict = {}
        for customer_id, customer_name, role, username in rows:
            temp_dict = {role: username}
            role_dict.update(temp_dict)
        return role_dict

    def get_customer_name_from_id(self, customer_id):
        """Get customer name for a given customer ID."""
        query = ("""
                SELECT customer_name
                FROM customers
                WHERE customer_id = ?;
            """, (customer_id,))  # example customer_id = 1
        cursor = self.connection.cursor()

        cursor.execute(*query)
        row = cursor.fetchone()
        if row:
            return row[0]
        return None

    def get_customer_id_from_name(self, customer_name):
        """Get customer ID for a given customer name."""
        query = ("""
                SELECT customer_id
                FROM customers
                WHERE customer_name = ?;
            """, (customer_name,))  # example customer_name = "Acme Corp"
        cursor = self.connection.cursor()

        cursor.execute(*query)
        row = cursor.fetchone()
        if row:
            return row[0]
        return None

    def get_comma_separated_customer_ids(self):
        """Get all customer IDs as a comma-separated string."""
        query = "SELECT customer_id FROM customers;"
        cursor = self.connection.cursor()

        cursor.execute(query)
        rows = cursor.fetchall()
        customer_ids = [str(row[0]) for row in rows]
        return ",".join(customer_ids)

    def get_customer_names_list(self):
        """Get all customer names as a list."""
        query = "SELECT customer_name FROM customers;"
        cursor = self.connection.cursor()

        cursor.execute(query)
        rows = cursor.fetchall()
        customer_names = [row[0] for row in rows]
        return customer_names

    def get_total_customers_count(self):
        """Get the total number of customers in the database."""
        query = "SELECT COUNT(*) FROM customers;"
        cursor = self.connection.cursor()

        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return row[0]
        return 0

    def update_username_for_role(self, customer_id, role, new_username):
        """Update the username for a specific role of a customer."""
        with self.connection:
            cursor = self.connection.cursor()

            cursor.execute("""
                UPDATE customer_accounts
                SET username = ?, updated_at = CURRENT_TIMESTAMP
                WHERE customer_id = ? AND role = ?;
            """, (new_username, customer_id, role))

    # DB Functions for the Test Runs and Test Logs Tables
    def create_run_and_log_tables(self):
        with self.connection:
            cursor = self.connection.cursor()

            cursor.executescript("""
            CREATE TABLE IF NOT EXISTS test_runs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT NOT NULL UNIQUE,
              prefix TEXT NOT NULL DEFAULT 'RTVS',
              category TEXT NOT NULL,
              env TEXT NOT NULL,
              test_package TEXT NOT NULL,
              test_package_desc TEXT,
              browsers TEXT NOT NULL,
              clients TEXT,
              user_roles TEXT,
              threads INTEGER NOT NULL DEFAULT 1,
              multiprocessing INTEGER NOT NULL DEFAULT 0,
              started_at TEXT NOT NULL,
              ended_at TEXT,
              status TEXT NOT NULL DEFAULT 'RUNNING',
              failed_cases INTEGER NOT NULL DEFAULT 0,
              last_heartbeat_at TEXT,
              last_update_at TEXT,
              last_update_message TEXT,
              unique_id TEXT NOT NULL,
              other_info_json TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_test_runs_run_id ON test_runs(run_id);
            CREATE INDEX IF NOT EXISTS idx_test_runs_status ON test_runs(status);

            CREATE TABLE IF NOT EXISTS test_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT NOT NULL,
              type TEXT NOT NULL,
              browser TEXT,
              test_package TEXT,
              test_name TEXT,
              client_id INTEGER,
              user_role TEXT,
              user_name TEXT,
              pid INTEGER,
              worker TEXT,
              status TEXT,
              message TEXT,
              timestamp TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
              current_url TEXT,
              FOREIGN KEY (run_id) REFERENCES test_runs(run_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_test_logs_run_id ON test_logs(run_id);
            CREATE INDEX IF NOT EXISTS idx_test_logs_run_id_ts ON test_logs(run_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_test_logs_run_id_test ON test_logs(run_id, test_name);
            """)

    def insert_test_run(self, rc) -> None: # controller will call this function
        other = json.dumps(rc.other_info or {}, ensure_ascii=False)

        with self.connection:
            cursor = self.connection.cursor()

            cursor.execute(
                """
                INSERT INTO test_runs (
                  run_id, prefix, category, env, test_package, test_package_desc,
                  browsers, clients, user_roles, threads, multiprocessing,
                  started_at, status, failed_cases, unique_id, other_info_json,
                  last_heartbeat_at, last_update_at, last_update_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'RUNNING', 0, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Run created')
                ON CONFLICT(run_id) DO UPDATE SET
                  category=excluded.category,
                  env=excluded.env,
                  test_package=excluded.test_package,
                  test_package_desc=excluded.test_package_desc,
                  browsers=excluded.browsers,
                  clients=excluded.clients,
                  user_roles=excluded.user_roles,
                  threads=excluded.threads,
                  multiprocessing=excluded.multiprocessing,
                  last_update_at=CURRENT_TIMESTAMP,
                  last_update_message='Run updated by controller'
                """,
                (
                    rc.run_id,
                    rc.prefix,
                    rc.category,
                    rc.env,
                    rc.test_package,
                    rc.test_package_desc,
                    rc.browsers,
                    rc.clients,
                    rc.user_roles,
                    rc.threads,
                    1 if rc.multiprocessing else 0,
                    rc.timestamp or rc.started_at,
                    rc.unique_id,
                    other,
                ),
            )

    def get_test_run_row(self, run_id: str) -> dict | None:
        cursor = self.connection.cursor()

        cursor.execute("SELECT * FROM test_runs WHERE run_id = ?;", (run_id,))
        row = cursor.fetchone()
        if not row:
            return None
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))

    def insert_test_log(
            self,
            run_id: str,
            type_: str,
            status: str,
            message: str,
            *,
            browser: str | None = None,
            test_package: str | None = None,
            test_name: str | None = None,
            client_id: int | None = None,
            user_role: str | None = None,
            user_name: str | None = None,
            pid: int | None = None,
            worker: str | None = None,
            current_url: str | None = None,
    ):
        with self.connection:
            cursor = self.connection.cursor()

            cursor.execute(
                """
                INSERT INTO test_logs (
                  run_id, type, browser, test_package, test_name,
                  client_id, user_role, user_name, pid, worker,
                  status, message, current_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run_id, type_, browser, test_package, test_name,
                    client_id, user_role, user_name, pid, worker,
                    status, message, current_url
                ),
            )
            cursor.execute(
                """
                UPDATE test_runs
                SET last_update_at = CURRENT_TIMESTAMP,
                    last_heartbeat_at = CURRENT_TIMESTAMP,
                    last_update_message = ?
                WHERE run_id = ?;
                """,
                (message[:250], run_id),
            )

    def mark_test_failure(self, run_id: str, message: str = "Test failed"):
        with self.connection:
            cursor = self.connection.cursor()

            cursor.execute(
                """
                UPDATE test_runs
                SET failed_cases = failed_cases + 1,
                    status = CASE
                        WHEN status IN ('ERR') THEN status
                        ELSE 'FAIL'
                    END,
                    last_update_at = CURRENT_TIMESTAMP,
                    last_update_message = ?
                WHERE run_id = ?;
                """,
                (message[:250], run_id),
            )

    def finish_run(self, run_id: str, final_status: str):
        with self.connection:
            cursor = self.connection.cursor()

            cursor.execute(
                """
                UPDATE test_runs
                SET ended_at = CURRENT_TIMESTAMP,
                    status = ?,
                    last_update_at = CURRENT_TIMESTAMP,
                    last_update_message = 'Run finished'
                WHERE run_id = ?;
                """,
                (final_status, run_id),
            )




# Example usage
if __name__ == "__main__":
    db = RTVSDB()
    print(sqlite3.sqlite_version)

    # test_packages_dict_list = [
    #     {"name": "SidebarTestPackage", "category": "REG", "desc": "Desc", "available_to": "ALL_BASE"},
    #     {"name": "AnalyticsTestPackage", "category": "REG", "desc": "Desc", "available_to": "ALL_BASE"},
    #     {"name": "BridgeRegressionPackage", "category": "REG", "desc": "Desc", "available_to": "ALL_BASE"},
    #     {"name": "RegistriesRegressionPackage", "category": "REG", "desc": "Desc", "available_to": "ALL_BASE"},
    #     {"name": "ChartListRegressionPackage", "category": "REG", "desc": "Desc", "available_to": "ALL_BASE"},
    #     {"name": "NavigationsRegressionPackage", "category": "REG", "desc": "Desc", "available_to": "ALL_BASE"},
    #     {"name": "CozevaComboPack1", "category": "REG", "desc": "Contains All of the above", "available_to": "ALL_BASE"},
    #
    #     {"name": "HomePageLanguagesRegressionPackage", "category": "REG", "desc": "Desc", "available_to": "ALL_BASE"},
    #     {"name": "HomePageComboPack1", "category": "REG", "desc": "Contains Languages and Search Regression", "available_to": "ALL_BASE"},
    #     {"name": "HomePageSearchRegressionPackage", "category": "REG", "desc": "Desc", "available_to": "ALL_BASE"},
    #
    #     {"name": "ClientScoresDaily", "category": "DATA", "desc": "Desc", "available_to": "CS"},
    #     {"name": "PracticeProviderDaily", "category": "DATA", "desc": "Desc", "available_to": "CS"}
    #
    #
    # ]
    #
    # for tp in test_packages_dict_list:
    #     db.insert_test_package(tp["name"], tp["category"], tp["desc"], tp["available_to"])

    # test_packages = db.fetch_regression_test_packages()
    #
    # for tp in test_packages:
    #     print(f"{tp[0]}:{tp[1]}")  # Each tp is a tuple (test_package_name, test_package_desc)


    print(db.fetch_regression_test_packages())



    db.close()
