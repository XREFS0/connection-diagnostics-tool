import socket
import ssl
import time
import urllib.request
import urllib.error
import platform
import subprocess
import re
from typing import Dict, Any, List, Optional

class NetworkStats:
    @staticmethod
    def resolve_dns(host: str, timeout: float = 5.0) -> Dict[str, Any]:
        start = time.time()
        try:
            addrinfo = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
            duration = (time.time() - start) * 1000
            ips = list(set([info[4][0] for info in addrinfo]))
            return {
                "success": True,
                "duration_ms": duration,
                "ips": ips,
                "error": ""
            }
        except Exception as e:
            return {
                "success": False,
                "duration_ms": (time.time() - start) * 1000,
                "ips": [],
                "error": str(e)
            }

    @staticmethod
    def check_tcp_port(host: str, port: int, timeout: float = 5.0) -> Dict[str, Any]:
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            duration = (time.time() - start) * 1000
            s.close()
            return {
                "success": True,
                "duration_ms": duration,
                "error": ""
            }
        except Exception as e:
            return {
                "success": False,
                "duration_ms": (time.time() - start) * 1000,
                "error": str(e)
            }

    @staticmethod
    def check_http_endpoint(url: str, timeout: float = 5.0) -> Dict[str, Any]:
        start = time.time()
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Connection-Diagnostics-Tool/1.0'}
            )
            context = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
                duration = (time.time() - start) * 1000
                return {
                    "success": True,
                    "status_code": response.status,
                    "duration_ms": duration,
                    "tls_version": context.protocol.name if hasattr(context, "protocol") else "Unknown",
                    "cert_info": "Certificate successfully validated",
                    "error": ""
                }
        except urllib.error.HTTPError as e:
            duration = (time.time() - start) * 1000
            return {
                "success": True,
                "status_code": e.code,
                "duration_ms": duration,
                "tls_version": "Unknown",
                "cert_info": "Unknown",
                "error": f"HTTP Error {e.code}"
            }
        except urllib.error.URLError as e:
            duration = (time.time() - start) * 1000
            err_msg = str(e.reason)
            cert_info = "SSL verification failed" if "CERTIFICATE_VERIFY_FAILED" in err_msg else "Unknown"
            return {
                "success": False,
                "status_code": 0,
                "duration_ms": duration,
                "tls_version": "Failed",
                "cert_info": cert_info,
                "error": err_msg
            }
        except Exception as e:
            duration = (time.time() - start) * 1000
            return {
                "success": False,
                "status_code": 0,
                "duration_ms": duration,
                "tls_version": "Failed",
                "cert_info": "Unknown",
                "error": str(e)
            }

    @staticmethod
    def get_public_ip(timeout: float = 5.0) -> str:
        providers = [
            "https://api.ipify.org",
            "https://icanhazip.com",
            "https://ifconfig.me/ip"
        ]
        for url in providers:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    ip = response.read().decode('utf-8').strip()
                    if ip:
                        return ip
            except Exception:
                continue
        return "Unknown / Offline"

    @staticmethod
    def get_dns_servers() -> List[str]:
        servers: List[str] = []
        try:
            if platform.system().lower() == "windows":
                output = subprocess.check_output(
                    ["nslookup", "localhost"], 
                    text=True, 
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                match = re.search(r"Server:\s+(.+)", output)
                if match:
                    srv = match.group(1).strip()
                    if srv and srv not in ["UnKnown", "localhost", "127.0.0.1"]:
                        servers.append(srv)
                
                ipconfig_out = subprocess.check_output(
                    ["ipconfig", "/all"],
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                dns_matches = re.findall(r"DNS Servers[\s\.:]+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", ipconfig_out)
                for dns in dns_matches:
                    if dns not in servers:
                        servers.append(dns)
            else:
                with open("/etc/resolv.conf", "r") as f:
                    for line in f:
                        if line.startswith("nameserver"):
                            servers.append(line.split()[1])
        except Exception:
            pass
        return servers if servers else ["8.8.8.8", "8.8.4.4"]

    @staticmethod
    def get_default_gateway() -> str:
        try:
            if platform.system().lower() == "windows":
                output = subprocess.check_output(
                    ["route", "print", "0.0.0.0"], 
                    text=True, 
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                for line in output.splitlines():
                    parts = line.split()
                    if len(parts) >= 4 and parts[0] == "0.0.0.0" and parts[1] == "0.0.0.0":
                        return parts[2]
            else:
                output = subprocess.check_output("ip route show | grep default", shell=True, text=True)
                parts = output.split()
                if len(parts) >= 3 and parts[2]:
                    return parts[2]
        except Exception:
            pass
        return "Unknown"

    @staticmethod
    def get_interfaces() -> List[Dict[str, Any]]:
        interfaces: List[Dict[str, Any]] = []
        try:
            hostname = socket.gethostname()
            ips = socket.gethostbyname_ex(hostname)[2]
            for i, ip in enumerate(ips):
                interfaces.append({
                    "name": f"Interface {i}",
                    "status": "Active",
                    "ipv4": ip,
                    "ipv6": "Not detected",
                    "mac": "Unknown",
                    "type": "Ethernet/Wi-Fi"
                })
        except Exception:
            pass
        if not interfaces:
            interfaces.append({
                "name": "Loopback",
                "status": "Active",
                "ipv4": "127.0.0.1",
                "ipv6": "::1",
                "mac": "00:00:00:00:00:00",
                "type": "Loopback"
            })
        return interfaces
