from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
import socket
import platform
import uuid
from app.networking.stats import NetworkStats

class NetworkInfoView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("System Network Interfaces")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Property", "Value", "Interface Type", "MAC Address"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.refresh()

    def refresh(self):
        self.table.setRowCount(0)
        
        hostname = socket.gethostname()
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])
        gateway = NetworkStats.get_default_gateway()
        dns = ", ".join(NetworkStats.get_dns_servers())

        properties = [
            ("Hostname", hostname, "System", "N/A"),
            ("Operating System", platform.system() + " " + platform.release(), "System", "N/A"),
            ("Default Gateway", gateway, "Gateway", "N/A"),
            ("DNS Servers", dns, "DNS", "N/A")
        ]

        try:
            local_ips = socket.gethostbyname_ex(hostname)[2]
            for i, ip in enumerate(local_ips):
                properties.append((f"IPv4 Address ({i})", ip, "Interface adapter", mac))
        except Exception:
            pass

        self.table.setRowCount(len(properties))
        for row, (prop, val, itype, imac) in enumerate(properties):
            self.table.setItem(row, 0, QTableWidgetItem(prop))
            self.table.setItem(row, 1, QTableWidgetItem(val))
            self.table.setItem(row, 2, QTableWidgetItem(itype))
            self.table.setItem(row, 3, QTableWidgetItem(imac))
