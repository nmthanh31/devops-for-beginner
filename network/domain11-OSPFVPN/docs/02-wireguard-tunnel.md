# N11 Bài 2 — VPN tunnel và WireGuard

> **Sau bài này bạn sẽ:**
> - Tách **underlay** (outer UDP) và **overlay** (inner packet) thành hai bài toán riêng.
> - Hiểu **AllowedIPs** làm hai việc: chọn peer khi gửi + lọc nguồn khi nhận.
> - Biết handshake thành công chứng minh gì và **không** chứng minh gì.
>
> **Cần trước:** [Bài 1](./01-ospf-adjacency.md), [N10 MTU](../../domain10-LossMTU/docs/02-mtu-pmtud.md).

---

## 1. Hình dung: phong bì trong phong bì

Bạn bỏ lá thư nội bộ (inner packet `10.90.1.10 → 10.90.2.10`) vào phong bì khóa kín, rồi gửi phong bì qua bưu điện công cộng (outer UDP `192.0.2.1:51820 → 192.0.2.2:51820`). Bưu điện chỉ thấy phong bì ngoài.

```text
                  inner: 10.90.1.10 → 10.90.2.10 (ICMP/TCP...)
 App ─► wg0 ─► mã hóa + bọc ─► outer: 192.0.2.1:51820 → 192.0.2.2:51820 (UDP)
                                  │ underlay route (NIC thật)
                                  ▼
 Peer ◄─ giải mã ◄─ wg0 ◄─────────┘   inner packet tiếp tục routing ở peer
```

## 2. Hai bài toán, hai bảng route

| | Underlay (outer) | Overlay (inner) |
|---|---|---|
| Địa chỉ | Endpoint IP:UDP port | IP ứng dụng / subnet sau peer |
| Route phải đi | Qua **NIC thật** | Qua **wg0** |
| Lỗi thì thấy | Không có handshake | Có handshake, không có inner traffic |

> **Bẫy:** route tới endpoint vô tình đi vào chính `wg0` (ví dụ AllowedIPs `0.0.0.0/0` mà không có route riêng cho endpoint) → tunnel không bao giờ lên.

## 3. Cấu hình một peer

```ini
[Interface]
PrivateKey = <key-site1>
Address    = 10.90.0.1/24          # IP tunnel
ListenPort = 51820

[Peer]
PublicKey  = <pub-site2>
Endpoint   = 192.0.2.2:51820       # underlay
AllowedIPs = 10.90.0.2/32, 10.90.2.0/24
```

**AllowedIPs** làm hai việc:

| Chiều | Vai trò |
|---|---|
| Gửi | Đích thuộc AllowedIPs của peer nào → gửi cho peer đó (cryptokey routing) |
| Nhận | Inner source không thuộc AllowedIPs của peer gửi → **drop** |

Ngoài ra OS vẫn cần **route** đưa `10.90.2.0/24` vào `wg0` (`wg-quick` tự thêm từ AllowedIPs; `wg set` thủ công thì không).

Đầu kia cần đối xứng: AllowedIPs chứa `10.90.1.0/24`, route về, và **ip_forward** nếu route subnet phía sau.

## 4. Đọc `wg show`

```text
peer: <pub-site2>
  endpoint: 192.0.2.2:51820
  allowed ips: 10.90.0.2/32, 10.90.2.0/24
  latest handshake: 12 seconds ago
  transfer: 15.2 KiB received, 18.9 KiB sent
```

| Quan sát | Nghĩa | Kiểm |
|---|---|---|
| Không có `latest handshake` | Outer không thông | Route/DNS tới endpoint, UDP port, firewall, key |
| Handshake OK, transfer **một chiều** | Inner bị drop/không về | AllowedIPs, inner route, forwarding, return path |
| Handshake OK, inner OK tới IP tunnel nhưng không tới subnet sau peer | Peer không forward | `ip_forward`, route/firewall ở peer |

> Handshake = hai peer liên lạc mật mã được. **Chưa** chứng minh inner route, AllowedIPs, firewall.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Ping IP tunnel peer OK → subnet sau peer OK." | Cần forwarding + route ở peer. |
| "AllowedIPs chỉ là ACL." | Còn là bảng chọn peer khi gửi. |
| "Tunnel lên thì MTU không đổi." | Overhead ~60–80 byte → PMTU giảm ([N10](../../domain10-LossMTU/README.md)). |

## Tự kiểm tra

1. Site1 ping `10.90.2.10`, `wg show` transfer sent tăng, received không. Capture `wg0` ở site2 thấy request. Nghi gì?
2. Bạn đổi AllowedIPs site2 bỏ `10.90.1.0/24`. Handshake còn không? Inner traffic?

<details>
<summary>Đáp án</summary>

1. Site2 không có đường về / reply không vào `wg0` (route về, AllowedIPs site2 thiếu prefix nguồn, hoặc firewall).
2. Handshake vẫn còn (không phụ thuộc AllowedIPs); inner traffic từ `10.90.1.x` bị site2 drop và reply không có peer để gửi.

</details>

## Nguồn

[WireGuard Quick Start](https://www.wireguard.com/quickstart/) · [WireGuard — Cryptokey Routing](https://www.wireguard.com/#cryptokey-routing)
