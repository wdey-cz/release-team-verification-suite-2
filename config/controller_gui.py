from __future__ import annotations
from config.rtvsdb import RTVSDB  # type: ignore
from config.config_assists import ConfigAssists  # type: ignore
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

@dataclass
class ChromeProfileRow:
    id: int
    profile_name: str
    currently_running: str | None
    is_active: int
    last_mfa_time: str


class ControllerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTVS Controller")
        self.resize(1100, 720)

        self.assists: ConfigAssists | None = None

        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(120)

        self._build_setup_tab()
        self._build_chrome_tab()
        self._build_customers_tab()

        self.statusBar().showMessage("Ready")

        # Try to initialize on startup, but do not crash the UI if something fails
        self._safe_call("Init ConfigAssists", self._init_assists)

    # -------------------------
    # Core helpers
    # -------------------------

    def _append_log(self, text: str) -> None:
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
        self._db().load_customer_json_into_db(json_path=json_name)
        self._append_log(f"[OK] Reloaded customers from {json_name}")

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
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        top = QtWidgets.QHBoxLayout()
        self.customer_id_input = QtWidgets.QLineEdit()
        self.customer_id_input.setPlaceholderText("Customer ID (int)")
        self.customer_id_input.setMaximumWidth(200)
        top.addWidget(self.customer_id_input)

        self.btn_load_customer = QtWidgets.QPushButton("Load")
        self.btn_load_customer.clicked.connect(lambda: self._safe_call("Load customer", self._load_customer))
        top.addWidget(self.btn_load_customer)

        self.customer_name_label = QtWidgets.QLabel("Customer name: (not loaded)")
        top.addWidget(self.customer_name_label)

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

    def _parse_customer_id(self) -> int:
        raw = self.customer_id_input.text().strip()
        if not raw:
            raise ValueError("Customer ID is required.")
        return int(raw)

    def _load_customer(self):
        self._init_assists()
        customer_id = self._parse_customer_id()

        db = self._db()
        name = db.get_customer_name_from_id(customer_id)
        self.customer_name_label.setText(f"Customer name: {name if name else '(not found)'}")

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
        customer_id = self._parse_customer_id()
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
        customer_id = self._parse_customer_id()

        n = self.roles_table.rowCount()
        if n == 0:
            QtWidgets.QMessageBox.information(self, "No data", "Load a customer first.")
            return

        for row in range(n):
            role = self.roles_table.item(row, 0).text()
            username = self.roles_table.item(row, 1).text().strip()
            self.assists.update_username_for_role(customer_id, role, username)

        self._append_log(f"[OK] Updated all {n} roles for customer_id={customer_id}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = ControllerWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()