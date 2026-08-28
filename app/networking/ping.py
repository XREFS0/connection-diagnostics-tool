import subprocess
import platform
import re
import time
from typing import Dict, Any

class PingDiagnostics:
    @staticmethod
    def ping(host: str, count: int = 4, timeout_sec: float = 5.0) -> Dict[str, Any]:
        system_name = platform.system().lower()
        timeout_ms = int(timeout_sec * 1000)
        
        if system_name == "windows":
            cmd = ["ping", "-n", str(count), "-w", str(timeout_ms), host]
        else:
            cmd = ["ping", "-c", str(count), "-W", str(timeout_sec), host]

        start_time = time.time()
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if system_name == "windows" else 0
            )
            duration = time.time() - start_time
            stdout = res.stdout
            
            if res.returncode != 0 or not stdout:
                return {
                    "reachable": False,
                    "packets_sent": count,
                    "packets_received": 0,
                    "packet_loss": 100.0,
                    "min_latency": 0.0,
                    "max_latency": 0.0,
                    "avg_latency": 0.0,
                    "jitter": 0.0,
                    "error": res.stderr.strip() or "Ping failed with non-zero exit code"
                }

            return PingDiagnostics.parse_output(stdout, count, duration)
        except Exception as e:
            return {
                "reachable": False,
                "packets_sent": count,
                "packets_received": 0,
                "packet_loss": 100.0,
                "min_latency": 0.0,
                "max_latency": 0.0,
                "avg_latency": 0.0,
                "jitter": 0.0,
                "error": str(e)
            }

    @staticmethod
    def parse_output(stdout: str, count: int, duration: float) -> Dict[str, Any]:
        packets_sent = count
        packets_received = 0
        packet_loss = 100.0
        min_lat = 0.0
        max_lat = 0.0
        avg_lat = 0.0
        latencies = []

        if "packets transmitted" in stdout.lower() or "rtt min/avg/max/mdev" in stdout.lower():
            rec_match = re.search(r"(\d+) packets transmitted, (\d+) received", stdout)
            if rec_match:
                packets_sent = int(rec_match.group(1))
                packets_received = int(rec_match.group(2))
                packet_loss = ((packets_sent - packets_received) / packets_sent) * 100.0 if packets_sent else 100.0

            time_matches = re.findall(r"time=(\d+\.?\d*) ms", stdout)
            if time_matches:
                latencies = [float(t) for t in time_matches]
            else:
                rtt_match = re.search(r"rtt min/avg/max/mdev = (\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*) ms", stdout)
                if rtt_match:
                    min_lat = float(rtt_match.group(1))
                    avg_lat = float(rtt_match.group(2))
                    max_lat = float(rtt_match.group(3))
                    latencies = [avg_lat] * packets_received
        else:
            sent_match = re.search(r"Sent = (\d+)", stdout)
            rec_match = re.search(r"Received = (\d+)", stdout)
            loss_match = re.search(r"Lost = \d+ \((\d+)% loss\)", stdout)
            
            if sent_match:
                packets_sent = int(sent_match.group(1))
            if rec_match:
                packets_received = int(rec_match.group(1))
            if loss_match:
                packet_loss = float(loss_match.group(1))
            else:
                packet_loss = ((packets_sent - packets_received) / packets_sent) * 100.0 if packets_sent else 100.0

            time_matches = re.findall(r"reply from.*time[=<](\d+)ms", stdout, re.IGNORECASE)
            if time_matches:
                latencies = [float(t) for t in time_matches]
            else:
                min_match = re.search(r"Minimum = (\d+)ms", stdout)
                max_match = re.search(r"Maximum = (\d+)ms", stdout)
                avg_match = re.search(r"Average = (\d+)ms", stdout)
                if min_match and max_match and avg_match:
                    min_lat = float(min_match.group(1))
                    max_lat = float(max_match.group(1))
                    avg_lat = float(avg_match.group(1))
                    latencies = [avg_lat] * packets_received

        if latencies:
            min_lat = min(latencies)
            max_lat = max(latencies)
            avg_lat = sum(latencies) / len(latencies)
            
            jitter = 0.0
            if len(latencies) > 1:
                diffs = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
                jitter = sum(diffs) / len(diffs)
        else:
            jitter = 0.0

        return {
            "reachable": packets_received > 0,
            "packets_sent": packets_sent,
            "packets_received": packets_received,
            "packet_loss": packet_loss,
            "min_latency": min_lat,
            "max_latency": max_lat,
            "avg_latency": avg_lat,
            "jitter": jitter,
            "error": "" if packets_received > 0 else "All packets lost"
        }
