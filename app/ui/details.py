from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt
from typing import List
from app.models.diagnostic_results import DiagnosticStepResult

class DetailsView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(12)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)

    def apply_results(self, results: List[DiagnosticStepResult]):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for step in results:
            self.container_layout.addWidget(self.create_step_card(step))
        self.container_layout.addStretch()

    def create_step_card(self, step: DiagnosticStepResult) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        
        header = QHBoxLayout()
        name_lbl = QLabel(step.name)
        name_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        status_lbl = QLabel(step.status)
        if step.status == "Passed":
            status_lbl.setStyleSheet("color: #22c55e; font-weight: bold;")
        elif step.status == "Warning":
            status_lbl.setStyleSheet("color: #eab308; font-weight: bold;")
        elif step.status == "Failed":
            status_lbl.setStyleSheet("color: #ef4444; font-weight: bold;")
        else:
            status_lbl.setStyleSheet("color: #94a3b8;")
            
        header.addWidget(name_lbl)
        header.addWidget(status_lbl, 0, Qt.AlignRight)
        card_layout.addLayout(header)

        body = QVBoxLayout()
        body.setContentsMargins(0, 8, 0, 0)
        body.setSpacing(4)
        
        if step.result:
            body.addWidget(QLabel(f"Result: {step.result}"))
        if step.duration_ms > 0:
            body.addWidget(QLabel(f"Duration: {step.duration_ms:.1f} ms"))
        if step.error:
            body.addWidget(QLabel(f"Error: {step.error}"))
            
        if step.details:
            details_str = ", ".join([f"{k}: {v}" for k, v in step.details.items()])
            body.addWidget(QLabel(f"Details: {details_str}"))

        card_layout.addLayout(body)
        return card
