from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt
from app.ui.dashboard import DashboardView
from app.ui.details import DetailsView
from app.ui.network_info import NetworkInfoView
from app.ui.history import HistoryView
from app.ui.settings_view import SettingsView
from app.ui.styles import DARK_STYLE
from app.diagnostics.runner import DiagnosticRunner
from app.storage.database import HistoryStore
from app.config.settings import Settings
import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connection Diagnostics Tool")
        self.resize(1000, 650)
        self.setStyleSheet(DARK_STYLE)
        
        self.settings = Settings()
        self.store = HistoryStore()
        
        self.init_ui()

        if self.settings.get("start_automatically"):
            self.start_diagnostics()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        title_frame = QFrame()
        title_frame.setObjectName("Header")
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 0, 20, 0)
        title_lbl = QLabel("DIAGNOSTICS")
        title_lbl.setObjectName("AppTitle")
        title_layout.addWidget(title_lbl)
        sidebar_layout.addWidget(title_frame)

        self.nav_buttons = []
        self.dashboard_btn = self.add_nav_button("Dashboard", 0, sidebar_layout)
        self.details_btn = self.add_nav_button("Detailed View", 1, sidebar_layout)
        self.net_info_btn = self.add_nav_button("Network Interfaces", 2, sidebar_layout)
        self.history_btn = self.add_nav_button("Diagnostic History", 3, sidebar_layout)
        self.settings_btn = self.add_nav_button("Settings", 4, sidebar_layout)

        sidebar_layout.addStretch()

        footer_lbl = QLabel("© 2026 XREFS0")
        footer_lbl.setAlignment(Qt.AlignCenter)
        footer_lbl.setStyleSheet("color: #64748b; font-size: 11px; padding-bottom: 16px;")
        sidebar_layout.addWidget(footer_lbl)

        main_layout.addWidget(sidebar)

        content_pane = QFrame()
        content_pane.setObjectName("MainContent")
        content_layout = QVBoxLayout(content_pane)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("Header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(self.page_title)
        content_layout.addWidget(header)

        self.stack = QStackedWidget()
        
        self.dashboard_view = DashboardView()
        self.dashboard_view.run_clicked.connect(self.start_diagnostics)
        
        self.details_view = DetailsView()
        self.net_info_view = NetworkInfoView()
        
        self.history_view = HistoryView()
        self.history_view.view_details_requested.connect(self.show_historical_details)
        
        self.settings_view = SettingsView()
        self.settings_view.settings_changed.connect(self.reload_settings)

        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.details_view)
        self.stack.addWidget(self.net_info_view)
        self.stack.addWidget(self.history_view)
        self.stack.addWidget(self.settings_view)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_pane)

        self.set_active_page(0)

    def add_nav_button(self, text: str, index: int, layout: QVBoxLayout) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("SidebarButton")
        btn.setProperty("active", "false")
        btn.clicked.connect(lambda: self.set_active_page(index))
        layout.addWidget(btn)
        self.nav_buttons.append(btn)
        return btn

    def set_active_page(self, index: int):
        self.stack.setCurrentIndex(index)
        titles = ["Dashboard", "Detailed View", "Network Interfaces", "Diagnostic History", "Settings"]
        self.page_title.setText(titles[index])
        
        for idx, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if idx == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if index == 2:
            self.net_info_view.refresh()
        elif index == 3:
            self.history_view.refresh()

    def start_diagnostics(self):
        self.dashboard_view.set_running(True)
        
        self.runner = DiagnosticRunner(self.settings.data)
        self.runner.step_started.connect(self.on_step_started)
        self.runner.step_finished.connect(self.on_step_finished)
        self.runner.pipeline_finished.connect(self.on_pipeline_finished)
        self.runner.start()

    def on_step_started(self, idx: int, name: str):
        self.dashboard_view.update_progress(idx)

    def on_step_finished(self, idx: int, result: str):
        pass

    def on_pipeline_finished(self, results: list):
        self.dashboard_view.set_running(False)
        self.dashboard_view.apply_results(results)
        self.details_view.apply_results(results)

        avg_lat = results[11].details.get("Average Latency", "0.0")
        loss = results[12].details.get("Packet Loss Ratio", "0.0%")
        jitter = results[11].details.get("Jitter", "0.0")
        
        errors = [r for r in results if r.status == "Failed"]
        warnings = [r for r in results if r.status == "Warning"]
        
        status = "Healthy"
        if errors:
            status = "Problems Detected"
        elif warnings:
            status = "Warnings Detected"

        session = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "avg_latency": avg_lat,
            "packet_loss": loss,
            "jitter": jitter,
            "steps": [
                {
                    "name": r.name,
                    "status": r.status,
                    "duration_ms": r.duration_ms,
                    "result": r.result,
                    "details": r.details,
                    "error": r.error
                } for r in results
            ]
        }
        self.store.save_session(session, self.settings.get("history_retention"))
        self.history_view.refresh()

    def show_historical_details(self, results: list):
        self.details_view.apply_results(results)
        self.set_active_page(1)

    def reload_settings(self):
        self.settings.load()
