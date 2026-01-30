from __future__ import annotations

import os
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSplashScreen
from PySide6 import QtCore, QtGui, QtWidgets

from config.rtvsdb import RTVSDB  # type: ignore
from config.config_assists import ConfigAssists  # type: ignore
from core.rtvs_runner import build_lanes, print_plan, run_lanes_parallel
from core.config import Config



@dataclass
class ChromeProfileRow:
    id: int
    profile_name: str
    currently_running: str | None
    is_active: int
    last_mfa_time: str

@dataclass
class TestRunRow:
    run_id: str
    category: str
    env: str
    test_package: str
    browsers: str
    clients: str
    user_roles: str
    threads: int
    multiprocessing: int
    started_at: str
    ended_at: str | None
    status: str
    failed_cases: int
    last_update_at: str | None
    last_update_message: str | None


@dataclass
class TestLogRow:
    timestamp: str
    type: str
    status: str
    test_name: str | None
    message: str | None
    worker: str | None
    pid: int | None
    current_url: str | None


class TestRunWorker(QtCore.QThread):
    run_finished = QtCore.Signal(str, str)  # run_id, final_status
    run_failed = QtCore.Signal(str, str)  # run_id, error

    def __init__(
        self,
        *,
        db_path: str,
        run_id: str,
        marker: str,
        clients: list[str],
        roles: list[str],
        browsers: list[str],
        mp_clients: bool,
        mp_roles: bool,
        mp_browsers: bool,
        max_parallel_lanes: int,
        test_env: str,
        headless: bool,
    ):
        super().__init__()
        self.db_path = db_path
        self.run_id = run_id
        self.marker = marker
        self.clients = clients
        self.roles = roles
        self.browsers = browsers
        self.mp_clients = mp_clients
        self.mp_roles = mp_roles
        self.mp_browsers = mp_browsers
        self.max_parallel_lanes = max_parallel_lanes
        self.test_env = test_env
        self.headless = headless

    def run(self):
        final_status = "ERR"
        try:
            # Build per-run environment for subprocesses
            base_env = os.environ.copy()
            base_env["TEST_ENV"] = self.test_env
            base_env["HEADLESS"] = "true" if self.headless else "false"

            lanes = build_lanes(
                clients=self.clients,
                roles=self.roles,
                browsers=self.browsers,
                mp_clients=self.mp_clients,
                mp_roles=self.mp_roles,
                mp_browsers=self.mp_browsers,
            )

            print_plan(lanes)

            results = run_lanes_parallel(
                lanes=lanes,
                run_id=self.run_id,
                marker=self.marker,
                max_parallel_lanes=self.max_parallel_lanes,
                base_env=base_env,   # PASS PER-RUN ENV
            )

            exit_ok = all(code == 0 for _, _, code in results)
            final_status = "PASS" if exit_ok else "FAIL"

            db = RTVSDB(self.db_path)
            db.finish_run(self.run_id, final_status)
            db.close()

            self.run_finished.emit(self.run_id, final_status)

        except Exception as e:
            print(e)
            try:
                db = RTVSDB(self.db_path)
                db.finish_run(self.run_id, "ERR")
                db.close()
            except Exception:
                pass
            self.run_failed.emit(self.run_id, str(e))


