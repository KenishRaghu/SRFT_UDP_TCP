import pytest

import struct
from protocol.checksum import calculate_checksum, verify_checksum


class TestCalculateChecksum:
    """Unit tests for the Internet checksum calculation."""

    @pytest.mark.parametrize(
        "data,expected_checksum",
        [
            # Some corner cases
            (b"", 0xFFFF),
            (b"\x00\x00", 0xFFFF),
            (b"\xff\xff", 0),
            # Odd-length data
            (b"\xab\xcd\xef", 0x6531),
            # Example from Module 6
            (
                bytes.fromhex("4500 001C C001 0000 0411 0000 0A0C 0E05 0C06 0709"),
                0xCBB0,
            ),
        ],
    )
    def test_data(self, data, expected_checksum):
        assert calculate_checksum(data) == expected_checksum


class TestVerifyChecksum:
    """Unit tests for checksum verification."""

    def test_data_with_checksum(self):
        data = b"Hello!"
        # Append checksum as big-endian 16-bit value
        data_with_checksum = data + struct.pack("!H", calculate_checksum(data))
        assert verify_checksum(data_with_checksum)

    def test_corruption_detected(self):
        data = b"Hello!"
        data_with_checksum = bytearray(
            data + struct.pack("!H", calculate_checksum(data))
        )
        data_with_checksum[0] ^= 1  # Flip a bit
        assert verify_checksum(bytes(data_with_checksum)) is False
