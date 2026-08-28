from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QFileDialog, QMessageBox
from PySide6.QtCore import Qt, Signal
import json
import csv
from typing import List, Dict, Any
from app.storage.database import HistoryStore

class HistoryView(QWidget):
    view_details_requested = Signal(list)

    def __init__(self):
        super().__init__()
        self.store = HistoryStore()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        actions = QHBoxLayout()
        self.export_btn = QPushButton("Export Diagnostic Report")
        self.export_btn.clicked.connect(self.export_report)
        
        self.clear_btn = QPushButton("Clear History")
        self.clear_btn.clicked.connect(self.clear_history)
        
        actions.addWidget(self.export_btn)
        actions.addWidget(self.clear_btn)
        actions.addStretch()
        layout.addLayout(actions)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Status", "Avg Latency", "Packet Loss", "Jitter", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellDoubleClicked.connect(self.row_double_clicked)
        layout.addWidget(self.table)
        
        self.refresh()

    def refresh(self):
        self.table.setRowCount(0)
        self.history_records = self.store.get_all()
        self.table.setRowCount(len(self.history_records))
        for row, rec in enumerate(self.history_records):
            self.table.setItem(row, 0, QTableWidgetItem(str(rec.get("timestamp", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(rec.get("status", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(rec.get("avg_latency", ""))))
            self.table.setItem(row, 3, QTableWidgetItem(str(rec.get("packet_loss", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(str(rec.get("jitter", ""))))
            
            btn = QPushButton("View Details")
            btn.clicked.connect(lambda checked=False, r=row: self.view_details_of_row(r))
            self.table.setCellWidget(row, 5, btn)

    def row_double_clicked(self, row, col):
        self.view_details_of_row(row)

    def view_details_of_row(self, row: int):
        rec = self.history_records[row]
        steps_data = rec.get("steps", [])
        from app.models.diagnostic_results import DiagnosticStepResult
        results = []
        for s in steps_data:
            results.append(DiagnosticStepResult(
                name=s.get("name", ""),
                status=s.get("status", ""),
                duration_ms=s.get("duration_ms", 0.0),
                result=s.get("result", ""),
                details=s.get("details", {}),
                error=s.get("error", "")
            ))
        self.view_details_requested.emit(results)

    def clear_history(self):
        self.store.clear()
        self.refresh()

    def export_report(self):
        if not self.history_records:
            QMessageBox.information(self, "Export Diagnostic Report", "No diagnostic history records available to export.")
            return

        filepath, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Diagnostic Report",
            "",
            "JSON (*.json);;CSV (*.csv);;Text (*.txt)"
        )
        if not filepath:
            return

        try:
            if "json" in selected_filter.lower() or filepath.endswith(".json"):
                with open(filepath, "w") as f:
                    json.dump(self.history_records, f, indent=4)
            elif "csv" in selected_filter.lower() or filepath.endswith(".csv"):
                with open(filepath, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Status", "Avg Latency", "Packet Loss", "Jitter"])
                    for rec in self.history_records:
                        writer.writerow([
                            rec.get("timestamp", ""),
                            rec.get("status", ""),
                            rec.get("avg_latency", ""),
                            rec.get("packet_loss", ""),
                            rec.get("jitter", "")
                        ])
            else:
                with open(filepath, "w") as f:
                    for rec in self.history_records:
                        f.write(f"Timestamp: {rec.get('timestamp')}\n")
                        f.write(f"Status: {rec.get('status')}\n")
                        f.write(f"Avg Latency: {rec.get('avg_latency')}\n")
                        f.write(f"Packet Loss: {rec.get('packet_loss')}\n")
                        f.write(f"Jitter: {rec.get('jitter')}\n")
                        f.write("-" * 40 + "\n")
            QMessageBox.information(self, "Export Diagnostic Report", "Diagnostic report successfully exported.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not write file: {str(e)}")
