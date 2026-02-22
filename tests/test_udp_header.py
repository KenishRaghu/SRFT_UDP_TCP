import pytest

import struct
from protocol.udp_header import build_udp_header, parse_udp_header

pytestmark = pytest.mark.parametrize(
    "src_port,dst_port,payload_len",
    [
        (0, 0, 0),
        (12345, 54321, 100),
        (65535, 65535, 1024),
    ],
)


class TestBuildUdpHeader:
    """Tests for build_udp_header."""

    def test_header_length_is_8(self, src_port, dst_port, payload_len):
        header = build_udp_header(src_port, dst_port, payload_len)
        assert len(header) == 8  # UDP header is always 8 bytes

    def test_checksum_is_zero(self, src_port, dst_port, payload_len):
        header = build_udp_header(src_port, dst_port, payload_len)
        checksum = struct.unpack("!H", header[6:8])[0]
        assert checksum == 0  # Implementation hardcodes checksum to 0

    def test_udp_length(self, src_port, dst_port, payload_len):
        header = build_udp_header(src_port, dst_port, payload_len)
        udp_length = struct.unpack("!H", header[4:6])[0]
        assert udp_length == 8 + payload_len  # Length = 8 (header) + payload length


class TestParseUdpHeader:
    """Tests for parse_udp_header."""

    def test_all_fields_present(self, src_port, dst_port, payload_len):
        header = build_udp_header(src_port, dst_port, payload_len)
        parsed = parse_udp_header(header)
        assert len(parsed) == 4
        assert set(parsed.keys()) == {"src_port", "dst_port", "length", "checksum"}

    def test_round_trip_ports(self, src_port, dst_port, payload_len):
        header = build_udp_header(src_port, dst_port, payload_len)
        parsed = parse_udp_header(header)
        assert parsed["src_port"] == src_port
        assert parsed["dst_port"] == dst_port

    def test_round_trip_length(self, src_port, dst_port, payload_len):
        header = build_udp_header(src_port, dst_port, payload_len)
        parsed = parse_udp_header(header)
        assert parsed["length"] == 8 + payload_len

    def test_round_trip_checksum(self, src_port, dst_port, payload_len):
        header = build_udp_header(src_port, dst_port, payload_len)
        parsed = parse_udp_header(header)
        assert parsed["checksum"] == 0
