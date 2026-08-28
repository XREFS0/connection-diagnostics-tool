DARK_STYLE = """
QMainWindow {
    background-color: #0f172a;
}

QFrame {
    border: none;
}

#Sidebar {
    background-color: #1e293b;
    border-right: 1px solid #334155;
    min-width: 220px;
    max-width: 220px;
}

#Header {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
    min-height: 60px;
    max-height: 60px;
}

#MainContent {
    background-color: #0f172a;
}

QLabel {
    color: #f8fafc;
    font-size: 13px;
    font-family: 'Segoe UI', Arial, sans-serif;
}

#AppTitle {
    font-size: 18px;
    font-weight: bold;
    color: #38bdf8;
}

QPushButton {
    background-color: #334155;
    color: #f8fafc;
    border: 1px solid #475569;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #475569;
    border-color: #64748b;
}

QPushButton:pressed {
    background-color: #1e293b;
}

#SidebarButton {
    text-align: left;
    padding: 12px 20px;
    border: none;
    border-radius: 0px;
    background-color: transparent;
    font-size: 14px;
}

#SidebarButton:hover {
    background-color: #334155;
}

#SidebarButton[active="true"] {
    background-color: #38bdf8;
    color: #0f172a;
    font-weight: bold;
}

#Card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
}

#CardTitle {
    font-size: 12px;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
}

#CardValue {
    font-size: 20px;
    color: #f8fafc;
    font-weight: bold;
}

#RunDiagnosticsBtn {
    background-color: #0284c7;
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
    border: none;
    border-radius: 4px;
    padding: 10px 24px;
}

#RunDiagnosticsBtn:hover {
    background-color: #0369a1;
}

#RunDiagnosticsBtn:disabled {
    background-color: #334155;
    color: #64748b;
}

QProgressBar {
    border: 1px solid #334155;
    border-radius: 4px;
    text-align: center;
    background-color: #1e293b;
    color: #ffffff;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #38bdf8;
    width: 10px;
}

QTableWidget {
    background-color: #1e293b;
    gridline-color: #334155;
    color: #f8fafc;
    border: 1px solid #334155;
    font-size: 13px;
}

QHeaderView::section {
    background-color: #334155;
    color: #f8fafc;
    padding: 8px;
    border: 1px solid #1e293b;
    font-weight: bold;
}

QTableWidget::item {
    padding: 8px;
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
}

QTableWidget::item:selected {
    background-color: #0284c7;
    color: #ffffff;
}

QLineEdit, QComboBox, QSpinBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    color: #f8fafc;
    padding: 6px;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border-color: #38bdf8;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

QStackedWidget {
    background-color: #0f172a;
}

QTableWidget {
    background-color: #1e293b;
    gridline-color: #334155;
    color: #f8fafc;
    border: 1px solid #334155;
    font-size: 13px;
}

QTableWidget QHeaderView {
    background-color: #1e293b;
}

QTableWidget QTableCornerButton::section {
    background-color: #1e293b;
    border: none;
}

QTableView {
    background-color: #1e293b;
}

QScrollBar:vertical {
    border: none;
    background-color: #0f172a;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
"""
