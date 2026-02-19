# Checksum calculation

# Implements the Internet checksum algorithm.
# This is the same checksum used by IP, UDP, and TCP headers.
# We also use it in our app-layer packet to detect corruption.


def calculate_checksum(data: bytes) -> int:
    """
    Calculate Internet checksum for the given data.
    
    How it works:
    1. Split data into 16-bit (2-byte) words
    2. Add them all together
    3. If there's overflow beyond 16 bits, wrap it around (add carry)
    4. Flip all the bits (one's complement)
    
    The result is a 16-bit checksum. If the receiver runs this same
    algorithm on the data INCLUDING the checksum, they should get 0
    if nothing was corrupted.
    
    Args:
        data: The bytes to checksum (header, payload, whatever)
        
    Returns:
        16-bit checksum as an integer
    """
    

    if len(data) % 2 != 0:
        data += b'\x00'
    
    checksum = 0
    
   
    for i in range(0, len(data), 2):
        
        word = (data[i] << 8) + data[i + 1]
        checksum += word
        
       
        if checksum > 0xFFFF:
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
    
   
    checksum = checksum ^ 0xFFFF
    
    return checksum


def verify_checksum(data: bytes) -> bool:
    """
    Verify that data (which includes a checksum) is not corrupted.
    
    When you run the checksum algorithm over data that already contains
    a valid checksum, the result should be 0 (or 0xFFFF before the flip).
    
    Args:
        data: The bytes to verify, must include the checksum field
        
    Returns:
        True if checksum is valid (no corruption), False otherwise
    """
    
    
    result = calculate_checksum(data)
    
    return result == 0