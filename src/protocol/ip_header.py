# IP header build/parse

# Builds and parses the IPv4 header.
# Since we're using SOCK_RAW, the OS won't build this for us, we do it manually.
# The IP header is always the first 20 bytes of our raw packet.

import struct
import socket
from protocol.checksum import calculate_checksum


def build_ip_header(src_ip: str, dst_ip: str, payload_length: int) -> bytes:
    """
    Build a 20-byte IPv4 header.
    
    IP Header Structure (20 bytes without options):
    - Bytes 0:      Version (4 bits) + Header Length (4 bits)
    - Bytes 1:      Type of Service (we don't care, set to 0)
    - Bytes 2-3:    Total Length (header + payload)
    - Bytes 4-5:    Identification (for fragmentation, we set to 0)
    - Bytes 6-7:    Flags (3 bits) + Fragment Offset (13 bits)
    - Bytes 8:      TTL (Time to Live, how many hops before packet dies)
    - Bytes 9:      Protocol (17 = UDP)
    - Bytes 10-11:  Header Checksum
    - Bytes 12-15:  Source IP Address
    - Bytes 16-19:  Destination IP Address
    
    Args:
        src_ip: Source IP address as string (e.g., "192.168.1.1")
        dst_ip: Destination IP address as string
        payload_length: Size of everything after IP header (UDP header + data)
        
    Returns:
        20 bytes representing the IP header
    """
    
    
    version_ihl = 0x45
    
    tos = 0
    
    total_length = 20 + payload_length
    
    
    identification = 0
    
    
    flags_fragment = 0x4000
    

    ttl = 64
    

    protocol = 17
    
    
    checksum = 0
    
    
    src_ip_packed = socket.inet_aton(src_ip)
    dst_ip_packed = socket.inet_aton(dst_ip)
    
   
    ip_header = struct.pack(
        '!BBHHHBBH4s4s',
        version_ihl,      # B: version + header length
        tos,              # B: type of service
        total_length,     # H: total length
        identification,   # H: identification
        flags_fragment,   # H: flags + fragment offset
        ttl,              # B: time to live
        protocol,         # B: protocol (UDP = 17)
        checksum,         # H: checksum (0 for now)
        src_ip_packed,    # 4s: source IP
        dst_ip_packed     # 4s: destination IP
    )
    
    checksum = calculate_checksum(ip_header)
    
    
    ip_header = struct.pack(
        '!BBHHHBBH4s4s',
        version_ihl,
        tos,
        total_length,
        identification,
        flags_fragment,
        ttl,
        protocol,
        checksum,         
        src_ip_packed,
        dst_ip_packed
    )
    
    return ip_header


def parse_ip_header(packet: bytes) -> dict:
    """
    Parse a raw packet and extract IP header fields.
    Useful when receiving packets to know where they came from.
    
    Args:
        packet: Raw bytes starting with IP header
        
    Returns:
        Dictionary with IP header fields
    """
    
    ip_header_raw = packet[:20]
    
    fields = struct.unpack('!BBHHHBBH4s4s', ip_header_raw)
    
    version_ihl = fields[0]
    version = version_ihl >> 4          
    header_length = (version_ihl & 0x0F) * 4  
    
    return {
        'version': version,
        'header_length': header_length,
        'tos': fields[1],
        'total_length': fields[2],
        'identification': fields[3],
        'flags_fragment': fields[4],
        'ttl': fields[5],
        'protocol': fields[6],
        'checksum': fields[7],
        'src_ip': socket.inet_ntoa(fields[8]),   
        'dst_ip': socket.inet_ntoa(fields[9])
    }