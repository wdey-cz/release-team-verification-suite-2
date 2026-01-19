import sqlite3
import json
import os
import time
from pathlib import Path

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
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    ASSETS_DIR = PROJECT_ROOT / "assets"
    DEFAULT_DB_PATH = ASSETS_DIR / "rtvs_database.db"


    def __init__(self, db_path: str | Path | None = None):

        # self.assets_dir = find_assets_dir()
        # db_path = self.assets_dir / "rtvs_database.db"
        # db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(db_path).resolve() if db_path else self.DEFAULT_DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.db_path), timeout=5)
        self.cursor = self.connection.cursor()
        self.connection.execute('PRAGMA foreign_keys = ON;')
        self.connection.execute("PRAGMA journal_mode=WAL;")
        self.connection.execute("PRAGMA busy_timeout = 5000;")

        # Initialize tables
        self.create_chrome_profile_info_table()
        self.create_customer_tables()
        self.create_test_activity_table()

        # Commit any initial changes
        self.connection.commit()

    @property
    def _db_path(self) -> Path:
        return self.db_path

    def check_if_table_exists(self, table_name):
        """Check if a table exists in the database."""
        self.cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name=?;
        """, (table_name,))
        return self.cursor.fetchone() is not None

    def create_table(self, table_name, columns):
        """Create a table with the specified columns."""
        columns_with_types = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        with self.connection:
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types});
            """)

    def run_query(self, query, params=()):
        """Run a custom query with optional parameters."""
        with self.connection:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.connection.close()

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
            self.cursor.executemany(
                """
                INSERT INTO chrome_profiles (profile_name, currently_running, is_active)
                VALUES (?, ?, ?)
                ON CONFLICT(profile_name) DO NOTHING;
                """,
                profiles,
            )

    def display_chrome_profiles(self):
        """Display the Chrome profiles in the database."""
        self.cursor.execute("SELECT * FROM chrome_profiles;")
        profiles = self.cursor.fetchall()
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
                self.cursor.execute("""
                    UPDATE chrome_profiles
                    SET last_mfa_time = {}
                    WHERE profile_name = '{}';
                """.format(timestamp, profile_name))
        if change_type == 'SET_ACTIVE_PROFILE' and profile_name:
            # this will look for profile name and set its only its is active to 1.
            print(f"Setting profile {profile_name} as active.")
            with self.connection:
                self.cursor.execute("""
                    UPDATE chrome_profiles
                    SET is_active = 1
                    WHERE profile_name = ?;
                """, (profile_name,))
        if change_type == 'SET_INACTIVE_PROFILE' and profile_name:
            # this will look for profile name and set its only its is active to 0.
            print(f"Setting profile {profile_name} as inactive.")
            with self.connection:
                self.cursor.execute("""
                    UPDATE chrome_profiles
                    SET is_active = 0
                    WHERE profile_name = ?;
                """, (profile_name,))

    def get_inactive_chrome_profiles(self):
        """Fetch and return all inactive Chrome profiles."""
        self.cursor.execute("""
            SELECT c.id,c.profile_name, c.is_active FROM chrome_profiles c WHERE is_active = 0;
        """)
        return self.cursor.fetchall()

    # DB Functions for the Customer table
    def create_customer_tables(self):
        with self.connection:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
              customer_id   INTEGER PRIMARY KEY,
              customer_name TEXT NOT NULL,
              updated_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_accounts (
              customer_id INTEGER NOT NULL,
              role        TEXT NOT NULL,
              username    TEXT NOT NULL,
              updated_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (customer_id, role),
              FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            );
            """)

            self.cursor.execute("""
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
            for c in customers:
                customer_id = int(c["id"])
                customer_name = str(c["name"]).strip()
                accounts = c.get("accounts", [])

                # 1) Upsert customer (portable)
                self.cursor.execute(
                    """
                    UPDATE customers
                    SET customer_name = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE customer_id = ?;
                    """,
                    (customer_name, customer_id)
                )

                if self.cursor.rowcount == 0:
                    self.cursor.execute(
                        """
                        INSERT INTO customers (customer_id, customer_name, updated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP);
                        """,
                        (customer_id, customer_name)
                    )

                # 2) Overwrite roles for this customer_id
                self.cursor.execute(
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
                    self.cursor.executemany(
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
        self.cursor.execute(*query)
        rows = self.cursor.fetchall()
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
        self.cursor.execute(*query)
        row = self.cursor.fetchone()
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
        self.cursor.execute(*query)
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return None

    def get_comma_separated_customer_ids(self):
        """Get all customer IDs as a comma-separated string."""
        query = "SELECT customer_id FROM customers;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        customer_ids = [str(row[0]) for row in rows]
        return ",".join(customer_ids)

    def update_username_for_role(self, customer_id, role, new_username):
        """Update the username for a specific role of a customer."""
        with self.connection:
            self.cursor.execute("""
                UPDATE customer_accounts
                SET username = ?, updated_at = CURRENT_TIMESTAMP
                WHERE customer_id = ? AND role = ?;
            """, (new_username, customer_id, role))

    # db Functions for the test_activity table
    def create_test_activity_table(self):
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

        test_activity_table_query = """
        CREATE TABLE IF NOT EXISTS test_activity (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id           TEXT NOT NULL,
            test_name        TEXT NOT NULL,
            profile_name     TEXT NOT NULL,
            status           TEXT NOT NULL DEFAULT 'RUNNING',
            pid              INTEGER,
            worker           TEXT,
            started_at       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_heartbeat   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            finished_at      TEXT,
            message          TEXT,

            UNIQUE (run_id, test_name, pid)
        );      
        """
        test_activity_status_index_query = """
        CREATE INDEX IF NOT EXISTS idx_test_activity_status ON test_activity(status);
        """
        test_activity_runid_index_query = """
        CREATE INDEX IF NOT EXISTS idx_test_activity_runid ON test_activity(run_id);
        """
        test_activity_profile_index_query = """
        CREATE INDEX IF NOT EXISTS idx_test_activity_profile ON test_activity(profile_name);
        """
        self.run_query(test_activity_table_query)
        self.run_query(test_activity_status_index_query)
        self.run_query(test_activity_runid_index_query)
        self.run_query(test_activity_profile_index_query)

    def upsert_test_start(self, run_id: str, test_name: str, profile_name: str, pid: int | None = None, worker: str | None = None):
        """ Usage:
        db.upsert_test_start(
            run_id="RTVS-REG-STAGE-ComboPack1-20231101_101015-5678-AnotherSuffix",
            test_name="Combo Pack 1 : Sidebars, Registries, MSPLs, Patient Dashboard, Analytics Pack",
            profile_name="ChromeTestProfile2",
            pid=pid, (optional)
            worker="worker2"
            )
        """
        with self.connection:
            # First try update (portable)
            self.cursor.execute("""
                        UPDATE test_activity
                        SET status='RUNNING', last_heartbeat=CURRENT_TIMESTAMP, message=NULL
                        WHERE run_id=? AND test_name=? AND pid IS ?;
                    """, (run_id, test_name, pid))
            if self.cursor.rowcount == 0:
                self.cursor.execute("""
                            INSERT INTO test_activity (run_id, test_name, profile_name, status, pid, worker)
                            VALUES (?, ?, ?, 'RUNNING', ?, ?);
                        """, (run_id, test_name, profile_name, pid, worker))
        print(f"Test {test_name} in run {run_id} started or updated.")

    def heartbeat_test(self, run_id: str, test_name: str, pid: int | None = None, message: str | None = None):
        """ Usage:
        db.heartbeat_test(
            run_id="RTVS-REG-STAGE-AnalyticsPack-20231101_101015-5678-AnotherSuffix",
            test_name="Analytics Regression Pack",
            pid=pid,
            message="Heartbeat updated after 5 seconds"
            )
        """
        with self.connection:
            self.cursor.execute("""
                UPDATE test_activity
                SET last_heartbeat=CURRENT_TIMESTAMP,
                    message = COALESCE(?, message)
                WHERE run_id=? AND test_name=? AND pid IS ? AND status='RUNNING';
            """, (message, run_id, test_name, pid))
        print(f"Heartbeat updated for test {test_name} in run {run_id}.")

    def finish_test(self, run_id: str, test_name: str, status: str, pid: int | None = None, message: str | None = None):
        """
        Usage:
        db.finish_test(
            run_id="RTVS-REG-STAGE-AnalyticsPack-20231101_101015-5678-AnotherSuffix",
            test_name="Analytics Regression Pack",
            status="FINISHED",
            pid=pid,
            message="Test completed successfully"
        )
        """
        with self.connection:
            self.cursor.execute("""
                UPDATE test_activity
                SET status=?,
                    finished_at=CURRENT_TIMESTAMP,
                    last_heartbeat=CURRENT_TIMESTAMP,
                    message=?
                WHERE run_id=? AND test_name=? AND pid IS ?;
            """, (status, message, run_id, test_name, pid))

    def fetch_current_tests(self, only_running: bool = False):
        q = """
            SELECT run_id, test_name, profile_name, status, pid, worker, started_at, last_heartbeat, finished_at, message
            FROM test_activity
        """
        params = []
        if only_running:
            q += " WHERE status='RUNNING' "
        q += " ORDER BY started_at DESC, last_heartbeat DESC;"
        self.cursor.execute(q, params)
        return self.cursor.fetchall()

    def mark_stale_running_as_crashed(self, stale_seconds: int = 120):
        # Anything RUNNING but not updated in N seconds becomes CRASHED
        # when to use : db.mark_stale_running_as_crashed(stale_seconds=120)
        with self.connection:
            self.cursor.execute("""
                UPDATE test_activity
                SET status='CRASHED', finished_at=CURRENT_TIMESTAMP, message=COALESCE(message, 'stale heartbeat')
                WHERE status='RUNNING'
                  AND (strftime('%s','now') - strftime('%s', last_heartbeat)) > ?;
            """, (stale_seconds,))


# Example usage
if __name__ == "__main__":
    db = RTVSDB()
    print(sqlite3.sqlite_version)
    # usage: db.upsert_test_start(run_id="run123", test_name="test_login", profile_name="ChromeTestProfile1", pid=12345, worker="worker1")
    pid = None
    db.upsert_test_start(
        run_id="RTVS-REG-STAGE-AnalyticsPack-20231101_101015-5679-AnotherSuffix",
        test_name="Analytics Regression Pack",
        profile_name="ChromeTestProfile1",
        pid=pid,
        worker="worker1"
    )
    # db.upsert_test_start(
    #     run_id="RTVS-REG-STAGE-ComboPack1-20231101_101015-5678-AnotherSuffix",
    #     test_name="Combo Pack 1 : Sidebars, Registries, MSPLs, Patient Dashboard, Analytics Pack",
    #     profile_name="ChromeTestProfile2",
    #     pid=pid,
    #     worker="worker2"
    # )
    # # usage: db.heartbeat_test(run_id="run123", test_name="test_login", pid=12345, message="Still running")
    # time.sleep(5)
    # db.heartbeat_test(
    #     run_id="RTVS-REG-STAGE-AnalyticsPack-20231101_101015-5678-AnotherSuffix",
    #     test_name="Analytics Regression Pack",
    #     pid=pid,
    #     message="Heartbeat updated after 5 seconds"
    #
    # )
    # print("heartbeat sent")
    # time.sleep(5)
    # db.heartbeat_test(
    #     run_id="RTVS-REG-STAGE-ComboPack1-20231101_101015-5678-AnotherSuffix",
    #     test_name="Combo Pack 1 : Sidebars, Registries, MSPLs, Patient Dashboard, Analytics Pack",
    #     pid=pid,
    #     message="Heartbeat updated after 10 seconds"
    #
    # )
    # print("heartbeat sent")
    # time.sleep(5)
    # # usage: db.finish_test(run_id="run123", test_name="test_login", status="PASSED", pid=12345, message="Test completed successfully")
    # db.finish_test(
    #     run_id="RTVS-REG-STAGE-AnalyticsPack-20231101_101015-5678-AnotherSuffix",
    #     test_name="Analytics Regression Pack",
    #     status="FINISHED",
    #     pid=pid,
    #     message="Test completed successfully"
    # )
    # print("Test finished")
    # time.sleep(5)
    # db.finish_test(
    #     run_id="RTVS-REG-STAGE-ComboPack1-20231101_101015-5678-AnotherSuffix",
    #     test_name="Combo Pack 1 : Sidebars, Registries, MSPLs, Patient Dashboard, Analytics Pack",
    #     status="ERRORED",
    #     pid=pid,
    #     message="Some Error Bro, pls check it out"
    # )
    # print("Test finished")

    db.close()
