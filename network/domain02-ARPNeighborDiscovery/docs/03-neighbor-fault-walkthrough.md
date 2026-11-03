# N02 Ví dụ — Route đúng nhưng không tới được next hop

> **Mục tiêu:** luyện thói quen "route lookup đúng ≠ gửi được", và điều tra theo thứ tự từ L1 lên.

## Bối cảnh

```text
VM A 10.66.10.11/24 ──veth-a── bridge ── ? ── gateway 10.66.10.1 ── ... ── 10.66.20.12
```

Triệu chứng: `ping 10.66.20.12` → không có reply.

```bash
$ ip route get 10.66.20.12
10.66.20.12 via 10.66.10.1 dev veth-a src 10.66.10.11
```

Route đúng. Nhưng điều này **chỉ** chứng minh kernel *chọn* được đường — kernel chưa biết MAC gateway.

```bash
$ ip neigh show 10.66.10.1
10.66.10.1 dev veth-a FAILED
```

`INCOMPLETE → FAILED`: không ai trả lời ARP. Packet **không thể** đóng vào frame tới gateway, nên ICMP/TCP không bao giờ rời A.

---

## Điều tra theo thứ tự (từ dưới lên)

| # | Lệnh | Câu hỏi | Nếu sai |
|---|---|---|---|
| 1 | `ip -br link` | veth-a và peer/bridge port có `UP`? | Bật port, kiểm carrier |
| 2 | `ip -br addr` (ở gateway) | Gateway có thật IP `10.66.10.1/24` trên đúng link? | Sửa IP gateway |
| 3 | `bridge vlan show` | Port của A và gateway cùng VLAN? | Sửa VLAN membership/PVID |
| 4 | `sudo tcpdump -eni veth-a arp` | A có phát ARP? Có reply? | Xem bảng dưới |
| 5 | `ip neigh` | Mapping cuối cùng là gì? | — |

## Diễn giải capture

| Thấy gì | Kết luận | **Không** làm |
|---|---|---|
| Request, không reply | Link / VLAN / IP gateway | Sửa DNS, sửa route |
| Reply có, `ip neigh` không ổn định | Duplicate IP / MAC đổi | Thêm static ARP |
| Neighbor `REACHABLE`, ping gateway OK | L2 ổn → chuyển sang **routing/firewall** lớp tiếp theo | Tiếp tục đào ARP |

---

## Bài học

```text
route lookup  → quyết định CÓ cố gửi không, gửi qua ai
ARP/ND        → quyết định MAC của next hop
bridge/VLAN   → quyết định frame có tới được port đó không
```

Ba bước độc lập; một bước đúng không chứng minh bước sau đúng.

## Tự kiểm tra

Capture thấy ARP request `who-has 10.66.10.1` lặp lại mỗi giây, không có reply. `bridge vlan show` cho thấy port của A ở VLAN 10, port của gateway ở VLAN 20. Root cause là gì, sửa tối thiểu ra sao?

<details>
<summary>Đáp án</summary>

Root cause: A và gateway khác VLAN nên ARP broadcast không tới gateway. Sửa tối thiểu: đưa port (của A hoặc gateway, theo address plan) về đúng VLAN; sau đó verify `ip neigh` → `REACHABLE`, ping gateway, rồi ping `10.66.20.12`.

</details>
