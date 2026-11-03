# N11 Ví dụ — Control plane khỏe, data plane vẫn lỗi

> **Bài học chung:** *trạng thái "xanh" của giao thức điều khiển (neighbor Full, handshake gần đây) không chứng minh packet dữ liệu đi được.*

## Phần 1 — OSPF Full nhưng không tới LAN

R1/R2 neighbor `Full`. Client sau R1 không tới `10.11.2.10` (LAN sau R2).

| # | Kiểm | Lớp | Ví dụ thấy |
|---|---|---|---|
| 1 | `show ip ospf neighbor` | Adjacency | Full ✅ |
| 2 | `show ip ospf database` | LSDB | **Không** có LSA cho `10.11.2.0/24` ❌ |
| 3 | `show ip route ospf` | FRR route | Không có |
| 4 | `ip route get 10.11.2.10` | Kernel | Đi default |
| 5 | ping / capture | Data | Fail |

Root cause trong ví dụ: R2 chưa quảng bá LAN (thiếu `network 10.11.2.0/24 area 0` hoặc interface chưa bật OSPF). Fix → LSA xuất hiện → route cài vào kernel → verify data hai chiều.

## Phần 2 — WireGuard handshake OK nhưng inner fail

```text
Outer: R1 192.0.2.1:51820 → R2 192.0.2.2:51820   (UDP mã hóa)
Inner: 10.11.1.10         → 10.11.2.10
```

| Capture ở | Thấy | Kết luận |
|---|---|---|
| Underlay NIC | UDP 51820 hai chiều | Outer OK |
| `wg0` R1 | Không có inner packet | **Route/AllowedIPs ở R1** — packet không vào tunnel |
| `wg0` R2 | Request có, reply không | **Return route/policy ở R2** |

> Capture underlay chỉ thấy UDP mã hóa; muốn thấy inner phải capture trên `wg0`.
