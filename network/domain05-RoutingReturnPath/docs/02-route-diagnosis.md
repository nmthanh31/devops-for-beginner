# N05 Bài 2 — Bằng chứng cho lỗi route: paired capture, asymmetric, policy routing

> **Sau bài này bạn sẽ:**
> - Theo một quy trình 5 bước để định vị packet dừng ở đâu.
> - Dùng **paired capture** và tuple để ghép một flow qua nhiều điểm.
> - Nhận ra **asymmetric routing** và **policy routing** khi bảng `main` trông đúng mà vẫn lỗi.
>
> **Cần trước:** [Bài 1](./01-forward-and-return.md).

---

## 1. Quy trình 5 bước

| # | Lệnh | Câu hỏi |
|---|---|---|
| 1 | `ip -br addr` | Address/prefix từng interface đúng plan? |
| 2 | `ip route get DEST` | Source, next hop, egress interface? |
| 3 | `ip neigh` | Next hop có phân giải được MAC? ([N02](../../domain02-ARPNeighborDiscovery/README.md)) |
| 4 | `sysctl net.ipv4.ip_forward` | Router có forward? |
| 5 | Capture nhiều điểm | Packet dừng ở đâu? |

> **Đừng thêm route theo cảm tính** khi chưa biết packet dừng ở đâu.

## 2. Paired capture — capture nhiều điểm cùng lúc

```text
Client ─[1]─► Router ingress ─[2]─ Router egress ─[3]─► Server ─[4]
```

| Thấy ở | Không thấy ở | Lỗi nằm ở |
|---|---|---|
| [1] SYN | [2] | Trước router: link, ARP gateway, VLAN |
| [2] | [3] | **Trong router**: `ip_forward`, FORWARD, route |
| [4] SYN, không SYN-ACK | — | Server: firewall INPUT, không listener, chọn source sai |
| [4] SYN-ACK đi ra | [1] không có SYN-ACK | **Đường về**: route ở server/router, firewall chiều về |

Ghép flow bằng **timestamp + tuple** `src IP:port → dst IP:port`. Router thuần chỉ đổi MAC/TTL. Có NAT thì tuple đổi — ghi cả trước/sau ([N09](../../domain09-FirewallConntrackNAT/README.md)).

---

## 3. Asymmetric routing

Request và response đi **hai đường khác nhau**.

```text
          ┌── R1 (stateful firewall) ──┐
Client ───┤                            ├─── Server
          └── R2 ──────────────────────┘
SYN đi qua R1     → R1 lưu state
SYN-ACK về qua R2 → R2 chưa từng thấy SYN → có thể drop
```

Asymmetric **không luôn sai**, nhưng stateful firewall/NAT chỉ thấy một chiều sẽ drop. Khi server có reply mà client không nhận, kiểm:

```bash
ip route get CLIENT_IP from SERVER_IP    # chạy trên server
```

## 4. Policy routing

`ip rule` chọn **bảng route** theo source IP, fwmark... *trước khi* tra bảng.

```bash
ip rule                          # 0: local, 32766: main, 32767: default (mặc định)
ip route show table all
ip route get DEST from SOURCE    # mô phỏng với source cụ thể
```

Dấu hiệu: `ip route` (bảng main) đúng mà kernel vẫn chọn đường lạ → xem `ip rule`.

### Nhiều NIC và source IP

Ứng dụng bind source khác với source kernel chọn → request đi ra được nhưng reply về sai interface, hoặc bị **reverse-path filter** (`rp_filter`) chặn. So `ip route get DEST from SRC` cho **từng** source IP.

---

## 5. Sửa đúng cách

- Thêm **route nhỏ nhất** tại **đúng endpoint/router** (ví dụ một `/24`), không sửa rộng.
- **Không thay default route** của VM đang SSH khi chỉ cần tới một lab subnet.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Bảng main đúng là đủ." | `ip rule` có thể chọn bảng khác. |
| "Asymmetric luôn là lỗi." | Chỉ lỗi khi có thiết bị stateful thấy một chiều. |
| "Capture một điểm là đủ." | Một điểm chỉ nói packet *có ở đó*, không nói dừng ở đâu. |

## Tự kiểm tra

1. Thấy SYN ở router ingress, không thấy ở egress. `ip_forward=1`. Kiểm gì tiếp?
2. Server có 2 NIC; `ip route get 10.51.1.10` ra `eth0` nhưng `ip route get 10.51.1.10 from 10.99.0.5` ra `eth1`. Điều này gợi ý gì?

<details>
<summary>Đáp án</summary>

1. Firewall chain FORWARD và route tới đích trong router namespace.
2. Có policy routing theo source (hoặc route khác nhau theo source); reply phụ thuộc source IP ứng dụng dùng.

</details>

## Nguồn

- [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html) · [ip-rule(8)](https://man7.org/linux/man-pages/man8/ip-rule.8.html)
- [LPIC-1 109.3](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
