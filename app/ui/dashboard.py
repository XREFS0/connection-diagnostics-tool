from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QProgressBar
from PySide6.QtCore import Qt, Signal
from typing import Dict, Any, List
from app.models.diagnostic_results import DiagnosticStepResult

class DashboardView(QWidget):
    run_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        self.status_banner = QFrame()
        self.status_banner.setObjectName("Card")
        self.status_banner.setStyleSheet("#Card { background-color: #1e293b; border-left: 6px solid #64748b; }")
        banner_layout = QHBoxLayout(self.status_banner)
        banner_layout.setContentsMargins(16, 16, 16, 16)
        
        self.status_text = QLabel("Connection State Unknown")
        self.status_text.setStyleSheet("font-size: 18px; font-weight: bold;")
        banner_layout.addWidget(self.status_text)
        
        self.run_btn = QPushButton("Run Diagnostics")
        self.run_btn.setObjectName("RunDiagnosticsBtn")
        self.run_btn.clicked.connect(self.run_clicked.emit)
        banner_layout.addWidget(self.run_btn, 0, Qt.AlignRight)
        
        layout.addWidget(self.status_banner)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 14)
        layout.addWidget(self.progress_bar)

        grid = QVBoxLayout()
        grid.setSpacing(12)

        row1 = QHBoxLayout()
        self.card_internet = self.create_card("Internet Status", "Offline")
        self.card_gateway = self.create_card("Gateway Status", "Offline")
        self.card_dns = self.create_card("DNS Status", "Offline")
        row1.addWidget(self.card_internet)
        row1.addWidget(self.card_gateway)
        row1.addWidget(self.card_dns)
        grid.addLayout(row1)

        row2 = QHBoxLayout()
        self.card_latency = self.create_card("Current Latency", "--")
        self.card_avg_latency = self.create_card("Average Latency", "--")
        self.card_jitter = self.create_card("Jitter", "--")
        self.card_loss = self.create_card("Packet Loss", "--")
        row2.addWidget(self.card_latency)
        row2.addWidget(self.card_avg_latency)
        row2.addWidget(self.card_jitter)
        row2.addWidget(self.card_loss)
        grid.addLayout(row2)

        row3 = QHBoxLayout()
        self.card_pub_ip = self.create_card("Public IP", "Unknown")
        self.card_local_ip = self.create_card("Local IP", "Unknown")
        self.card_interface = self.create_card("Active Interface", "Unknown")
        row3.addWidget(self.card_pub_ip)
        row3.addWidget(self.card_local_ip)
        row3.addWidget(self.card_interface)
        grid.addLayout(row3)

        layout.addLayout(grid)
        layout.addStretch()

    def create_card(self, title: str, default_val: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(8)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("CardTitle")
        
        lbl_val = QLabel(default_val)
        lbl_val.setObjectName("CardValue")
        
        lay.addWidget(lbl_title)
        lay.addWidget(lbl_val)
        return card

    def update_card(self, card: QFrame, val: str):
        lbl = card.findChild(QLabel, "CardValue")
        if lbl:
            lbl.setText(val)

    def set_running(self, running: bool):
        self.run_btn.setEnabled(not running)
        self.progress_bar.setVisible(running)
        if running:
            self.progress_bar.setValue(0)

    def update_progress(self, index: int):
        self.progress_bar.setValue(index)

    def apply_results(self, results: List[DiagnosticStepResult]):
        internet = results[7].status
        gateway = results[3].status
        dns = results[5].status
        
        avg_lat = results[11].details.get("Average Latency", "--")
        jitter = results[11].details.get("Jitter", "--")
        loss = results[12].details.get("Packet Loss Ratio", "--")
        
        pub_ip = results[7].details.get("Public IP", "Offline / Private") if len(results) > 7 else "Unknown"
        local_ip = results[1].details.get("IPv4", "Unknown")
        
        self.update_card(self.card_internet, internet)
        self.update_card(self.card_gateway, gateway)
        self.update_card(self.card_dns, dns)
        self.update_card(self.card_avg_latency, avg_lat)
        self.update_card(self.card_jitter, jitter)
        self.update_card(self.card_loss, loss)
        self.update_card(self.card_local_ip, local_ip)
        self.update_card(self.card_pub_ip, pub_ip)
        
        interfaces = results[0].details.get("Interfaces", [])
        if interfaces:
            self.update_card(self.card_interface, interfaces[0])

        errors = [r for r in results if r.status == "Failed"]
        warnings = [r for r in results if r.status == "Warning"]

        if errors:
            self.status_text.setText("Connection Problems Detected")
            self.status_banner.setStyleSheet("#Card { background-color: #1e293b; border-left: 6px solid #ef4444; }")
        elif warnings:
            self.status_text.setText("Connection Has Warnings")
            self.status_banner.setStyleSheet("#Card { background-color: #1e293b; border-left: 6px solid #eab308; }")
        else:
            self.status_text.setText("Connection Healthy")
            self.status_banner.setStyleSheet("#Card { background-color: #1e293b; border-left: 6px solid #22c55e; }")
