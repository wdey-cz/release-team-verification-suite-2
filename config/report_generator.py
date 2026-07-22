import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font
import re


class ReportGenerator:

    def __init__(self, db, log_fn, template_dir):
        self.db = db
        self.log = log_fn
        self.template_dir = Path(template_dir)
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def _split_csv(self, s):
        return [x.strip() for x in (s or "").split(",") if x.strip()]

    def _fetch_run_metadata(self, run_id):
        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT browsers, clients, user_roles
            FROM test_runs
            WHERE run_id = ?;
        """, (run_id,))

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"No data found for run_id={run_id}")

        return (
            self._split_csv(row[0]),
            self._split_csv(row[1]),
            self._split_csv(row[2])
        )

    def _fetch_run_summary(self, run_id):
        """
        Pulls run-level metadata needed for the Overview page header:
          - test_package / test_package_desc
          - started_at / ended_at  (+ computed time_taken)
          - customer name(s), joined from customers table via clients CSV

        started_at and ended_at are read directly from test_runs. If ended_at
        is missing, or the started_at/ended_at pair produces a negative delta
        (indicating ended_at wasn't written correctly, e.g. the run crashed
        before completion), last_heartbeat_at is used as a fallback end-time
        source — it reflects the last moment the test run was confirmed alive.

        Returns a dict consumed directly by the template.
        """
        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT run_id, test_package, test_package_desc,
                   clients, started_at, ended_at, last_heartbeat_at
            FROM test_runs
            WHERE run_id = ?;
        """, (run_id,))

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"No run summary found for run_id={run_id}")

        (
            db_run_id, test_package, test_package_desc,
            clients_csv, started_at, ended_at, last_heartbeat_at
        ) = row

        client_ids = self._split_csv(clients_csv)

        # --------------------------------------------------------
        # Join customers table to resolve names for each client id
        # --------------------------------------------------------
        customers = []

        if client_ids:
            placeholders = ",".join(["?"] * len(client_ids))
            cursor.execute(f"""
                SELECT customer_id, customer_name
                FROM customers
                WHERE customer_id IN ({placeholders})
            """, client_ids)

            name_by_id = {
                str(cid): cname
                for cid, cname in cursor.fetchall()
            }

            for cid in client_ids:
                customers.append({
                    "id": cid,
                    "name": name_by_id.get(str(cid), f"Unknown ({cid})")
                })

        # --------------------------------------------------------
        # Time taken calculation — tries ended_at first, falls back
        # to last_heartbeat_at if ended_at is missing or produces an
        # inconsistent (negative) delta against started_at.
        # --------------------------------------------------------
        time_taken, effective_end = self._compute_time_taken(
            started_at, ended_at, last_heartbeat_at
        )

        return {
            "run_id": db_run_id,
            "test_package": test_package or "N/A",
            "test_package_desc": test_package_desc or "",
            "customers": customers,
            "started_at": started_at or "N/A",
            "ended_at": effective_end or "N/A",
            "time_taken": time_taken
        }

    def _parse_timestamp(self, value):
        """
        Parses a timestamp string against known formats used across
        test_runs (started_at/ended_at/last_heartbeat_at). Returns a
        datetime, or None if value is missing/unparseable.
        """
        from datetime import datetime

        if not value:
            return None

        fmts = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y%m%d_%H%M%S",          # compact format, e.g. "20260619_090327"
        ]

        for fmt in fmts:
            try:
                return datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                continue

        return None

    def _compute_time_taken(self, started_at, ended_at, last_heartbeat_at):
        """
        Computes HH:MM:SS for the Date & Time card, trying ended_at first
        and falling back to last_heartbeat_at when ended_at is missing or
        produces an inconsistent (negative) delta against started_at —
        which happens when a run crashed or was killed before ended_at
        was ever written, but heartbeats were still being recorded.

        Returns (time_taken_str, effective_end_value) where effective_end_value
        is whichever raw string (ended_at or last_heartbeat_at) was actually
        used, so the caller can display the timestamp that matches the
        duration shown.

        Both candidates are tried in order; if neither produces a valid,
        non-negative delta against started_at, returns ("N/A", ended_at)
        — preferring to display whatever ended_at raw value exists (even
        if unusable for the calculation) rather than silently swapping it
        for last_heartbeat_at when neither could be used to compute anything.
        """
        start_dt = self._parse_timestamp(started_at)

        if start_dt is None:
            return "N/A", ended_at

        # Try ended_at first
        end_dt = self._parse_timestamp(ended_at)
        if end_dt is not None:
            delta_seconds = int((end_dt - start_dt).total_seconds())
            if delta_seconds >= 0:
                return self._seconds_to_hms(delta_seconds), ended_at
            else:
                self.log(
                    f"[WARN] started_at ({started_at}) is after ended_at ({ended_at}) "
                    f"— falling back to last_heartbeat_at."
                )

        # Fall back to last_heartbeat_at
        heartbeat_dt = self._parse_timestamp(last_heartbeat_at)
        if heartbeat_dt is not None:
            delta_seconds = int((heartbeat_dt - start_dt).total_seconds())
            if delta_seconds >= 0:
                return self._seconds_to_hms(delta_seconds), last_heartbeat_at
            else:
                self.log(
                    f"[WARN] started_at ({started_at}) is also after "
                    f"last_heartbeat_at ({last_heartbeat_at}) — showing N/A."
                )

        return "N/A", ended_at

    def _seconds_to_hms(self, total_seconds):
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def _fetch_logs(self, run_id, client, role, browser, only_types=None):
        cursor = self.db.connection.cursor()

        query = """
            SELECT timestamp, type, test_case_id, test_name,
                   message, status, time_taken_ms, comment, current_url
            FROM test_logs
            WHERE run_id = ?
              AND client_id = ?
              AND user_role = ?
              AND browser = ?
        """

        params = [run_id, client, role, browser]

        if only_types:
            query += " AND type IN ({})".format(",".join(["?"] * len(only_types)))
            params.extend(only_types)

        query += " ORDER BY id ASC"

        cursor.execute(query, params)
        return cursor.fetchall()

    from collections import defaultdict

    def _transform_logs(self, logs):
        """
        Main orchestrator function - transforms logs into structured format.

        Delegates specific log processing to individual handler functions.
        Returns dict of test cases grouped by test name.
        """
        result = defaultdict(list)
        current_block = None
        pending_logs = []
        has_error_in_block = False
        orphan_logs = []

        for row in logs:
            ts, typ, tci, test_name, msg, status, timetaken, comment, url = row
            test_name = test_name or "NO_TEST_NAME"

            # Delegate to appropriate handler based on log type
            if typ == "start":
                orphan_logs, current_block, pending_logs, has_error_in_block = self._process_start_log(
                    row, current_block, orphan_logs, pending_logs
                )

            elif typ == "end":
                result, current_block, pending_logs, has_error_in_block = self._process_end_log(
                    row, current_block, pending_logs, has_error_in_block, result
                )

            elif typ == "test_case":
                orphan_logs, current_block = self._process_test_case_log(
                    row, current_block, orphan_logs
                )

            elif typ == "error":
                orphan_logs, pending_logs, current_block, has_error_in_block = self._process_error_log(
                    row, current_block, pending_logs, orphan_logs, has_error_in_block
                )

            else:  # heartbeat, update, force_skip, etc.
                orphan_logs, pending_logs, current_block = self._process_other_log(
                    row, current_block, pending_logs, orphan_logs
                )

        # Handle unclosed block at end of logs
        if current_block is not None:
            result = self._close_current_block(
                current_block, pending_logs, has_error_in_block, result
            )

        # Create orphan/system block if orphan logs exist
        if orphan_logs:
            result = self._create_orphan_block(orphan_logs, result)

        return result

    # ============================================================================
    # LOG ENTRY CREATION
    # ============================================================================

    def _create_log_entry(self, row):
        """
        Create a standardized log entry dictionary from a row tuple.

        Args:
            row: Tuple of (ts, typ, tci, test_name, msg, status, timetaken, comment, url)

        Returns:
            dict: Formatted log entry
        """
        ts, typ, tci, test_name, msg, status, timetaken, comment, url = row

        return {
            "timestamp": ts,
            "type": typ,
            "message": msg,
            "status": status,
            "time": timetaken,
            "comment": comment,
            "url": url,
            "test_case_id": tci if typ == "test_case" else None
        }

    def _create_test_block(self, row):
        """
        Create a new test block from a START log entry.

        Args:
            row: Tuple of (ts, typ, tci, test_name, msg, status, timetaken, comment, url)

        Returns:
            dict: New test block structure
        """
        ts, typ, tci, test_name, msg, status, timetaken, comment, url = row

        return {
            "test_case_id": "N/A",
            "test_name": test_name,
            "test_case_name": msg,
            "status": "IN_PROGRESS",
            "time": timetaken,
            "comment": None,
            "url": url,
            "logs": []
        }

    # ============================================================================
    # LOG TYPE HANDLERS
    # ============================================================================

    def _process_start_log(self, row, current_block, orphan_logs, pending_logs):
        """
        Handle START log type.

        Opens a new test block. If a block is already open without an end,
        collect it as orphan instead of silently replacing.
        """
        ts, typ, tci, test_name, msg, status, timetaken, comment, url = row

        if current_block is not None:
            # Block already open without end -> collect as orphan
            orphan_logs.append(self._create_log_entry(row))
        else:
            # No block open -> create new one
            current_block = self._create_test_block(row)
            pending_logs = []

        return orphan_logs, current_block, pending_logs, False

    def _process_end_log(self, row, current_block, pending_logs, has_error_in_block, result):
        """
        Handle END log type.

        Seals and commits the current block. If errors were found in the block,
        overrides status to FAILED.
        """
        ts, typ, tci, test_name, msg, status, timetaken, comment, url = row

        if current_block is not None:
            # Update status from end log
            if current_block["status"] == "IN_PROGRESS":
                current_block["status"] = status

            # Override status if errors found
            if has_error_in_block:
                current_block["status"] = "FAILED"
                print(f"[LOG TRANSFORM] Test case '{current_block['test_case_name']}' "
                      f"marked as FAILED due to error logs")

            # Commit block
            current_block["logs"] = pending_logs
            result[current_block["test_name"]].append(current_block)
            current_block = None
            pending_logs = []
            has_error_in_block = False

        return result, current_block, pending_logs, has_error_in_block

    def _process_test_case_log(self, row, current_block, orphan_logs):
        """
        Handle TEST_CASE log type.

        Enriches the open test block with detailed test case metadata.
        If no block is open, collects as orphan.
        """
        ts, typ, tci, test_name, msg, status, timetaken, comment, url = row

        if current_block is None:
            # No open block -> collect as orphan
            orphan_logs.append(self._create_log_entry(row))
        else:
            # Block is open -> enrich it with test case data
            current_block["test_case_id"] = tci
            current_block["test_case_name"] = msg
            current_block["status"] = status
            current_block["time"] = timetaken
            current_block["comment"] = comment
            current_block["url"] = url or current_block["url"]

        return orphan_logs, current_block

    def _process_error_log(self, row, current_block, pending_logs, orphan_logs, has_error_in_block):
        """
        Handle ERROR log type.

        Marks the current block as containing errors. If no block is open,
        collects as orphan.
        """
        ts, typ, tci, test_name, msg, status, timetaken, comment, url = row

        log_entry = self._create_log_entry(row)

        if current_block is not None:
            # Mark block as having errors
            has_error_in_block = True
            print(f"[LOG TRANSFORM] Error detected in test case: {current_block['test_case_name']}")
            pending_logs.append(log_entry)
        else:
            # Error outside block -> collect as orphan
            print(f"[LOG TRANSFORM] Orphan error log detected: {msg}")
            orphan_logs.append(log_entry)

        return orphan_logs, pending_logs, current_block, has_error_in_block

    def _process_other_log(self, row, current_block, pending_logs, orphan_logs):
        """
        Handle other log types: heartbeat, update, force_skip, etc.

        If block is open, add to pending logs. Otherwise, collect as orphan.
        """
        log_entry = self._create_log_entry(row)

        if current_block is None:
            # No open block -> collect as orphan
            orphan_logs.append(log_entry)
        else:
            # Block is open -> add to logs
            pending_logs.append(log_entry)

        return orphan_logs, pending_logs, current_block

    # ============================================================================
    # BLOCK MANAGEMENT
    # ============================================================================

    def _close_current_block(self, current_block, pending_logs, has_error_in_block, result):
        """
        Close an unclosed test block at end of logs.

        Sets status to INCOMPLETE or FAILED if errors were found.
        """
        current_block["logs"] = pending_logs

        # Mark as incomplete if no explicit end
        if current_block["status"] == "IN_PROGRESS":
            current_block["status"] = "INCOMPLETE"

        # Override status if errors found
        if has_error_in_block:
            current_block["status"] = "FAILED"
            print(f"[LOG TRANSFORM] Unclosed test case '{current_block['test_case_name']}' "
                  f"marked as FAILED due to error logs")

        # Commit block
        result[current_block["test_name"]].append(current_block)

        return result

    # ============================================================================
    # ORPHAN BLOCK CREATION
    # ============================================================================

    def _create_orphan_block(self, orphan_logs, result):
        """
        Create a System/Useful Execution Notes block from orphan logs.

        Orphan logs are those that occur outside any test block.
        If orphan logs contain errors, the block is marked as FAILED.
        """
        # Check if any orphan log is an error
        orphan_has_error = any(log.get("type") == "error" for log in orphan_logs)

        if orphan_has_error:
            print(f"[LOG TRANSFORM] System block marked as FAILED due to orphan error logs")

        # Create orphan block
        orphan_block = {
            "test_case_id": "INFO",
            "test_name": "System",
            "test_case_name": "Useful Execution Notes",
            "status": "FAILED" if orphan_has_error else "Success",
            "time": None,
            "comment": f"{len(orphan_logs)} event(s) captured outside test blocks",
            "url": None,
            "logs": orphan_logs
        }

        # Add to result
        if "System" not in result:
            result["System"] = []
        result["System"].append(orphan_block)

        return result
    def _compute_pass_fail_counts(self, data):
        """
        Walks the transformed data structure and counts PASS / FAIL
        across every test case block in every suite/env.

        A block counts as PASS only if its status explicitly contains 'PASS'.
        Everything else (FAILED, ERROR, INCOMPLETE, ORPHAN) counts as FAIL,
        matching the same rule already used in the template's badge logic.
        """
        passed = 0
        failed = 0

        for env, suites in data.items():
            for suite_name, tests in suites.items():
                for test in tests:
                    status = (test.get("status") or "").upper()
                    if "PASS" in status:
                        passed += 1
                    else:
                        failed += 1

        total = passed + failed
        return total, passed, failed

    # -------------------------
    # HTML REPORT
    # -------------------------
    def generate_html(self, run_id, output_dir, icon_path):
        browsers, clients, roles = self._fetch_run_metadata(run_id)

        data = {}
        for client in clients:
            for role in roles:
                for browser in browsers:
                    logs = self._fetch_logs(run_id, client, role, browser)
                    key = f"{client}_{role}_{browser}"
                    data[key] = self._transform_logs(logs)

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # --------------------------------------------------------
        # Copy the modular css/ js/ assets/ folders next to the HTML
        # so the template's relative links resolve when opened.
        # --------------------------------------------------------
        for folder in ("css", "js", "assets"):
            src = self.template_dir / folder
            if src.is_dir():
                shutil.copytree(src, output_dir / folder, dirs_exist_ok=True)

        # --------------------------------------------------------
        # Place the run's logo inside assets/icons/ (where the
        # template looks: assets/icons/{{ icon_path }})
        # --------------------------------------------------------
        icon_path = Path(icon_path)
        icons_dir = output_dir / "assets" / "icons"
        icons_dir.mkdir(parents=True, exist_ok=True)
        dest_icon = icons_dir / icon_path.name
        if not dest_icon.exists():
            shutil.copy(icon_path, dest_icon)

        run_summary = self._fetch_run_summary(run_id)
        total, passed, failed = self._compute_pass_fail_counts(data)

        template = self.env.get_template("report_template_combinedco.html")
        html = template.render(
            data=data,
            run_id=run_id,
            icon_path=icon_path.name,
            run_summary=run_summary,
            total=total,
            passed=passed,
            failed=failed
        )

        output_path = output_dir / f"Report_{run_id}.html"
        output_path.write_text(html, encoding="utf-8")

        self.log(f"[OK] HTML report generated at {output_path}")
        return output_path
    # -------------------------
    # XLSX REPORT
    # -------------------------
    def _sanitize_sheet_name(self, name):
        name = (name or "").strip() or "NO_TEST_NAME"
        name = re.sub(r"[:\\/?*\[\]]", "_", name)
        return name[:31]

    def _unique_sheet_title(self, wb, base):
        base = self._sanitize_sheet_name(base)
        if base not in wb.sheetnames:
            return base

        i = 2
        while True:
            suffix = f"_{i}"
            trimmed = base[:31 - len(suffix)]
            candidate = f"{trimmed}{suffix}"
            if candidate not in wb.sheetnames:
                return candidate
            i += 1

    def generate_xlsx(self, run_id, output_dir):
        browsers, clients, roles = self._fetch_run_metadata(run_id)

        header = ["Timestamp", "Type", "Test Case ID", "Test Name",
                  "Message", "Status", "Time Taken", "Comments", "Current URL"]

        header_font = Font(bold=True)

        for client in clients:
            for role in roles:
                for browser in browsers:

                    logs = self._fetch_logs(
                        run_id, client, role, browser,
                        only_types=["test_case", "heartbeat"]
                    )

                    xlsx_file = output_dir / f"report_{client}_{role}_{browser}.xlsx"

                    wb = Workbook()
                    wb.remove(wb.active)

                    sheets = {}

                    if not logs:
                        ws = wb.create_sheet("NO_DATA")
                        for c, h in enumerate(header, 1):
                            cell = ws.cell(row=1, column=c, value=h)
                            cell.font = header_font
                    else:
                        for row in logs:
                            ts, typ, tci, test_name, msg, status, timetaken, comment, url = row

                            tab_key = "HEARTBEAT" if typ == "heartbeat" else (test_name or "NO_TEST_NAME")

                            if tab_key not in sheets:
                                title = self._unique_sheet_title(wb, tab_key)
                                ws = wb.create_sheet(title)
                                sheets[tab_key] = ws

                                for c, h in enumerate(header, 1):
                                    cell = ws.cell(row=1, column=c, value=h)
                                    cell.font = header_font

                            sheets[tab_key].append(
                                [ts, typ, tci, test_name, msg, status, timetaken, comment, url]
                            )

                    wb.save(xlsx_file)

        self.log(f"[OK] XLSX reports generated at {output_dir}")
        return output_dir