from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox, QComboBox, QCheckBox, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import Signal
from app.config.settings import Settings

class SettingsView(QWidget):
    settings_changed = Signal()

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.timeout_input = QLineEdit()
        self.timeout_input.setText(str(self.settings.get("timeout")))
        form.addRow("Diagnostic Timeout (s):", self.timeout_input)

        self.ping_count_input = QSpinBox()
        self.ping_count_input.setRange(1, 20)
        self.ping_count_input.setValue(self.settings.get("ping_count"))
        form.addRow("Ping Count:", self.ping_count_input)

        self.host_input = QLineEdit()
        self.host_input.setText(self.settings.get("default_test_host"))
        form.addRow("Default Test Host:", self.host_input)

        self.url_input = QLineEdit()
        self.url_input.setText(self.settings.get("http_test_url"))
        form.addRow("HTTP/HTTPS URL:", self.url_input)

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(self.settings.get("tcp_test_port"))
        form.addRow("TCP Test Port:", self.port_input)

        self.retention_input = QSpinBox()
        self.retention_input.setRange(5, 500)
        self.retention_input.setValue(self.settings.get("history_retention"))
        form.addRow("History Retention Limit:", self.retention_input)

        self.auto_start_cb = QCheckBox("Start diagnostics automatically on launch")
        self.auto_start_cb.setChecked(self.settings.get("start_automatically"))
        form.addRow("", self.auto_start_cb)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(self.settings.get("theme"))
        form.addRow("Application Theme:", self.theme_combo)

        layout.addLayout(form)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()

    def save_settings(self):
        try:
            timeout_val = float(self.timeout_input.text())
            self.settings.set("timeout", timeout_val)
        except ValueError:
            QMessageBox.critical(self, "Invalid Value", "Timeout must be a decimal number.")
            return

        self.settings.set("ping_count", self.ping_count_input.value())
        self.settings.set("default_test_host", self.host_input.text().strip())
        self.settings.set("http_test_url", self.url_input.text().strip())
        self.settings.set("tcp_test_port", self.port_input.value())
        self.settings.set("history_retention", self.retention_input.value())
        self.settings.set("start_automatically", self.auto_start_cb.isChecked())
        self.settings.set("theme", self.theme_combo.currentText())
        
        QMessageBox.information(self, "Settings Saved", "Configurations updated and saved successfully.")
        self.settings_changed.emit()
