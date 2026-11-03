# N10 Ví dụ — Ping nhỏ được nhưng response lớn treo

## Bối cảnh

```text
Client (MTU 1500) ── Router A ══ VPN tunnel (PMTU ~1400) ══ Router B ── Server (MTU 1500)
                                 firewall chặn ICMP type 3
```

Triệu chứng: `curl https://server/` lấy header được rồi **treo** khi tải body lớn; `ping` mặc định đẹp.

> ✋ Vì sao ping mặc định (`-s 56`) không phát hiện được?

## Diễn biến

```text
Packet nhỏ (SYN, ping, request)  → vừa tunnel → PASS
Response lớn 1500 + DF           → router A không fragment được
                                 → gửi ICMP Frag Needed → bị firewall chặn
Server không học được PMTU       → gửi lại 1500 → mất → retransmit → treo
```

## Chứng minh

| # | Evidence | Thấy |
|---|---|---|
| 1 | `ping -M do -s 1300` / `-s 1400` | 1300 OK, 1400 timeout (không có error) |
| 2 | `tracepath server` | `pmtu 1400` hoặc dừng ở hop tunnel |
| 3 | Capture tại server | Segment lớn bị retransmit lặp lại |
| 4 | Capture router A | Gửi ICMP Frag Needed — nhưng không thấy ở server |

## Sửa

Đúng gốc: cho ICMP Frag Needed đi qua firewall, **hoặc** đặt MTU tunnel đúng, **hoặc** MSS clamp trên router. Không hạ MTU toàn bộ host.

## Trên lab veth

Hạ MTU một link, `ping -M do -s SIZE` tăng dần. Nhớ: `-s` **không gồm** 28 byte header → ngưỡng `-s` thấp hơn MTU 28. Capture cả hai đầu để phân biệt bị từ chối **tại source** (`message too long`) hay **tại router** (ICMP Frag needed).
