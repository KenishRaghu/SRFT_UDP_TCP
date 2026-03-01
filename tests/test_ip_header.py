import pytest

import struct
from protocol.ip_header import build_ip_header, parse_ip_header
from protocol.checksum import calculate_checksum


class TestBuildIpHeader:
    """Unit tests for build_ip_header."""

    def test_header_constants(self):
        header = build_ip_header("10.0.0.1", "10.0.0.2", 100)
        assert len(header) == 20  # IP header without options is 20 bytes
        version = header[0] >> 4
        assert version == 4  # IPv4
        ihl = header[0] & 0x0F
        assert ihl == 5  # 5 * 4 = 20 bytes
        protocol = header[9]
        assert protocol == 17  # UDP

    def test_total_length(self):
        payload_len = 256
        header = build_ip_header("10.0.0.1", "10.0.0.2", payload_len)
        total_length = struct.unpack("!H", header[2:4])[0]
        assert total_length == 20 + payload_len

    def test_checksum_valid(self):
        header = build_ip_header("10.0.0.1", "10.0.0.2", 100)
        # Running checksum over a correct header yields 0
        assert calculate_checksum(header) == 0


@pytest.mark.parametrize(
    "src,dst,payload_len",
    [
        ("127.0.0.1", "127.0.0.1", 0),
        ("192.168.0.1", "10.0.0.1", 128),
        ("255.255.255.255", "0.0.0.0", 256),
    ],
)
class TestParseIpHeader:
    """Unit tests for parse_ip_header."""

    def test_round_trip(self, src, dst, payload_len):
        header = build_ip_header(src, dst, payload_length=payload_len)
        parsed = parse_ip_header(header)
        assert parsed["version"] == 4
        assert parsed["header_length"] == 20
        assert parsed["total_length"] == 20 + payload_len
        assert parsed["protocol"] == 17
        assert parsed["src_ip"] == src
        assert parsed["dst_ip"] == dst
