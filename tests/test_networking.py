from app.networking.ping import PingDiagnostics

def test_ping_parsing_windows():
    sample_stdout = """
Pinging 8.8.8.8 with 32 bytes of data:
Reply from 8.8.8.8: bytes=32 time=12ms TTL=115
Reply from 8.8.8.8: bytes=32 time=14ms TTL=115
Reply from 8.8.8.8: bytes=32 time=15ms TTL=115
Reply from 8.8.8.8: bytes=32 time=11ms TTL=115

Ping statistics for 8.8.8.8:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 11ms, Maximum = 15ms, Average = 13ms
"""
    res = PingDiagnostics.parse_output(sample_stdout, 4, 1.0)
    assert res["reachable"] is True
    assert res["packet_loss"] == 0.0
    assert res["min_latency"] == 11.0
    assert res["max_latency"] == 15.0
    assert res["avg_latency"] == 13.0

def test_ping_parsing_linux():
    sample_stdout = """
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=115 time=10.5 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=115 time=11.2 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=115 time=10.8 ms
64 bytes from 8.8.8.8: icmp_seq=4 ttl=115 time=12.1 ms

--- 8.8.8.8 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 10.512/11.150/12.102/0.612 ms
"""
    res = PingDiagnostics.parse_output(sample_stdout, 4, 1.0)
    assert res["reachable"] is True
    assert res["packet_loss"] == 0.0
    assert res["min_latency"] == 10.5
    assert res["max_latency"] == 12.1
    assert abs(res["avg_latency"] - 11.15) < 0.1
