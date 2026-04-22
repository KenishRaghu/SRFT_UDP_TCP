# SRFT — Secure Reliable File Transfer

A custom UDP-based file transfer protocol built from scratch using raw sockets (SOCK_RAW). Implements reliable data transfer with Go-Back-N sliding window protocol and comprehensive security features including end-to-end encryption, authentication, and replay protection.

## Features

**Phase 1 — Reliable File Transfer:**

- Raw socket implementation with custom IP/UDP header construction
- Go-Back-N (GBN) sliding window protocol with configurable window size (128 packets)
- Timeout-based retransmission and fast retransmit on 3 duplicate ACKs
- Cumulative ACK with delayed ACK optimization (ACK every 16 packets or 10ms)
- Out-of-order packet handling and duplicate detection
- Internet checksum for packet integrity verification
- Transfer statistics and performance reporting

**Phase 2 — Secure File Transfer:**

- HMAC-based secure handshake (ClientHello/ServerHello) with pre-shared key (PSK)
- End-to-end encryption using AES-GCM AEAD (Authenticated Encryption with Associated Data)
- HKDF-SHA256 key derivation for session keys
- Sliding-window bitmap-based replay protection
- SHA-256 file integrity verification
- Built-in attack simulator for security testing (tamper, replay, inject modes)
- Comprehensive security metrics reporting (AEAD failures, replay drops)
- Optional insecure mode (`--insecure`) for testing without encryption

**Testing:**

- 108 unit and integration tests covering all protocol and security components
- Phase 1 and Phase 2 test reports with performance benchmarks
- Tested with files up to 1GB and various packet loss scenarios (0%-4%)

---

## How to run

### Requirements

- Python 3.12+
- Administrator/root privileges (required for raw sockets)
- Both machines must have ports 12345 and 12346 open for UDP traffic

### Starting the server

Run on the server machine with administrator/root privileges:

```bash
# Basic usage:
# python SRFT_UDPServer.py <server_ip> [files_directory] [--insecure] [--attack {tamper,replay,inject}]

# Windows (run PowerShell as Administrator):
cd src
python SRFT_UDPServer.py 127.0.0.1 ./test_files

# Linux/AWS EC2:
cd src
sudo python SRFT_UDPServer.py 192.168.1.10

# Run without encryption (Phase 1 mode):
python SRFT_UDPServer.py 127.0.0.1 ./test_files --insecure

# Run with simulated security attacks:
python SRFT_UDPServer.py 127.0.0.1 ./test_files --attack tamper
```

### Starting the client

Before running, set the server IP address and the client IP address in `config.py`:

```python
SERVER_IP = "127.0.0.1"  # use 127.0.0.1 for local testing
                         # replace with server EC2 private IP for AWS testing
CLIENT_IP = "127.0.0.1"  # use 127.0.0.1 for local testing
                         # replace with client EC2 private IP for AWS testing
```

Run on the client machine with administrator/root privileges:

```bash
# Basic usage:
# python SRFT_UDPClient.py <filename> [--insecure]

# Windows (run PowerShell as Administrator):
cd src
python SRFT_UDPClient.py test.txt

# Linux/AWS EC2:
cd src
sudo python SRFT_UDPClient.py test.txt

# Run without encryption (Phase 1 mode):
python SRFT_UDPClient.py test.txt --insecure
```

The requested file must exist in the server's `tests/test_files/` folder.
The received file will be saved in the `output/` folder.

### AWS testing with packet loss

```bash
# Apply 3% packet loss on the client EC2 instance:
sudo tc qdisc add dev eth0 root netem loss 3%

# Remove packet loss when done:
sudo tc qdisc del dev eth0 root
```

### Verifying file integrity

```bash
# On Linux, compare MD5 hashes on both machines:
md5sum tests/test_files/   # on server
md5sum output/             # on client
# Both hashes must match for a successful transfer.
```

### Running tests

