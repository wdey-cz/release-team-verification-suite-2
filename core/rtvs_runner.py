import os
import sys
import time
import subprocess
from dataclasses import dataclass
from itertools import product
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Any, Optional
from pathlib import Path


from core.config import Config


# TEST_PATH = "tests/test_home_page.py"


@dataclass(frozen=True)
class Job:
    client_id: str
    user_role: str
    browser: str
    user_name: str


def build_lanes(
    clients: List[str],
    roles: List[str],
    browsers: List[str],
    mp_clients: bool,
    mp_roles: bool,
    mp_browsers: bool,
) -> List[List[Job]]:
    """
    Returns lanes. Each lane is a list of Jobs that must run serially.
    Lanes can run in parallel.
    """

    dims: Dict[str, List[str]] = {
        "client_id": clients,
        "user_role": roles,
        "browser": browsers,
    }
    mp_flags: Dict[str, bool] = {
        "client_id": mp_clients,
        "user_role": mp_roles,
        "browser": mp_browsers,
    }

    parallel_keys = [k for k, v in mp_flags.items() if v]
    serial_keys = [k for k, v in mp_flags.items() if not v]

    if "browser" in serial_keys:
        serial_keys.remove("browser")
        serial_keys.insert(0, "browser")

    # If nothing is marked parallel, we still create 1 lane.
    parallel_space = [dims[k] for k in parallel_keys] if parallel_keys else [["_single_lane_"]]
    serial_space = [dims[k] for k in serial_keys] if serial_keys else [[]]

    lanes: List[List[Job]] = []

    for parallel_values in product(*parallel_space):
        lane_jobs: List[Job] = []

        for serial_values in product(*serial_space) if serial_keys else [()]:
            # Build a full assignment dict for this job
            assignment: Dict[str, str] = {}

            if parallel_keys:
                for k, v in zip(parallel_keys, parallel_values):
                    assignment[k] = v

            if serial_keys:
                for k, v in zip(serial_keys, serial_values):
                    assignment[k] = v

            # Fill any missing keys (happens when nothing is parallel)
            if "client_id" not in assignment:
                assignment["client_id"] = clients[0]
            if "user_role" not in assignment:
                assignment["user_role"] = roles[0]
            if "browser" not in assignment:
                assignment["browser"] = browsers[0]

            user_name = f"local_{assignment['user_role']}".replace(" ", "_").lower()

            lane_jobs.append(
                Job(
                    client_id=assignment["client_id"],
                    browser=assignment["browser"],
                    user_role=assignment["user_role"],
                    user_name=user_name,
                )
            )

        lanes.append(lane_jobs)

    return lanes



def run_lane_serial(
    *,
    lane_id: int,
    jobs: List[Job],
    run_id: str,
    marker: str,
    base_env: Dict[str, str],   # ADD THIS
) -> List[Tuple[Job, int]]:
    results: List[Tuple[Job, int]] = []

    # stagger parallel lanes so 10 Chromes don't slam the machine at once
    time.sleep(0.75 * (lane_id - 1))

    for j in jobs:
        env = base_env.copy()    # USE base_env, not os.environ.copy()
        env["BROWSER"] = j.browser

        cmd = [
            sys.executable, "-m", "pytest",
            "-m", marker,
            "-s",
            "-v",
            "--rtvs-run-id", run_id,
            "--client-id", j.client_id,
            "--user-role", j.user_role,
            "--user-name", j.user_name,
            str(Path(Config.RTVS_PROJECT_ROOT / 'tests')),
        ]

        print(f"\n[RTVS] Lane {lane_id} running job:")
        print(f"  client={j.client_id} role={j.user_role} browser={j.browser}")
        print(" ", " ".join(cmd))

        p = subprocess.run(cmd, env=env)
        results.append((j, p.returncode))

    return results


def run_lanes_parallel(
    *,
    lanes: List[List[Job]],
    run_id: str,
    marker: str,
    max_parallel_lanes: int = 10,
    base_env: Dict[str, str],   # ADD THIS
) -> List[Tuple[int, Job, int]]:
    all_results: List[Tuple[int, Job, int]] = []

    with ThreadPoolExecutor(max_workers=max_parallel_lanes) as ex:
        futures = {}
        for idx, lane_jobs in enumerate(lanes, start=1):
            futures[
                ex.submit(
                    run_lane_serial,
                    lane_id=idx,
                    jobs=lane_jobs,
                    run_id=run_id,
                    marker=marker,
                    base_env=base_env,   # PASS IT
                )
            ] = idx

        for fut in as_completed(futures):
            lane_id = futures[fut]
            lane_res = fut.result()
            for job, code in lane_res:
                all_results.append((lane_id, job, code))

    return all_results


def print_plan(lanes: List[List[Job]]):
    print("\n[RTVS] Execution plan:")
    for i, lane in enumerate(lanes, start=1):
        print(f"  Parallel lane {i}:")
        for j in lane:
            print(f"    client={j.client_id} role={j.user_role} browser={j.browser}")
