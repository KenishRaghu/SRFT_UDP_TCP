# UDP header build/parse

# Builds and parses the UDP header.
# UDP header comes right after the IP header and is much simpler, only 8 bytes.
# UDP itself doesn't provide reliability, which is why we add our own layer on top.

import struct


def build_udp_header(src_port: int, dst_port: int, payload_length: int) -> bytes:
    """
    Build an 8-byte UDP header.
    
    UDP Header Structure (8 bytes):
    - Bytes 0-1:    Source Port
    - Bytes 2-3:    Destination Port
    - Bytes 4-5:    Length (UDP header + payload)
    - Bytes 6-7:    Checksum (we set to 0, optional in IPv4)
    
    Args:
        src_port: Source port number (0-65535)
        dst_port: Destination port number (0-65535)
        payload_length: Size of the data after UDP header
        
    Returns:
        8 bytes representing the UDP header
    """
    
    
    udp_length = 8 + payload_length
    
    
    checksum = 0
    
    
    udp_header = struct.pack(
        '!HHHH',
        src_port,     
        dst_port,     
        udp_length,   
        checksum      
    )
    
    return udp_header


def parse_udp_header(data: bytes) -> dict:
    """
    Parse UDP header from received data.
    
    When we receive a raw packet, the UDP header starts after the IP header.
    This function extracts the port numbers and length.
    
    Args:
        data: Bytes starting with UDP header (not the full packet — 
              caller should skip the IP header first)
        
    Returns:
        Dictionary with UDP header fields
    """
    
    udp_header_raw = data[:8]
    
    fields = struct.unpack('!HHHH', udp_header_raw)
    
    return {
        'src_port': fields[0],
        'dst_port': fields[1],
        'length': fields[2],       
        'checksum': fields[3]
    }