```bash
# Run all unit tests (108 tests):
cd /path/to/SRFT_UDP_TCP
pytest tests/ -v

# Run specific test modules:
pytest tests/test_crypto.py -v              # Cryptography tests
pytest tests/test_handshake.py -v           # Handshake tests
pytest tests/test_secure_transfer.py -v     # End-to-end security tests
pytest tests/test_replay.py -v              # Replay protection tests

# Run with coverage:
pytest tests/ --cov=src --cov-report=html
```

## Performance Summary

All tests were conducted on AWS EC2 instances (free tier) with packet loss simulated using `tc netem`.

### Phase 1 — Reliable File Transfer (--insecure mode)

| File size | No packet loss | 2% packet loss | 3% packet loss | 4% packet loss |
| --------- | -------------- | -------------- | -------------- | -------------- |
| 10 MB     | 00:00:01       | 00:00:02       | TBD            | 00:00:02       |
| 100 MB    | 00:00:12       | 00:00:19       | TBD            | 00:01:08       |
| 500 MB    | 00:01:04       | 00:02:30       | TBD            | 00:04:51       |
| 800 MB    | 00:02:08       | 00:04:35       | TBD            | 00:06:48       |
| 1 GB      | 00:02:35       | 00:04:43       | TBD            | 00:07:46       |

**Note:** 3% packet loss tests are pending completion. All file transfers completed successfully with matching md5sum checksums.

### Phase 2 — Secure File Transfer (with encryption, 0% packet loss)

| File size | Time     | Packets sent | Retransmissions | ACKs received | AEAD failures | Replay drops | SHA-256 match |
| --------- | -------- | ------------ | --------------- | ------------- | ------------- | ------------ | ------------- |
| 10 MB     | 00:00:01 | 1,281        | 0               | 81            | 0             | 0            | Yes           |
| 100 MB    | 00:00:14 | 12,801       | 0               | 801           | 0             | 0            | Yes           |
| 500 MB    | 00:01:19 | 64,001       | 279             | 4,254         | 0             | 0            | Yes           |
| 800 MB    | 00:02:03 | 102,401      | 224             | 6,608         | 0             | 0            | Yes           |
| 1 GB      | 00:02:48 | 131,073      | 845             | 9,051         | 0             | 0            | Yes           |

**Observations:**
- Encryption overhead is minimal (< 10% performance impact compared to insecure mode)
- Retransmissions occur even at 0% packet loss due to network congestion and timing variations
- All security features (handshake, AEAD, replay protection, SHA-256) work correctly with zero failures in baseline tests


## Security tests using 1 mb file

| Test Case                 | Handshake | AEAD Failures  | Replay Drops  | SHA-256 Match  | Result | Time     |
|---------------------------|-----------|----------------|---------------|----------------|--------|----------|
| Secure transfer baseline  | Success   | 0              | 0             | Yes            | Passed | 00:00:01 |
| Wrong PSK                 | Failed    | N/A            | N/A           | N/A            | Passed |
| Tampered packet           | Success   | 1              | 0             | Yes            | Passed |
| Replay attack             | Success   | 0              | 1             | Yes            | Passed |
| Forged packet injection   | Success   | 1              | 0             | Yes            | Passed |

---

## Known Limitations

While the SRFT protocol implementation is fully functional, there are a few known limitations:

1. **Fixed Timeout Interval:** The timeout value is fixed at 0.5 seconds (configurable in `config.py`) rather than using adaptive timeout based on estimated RTT. This works well for most scenarios but could be optimized for varying network conditions.

2. **Window Size:** The sliding window size is fixed at 128 packets. A dynamic window size adjustment (similar to TCP congestion control) could improve performance in different network conditions.

3. **No Congestion Control:** The implementation uses a fixed sending rate without congestion control mechanisms. In high-loss scenarios, this can lead to increased retransmissions.

4. **Single Concurrent Transfer:** The server handles one client connection at a time. While the server stays running after a transfer completes, it processes requests sequentially rather than concurrently.

