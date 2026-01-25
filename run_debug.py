import os
import sys
import subprocess
from datetime import datetime
from multiprocessing import process

from config.config_assists import ConfigAssists
from core.rtvs_runner import build_lanes, print_plan, run_lanes_parallel




def main_single_process():
    # Force desired runtime config for this debug run
    os.environ["BROWSER"] = "chrome"
    os.environ["TEST_ENV"] = "PROD"
    os.environ["HEADLESS"] = "false"
    # multiprocess by clientids, user roles and browsers.

    marker = "HomePageComboPack1"
    client_id = "1000"
    user_role = "cs"
    user_name = "local_cs"

    ca = ConfigAssists()
    ca.create_first_time_setup()

    rc = ca.get_run_configuration()
    rc.prefix = "RTVS"
    rc.category = "REG"
    rc.env = os.getenv("TEST_ENV", "PROD")
    rc.test_package = marker
    rc.test_package_desc = "Home Page Combo Pack 1"
    rc.started_at = datetime.now().strftime("%Y%m%d_%H%M%S")
    rc.browser = os.getenv("BROWSER", "chrome")

    # store selection summary in run row
    rc.clients = client_id
    rc.user_roles = user_role
    rc.browsers = rc.browser
    rc.multiprocessing = False
    rc.threads = 1

    # stable unique id
    ca.set_unique_id()
    ca.create_run_id()

    # Insert run row
    ca.db.insert_test_run(rc)

    print("\n[RTVS] Inserted test_runs row:")
    print("  run_id:", rc.run_id)

    # Launch pytest
    cmd = [
        sys.executable, "-m", "pytest",
        "-m", marker,
        "-s",
        "--rtvs-run-id", rc.run_id,
        "--client-id", client_id,
        "--user-role", user_role,
        "--user-name", user_name,
        # Optional: point directly to your test file to keep it tight
        "tests/test_home_page.py",
    ]

    print("\n[RTVS] Running:")
    print(" ", " ".join(cmd))

    result = subprocess.run(cmd, env=os.environ.copy())
    exit_code = result.returncode

    print("\n[RTVS] pytest exit code:", exit_code)

    # Dump quick DB proof
    row = ca.db.get_test_run_row(rc.run_id)
    print("\n[RTVS] test_runs row after run:")
    for k in ["run_id", "status", "failed_cases", "started_at", "ended_at", "last_update_message"]:
        print(f"  {k}: {row.get(k)}")

    logs = ca.db.run_query(
        "SELECT id, type, test_name, status, message, timestamp FROM test_logs WHERE run_id = ? ORDER BY id DESC LIMIT 15;",
        (rc.run_id,)
    )
    print("\n[RTVS] Last 15 logs:")
    for r in reversed(logs):
        print(" ", r)

    ca.db.close()
    sys.exit(exit_code)


def main_multi_process():
    # Placeholder for future multi-process implementation
    # Force desired runtime config for this debug run
    # os.environ["BROWSER"] = "chrome"
    # os.environ["TEST_ENV"] = "PROD"
    # os.environ["HEADLESS"] = "false"
    # multiprocess by clientids, user roles and browsers.

    marker = "HomePageLanguagesRegressionPackage"
    clients = ["1000", "1500"]
    roles = ["Cozeva Support", "Regional Support"]
    browsers = ["chrome"]

    # Toggle these
    mp_clients = True
    mp_roles = False
    mp_browsers = False

    max_parallel_lanes = 10

    ca = ConfigAssists()
    ca.create_first_time_setup()

    rc = ca.get_run_configuration()
    rc.prefix = "RTVS"
    rc.category = "REG"
    rc.env = os.getenv("TEST_ENV", "PROD")
    rc.test_package = marker
    rc.test_package_desc = "Home Page Combo Pack 1"
    rc.started_at = datetime.now().strftime("%Y%m%d_%H%M%S")

    # store summary as TEXT
    rc.clients = ",".join(clients)
    rc.user_roles = ",".join(roles)
    rc.browsers = ",".join(browsers)
    rc.multiprocessing = True
    rc.threads = max_parallel_lanes

    ca.set_unique_id()
    ca.create_run_id()
    ca.db.insert_test_run(rc)

    lanes = build_lanes(
        clients=clients,
        roles=roles,
        browsers=browsers,
        mp_clients=mp_clients,
        mp_roles=mp_roles,
        mp_browsers=mp_browsers,
    )

    print_plan(lanes)

    results = run_lanes_parallel(
        lanes=lanes,
        run_id=rc.run_id,
        marker=marker,
        max_parallel_lanes=max_parallel_lanes,
    )

    print("\n[RTVS] Results:")
    for lane_id, job, code in results:
        print(f"  lane={lane_id} client={job.client_id} role={job.user_role} browser={job.browser} exit={code}")

    exit_code = 0 if all(code == 0 for _, _, code in results) else 1
    ca.db.close()
    sys.exit(exit_code)



if __name__ == "__main__":
    main_multi_process()
