from app.models.diagnostic_results import DiagnosticStepResult
from app.networking.stats import NetworkStats
from app.networking.ping import PingDiagnostics
import time
import socket

class DiagnosticSteps:
    @staticmethod
    def check_network_interfaces() -> DiagnosticStepResult:
        start = time.time()
        interfaces = NetworkStats.get_interfaces()
        duration = (time.time() - start) * 1000
        active_count = len([i for i in interfaces if i.get("status") == "Active"])
        
        if active_count > 0:
            return DiagnosticStepResult(
                name="Network interface availability",
                status="Passed",
                duration_ms=duration,
                result=f"{active_count} active interface(s) detected",
                details={"Interfaces": [i["name"] for i in interfaces]}
            )
        return DiagnosticStepResult(
            name="Network interface availability",
            status="Failed",
            duration_ms=duration,
            result="No active interfaces found",
            error="Ensure network card is enabled and connected"
        )

    @staticmethod
    def check_local_ip() -> DiagnosticStepResult:
        start = time.time()
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
            duration = (time.time() - start) * 1000
            return DiagnosticStepResult(
                name="Local IP configuration",
                status="Passed",
                duration_ms=duration,
                result=f"Local IP address: {local_ip}",
                details={"Hostname": hostname, "IPv4": local_ip}
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            return DiagnosticStepResult(
                name="Local IP configuration",
                status="Failed",
                duration_ms=duration,
                result="Failed to retrieve local IP configuration",
                error=str(e)
            )

    @staticmethod
    def detect_gateway() -> DiagnosticStepResult:
        start = time.time()
        gateway = NetworkStats.get_default_gateway()
        duration = (time.time() - start) * 1000
        if gateway and gateway != "Unknown":
            return DiagnosticStepResult(
                name="Default gateway detection",
                status="Passed",
                duration_ms=duration,
                result=f"Gateway: {gateway}",
                details={"Gateway Address": gateway}
            )
        return DiagnosticStepResult(
            name="Default gateway detection",
            status="Warning",
            duration_ms=duration,
            result="No default gateway detected",
            error="Could not parse gateway address from system routing table"
        )

    @staticmethod
    def reach_gateway(gateway_ip: str, count: int, timeout: float) -> DiagnosticStepResult:
        start = time.time()
        if not gateway_ip or gateway_ip == "Unknown":
            return DiagnosticStepResult(
                name="Gateway reachability",
                status="Failed",
                duration_ms=0.0,
                result="Gateway address is unknown",
                error="Cannot perform reachability test without a gateway IP"
            )
        
        res = PingDiagnostics.ping(gateway_ip, count=count, timeout_sec=timeout)
        duration = (time.time() - start) * 1000
        if res["reachable"]:
            return DiagnosticStepResult(
                name="Gateway reachability",
                status="Passed" if res["packet_loss"] < 25 else "Warning",
                duration_ms=duration,
                result=f"Gateway responded. Latency: {res['avg_latency']:.1f}ms",
                details={
                    "Gateway": gateway_ip,
                    "Avg Latency": f"{res['avg_latency']:.2f} ms",
                    "Packet Loss": f"{res['packet_loss']:.1f}%",
                    "Jitter": f"{res['jitter']:.2f} ms"
                }
            )
        return DiagnosticStepResult(
            name="Gateway reachability",
            status="Failed",
            duration_ms=duration,
            result="Gateway is unreachable",
            error=res.get("error", "No response from gateway")
        )

    @staticmethod
    def check_dns_config() -> DiagnosticStepResult:
        start = time.time()
        servers = NetworkStats.get_dns_servers()
        duration = (time.time() - start) * 1000
        if servers:
            return DiagnosticStepResult(
                name="DNS configuration",
                status="Passed",
                duration_ms=duration,
                result=f"DNS Server: {servers[0]}",
                details={"DNS Servers": servers}
            )
        return DiagnosticStepResult(
            name="DNS configuration",
            status="Warning",
            duration_ms=duration,
            result="No DNS configuration found",
            error="Local routing/DNS lookup servers are empty"
        )

    @staticmethod
    def check_dns_resolution(host: str, timeout: float) -> DiagnosticStepResult:
        start = time.time()
        res = NetworkStats.resolve_dns(host, timeout=timeout)
        duration = (time.time() - start) * 1000
        if res["success"]:
            return DiagnosticStepResult(
                name="DNS resolution",
                status="Passed",
                duration_ms=duration,
                result=f"Resolved {host} to {res['ips'][0]}",
                details={"Host": host, "IPs": res["ips"], "Resolution Time": f"{res['duration_ms']:.1f} ms"}
            )
        return DiagnosticStepResult(
            name="DNS resolution",
            status="Failed",
            duration_ms=duration,
            result=f"Failed to resolve {host}",
            error=res.get("error", "Unknown DNS resolution issue")
        )

    @staticmethod
    def reach_external_host(host: str, count: int, timeout: float) -> DiagnosticStepResult:
        start = time.time()
        res = PingDiagnostics.ping(host, count=count, timeout_sec=timeout)
        duration = (time.time() - start) * 1000
        if res["reachable"]:
            return DiagnosticStepResult(
                name="External host reachability",
                status="Passed" if res["packet_loss"] < 25 else "Warning",
                duration_ms=duration,
                result=f"Host responded. Latency: {res['avg_latency']:.1f}ms",
                details={
                    "Host": host,
                    "Avg Latency": f"{res['avg_latency']:.2f} ms",
                    "Packet Loss": f"{res['packet_loss']:.1f}%",
                    "Jitter": f"{res['jitter']:.2f} ms"
                }
            )
        return DiagnosticStepResult(
            name="External host reachability",
            status="Failed",
            duration_ms=duration,
            result=f"External host {host} is unreachable",
            error=res.get("error", "Failed to contact host")
        )

    @staticmethod
    def check_internet_connectivity(timeout: float) -> DiagnosticStepResult:
        start = time.time()
        res = NetworkStats.resolve_dns("google.com", timeout=timeout)
        duration = (time.time() - start) * 1000
        if res["success"]:
            pub_ip = NetworkStats.get_public_ip(timeout=timeout)
            return DiagnosticStepResult(
                name="Internet connectivity",
                status="Passed",
                duration_ms=duration,
                result="Internet connectivity verified via public DNS lookup",
                details={"Method": "DNS Query (google.com)", "Public IP": pub_ip}
            )
        return DiagnosticStepResult(
            name="Internet connectivity",
            status="Failed",
            duration_ms=duration,
            result="Offline / Local network only",
            error="Could not resolve public DNS name",
            details={"Public IP": "Offline / Private"}
        )

    @staticmethod
    def check_http(url: str, timeout: float) -> DiagnosticStepResult:
        start = time.time()
        http_url = url.replace("https://", "http://") if url.startswith("https://") else url
        res = NetworkStats.check_http_endpoint(http_url, timeout=timeout)
        duration = (time.time() - start) * 1000
        if res["success"]:
            return DiagnosticStepResult(
                name="HTTP connectivity",
                status="Passed" if res["status_code"] < 400 else "Warning",
                duration_ms=duration,
                result=f"Status Code: {res['status_code']}",
                details={"URL": http_url, "Response Time": f"{res['duration_ms']:.1f} ms"}
            )
        return DiagnosticStepResult(
            name="HTTP connectivity",
            status="Failed",
            duration_ms=duration,
            result="HTTP request failed",
            error=res.get("error", "Unknown transport error")
        )

    @staticmethod
    def check_https(url: str, timeout: float) -> DiagnosticStepResult:
        start = time.time()
        https_url = url.replace("http://", "https://") if url.startswith("http://") else url
        if not https_url.startswith("https://"):
            https_url = "https://" + https_url
        res = NetworkStats.check_http_endpoint(https_url, timeout=timeout)
        duration = (time.time() - start) * 1000
        if res["success"]:
            return DiagnosticStepResult(
                name="HTTPS connectivity",
                status="Passed" if res["status_code"] < 400 else "Warning",
                duration_ms=duration,
                result=f"Status Code: {res['status_code']} (TLS Validated)",
                details={
                    "URL": https_url,
                    "TLS Version": res["tls_version"],
                    "Cert Status": res["cert_info"],
                    "Response Time": f"{res['duration_ms']:.1f} ms"
                }
            )
        return DiagnosticStepResult(
            name="HTTPS connectivity",
            status="Failed",
            duration_ms=duration,
            result="HTTPS validation failed",
            error=res.get("error", "SSL or handshake error")
        )

    @staticmethod
    def check_tcp_port_conn(host: str, port: int, timeout: float) -> DiagnosticStepResult:
        start = time.time()
        res = NetworkStats.check_tcp_port(host, port, timeout=timeout)
        duration = (time.time() - start) * 1000
        if res["success"]:
            return DiagnosticStepResult(
                name="TCP port connectivity",
                status="Passed",
                duration_ms=duration,
                result=f"Successfully connected to {host}:{port}",
                details={"Target": host, "Port": port, "Connection Time": f"{res['duration_ms']:.1f} ms"}
            )
        return DiagnosticStepResult(
            name="TCP port connectivity",
            status="Failed",
            duration_ms=duration,
            result=f"Failed to connect to port {port}",
            error=res.get("error", "Connection refused or timed out")
        )

    @staticmethod
    def analyze_latency_stats(host: str, count: int, timeout: float) -> DiagnosticStepResult:
        start = time.time()
        res = PingDiagnostics.ping(host, count=count, timeout_sec=timeout)
        duration = (time.time() - start) * 1000
        if res["reachable"]:
            return DiagnosticStepResult(
                name="Latency analysis",
                status="Passed" if res["avg_latency"] < 100.0 else "Warning",
                duration_ms=duration,
                result=f"Avg: {res['avg_latency']:.1f}ms, Jitter: {res['jitter']:.1f}ms",
                details={
                    "Minimum Latency": f"{res['min_latency']:.2f} ms",
                    "Maximum Latency": f"{res['max_latency']:.2f} ms",
                    "Average Latency": f"{res['avg_latency']:.2f} ms",
                    "Jitter": f"{res['jitter']:.2f} ms"
                }
            )
        return DiagnosticStepResult(
            name="Latency analysis",
            status="Failed",
            duration_ms=duration,
            result="Cannot analyze latency (host is unreachable)",
            error="All latency test packets timed out"
        )

    @staticmethod
    def analyze_packet_loss_stats(host: str, count: int, timeout: float) -> DiagnosticStepResult:
        start = time.time()
        res = PingDiagnostics.ping(host, count=count, timeout_sec=timeout)
        duration = (time.time() - start) * 1000
        loss = res["packet_loss"]
        status = "Passed"
        if loss > 0.0:
            status = "Warning" if loss <= 25.0 else "Failed"
            
        return DiagnosticStepResult(
            name="Packet loss analysis",
            status=status,
            duration_ms=duration,
            result=f"Packet loss: {loss:.1f}% ({res['packets_received']}/{res['packets_sent']} received)",
            details={
                "Packets Sent": res["packets_sent"],
                "Packets Received": res["packets_received"],
                "Packet Loss Ratio": f"{loss:.1f}%"
            }
        )

    @staticmethod
    def analyze_stability_stats(host: str, count: int, timeout: float) -> DiagnosticStepResult:
        start = time.time()
        res = PingDiagnostics.ping(host, count=count, timeout_sec=timeout)
        duration = (time.time() - start) * 1000
        
        jitter = res["jitter"]
        loss = res["packet_loss"]
        
        if loss > 50.0:
            status = "Failed"
            desc = "Highly unstable or disconnected"
        elif loss > 0.0 or jitter > 30.0:
            status = "Warning"
            desc = "Connection stability issues detected"
        else:
            status = "Passed"
            desc = "Connection is stable"
            
        return DiagnosticStepResult(
            name="Connection stability analysis",
            status=status,
            duration_ms=duration,
            result=desc,
            details={
                "Jitter": f"{jitter:.2f} ms",
                "Packet Loss": f"{loss:.1f}%"
            }
        )