5. **Platform-Specific:** Requires root/administrator privileges for raw socket access. The implementation has been tested on Linux (Ubuntu/Amazon Linux) and macOS, but Windows support may require additional configuration.

6. **3% Packet Loss Testing:** The 3% packet loss benchmark is not yet completed (marked as TBD in performance tables).

---

## Lessons Learned

### Phase 1 — Reliable File Transfer

**1. Raw Socket Complexity**
- Working with SOCK_RAW sockets requires manual construction of IP and UDP headers, including checksum calculations. Understanding the packet structure and byte ordering (network byte order vs. host byte order) was crucial.
- Debugging at the packet level required tools like Wireshark to inspect raw frames and verify header correctness.

**2. Go-Back-N Protocol Trade-offs**
- Implementing Go-Back-N (GBN) sliding window protocol was simpler than Selective Repeat but less efficient under packet loss. When the base packet times out, all subsequent packets in the window must be retransmitted even if they were received successfully.
- Delayed ACK optimization (ACK every 16 packets or 10ms delay) significantly reduced ACK traffic and improved throughput.

**3. Timeout Tuning**
- Setting the timeout interval too low caused unnecessary retransmissions; too high caused poor performance. The fixed 0.5s timeout was chosen through empirical testing on AWS EC2.

**4. Threading Challenges**
- Using a separate thread for timeout checking required careful lock management to avoid race conditions when accessing shared state (unacked_packets, base, next_seq_num).

### Phase 2 — Secure File Transfer

**1. AEAD Encryption Integration**
- Integrating AES-GCM AEAD encryption transparently into the transport layer (inside RawSocket) kept the sender/receiver logic clean and modular.
- Using Additional Authenticated Data (AAD) to authenticate packet metadata (session_id, seq_num, ack_num, flags) prevents attackers from tampering with control fields.

**2. Key Derivation**
- Using HKDF-SHA256 to derive separate encryption keys (enc_key, ack_key) from the PSK and handshake nonces ensures each session has unique keys, even with the same PSK.
- Session IDs prevent replay attacks across different sessions.

**3. Replay Protection**
- Sliding-window bitmap-based replay detection was more memory-efficient than storing all seen sequence numbers.
- Integrating replay detection at the receiver's in-order packet handler (not before) was critical—out-of-order packets due to network reordering should not be confused with replays.

**4. Attack Testing**
- Implementing built-in attack modes (--attack tamper/replay/inject) made security testing reproducible and automated.
- AEAD authentication failure handling required careful consideration: drop the packet silently but increment counters for reporting.

**5. Testing Methodology**
- Comprehensive unit tests (108 tests) covering each module independently made integration much smoother.
- End-to-end integration tests on AWS EC2 with simulated packet loss revealed edge cases not found in local testing.

---

## Future Improvements

1. **Adaptive Timeout (Estimated RTT)**
   - Implement TCP-style smoothed RTT estimation and adaptive timeout calculation to handle varying network conditions more efficiently.

2. **Selective Repeat Protocol**
   - Replace Go-Back-N with Selective Repeat to avoid retransmitting successfully received packets, improving performance under packet loss.

3. **Congestion Control**
   - Add TCP-like congestion control (slow start, congestion avoidance, fast recovery) to be more network-friendly and improve performance.

4. **Dynamic Window Sizing**
   - Implement receiver window advertisement and sender window adjustment based on network conditions and receiver buffer availability.

5. **Multi-threaded Server**
   - Support concurrent client connections using multiple threads or async I/O to handle multiple file transfers simultaneously.

6. **Perfect Forward Secrecy (PFS)**
   - Replace PSK-based handshake with Diffie-Hellman Ephemeral (DHE) key exchange to achieve perfect forward secrecy.

7. **Error Recovery & Graceful Degradation**
   - Improve error handling for edge cases (e.g., server crash mid-transfer, client disconnect).
   - Add resume capability for interrupted transfers.

