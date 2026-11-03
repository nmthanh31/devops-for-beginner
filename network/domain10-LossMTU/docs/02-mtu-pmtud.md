# N10 Bài 2 — MTU, MSS và Path MTU Discovery

> **Sau bài này bạn sẽ:**
> - Phân biệt MTU interface, **Path MTU**, **MSS**.
> - Hiểu PMTUD và **PMTU black hole** (ping nhỏ OK, transfer lớn treo).
> - Tính đúng kích thước `ping -M do -s` để dò ngưỡng.
>
> **Cần trước:** [N01 — MTU](../../domain01-EncapsulationEthernet/docs/01-layers-and-frames.md#6-mtu--giới-hạn-kích-thước), [Bài 1](./01-loss-latency.md).

---

## 1. Hình dung: đường hầm thấp

Xe tải cao 4m (packet 1500) chạy tốt trên đường lớn, nhưng giữa đường có hầm cao 3.8m (tunnel/VPN). **Path MTU** là độ cao của chỗ thấp nhất trên **cả tuyến**. Biển báo "hầm thấp, quay lại" chính là **ICMP Fragmentation Needed / Packet Too Big**. Nếu ai đó gỡ biển (firewall chặn ICMP) → xe cứ lao vào, kẹt mãi.

## 2. Ba con số

| | Là gì | Ví dụ |
|---|---|---|
| **MTU** | IP packet tối đa trên **một link** | 1500 |
| **Path MTU** | MTU **nhỏ nhất** trên toàn đường | 1420 (qua WireGuard) |
| **MSS** | TCP payload tối đa/segment, quảng bá trong SYN | 1460 = 1500 − 20 IP − 20 TCP |

Tunnel thêm header ngoài → inner packet phải nhỏ hơn để còn chỗ:

```text
Underlay MTU 1500
┌────────────── outer IP+UDP+WG (~60–80 byte) ──────────────┐
│               inner packet ≤ ~1420                          │
└─────────────────────────────────────────────────────────────┘
```

## 3. PMTUD hoạt động thế nào

```text
IPv4: Source gửi packet 1500, cờ DF (Don't Fragment)
      Router có egress MTU 1420 → không fragment được
      → trả ICMP "Fragmentation Needed, next-hop MTU 1420"
      Source ghi nhớ PMTU = 1420, gửi lại nhỏ hơn
IPv6: Router KHÔNG BAO GIỜ fragment → luôn gửi ICMPv6 "Packet Too Big"
```

### PMTU black hole

ICMP trên bị chặn → source không bao giờ biết → cứ gửi packet lớn → mất → TCP retransmit mãi.

**Triệu chứng kinh điển:** ping nhỏ OK, SSH login OK, nhưng `git clone`/tải trang lớn/TLS handshake có cert dài **treo**. Phải **chứng minh** bằng kích thước + capture, không chỉ suy từ triệu chứng.

---

## 4. Dò ngưỡng bằng ping

`-s` là **ICMP payload**, không phải toàn bộ packet:

```text
IP packet = -s + 8 (ICMP header) + 20 (IPv4 header)
-s 1472 → 1500 byte   ✔ trên MTU 1500
-s 1473 → 1501 byte   ✘
```

```bash
ip link show dev IFACE               # MTU interface
tracepath DEST                       # dò pmtu theo từng hop
ping -M do -s 1472 -c 2 DEST         # -M do: cấm fragment (IPv4)
ping -M do -s 1473 -c 2 DEST
```

| Kết quả | Nghĩa |
|---|---|
| `message too long, mtu=1400` **ngay tại source** | Interface local (hoặc PMTU đã cache) nhỏ hơn |
| `Frag needed and DF set (mtu = 1400)` từ router | Router giữa đường báo đúng — PMTUD chạy |
| Không có phản hồi, timeout | Có thể **black hole** — capture hai phía link nhỏ |

## 5. Sửa đúng

| Cách | Khi nào |
|---|---|
| Cho ICMP type 3 code 4 / ICMPv6 Packet Too Big đi qua | Gốc rễ là firewall chặn |
| Đặt MTU đúng cho tunnel/inner interface | Tunnel cấu hình sai |
| **MSS clamping** trên router (`tcp option maxseg size set rt mtu`) | Không kiểm soát được middlebox; chỉ cứu TCP |

> Hạ MTU bừa bãi trên mọi host chỉ che nguyên nhân và giảm hiệu quả. **Không** đổi MTU NIC quản trị để thử giả thuyết.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "`-s 1500` là packet 1500." | Packet = 1528. |
| "Chặn hết ICMP cho an toàn." | Phá PMTUD. |
| "MSS clamping sửa mọi thứ." | Chỉ TCP; UDP/QUIC vẫn hỏng. |

## Tự kiểm tra

1. Path MTU 1420. `-s` lớn nhất để `ping -M do` qua được?
2. Ping `-s 1300` OK, `-s 1400` timeout không có ICMP error. Gợi ý gì?

<details>
<summary>Đáp án</summary>

1. 1420 − 28 = **1392**.
2. Ngưỡng nằm giữa 1328 và 1428 byte và ICMP báo lỗi bị chặn → nghi black hole; capture hai phía link.

</details>

## Nguồn

[RFC 1191 IPv4 PMTUD](https://www.rfc-editor.org/rfc/rfc1191) · [RFC 8201 IPv6 PMTUD](https://www.rfc-editor.org/rfc/rfc8201) · [tracepath(8)](https://man7.org/linux/man-pages/man8/tracepath.8.html)
