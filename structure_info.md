# SRFT Project Structure Explanation

## Why This Structure?

The project has two distinct layers of work:

1. **Low-level networking** (building raw packets with IP/UDP headers)
2. **Application logic** (reliability, security, file handling)

---

## Folder Breakdown

### `config.py`

Central place for all constants. Anyone can import from here instead of hardcoding values.

- Port numbers (client/server)
- Timeout interval (e.g., 500ms)
- Window size (e.g., 4 packets)
- Max packet payload size (e.g., 1024 bytes)
- PSK key (Phase 2)

---

## `src/protocol/` — Packet Construction Layer

These files handle the raw bytes of network packets.

| File            | Purpose                                                                         |
| --------------- | ------------------------------------------------------------------------------- |
| `checksum.py`   | Function to calculate Internet checksum (used by IP and your app-layer)         |
| `ip_header.py`  | Build and parse the 20-byte IP header (version, length, TTL, src/dst IP, etc.)  |
| `udp_header.py` | Build and parse the 8-byte UDP header (src port, dst port, length, checksum)    |
| `packet.py`     | Custom application-layer header inside UDP payload (seq#, ack#, flags, checksum, data) |


---

## `src/transport/` — Reliability Layer

These files implement the reliable data transfer mechanisms.

| File            | Purpose                                                                              |
| --------------- | ------------------------------------------------------------------------------------ |
| `raw_socket.py` | Wrapper class to create SOCK_RAW socket, send raw packets, receive raw packets       |
| `sender.py`     | Manages send window, tracks unacknowledged packets, handles timeouts and retransmissions |
| `receiver.py`   | Manages receive buffer, reorders out-of-order packets, generates cumulative ACKs     |


---

## `src/security/` — Phase 2 Only


| File           | Purpose                                                   |
| -------------- | --------------------------------------------------------- |
| `handshake.py` | ClientHello/ServerHello exchange, HMAC verification with PSK |
| `crypto.py`    | AES-GCM encryption/decryption, HKDF key derivation        |
| `replay.py`    | Track seen sequence numbers, reject duplicates            |

---

## `src/utils/` — Helper Utilities

| File              | Purpose                                                                    |
| ----------------- | -------------------------------------------------------------------------- |
| `file_handler.py` | Read file and split into chunks (sender), reassemble chunks into file (receiver) |
| `stats.py`        | Track packet counts, retransmits, timing; generate the required output report    |


---

## `src/SRFT_UDPClient.py` and `src/SRFT_UDPServer.py`

Main entry points. These wire everything together:

- Parse command-line arguments (filename, server IP, etc.)
- Initialize sockets, sender/receiver logic
- Start threads for sending and receiving
- Call file handler to read/write files
- Output stats at the end

---

## Other Folders

### `tests/test_files/`

Sample files (small.txt, image.png, large.zip) to test transfers.

### `output/`

Where received files and transfer reports are saved.

### `docs/meeting_notes.md`

Required by the project — document weekly meetings (date, agenda, conclusions).

---