8. **Performance Optimizations**
   - Larger payload sizes (currently 8KB) for better throughput on high-bandwidth networks.
   - Zero-copy optimizations to reduce memory overhead.

9. **IPv6 Support**
   - Extend implementation to support IPv6 addressing.

10. **Cross-Platform Testing**
    - Comprehensive testing on Windows with raw socket alternatives or platform-specific adjustments.

---

## Development Notes

### Team Collaboration
- **Group A (Boston campus):** Kenish, Simona - Responsible for Phase 1 implementation and Phase 2 testing
- **Group B (Vancouver campus):** Hui, Zeyi - Responsible for Phase 1 testing and Phase 2 implementation
- **Documentation:** Hui maintained all project documentation throughout both phases
- The team met weekly (online) to coordinate work and discuss design decisions

### AI Assistant Tool Usage

During development, AI assistant tools (Claude Code) were used for:

1. **Debugging Protocol Issues**
   - Problem: AEAD authentication failures on retransmitted packets
   - Solution: AI helped identify that the attack interceptor was double-encrypting packets
   - Learning: Understanding packet flow through attack interceptor vs. normal path

2. **Git Workflow Issues**
   - Problem: Divergent branches when pushing to remote
   - Solution: AI guided through git merge workflow to reconcile local and remote changes
   - Learning: Proper use of `git pull --no-rebase` for team collaboration

3. **Documentation Generation**
   - Problem: Creating comprehensive README that matches project structure
   - Solution: AI helped generate consistent documentation format and project structure diagram
   - Learning: Importance of keeping documentation in sync with code changes

4. **Code Review and Best Practices**
   - AI tools were used to review code structure, identify potential security issues, and suggest improvements
   - Learning: Defensive programming practices, proper error handling, and security-first mindset

**Note:** All code was written by team members. AI tools were used only for debugging assistance, documentation, and understanding complex concepts after team discussion. The core implementation logic, protocol design, and security architecture decisions were made collaboratively by the team.

### References
- Computer Networking: A Top-Down Approach (Kurose & Ross) - Chapter 3.4 on Reliable Data Transfer
- RFC 1071 - Internet Checksum Computation
- NIST SP 800-38D - AES-GCM AEAD Specification
- RFC 5869 - HKDF Key Derivation Function
- AWS EC2 Documentation - Network Configuration and `tc netem` Usage

---

## Security tests using 100 mb file

| Test Case                 | Handshake | AEAD Failures  | Replay Drops  | SHA-256 Match  | Result |   Time   |
|---------------------------|-----------|----------------|---------------|----------------|--------|----------|
| Secure transfer baseline  | Success   | 0              | 0             | Yes            | Passed | 00:00:19 |
| Wrong PSK                 | Failed    | N/A            | N/A           | N/A            | Passed |
| Tampered packet           | Success   | 1              | 0             | Yes            | Passed |
| Replay attack             | Success   | 0              | 1             | Yes            | Passed |
| Forged packet injection   | Success   | 1              | 0             | Yes            | Passed |


## Security tests using 500 mb file

| Test Case                 | Handshake | AEAD Failures  | Replay Drops  | SHA-256 Match  | Result |  Time    |
|---------------------------|-----------|----------------|---------------|----------------|--------|----------|
| Secure transfer baseline  | Success   | 0              | 0             | Yes            | Passed | 00:01:36 |
| Wrong PSK                 | Failed    | N/A            | N/A           | N/A            | Passed | 
| Tampered packet           | Success   | 1              | 0             | Yes            | Passed | 
| Replay attack             | Success   | 0              | 1             | Yes            | Passed |
| Forged packet injection   | Success   | 1              | 0             | Yes            | Passed |



## Project structure

