# SRFT Project Progress Log

## Project Overview

- **Course:** CS 5700 — Fundamentals of Computer Networking (Spring 2026)
- **Project:** Secure Reliable File Transfer (SRFT) over UDP using SOCK_RAW
- **Repo:** https://github.com/KenishRaghu/SRFT_UDP_TCP.git

## Key Deadlines

| Milestone | Target Date |
|-----------|-------------|
| Phase 1 — Reliable File Transfer | Mid-March 2026 |
| Phase 2 — Secure File Transfer | Mid-April 2026 |
| Final Demo | April 21–22, 2026 |
| Final Submission (Canvas) | April 22, 2026, 11:59 PM PDT |

---

## Current Status (as of Feb 25, 2026)

**Phase 1 progress: ~70% complete**
**Phase 2 progress: Not started**

### Completed Modules

| Module | File | Summary |
|--------|------|---------|
| Configuration | `config.py` | Server/client ports, window size (4), timeout (0.5s), max payload (1024B), packet flags (DATA, ACK, FIN, REQ) defined |
| Checksum | `src/protocol/checksum.py` | Internet checksum calculation and verification with overflow handling |
| IP Header | `src/protocol/ip_header.py` | Build and parse 20-byte IPv4 headers (version, TTL, protocol, src/dst IP, checksum) |
| UDP Header | `src/protocol/udp_header.py` | Build and parse 8-byte UDP headers (src/dst port, length, checksum) |
| SRFT Packet | `src/protocol/packet.py` | Packet class with seq#, ack#, flags, checksum, payload; serialization/deserialization; corruption detection |
| Sender | `src/transport/sender.py` | Sliding window protocol with timeout-based retransmission, ACK handling, background timer thread, statistics tracking |
| Server | `src/SRFT_UDPServer.py` | Full server entry point — raw socket setup, file chunking, packet transmission, ACK listener thread, transfer stats |
| Checksum Tests | `tests/test_checksum.py` | Comprehensive unit tests (empty data, all zeros, all ones, odd-length, RFC examples, bit-flip corruption detection) |
| UDP Header Tests | `tests/test_udp_header.py` | Round-trip tests for header build/parse, parametrized with multiple port/payload combinations |

### Stub Modules (Not Yet Implemented)

| Module | File | Required For |
|--------|------|--------------|
| Client | `src/SRFT_UDPClient.py` | Phase 1 — sends filename request, receives file, sends ACKs |
| Raw Socket Wrapper | `src/transport/raw_socket.py` | Phase 1 — modularize socket creation (currently inline in server) |
| Receiver | `src/transport/receiver.py` | Phase 1 — receive buffer, reorder out-of-order packets, cumulative ACKs |
| File Handler | `src/utils/file_handler.py` | Phase 1 — file chunking (send) and reassembly (receive) |
| Stats/Report | `src/utils/stats.py` | Phase 1 — transfer report output (name, size, packets sent/retransmitted/received, duration) |
| Crypto | `src/security/crypto.py` | Phase 2 — AES-GCM (AEAD) encryption, HKDF key derivation |
| Handshake | `src/security/handshake.py` | Phase 2 — ClientHello/ServerHello, HMAC verification with PSK |
| Replay Protection | `src/security/replay.py` | Phase 2 — reject duplicate/out-of-window sequence numbers |

---

## Phase 1 Remaining Work

To complete Phase 1 (reliable file transfer), the following items are needed:

1. **SRFT_UDPClient** — Client entry point: parse args (filename, server IP), send file request, receive data packets, send cumulative ACKs, reassemble file
2. **Receiver module** — Receive buffer with reordering, cumulative ACK generation (must avoid per-packet ACK)
3. **File handler** — Chunking files into MAX_PAYLOAD_SIZE blocks for sending; reassembling received chunks into the output file
4. **Stats/report** — Generate the required output report (file name, size, packets sent, retransmissions, packets received, transfer duration)
5. **Raw socket wrapper** — Extract raw socket logic from server into reusable module (used by both client and server)
6. **End-to-end testing** — Verify file integrity with md5sum on AWS EC2 with 2–4% packet loss (using `tc netem`)

## Phase 2 Planned Work

1. **PSK + Handshake** — ClientHello/ServerHello with HMAC, session key derivation via HKDF-SHA256
2. **AEAD Encryption** — AES-GCM for all DATA and ACK packets, with AAD (session_id, seq#, ack#, flags)
3. **Replay Protection** — Sequence number tracking, reject duplicates and out-of-window packets
4. **SHA-256 File Verification** — End-to-end file digest comparison
5. **Built-in Attack Modes** — `--attack tamper`, `--attack replay`, `--attack inject` flags for security testing
6. **Security Test Plan** — 5 required tests (baseline, wrong PSK, tamper, replay, forged injection)
7. **Updated Report Output** — Add security fields (PSK+AEAD enabled, handshake status, AEAD failures, replay drops, SHA-256 match)

---

## Notes

- Server implementation currently has raw socket and file chunking logic inline rather than using the modular `transport/` and `utils/` modules
- Tests exist only for protocol layer (checksum, UDP header); no integration tests yet
- AWS EC2 setup and packet loss emulation (`tc netem`) have not been tested yet