class StartTestDialog(QtWidgets.QDialog):
    """
    Secondary window to gather run config and lane options.
    """
    def __init__(self, parent: QtWidgets.QWidget, db: RTVSDB):
        super().__init__(parent)
        self.setWindowTitle("Start New Test")
        self.resize(1200, 800)

        self._db = db

        root = QtWidgets.QVBoxLayout(self)

        # --- Basic run config ---
        form = QtWidgets.QFormLayout()

        self.prefix_input = QtWidgets.QLineEdit("RTVS")

        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(["REG", "DATA", "CUSTOM"])

        self.env_combo = QtWidgets.QComboBox()
        self.env_combo.addItems(["PROD", "CERT", "STAGE", "TEST", "NOENV"])

        self.headless_chk = QtWidgets.QCheckBox("Headless")
        self.headless_chk.setChecked(False)

        self.marker_combo = QtWidgets.QComboBox()
        self.marker_combo.setEditable(False)

        # self.marker_combo.addItems(self.fetch_test_package_names())

        self.package_desc_input = QtWidgets.QLineEdit()
        self.package_desc_input.setReadOnly(True)
        self.package_desc_input.setPlaceholderText("Select A test Package to see its description")
        # self.package_desc_input.setPlaceholderText("Optional description shown in test_runs.test_package_desc")

        # Change signals
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        self.marker_combo.currentTextChanged.connect(self.on_marker_changed)

        # Initial population
        self.on_category_changed(self.category_combo.currentText())

        form.addRow("Prefix:", self.prefix_input)
        form.addRow("Category:", self.category_combo)
        form.addRow("Env (TEST_ENV):", self.env_combo)
        form.addRow("Marker (pytest -m):", self.marker_combo)
        form.addRow("Package description:", self.package_desc_input)
        form.addRow("", self.headless_chk)

        root.addLayout(form)

        # --- Selection panes ---
        panes = QtWidgets.QHBoxLayout()

        self.clients_list = self._make_check_list("Clients (from customers table)")
        self.roles_list = self._make_check_list("Roles (from customer_accounts table)")
        self.browsers_list = self._make_check_list("Browsers")

        panes.addWidget(self.clients_list["group"])
        panes.addWidget(self.roles_list["group"])
        panes.addWidget(self.browsers_list["group"])
        root.addLayout(panes)

        # Manual fallback inputs (comma separated) if tables empty or user prefers typing
        manual = QtWidgets.QFormLayout()
        self.manual_clients = QtWidgets.QLineEdit()
        self.manual_clients.setPlaceholderText("e.g. 1000,1500")
        self.manual_roles = QtWidgets.QLineEdit()
        self.manual_roles.setPlaceholderText("e.g. cs,regional_support")
        self.manual_browsers = QtWidgets.QLineEdit()
        self.manual_browsers.setPlaceholderText("e.g. chrome,firefox")
        manual.addRow("Manual clients:", self.manual_clients)
        manual.addRow("Manual roles:", self.manual_roles)
        manual.addRow("Manual browsers:", self.manual_browsers)
        root.addLayout(manual)

        # --- Parallelization options ---
        opts = QtWidgets.QGroupBox("Lane execution options")
        opts_layout = QtWidgets.QFormLayout(opts)

        self.mp_clients_chk = QtWidgets.QCheckBox("Parallelize by clients")
        self.mp_roles_chk = QtWidgets.QCheckBox("Parallelize by roles")
        self.mp_browsers_chk = QtWidgets.QCheckBox("Parallelize by browsers")

        self.max_parallel_spin = QtWidgets.QSpinBox()
        self.max_parallel_spin.setMinimum(1)
        self.max_parallel_spin.setMaximum(64)
        self.max_parallel_spin.setValue(5)

        opts_layout.addRow("", self.mp_clients_chk)
        opts_layout.addRow("", self.mp_roles_chk)
        opts_layout.addRow("", self.mp_browsers_chk)
        opts_layout.addRow("Max parallel lanes:", self.max_parallel_spin)

        root.addWidget(opts)

        # Buttons
        btns = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Start Test")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.start_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btns.addStretch(1)
        btns.addWidget(self.start_btn)
        btns.addWidget(self.cancel_btn)
        root.addLayout(btns)

        # Populate lists
        self._populate_clients()
        self._populate_roles()
        self._populate_browsers()

    def _make_check_list(self, title: str) -> dict:
        group = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QVBoxLayout(group)
        lw = QtWidgets.QListWidget()
        layout.addWidget(lw)
        return {"group": group, "list": lw}

    def _add_check_item(self, lw: QtWidgets.QListWidget, label: str, value: str):
        it = QtWidgets.QListWidgetItem(label)
        it.setData(QtCore.Qt.ItemDataRole.UserRole, value)
        it.setFlags(it.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
        it.setCheckState(QtCore.Qt.CheckState.Unchecked)
        lw.addItem(it)

    def _fetch_markers_for_category(self, category: str) -> list[str]:
        category = (category or "").strip().upper()

        if category == "REG":
            return self._db.fetch_regression_test_packages()

        if category == "DATA":
            return self._db.fetch_data_integrity_test_packages()

        # CUSTOM or anything else
        # If you later store CUSTOM packages in test_packages, you can query generically here.
        return []

    def on_category_changed(self, category: str) -> None:
        """
        Repopulate marker dropdown based on category.
        Keep a sentinel so description stays empty until a real marker is selected.
        """
        markers = self._fetch_markers_for_category(category)

        self.marker_combo.blockSignals(True)
        self.marker_combo.clear()
        self.marker_combo.addItem("-- Select a package --", userData=None)  # sentinel
        for m in markers:
            self.marker_combo.addItem(m, userData=m)
        self.marker_combo.setCurrentIndex(0)
        self.marker_combo.blockSignals(False)

        # Clear desc until user picks a real marker
        self.package_desc_input.setText("")

    def on_marker_changed(self, _index: int) -> None:
        """
        Always pull description from DB for the selected marker.
        """
        marker = self.marker_combo.currentData()  # None for sentinel
        if not marker:
            self.package_desc_input.setText("")
            return

        desc = self._db.fetch_test_package_description(str(marker)) or ""
        self.package_desc_input.setText(desc)


    def _populate_clients(self):
        lw = self.clients_list["list"]
        lw.clear()
        try:
            rows = self._db.run_query("SELECT customer_id, customer_name FROM customers ORDER BY customer_id ASC;")
            for cid, name in rows:
                self._add_check_item(lw, f"{cid} - {name}", str(cid))
        except Exception:
            pass

    def _populate_roles(self):
        lw = self.roles_list["list"]
        lw.clear()
        try:
            rows = self._db.run_query("SELECT DISTINCT role FROM customer_accounts ORDER BY role ASC;")
            for (role,) in rows:
                self._add_check_item(lw, str(role), str(role))
        except Exception:
            pass

    def _populate_browsers(self):
        lw = self.browsers_list["list"]
        lw.clear()
        for b in ["chrome", "firefox", "edge"]:
            self._add_check_item(lw, b, b)

    def _checked_values(self, lw: QtWidgets.QListWidget) -> list[str]:
        out: list[str] = []
        for i in range(lw.count()):
            it = lw.item(i)
            if it.checkState() == QtCore.Qt.CheckState.Checked:
                out.append(str(it.data(QtCore.Qt.ItemDataRole.UserRole)))
        return out

    def _csv(self, text: str) -> list[str]:
        return [x.strip() for x in text.split(",") if x.strip()]

    def get_config(self) -> dict:
        marker = self.marker_combo.currentData()
        if not marker:
            raise ValueError("Select a test package (marker).")
        marker = str(marker).strip()

        clients = self._checked_values(self.clients_list["list"]) or self._csv(self.manual_clients.text())
        roles = self._checked_values(self.roles_list["list"]) or self._csv(self.manual_roles.text())
        browsers = self._checked_values(self.browsers_list["list"]) or self._csv(self.manual_browsers.text())

        if not clients:
            raise ValueError("Select at least 1 client (or fill manual clients).")
        if not roles:
            raise ValueError("Select at least 1 role (or fill manual roles).")
        if not browsers:
            raise ValueError("Select at least 1 browser (or fill manual browsers).")

        return {
            "prefix": self.prefix_input.text().strip() or "RTVS",
            "category": self.category_combo.currentText().strip() or "REG",
            "env": self.env_combo.currentText().strip() or "PROD",
            "headless": self.headless_chk.isChecked(),
            "marker": marker,
            "test_package_desc": self.package_desc_input.text().strip() or None,
            "clients": clients,
            "roles": roles,
            "browsers": browsers,
            "mp_clients": self.mp_clients_chk.isChecked(),
            "mp_roles": self.mp_roles_chk.isChecked(),
            "mp_browsers": self.mp_browsers_chk.isChecked(),
            "max_parallel_lanes": int(self.max_parallel_spin.value()),
        }


class ControllerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._workers: dict[str, TestRunWorker] = {}
        self.setWindowTitle("RTVS Controller")
        self.resize(1100, 720)

        self.assists: ConfigAssists | None = None

        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(120)
        self._init_log_watermark()


        self._build_setup_tab()

        self._safe_call("Init ConfigAssists", self._init_assists)

        self._build_chrome_tab()
        self._build_customers_tab()
        self._build_tests_tab()

        # Auto refresh every 60s
        # self.tests_refresh_timer = QtCore.QTimer(self)
        # self.tests_refresh_timer.setInterval(30_000)
        # self.tests_refresh_timer.timeout.connect(
        #     lambda: self._safe_call("Auto refresh tests", self._refresh_tests_views))
        # self.tests_refresh_timer.start()

        self.statusBar().showMessage("Ready")






    # dumb watermark idea

    def _init_log_watermark(self) -> None:
        # 1) Load the logo pixmap once

        logo_path = Path(Config.RTVS_ASSETS_DIR / 'CombinedCo_RTVS2_logo_cropped_textless.png')
        pm = QtGui.QPixmap(str(logo_path))
        if pm.isNull():
            self._append_log(f"[WARN] Watermark logo not found: {logo_path}")
            return

        self._log_watermark_original = pm

        # 2) Create an overlay label inside the QTextEdit viewport
        self._log_watermark_label = QtWidgets.QLabel(self.log.viewport())
        self._log_watermark_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._log_watermark_label.setStyleSheet("background: transparent;")
        self._log_watermark_label.show()

        # 3) Set opacity
        eff = QtWidgets.QGraphicsOpacityEffect(self._log_watermark_label)
        eff.setOpacity(0.06)  # tweak: 0.05 to 0.15 is a nice range
        self._log_watermark_label.setGraphicsEffect(eff)

        # 4) Keep it updated when the viewport resizes
        self.log.viewport().installEventFilter(self)
        self._update_log_watermark()

    def _update_log_watermark(self) -> None:
        if not hasattr(self, "_log_watermark_label"):
            return
        if not hasattr(self, "_log_watermark_original"):
            return

        vp = self.log.viewport()
        vw, vh = vp.width(), vp.height()
        if vw <= 0 or vh <= 0:
            return

        # Scale relative to the log box size
        target_w = int(vw * 1)  # tweak: 0.40 to 0.70
        target_h = int(vh * 1)

        scaled = self._log_watermark_original.scaled(
            target_w,
            target_h,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )

        self._log_watermark_label.setPixmap(scaled)
        self._log_watermark_label.resize(scaled.size())

        # Position: top-right with padding
        pad = 10
        x = max(pad, vw - scaled.width() - pad)
        y = max(pad, vh - scaled.height() - pad)
        self._log_watermark_label.move(x, y)

        # Ensure it stays visually on top
        self._log_watermark_label.raise_()

    def eventFilter(self, obj, event):
        if obj == self.log.viewport():
            if event.type() == QtCore.QEvent.Type.Resize:
                self._update_log_watermark()
            elif event.type() == QtCore.QEvent.Type.Show:
                self._update_log_watermark()
        return super().eventFilter(obj, event)



    # -------------------------
    # Core helpers
    # -------------------------

    def _append_log(self, text: str) -> None:
        self._assert_gui_thread()
        self.log.append(text)

    def _safe_call(self, label: str, fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            self._append_log(f"[ERROR] {label}: {e}")
            self._append_log(traceback.format_exc())
            QtWidgets.QMessageBox.critical(self, "Error", f"{label}\n\n{e}")
            return None

    def _init_assists(self):
        if self.assists is None:
            self.assists = ConfigAssists()
        self._refresh_db_path_label()
        # self._refresh_profiles_table()
        self._append_log("[OK] ConfigAssists initialized and first-time setup ensured.")

    def _db(self) -> RTVSDB:
        if not self.assists:
            raise RuntimeError("ConfigAssists not initialized.")
        return self.assists.db

    # -------------------------
    # Setup tab
    # -------------------------

    def _build_setup_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        form = QtWidgets.QFormLayout()
        self.db_path_label = QtWidgets.QLabel("(unknown)")
        self.assets_dir_label = QtWidgets.QLabel("(unknown)")
        form.addRow("DB path:", self.db_path_label)
        form.addRow("Assets dir:", self.assets_dir_label)
        layout.addLayout(form)

        btn_row = QtWidgets.QHBoxLayout()
        self.btn_run_setup = QtWidgets.QPushButton("Run first-time setup")
        self.btn_run_setup.clicked.connect(lambda: self._safe_call("Run first-time setup", self._run_setup))
        btn_row.addWidget(self.btn_run_setup)

        self.btn_reload_customers = QtWidgets.QPushButton("Reload customers JSON...")
        self.btn_reload_customers.clicked.connect(lambda: self._safe_call("Reload customers JSON", self._reload_customers_json))
        btn_row.addWidget(self.btn_reload_customers)

        self.btn_open_assets = QtWidgets.QPushButton("Open assets folder")
        self.btn_open_assets.clicked.connect(lambda: self._safe_call("Open assets folder", self._open_assets_folder))
        btn_row.addWidget(self.btn_open_assets)

        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        layout.addWidget(QtWidgets.QLabel("Log:"))
        layout.addWidget(self.log)

        self.tabs.addTab(tab, "Setup")

    def _refresh_db_path_label(self):
        if not self.assists:
            return
        db = self._db()
        db_path = getattr(db, "db_path", None)
        assets_dir = getattr(db, "ASSETS_DIR", None)
        self.db_path_label.setText(str(db_path) if db_path else "(missing db_path on RTVSDB)")
        self.assets_dir_label.setText(str(assets_dir) if assets_dir else "(missing ASSETS_DIR on RTVSDB)")

    def _run_setup(self):
        self._init_assists()  # ensures exists
        self.assists.create_first_time_setup()
        self._append_log("[OK] First-time setup executed.")
        self._refresh_profiles_table()

    def _reload_customers_json(self):
        self._init_assists()
        start_dir = str(getattr(self._db(), "ASSETS_DIR", Path.cwd()))
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select customers JSON",
            start_dir,
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return

        # use filename only because your RTVSDB.load_customer_json_into_db expects json_path
        json_name = Path(path).name
        self._db().load_customer_json_into_db(json_path=path)
        self._append_log(f"[OK] Reloaded customers from {path}")

    def _open_assets_folder(self):
        self._init_assists()
        assets_dir = Path(getattr(self._db(), "ASSETS_DIR", Path.cwd()))
        url = QtCore.QUrl.fromLocalFile(str(assets_dir))
        QtGui.QDesktopServices.openUrl(url)

    # -------------------------
    # Chrome Profiles tab
    # -------------------------

    def _build_chrome_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        top_row = QtWidgets.QHBoxLayout()
        self.btn_refresh_profiles = QtWidgets.QPushButton("Refresh")
        self.btn_refresh_profiles.clicked.connect(lambda: self._safe_call("Refresh profiles", self._refresh_profiles_table))
        top_row.addWidget(self.btn_refresh_profiles)

        self.btn_set_active = QtWidgets.QPushButton("Set selected active")
        self.btn_set_active.clicked.connect(lambda: self._safe_call("Set active", self._set_selected_profile_active))
        top_row.addWidget(self.btn_set_active)

        self.btn_set_inactive = QtWidgets.QPushButton("Set selected inactive")
        self.btn_set_inactive.clicked.connect(lambda: self._safe_call("Set inactive", self._set_selected_profile_inactive))
        top_row.addWidget(self.btn_set_inactive)

        self.btn_mfa_now = QtWidgets.QPushButton("Stamp MFA time: NOW")
        self.btn_mfa_now.clicked.connect(lambda: self._safe_call("Update MFA time now", self._stamp_mfa_now))
        top_row.addWidget(self.btn_mfa_now)

        self.mfa_custom_input = QtWidgets.QLineEdit()
        self.mfa_custom_input.setPlaceholderText("Custom MFA time (YYYY-MM-DD HH:MM:SS)")
        self.mfa_custom_input.setMaximumWidth(240)
        top_row.addWidget(self.mfa_custom_input)

        self.btn_mfa_custom = QtWidgets.QPushButton("Stamp MFA: custom")
        self.btn_mfa_custom.clicked.connect(lambda: self._safe_call("Update MFA time custom", self._stamp_mfa_custom))
        top_row.addWidget(self.btn_mfa_custom)

        self.btn_fetch_first_inactive = QtWidgets.QPushButton("Fetch first inactive + activate")
        self.btn_fetch_first_inactive.clicked.connect(lambda: self._safe_call("Fetch first inactive", self._fetch_first_inactive))
        top_row.addWidget(self.btn_fetch_first_inactive)

        top_row.addStretch(1)
        layout.addLayout(top_row)

        self.profiles_model = QtGui.QStandardItemModel(0, 5)
        self.profiles_model.setHorizontalHeaderLabels(["ID", "Profile", "Status", "Active", "Last MFA"])

        self.profiles_view = QtWidgets.QTableView()
        self.profiles_view.setModel(self.profiles_model)
        self.profiles_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.profiles_view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.profiles_view.horizontalHeader().setStretchLastSection(True)
        self.profiles_view.setSortingEnabled(False)

        layout.addWidget(self.profiles_view)

        self.tabs.addTab(tab, "Chrome Profiles")

    def _query_profiles(self) -> list[ChromeProfileRow]:
        db = self._db()
        db.cursor.execute(
            """
            SELECT id, profile_name, currently_running, is_active, last_mfa_time
            FROM chrome_profiles
            ORDER BY id ASC;
            """
        )
        rows = db.cursor.fetchall()
        out: list[ChromeProfileRow] = []
        for r in rows:
            out.append(
                ChromeProfileRow(
                    id=int(r[0]),
                    profile_name=str(r[1]),
                    currently_running=(None if r[2] is None else str(r[2])),
                    is_active=int(r[3]),
                    last_mfa_time=str(r[4]),
                )
            )
        return out

    def _refresh_profiles_table(self):
        self._init_assists()
        profiles = self._query_profiles()

        self.profiles_model.removeRows(0, self.profiles_model.rowCount())
        for p in profiles:
            items = [
                QtGui.QStandardItem(str(p.id)),
                QtGui.QStandardItem(p.profile_name),
                QtGui.QStandardItem("" if p.currently_running is None else p.currently_running),
                QtGui.QStandardItem(str(p.is_active)),
                QtGui.QStandardItem(p.last_mfa_time),
            ]
            # simple visual cue for active
            if p.is_active == 1:
                for it in items:
                    it.setFont(QtGui.QFont(it.font().family(), it.font().pointSize(), QtGui.QFont.Weight.Bold))
            self.profiles_model.appendRow(items)

        self._append_log(f"[OK] Loaded {len(profiles)} chrome profiles.")

    def _selected_profile_name(self) -> str | None:
        idxs = self.profiles_view.selectionModel().selectedRows()
        if not idxs:
            return None
        row = idxs[0].row()
        return self.profiles_model.item(row, 1).text()

    def _set_selected_profile_active(self):
        name = self._selected_profile_name()
        if not name:
            QtWidgets.QMessageBox.information(self, "Select a row", "Select a profile row first.")
            return
        self.assists.set_profile_active(name)
        self._append_log(f"[OK] Set active: {name}")
        self._refresh_profiles_table()

    def _set_selected_profile_inactive(self):
        name = self._selected_profile_name()
        if not name:
            QtWidgets.QMessageBox.information(self, "Select a row", "Select a profile row first.")
            return
        self.assists.set_profile_inactive(name)
        self._append_log(f"[OK] Set inactive: {name}")
        self._refresh_profiles_table()

    def _stamp_mfa_now(self):
        name = self._selected_profile_name()
        if not name:
            QtWidgets.QMessageBox.information(self, "Select a row", "Select a profile row first.")
            return

        # Safer than your string-format SQL: do parameterized update directly here
        db = self._db()
        with db.connection:
            db.cursor.execute(
                "UPDATE chrome_profiles SET last_mfa_time = CURRENT_TIMESTAMP WHERE profile_name = ?;",
                (name,),
            )
        self._append_log(f"[OK] MFA stamped (NOW) for: {name}")
        self._refresh_profiles_table()

    def _stamp_mfa_custom(self):
        name = self._selected_profile_name()
        if not name:
            QtWidgets.QMessageBox.information(self, "Select a row", "Select a profile row first.")
            return

        ts = self.mfa_custom_input.text().strip()
        if not ts:
            QtWidgets.QMessageBox.information(self, "Missing timestamp", "Enter a custom timestamp first.")
            return

        # Parameterized update for safety
        db = self._db()
        with db.connection:
            db.cursor.execute(
                "UPDATE chrome_profiles SET last_mfa_time = ? WHERE profile_name = ?;",
                (ts, name),
            )
        self._append_log(f"[OK] MFA stamped (custom) for: {name} -> {ts}")
        self._refresh_profiles_table()

    def _fetch_first_inactive(self):
        self._init_assists()
        name = self.assists.fetch_first_inactive_profile()
        if not name:
            QtWidgets.QMessageBox.information(self, "No inactive profiles", "All profiles appear active.")
            self._append_log("[INFO] No inactive profile found.")
            return
        self._append_log(f"[OK] Fetched and activated first inactive: {name}")
        self._refresh_profiles_table()

    # -------------------------
    # Customers tab
    # -------------------------

    def _build_customers_tab(self):
        db = self._db()
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        top = QtWidgets.QHBoxLayout()

        self.customer_name_combo = QtWidgets.QComboBox()
        self.customer_name_combo.setEditable(False)
        self.customer_name_combo.addItems(sorted(db.get_customer_names_list()))
        top.addWidget(self.customer_name_combo)


        # self.customer_id_input = QtWidgets.QLineEdit()
        # self.customer_id_input.setPlaceholderText("Customer ID (int)")
        # self.customer_id_input.setMaximumWidth(200)
        # top.addWidget(self.customer_id_input)

        self.btn_load_customer = QtWidgets.QPushButton("Load")
        self.btn_load_customer.clicked.connect(lambda: self._safe_call("Load customer", self._load_customer))
        top.addWidget(self.btn_load_customer)

        self.total_client_count = QtWidgets.QLabel(str(db.get_total_customers_count()))
        top.addWidget(self.total_client_count)

        top.addStretch(1)
        layout.addLayout(top)

        self.roles_table = QtWidgets.QTableWidget(0, 2)
        self.roles_table.setHorizontalHeaderLabels(["Role", "Username"])
        self.roles_table.horizontalHeader().setStretchLastSection(True)
        self.roles_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.roles_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.roles_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked | QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)
        layout.addWidget(self.roles_table)

        btns = QtWidgets.QHBoxLayout()
        self.btn_update_selected_role = QtWidgets.QPushButton("Update selected role username")
        self.btn_update_selected_role.clicked.connect(lambda: self._safe_call("Update selected role", self._update_selected_role))
        btns.addWidget(self.btn_update_selected_role)

        self.btn_update_all_roles = QtWidgets.QPushButton("Update all rows")
        self.btn_update_all_roles.clicked.connect(lambda: self._safe_call("Update all roles", self._update_all_roles))
        btns.addWidget(self.btn_update_all_roles)

        btns.addStretch(1)
        layout.addLayout(btns)

        self.tabs.addTab(tab, "Customers")


    def _load_customer(self):
        self._init_assists()
        db = self._db()
        name = self.customer_name_combo.currentText()
        customer_id = db.get_customer_id_from_name(name)



        role_dict = self.assists.get_role_dict_for_customer_id(customer_id)
        self.roles_table.setRowCount(0)

        for role, username in role_dict.items():
            r = self.roles_table.rowCount()
            self.roles_table.insertRow(r)

            role_item = QtWidgets.QTableWidgetItem(str(role))
            role_item.setFlags(role_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            self.roles_table.setItem(r, 0, role_item)

            user_item = QtWidgets.QTableWidgetItem("" if username is None else str(username))
            self.roles_table.setItem(r, 1, user_item)

        self._append_log(f"[OK] Loaded {len(role_dict)} roles for customer_id={customer_id}")

    def _selected_role_row(self) -> int | None:
        sel = self.roles_table.selectionModel().selectedRows()
        if not sel:
            return None
        return sel[0].row()

    def _update_selected_role(self):
        self._init_assists()
        db = self._db()
        name = self.customer_name_combo.currentText()
        customer_id = db.get_customer_id_from_name(name)
        row = self._selected_role_row()
        if row is None:
            QtWidgets.QMessageBox.information(self, "Select a row", "Select a role row first.")
            return

        role = self.roles_table.item(row, 0).text()
        username = self.roles_table.item(row, 1).text().strip()

        self.assists.update_username_for_role(customer_id, role, username)
        self._append_log(f"[OK] Updated username for customer_id={customer_id}, role={role} -> {username}")

    def _update_all_roles(self):
        self._init_assists()
        db = self._db()
        name = self.customer_name_combo.currentText()
        customer_id = db.get_customer_id_from_name(name)

        n = self.roles_table.rowCount()
        if n == 0:
            QtWidgets.QMessageBox.information(self, "No data", "Load a customer first.")
            return

        for row in range(n):
            role = self.roles_table.item(row, 0).text()
            username = self.roles_table.item(row, 1).text().strip()
            self.assists.update_username_for_role(customer_id, role, username)

        self._append_log(f"[OK] Updated all {n} roles for customer_id={customer_id}")

    # -------------------------
    # Tests tab
    # -------------------------

    def _assert_gui_thread(self):
        app = QtWidgets.QApplication.instance()
        if app and QtCore.QThread.currentThread() != app.thread():
            raise RuntimeError("UI touched from non-GUI thread")

    def _build_tests_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        top_row = QtWidgets.QHBoxLayout()

        self.btn_tests_refresh = QtWidgets.QPushButton("Refresh")
        self.btn_tests_refresh.clicked.connect(lambda: self._safe_call("Refresh tests", self._refresh_tests_views))
        top_row.addWidget(self.btn_tests_refresh)

        self.btn_start_new_test = QtWidgets.QPushButton("Start new test...")
        self.btn_start_new_test.clicked.connect(lambda: self._safe_call("Start new test dialog", self._open_start_test_dialog))
        top_row.addWidget(self.btn_start_new_test)

        top_row.addStretch(1)
        layout.addLayout(top_row)

        # Runs table (test_runs)
        self.runs_model = QtGui.QStandardItemModel(0, 8)
        self.runs_model.setHorizontalHeaderLabels([
            "Run ID", "Status", "Failed", "Category", "Env", "Package", "Last Update", "Last Message"
        ])

        self.runs_view = QtWidgets.QTableView()
        self.runs_view.setModel(self.runs_model)
        self.runs_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.runs_view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.runs_view.horizontalHeader().setStretchLastSection(True)
        self.runs_view.setSortingEnabled(False)
        layout.addWidget(QtWidgets.QLabel("Latest runs (test_runs):"))
        layout.addWidget(self.runs_view)

        # Logs table (test_logs) for selected run
        self.logs_model = QtGui.QStandardItemModel(0, 6)
        self.logs_model.setHorizontalHeaderLabels([
            "Timestamp", "Type", "Status", "Test", "Message", "Worker"
        ])

        self.logs_view = QtWidgets.QTableView()
        self.logs_view.setModel(self.logs_model)
        self.logs_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.logs_view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.logs_view.horizontalHeader().setStretchLastSection(True)
        self.logs_view.setSortingEnabled(False)

        layout.addWidget(QtWidgets.QLabel("Latest logs for selected run (test_logs):"))
        layout.addWidget(self.logs_view)

        # When selection changes, refresh logs
        self.runs_view.selectionModel().selectionChanged.connect(
            lambda *_: self._safe_call("Refresh run logs", self._refresh_logs_for_selected_run)
        )

        self.tabs.addTab(tab, "Tests")

        # initial load (safe)
        self._safe_call("Initial tests refresh", self._refresh_tests_views)

    def _query_runs(self, limit: int = 200) -> list[TestRunRow]:
        db = self._db()
        cursor = db.connection.cursor()
        cursor.execute(
            f"""
            SELECT
                run_id, category, env, test_package, browsers,
                COALESCE(clients,''), COALESCE(user_roles,''), threads, multiprocessing,
                started_at, ended_at, status, failed_cases,
                last_update_at, last_update_message
            FROM test_runs
            ORDER BY started_at DESC
            LIMIT {int(limit)};
            """
        )
        rows = cursor.fetchall()
        out: list[TestRunRow] = []
        for r in rows:
            out.append(TestRunRow(
                run_id=str(r[0]),
                category=str(r[1]),
                env=str(r[2]),
                test_package=str(r[3]),
                browsers=str(r[4]),
                clients=str(r[5]),
                user_roles=str(r[6]),
                threads=int(r[7]),
                multiprocessing=int(r[8]),
                started_at=str(r[9]),
                ended_at=(None if r[10] is None else str(r[10])),
                status=str(r[11]),
                failed_cases=int(r[12]),
                last_update_at=(None if r[13] is None else str(r[13])),
                last_update_message=(None if r[14] is None else str(r[14])),
            ))
        return out

    def _query_logs(self, run_id: str, limit: int = 200) -> list[TestLogRow]:
        db = self._db()
        cursor = db.connection.cursor()

        cursor.execute(
            f"""
            SELECT timestamp, type, status, test_name, message, worker, pid, current_url
            FROM test_logs
            WHERE run_id = ?
            ORDER BY id DESC
            LIMIT {int(limit)};
            """,
            (run_id,),
        )
        rows = cursor.fetchall()
        out: list[TestLogRow] = []
        for r in rows:
            out.append(TestLogRow(
                timestamp=str(r[0]),
                type=str(r[1]),
                status=str(r[2]),
                test_name=(None if r[3] is None else str(r[3])),
                message=(None if r[4] is None else str(r[4])),
                worker=(None if r[5] is None else str(r[5])),
                pid=(None if r[6] is None else int(r[6])),
                current_url=(None if r[7] is None else str(r[7])),
            ))
        return out

    def _refresh_tests_views(self):
        self._assert_gui_thread()
        self._init_assists()
        self._refresh_runs_table()
        self._refresh_logs_for_selected_run()

    def _refresh_runs_table(self):
        self._assert_gui_thread()
        runs = self._query_runs()

        # keep currently selected run_id if possible
        selected = self._selected_run_id()

        self.runs_model.removeRows(0, self.runs_model.rowCount())
        for r in runs:
            items = [
                QtGui.QStandardItem(r.run_id),
                QtGui.QStandardItem(r.status),
                QtGui.QStandardItem(str(r.failed_cases)),
                QtGui.QStandardItem(r.category),
                QtGui.QStandardItem(r.env),
                QtGui.QStandardItem(r.test_package),
                QtGui.QStandardItem("" if r.last_update_at is None else r.last_update_at),
                QtGui.QStandardItem("" if r.last_update_message is None else r.last_update_message),
            ]

            # simple visual cue
            if r.status in ("FAIL", "ERR"):
                f = QtGui.QFont(items[0].font())
                f.setBold(True)
                for it in items:
                    it.setFont(f)

            self.runs_model.appendRow(items)

        # reselect
        if selected:
            for row in range(self.runs_model.rowCount()):
                if self.runs_model.item(row, 0).text() == selected:
                    self.runs_view.selectRow(row)
                    break

        self._append_log(f"[OK] Loaded {len(runs)} runs from test_runs.")

    def _selected_run_id(self) -> str | None:
        idxs = self.runs_view.selectionModel().selectedRows()
        if not idxs:
            return None
        row = idxs[0].row()
        return self.runs_model.item(row, 0).text()

    def _refresh_logs_for_selected_run(self):
        self._assert_gui_thread()
        run_id = self._selected_run_id()
        self.logs_model.removeRows(0, self.logs_model.rowCount())
        if not run_id:
            return

        logs = self._query_logs(run_id)

        for l in reversed(logs):  # show oldest at top
            items = [
                QtGui.QStandardItem(l.timestamp),
                QtGui.QStandardItem(l.type),
                QtGui.QStandardItem(l.status),
                QtGui.QStandardItem("" if l.test_name is None else l.test_name),
                QtGui.QStandardItem("" if l.message is None else l.message),
                QtGui.QStandardItem("" if l.worker is None else l.worker),
            ]
            self.logs_model.appendRow(items)

    def _open_start_test_dialog(self):
        self._init_assists()
        dlg = StartTestDialog(self, self._db())
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        cfg = dlg.get_config()
        self._launch_run_from_config(cfg)

    def _launch_run_from_config(self, cfg: dict):
        """
        1) Insert test_runs row
        2) Insert a controller log line
        3) Start worker thread to execute lanes
        """
        self._init_assists()

        # Create a fresh ConfigAssists just for run creation (keeps controller state clean)
        ca = ConfigAssists()

        rc = ca.get_run_configuration()
        rc.prefix = cfg["prefix"]
        rc.category = cfg["category"]
        rc.env = cfg["env"]
        rc.test_package = cfg["marker"]
        rc.test_package_desc = cfg.get("test_package_desc")
        rc.started_at = datetime.now().strftime("%Y%m%d_%H%M%S")

        clients: list[str] = cfg["clients"]
        roles: list[str] = cfg["roles"]
        browsers: list[str] = cfg["browsers"]

        # store selection summary in run row
        rc.clients = ",".join(clients)
        rc.user_roles = ",".join(roles)
        rc.browsers = ",".join(browsers)

        mp_clients = bool(cfg["mp_clients"])
        mp_roles = bool(cfg["mp_roles"])
        mp_browsers = bool(cfg["mp_browsers"])
        rc.multiprocessing = mp_clients or mp_roles or mp_browsers
        rc.threads = int(cfg["max_parallel_lanes"])

        ca.set_unique_id()
        ca.create_run_id()

        # Insert run
        ca.db.insert_test_run(rc)

        # Controller-side log line
        ca.db.insert_test_log(
            run_id=rc.run_id,
            type_="controller",
            status="Info",
            message=f"Run launched from Controller UI | marker={rc.test_package} | lanes<= {rc.threads}",
            test_package=rc.test_package,
        )

        # Close that helper DB (tests will open their own connections)
        db_path = str(ca.db.db_path)
        ca.db.close()

        # Refresh UI to show the new run immediately
        self._refresh_tests_views()

        # Start worker in background (so UI does not freeze)
        self._append_log(f"[OK] Starting lanes for run_id={rc.run_id}")

        worker = TestRunWorker(
            db_path=db_path,
            run_id=rc.run_id,
            marker=cfg["marker"],
            clients=clients,
            roles=roles,
            browsers=browsers,
            mp_clients=mp_clients,
            mp_roles=mp_roles,
            mp_browsers=mp_browsers,
            max_parallel_lanes=int(cfg["max_parallel_lanes"]),
            test_env=cfg["env"],
            headless=bool(cfg["headless"]),
        )

        self._workers[rc.run_id] = worker

        worker.run_finished.connect(self._on_run_finished)
        worker.run_failed.connect(self._on_run_failed)

        # Cleanup so dict doesn't grow forever
        worker.run_finished.connect(lambda rid, *_: self._cleanup_worker(rid))
        worker.run_failed.connect(lambda rid, *_: self._cleanup_worker(rid))

        worker.start()

    def _on_run_finished(self, run_id: str, status: str):
        self._append_log(f"[OK] Run finished: {run_id} -> {status}")
        self._refresh_tests_views()

    def _on_run_failed(self, run_id: str, error: str):
        self._append_log(f"[ERROR] Run failed: {run_id} -> {error}")
        self._refresh_tests_views()

    def _cleanup_worker(self, run_id: str):
        w = self._workers.pop(run_id, None)
        if w is not None:
            w.quit()
            w.wait(2000)
            w.deleteLater()


def main():
    app = QtWidgets.QApplication(sys.argv)

    app_icon = QtGui.QIcon(str(Config.RTVS_ASSETS_DIR / 'rtvs.ico'))
    app.setWindowIcon(app_icon)

    splash_logo_path = Config.RTVS_ASSETS_DIR / "CombinedCo_RTVS2_logo.png"

    splash = QSplashScreen(QPixmap(splash_logo_path))
    splash.setWindowFlags(splash.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()
    time.sleep(2)  # simulate loading time

    win = ControllerWindow()
    win.setWindowIcon(app_icon)
    win.show()

    splash.finish(win)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()