```
SRFT_UDP_TCP/
├── README.md
├── config.py                          # Global configuration (ports, window size, PSK, timeouts)
├── src/                               # Main source code
│   ├── __init__.py
│   ├── SRFT_UDPClient.py             # Client entry point
│   ├── SRFT_UDPServer.py             # Server entry point
│   ├── protocol/                      # Packet format and headers
│   │   ├── __init__.py
│   │   ├── packet.py                 # SRFT packet structure
│   │   ├── ip_header.py              # IPv4 header build/parse
│   │   ├── udp_header.py             # UDP header build/parse
│   │   └── checksum.py               # Internet checksum
│   ├── transport/                     # Reliable data transfer
│   │   ├── __init__.py
│   │   ├── raw_socket.py             # Raw socket with encryption/replay detection
│   │   ├── sender.py                 # GBN sender with sliding window
│   │   └── receiver.py               # Cumulative ACK receiver
│   ├── security/                      # Phase 2 security features
│   │   ├── __init__.py
│   │   ├── handshake.py              # ClientHello/ServerHello handshake
│   │   ├── crypto.py                 # AES-GCM AEAD, HKDF, HMAC
│   │   ├── replay.py                 # Sliding-window replay protection
│   │   └── attack.py                 # Attack simulator (tamper/replay/inject)
│   └── utils/                         # Shared utilities
│       ├── __init__.py
│       ├── file_handler.py           # File I/O and chunking
│       └── stats.py                  # Transfer report generation
├── tests/                             # Test suite (108 tests)
│   ├── __init__.py
│   ├── test_checksum.py              # Checksum unit tests
│   ├── test_ip_header.py             # IP header tests
│   ├── test_udp_header.py            # UDP header tests
│   ├── test_crypto.py                # Crypto unit tests
│   ├── test_handshake.py             # Handshake unit tests
│   ├── test_handshake_integration.py # Handshake integration tests
│   ├── test_replay.py                # Replay protection tests
│   ├── test_secure_transfer.py       # End-to-end security tests
│   ├── test_forged_injection.py      # Forged packet tests
│   ├── test_files/                   # Test data (10MB-1GB files)
│   ├── phase1/                       # Phase 1 test reports
│   └── phase2/                       # Phase 2 test reports
├── output/                            # Received files and transfer reports
└── docs/                              # Project documentation
    ├── meeting_notes.md              # Team meeting notes
    ├── project_progress.md           # Implementation progress log
```

---

## Root

| Item          | Description                                                                                                                                                                                                                                                                                               |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **README.md** | This file. Overview of the project, how to run client/server, and a guide to the folder and file structure.                                                                                                                                                                                               |
| **config.py** | Central configuration containing: server/client IP addresses and ports (12345/12346), sliding window size (128 packets), timeout interval (0.5s), maximum retries (10), maximum payload size (8KB), packet flags (SYN, ACK, FIN, DATA), and the pre-shared key (PSK) for Phase 2 cryptographic handshake. |

---

## `src/` — Main source code

