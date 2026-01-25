#!/usr/bin/env python3
"""
Environment Variables + Threads + Processes: a hands-on tutorial script.

Run it like:
  python env_tutorial.py

What you'll learn by watching the output:
- os.environ is process-wide (shared by threads)
- child processes inherit a COPY of the parent's environment at spawn time
- mutating os.environ in one thread affects all threads
- safe pattern: build an env dict and pass it to subprocesses (no global mutation)
"""

from __future__ import annotations

import os
import sys
import time
import threading
import subprocess
from typing import Dict


KEY = "RTVS_DEMO_ENV"


def hr(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def show_env(label: str) -> None:
    pid = os.getpid()
    tid = threading.get_ident()
    val = os.environ.get(KEY, "<not set>")
    print(f"[{label}] PID={pid} | TID={tid} | os.environ[{KEY}] = {val!r}")


def run_child(label: str, extra_env: Dict[str, str] | None = None) -> None:
    """
    Spawn a child python process and make it print its view of the environment.
    We pass a tiny inline python program via -c for simplicity.
    """
    child_code = r"""
import os, threading, time
KEY = "RTVS_DEMO_ENV"
print(f"[child] PID={os.getpid()} | TID={threading.get_ident()} | {KEY}={os.environ.get(KEY, '<not set>')!r}")
print("Wolololo from child process!")
time.sleep(0.5)  # keep it alive a bit for demo
print("Wolololo after sleep!")
time.sleep(0.5)
print("wolololo after more sleep!")
time.sleep(0.5)
print("child exiting.")
"""
    env = None
    if extra_env is not None:
        # IMPORTANT: subprocess env must be a complete environment mapping.
        # So we start from a copy of current process environment and then add our overrides.
        env = os.environ.copy()
        env.update(extra_env)

    print(f"  -> launching child process ({label})")
    subprocess.run([sys.executable, "-c", child_code], env=env, check=False)


def section_0_baseline() -> None:
    hr("0) Baseline: environment variables live on the PROCESS, not on the thread")
    show_env("parent baseline")
    print("Now we'll spawn a child. It inherits the parent's current env (a COPY at spawn time).")
    run_child("inherit baseline")


def section_1_parent_changes_affect_future_children() -> None:
    hr("1) If parent process changes os.environ, future children inherit the NEW value")

    print("Setting os.environ in the PARENT process...")
    os.environ[KEY] = "set_in_parent"
    show_env("parent after set")

    print("\nChild spawned AFTER the change will see the new value:")
    run_child("after parent set")

    print("\nNow deleting it in the parent process...")
    os.environ.pop(KEY, None)
    show_env("parent after delete")

    print("\nChild spawned AFTER delete will see it missing:")
    run_child("after parent delete")


def section_2_threads_share_os_environ() -> None:
    hr("2) Threads share os.environ (shared global state inside one process)")

    print("We'll start two threads. One thread will keep flipping the env var.")
    print("The other thread will repeatedly read it.")
    print("Because threads share the same process env, the reader sees the flips.\n")

    stop = threading.Event()

    def flipper() -> None:
        i = 0
        while not stop.is_set() and i < 10:
            os.environ[KEY] = f"flip_{i}"
            show_env("flipper set")
            time.sleep(0.15)
            i += 1

    def reader() -> None:
        for _ in range(15):
            show_env("reader sees")
            time.sleep(0.10)

    t1 = threading.Thread(target=flipper, name="flipper-thread")
    t2 = threading.Thread(target=reader, name="reader-thread")
    t1.start()
    t2.start()
    t1.join()
    stop.set()
    t2.join()

    print("\nTakeaway:")
    print("- os.environ is a process-wide dict.")
    print("- All threads in a process see the same os.environ.")
    print("- If you mutate it from one thread, you affect all threads.")


def section_3_safe_pattern_subprocess_env_dict() -> None:
    hr("3) SAFE pattern: don't mutate os.environ; pass env dict to each subprocess")

    print("In a multi-threaded orchestrator (like your Qt app), this is the golden rule:")
    print("  ✅ build a per-child env dict and pass it to subprocess.run(..., env=env_dict)")
    print("  ❌ avoid os.environ[...] = ... (shared mutation)\n")

    # Ensure parent has a known value (or none). We'll demonstrate both children getting different values
    os.environ.pop(KEY, None)
    show_env("parent before safe demo")

    print("\nSpawning two children with different values WITHOUT changing parent os.environ:\n")

    run_child("child A gets value 'A_ONLY'", extra_env={KEY: "A_ONLY"})
    run_child("child B gets value 'B_ONLY'", extra_env={KEY: "B_ONLY"})

    print("\nNow check parent again. It never changed:")
    show_env("parent after safe demo")

    print("\nTakeaway:")
    print("- Passing env=... isolates environment config per child process.")
    print("- No shared global mutation, so it is thread-safe.")


def section_4_the_exact_bug_pattern_you_hit() -> None:
    hr("4) The BUG pattern: one thread clears os.environ while another thread is still running")

    print("This simulates what happened in your code:")
    print("- Thread A: sets env, launches work, then restores env in finally.")
    print("- Thread B: sets env, launches work, still running.")
    print("- If A calls os.environ.clear() in finally, it nukes the env for B too.\n")

    # Start with a stable env state
    os.environ[KEY] = "stable_start"
    show_env("parent start")

    barrier = threading.Barrier(2)
    done = threading.Event()

    def thread_a() -> None:
        old_env = os.environ.copy()
        try:
            print("\n[thread A] Setting env to 'A_RUN' (global mutation).")
            os.environ[KEY] = "A_RUN"
            show_env("thread A after set")

            print("[thread A] Launching child that inherits A_RUN (works).")
            run_child("from thread A (inherit)")

            barrier.wait()  # sync point

        finally:
            print("\n[thread A] FINALLY: clearing and restoring environment (DANGEROUS in multi-thread).")
            os.environ.clear()
            os.environ.update(old_env)
            show_env("thread A after restore")
            done.set()

    def thread_b() -> None:
        old_env = os.environ.copy()
        try:
            print("\n[thread B] Setting env to 'B_RUN' (global mutation).")
            os.environ[KEY] = "B_RUN"
            show_env("thread B after set")

            barrier.wait()  # sync with thread A

            print("\n[thread B] Now trying to launch child. If thread A cleared env, B may be impacted.")
            run_child("from thread B (inherit)")

        finally:
            # We'll NOT clear here, just restore the key for cleanliness.
            os.environ.clear()
            os.environ.update(old_env)
            show_env("thread B after restore")

    tA = threading.Thread(target=thread_a, name="A")
    tB = threading.Thread(target=thread_b, name="B")
    tA.start()
    tB.start()
    tA.join()
    tB.join()

    print("\nTakeaway:")
    print("- Clearing/restoring os.environ in a thread is a foot-gun.")
    print("- It affects all threads because it's process-global.")
    print("- Fix: never do global mutation. Use per-subprocess env dict.")


def section_5_practical_guidelines() -> None:
    hr("5) Practical guidelines you can apply immediately")

    print("Rules of thumb:")
    print("1) Threads share process state (globals, os.environ, cwd). Treat those as unsafe to mutate.")
    print("2) Child processes inherit a COPY of env at spawn time.")
    print("3) Always pass env overrides via subprocess.run(env=...) instead of os.environ mutations.")
    print("4) If you must store run config, store it in your own objects, not environment variables.")
    print("5) In orchestration code, threads should orchestrate; subprocesses should do the work.\n")

    print("Your runner already does the safe thing here:")
    print("  env = os.environ.copy(); env['BROWSER']=...; subprocess.run(..., env=env)")
    print("So keep TEST_ENV, HEADLESS, etc in that env dict too.\n")

    print("Extra: if you later add pytest-xdist:")
    print("- Each xdist worker is a separate process (gw0, gw1, ...).")
    print("- They won't share Python memory, but they can still clash on Chrome profiles or SQLite writes.")
    print("- Keep per-worker identifiers (worker name, pid) in logs, like you're already doing.")


def main() -> None:
    print("ENV TUTORIAL SCRIPT")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Parent PID: {os.getpid()}")
    print(f"Platform: {sys.platform}")
    print("\nThis script will spawn child python processes. Watch the prints carefully.\n")

    section_0_baseline()
    section_1_parent_changes_affect_future_children()
    section_2_threads_share_os_environ()
    section_3_safe_pattern_subprocess_env_dict()
    section_4_the_exact_bug_pattern_you_hit()
    section_5_practical_guidelines()

    hr("Done")
    print("If you want, I can tailor this script to mirror your exact variables (TEST_ENV, HEADLESS, BROWSER)")
    print("and even simulate two concurrent RTVS runs launching pytest, without touching your codebase.")


if __name__ == "__main__":
    main()
