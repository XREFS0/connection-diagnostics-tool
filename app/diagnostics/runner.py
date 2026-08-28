from PySide6.QtCore import QThread, Signal
from app.diagnostics.steps import DiagnosticSteps
from app.models.diagnostic_results import DiagnosticStepResult
from typing import List, Dict, Any

class DiagnosticRunner(QThread):
    step_started = Signal(int, str)
    step_finished = Signal(int, DiagnosticStepResult)
    pipeline_finished = Signal(list)

    def __init__(self, settings_data: Dict[str, Any]):
        super().__init__()
        self.settings = settings_data
        self.results: List[DiagnosticStepResult] = []

    def run(self):
        timeout = self.settings.get("timeout", 5.0)
        ping_count = self.settings.get("ping_count", 4)
        default_host = self.settings.get("default_test_host", "8.8.8.8")
        http_url = self.settings.get("http_test_url", "https://www.google.com")
        tcp_port = int(self.settings.get("tcp_test_port", 443))

        steps = [
            ("Network interface availability", lambda: DiagnosticSteps.check_network_interfaces()),
            ("Local IP configuration", lambda: DiagnosticSteps.check_local_ip()),
            ("Default gateway detection", lambda: DiagnosticSteps.detect_gateway()),
            ("Gateway reachability", lambda: DiagnosticSteps.reach_gateway(
                self.results[2].details.get("Gateway Address", "") if len(self.results) > 2 else "",
                ping_count,
                timeout
            )),
            ("DNS configuration", lambda: DiagnosticSteps.check_dns_config()),
            ("DNS resolution", lambda: DiagnosticSteps.check_dns_resolution(default_host, timeout)),
            ("External host reachability", lambda: DiagnosticSteps.reach_external_host(default_host, ping_count, timeout)),
            ("Internet connectivity", lambda: DiagnosticSteps.check_internet_connectivity(timeout)),
            ("HTTP connectivity", lambda: DiagnosticSteps.check_http(http_url, timeout)),
            ("HTTPS connectivity", lambda: DiagnosticSteps.check_https(http_url, timeout)),
            ("TCP port connectivity", lambda: DiagnosticSteps.check_tcp_port_conn(default_host, tcp_port, timeout)),
            ("Latency analysis", lambda: DiagnosticSteps.analyze_latency_stats(default_host, ping_count, timeout)),
            ("Packet loss analysis", lambda: DiagnosticSteps.analyze_packet_loss_stats(default_host, ping_count, timeout)),
            ("Connection stability analysis", lambda: DiagnosticSteps.analyze_stability_stats(default_host, ping_count, timeout))
        ]

        self.results = []
        for idx, (name, task) in enumerate(steps):
            self.step_started.emit(idx, name)
            try:
                res = task()
            except Exception as e:
                res = DiagnosticStepResult(name=name, status="Failed", error=str(e))
            self.results.append(res)
            self.step_finished.emit(idx, res)

        self.pipeline_finished.emit(self.results)