| File / folder             | Description                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **src/**init**.py**       | Marks `src` as a Python package.                                                                                                                                                                                                                                                                                                                                                                  |
| **src/SRFT_UDPClient.py** | Client entry point with command-line argument parsing. Performs secure handshake (unless `--insecure`), receives requested file from server, verifies SHA-256 file integrity, and generates client-side transfer report with security statistics (AEAD failures, replay drops).                                                                                                                   |
| **src/SRFT_UDPServer.py** | Server entry point with persistent connection handling. Accepts multiple client requests sequentially, performs secure handshake (unless `--insecure`), sends requested files with SHA-256 hash, supports attack simulation modes (`--attack tamper/replay/inject` for security testing), and generates server-side transfer report. Stays running after each transfer to accept the next client. |

---

## `src/protocol/` — Protocol layer

Defines the SRFT packet format, IP/UDP headers, and checksum calculation for raw socket communication.

| File                       | Description                                                                                                                                                                                                                          |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **protocol/**init**.py**   | Package initializer for the protocol module.                                                                                                                                                                                         |
| **protocol/packet.py**     | SRFT packet structure with sequence number, acknowledgment number, flags (SYN, ACK, FIN, DATA), Internet checksum, and payload. Provides serialization (`to_bytes()`) and deserialization (`from_bytes()`) with checksum validation. |
| **protocol/ip_header.py**  | IPv4 header construction and parsing (20 bytes): version, header length, TTL, protocol (UDP=17), source/destination IP addresses, and IP header checksum.                                                                            |
| **protocol/udp_header.py** | UDP header construction and parsing (8 bytes): source/destination ports, length, and UDP checksum (computed over pseudo-header + UDP header + payload).                                                                              |
| **protocol/checksum.py**   | Internet checksum calculation using one's complement arithmetic with proper overflow handling. Used for both packet-level and IP/UDP header checksums.                                                                               |

---

## `src/transport/` — Transport logic

Implements reliable data transfer over raw UDP with sliding window protocol, retransmission, and integrated security.

| File                        | Description                                                                                                                                                                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **transport/**init**.py**   | Package initializer for the transport module.                                                                                                                                                                                                                                               |
| **transport/raw_socket.py** | Raw socket wrapper providing transparent encryption/decryption and replay detection. Handles SOCK_RAW creation, IP/UDP header construction, and integrates AEAD encryption on send and AEAD decryption + replay detection on receive. Tracks AEAD authentication failures and replay drops. |
| **transport/sender.py**     | Sender implementation using Go-Back-N (GBN) sliding window protocol. Manages send window, timeout-based retransmission, cumulative ACK processing, fast retransmit on 3 duplicate ACKs, and transfer statistics.                                                                            |
| **transport/receiver.py**   | Receiver implementation with cumulative ACK protocol. Handles in-order packet acceptance, duplicate detection, out-of-order packet handling, delayed ACK optimization (ACK every 16 packets or 10ms delay), SHA-256 file hash verification, and statistics tracking.                        |

---

## `src/security/` — Phase 2 security features

Security layer providing handshake, encryption, replay protection, and attack simulation.

| File                      | Description                                                                                                                                                                                                                                      |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **security/**init**.py**  | Package initializer for the security module.                                                                                                                                                                                                     |
| **security/handshake.py** | ClientHello/ServerHello handshake protocol with HMAC-based verification. Both sides derive session keys from the pre-shared key (PSK) defined in config.py.                                                                                      |
| **security/crypto.py**    | AEAD encryption using AES-GCM for data confidentiality and authenticity. Implements HKDF-SHA256 for key derivation, HMAC for authentication, and AAD (Additional Authenticated Data) construction.                                               |
| **security/replay.py**    | Replay protection using sliding-window bitmap-based detection. Tracks sequence numbers and rejects duplicate or replayed packets.                                                                                                                |
| **security/attack.py**    | Built-in attack simulator for security testing. Implements `--attack tamper` (bit-flip in encrypted payload), `--attack replay` (duplicate packet), and `--attack inject` (forged packet) modes to verify AEAD and replay protection mechanisms. |

---

## `src/utils/` — Shared utilities

| File                      | Description                                                                                                                                                                                                                                                                                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **utils/**init**.py**     | Package initializer for the utils module.                                                                                                                                                                                                                                                                                                              |
| **utils/file_handler.py** | File I/O operations: reads files in chunks for transmission (respecting MAX_PAYLOAD_SIZE from config) and writes received chunks to output files sequentially.                                                                                                                                                                                         |
| **utils/stats.py**        | Transfer statistics and report generation. Produces `transfer_report.txt` containing transfer metadata (file name, size, duration, throughput), protocol statistics (packets sent, retransmissions, ACKs, duplicates, out-of-order), and security metrics (handshake status, encryption mode, AEAD failures, replay drops, SHA-256 hash verification). |

---

## `tests/` — Unit tests and test data

Comprehensive test suite covering protocol, security, and integration testing.

| Item                                    | Description                                                                                                                                                                              |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **tests/**init**.py**                   | Package initializer for the tests module.                                                                                                                                                |
| **tests/test_checksum.py**              | Unit tests for checksum calculation: empty data, all zeros, all ones, odd-length data, RFC examples, and bit-flip detection.                                                             |
| **tests/test_ip_header.py**             | Unit tests for IP header build/parse operations with round-trip validation.                                                                                                              |
| **tests/test_udp_header.py**            | Unit tests for UDP header build/parse operations with parametrized test cases.                                                                                                           |
| **tests/test_crypto.py**                | Unit tests for cryptographic operations: HKDF key derivation, HMAC authentication, and AES-GCM AEAD encrypt/decrypt.                                                                     |
| **tests/test_handshake.py**             | Unit tests for ClientHello, ServerHello, and full handshake round-trip with key derivation.                                                                                              |
| **tests/test_handshake_integration.py** | End-to-end handshake integration tests with encrypted data exchange and tamper detection.                                                                                                |
| **tests/test_replay.py**                | Unit tests for replay protection: rejects exact duplicates, in-window duplicates, and packets older than the sliding window.                                                             |
| **tests/test_secure_transfer.py**       | Integration tests for secure file transfer: baseline handshake, encrypted data round-trip, SHA-256 hash verification (match/mismatch), wrong PSK rejection, and tampered data detection. |
| **tests/test_forged_injection.py**      | Tests that forged packets with incorrect encryption keys fail AEAD authentication.                                                                                                       |
| **tests/test_files/**                   | Sample files used for testing transfers (e.g., 10MB, 100MB, 500MB, 800MB, 1GB files).                                                                                                    |
| **tests/phase1/**                       | Phase 1 test reports and screenshots documenting reliable transfer with various file sizes and packet loss scenarios.                                                                    |
| **tests/phase2/**                       | Phase 2 test reports and screenshots documenting secure transfer, attack modes, and AEAD/replay protection validation.                                                                   |

---

## `output/` — Transfer results

| Item                           | Description                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **output/**                    | Directory for received files and transfer reports.                                                                                                                                                                                                                                                                                                                                                                    |
| **output/[filename]**          | Files received by the client are saved here with their original names.                                                                                                                                                                                                                                                                                                                                                |
| **output/transfer_report.txt** | Detailed transfer report generated after each transfer containing: transfer metadata (file name, size, duration, throughput), protocol statistics (packets sent, retransmissions, ACKs sent/received, duplicates, out-of-order packets), and security metrics (handshake status, encryption mode, AEAD authentication failures, replay drops, SHA-256 hash verification result). Generated by both client and server. |

---

## `docs/` — Project documentation

| Item                         | Description                                                                                                                                  |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **docs/meeting_notes.md**    | Team meeting notes documenting project timeline, work distribution, and phase transitions (Phase 1 and Phase 2).                             |
| **docs/project_progress.md** | Comprehensive project progress log with implementation status, module completion tracking, phase summaries, and final deliverable checklist. |

---

## Submission Links

### Project Collaboration Documents

- **Meeting Notes (Google Doc):** [Add link here - Ensure proper access permissions are set]
- **Project Management Tool:** [Add link to Trello/Kanban/Google Doc - Ensure proper access permissions are set]
- **GitHub Repository:** https://github.com/KenishRaghu/SRFT_UDP_TCP.git

### Final Submission Checklist

- [x] Phase 1 implementation complete with all error control mechanisms
- [x] Phase 1 testing with 0%, 2%, 4% packet loss (screenshots included)
- [ ] Phase 1 testing with 3% packet loss (pending)
- [x] Phase 2 implementation complete with all security features
- [x] Phase 2 security test plan (all 5 required tests + bonus hash test)
- [x] README with usage instructions, design overview, and performance tables
- [x] Meeting notes documented
- [x] Project progress log maintained
- [x] Source code with proper comments and structure
- [x] 108 unit and integration tests passing
- [ ] Meeting notes Google Doc link (to be added)
- [ ] Project management tool link (to be added)
- [x] Final demo preparation (April 21-22, 2026)

---
